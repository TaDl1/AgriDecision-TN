"""
Crop and agrarian period models
"""
from models.base import db


class Crop(db.Model):
    """Crop information model"""
    __tablename__ = 'crops'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    scientific_name = db.Column(db.String(100))
    category = db.Column(db.String(20), nullable=False)  # field, vegetable, perennial
    min_temp = db.Column(db.Float, nullable=False)
    max_temp = db.Column(db.Float, nullable=False)
    optimal_temp_min = db.Column(db.Float)
    optimal_temp_max = db.Column(db.Float)
    water_needs = db.Column(db.String(20))  # low, medium, high
    growth_days = db.Column(db.Integer)
    icon = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Financial & Yield Modeling
    input_type = db.Column(db.String(30), default='seeds_kg') # e.g. seeds_kg, seedlings, sapling
    yield_min = db.Column(db.Float, default=1.0) # Multiplier min (e.g. 8.0)
    yield_max = db.Column(db.Float, default=1.0) # Multiplier max (e.g. 15.0)
    yield_unit = db.Column(db.String(20), default='kg') # Output unit (kg, unit, etc)
    
    # Relationships
    period_rules = db.relationship('CropPeriodRule', backref='crop', lazy='dynamic')
    decisions = db.relationship('Decision', backref='crop', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'scientific_name': self.scientific_name,
            'category': self.category,
            'min_temp': self.min_temp,
            'max_temp': self.max_temp,
            'water_needs': self.water_needs,
            'icon': self.icon,
            'input_type': self.input_type,
            'yield_unit': self.yield_unit,
            'yield_range': [self.yield_min, self.yield_max]
        }
    
    def to_detailed_dict(self):
        """Convert to detailed dictionary"""
        return {
            **self.to_dict(),
            'optimal_temp_range': f"{self.optimal_temp_min}-{self.optimal_temp_max}°C" if self.optimal_temp_min else None,
            'growth_days': self.growth_days,
            'description': self.description
        }
    
    def __repr__(self):
        return f'<Crop {self.name}>'


class AgrarianPeriod(db.Model):
    """Agrarian calendar period model"""
    __tablename__ = 'agrarian_periods'
    
    id = db.Column(db.String(10), primary_key=True)  # P1, P2, etc.
    name = db.Column(db.String(50), nullable=False)
    start_month = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    end_month = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # low, medium, high
    description = db.Column(db.Text)
    temperature_profile = db.Column(db.String(50))
    rainfall_profile = db.Column(db.String(50))
    
    # Relationships
    crop_rules = db.relationship('CropPeriodRule', backref='period', lazy='dynamic')
    regional_adjustments = db.relationship('PeriodRegionAdjustment', backref='period', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'start_month': self.start_month,
            'start_day': self.start_day,
            'end_month': self.end_month,
            'end_day': self.end_day,
            'risk_level': self.risk_level,
            'description': self.description
        }
    
    def __repr__(self):
        return f'<AgrarianPeriod {self.id} - {self.name}>'


class CropPeriodRule(db.Model):
    """Rules linking crops to agrarian periods"""
    __tablename__ = 'crop_period_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False, index=True)
    period_id = db.Column(db.String(10), db.ForeignKey('agrarian_periods.id'), nullable=False, index=True)
    suitability = db.Column(db.String(20), nullable=False)  # optimal, acceptable, risky, forbidden
    reason = db.Column(db.Text)
    additional_conditions = db.Column(db.Text)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('crop_id', 'period_id', name='unique_crop_period'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'crop_id': self.crop_id,
            'period_id': self.period_id,
            'suitability': self.suitability,
            'reason': self.reason
        }
    
    def __repr__(self):
        return f'<CropPeriodRule {self.crop_id}-{self.period_id}: {self.suitability}>'