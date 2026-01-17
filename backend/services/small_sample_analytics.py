
import math
import numpy as np
from datetime import datetime, timedelta

class SmallSampleAnalytics:
    def __init__(self):
        self.MIN_SAMPLES = {
            'aes': 3,      # Minimum per group (followed/ignored)
            'success_rate': 3,
            'rar': 3,
            'tls': 3,
            'spi': 1       # Can work with 0 using regional
        }
        
        self.BAYESIAN_PRIORS = {
            'success': 2,
            'failure': 2,
            'regional_weight': 5  # Pseudocounts for regional blending
        }
        
        self.RELIABILITY_THRESHOLDS = {
            'high': 0.7,    # DRS >= 0.7
            'medium': 0.3,   # DRS >= 0.3
            'low': 0.0      # DRS < 0.3
        }

    def wilson_interval(self, p, n, z=1.96):
        """Wilson score interval for population proportion (Standard for small n)"""
        if n == 0: return 0, 1
        denominator = 1 + z*z/n
        centre = p + z*z/(2*n)
        width = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
        lower = (centre - width) / denominator
        upper = (centre + width) / denominator
        return max(0, lower), min(1, upper)

    def calculate_aes(self, n_followed, s_followed, n_ignored, s_ignored, regional_aes_avg=15.0):
        """Advice Effectiveness Score with Bayesian Smoothing and Wilson CI"""
        prior_s = self.BAYESIAN_PRIORS['success']
        prior_f = self.BAYESIAN_PRIORS['failure']
        
        # Bayesian adjusted success rates (Beta(2,2) prior)
        p1_adj = (s_followed + prior_s) / (n_followed + prior_s + prior_f)
        p2_adj = (s_ignored + prior_s) / (n_ignored + prior_s + prior_f)
        
        aes_val = (p1_adj - p2_adj) * 100
        
        # Calculate CIs using Wilson Score Interval
        l1, u1 = self.wilson_interval(p1_adj, n_followed)
        l2, u2 = self.wilson_interval(p2_adj, n_ignored)
        
        # CI for the difference (Square root of sum of squares of widths/2)
        ci_width = 1.96 * math.sqrt(((u1-l1)/2)**2 + ((u2-l2)/2)**2) * 100
        
        if n_followed >= self.MIN_SAMPLES['aes'] and n_ignored >= self.MIN_SAMPLES['aes']:
            method = 'direct_bayesian'
        else:
            method = 'regional_estimate'
            # Confidence factor fades in personal data (N/10 scaling)
            conf_factor = min(n_followed + n_ignored, 10) / 10
            aes_val = regional_aes_avg * (1 - conf_factor) + aes_val * conf_factor
            ci_width = max(ci_width, 40.0 * (1 - conf_factor)) # Wide CI for regional
            
        return {
            'value': round(aes_val, 1),
            'ci_width': round(ci_width, 1),
            'method': method,
            'sample_size': n_followed + n_ignored,
            'confidence_range': [round(aes_val - ci_width, 1), round(aes_val + ci_width, 1)]
        }

    def calculate_rar(self, n_followed_wait, n_ignored, failures_ignored, avg_loss, farm_size_ha=1.0):
        """Risk Avoidance ROI with Bayesian Fallback and Farm Size Normalization"""
        # Bayesian estimate of failure rate
        if n_ignored >= 3:
            failure_rate = failures_ignored / n_ignored
            method = 'direct'
        else:
            # Conservative regional estimate (15%)
            failure_rate = 0.15
            method = 'conservative_estimate'
        
        # Adjust avg_loss for farm size (Power law scaling / direct multiplier)
        # Using a simple linear multiplier for ROI but could be log-scaled for risk
        adjusted_loss = abs(avg_loss) * farm_size_ha
        
        rar = n_followed_wait * failure_rate * adjusted_loss
        
        return {
            'value': round(rar, 2),
            'method': method,
            'failure_rate': round(failure_rate, 2),
            'adjusted_loss': round(adjusted_loss, 2),
            'interpretation': "Excellent defensive farming strategy." if n_followed_wait > 5 else 
                              "Successfully identifying and avoiding risks." if n_followed_wait > 0 else 
                              "No high-risk scenarios encountered yet.",
            'risks_avoided': n_followed_wait,
            'total_saved_tnd': round(rar, 2)
        }

    def calculate_cvs(self, predictions, outcomes):
        """Confidence Validation Score using Brier Score Calibration"""
        if not predictions:
            return {'calibration_score': 0, 'overconfidence': 0, 'status': 'no_data'}
            
        # Brier Score = 1/N * sum((p - o)^2)
        # predictions expected to be [0.2, 0.5, 0.8] based on LOW/MEDIUM/HIGH
        squared_errors = [(p - o)**2 for p, o in zip(predictions, outcomes)]
        brier_score = sum(squared_errors) / len(predictions)
        
        # Calibration Score (1 - Brier)
        calibration_score = 1 - brier_score
        
        # Overconfidence = Mean(Confidence) - Mean(Accuracy)
        mean_conf = sum(predictions) / len(predictions)
        mean_acc = sum(outcomes) / len(outcomes)
        overconfidence = mean_conf - mean_acc
        
        return {
            'calibration_score': round(calibration_score, 3),
            'overconfidence': round(overconfidence, 3),
            'brier_score': round(brier_score, 3),
            'status': 'calibrated' if calibration_score > 0.85 else 'needs_calibration'
        }

    def calculate_drs(self, n_total, n_months, days_since_last, completeness_score):
        """Data Reliability Score (DRS) with refined clipping / thresholds"""
        # Volume: 20 decisions = full score (0.3 weight)
        vol_score = min(n_total / 20.0, 1.0)
        
        # Consistency: 6 months = full score (0.3 weight)
        consistency_score = min(n_months / 6.0, 1.0)
        
        # Recency: 90 days = 0 (0.2 weight)
        recency_score = max(0, 1.0 - (days_since_last / 90.0))
        
        # Completeness: (0.2 weight)
        
        drs = (0.3 * vol_score + 
               0.3 * consistency_score + 
               0.2 * recency_score + 
               0.2 * completeness_score)
               
        return round(drs, 2)

    def get_reliability_tier(self, drs):
        if drs >= self.RELIABILITY_THRESHOLDS['high']: return 1
        if drs >= self.RELIABILITY_THRESHOLDS['medium']: return 2
        return 3

    def get_insight_level(self, n_decisions):
        if n_decisions < 3: return "BASIC"
        if n_decisions < 10: return "INTERMEDIATE"
        if n_decisions < 30: return "ADVANCED"
        return "EXPERT"

    def calculate_dampened_sr(self, successes, total):
        """
        Bayesian Dampening (Laplace Smoothing)
        Prevents 100% labels for small 'n' (e.g., 1/1 = 100% -> 60%)
        Formula: (s + 2) / (n + 4)
        """
        if total < 10:
            import logging
            logging.info(f"Applying Bayesian dampening to small sample: {successes}/{total}")
            
        dampened = (successes + 2) / (total + 4)
        return round(dampened * 100, 1)
