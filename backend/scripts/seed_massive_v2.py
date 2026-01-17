
import random
from datetime import datetime, timedelta
from app import app
from models.base import db
from models.user import Farmer
from models.crop import Crop, AgrarianPeriod
from models.decision import Decision, Outcome

def seed_massive():
    with app.app_context():
        # Get all farmers
        farmers = Farmer.query.all()
        crops = Crop.query.all()
        periods = AgrarianPeriod.query.all()
        
        if not farmers or not crops:
            print("❌ No farmers or crops found. Run primary seed first.")
            return

        print(f"🚜 Starting massive seed for {len(farmers)} farmers...")
        
        # Performance mapping for variety
        # skill_map = {f.id: random.uniform(0.5, 0.9) for f in farmers}
        
        for farmer in farmers:
            print(f"  - Seeding {farmer.first_name} ({farmer.governorate})...")
            
            # 100 decisions over 10 months
            for days_ago in range(300, 0, -3):
                ts = datetime.utcnow() - timedelta(days=days_ago)
                crop = random.choice(crops)
                
                # Alternate between PLANT_NOW and WAIT
                reco = random.choice(['PLANT_NOW', 'WAIT', 'NOT_RECOMMENDED'])
                
                # Record decision
                decision = Decision(
                    farmer_id=farmer.id,
                    crop_id=crop.id,
                    governorate=farmer.governorate,
                    recommendation=reco,
                    confidence=random.choice(['HIGH', 'MEDIUM']),
                    explanation="Automated massive seed data for analytics validation.",
                    period_id=random.choice(periods).id,
                    timestamp=ts,
                    weather_temp_avg=random.uniform(15, 30),
                    weather_humidity=random.uniform(40, 80),
                    weather_rainfall=random.uniform(0, 50),
                    weather_risks="[]"
                )
                
                # Most follow, some ignore
                if random.random() < 0.8:
                    if reco == 'PLANT_NOW': action = 'planted_now'
                    elif reco == 'WAIT': action = 'waited'
                    else: action = 'not_planted'
                    status = 'followed'
                else:
                    action = 'planted_now' if random.random() > 0.5 else 'waited'
                    status = 'ignored'
                
                decision.actual_action = action
                decision.advice_status = status
                db.session.add(decision)
                db.session.flush() # Get ID
                
                # Create outcomes for plantings
                if action == 'planted_now':
                    # Skill-based success
                    skill = 0.5 + (farmer.id % 5) * 0.1 # Varying skill levels 0.5 to 0.9
                    is_success = random.random() < skill
                    
                    outcome = Outcome(
                        decision_id=decision.id,
                        outcome='success' if is_success else 'failure',
                        yield_kg=random.uniform(500, 2000) if is_success else random.uniform(50, 300),
                        revenue_tnd=random.uniform(1000, 5000) if is_success else random.uniform(0, 500),
                        recorded_at=ts + timedelta(days=60) # Harvest 2 months later
                    )
                    db.session.add(outcome)
            
            db.session.commit()
            print(f"    ✅ Done for {farmer.first_name}")

        print("✨ Massive seeding complete!")

if __name__ == "__main__":
    seed_massive()
