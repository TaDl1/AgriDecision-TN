"""
Analytics Service for Prescriptive Insights
"""
import logging
import numpy as np
from datetime import datetime, timedelta
import random       # Imported random
from collections import defaultdict
from sqlalchemy import func, cast, Integer, case, desc, and_
from models.base import db
from models.decision import Decision, Outcome
from models.user import Farmer
from models.crop import Crop, AgrarianPeriod
from services.small_sample_analytics import SmallSampleAnalytics
from services.regional_analytics import RegionalAnalyticsService

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Advanced Analytics Calculation Engine
    Implements AES, FCI, RAR, TLS, and Regional Benchmarks
    """
    
    def __init__(self):
        self.ssa = SmallSampleAnalytics()
        self.regional = RegionalAnalyticsService()
    def get_dashboard_data(self, farmer_id: int, timeframe: str = 'monthly'):
        """
        Refined Analytics Pipeline with Expert Logic:
        1. Multi-Tier Sufficiency Check
        2. Wilson-CI for all proportions
        3. Farm Size Normalization for RAR
        4. Brier Score Calibration for Confidence
        """
        try:
            farmer = Farmer.query.get(farmer_id)
            if not farmer: return {"error": "Farmer not found"}
            
            # 1. Gather all raw data
            personal_stats = self._get_personal_stats(farmer_id)
            aes_raw = self._get_aes_raw_data(farmer_id)
            rar_raw = self._get_rar_raw_data(farmer_id)
            trends_raw = self.calculate_performance_trends(farmer_id, timeframe)
            cvs_raw = self._get_cvs_raw_data(farmer_id)
            
            # 2. Get Regional Fallbacks (Improved hierarchy)
            reg_sr = self.regional.get_regional_success_rate(farmer.governorate, None)
            reg_aes = self.regional.get_regional_AES_avg(farmer.governorate, None)
            reg_loss = self.regional.get_regional_avg_loss(farmer.governorate, None)
            
            # 3. Calculate metrics using unified SSA engine
            aes_results = self.calculate_aes(farmer_id)
            rar_results = self.calculate_rar(farmer_id)
            cvs_results = self.ssa.calculate_cvs(cvs_raw['predictions'], cvs_raw['outcomes'])
            
            drs = self.ssa.calculate_drs(
                personal_stats['total_decisions'],
                len(trends_raw['data']),
                self._get_days_since_last_decision(farmer_id),
                0.8 # Completeness
            )
            
            # 4. Gather Derived Insights
            fci_full = self.calculate_fci(farmer_id)
            crop_acc = self.calculate_crop_accuracy(farmer_id)
            sweet_spot = self.calculate_environmental_sweet_spot(farmer_id)
            benchmarks = self.calculate_regional_benchmarks(farmer_id)
            
            strategic_advice = self._generate_strategic_advice(
                farmer_id, benchmarks, trends_raw, aes_results, rar_results, farmer.governorate
            )
            
            smart_summary = self._generate_smart_summary_v3(aes_results, drs, cvs_results)

            # 5. Build Structured, Non-Redundant Response
            response = {
                # --- PILLARS (Canonical Objects) ---
                "production": {
                    "success_rate": personal_stats['success_rate'],
                    "reliability_tier": self.ssa.get_reliability_tier(drs),
                    "data_sufficiency": drs,
                    "crop_performance": crop_acc['chart_data'],
                    "regional_comparison": benchmarks
                },
                "financial": {
                    "total_saved_tnd": rar_results['total_saved_tnd'],
                    "risks_avoided": rar_results['risks_avoided'],
                    "compliance": fci_full,
                    "interpretation": rar_results['interpretation']
                },
                "growth": {
                    "advice_uplift": aes_results,
                    "calibration": cvs_results,
                    "trends": trends_raw
                },
                "strategy": strategic_advice,
                
                # --- EXECUTIVE SUMMARY ---
                "executive_summary": {
                    "success_rate": personal_stats['success_rate'],
                    "total_saved": rar_results['total_saved_tnd'],
                    "data_reliability": drs,
                    "smart_summary": smart_summary
                },

                # --- FRONTEND COMPATIBILITY (Flat keys pointing to canonical data) ---
                "success_rate": personal_stats['success_rate'],
                "savings_tnd": rar_results['total_saved_tnd'],
                "risk_avoided_count": rar_results['risks_avoided'],
                "interpretation": rar_results['interpretation'],
                "performance_trends": trends_raw.get('data', []),
                "performance_trends_interpretation": trends_raw.get('interpretation', ''),
                "advice_effectiveness_score": aes_results,
                "crop_accuracy": crop_acc,
                "regional_data": benchmarks,
                "personal_insights": sweet_spot,
                "smart_summary": smart_summary,
                "strategic_advice": strategic_advice,
                "total_decisions": personal_stats['total_decisions'],
                "outcome_count": personal_stats['outcome_count']
            }
            return response
        except Exception as e:
            logger.error(f"Dashboard analytics error: {e}", exc_info=True)
            return {
                "error": str(e),
                "success_rate": 0,
                "performance_trends": []
            }

    def calculate_performance_trends(self, farmer_id: int, timeframe: str = 'monthly'):
        """
        Calculate success rate trends over time with dynamic grouping
        """
        # Determine grouping format and window
        now = datetime.utcnow()
        if timeframe == 'daily':
            date_format = '%Y-%m-%d'
            start_date = now - timedelta(days=30)
            label_format = lambda d: d.strftime('%d %b') # 05 Jan
        elif timeframe == 'weekly':
            date_format = '%Y-%W'
            start_date = now - timedelta(weeks=12)
            label_format = lambda d: f"W{d.strftime('%W')}" # W01
        elif timeframe == 'quarterly':
            # SQLite doesn't have direct quarter function, use case/strftime mapping or simple grouping
            date_format = 'Q' # Placeholder
            start_date = now - timedelta(days=365)
            # Custom label logic below
        elif timeframe == 'agrarian':
            date_format = 'P'
            start_date = now - timedelta(days=365)
            # Custom logic
        else: # monthly
            date_format = '%Y-%m'
            start_date = now - timedelta(days=365)
            label_format = lambda d: d.strftime('%b %Y') # Jan 2026
            
        # Specific query for quarterly if needed, or generic
        if timeframe == 'quarterly':
            # SQLite specific for Quarter: (strftime('%m', date) + 2) / 3
            # Use DISTINCT to avoid duplicates if raw data has overlapping join results
            results = db.session.query(
                func.strftime('%Y', Outcome.recorded_at).label('year'),
                ((func.cast(func.strftime('%m', Outcome.recorded_at), Integer) + 2) / 3).label('quarter'),
                func.avg(cast(Outcome.outcome == 'success', Integer))
            ).join(Decision).filter(
                Decision.farmer_id == farmer_id,
                Outcome.recorded_at >= start_date
            ).group_by('year', 'quarter').order_by('year', 'quarter').all()
            
            data = []
            seen_periods = set()
            for r in results:
                period_label = f"Q{int(r[1])} {r[0]}"
                if period_label in seen_periods: continue
                seen_periods.add(period_label)
                
                data.append({
                    'period': period_label,
                    'raw_date': f"{r[0]}-{r[1]}",
                    'rate': round(r[2] * 100, 1)
                })
        elif timeframe == 'agrarian':
            # Use Python-side bucketing for robust agrarian period mapping
            # 1. Fetch all outcomes with dates
            results = db.session.query(
                Outcome.recorded_at,
                cast(Outcome.outcome == 'success', Integer)
            ).join(Decision).filter(
                Decision.farmer_id == farmer_id,
                Outcome.recorded_at >= start_date
            ).all()

            # 2. Define or Fetch Periods (Fallback included)
            # Try to fetch from DB, fallback to hardcoded if empty
            periods_db = AgrarianPeriod.query.all()
            periods = []
            if periods_db:
                periods = [p.to_dict() for p in periods_db]
            else:
                # Fallback: Standard Tunisian Agrarian Calendar
                # Note: This is an approximation of the traditional Julian-based calendar
                periods = [
                    {'name': 'El Llayeli El Bidh', 'start_month': 12, 'start_day': 25, 'end_month': 1, 'end_day': 13},
                    {'name': 'El Llayeli Essoud', 'start_month': 1, 'start_day': 14, 'end_month': 2, 'end_day': 2},
                    {'name': 'El Azara', 'start_month': 2, 'start_day': 3, 'end_month': 2, 'end_day': 13},
                    {'name': 'Guerret El Anz', 'start_month': 2, 'start_day': 14, 'end_month': 2, 'end_day': 19},
                    {'name': 'Nezoul Jamrat El Hawa', 'start_month': 2, 'start_day': 20, 'end_month': 2, 'end_day': 26},
                    {'name': 'Nezoul Jamrat El Ma', 'start_month': 2, 'start_day': 27, 'end_month': 3, 'end_day': 9},
                    {'name': 'Nezoul Jamrat El Thra', 'start_month': 3, 'start_day': 6, 'end_month': 3, 'end_day': 10}, # Overlaps slightly, using standard
                    {'name': 'El Hassoum', 'start_month': 3, 'start_day': 10, 'end_month': 3, 'end_day': 17},
                    {'name': 'Equinox Spring', 'start_month': 3, 'start_day': 20, 'end_month': 5, 'end_day': 29}, # Generic Spring
                    {'name': 'El Hamsin', 'start_month': 4, 'start_day': 28, 'end_month': 6, 'end_day': 16},
                    {'name': 'Awussu', 'start_month': 7, 'start_day': 25, 'end_month': 9, 'end_day': 2},
                ]

            # 3. Bucket Outcomes
            period_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'order': 999})
            
            for r in results:
                date = r[0]
                is_success = r[1]
                month = date.month
                day = date.day
                
                # Find matching period
                matched_period = "Other"
                order = 999
                
                for idx, p in enumerate(periods):
                    # Check date range (handles year wrap roughly, but most are within-year or across Dec-Jan)
                    # Simplified check:
                    matches = False
                    if p['start_month'] == p['end_month']:
                        if month == p['start_month'] and p['start_day'] <= day <= p['end_day']: matches = True
                    elif p['start_month'] < p['end_month']:
                         if (month == p['start_month'] and day >= p['start_day']) or \
                            (month == p['end_month'] and day <= p['end_day']) or \
                            (p['start_month'] < month < p['end_month']): matches = True
                    else: # Wrap around year (Dec to Jan)
                         if (month == p['start_month'] and day >= p['start_day']) or \
                            (month == p['end_month'] and day <= p['end_day']) or \
                            (month > p['start_month']) or \
                            (month < p['end_month']): matches = True
                    
                    if matches:
                        matched_period = p['name']
                        order = idx
                        break
                
                period_stats[matched_period]['total'] += 1
                period_stats[matched_period]['success'] += is_success
                period_stats[matched_period]['order'] = min(period_stats[matched_period]['order'], order)

            # 4. Format Output
            # Sort by calendar order
            sorted_stats = sorted(period_stats.items(), key=lambda x: x[1]['order'])
            
            data = []
            for name, stats in sorted_stats:
                if stats['total'] > 0:
                    rate = (stats['success'] / stats['total']) * 100
                    data.append({
                        'period': name,
                        'raw_date': name,
                        'rate': round(rate, 1)
                    })
        else:
            results = db.session.query(
                func.strftime(date_format, Outcome.recorded_at).label('period'),
                func.avg(cast(Outcome.outcome == 'success', Integer))
            ).join(Decision).filter(
                Decision.farmer_id == farmer_id,
                Outcome.recorded_at >= start_date
            ).group_by('period').order_by('period').all()
            
            data = []
            for r in results:
                # Parse date for friendly label
                try:
                    if timeframe == 'daily':
                        dt = datetime.strptime(r[0], '%Y-%m-%d')
                        label = label_format(dt)
                    elif timeframe == 'weekly':
                        dt = datetime.strptime(r[0] + '-1', '%Y-%W-%w')
                        label = label_format(dt)
                    else:
                        dt = datetime.strptime(r[0], '%Y-%m')
                        label = label_format(dt)
                except:
                    label = r[0]
                    
                data.append({
                    'period': label, # For display
                    'raw_date': r[0],
                    'rate': round(r[1] * 100, 1)
                })
            
        # Slope Calculation
        slope = 0
        if len(data) >= 2:
            y = [d['rate'] for d in data]
            x = range(len(y))
            n = len(x)
            denominator = (n*sum(i**2 for i in x) - sum(x)**2)
            if denominator != 0:
                slope = (n * sum(i*j for i,j in zip(x,y)) - sum(x)*sum(y)) / denominator
            
        # Interpretation
        if slope > 0.5: interpretation = "Rapidly improving performance efficiency."
        elif slope > 0.1: interpretation = "Steady positive improvement trend."
        elif slope > -0.1: interpretation = "stable and consistent performance."
        elif slope > -0.5: interpretation = "Slight downward trend detected."
        else: interpretation = "Significant performance drop needing attention."
            
        return {'data': data, 'slope': round(slope, 2), 'interpretation': interpretation}

    def _get_personal_stats(self, farmer_id):
        decisions = Decision.query.filter_by(farmer_id=farmer_id).all()
        total = len(decisions)
        if total == 0: return {'success_rate': 0, 'total_decisions': 0, 'outcome_count': 0}
        
        success_count = 0
        outcome_count = 0
        for d in decisions:
            o = d.outcomes.first()
            if o:
                outcome_count += 1
                if o.outcome == 'success': success_count += 1
        
        # Apply Bayesian Dampening to avoid artificial 100% labels
        sr = self.ssa.calculate_dampened_sr(success_count, outcome_count) if outcome_count > 0 else 0
        
        return {
            'success_rate': sr, 
            'total_decisions': total,
            'outcome_count': outcome_count
        }

    def _get_days_since_last_decision(self, farmer_id):
        last_decision = Decision.query.filter_by(farmer_id=farmer_id).order_by(Decision.timestamp.desc()).first()
        if not last_decision: return 365 # Default to year if none
        delta = datetime.utcnow() - last_decision.timestamp
        return delta.days

    def _get_aes_raw_data(self, farmer_id):
        """Gather raw success/failure counts for followed vs ignored advice"""
        decisions = Decision.query.filter_by(farmer_id=farmer_id).all()
        data = {'n_followed': 0, 's_followed': 0, 'n_ignored': 0, 's_ignored': 0}
        for d in decisions:
            o = d.outcomes.first()
            if not o: continue
            is_success = 1 if o.outcome == 'success' else 0
            if d.advice_status == 'followed':
                data['n_followed'] += 1
                data['s_followed'] += is_success
            elif d.advice_status == 'ignored':
                data['n_ignored'] += 1
                data['s_ignored'] += is_success
        return data

    def _get_rar_raw_data(self, farmer_id):
        """Gather raw data for Risk Avoidance calculation"""
        avoided = Decision.query.filter(
            Decision.farmer_id == farmer_id,
            Decision.advice_status == 'followed',
            Decision.recommendation.in_(['WAIT', 'NOT_RECOMMENDED', 'AVOID'])
        ).all()
        
        ignored_failures = db.session.query(Outcome).join(Decision).filter(
            Decision.farmer_id == farmer_id,
            Decision.advice_status == 'ignored',
            Decision.recommendation.in_(['WAIT', 'NOT_RECOMMENDED', 'AVOID']),
            Outcome.outcome == 'failure'
        ).all()
        
        ignored_count = Decision.query.filter(
            Decision.farmer_id == farmer_id,
            Decision.advice_status == 'ignored',
            Decision.recommendation.in_(['WAIT', 'NOT_RECOMMENDED', 'AVOID'])
        ).count()

        loss_values = [abs(o.revenue_tnd) for o in ignored_failures if o.revenue_tnd is not None]
        
        return {
            'n_followed': len(avoided),
            'n_ignored': ignored_count,
            's_ignored': ignored_count - len(ignored_failures), # Succesfully ignored meant no failure?
            'failure_losses_ignored': loss_values
        }

    def _get_cvs_raw_data(self, farmer_id):
        """Gather confidence/outcome pairs for Brier Score"""
        decisions = Decision.query.filter(
            Decision.farmer_id == farmer_id,
            Decision.advice_status == 'followed'
        ).all()
        
        preds = []
        outs = []
        
        conf_map = {'HIGH': 0.85, 'MEDIUM': 0.70, 'LOW': 0.50}
        
        for d in decisions:
            o = d.outcomes.first()
            if o:
                preds.append(conf_map.get(d.confidence, 0.5))
                outs.append(1 if o.outcome == 'success' else 0)
                
        return {'predictions': preds, 'outcomes': outs}

    def _generate_smart_summary_v3(self, aes, drs, cvs):
        """Sophisticated NL summary based on high-rigor metrics"""
        if drs < 0.2:
            return "Welcome! Record your first 3 outcomes to unlock Bayesian-smoothed performance insights."
            
        summary = f"Analysis based on {int(drs*100)}% data reliability. "
        
        # Advice Insight
        if aes['value'] > 10:
            summary += f"Following system advice provides a statistically significant +{aes['value']}% success uplift. "
        elif aes['value'] < 0:
            summary += "Your intuition is currently outperforming the model; this often happens during local micro-climate shifts. "
            
        # Calibration Insight
        if cvs['calibration_score'] > 0.9:
            summary += "The advisor's confidence scores are perfectly calibrated to your farm's reality."
        elif cvs['overconfidence'] > 0.2:
            summary += "The system is currently over-optimistic about your farm's specific constraints."
            
        return summary

    def calculate_aes(self, farmer_id: int):
        """Advice Effectiveness Score (Wrapper for SSA)"""
        raw = self._get_aes_raw_data(farmer_id)
        reg_aes = self.regional.get_regional_AES_avg(None, None) # TODO: Use governorat from farmer
        results = self.ssa.calculate_aes(
            raw['n_followed'], raw['s_followed'],
            raw['n_ignored'], raw['s_ignored'],
            reg_aes
        )
        # Ensure 'aes' key for backward compatibility
        results['aes'] = results['value']
        results['interpretation'] = self._interpret_aes(results['value'], raw['n_ignored'] == 0)
        return results

    def _interpret_aes(self, aes, is_provisional):
        interpretation = "neutral"
        if aes > 15: interpretation = "Following advice significantly improves outcomes"
        elif aes > 5: interpretation = "Advice provides moderate benefit"
        elif aes < -5: interpretation = "System learning adjustment required"
        else: interpretation = "Consistent results regardless of advice"
        if is_provisional: interpretation += " (Provisional)"
        return interpretation

    def calculate_rar(self, farmer_id: int):
        """Risk Avoidance ROI (Wrapper for SSA)"""
        raw = self._get_rar_raw_data(farmer_id)
        farmer = Farmer.query.get(farmer_id)
        farm_size = getattr(farmer, 'farm_size', 1.0) or 1.0
        reg_loss = self.regional.get_regional_avg_loss(farmer.governorate, None)
        
        return self.ssa.calculate_rar(
            raw['n_followed'], raw['n_ignored'], raw['s_ignored'],
            reg_loss, farm_size
        )

    def calculate_crop_accuracy(self, farmer_id: int):
        """Crop-Specific Advice Accuracy (CSAA) with Bayesian Dampening"""
        # Get crops with outcomes
        results = db.session.query(
            Crop.name,
            func.count(Outcome.id).label('total'),
            func.coalesce(func.sum(cast(Outcome.outcome == 'success', Integer)), 0).label('successes')
        ).select_from(Crop).join(Decision, Decision.crop_id == Crop.id).join(Outcome, Outcome.decision_id == Decision.id).filter(
            Decision.farmer_id == farmer_id
        ).group_by(Crop.name).having(func.count(Outcome.id) >= 1).all()
        
        chart_data = []
        user = Farmer.query.get(farmer_id)
        governorate = user.governorate if user else "Tunis"

        for r in results:
            # Apply Bayesian Dampening (Laplace Smoothing)
            sr = self.ssa.calculate_dampened_sr(r.successes, r.total)
            
            # Regional Suitability Bonus
            suitability_weight = self.regional.get_regional_weight(r.name, governorate)
            
            # Reliability weight: Map 1 sample -> 10%, 10 samples -> 100%
            reliability = min(r.total * 10, 100) 
            
            chart_data.append({
                'crop': r.name,
                'success_rate': sr,
                'raw_sr': round((r.successes / r.total) * 100, 1), # Keep raw for debugging/advanced views
                'reliability': reliability,
                'suitability_weight': suitability_weight,
                'weighted_score': round(sr * suitability_weight, 1)
            })
            
        return {'chart_data': chart_data}

    def calculate_environmental_sweet_spot(self, farmer_id: int):
        """Identify optimal temperature for success"""
        successes = db.session.query(Decision.weather_temp_avg).join(Outcome).filter(
            Decision.farmer_id == farmer_id,
            Outcome.outcome == 'success',
            Decision.weather_temp_avg.isnot(None)
        ).all()
        
        temps = [r[0] for r in successes]
        if len(temps) < 1: return None # Show even if just 1 point
        
        # Simple percentile-based sweet spot (IQR)
        temps.sort()
        q1 = temps[int(len(temps)*0.25)]
        q3 = temps[int(len(temps)*0.75)]
        median = temps[int(len(temps)*0.5)]
        
        return {
            'optimal_conditions': {
                'temp': {
                    'optimal_value': round(median, 1),
                    'range_min': round(q1, 1),
                    'range_max': round(q3, 1)
                }
            }
        }

    def calculate_fci(self, farmer_id: int):
        """
        Farmer Compliance Index (FCI)
        Formula: (Completed Adherence / Total Valid Decisions) * 100
        Measures how often the farmer follows the system's advice.
        """
        # Count decisions by status
        stats = db.session.query(
            Decision.advice_status,
            func.count(Decision.id)
        ).filter(
            Decision.farmer_id == farmer_id,
            Decision.advice_status.in_(['followed', 'ignored'])
        ).group_by(Decision.advice_status).all()
        
        counts = {s[0]: s[1] for s in stats}
        followed = counts.get('followed', 0)
        ignored = counts.get('ignored', 0)
        total = followed + ignored
        
        if total == 0:
            return {'score': 0, 'grade': 'N/A', 'total_valid_decisions': 0}
            
        fci = (followed / total) * 100
        
        # Grading System
        if fci >= 90: grade = 'A+'
        elif fci >= 80: grade = 'A'
        elif fci >= 70: grade = 'B'
        elif fci >= 60: grade = 'C'
        elif fci >= 50: grade = 'D'
        else: grade = 'F'
        
        return {
            'score': round(fci, 1),
            'grade': grade,
            'total_decisions': total,
            'followed_count': followed
        }

    def calculate_rar(self, farmer_id: int):
        """
        Risk Avoidance ROI (RAR)
        Formula: Sum of (Cost per Plant * Estimated Plants) for every avoided failure.
        """
        # Decisions where user successfully avoided a risk
        avoided_decisions = Decision.query.filter(
            Decision.farmer_id == farmer_id,
            Decision.advice_status == 'followed',
            Decision.recommendation.in_(['WAIT', 'NOT_RECOMMENDED', 'AVOID'])
        ).all()
        
        risk_avoidance_events = len(avoided_decisions)
        
        # Calculate dynamic saved value
        # Assumption: Average small plot ~ 500 plants if not specified
        PLANTS_PER_DECISION = 500
        
        total_saved_value = 0
        breakdown = []
        
        for d in avoided_decisions:
            # Use stored cost if available, else default to 2.5 TND
            cost = d.seedling_cost_tnd if d.seedling_cost_tnd is not None else 2.5
            qty = d.input_quantity if d.input_quantity is not None else 1.0
            
            # Value saved = Investment at risk
            # If quantity is small (e.g. 1 packet), assume representative plot size? 
            # No, explicit input is better. If they bought 1kg wheat, they saved price of 1kg wheat.
            saved = cost * qty
            
            # Legacy fallback: If quantity is 1.0 (default) and cost is low, maybe apply a multiplier?
            # For now, trust the input.
            
            total_saved_value += saved
            
        # Interpretation
        if risk_avoidance_events > 5:
            interpretation = "Excellent defensive farming strategy."
        elif risk_avoidance_events > 0:
            interpretation = "Successfully identifying and avoiding risks."
        else:
            interpretation = "No high-risk scenarios encountered yet."

        return {
            'risks_avoided': risk_avoidance_events,
            'total_saved_tnd': round(total_saved_value, 2),
            'interpretation': interpretation
        }

    def calculate_tls(self, farmer_id: int):
        """
        Temporal Learning Slope (Legacy Wrapper).
        Returns monthly slope.
        """
        return self.calculate_performance_trends(farmer_id, 'monthly')

    def calculate_regional_benchmarks(self, farmer_id: int):
        """
        Governorate Success Index (GSI) & Comparison
        """
        farmer = Farmer.query.get(farmer_id)
        if not farmer: return {}
        
        gov = farmer.governorate
        
        # Personal stats
        personal_stats = self._get_personal_stats(farmer_id)
        personal_sr = personal_stats['success_rate']
        
        # Regional average
        regional_query = db.session.query(
            func.avg(
                case(
                    (Outcome.outcome == 'success', 100.0),
                    else_=0.0
                )
            ).label('avg_sr')
        ).join(Decision).join(Farmer).filter(Farmer.governorate == gov)
        
        result = regional_query.first()
        regional_sr = result.avg_sr if result and result.avg_sr else 0
        
        alpha = personal_sr - regional_sr
        
        # Get risk avoided count
        risk_avoided = Decision.query.filter_by(
            farmer_id=farmer_id,
            recommendation='WAIT'
        ).count()
        
        # Interpretation
        if alpha > 10: interpretation = "Significantly outperforming regional peers."
        elif alpha > 2: interpretation = "Above average regional performance."
        elif alpha >= -2: interpretation = "Performance in line with regional average."
        else: interpretation = "Opportunity to improve vs regional standards."

        return {
            'governorate': gov,
            'gsi': {'gsi': round(regional_sr, 1)},
            'personal_benchmark': {'personal': personal_sr, 'regional_avg': round(regional_sr, 1)},
            'alpha': round(alpha, 1),
            'interpretation': interpretation,
            'total_decisions': personal_stats['total_decisions'],
            'success_rate': personal_sr,
            'risks_avoided': risk_avoided,
            'top_regional_crops': self.analyze_opportunities(farmer_id)
        }

    def analyze_opportunities(self, farmer_id: int):
        """
        Identify top crops in region (by Weighted Score) that user isn't growing
        """
        user = Farmer.query.get(farmer_id)
        if not user: return []
        
        # User's crops
        user_crop_ids = [r[0] for r in db.session.query(Decision.crop_id).filter_by(farmer_id=farmer_id).distinct().all()]
        
        # Top regional crops (Larger sample to allow suitability sorting)
        top_crops_raw = db.session.query(
            Crop.name,
            Crop.icon,
            func.avg(cast(Outcome.outcome == 'success', Integer)).label('sr'),
            func.count(Outcome.id)
        ).select_from(Crop).join(Decision, Decision.crop_id == Crop.id).join(Outcome, Outcome.decision_id == Decision.id).join(Farmer, Decision.farmer_id == Farmer.id).filter(
            Farmer.governorate == user.governorate,
            Crop.id.notin_(user_crop_ids), # Exclude what user already grows
            Outcome.recorded_at >= datetime.utcnow() - timedelta(days=365)
        ).group_by(Crop.id).having(func.count(Outcome.id) >= 1).all()
        
        results = []
        for c in top_crops_raw:
            # Generate RCPS score (Regional Crop Performance Score)
            # Weighted mix of Success Rate + Sample Reliability + Suitability
            sr = c[2] * 100
            confidence = min(c[3] * 10, 100) # Simple confidence up to 10 samples
            suitability_weight = self.regional.get_regional_weight(c[0], user.governorate)
            
            # Base logic: SR * reliability
            base_rcps = (sr * 0.7) + (confidence * 0.3)
            # Multiplier for regional suitability
            final_rcps = base_rcps * suitability_weight
            
            results.append({
                'crop_name': c[0],
                'icon': c[1] or '🌱',
                'success_rate': round(sr, 1),
                'rcps': round(final_rcps, 0),
                'suitability_bonus': suitability_weight > 1.1
            })
            
        # Sort by finalized RCPS
        results.sort(key=lambda x: x['rcps'], reverse=True)
        return results[:3]

    def _calculate_diversification(self, farmer_id: int):
        """
        Market Diversification Opportunity Index (DOI)
        Formula: 1 - Simpson's Index (Sum of squared crop shares)
        0 = Monoculture (High Risk), 1 = Infinite Diversity
        """
        # Count decisions per crop
        crop_counts = db.session.query(
            Decision.crop_id, 
            func.count(Decision.id)
        ).filter_by(farmer_id=farmer_id).group_by(Decision.crop_id).all()
        
        total = sum(count for _, count in crop_counts)
        if total == 0: return 0.0
        
        # Sum of squared shares
        sum_sq = sum((count/total)**2 for _, count in crop_counts)
        
        doi = 1.0 - sum_sq
        return round(doi, 2)

    def _generate_smart_summary(self, aes: dict, benchmarks: dict, trends: dict):
        """
        Generate natural language insight based on metrics
        """
        # Get basic stats to generate a summary even without AES
        total_decisions = benchmarks.get('total_decisions', 0) if benchmarks else 0
        
        # If we have AES data, use it
        if aes and aes.get('aes') is not None:
            score = aes.get('aes', 0)
            gsi_alpha = benchmarks.get('alpha', 0) if benchmarks else 0
            trend_slope = trends.get('slope', 0) if trends else 0
            
            # Build narrative with AES
            summary = f"Analysis of your decision history indicates a {score:+.1f}% performance uplift when following system advice. "
            
            if gsi_alpha > 0:
                summary += f"You are currently outperforming the {benchmarks.get('governorate', 'regional')} average by {gsi_alpha:+.1f}%. "
            elif gsi_alpha < 0:
                summary += f"Your performance is trailing the {benchmarks.get('governorate', 'regional')} benchmark by {abs(gsi_alpha):.1f}%; consider stricter adherence to advice. "
                
            if trend_slope > 0.1:
                summary += "Your success trajectory shows a strong positive learning curve."
            elif trend_slope < -0.1:
                summary += "Recent trends suggest a need to revisit your crop selection strategy."
            else:
                summary += "Performance has remained stable over the analysis period."
                
            return summary
        
        # Fallback: Generate summary based on available data
        if total_decisions > 0:
            success_rate = benchmarks.get('success_rate', 0) if benchmarks else 0
            risk_avoided = benchmarks.get('risks_avoided', 0) if benchmarks else 0
            
            summary = f"You have made {total_decisions} planting decisions with our AI advisor. "
            
            if success_rate > 0:
                summary += f"Your current success rate is {success_rate}%. "
            
            if risk_avoided > 0:
                summary += f"You've successfully avoided {risk_avoided} high-risk planting scenarios. "
            
            summary += "Continue recording your actions after each decision to unlock detailed performance analytics and personalized growth strategies."
            
            return summary
        
        # Ultimate fallback for brand new users
        return "Welcome to your Intelligence Center! Start by getting planting advice and recording your decisions to unlock powerful analytics and insights tailored to your farm."

    def _generate_strategic_advice(self, farmer_id, benchmarks, trends, aes, rar, governorate):
        """
        Generate detailed, actionable strategic advice using Expert Logic Rule Base.
        Returns advice structured in three key pillars: Financial, Production, Growth.
        """
        # --- NEW USER / NO DATA CASE ---
        personal_stats = self._get_personal_stats(farmer_id)
        if personal_stats['total_decisions'] == 0:
            return self._generate_new_user_advice(governorate)

        advice = {
            'financial': [],
            'production': [],
            'strategy': [] # Maps to 'Growth' in requirements
        }
        
        # 2. Generate Pillar Strategies
        advice['financial'] = self._generate_financial_strategy(rar, personal_stats)
        advice['production'] = self._generate_production_strategy(farmer_id, personal_stats, benchmarks, governorate)
        advice['strategy'] = self._generate_growth_strategy(aes, trends, personal_stats, farmer_id)
        
        return advice

    def _generate_new_user_advice(self, governorate):
        """Logic for users with zero history: Driven 100% by Regional Suitability"""
        # Find hero crops for the zone
        target_zone = 'Other'
        for zone, govs in self.regional.REGIONAL_ZONES.items():
            if governorate in govs:
                target_zone = zone
                break
        
        hero_crops = [crop for crop, weight in self.regional.SUITABILITY_WEIGHTS.get(target_zone, {}).items() if weight > 1.2]
        risky_crops = [crop for crop, weight in self.regional.SUITABILITY_WEIGHTS.get(target_zone, {}).items() if weight < 0.8]
        
        hero_list = ", ".join(hero_crops[:3]) if hero_crops else "Staples like Wheat"
        risky_list = ", ".join(risky_crops[:2]) if risky_crops else "Unproven crops"

        return {
            'financial': [
                "📊 <strong>FINANCIAL GOAL:</strong> Establish your baseline investment efficiency.",
                f"🚀 <strong>STRATEGY:</strong> Focus on established {target_zone} hero crops like <strong>{hero_list}</strong> to minimize initial capital risk."
            ],
            'production': [
                f"📊 <strong>PRODUCTION PROFILE:</strong> New Farmer in <strong>{governorate}</strong>.",
                f"🚀 <strong>ACTION PLAN:</strong><br>1. <strong>PLANT:</strong> Prioritize {hero_crops[0] if hero_crops else 'Wheat'} and {hero_crops[1] if len(hero_crops)>1 else 'Barley'}<br>2. <strong>AVOID:</strong> Higher risk crops like {risky_list} for your first season."
            ],
            'strategy': [
                "📊 <strong>GROWTH STATUS:</strong> Learning Phase.",
                "🚀 <strong>NEXT STEPS:</strong> Record 3 decisions to calibrate the AI to your specific plot."
            ]
        }

    def _generate_financial_strategy(self, rar, stats):
        """
        Logic: Money Saved vs. Risk Avoidance
        Output: Profile -> Insight -> Actions -> Impact
        """
        items = []
        
        saved = rar.get('total_saved_tnd', 0)
        avoided = rar.get('risks_avoided', 0)
        
        # --- 1. DETERMINE PROFILE ---
        if avoided > 10:
            profile = "Cautious Investor"
            insight = f"You save money beautifully ({int(saved)} TND) by avoiding risks. This discipline provides a strong capital buffer for future investments."
            recommendation = (
                "<strong>OPTIMIZE CAPITAL ALLOCATION</strong><br>"
                "1. <strong>KEEP DOING:</strong> Continue following WAIT advice for extreme risks<br>"
                "2. <strong>START DOING:</strong> Reinvest 20% of your current savings into higher-quality inputs (seeds/fertilizer)<br>"
                "3. <strong>STOP DOING:</strong> Manual guesswork for weather-dependent timings"
            )
            impact = "Strategic reinvestment of saved capital can boost your projected yield by 15-20%."
            
        elif avoided > 3:
            profile = "Balanced Defensive"
            insight = f"You have a healthy risk management habit, having successfully avoided {avoided} high-risk scenarios."
            recommendation = (
                "<strong>REDUCE OPERATIONAL LEAKAGE</strong><br>"
                "1. <strong>KEEP DOING:</strong> Trusting the 'WAIT' warnings—they are protecting your recurring costs.<br>"
                "2. <strong>START DOING:</strong> Track exact seedling costs to refine ROI calculations.<br>"
                "3. <strong>STOP DOING:</strong> Ignoring 'LOW' confidence alerts during peak season."
            )
            impact = "Precise tracking of saved inputs will improve your credit-worthiness for seasonal loans."
            
        else:
            profile = "Growth Starter"
            insight = "You are in the early stages of building a financial safety net. Your baseline capital protection is being established."
            recommendation = (
                "<strong>BUILD YOUR SAFETY NET</strong><br>"
                "1. <strong>START DOING:</strong> Record seedling costs for every decision.<br>"
                "2. <strong>GOAL:</strong> Successfully avoid your first major weather event using the system tips.<br>"
            )
            impact = "Preventing just one failed hectare of high-value crops can save over 500 TND in direct input losses."
            
        # Format into list items for frontend
        items.append(f"📊 <strong>YOUR FINANCIAL PROFILE:</strong><br>You're a <strong>{profile}</strong>. {insight}")
        items.append(f"🚀 <strong>STRATEGY RECOMMENDATION:</strong><br>{recommendation}")
        items.append(f"📈 <strong>EXPECTED IMPACT:</strong><br>{impact}")
        
        return items

    def _generate_production_strategy(self, farmer_id, stats, benchmarks, governorate):
        """
        Logic: Weighted Crop Performance (SR * Suitability) vs Regional Benchmarks
        """
        items = []
        
        # Get Crop Performance
        acc_result = self.calculate_crop_accuracy(farmer_id)
        chart_data = acc_result.get('chart_data', [])
        
        if not chart_data:
            return ["🚜 <strong>START PLANTING:</strong> Record outcomes for different crops to unlock production profiles."]

        # Sort by Weighted Score (SR * Suitability) to find the true "Winner" for the region
        acc = sorted(chart_data, key=lambda x: x['weighted_score'], reverse=True)
        winner = acc[0]
        
        # Laggard is lowest raw performance or lowest suitability fit
        laggard = sorted(chart_data, key=lambda x: x['success_rate'])[0] if len(acc) > 1 else None
        
        # Regional comparison
        alpha = benchmarks.get('alpha', 0) if benchmarks else 0
        
        # --- PROFILE & INSIGHT ---
        # Include Region in Profile as requested
        region_label = governorate

        if winner['weighted_score'] > 70:
            # Winner is high performance AND high suitability
            profile = f"{winner['crop']} Specialist in {region_label}"
            insight = f"Your mastery of <strong>{winner['crop']}</strong> in {region_label} is your competitive advantage."
            
            if winner['suitability_weight'] > 1.2:
                insight += " You are perfectly aligned with your regional soil/climate strengths."
            
            rec_title = "STRENGTHEN YOUR SPECIALTY"
            rec_steps = (
                f"1. <strong>EXPAND:</strong> Increase {winner['crop']} acreage (Optimal regional fit)<br>"
                "2. <strong>OPTIMIZE:</strong> Use precision irrigation to push yields even higher<br>"
                "3. <strong>BENCHMARK:</strong> Share your success metrics with the community"
            )
            
        elif winner['success_rate'] > 80:
            # High success but maybe low suitability (e.g. Citrus in Sfax)
            profile = f"General {winner['crop']} Expert in {region_label}"
            insight = f"You're seeing high success with <strong>{winner['crop']}</strong>, but this crop is higher risk for {region_label}."
            rec_title = "MITIGATE REGIONAL RISK"
            rec_steps = (
                f"1. <strong>DIVERSIFY:</strong> Start a trial plot of a high-suitability hero crop (Olive/Almond)<br>"
                f"2. <strong>PROTECT:</strong> Since {winner['crop']} is sensitive here, prioritize pest monitoring"
            )
        else:
            profile = f"Active Producer in {region_label}"
            insight = f"You're building experience in {region_label}. Your current focus is stabilizing outcomes."
            rec_title = "STABILIZE PRODUCTION"
            rec_steps = (
                "1. <strong>ANALYZE:</strong> Review weather patterns for your last 3 harvest windows<br>"
                "2. <strong>CONSULT:</strong> Use 'Top Regional Crops' to pick your next planting"
            )

        # Format into list items for frontend
        items.append(f"📊 <strong>YOUR PRODUCTION PROFILE:</strong><br>You're an <strong>{profile}</strong>. {insight}")
        items.append(f"🚀 <strong>STRATEGY RECOMMENDATION:</strong><br>{rec_title}<br>{rec_steps}")
        
        if alpha < -5:
            items.append(f"⚠️ <strong>REGIONAL PERFORMANCE GAP:</strong> Your success rate is {abs(alpha)}% below the {region_label} average. Focus on timing.")
        
        # Seasonal focus (Dynamic mocked)
        current_month = datetime.now().month
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        if winner:
            next_month_idx = current_month % 12
            items.append(
                f"📅 <strong>SEASONAL FOCUS:</strong><br>"
                f"• <strong>{month_names[current_month-1]}:</strong> Maximize {winner['crop']} care<br>"
                f"• <strong>{month_names[next_month_idx]}:</strong> Prep land for next cycle<br>"
            )
            
        return items

    def _generate_growth_strategy(self, aes, trends, stats, farmer_id):
        """
        Logic: Uplift vs Trends vs Sweet Spot
        """
        items = []
        
        uplift = aes.get('value', 0)
        slope = trends.get('slope', 0)
        sweet_spot = self.calculate_environmental_sweet_spot(farmer_id)
        
        # --- PROFILE ---
        if uplift > 40:
            profile = "Steady Improver"
            type_text = "learns well from advice"
        elif uplift > 10:
            profile = "Independent Operator"
            type_text = "validating the system"
        else:
            profile = "Skeptic / New User"
            type_text = "establishing a baseline"
            
        # --- SWEET SPOT ---
        temp_range = "20-25°C" # default
        if sweet_spot and 'optimal_conditions' in sweet_spot:
             t = sweet_spot['optimal_conditions'].get('temp', {})
             if t: temp_range = f"{t.get('optimal_value', 22)}°C"

        # --- LOGIC ---
        # --- LOGIC ---
        if uplift > 30:
            insight = f"Your +{uplift:.1f}% uplift shows you {type_text}. You perform best around <strong>{temp_range}</strong>."
            rec = (
                f"<strong>STAY IN YOUR SWEET SPOT</strong><br>"
                f"1. <strong>SCHEDULE:</strong> Plan major plantings around {temp_range}<br>"
                "2. <strong>DOCUMENT:</strong> Create a 'success recipe' for your best crop<br>"
                "3. <strong>LIMIT:</strong> One new experiment per season"
            )
            
            # Dynamic Path
            current_sr = float(stats.get('success_rate', 0))
            if current_sr >= 95:
                path = (
                    "<strong>GROWTH PATH:</strong><br>"
                    "🌟 <strong>MAINTENANCE MODE:</strong> You are at peak performance.<br>"
                    "Goal: Ensure consistency across seasons."
                )
            else:
                target_q1 = min(100, int(current_sr + 5))
                target_q2 = min(100, int(current_sr + 10))
                path = (
                    "<strong>GROWTH PATH:</strong><br>"
                    f"Q1: Perfect timing → Target {target_q1}% Success<br>"
                    f"Q2: Fix Irrigation → Target {target_q2}% Success"
                )

        elif stats['total_decisions'] < 5:
             # New User (Tier 1)
             profile = "New Data Farmer"
             insight = "You are beginning your data-driven journey. First decisions establish your baseline."
             rec = (
                 "<strong>FOUNDATION FIRST</strong><br>"
                 "1. <strong>PLANT:</strong> 3 different crops to discover aptitude<br>"
                 "2. <strong>RECORD:</strong> Every outcome (good or bad)<br>"
                 "3. <strong>FOLLOW:</strong> All advice to build trust"
             )
             path = "<strong>FIRST 90 DAYS:</strong><br>Month 1: Plant Staple<br>Month 2: Test Summer Crop"
        else:
            insight = f"Performance is stable ({stats['success_rate']}%) but could be higher. You might be ignoring advice in crucial moments."
            rec = (
                "<strong>ALIGNMENT CHECK</strong><br>"
                "1. <strong>COMPARE:</strong> Review ignored advice that succeeded<br>"
                "2. <strong>ADAPT:</strong> Shift planting dates by 10 days<br>"
                "3. <strong>TEST:</strong> Follow advice 100% for one plot"
            )
            # Dynamic Recovery Path
            current_sr = float(stats.get('success_rate', 0))
            target_sr = min(100, int(current_sr + 10))
            path = f"<strong>RECOVERY PATH:</strong><br>Goal: Reconnect with regional best practices to hit {target_sr}%."

        items.append(f"📊 <strong>YOUR GROWTH PROFILE:</strong><br>You're a <strong>{profile}</strong> who {type_text}.")
        items.append(f"🎯 <strong>CORE INSIGHT:</strong><br>{insight}")
        items.append(f"🚀 <strong>STRATEGY:</strong><br>{rec}")
        items.append(path)
        
        return items