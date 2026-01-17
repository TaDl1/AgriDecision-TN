"""
Advanced Analytics Service with Statistical Validation
Implements the 6 core metrics: AES, FCI, RAR, CVS, TLS, CSAA
"""
from models.base import db
from models.decision import Decision, Outcome
from models.crop import Crop, AgrarianPeriod
from models.user import Farmer
from sqlalchemy import func, case, and_
from datetime import datetime, timedelta
import math
import random


class AdvancedAnalyticsService:
    """Service for calculating statistically-validated analytics metrics"""
    
    # Minimum sample sizes for valid calculations
    MIN_SAMPLE_AES = 3
    MIN_SAMPLE_CSAA = 5
    MIN_MONTHS_TLS = 6
    MIN_SAMPLE_CVS = 10
    
    @staticmethod
    def calculate_aes(user_id):
        """
        Advice Effectiveness Score (AES)
        AES = SR_followed - SR_ignored
        
        Returns dict with AES, confidence interval, and validity
        """
        # Get followed decisions with outcomes
        followed = db.session.query(
            func.count(Outcome.id).label('total'),
            func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes')
        ).join(Decision, Outcome.decision_id == Decision.id).filter(
            Decision.farmer_id == user_id,
            Decision.advice_status == 'followed'
        ).first()
        
        # Get ignored decisions with outcomes
        ignored = db.session.query(
            func.count(Outcome.id).label('total'),
            func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes')
        ).join(Decision, Outcome.decision_id == Decision.id).filter(
            Decision.farmer_id == user_id,
            Decision.advice_status == 'ignored'
        ).first()
        
        n_followed = followed.total or 0
        n_ignored = ignored.total or 0
        s_followed = followed.successes or 0
        s_ignored = ignored.successes or 0
        
        # Check minimum sample size
        if n_followed < AdvancedAnalyticsService.MIN_SAMPLE_AES or n_ignored < AdvancedAnalyticsService.MIN_SAMPLE_AES:
            return {
                'aes': None,
                'sr_followed': round((s_followed / n_followed * 100), 1) if n_followed > 0 else 0,
                'sr_ignored': round((s_ignored / n_ignored * 100), 1) if n_ignored > 0 else 0,
                'valid': False,
                'message': f'Insufficient data (need {AdvancedAnalyticsService.MIN_SAMPLE_AES} followed and {AdvancedAnalyticsService.MIN_SAMPLE_AES} ignored decisions)',
                'n_followed': n_followed,
                'n_ignored': n_ignored
            }
        
        # Calculate success rates
        sr_followed = s_followed / n_followed
        sr_ignored = s_ignored / n_ignored
        
        # Calculate AES
        aes = (sr_followed - sr_ignored) * 100
        
        # Calculate 95% confidence interval
        ci = 1.96 * math.sqrt(
            (sr_followed * (1 - sr_followed) / n_followed) +
            (sr_ignored * (1 - sr_ignored) / n_ignored)
        ) * 100
        
        # Interpretation
        if aes > 15:
            interpretation = "Following advice significantly improves outcomes"
        elif aes > 5:
            interpretation = "Advice provides moderate benefit"
        elif aes > -5:
            interpretation = "Advice has minimal impact"
        else:
            interpretation = "System advice may need adjustment"
        
        return {
            'aes': round(aes, 1),
            'sr_followed': round(sr_followed * 100, 1),
            'sr_ignored': round(sr_ignored * 100, 1),
            'confidence_interval': round(ci, 1),
            'aes_range': [round(aes - ci, 1), round(aes + ci, 1)],
            'valid': True,
            'interpretation': interpretation,
            'n_followed': n_followed,
            'n_ignored': n_ignored
        }
    
    @staticmethod
    def calculate_fci(user_id):
        """
        Farmer Compliance Index (FCI)
        FCI = (followed_decisions / total_decisions) × 100
        """
        followed = Decision.query.filter_by(
            farmer_id=user_id,
            advice_status='followed'
        ).count()
        
        total = Decision.query.filter(
            Decision.farmer_id == user_id,
            Decision.advice_status.in_(['followed', 'ignored'])
        ).count()
        
        if total == 0:
            return {
                'fci': 0,
                'followed_count': 0,
                'total_count': 0,
                'message': 'No actions recorded yet'
            }
        
        fci = (followed / total) * 100
        
        # Interpretation
        if fci >= 80:
            interpretation = "High trust in system"
        elif fci >= 60:
            interpretation = "Moderate engagement"
        elif fci >= 40:
            interpretation = "Low compliance - consider reviewing advice quality"
        else:
            interpretation = "Very low compliance - system needs improvement"
        
        return {
            'fci': round(fci, 1),
            'followed_count': followed,
            'total_count': total,
            'interpretation': interpretation
        }
    
    @staticmethod
    def calculate_rar(user_id):
        """
        Risk Avoidance ROI (RAR)
        RAR = failures_prevented × avg_loss_per_failure
        """
        # Count WAIT recommendations that were followed
        wait_followed = Decision.query.filter_by(
            farmer_id=user_id,
            recommendation='WAIT',
            advice_status='followed'
        ).count()
        
        # Count WAIT recommendations that were ignored and resulted in failure
        wait_ignored_failures = db.session.query(func.count(Outcome.id)).join(
            Decision, Outcome.decision_id == Decision.id
        ).filter(
            Decision.farmer_id == user_id,
            Decision.recommendation == 'WAIT',
            Decision.advice_status == 'ignored',
            Outcome.outcome == 'failure'
        ).scalar() or 0
        
        # Calculate average loss per failure from historical data
        avg_loss = db.session.query(
            func.avg(Outcome.revenue_tnd)
        ).join(Decision, Outcome.decision_id == Decision.id).filter(
            Decision.farmer_id == user_id,
            Outcome.outcome == 'failure',
            Outcome.revenue_tnd != None
        ).scalar()
        
        # Use default if no historical loss data
        if not avg_loss:
            avg_loss = 200  # Default average loss in TND
        
        # Calculate ROI
        # Assumption: followed WAIT advice prevented similar failure rate
        if wait_followed > 0 and wait_ignored_failures > 0:
            failure_rate_when_ignored = wait_ignored_failures / Decision.query.filter_by(
                farmer_id=user_id,
                recommendation='WAIT',
                advice_status='ignored'
            ).count()
            
            estimated_failures_prevented = wait_followed * failure_rate_when_ignored
        else:
            # Conservative estimate: 30% failure prevention
            estimated_failures_prevented = wait_followed * 0.3
        
        rar = estimated_failures_prevented * abs(avg_loss)
        
        return {
            'rar': round(rar, 2),
            'wait_followed': wait_followed,
            'estimated_failures_prevented': round(estimated_failures_prevented, 1),
            'avg_loss_per_failure': round(abs(avg_loss), 2)
        }
    
    @staticmethod
    def calculate_cvs(user_id=None):
        """
        Confidence Validation Score (CVS)
        Validates decision engine's confidence scoring
        """
        # Calculate for all users if user_id not specified (system-wide metric)
        base_query = db.session.query(
            Decision.confidence,
            func.count(Outcome.id).label('total'),
            func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes')
        ).join(Outcome, Decision.id == Outcome.decision_id).filter(
            Decision.advice_status == 'followed'
        )
        
        if user_id:
            base_query = base_query.filter(Decision.farmer_id == user_id)
        
        results = base_query.group_by(Decision.confidence).all()
        
        cvs = {}
        for confidence, total, successes in results:
            if total >= AdvancedAnalyticsService.MIN_SAMPLE_CVS:
                sr = (successes / total) * 100
                cvs[confidence] = round(sr, 1)
        
        # Calculate calibration metric
        target_rates = {'HIGH': 85, 'MEDIUM': 70, 'LOW': 50}
        calibration = 0
        for conf, target in target_rates.items():
            if conf in cvs:
                calibration += abs(cvs[conf] - target)
        
        return {
            'cvs': cvs,
            'calibration_score': round(calibration, 1),
            'interpretation': 'Well-calibrated' if calibration < 15 else 'Needs calibration'
        }
    
    @staticmethod
    def calculate_tls(user_id):
        """
        Temporal Learning Slope (TLS)
        Measures improvement over time
        """
        # Get monthly success rates for last 12 months
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        
        # Query decisions grouped by month
        group_expr = func.strftime('%Y-%m', Decision.timestamp)
        monthly_data = db.session.query(
            group_expr.label('month'),
            func.count(Outcome.id).label('total'),
            func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes')
        ).join(Outcome, Decision.id == Outcome.decision_id).filter(
            Decision.farmer_id == user_id,
            Decision.advice_status == 'followed',
            Decision.timestamp >= twelve_months_ago
        ).group_by(group_expr).order_by(group_expr).all()
        
        if len(monthly_data) < AdvancedAnalyticsService.MIN_MONTHS_TLS:
            return {
                'tls': None,
                'valid': False,
                'message': f'Need at least {AdvancedAnalyticsService.MIN_MONTHS_TLS} months of data',
                'months_available': len(monthly_data)
            }
        
        # Calculate success rates
        months = []
        rates = []
        for i, (month, total, successes) in enumerate(monthly_data):
            if total > 0:
                months.append(i)
                rates.append((successes / total) * 100)
        
        # Simple linear regression
        n = len(months)
        if n < 2:
            return {'tls': None, 'valid': False, 'message': 'Insufficient data points'}
        
        sum_x = sum(months)
        sum_y = sum(rates)
        sum_xy = sum(x * y for x, y in zip(months, rates))
        sum_x2 = sum(x * x for x in months)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Calculate R²
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in rates)
        intercept = (sum_y - slope * sum_x) / n
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(months, rates))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Interpretation
        if slope > 2:
            interpretation = "Strong improvement trend"
        elif slope > 0.5:
            interpretation = "Moderate improvement"
        elif slope > -0.5:
            interpretation = "Stable performance"
        else:
            interpretation = "Declining performance - needs attention"
        
        return {
            'tls': round(slope, 2),
            'r_squared': round(r_squared, 3),
            'valid': True,
            'interpretation': interpretation,
            'months_analyzed': n,
            'current_rate': round(rates[-1], 1) if rates else 0,
            'starting_rate': round(rates[0], 1) if rates else 0,
            'trend_data': [{'month': m[0], 'rate': round((m[2]/m[1]*100), 1) if m[1]>0 else 0} for m in monthly_data]
        }
    
    @staticmethod
    def calculate_csaa(user_id):
        """
        Crop-Specific Advice Accuracy (CSAA)
        Identifies which crops have best advice accuracy
        """
        # Query per-crop success rates
        crop_data = db.session.query(
            Crop.name,
            func.count(Outcome.id).label('total'),
            func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes')
        ).join(Decision, Crop.id == Decision.crop_id).join(
            Outcome, Decision.id == Outcome.decision_id
        ).filter(
            Decision.farmer_id == user_id,
            Decision.advice_status == 'followed'
        ).group_by(Crop.name).all()
        
        csaa = {}
        for crop_name, total, successes in crop_data:
            if total >= AdvancedAnalyticsService.MIN_SAMPLE_CSAA:
                sr = (successes / total) * 100
                
                # Calculate statistical power
                statistical_power = 1 - (1 / math.sqrt(total))
                reliability_score = sr * statistical_power
                
                csaa[crop_name] = {
                    'success_rate': round(sr, 1),
                    'attempts': total,
                    'successes': successes,
                    'statistical_power': round(statistical_power, 3),
                    'reliability_score': round(reliability_score, 1)
                }
        
        # Sort by reliability score
        sorted_crops = sorted(csaa.items(), key=lambda x: x[1]['reliability_score'], reverse=True)
        
        return {
            'csaa': dict(sorted_crops),
            'best_crop': sorted_crops[0][0] if sorted_crops else None,
            'worst_crop': sorted_crops[-1][0] if sorted_crops else None,
            'chart_data': [{'crop': k, 'success_rate': v['success_rate'], 'reliability': v['reliability_score']} for k, v in sorted_crops]
        }

    @staticmethod
    def calculate_performance_trends(user_id):
        """
        Calculates success rate trends over time for visualization
        """
        # Get last 6 months of data
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        group_expr = func.strftime('%Y-%m', Decision.timestamp)
        data = db.session.query(
            group_expr.label('month'),
            func.count(Outcome.id).label('total'),
            func.sum(case((Outcome.outcome == 'success', 1), else_=0)).label('successes')
        ).join(Outcome, Decision.id == Outcome.decision_id).filter(
            Decision.farmer_id == user_id,
            Decision.advice_status == 'followed',
            Decision.timestamp >= six_months_ago
        ).group_by(group_expr).order_by(group_expr).all()
        
        return [
            {
                'month': row.month,
                'rate': round((row.successes / row.total * 100), 1) if row.total > 0 else 0,
                'total': row.total
            } for row in data
        ]

    @staticmethod
    def generate_smart_summary(user_id):
        """
        Generates a natural language interpretation of the farm's analytics.
        """
        from services.regional_analytics import RegionalAnalyticsService
        farmer = Farmer.query.get(user_id)
        if not farmer:
            return "Unable to retrieve farmer profile."

        aes = AdvancedAnalyticsService.calculate_aes(user_id)
        fci = AdvancedAnalyticsService.calculate_fci(user_id)
        pbd = RegionalAnalyticsService.calculate_pbd(user_id, farmer.governorate)
        csaa = AdvancedAnalyticsService.calculate_csaa(user_id)
        
        summary = []
        
        # Success Rate & Regional Comparison
        if pbd and pbd.get('pbd') is not None:
            val = pbd['pbd']
            if val > 10:
                summary.append(f"You are significantly outperforming the {farmer.governorate} regional average by {val}%. Your specialized techniques are yielding superior results.")
            elif val > 0:
                summary.append(f"Your performance is slightly above the regional average in {farmer.governorate}. You're on the right track.")
            else:
                summary.append(f"You are currently trailing the regional success rate by {abs(val)}%. There is a significant opportunity to optimize your planting timing based on local GSI benchmarks.")

        # Advice Effectiveness
        if aes.get('valid') and aes.get('aes') is not None:
            if aes['aes'] > 10:
                summary.append(f"The AgriDecision engine is providing a high 'Uplift' of +{aes['aes']}% to your success. Following system recommendations is your strongest lever for growth.")
            elif aes['aes'] < 0:
                summary.append("Your personal intuition is currently outperforming the system defaults. Consider recording more 'Ignored' outcomes to help us calibrate to your specific micro-climate.")

        # Compliance
        if fci.get('fci', 0) < 50:
            summary.append(f"Your compliance index is low ({fci['fci']}%). Trusting the system more consistently could help mitigate the common risks identified in {farmer.governorate}.")

        # Crop Accuracy
        best_crop = csaa.get('best_crop')
        if best_crop:
            summary.append(f"Technically, you are most proficient with {best_crop}. The data shows highest reliability for this crop in your specific soil conditions.")

        if not summary:
            return "Recording more outcomes will allow our 'Smart Advisor' to generate a detailed technical strategy for your farm."

        return " ".join(summary)

    @staticmethod
    def seed_user_simulation(user_id):
        """
        Seeds 100 sample data points for a user to simulate a mature account.
        """
        farmer = Farmer.query.get(user_id)
        crops = Crop.query.all()
        periods = AgrarianPeriod.query.all()
        
        if not crops or not periods:
            return False

        # Clear existing decisions if any to avoid mess
        for days_ago in range(180, 0, -2):
            ts = datetime.utcnow() - timedelta(days=days_ago)
            crop = random.choice(crops)
            reco = random.choice(['PLANT_NOW', 'WAIT'])
            
            decision = Decision(
                farmer_id=user_id,
                crop_id=crop.id,
                governorate=farmer.governorate,
                recommendation=reco,
                confidence=random.choice(['HIGH', 'MEDIUM']),
                explanation="Simulation data to demonstrate dashboard capabilities.",
                period_id=random.choice(periods).id,
                timestamp=ts,
                weather_temp_avg=random.uniform(15, 30),
                weather_humidity=random.uniform(40, 80),
                weather_rainfall=random.uniform(0, 50),
                weather_risks="[]",
                advice_status='followed' if random.random() > 0.2 else 'ignored',
                actual_action='planted_now' if reco == 'PLANT_NOW' else 'waited'
            )
            db.session.add(decision)
            db.session.flush()
            
            if decision.actual_action == 'planted_now':
                is_success = random.random() < 0.75
                outcome = Outcome(
                    decision_id=decision.id,
                    outcome='success' if is_success else 'failure',
                    yield_kg=random.uniform(500, 2000) if is_success else 100,
                    revenue_tnd=random.uniform(1000, 5000) if is_success else 50,
                    recorded_at=ts + timedelta(days=60)
                )
                db.session.add(outcome)
        
        db.session.commit()
        return True
