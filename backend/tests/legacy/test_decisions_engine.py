"""
Decision engine tests
"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from services.decision_engine import DecisionEngine
from models.crop import Crop, AgrarianPeriod, CropPeriodRule


class TestDecisionEngine:
    """Test decision engine functionality"""
    
    def test_get_current_period(self, app):
        """Test getting current agrarian period"""
        with app.app_context():
            engine = DecisionEngine()
            period = engine._get_current_period()
            
            assert period is not None
            assert hasattr(period, 'id')
            assert hasattr(period, 'name')
    
    @patch.object(DecisionEngine, '_get_current_period')
    @patch('services.weather_service.WeatherService.get_forecast')
    @patch('services.ai_service.AIService.generate_explanation')
    def test_get_advice_plant_now(self, mock_ai, mock_weather, mock_period, app, db_session, test_farmer, test_crop):
        """Test advice generation for PLANT_NOW scenario"""
        with app.app_context():
            # Mock current period
            period = AgrarianPeriod.query.get('P4')
            mock_period.return_value = period
            
            # Mock favorable weather
            mock_weather.return_value = [{
                'date': '2024-03-15',
                'temp_min': 15.0,
                'temp_max': 25.0,
                'temp_avg': 20.0,
                'humidity': 60,
                'wind': 12.0,
                'rainfall': 0.0,
                'description': 'Clear'
            }]
            
            mock_ai.return_value = 'Good time to plant.'
            
            engine = DecisionEngine()
            result = engine.get_advice(test_farmer.id, test_crop.id, 'Tunis')
            
            assert 'decision' in result
            assert result['decision']['action'] in ['PLANT_NOW', 'WAIT']
            assert 'explanation' in result
    
    def test_analyze_weather_no_risks(self, app, test_crop):
        """Test weather analysis with no risks"""
        with app.app_context():
            engine = DecisionEngine()
            forecast = [{
                'date': '2024-03-15',
                'temp_min': 15.0,
                'temp_max': 25.0,
                'temp_avg': 20.0,
                'rainfall': 0.0
            }]
            
            analysis = engine._analyze_weather(forecast, test_crop.id)
            
            assert 'risks' in analysis
            assert len(analysis['risks']) == 0
            assert 'avg_temp' in analysis
    
    def test_analyze_weather_with_frost_risk(self, app, test_crop):
        """Test weather analysis with frost risk"""
        with app.app_context():
            engine = DecisionEngine()
            forecast = [{
                'date': '2024-03-15',
                'temp_min': 1.0,  # Below frost threshold
                'temp_max': 15.0,
                'temp_avg': 8.0,
                'rainfall': 0.0
            }]
            
            analysis = engine._analyze_weather(forecast, test_crop.id)
            
            assert len(analysis['risks']) > 0
            assert any(r['type'] == 'frost_risk' for r in analysis['risks'])
    
    def test_make_decision_forbidden_period(self, app):
        """Test decision for forbidden period"""
        with app.app_context():
            engine = DecisionEngine()
            
            # Create mock rule for forbidden period
            rule = type('obj', (object,), {
                'suitability': 'forbidden',
                'reason': 'Too hot for this crop'
            })()
            
            weather_analysis = {'risks': [], 'avg_temp': 25.0}
            
            decision = engine._make_decision(rule, weather_analysis)
            
            assert decision['action'] == 'NOT_RECOMMENDED'
            assert decision['confidence'] == 'HIGH'
    
    def test_make_decision_optimal_no_risks(self, app):
        """Test decision for optimal period with no risks"""
        with app.app_context():
            engine = DecisionEngine()
            
            rule = type('obj', (object,), {
                'suitability': 'optimal',
                'reason': 'Perfect conditions'
            })()
            
            weather_analysis = {'risks': [], 'avg_temp': 20.0}
            
            decision = engine._make_decision(rule, weather_analysis)
            
            assert decision['action'] == 'PLANT_NOW'
            assert decision['confidence'] == 'HIGH'