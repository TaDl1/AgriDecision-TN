"""
Regional adjustment model for agrarian periods
"""
from models.base import db


class PeriodRegionAdjustment(db.Model):
    """Regional adjustments for agrarian periods"""
    __tablename__ = 'period_region_adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.String(10), db.ForeignKey('agrarian_periods.id'), nullable=False, index=True)
    governorate = db.Column(db.String(50), nullable=False, index=True)
    
    # Adjustments
    start_adjustment_days = db.Column(db.Integer, default=0)  # +7 = starts 7 days later
    end_adjustment_days = db.Column(db.Integer, default=0)
    risk_multiplier = db.Column(db.Float, default=1.0)  # 1.2 = 20% higher risk
    
    # Additional info
    notes = db.Column(db.Text)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('period_id', 'governorate', name='unique_period_region'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'period_id': self.period_id,
            'governorate': self.governorate,
            'start_adjustment_days': self.start_adjustment_days,
            'end_adjustment_days': self.end_adjustment_days,
            'risk_multiplier': self.risk_multiplier
        }
    
    def __repr__(self):
        return f'<PeriodRegionAdjustment {self.period_id} - {self.governorate}>'