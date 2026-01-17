from app import create_app
from models.base import db
from models.user import Farmer
from models.crop import Crop, AgrarianPeriod, CropPeriodRule
from services.decision_engine import DecisionEngine
from unittest.mock import MagicMock  # We'll patch manually or just run without patches if possible

def debug_run():
    # Setup app in test mode
    app = create_app('testing')
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-key"
    })
    
    with app.app_context():
        db.create_all()
        print("✅ DB Created")
        
        # 1. Create Farmer
        farmer = Farmer(
            phone_number="12345678",
            password_hash="pw",
            governorate="Sfax",
            farm_type="irrigated"
        )
        db.session.add(farmer)
        db.session.commit()
        print(f"✅ Farmer Created: ID={farmer.id}")
        
        # 2. Create Crop & Period
        crop = Crop(
            name="Debug Crop",
            category="Test",
            min_temp=10, max_temp=40
        )
        db.session.add(crop)
        db.session.flush()
        print(f"✅ Crop Created: ID={crop.id}")
        
        period = AgrarianPeriod(
            id="P_DEBUG",
            name="Debug Period",
            start_month=1, start_day=1,
            end_month=12, end_day=31,
            risk_level="low"
        )
        db.session.add(period)
        
        rule = CropPeriodRule(
            crop_id=crop.id,
            period_id="P_DEBUG",
            suitability="optimal"
        )
        db.session.add(rule)
        db.session.commit()
        print("✅ Period & Rule Created")
        
        # 3. Call Decision Engine
        engine = DecisionEngine()
        
        # Mock weather service to avoid external API calls
        mock_weather = MagicMock()
        mock_weather.get_forecast.return_value = [
            {'date': '2026-01-01', 'temp_min': 20, 'temp_max': 30, 'temp_avg': 25, 'rainfall': 0, 'humidity': 50}
        ]
        engine.weather_service = mock_weather
        
        # Mock AI to avoid API calls
        mock_ai = MagicMock()
        mock_ai.generate_explanation.return_value = "Debug explanation"
        engine.ai_service = mock_ai
        
        print("🚀 Invoking get_advice...")
        try:
            result = engine.get_advice(
                farmer_id=farmer.id,
                crop_id=crop.id,
                governorate="Sfax"
            )
            print(f"✅ Success! Decision ID: {result.get('id')}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_run()
