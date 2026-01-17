"""
Check demo user data in database
"""
from app import app
from models.decision import Decision
from models.user import Farmer
from models.base import db

with app.app_context():

    # Find demo user
    farmer = Farmer.query.filter_by(phone_number='22222222').first()
    
    if not farmer:
        print("❌ Demo user NOT FOUND")
    else:
        print(f"✅ Demo User Found - ID: {farmer.id}")
        print(f"   Name: {farmer.first_name} {farmer.last_name}")
        print(f"   Governorate: {farmer.governorate}")
        
        # Get decisions
        decisions = Decision.query.filter_by(farmer_id=farmer.id).all()
        print(f"\n📊 Total Decisions: {len(decisions)}")
        
        # Count outcomes
        with_outcomes = [d for d in decisions if d.outcome]
        print(f"   With Outcomes: {len(with_outcomes)}")
        
        # Count advice status
        with_advice_status = [d for d in decisions if d.advice_status]
        print(f"   With Advice Status: {len(with_advice_status)}")
        
        # Show sample decisions
        if decisions:
            print("\n📋 Sample Decisions:")
            for i, dec in enumerate(decisions[:5], 1):
                print(f"   {i}. Crop: {dec.crop.name if dec.crop else 'Unknown'}")
                print(f"      Recommendation: {dec.recommendation}")
                print(f"      Advice Status: {dec.advice_status}")
                outcome = dec.outcomes.first() if dec.outcomes.count() \u003e 0 else None
                if outcome:
                    print(f"      Outcome: {outcome.outcome}")
                print()
