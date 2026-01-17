
from app import create_app
from services.analytics_service import AnalyticsService
import json
import sys
import os

sys.path.append(os.getcwd())
app = create_app()

def verify():
    with app.app_context():
        service = AnalyticsService()
        # Use first farmer in DB
        from models.user import Farmer
        farmer = Farmer.query.first()
        if not farmer:
            print("No farmer found to test.")
            return
        
        print(f"Testing analytics for Farmer: {farmer.id} ({farmer.governorate})")
        data = service.get_dashboard_data(farmer.id)
        
        print("\nStructured Response Check:")
        if 'metrics' in data and 'summary' in data:
            print("✅ Root structure correct")
            
            # Check success_rate
            sr = data['metrics'].get('success_rate', {})
            if 'reliability_tier' in sr and 'data_sufficiency' in sr:
                print(f"✅ success_rate metadata present (Tier: {sr['reliability_tier']}, DRS: {sr['data_sufficiency']})")
            else:
                print("❌ success_rate metadata missing")
                
            # Check advice_uplift
            uplift = data['metrics'].get('advice_uplift', {})
            if 'confidence_interval' in uplift and 'calculation_method' in uplift:
                print(f"✅ advice_uplift metadata present (Method: {uplift['calculation_method']})")
            else:
                print("❌ advice_uplift metadata missing")
                
            # Check summary
            summary = data.get('summary', {})
            if 'data_reliability_score' in summary and 'insight_level' in summary:
                print(f"✅ summary metadata present (Level: {summary['insight_level']})")
            else:
                print("❌ summary metadata missing")
        else:
            print("❌ Root structure incorrect")
            
        print("\nFull Data Preview:")
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    verify()
