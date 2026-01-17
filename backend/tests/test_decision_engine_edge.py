import pytest
from unittest.mock import MagicMock, patch
from services.decision_engine import DecisionEngine
from models.crop import Crop, AgrarianPeriod, CropPeriodRule
from models.user import Farmer
from models.base import db

@pytest.fixture
def engine():
    return DecisionEngine()

@pytest.fixture
def mock_farmer(app):
    with app.app_context():
        # Clean up any existing records to avoid phone number conflicts
        Farmer.query.delete()
        farmer = Farmer(
            phone_number="21600000000",
            password_hash="pw",
            governorate="Sfax",
            farm_type="irrigated"
        )
        db.session.add(farmer)
        db.session.commit()
        return farmer

@pytest.fixture
def mock_crop(app):
    with app.app_context():
        # Clean up existing to be safe
        Crop.query.delete()
        AgrarianPeriod.query.delete()
        
        crop = Crop(
            name="Test Tomato",
            category="Vegetable",
            min_temp=10,
            max_temp=35,
            water_needs="medium"
        )
        db.session.add(crop)
        db.session.flush() # Ensure ID is generated
        
        # Add a period and rule
        period = AgrarianPeriod(
            id="P_EDGE",
            name="Edge Period",
            start_month=1, start_day=1,
            end_month=12, end_day=31,
            risk_level="low"
        )
        db.session.add(period)
        
        rule = CropPeriodRule(
            crop_id=crop.id,
            period_id="P_EDGE",
            suitability="optimal"
        )
        db.session.add(rule)
        db.session.commit()
        return crop

@patch('services.weather_service.WeatherService.get_forecast')
@patch('services.ai_service.AIService.generate_explanation')
def test_economic_edge_zero_price(mock_ai, mock_weather, engine, app, mock_farmer, mock_crop):
    """Test decision logic when market price is zero (extreme crash)"""
    mock_weather.return_value = [
        {'date': '2026-01-14', 'temp_min': 20, 'temp_max': 25, 'temp_avg': 22, 'rainfall': 0}
    ]
    mock_ai.return_value = "Price is 0, reconsider."
    
    with app.app_context():
        advice = engine.get_advice(
            farmer_id=mock_farmer.id,
            crop_id=mock_crop.id,
            governorate=mock_farmer.governorate,
            seedling_cost=5.0,
            market_price=0.0,
            input_quantity=100
        )
        
        assert advice['id'] is not None
        assert advice['explanation'] == "Price is 0, reconsider."

@patch('services.weather_service.WeatherService.get_forecast')
def test_climate_edge_extreme_heat(mock_weather, engine, app, mock_farmer, mock_crop):
    """Test decision logic during a 50C heatwave"""
    mock_weather.return_value = [
        {'date': '2026-01-14', 'temp_min': 40, 'temp_max': 50, 'temp_avg': 45, 'rainfall': 0}
    ]
    
    with app.app_context():
        advice = engine.get_advice(mock_farmer.id, mock_crop.id, mock_farmer.governorate)
        assert advice['decision']['action'] == 'WAIT'

@patch('services.weather_service.WeatherService.get_forecast')
def test_climate_edge_flood(mock_weather, engine, app, mock_farmer, mock_crop):
    """Test decision logic during a flood (extreme rain)"""
    mock_weather.return_value = [
        {'date': '2026-01-14', 'temp_min': 20, 'temp_max': 25, 'temp_avg': 22, 'rainfall': 150}
    ]
    
    with app.app_context():
        advice = engine.get_advice(mock_farmer.id, mock_crop.id, mock_farmer.governorate)
        assert advice['decision']['action'] == 'WAIT'

def test_missing_period_rule_fallback(engine, app, mock_farmer):
    """Test fallback logic when no crop rule is defined for the period"""
    with app.app_context():
        # Ensure a period exists so _get_current_period doesn't fail
        if not AgrarianPeriod.query.first():
            p = AgrarianPeriod(id="P_FALLBACK", name="Fallback", start_month=1, start_day=1, end_month=12, end_day=31)
            db.session.add(p)
            db.session.commit()
            
        crop = Crop(name="Lonely Onion", category="Vegetable", min_temp=5, max_temp=40)
        db.session.add(crop)
        db.session.commit()
        
        with patch('services.weather_service.WeatherService.get_forecast') as mock_w:
            mock_w.return_value = [{'date': '2026-01-14', 'temp_min': 20, 'temp_max': 25, 'temp_avg': 22, 'rainfall': 0}]
            advice = engine.get_advice(mock_farmer.id, crop.id, "Sfax")
            assert advice['decision']['action'] == 'WAIT'
            assert "No specific guidance" in advice['decision']['reason']
