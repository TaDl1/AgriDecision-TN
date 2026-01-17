"""
Core decision engine - combines agrarian calendar, weather, and AI
"""
import logging
from datetime import datetime, date
from typing import Dict, List, Tuple
from models.base import db
from models.crop import Crop, AgrarianPeriod, CropPeriodRule
from models.decision import Decision
from services.weather_service import WeatherService
from services.ai_service import AIService

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Core decision-making engine"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.ai_service = AIService()
    
    def get_advice(self, farmer_id: int, crop_id: int, governorate: str, 
                   seedling_cost: float = None, market_price: float = None,
                   input_quantity: float = 1.0) -> Dict:
        """
        Get comprehensive planting advice
        
        Args:
            farmer_id: ID of the farmer
            crop_id: ID of the crop
            governorate: Tunisian governorate
            seedling_cost: Cost per seedling in TND (optional)
            market_price: Market price per kg in TND (optional)
            input_quantity: Quantity of inputs bought (optional, default 1.0)
        
        Returns:
            Complete advice dictionary
        """
        # Step 1: Determine current agrarian period
        current_period = self._get_current_period()
        logger.info(f"Current period: {current_period.id} - {current_period.name}")
        
        # Step 2: Get crop-specific rules for this period
        rule = CropPeriodRule.query.filter_by(
            crop_id=crop_id,
            period_id=current_period.id
        ).first()
        
        if not rule:
            logger.warning(f"No rule found for crop {crop_id} in period {current_period.id}")
            # Create default risky rule
            rule = type('obj', (object,), {
                'suitability': 'risky',
                'reason': 'No specific guidance for this period'
            })()
        
        # Step 3: Get weather forecast
        weather_forecast = self.weather_service.get_forecast(governorate, days=7)
        
        # Step 4: Analyze weather against crop requirements
        weather_analysis = self._analyze_weather(weather_forecast, crop_id)
        
        # Step 5: Make decision based on rules + weather
        decision = self._make_decision(rule, weather_analysis)
        
        # Step 6: Generate AI explanation
        crop = Crop.query.get(crop_id)
        ai_input = {
            'crop_name': crop.name,
            'action': decision['action'],
            'wait_days': decision.get('wait_days', 0),
            'period_name': current_period.name,
            'risks': [r['type'] for r in weather_analysis['risks']]
        }
        explanation = self.ai_service.generate_explanation(ai_input)
        
        # Step 7: Build response
        response = {
            'decision': decision,
            'period': {
                'id': current_period.id,
                'name': current_period.name,
                'risk': current_period.risk_level,
                'description': current_period.description
            },
            'weather_forecast': weather_forecast,
            'weather_analysis': weather_analysis,
            'explanation': explanation
        }
        
        # Step 8: Record decision in database
        decision_id = self._record_decision(
            farmer_id, crop_id, governorate,
            decision, explanation, current_period.id,
            weather_analysis, seedling_cost, market_price, input_quantity
        )
        
        response['id'] = decision_id
        return response
    
    def _get_current_period(self) -> AgrarianPeriod:
        """Determine current agrarian period based on date"""
        today = date.today()
        periods = AgrarianPeriod.query.order_by(
            AgrarianPeriod.start_month,
            AgrarianPeriod.start_day
        ).all()
        
        for period in periods:
            # Handle period that crosses year boundary
            if period.start_month > period.end_month:
                # Period spans New Year (e.g., Dec-Jan)
                if today.month >= period.start_month or today.month <= period.end_month:
                    start_date = date(today.year if today.month >= period.start_month else today.year - 1,
                                    period.start_month, period.start_day)
                    end_date = date(today.year if today.month <= period.end_month else today.year + 1,
                                  period.end_month, period.end_day)
                    if start_date <= today or today <= end_date:
                        return period
            else:
                # Normal period within same year
                start_date = date(today.year, period.start_month, period.start_day)
                end_date = date(today.year, period.end_month, period.end_day)
                if start_date <= today <= end_date:
                    return period
        
        # Fallback to first period
        return periods[0] if periods else None
    
    def _analyze_weather(self, forecast: List[Dict], crop_id: int) -> Dict:
        """
        Analyze weather forecast against crop requirements
        
        Args:
            forecast: List of weather forecast days
            crop_id: Crop ID
        
        Returns:
            Dictionary with risks and metrics
        """
        crop = Crop.query.get(crop_id)
        risks = []
        
        for day in forecast:
            # Check temperature risks
            if day['temp_min'] < crop.min_temp:
                severity = 'high' if day['temp_min'] < crop.min_temp - 3 else 'medium'
                risks.append({
                    'type': 'low_temperature',
                    'severity': severity,
                    'date': day['date'],
                    'value': day['temp_min']
                })
            
            if day['temp_max'] > crop.max_temp:
                severity = 'high' if day['temp_max'] > crop.max_temp + 5 else 'medium'
                risks.append({
                    'type': 'high_temperature',
                    'severity': severity,
                    'date': day['date'],
                    'value': day['temp_max']
                })
            
            # Check frost risk (critical for all crops)
            if day['temp_min'] < 2:
                risks.append({
                    'type': 'frost_risk',
                    'severity': 'high',
                    'date': day['date'],
                    'value': day['temp_min']
                })
            
            # Check heavy rain risk
            if day['rainfall'] > 20:
                risks.append({
                    'type': 'heavy_rain',
                    'severity': 'medium',
                    'date': day['date'],
                    'value': day['rainfall']
                })
        
        avg_temp = sum(d['temp_avg'] for d in forecast) / len(forecast) if forecast else 0
        avg_humidity = sum(d.get('humidity', 60) for d in forecast) / len(forecast) if forecast else 60
        total_rainfall = sum(d.get('rainfall', 0) for d in forecast) if forecast else 0
        
        return {
            'risks': risks,
            'avg_temp': round(avg_temp, 1),
            'avg_humidity': round(avg_humidity, 1),
            'total_rainfall': round(total_rainfall, 1),
            'temp_min_forecast': min([d['temp_min'] for d in forecast]) if forecast else None,
            'temp_max_forecast': max([d['temp_max'] for d in forecast]) if forecast else None,
            'risk_count': len(risks)
        }
    
    def _make_decision(self, rule, weather_analysis: Dict) -> Dict:
        """
        Make final decision based on rules and weather
        
        Args:
            rule: CropPeriodRule object
            weather_analysis: Weather analysis dictionary
        
        Returns:
            Decision dictionary
        """
        # If period is forbidden, immediate rejection
        if rule.suitability == 'forbidden':
            return {
                'action': 'NOT_RECOMMENDED',
                'confidence': 'HIGH',
                'reason': rule.reason or "Not in the planting season.",
                'wait_days': 0
            }
        
        # Check for critical weather risks
        critical_risks = [r for r in weather_analysis['risks'] if r['severity'] == 'high']
        if critical_risks:
            return {
                'action': 'WAIT',
                'wait_days': 7,
                'confidence': 'HIGH',
                'reason': f"Severe weather risk: {critical_risks[0]['type']}"
            }
        
        # If period is risky, recommend waiting
        if rule.suitability == 'risky':
            return {
                'action': 'WAIT',
                'wait_days': 5,
                'confidence': 'MEDIUM',
                'reason': rule.reason or "Agrarian calendar indicates risk."
            }
        
        # If there are medium risks, calculate wait time
        if weather_analysis['risks']:
            last_risk_date_str = max(r['date'] for r in weather_analysis['risks'])
            last_risk_date = datetime.strptime(last_risk_date_str, '%Y-%m-%d').date()
            today = date.today()
            wait_days = (last_risk_date - today).days + 1
            wait_days = max(1, min(wait_days, 14))  # Between 1 and 14 days
            
            return {
                'action': 'WAIT',
                'wait_days': wait_days,
                'confidence': 'MEDIUM',
                'reason': "Minor weather conditions unfavorable."
            }
        
        # Optimal conditions - plant now!
        return {
            'action': 'PLANT_NOW',
            'confidence': 'HIGH',
            'reason': "Optimal period with favorable weather.",
            'wait_days': 0
        }
    
    def _record_decision(self, farmer_id: int, crop_id: int, governorate: str,
                        decision: Dict, explanation: str, period_id: str,
                        weather_data: Dict, seedling_cost: float = None, 
                        market_price: float = None, input_quantity: float = 1.0):
        """Record decision in database for analytics"""
        try:
            new_decision = Decision(
                farmer_id=farmer_id,
                crop_id=crop_id,
                governorate=governorate,
                recommendation=decision['action'],
                wait_days=decision.get('wait_days', 0),
                confidence=decision['confidence'],
                explanation=explanation,
                period_id=period_id,
                weather_temp_avg=weather_data.get('avg_temp'),
                weather_temp_min=weather_data.get('temp_min_forecast'),
                weather_temp_max=weather_data.get('temp_max_forecast'),
                weather_humidity=weather_data.get('avg_humidity'),
                weather_rainfall=weather_data.get('total_rainfall'),
                weather_risks=str([r['type'] for r in weather_data.get('risks', [])]),
                seedling_cost_tnd=seedling_cost,
                market_price_tnd=market_price,
                input_quantity=input_quantity
            )
            db.session.add(new_decision)
            db.session.commit()
            logger.info(f"Decision recorded: ID={new_decision.id}, Qty={input_quantity}, Cost={seedling_cost}, MkPrice={market_price}")
            return new_decision.id
        except Exception as e:
            logger.error(f"Failed to record decision: {e}")
            db.session.rollback()
            return None