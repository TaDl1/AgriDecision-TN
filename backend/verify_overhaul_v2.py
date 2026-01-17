
import os
import sys
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from models.base import db
from models.user import Farmer
from models.crop import Crop
from models.decision import Decision, Outcome
from services.analytics_service import AnalyticsService

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        # Fallback for Windows console with limited encoding
        print(msg.encode('ascii', 'ignore').decode('ascii'))

def verify_v2():
    app = create_app()
    with app.app_context():
        service = AnalyticsService()
        
        # Cleanup old test users if they exist
        Farmer.query.filter(Farmer.phone_number.in_(["111", "222"])).delete()
        db.session.commit()
        
        # 1. Create Test Farmers for different regions
        sfax_farmer = Farmer(phone_number="111", governorate="Sfax", farm_type="Smallholder")
        sfax_farmer.set_password("pass")
        nabeul_farmer = Farmer(phone_number="222", governorate="Nabeul", farm_type="Smallholder")
        nabeul_farmer.set_password("pass")
        db.session.add_all([sfax_farmer, nabeul_farmer])
        db.session.commit()
        
        safe_print("\nTEST 1: New User Logic (Regional Hero Crops)")
        sfax_data = service.get_dashboard_data(sfax_farmer.id)
        nabeul_data = service.get_dashboard_data(nabeul_farmer.id)
        
        sfax_advice = sfax_data['strategy']['production'][1]
        nabeul_advice = nabeul_data['strategy']['production'][1]
        
        safe_print(f"Sfax Advice: {sfax_advice}")
        safe_print(f"Nabeul Advice: {nabeul_advice}")
        
        assert "Olive" in sfax_advice or "Almond" in sfax_advice
        assert "Citrus" in nabeul_advice
        safe_print("TEST 1 PASSED: Regional Hero recommendations are correct.")

        safe_print("\nTEST 2: Bayesian Dampening (1/1 != 100%)")
        # Add 1 success to Sfax farmer
        olive = Crop.query.filter_by(name="Olive").first()
        d = Decision(
            farmer_id=sfax_farmer.id, 
            crop_id=olive.id, 
            governorate=sfax_farmer.governorate, 
            confidence=0.8, 
            advice_status='followed', 
            recommendation='PLANT'
        )
        db.session.add(d)
        db.session.flush()
        o = Outcome(decision_id=d.id, outcome='success', yield_kg=100)
        db.session.add(o)
        db.session.commit()
        
        dampened_data = service.get_dashboard_data(sfax_farmer.id)
        sr = dampened_data['production']['success_rate']
        safe_print(f"Success Rate for 1/1 outcome: {sr}%")
        assert sr < 100
        assert sr == 60.0 # (1+2)/(1+4) = 3/5 = 60%
        safe_print("TEST 2 PASSED: Bayesian dampening prevented artificial 100%.")

        safe_print("\nTEST 3: Dashboard Structure (Non-Redundant)")
        keys = list(dampened_data.keys())
        expected = ['executive_summary', 'production', 'financial', 'growth', 'strategy']
        safe_print(f"Dashboard Keys: {keys}")
        for k in expected:
            assert k in dampened_data
        
        # Check canonical success rate
        exec_sr = dampened_data['executive_summary']['success_rate']
        prod_sr = dampened_data['production']['success_rate']
        assert exec_sr == prod_sr
        safe_print("TEST 3 PASSED: Dashboard structure is clean and canonical.")

        safe_print("\nTEST 4: Profile Personalization")
        profile_text = dampened_data['strategy']['production'][0]
        safe_print(f"Personalized Profile: {profile_text}")
        assert "Sfax" in profile_text
        safe_print("TEST 4 PASSED: Profile includes regional context.")

        # Cleanup
        Farmer.query.filter(Farmer.phone_number.in_(["111", "222"])).delete()
        db.session.commit()
        safe_print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    verify_v2()
