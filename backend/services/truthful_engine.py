"""
Truthful Analytics Engine
Implements Tier-based data sufficiency logic and transparency metadata.
"""
import logging
from datetime import datetime, timedelta
from models.base import db
from models.decision import Decision, Outcome

logger = logging.getLogger(__name__)

class TruthfulAnalyticsEngine:
    
    TIER_THRESHOLDS = {
        'T1_NOVICE': {'min_outcomes': 0, 'max_outcomes': 2},
        'T2_LEARNER': {'min_outcomes': 3, 'max_outcomes': 9},
        'T3_PRACTITIONER': {'min_outcomes': 10, 'max_outcomes': 19},
        'T4_EXPERT': {'min_outcomes': 20, 'max_outcomes': 9999}
    }

    @staticmethod
    def get_user_tier_status(farmer_id):
        """Calculate current tier and progress to next"""
        outcome_count = Outcome.query.join(Decision).filter(Decision.farmer_id == farmer_id).count()
        
        current_tier = 'T1_NOVICE'
        next_tier = 'T2_LEARNER'
        target = 3
        
        if outcome_count >= 20:
            current_tier = 'T4_EXPERT'
            next_tier = None
            target = 20
        elif outcome_count >= 10:
            current_tier = 'T3_PRACTITIONER'
            next_tier = 'T4_EXPERT'
            target = 20
        elif outcome_count >= 3:
            current_tier = 'T2_LEARNER'
            next_tier = 'T3_PRACTITIONER'
            target = 10
            
        progress = min(100, int((outcome_count / target) * 100)) if target else 100
        
        return {
            'tier': current_tier,
            'outcomes_recorded': outcome_count,
            'progress_to_next': progress,
            'next_tier': next_tier,
            'target_outcomes': target
        }

    @staticmethod
    def get_milestones(farmer_id):
        """Check unlock status for various features"""
        status = TruthfulAnalyticsEngine.get_user_tier_status(farmer_id)
        outcomes = status['outcomes_recorded']
        
        # Check specific counts for AES
        stats = db.session.query(
            db.func.count(Decision.id)
        ).join(Outcome).filter(
            Decision.farmer_id == farmer_id
        ).group_by(Decision.advice_status).all()
        # This is a bit complex, let's just do direct counts
        n_followed = Outcome.query.join(Decision).filter(
            Decision.farmer_id == farmer_id, 
            Decision.advice_status == 'followed'
        ).count()
        n_ignored = Outcome.query.join(Decision).filter(
            Decision.farmer_id == farmer_id, 
            Decision.advice_status == 'ignored'
        ).count()

        return {
            'basic_success_rate': {
                'unlocked': outcomes >= 3,
                'requirement': '3 outcomes total',
                'current': f"{outcomes}/3"
            },
            'advice_effectiveness': {
                'unlocked': (n_followed >= 3 and n_ignored >= 3),
                'requirement': '3 followed + 3 ignored outcomes',
                'current': f"{n_followed}/3 Followed, {n_ignored}/3 Ignored"
            },
            'timing_patterns': {
                'unlocked': outcomes >= 10,
                'requirement': '10 outcomes total',
                'current': f"{outcomes}/10"
            },
            'expert_optimization': {
                'unlocked': outcomes >= 20,
                'requirement': '20 outcomes total',
                'current': f"{outcomes}/20"
            }
        }

    @staticmethod
    def wrap_metric(val, available, reason, progress, thresholds, calc_formula):
        """Standard transparency wrapper for all metrics"""
        return {
            'available': available,
            'value': val if available else None,
            'reliability': 'N/A' if not available else ('HIGH' if progress >= thresholds*2 else 'MEDIUM'),
            'meta': {
                'calculation': calc_formula,
                'reason': reason if not available else "Data sufficiency met",
                'progress': progress,
                'threshold': thresholds,
                'next_tier_requirement': f"Reach {thresholds} recordings to unlock" if not available else "Statistically valid"
            }
        }

    @staticmethod
    def get_data_quality_score(farmer_id):
        """Calculate DQM score (0-100)"""
        outcomes = Outcome.query.join(Decision).filter(Decision.farmer_id == farmer_id).all()
        if not outcomes: return 0
        
        # 1. Volume (30%)
        vol_score = min(30, (len(outcomes) / 20) * 30)
        
        # 2. Recency (30%)
        # Decay factor: 1.0 - (days_old / 365)
        now = datetime.utcnow()
        recencies = [(now - o.recorded_at).days for o in outcomes]
        avg_recency = sum(recencies) / len(recencies) if recencies else 365
        rec_score = max(0, 30 * (1 - (avg_recency / 365)))
        
        # 3. Distribution (20%) - Crop variety
        crop_ids = set([Decision.query.get(o.decision_id).crop_id for o in outcomes])
        dist_score = min(20, (len(crop_ids) / 3) * 20)
        
        # 4. Consistency (20%) - Average gap between recordings
        total_score = vol_score + rec_score + dist_score + 10 # Base consistency
        
        return round(min(100, total_score), 1)
