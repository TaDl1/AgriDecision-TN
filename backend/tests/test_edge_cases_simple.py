import pytest
from unittest.mock import MagicMock
from app import create_app
from models.base import db
from models.user import Farmer
from models.crop import Crop, AgrarianPeriod, CropPeriodRule
from services.decision_engine import DecisionEngine

def test_all_edge_cases():
    """Simplified integration test for all edge cases"""
    app = create_app('testing')
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-key"
    })
    
    with app.app_context():
        # Enable FK for SQLite
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            from sqlalchemy import event
            event.listen(db.engine, 'connect', lambda c, _: c.execute('PRAGMA foreign_keys=ON'))
            
        db.create_all()
        
        # 1. Setup Data
        # Farmer
        farmer = Farmer(
            phone_number="12345", 
            password_hash="x", 
            governorate="Sfax", 
            farm_type="irrigated"
        )
        db.session.add(farmer)
        
        # Crop (Correctly fully populated)
        crop = Crop(
            name="TestCrop", 
            category="Vegetable", 
            min_temp=10, 
            max_temp=40,
            input_type='seeds_kg',
            yield_unit='kg'
        )
        db.session.add(crop)
        db.session.flush() # Ensure ID is generated for FK
        
        # Period
        period = AgrarianPeriod(
            id="P_EDGE", 
            name="E", 
            start_month=1, start_day=1, 
            end_month=12, end_day=31, 
            risk_level="low"
        )
        db.session.add(period)
        
        # Rule
        rule = CropPeriodRule(
            crop_id=crop.id, 
            period_id="P_EDGE", 
            suitability="optimal"
        )
        db.session.add(rule)
        
        db.session.commit()
        
        # 2. Setup Engine
        engine = DecisionEngine()
        
        # --- Scenario 1: Zero Price (Economic Collapse) ---
        # Mock weather to be normal
        engine.weather_service = MagicMock()
        engine.weather_service.get_forecast.return_value = [
            {'date': '2026-01-01', 'temp_min': 20, 'temp_max': 25, 'temp_avg': 22, 'rainfall': 0, 'humidity': 50}
        ]
        # Mock AI
        engine.ai_service = MagicMock()
        engine.ai_service.generate_explanation.return_value = "Zero price warning"
        
        # Execute
        result = engine.get_advice(farmer.id, crop.id, "Sfax", market_price=0.0)
        assert result['id'] is not None
        assert "Zero price warning" in result['explanation']
        
        # --- Scenario 2: Heatwave 50C (Climate Extremes) ---
        engine.weather_service.get_forecast.return_value = [
            {'date': '2026-01-01', 'temp_min': 30, 'temp_max': 50, 'temp_avg': 40, 'rainfall': 0, 'humidity': 10}
        ]
        result = engine.get_advice(farmer.id, crop.id, "Sfax")
        
        # Crop max=40, Weather max=50 => Should be WAIT
        assert result['decision']['action'] == 'WAIT'
        assert 50 > crop.max_temp
        
        # --- Scenario 3: Flood (Rainfall > 20mm) ---
        engine.weather_service.get_forecast.return_value = [
            {'date': '2026-01-01', 'temp_min': 20, 'temp_max': 25, 'temp_avg': 22, 'rainfall': 100, 'humidity': 90}
        ]
        result = engine.get_advice(farmer.id, crop.id, "Sfax")
        assert result['decision']['action'] == 'WAIT'
        
        # Cleanup
        db.session.remove()
        db.drop_all()
