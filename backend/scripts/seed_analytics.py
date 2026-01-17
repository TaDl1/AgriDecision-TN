from app import app, db
from models.user import Farmer
from models.decision import Decision, Outcome
from models.crop import Crop, AgrarianPeriod
from datetime import datetime, timedelta
import random
import logging
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOVERNORATES = [
    'Tunis', 'Ariana', 'Ben Arous', 'Manouba', 'Nabeul', 'Zaghouan',
    'Bizerte', 'Beja', 'Jendouba', 'Kef', 'Siliana', 'Kairouan',
    'Kasserine', 'Sidi Bouzid', 'Sousse', 'Monastir', 'Mahdia',
    'Sfax', 'Gabes', 'Medenine', 'Tataouine', 'Gafsa', 'Tozeur', 'Kebili'
]

def seed_analytics_data():
    """
    Seed database with comprehensive mock data for advanced analytics.
    Generates:
    1. 50 Peer Farmers across regions
    2. Historical decisions for them (~20 each)
    3. Outcomes demonstrating 'Advice Following' = Higher Success
    """
    
    with app.app_context():
        logger.info("🌱 Starting Analytics Data Seeding...")
        
        # 1. Create Peer Farmers (if not exist)
        farmers = []
        for i in range(50):
            phone = f"21699000{i:02d}"
            # Check if user exists (using filter instead of filter_by for safety if inheritance involved)
            farmer = Farmer.query.filter(Farmer.phone_number == phone).first()
            if not farmer:
                gov = random.choice(GOVERNORATES)
                farmer = Farmer(
                    phone_number=phone,
                    password_hash=generate_password_hash('password123'),
                    first_name=f"Farmer{i}",
                    last_name=f"Tunisi",
                    governorate=gov,
                    farm_type=random.choice(['irrigated', 'rain_fed']),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(100, 365))
                )
                db.session.add(farmer)
                farmers.append(farmer)
            else:
                farmers.append(farmer)
        
        db.session.commit()
        logger.info(f"✅ Verified/Created {len(farmers)} peer farmers")

        # Get crops & periods for reference
        crops = Crop.query.all()
        periods = AgrarianPeriod.query.all()
        
        if not crops or not periods:
            logger.error("❌ Crops or Periods missing. Run seed_crops/seed_rules first.")
            return

        # 2. Generate Decisions & Outcomes
        total_decisions = 0
        
        for farmer in farmers:
            # Each farmer makes 15-30 decisions over the last year
            num_decisions = random.randint(15, 30)
            
            for _ in range(num_decisions):
                # Random date in last 365 days
                days_ago = random.randint(1, 365)
                decision_date = datetime.utcnow() - timedelta(days=days_ago)
                
                crop = random.choice(crops)
                
                # Determine "Advice Quality" simulation
                # If PLANT_NOW is followed -> 85% success
                # If PLANT_NOW is ignored (waited) -> 40% success
                # If WAIT is followed -> Risk Avoided (Success)
                # If WAIT is ignored (planted) -> 30% success (failure likely)
                
                recommendation = random.choices(['PLANT_NOW', 'WAIT', 'NOT_RECOMMENDED'], weights=[0.4, 0.4, 0.2])[0]
                
                # Simulate Farmer Behavior (Compliance)
                # 70% chance to follow advice
                followed = random.random() < 0.7
                
                actual_action = 'unknown'
                advice_status = 'pending'
                
                if recommendation == 'PLANT_NOW':
                    if followed:
                        actual_action = 'planted_now'
                        advice_status = 'followed'
                    else:
                        actual_action = 'waited' # or not_planted
                        advice_status = 'ignored'
                elif recommendation == 'WAIT':
                    if followed:
                        actual_action = 'waited'
                        advice_status = 'followed'
                    else:
                        actual_action = 'planted_now'
                        advice_status = 'ignored'
                else: # NOT_RECOMMENDED
                    if followed:
                        actual_action = 'not_planted'
                        advice_status = 'followed'
                    else:
                        actual_action = 'planted_now'
                        advice_status = 'ignored'

                # Create Decision
                decision = Decision(
                    farmer_id=farmer.id,
                    crop_id=crop.id,
                    governorate=farmer.governorate,
                    recommendation=recommendation,
                    wait_days=0 if recommendation == 'PLANT_NOW' else 7,
                    confidence=random.choice(['HIGH', 'MEDIUM', 'HIGH']), # Skew high
                    explanation="Simulated historical advice",
                    period_id='P1', # Simplified
                    timestamp=decision_date,
                    advice_status=advice_status,
                    actual_action=actual_action,
                    action_recorded_at=decision_date + timedelta(days=1),
                    weather_risks="[]"
                )
                db.session.add(decision)
                db.session.flush() # Get ID
                
                # 3. generate Outcome (if it wasn't just "not_planted")
                if actual_action != 'not_planted':
                    # Determine success probability
                    success_prob = 0.5 # Default
                    
                    if advice_status == 'followed':
                        success_prob = 0.85 # High reward for following
                    else: # ignored
                        success_prob = 0.35 # Penalty for ignoring
                        
                    is_success = random.random() < success_prob
                    outcome_status = 'success' if is_success else 'failure'
                    
                    outcome = Outcome(
                        decision_id=decision.id,
                        outcome=outcome_status,
                        yield_kg=random.uniform(500, 2000) if is_success else random.uniform(0, 200),
                        revenue_tnd=random.uniform(1000, 5000) if is_success else 0,
                        notes="Simulated outcome",
                        recorded_at=decision_date + timedelta(days=90) # Harvest time
                    )
                    db.session.add(outcome)
                
                total_decisions += 1
                
        # 4. Ensure CURRENT USER (ID 1 usually) has specific data for AES
        # Need >=3 Followed and >=3 Ignored
        current_user = Farmer.query.get(1)
        if current_user:
            logger.info("🔧 Injecting specific AES test data for User 1...")
            
            # 5 Followed Decisions (4 Success, 1 Failure) -> 80% SR
            for _ in range(5):
                 d = Decision(
                     farmer_id=current_user.id, crop_id=crops[0].id, governorate=current_user.governorate,
                     recommendation='PLANT_NOW', confidence='HIGH', advice_status='followed', actual_action='planted_now',
                     timestamp=datetime.utcnow() - timedelta(days=60)
                 )
                 db.session.add(d)
                 db.session.flush()
                 # 4 successes
                 is_success = _ > 0 
                 o = Outcome(decision_id=d.id, outcome='success' if is_success else 'failure', decision=d)
                 db.session.add(o)

            # 5 Ignored Decisions (1 Success, 4 Failure) -> 20% SR
            for _ in range(5):
                 d = Decision(
                     farmer_id=current_user.id, crop_id=crops[0].id, governorate=current_user.governorate,
                     recommendation='WAIT', confidence='HIGH', advice_status='ignored', actual_action='planted_now',
                     timestamp=datetime.utcnow() - timedelta(days=60)
                 )
                 db.session.add(d)
                 db.session.flush()
                 # 1 success only
                 is_success = _ == 0
                 o = Outcome(decision_id=d.id, outcome='success' if is_success else 'failure', decision=d)
                 db.session.add(o)
                 
            logger.info("✅ AES test data injected: Expected AES ~ +60%")

        try:
            db.session.commit()
            logger.info(f"🚀 Successfully seeded {total_decisions} decisions across 50 farmers!")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to seed analytics: {e}")

if __name__ == '__main__':
    seed_analytics_data()
