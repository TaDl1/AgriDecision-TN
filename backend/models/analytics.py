"""
Analytics models for tracking farmer performance and events
"""
from models.base import db
from datetime import datetime


class FarmerAnalytics(db.Model):
    """Aggregated analytics for farmers"""
    __tablename__ = 'farmer_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False, unique=True, index=True)
    total_decisions = db.Column(db.Integer, default=0)
    total_outcomes = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'farmer_id': self.farmer_id,
            'total_decisions': self.total_decisions,
            'total_outcomes': self.total_outcomes,
            'success_rate': self.success_rate,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class AnalyticsEvent(db.Model):
    """Event log for farming intelligence transitions and interactions"""
    __tablename__ = 'analytics_events'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True) # TIER_UP, DATA_VIEW, MILESTONE_CLICK
    event_category = db.Column(db.String(50)) # 'ANALYTICS', 'ADVICE', 'PROFILE'
    event_value = db.Column(db.String(255)) # e.g. 'T3_PRACTITIONER'
    metadata_json = db.Column(db.JSON) # Additional context
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.event_type,
            'category': self.event_category,
            'value': self.event_value,
            'timestamp': self.timestamp.isoformat()
        }


class RegionalBenchmarks(db.Model):
    """Regional performance benchmarks for crops"""
    __tablename__ = 'regional_benchmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    governorate = db.Column(db.String(50), nullable=False, index=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False, index=True)
    avg_success_rate = db.Column(db.Float, default=0.0)
    avg_loss_per_failure = db.Column(db.Float, default=200.0)
    sample_size = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('governorate', 'crop_id', name='unique_region_crop'),
    )
    
    def to_dict(self):
        return {
            'governorate': self.governorate,
            'crop_id': self.crop_id,
            'avg_success_rate': self.avg_success_rate,
            'avg_loss_per_failure': self.avg_loss_per_failure,
            'sample_size': self.sample_size
        }


class CropSpecificDefaults(db.Model):
    """Expert-defined defaults for specific crops"""
    __tablename__ = 'crop_specific_defaults'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False, unique=True, index=True)
    default_success_rate = db.Column(db.Float, default=0.70)
    default_avg_loss = db.Column(db.Float, default=200.0)
    seasonal_factor_summer = db.Column(db.Float, default=1.0)
    seasonal_factor_winter = db.Column(db.Float, default=1.0)
    
    def to_dict(self):
        return {
            'crop_id': self.crop_id,
            'default_success_rate': self.default_success_rate,
            'default_avg_loss': self.default_avg_loss
        }
