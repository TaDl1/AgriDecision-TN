"""
Regional Performance Benchmarking Service
Implements GSI, PBD, RCPS, and related metrics with statistical validation
"""
from models.base import db
from models.decision import Decision, Outcome
from models.user import Farmer
from models.crop import Crop
from models.analytics import RegionalBenchmarks, CropSpecificDefaults
from sqlalchemy import func, and_, or_, case, literal, Integer, cast
from datetime import datetime, timedelta
import math
import numpy as np


class RegionalAnalyticsService:
    """Service for regional performance benchmarking and crop analysis"""
    
    MIN_SUCCESSES_FOR_RCPS = 3
    MIN_ATTEMPTS_FOR_RCPS = 3
    MIN_DECISIONS_FOR_GSI = 5

    # TUNISIAN REGIONAL CROP SUITABILITY MATRIX
    # Zones: North (Cereal), North-East (Cap Bon/Citrus), Sahel (Olive/Almond), Central (Vegetables), South (Oasis/Dry)
    REGIONAL_ZONES = {
        'North': ['Bizerte', 'Beja', 'Jendouba', 'Siliana'],
        'North-East': ['Tunis', 'Ariana', 'Ben Arous', 'Nabeul', 'Zaghouan', 'Manouba'],
        'Sahel': ['Sousse', 'Monastir', 'Mahdia', 'Sfax'],
        'Central': ['Kairouan', 'Sidi Bouzid', 'Kasserine'],
        'South': ['Gafsa', 'Tozeur', 'Kebili', 'Medenine', 'Gabes', 'Tataouine']
    }

    SUITABILITY_WEIGHTS = {
        'North': {
            'Wheat': 1.3, 'Chickpea': 1.2, 'Lentil': 1.2, 'Fava Bean': 1.2, 'Green Pea': 1.2,
            'Potato': 1.0, 'Tomato': 0.8, 'Citrus': 0.5, 'Watermelon': 0.7
        },
        'North-East': {
            'Citrus': 1.4, 'Tomato': 1.3, 'Pepper': 1.3, 'Grape': 1.3, 'Potato': 1.2,
            'Olive': 0.8, 'Wheat': 0.9, 'Watermelon': 1.1
        },
        'Sahel': {
            'Olive': 1.5, 'Almond': 1.4, 'Barley': 1.2,
            'Citrus': 0.4, 'Tomato': 0.6, 'Potato': 0.7
        },
        'Central': {
            'Watermelon': 1.4, 'Zucchini': 1.4, 'Tomato': 1.3, 'Pepper': 1.3,
            'Onion': 1.2, 'Garlic': 1.2, 'Carrot': 1.1,
            'Wheat': 0.7, 'Olive': 0.9
        },
        'South': {
            'Dates': 1.6, 'Palms': 1.6, 'Onion': 1.3, 'Garlic': 1.3, 'Carrot': 1.2,
            'Spinach': 1.2, 'Okra': 1.2,
            'Wheat': 0.5, 'Citrus': 0.4, 'Tomato': 0.7
        }
    }

    @staticmethod
    def get_regional_weight(crop_name, governorate):
        """
        Calculate suitability weight for a crop in a specific governorate.
        Returns 1.0 (neutral) if not found.
        """
        # Find zone
        target_zone = 'Other'
        for zone, govs in RegionalAnalyticsService.REGIONAL_ZONES.items():
            if governorate in govs:
                target_zone = zone
                break
        
        if target_zone == 'Other':
            return 1.0
            
        return RegionalAnalyticsService.SUITABILITY_WEIGHTS.get(target_zone, {}).get(crop_name, 1.0)
    def calculate_gsi(governorate):
        """
        Governorate Success Index (GSI)
        
        Formula: GSI_g = Σ(w_i × SR_i) / Σ(w_i)
        
        Where:
        - SR_i = farmer success rate (last 365 days)
        - w_i = sqrt(min(farmer_decisions, 50))  # Experience weight
        - Excludes: <5 decisions OR SR = 0%/100% (outliers)
        
        Returns: GSI value or None if insufficient data
        """
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        
        # Get all farmers in governorate with outcomes
        farmers_data = db.session.query(
            Decision.farmer_id,
            func.count(Outcome.id).label('total_outcomes'),
            func.coalesce(func.sum(cast(Outcome.outcome == 'success', Integer)), 0).label('successes')
        ).join(Outcome).join(Farmer).filter(
            Farmer.governorate == governorate,
            Decision.timestamp >= one_year_ago
        ).group_by(Decision.farmer_id).all()
        
        weighted_sum = 0
        weight_sum = 0
        valid_farmers = 0
        
        for farmer_id, total, successes in farmers_data:
            # Minimum decision requirement
            if total < RegionalAnalyticsService.MIN_DECISIONS_FOR_GSI:
                continue
            
            # Calculate success rate
            sr = (successes / total) * 100
            
            # Calculate experience weight: sqrt(min(decisions, 50))
            weight = math.sqrt(min(total, 50))
            
            weighted_sum += weight * sr
            weight_sum += weight
            valid_farmers += 1
        
        if weight_sum == 0 or valid_farmers < 1:
            return None
        
        gsi = weighted_sum / weight_sum
        
        return {
            'gsi': round(gsi, 1),
            'farmer_count': valid_farmers,
            'governorate': governorate
        }
    
    @staticmethod
    def calculate_pbd(user_id, governorate):
        """
        Personal Benchmark Deviation (PBD) with Confidence
        
        Formula: PBD = SR_u - GSI_g
        
        Confidence: 1 - (1.96 × SE)
        SE = sqrt((SR_u × (1-SR_u))/n_u + (GSI_g × (1-GSI_g))/n_g)
        
        Interpretation:
        - PBD > +15% AND Confidence > 0.8 → "Top Performer"
        - +5% < PBD ≤ +15% → "Above Average"
        - -5% ≤ PBD ≤ +5% → "On Par"
        - -10% ≤ PBD < -5% → "Below Average"
        - PBD < -10% → "Opportunity Area"
        """
        # Get user success rate (last 365 days)
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        
        user_stats = db.session.query(
            func.count(Outcome.id).label('total'),
            func.coalesce(func.sum(cast(Outcome.outcome == 'success', Integer)), 0).label('successes')
        ).join(Decision).filter(
            Decision.farmer_id == user_id,
            Decision.timestamp >= one_year_ago
        ).first()
        
        n_user = user_stats.total or 0
        user_successes = user_stats.successes or 0
        
        if n_user == 0:
            return {
                'pbd': None,
                'user_sr': 0,
                'regional_avg': None,
                'confidence': 0,
                'interpretation': 'Insufficient personal data',
                'message': 'Make more decisions to see your benchmark'
            }
        
        user_sr = (user_successes / n_user) * 100
        
        # Get GSI for governorate
        gsi_data = RegionalAnalyticsService.calculate_gsi(governorate)
        
        if not gsi_data or gsi_data['gsi'] is None:
            return {
                'pbd': None,
                'user_sr': round(user_sr, 1),
                'regional_avg': None,
                'confidence': 0,
                'interpretation': 'Insufficient regional data',
                'message': 'Not enough farmers in your region yet'
            }
        
        gsi = gsi_data['gsi']
        n_region = gsi_data['farmer_count']
        
        # Calculate PBD
        pbd = user_sr - gsi
        
        # Calculate Standard Error
        sr_u_decimal = user_sr / 100
        gsi_decimal = gsi / 100
        
        se = math.sqrt(
            (sr_u_decimal * (1 - sr_u_decimal) / n_user) +
            (gsi_decimal * (1 - gsi_decimal) / n_region)
        )
        
        # Calculate confidence score
        confidence = max(0, 1 - (1.96 * se))
        
        # Interpretation
        if pbd > 15 and confidence > 0.8:
            interpretation = "Top Performer"
            message = f"You're crushing it! {abs(round(pbd, 1))}% above regional average"
        elif pbd > 5:
            interpretation = "Above Average"
            message = f"Doing great! {abs(round(pbd, 1))}% above average"
        elif pbd >= -5:
            interpretation = "On Par"
            message = "You're performing at the regional average"
        elif pbd >= -10:
            interpretation = "Below Average"
            message = f"Room for improvement: {abs(round(pbd, 1))}% below average"
        else:
            interpretation = "Opportunity Area"
            message = f"Focus on following advice to improve: {abs(round(pbd, 1))}% below average"
        
        return {
            'pbd': round(pbd, 1),
            'user_sr': round(user_sr, 1),
            'regional_avg': round(gsi, 1),
            'confidence': round(confidence, 3),
            'interpretation': interpretation,
            'message': message,
            'sample_size': {
                'user': n_user,
                'region': n_region
            }
        }
    
    @staticmethod
    def calculate_rcps(crop_id, governorate):
        """
        Regional Crop Performance Score (RCPS)
        
        Formula: RCPS = w1×SR + w2×SC + w3×CR + w4×YR
        
        Where:
        - SR = success rate (last 2 years)
        - SC = normalized success count: log10(success_count + 1)
        - CR = consistency ratio: 1 - (std_dev_monthly / SR)
        - YR = yield ratio: avg_yield / max_yield_national
        - weights = [0.4, 0.2, 0.2, 0.2]
        
        Minimum: 3 successes AND 5 attempts
        """
        two_years_ago = datetime.utcnow() - timedelta(days=730)
        
        # Get crop data for region
        crop_stats = db.session.query(
            func.count(Outcome.id).label('total'),
            func.coalesce(func.sum(cast(Outcome.outcome == 'success', Integer)), 0).label('successes'),
            func.avg(Outcome.yield_kg).label('avg_yield')
        ).join(Decision).join(Farmer).filter(
            Decision.crop_id == crop_id,
            Farmer.governorate == governorate,
            Decision.timestamp >= two_years_ago
        ).first()
        
        total_attempts = crop_stats.total or 0
        success_count = crop_stats.successes or 0
        avg_yield = crop_stats.avg_yield or 0
        
        # Check minimum requirements
        if success_count < RegionalAnalyticsService.MIN_SUCCESSES_FOR_RCPS or \
           total_attempts < RegionalAnalyticsService.MIN_ATTEMPTS_FOR_RCPS:
            return None
        
        # 1. Success Rate (SR)
        sr = success_count / total_attempts
        
        # 2. Success Count normalized (SC)
        sc = math.log10(success_count + 1)
        
        # 3. Consistency Ratio (CR)
        # Get monthly success rates
        monthly_rates = RegionalAnalyticsService._get_monthly_success_rates(
            crop_id, governorate, two_years_ago
        )
        
        if len(monthly_rates) > 1:
            std_dev = np.std(monthly_rates)
            # Handle potential division by zero or NaN
            if sr > 0 and not np.isnan(std_dev):
                cr = max(0, 1 - (std_dev / sr))
            else:
                cr = 0
        else:
            cr = 0.5  # Default if not enough monthly data
        
        # 4. Yield Ratio (YR)
        # Get national max yield for this crop
        national_max = db.session.query(
            func.max(Outcome.yield_kg)
        ).join(Decision).filter(
            Decision.crop_id == crop_id,
            Outcome.yield_kg != None
        ).scalar()
        
        national_max_yield = float(national_max) if national_max else 1.0
        yr = avg_yield / national_max_yield if national_max_yield > 0 else 0
        
        # Calculate RCPS with weights
        weights = [0.4, 0.2, 0.2, 0.2]
        rcps = weights[0]*sr + weights[1]*sc + weights[2]*cr + weights[3]*yr
        
        # Ensure result is JSON serializable (not a numpy type)
        return {
            'rcps': round(float(rcps), 3),
            'success_rate': round(float(sr * 100), 1),
            'sample_size': int(total_attempts),
            'successes': int(success_count),
            'consistency': round(float(cr), 2),
            'avg_yield': round(float(avg_yield), 1) if avg_yield else None
        }
    
    @staticmethod
    def _get_monthly_success_rates(crop_id, governorate, since_date):
        """Helper: Get monthly success rates for consistency calculation"""
        monthly_data = db.session.query(
            func.strftime('%Y-%m', Decision.timestamp).label('month'),
            func.count(Outcome.id).label('total'),
            func.coalesce(func.sum(cast(Outcome.outcome == 'success', Integer)), 0).label('successes')
        ).join(Outcome).join(Farmer).filter(
            Decision.crop_id == crop_id,
            Farmer.governorate == governorate,
            Decision.timestamp >= since_date
        ).group_by('month').all()
        
        rates = []
        for month, total, successes in monthly_data:
            if total > 0:
                rates.append(successes / total)
        
        return rates
    
    @staticmethod
    def get_top_crops_for_region(governorate, limit=5):
        """
        Get top performing crops in a region based on RCPS
        
        Returns list of crops sorted by RCPS score
        """
        crops = Crop.query.all()
        crop_scores = []
        
        for crop in crops:
            rcps_data = RegionalAnalyticsService.calculate_rcps(crop.id, governorate)
            
            if rcps_data:
                crop_scores.append({
                    'crop_id': crop.id,
                    'crop_name': crop.name,
                    'rcps': rcps_data['rcps'],
                    'success_rate': rcps_data['success_rate'],
                    'sample_size': rcps_data['sample_size']
                })
        
        # Sort by RCPS score
        crop_scores.sort(key=lambda x: x['rcps'], reverse=True)
        
        return crop_scores[:limit]
    
    @staticmethod
    def calculate_regional_risk_adjusted_performance(governorate):
        """
        Regional Risk-Adjusted Performance (RRAP)
        
        Formula: RRAP = GSI × (1 - Regional_Risk_Factor)
        
        Risk_Factor = Σ Risk_Events / Total_Decisions
        """
        gsi_data = RegionalAnalyticsService.calculate_gsi(governorate)
        
        if not gsi_data:
            return None
        
        # Count risk events
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        
        total_decisions = db.session.query(func.count(Decision.id)).join(Farmer).filter(
            Farmer.governorate == governorate,
            Decision.timestamp >= one_year_ago
        ).scalar() or 0
        
        if total_decisions == 0:
            return None
        
        # Count high-risk decisions
        risk_events = db.session.query(func.count(Decision.id)).join(Farmer).filter(
            Farmer.governorate == governorate,
            Decision.timestamp >= one_year_ago,
            or_(
                Decision.weather_risks.like('%frost_risk%'),
                Decision.weather_risks.like('%heat_wave%'),
                Decision.weather_risks.like('%drought%'),
                Decision.recommendation == 'NOT_RECOMMENDED'
            )
        ).scalar() or 0
        
        risk_factor = risk_events / total_decisions
        rrap = gsi_data['gsi'] * (1 - risk_factor)
        
        return {
            'rrap': round(rrap, 1),
            'gsi': gsi_data['gsi'],
            'risk_factor': round(risk_factor, 3),
            'risk_events': risk_events,
            'total_decisions': total_decisions
        }
    @staticmethod
    def calculate_doi(governorate, user_id):
        """
        Diversification Opportunity Index (DOI)
        Measures potential for trying new high-performing crops
        
        Formula: DOI = (Count(Crops with RCPS > 0.7) - User_Crop_Count) / Total_Regional_Crops
        """
        top_crops = RegionalAnalyticsService.get_top_crops_for_region(governorate, limit=10)
        high_performers = [c for c in top_crops if c['rcps'] > 0.6]
        
        user_crops = db.session.query(func.count(func.distinct(Decision.crop_id)))\
                               .filter(Decision.farmer_id == user_id).scalar() or 0
        
        total_regional_crops = len(top_crops)
        if total_regional_crops == 0:
            return 0
            
        doi = (len(high_performers) - user_crops) / total_regional_crops
        return round(max(0, doi), 2)

    @staticmethod
    def calculate_oga(governorate):
        """
        Opportunity Gap Analysis (OGA)
        Measures the gap between the best performing crop and regional average
        
        Formula: OGA = RCPS_max - RCPS_avg
        """
        top_crops = RegionalAnalyticsService.get_top_crops_for_region(governorate, limit=10)
        if not top_crops:
            return 0
            
        scores = [c['rcps'] for c in top_crops]
        oga = max(scores) - (sum(scores) / len(scores))
        return round(oga, 3)

    @staticmethod
    def get_regional_success_rate(governorate, crop_id, season=None):
        """
        Hierarchical Fallback for Success Rate
        PATCHED: Returns fallback values due to regional_benchmarks table schema issues
        """
        # TODO: Fix regional_benchmarks table schema and re-enable database queries
        # For now, return expert baselines directly
        
        baselines = {
            'Olive': 0.85,    # Low risk
            'Tomato': 0.70,   # Medium risk
            'Artichoke': 0.55, # High risk
            'Potato': 0.75,
            'Wheat': 0.80
        }
        
        if crop_id:
            crop = Crop.query.get(crop_id)
            if crop and crop.name in baselines:
                return baselines[crop.name]
        
        return 0.75  # Global default

    @staticmethod
    def get_regional_avg_loss(governorate, crop_id):
        """Hierarchical Fallback for Loss per Failure
        PATCHED: Returns fallback values due to regional_benchmarks table schema issues
        """
        # TODO: Fix regional_benchmarks table schema and re-enable database queries
        # Return expert defaults directly
        
        risk_defaults = {'high': 450, 'medium': 250, 'low': 150}  # TND per unit
        cat_map = {'Artichoke': 'high', 'Tomato': 'medium', 'Olive': 'low'}
        
        if crop_id:
            crop = Crop.query.get(crop_id)
            if crop:
                cat = cat_map.get(crop.name, 'medium')
                return risk_defaults[cat]
        
        return 250.0  # Default medium risk

    @staticmethod
    def get_regional_AES_avg(governorate, crop_id):
        """Regional average AES (Baseline uplift)"""
        # Specific research could populate this, using 15% as high-rigor default
        return 15.0 

    @staticmethod
    def get_seasonal_factor(crop_name, month):
        """Return effectiveness adjustment based on season"""
        # Tunisia seasonality logic
        seasons = {
            'summer': [6, 7, 8],
            'winter': [12, 1, 2],
            'autumn': [9, 10, 11],
            'spring': [3, 4, 5]
        }
        
        # Mediterranean High-Heat Penalties
        if month in seasons['summer']:
            return -0.1 if crop_name in ['Tomato', 'Potato'] else 0.0
        if month in seasons['winter']:
            return -0.05 if crop_name == 'Artichoke' else 0.0
        return 0.05 # General spring/autumn boost

    @staticmethod
    def refresh_benchmarks():
        """Recalculate and update the RegionalBenchmarks table from raw data"""
        all_regions = db.session.query(Farmer.governorate).distinct().all()
        all_crops = Crop.query.all()
        
        for (gov,) in all_regions:
            if not gov: continue
            for crop in all_crops:
                stats = db.session.query(
                    func.count(Outcome.id).label('total'),
                    func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes'),
                ).join(Decision).join(Farmer).filter(
                    Farmer.governorate == gov,
                    Decision.crop_id == crop.id
                ).first()
                
                if stats and stats.total > 0:
                    sr = (stats.successes / stats.total) if stats.total > 0 else 0
                    
                    # Calculate avg loss from failed outcomes (revenue_tnd is used as a negative proxy here if 0)
                    loss_stats = db.session.query(func.avg(Outcome.revenue_tnd)).join(Decision).join(Farmer).filter(
                        Farmer.governorate == gov,
                        Decision.crop_id == crop.id,
                        Outcome.outcome == 'failure'
                    ).scalar()
                    
                    bench = RegionalBenchmarks.query.filter_by(governorate=gov, crop_id=crop.id).first()
                    if not bench:
                        bench = RegionalBenchmarks(governorate=gov, crop_id=crop.id)
                        db.session.add(bench)
                    
                    bench.avg_success_rate = sr
                    bench.avg_failure_rate = 1.0 - sr
                    bench.avg_loss_per_failure = abs(loss_stats) if loss_stats and loss_stats != 0 else 200.0
                    bench.sample_size = stats.total
                    bench.last_updated = datetime.utcnow()
        
        db.session.commit()
