"""
User/Farmer model
"""
from models.base import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Farmer(db.Model):
    """Farmer user model"""
    __tablename__ = 'farmers'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    governorate = db.Column(db.String(50), nullable=False, index=True)
    farm_type = db.Column(db.String(20), nullable=False)
    soil_type = db.Column(db.String(20), nullable=True)  # CLAY, SANDY, LOAM, CALCAREOUS, SILT
    farm_size_ha = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), default='farmer')  # farmer or admin
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    preferences = db.Column(db.JSON, default=dict)  # Store user settings (lang, units, etc.)
    
    # Relationships
    decisions = db.relationship('Decision', backref='farmer', lazy='dynamic', cascade='all, delete-orphan')
    analytics = db.relationship('FarmerAnalytics', backref='farmer', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'phone': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'governorate': self.governorate,
            'farm_type': self.farm_type,
            'soil_type': self.soil_type,
            'farm_size': self.farm_size_ha,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<Farmer {self.phone_number} - {self.governorate}>'