"""
Success Condition Analysis Service
Implements OCI, MFSP, and SPI formulas for advanced prescriptive analytics
"""
from models.base import db
from models.decision import Decision, Outcome
from sqlalchemy import func, case, and_
import math
import numpy as np
from services.small_sample_analytics import SmallSampleAnalytics
from services.regional_analytics import RegionalAnalyticsService


class SuccessConditionService:
    """Analyzes conditions that lead to success and predicts future performance"""
    ssa = SmallSampleAnalytics()
    regional = RegionalAnalyticsService()
    
    @staticmethod
    def calculate_oci(user_id=None, crop_id=None):
        """
        Optimal Condition Interpretation (OCI)
        Identifies the 'Sweet Spot' for environmental variables
        
        Formula: OCI_v = Median(v_success) ± (IQR(v_success) * 0.5)
        Variables: temp_avg, rainfall, humidity
        """
        query = db.session.query(
            Decision.weather_temp_avg,
            Decision.weather_rainfall,
            Decision.weather_humidity
        ).join(Outcome).filter(Outcome.outcome == 'success')
        
        if user_id:
            query = query.filter(Decision.farmer_id == user_id)
        if crop_id:
            query = query.filter(Decision.crop_id == crop_id)
            
        data = query.all()
        
        if len(data) < 3:
            return None
            
        results = {}
        var_names = ['temp', 'rainfall', 'humidity']
        
        for i, name in enumerate(var_names):
            values = [row[i] for row in data if row[i] is not None]
            if not values:
                continue
                
            median = np.median(values)
            q75, q25 = np.percentile(values, [75, 25])
            iqr = q75 - q25
            
            results[name] = {
                'optimal_value': round(float(median), 1),
                'range_min': round(float(median - iqr * 0.5), 1),
                'range_max': round(float(median + iqr * 0.5), 1),
                'iqr': round(float(iqr), 1)
            }
            
        return results

    @staticmethod
    def find_mfsp(user_id=None, governorate=None):
        """
        Most Frequent Success Pattern (MFSP)
        Identifies the combination of factors that most often leads to success
        
        Formula: MFSP = Mode({Crop_i, Period_j, Condition_k})
        """
        query = db.session.query(
            Decision.crop_id,
            Decision.period_id,
            func.count(Outcome.id).label('success_count')
        ).join(Outcome).filter(Outcome.outcome == 'success')
        
        if user_id:
            query = query.filter(Decision.farmer_id == user_id)
        if governorate:
            from models.user import Farmer
            query = query.join(Farmer).filter(Farmer.governorate == governorate)
            
        patterns = query.group_by(Decision.crop_id, Decision.period_id)\
                        .order_by(db.desc('success_count')).limit(3).all()
        
        if not patterns:
            return []
            
        from models.crop import Crop, AgrarianPeriod
        
        detailed_patterns = []
        for crop_id, period_id, count in patterns:
            crop = Crop.query.get(crop_id)
            period = AgrarianPeriod.query.get(period_id)
            
            detailed_patterns.append({
                'crop_name': crop.name if crop else "Unknown",
                'period_name': period.name if period else "Unknown",
                'success_count': count
            })
            
        return detailed_patterns

    @staticmethod
    def calculate_spi(user_id, target_crop_id, target_period_id, current_weather):
        """
        Success Predictive Index (SPI) with Regional Fallbacks and Bayesian Smoothing
        """
        # 1. Historical Personal Data
        hist_stats = db.session.query(
            func.count(Outcome.id).label('total'),
            func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes')
        ).join(Decision).filter(
            Decision.farmer_id == user_id,
            Decision.crop_id == target_crop_id
        ).first()
        
        n_personal = hist_stats.total or 0
        s_personal = hist_stats.successes or 0
        
        # 2. Regional/Default Data
        from models.user import Farmer
        farmer = Farmer.query.get(user_id)
        governorate = farmer.governorate if farmer else "Tunis"
        
        reg_sr = SuccessConditionService.regional.get_regional_success_rate(governorate, target_crop_id)
        
        # 3. Optimal Conditions (OCI)
        oci = SuccessConditionService.calculate_oci(crop_id=target_crop_id)
        # Fallback to defaults if no OCI
        if not oci:
            from models.analytics import CropSpecificDefaults
            defaults = CropSpecificDefaults.query.filter_by(crop_id=target_crop_id).first()
            if defaults and defaults.optimal_temp_range:
                try:
                    t_min, t_max = map(float, defaults.optimal_temp_range.split('-'))
                    oci = {'temp': {'optimal_value': (t_min + t_max)/2, 'iqr': t_max - t_min}}
                except: pass

        # 4. Use Centralized Logic
        spi_results = SuccessConditionService.ssa.calculate_spi(
            n_personal, s_personal, 
            current_weather, 
            {'success_rate': reg_sr, 'n': 20},
            oci
        )
        
        return spi_results
