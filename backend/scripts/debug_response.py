from app import create_app
from services.analytics_service import AnalyticsService
from models.user import Farmer
import json

def debug_response():
    app = create_app()
    with app.app_context():
        service = AnalyticsService()
        # Find a farmer with some data or use the one from seeds
        farmer = Farmer.query.first()
        if not farmer:
            print("No farmers found")
            return
            
        print(f"Checking data for Farmer ID: {farmer.id} ({farmer.governorate})")
        data = service.get_dashboard_data(farmer.id)
        
        # Check for key variables at root
        required_keys = [
            'success_rate', 'savings_tnd', 'risk_avoided_count', 
            'performance_trends', 'smart_summary', 'regional_data'
        ]
        
        print("\n--- Root Keys Status ---")
        for key in required_keys:
            val = data.get(key, 'MISSING')
            print(f"{key}: {val if key != 'performance_trends' else len(val) if isinstance(val, list) else 'NOT A LIST'}")

        print("\n--- Full JSON Structure (Excerpt) ---")
        print(json.dumps(data, indent=2)[:1000])

if __name__ == "__main__":
    debug_response()
