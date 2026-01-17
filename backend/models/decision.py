"""
Decision and outcome models
"""
from models.base import db
from datetime import datetime


class Decision(db.Model):
    """Planting decision model"""
    __tablename__ = 'decisions'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False, index=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False, index=True)
    governorate = db.Column(db.String(50), nullable=False, index=True)
    
    # Decision details
    recommendation = db.Column(db.String(20), nullable=False, index=True)  # PLANT_NOW, WAIT, NOT_RECOMMENDED
    wait_days = db.Column(db.Integer, default=0)
    confidence = db.Column(db.String(20), nullable=False)  # HIGH, MEDIUM, LOW
    explanation = db.Column(db.Text)
    
    # Context
    period_id = db.Column(db.String(10), db.ForeignKey('agrarian_periods.id'), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Weather snapshot
    weather_temp_min = db.Column(db.Float)
    weather_temp_max = db.Column(db.Float)
    weather_temp_avg = db.Column(db.Float)
    weather_humidity = db.Column(db.Float)
    weather_wind = db.Column(db.Float)
    weather_rainfall = db.Column(db.Float)
    weather_risks = db.Column(db.Text)  # JSON string of risks
    
    # Action-Feedback Loop fields
    advice_status = db.Column(db.String(20), default='pending', index=True)  # 'followed', 'ignored', 'pending'
    actual_action = db.Column(db.String(30))  # 'planted_now', 'waited', 'not_planted'
    deviation_reason = db.Column(db.Text)  # Why advice was ignored (optional)
    action_recorded_at = db.Column(db.DateTime)  # When farmer recorded their action
    
    # Financial Settings (for analytics)
    input_quantity = db.Column(db.Float, default=1.0) # Quantity of inputs bought
    seedling_cost_tnd = db.Column(db.Float)  # Cost per seedling in TND
    market_price_tnd = db.Column(db.Float)  # Market price per kg in TND
    cost_basis_tnd = db.Column(db.Float)   # Pre-calculated (input_quantity * seedling_cost)
    
    # User interaction (legacy - kept for backward compatibility)
    user_followed = db.Column(db.Boolean)  # Did user follow advice?
    user_notes = db.Column(db.Text)
    
    # Relationships
    outcomes = db.relationship('Outcome', backref='decision', lazy='dynamic', cascade='all, delete-orphan')
    period = db.relationship('AgrarianPeriod')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'crop_name': self.crop.name if self.crop else None,
            'governorate': self.governorate,
            'recommendation': self.recommendation,
            'wait_days': self.wait_days,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'period_id': self.period_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'weather_temp': self.weather_temp_avg,
            'advice_status': self.advice_status,
            'actual_action': self.actual_action,
            'action_recorded_at': self.action_recorded_at.isoformat() if self.action_recorded_at else None,
            'seedling_cost_tnd': self.seedling_cost_tnd,
            'market_price_tnd': self.market_price_tnd,
            'cost_basis_tnd': self.cost_basis_tnd
        }
    
    def __repr__(self):
        return f'<Decision {self.id} - {self.recommendation}>'


class Outcome(db.Model):
    """Outcome tracking for decisions"""
    __tablename__ = 'outcomes'
    
    id = db.Column(db.Integer, primary_key=True)
    decision_id = db.Column(db.Integer, db.ForeignKey('decisions.id'), nullable=False, index=True)
    
    # Outcome details
    outcome = db.Column(db.String(30), nullable=False, index=True)  # success, failure, unknown
    yield_kg = db.Column(db.Float)
    revenue_tnd = db.Column(db.Float)
    net_profit_loss = db.Column(db.Float) # (actual_revenue - decision.cost_basis)
    notes = db.Column(db.Text)
    
    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    harvest_date = db.Column(db.Date)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'decision_id': self.decision_id,
            'outcome': self.outcome,
            'yield_kg': self.yield_kg,
            'revenue_tnd': self.revenue_tnd,
            'net_profit_loss': self.net_profit_loss,
            'notes': self.notes,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }
    
    def __repr__(self):
        return f'<Outcome {self.id} - {self.outcome}>'