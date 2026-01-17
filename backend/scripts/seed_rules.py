from app import app, db
from models.crop import Crop, CropPeriodRule, AgrarianPeriod
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_rules():
    """Seed the database with crop period rules for new crops"""
    
    # Define rules for the new crops
    # Period P1 (Jan 1 - Feb 14) - Winter Dormancy
    # Recommended: Fava Beans, Garlic, Winter Spinach, Artichoke, Green Peas
    
    with app.app_context():
        # Ensure periods exist (if not, you might need to seed them too, but assuming P1 exists)
        p1 = AgrarianPeriod.query.get('P1')
        if not p1:
            logger.info("Seeding P1 period first...")
            p1 = AgrarianPeriod(
                id='P1', name='Winter Dormancy', 
                start_month=1, start_day=1, 
                end_month=2, end_day=14, 
                risk_level='medium',
                description='Winter period with cold temperatures and frost risk.'
            )
            db.session.add(p1)
            db.session.commit()
            
        crops_p1_optimal = [
            'Fava Beans', 'Garlic', 'Winter Spinach', 'Artichoke', 'Green Peas'
        ]
        
        for crop_name in crops_p1_optimal:
            crop = Crop.query.filter_by(name=crop_name).first()
            if not crop:
                logger.warning(f"Crop {crop_name} not found!")
                continue
                
            # Check if rule exists
            existing_rule = CropPeriodRule.query.filter_by(
                crop_id=crop.id,
                period_id='P1'
            ).first()
            
            if not existing_rule:
                new_rule = CropPeriodRule(
                    crop_id=crop.id,
                    period_id='P1',
                    suitability='optimal',
                    reason=f'Perfect time for planting {crop_name} in cool weather.'
                )
                db.session.add(new_rule)
                logger.info(f"Added P1 rule for {crop_name}")
            else:
                logger.info(f"Rule already exists for {crop_name} in P1")
                # Update to optimal just in case
                existing_rule.suitability = 'optimal'

        # Period P4/P5 for Heat lovers (Watermelon, Okra, etc.)
        p5 = AgrarianPeriod.query.get('P5')
        if not p5:
             # Basic fallback creation if P5 missing
             p5 = AgrarianPeriod(
                id='P5', name='Early Summer',
                start_month=6, start_day=15, end_month=7, end_day=31,
                risk_level='medium'
             )
             db.session.add(p5)
             db.session.commit()

        crops_p5_optimal = ['Okra', 'Watermelon', 'Hot Peppers']
        for crop_name in crops_p5_optimal:
             crop = Crop.query.filter_by(name=crop_name).first()
             if not crop: continue
             
             rule = CropPeriodRule.query.filter_by(crop_id=crop.id, period_id='P5').first()
             if not rule:
                 db.session.add(CropPeriodRule(
                     crop_id=crop.id, period_id='P5', 
                     suitability='optimal', 
                     reason='High heat required for growth.'
                 ))
                 logger.info(f"Added P5 rule for {crop_name}")

        try:
            db.session.commit()
            print("Successfully seeded crop period rules.")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding rules: {e}")

if __name__ == '__main__':
    seed_rules()
