
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.base import db
from models.user import Farmer
from models.decision import Decision, Outcome
from models.crop import Crop, AgrarianPeriod
from datetime import datetime, timedelta
import random
from seed_analytics import seed_analytics_data

def create_demo_user():
    with app.app_context():
        print("🌱 seeding analytics background data (peers)...")
        # Ensure peer data exists first
        seed_analytics_data()
        
        print("👤 Creating/Resetting Demo User...")
        # 1. Create Demo User
        phone = "22222222"
        demo_user = Farmer.query.filter_by(phone_number=phone).first()
        
        if demo_user:
            # Clear existing data for a clean slate
            Decision.query.filter_by(farmer_id=demo_user.id).delete()
            db.session.commit()
            print(f"   - Cleared existing data for {phone}")
        else:
            demo_user = Farmer(
                phone_number=phone,
                first_name="Demo",
                last_name="Farmer",
                governorate="Beja",
                farm_type="irrigated"
            )
            demo_user.set_password("password123")
            db.session.add(demo_user)
            db.session.commit()
            print(f"   - Created new user {phone}")

        # 2. Get Crops
        crops = Crop.query.all()
        if not crops:
            print("❌ No crops found! Run seed_crops.py first.")
            return

        wheat = next((c for c in crops if 'wheat' in c.name.lower() or 'ble' in c.name.lower()), crops[0])
        tomato = next((c for c in crops if 'tomato' in c.name.lower() or 'tomate' in c.name.lower()), crops[1])
        
        # 3. Generate History (Trend: Improving)
        # Months 6-4 ago: Chaotic/Ignoring advice
        # Months 3-0 ago: Following advice
        
        print("📅 Generating 6 months of history...")
        
        decisions_to_add = []
        outcomes_to_add = []
        
        current_time = datetime.utcnow()
        
        # Phase 1: 6 months ago to 3 months ago (Ignoring Advice)
        for i in range(10):
            days_ago = random.randint(90, 180)
            date = current_time - timedelta(days=days_ago)
            
            # Recommendation: WAIT (but they plant) or PLANT (but they wait)
            decision = Decision(
                farmer_id=demo_user.id,
                crop_id=random.choice([wheat.id, tomato.id]),
                governorate=demo_user.governorate,
                recommendation='WAIT', 
                confidence='HIGH',
                explanation="Demo: Ignored advice phase",
                period_id='P1',
                timestamp=date,
                advice_status='ignored',
                actual_action='planted_now',
                weather_risks='["frost_risk"]'
            )
            db.session.add(decision)
            db.session.flush()
            
            # Outcome: Failure or Low Yield
            outcome = Outcome(
                decision_id=decision.id,
                outcome='failure',
                yield_kg=random.uniform(100, 500),
                revenue_tnd=random.uniform(0, 300),
                recorded_at=date + timedelta(days=90)
            )
            db.session.add(outcome)

        # Phase 2: 3 months ago to Now (Following Advice)
        for i in range(15):
            days_ago = random.randint(10, 90)
            date = current_time - timedelta(days=days_ago)
            
            decision = Decision(
                farmer_id=demo_user.id,
                crop_id=random.choice([wheat.id, tomato.id]),
                governorate=demo_user.governorate,
                recommendation='PLANT_NOW', 
                confidence='HIGH',
                explanation="Demo: Following advice phase",
                period_id='P1',
                timestamp=date,
                advice_status='followed',
                actual_action='planted_now',
                weather_risks='[]'
            )
            db.session.add(decision)
            db.session.flush()
            
            # Outcome: Success
            outcome = Outcome(
                decision_id=decision.id,
                outcome='success',
                yield_kg=random.uniform(2000, 5000),
                revenue_tnd=random.uniform(4000, 10000),
                recorded_at=date + timedelta(days=90)
            )
            db.session.add(outcome)

        db.session.commit()
        print(f"✅ Created Demo Account: Phone={phone}, Pass=password123")
        print("   - 10 Ignored decisions (older)")
        print("   - 15 Followed decisions (recent)")
        print("   - Ready for Analytics validation.")

if __name__ == "__main__":
    create_demo_user()
