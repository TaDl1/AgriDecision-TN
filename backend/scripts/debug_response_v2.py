from app import create_app
from services.analytics_service import AnalyticsService
from models.user import Farmer
import json

def debug_response():
    app = create_app()
    with app.app_context():
        service = AnalyticsService()
        # Find a farmer in Sfax if possible
        farmer = Farmer.query.filter_by(governorate='Sfax').first() or Farmer.query.first()
        if not farmer:
            print("No farmers found")
            return
            
        print(f"Checking data for Farmer ID: {farmer.id} ({farmer.governorate})")
        data = service.get_dashboard_data(farmer.id)
        
        print("\n--- Crop Performance (Should be dampened) ---")
        for crop in data.get('production', {}).get('crop_performance', []):
            print(f"{crop['crop']}: SR={crop['success_rate']}%, Raw={crop['raw_sr']}%, Weight={crop['suitability_weight']}, WeightedScore={crop['weighted_score']}")
            if crop['raw_sr'] == 100.0 and crop['success_rate'] == 100.0:
                print("--- ERROR: 100% SR not dampened! ---")

        print("\n--- Production Strategy (Should include region) ---")
        for item in data.get('strategy', {}).get('production', []):
            # Strip emojis for display
            clean_item = item.encode('ascii', 'ignore').decode('ascii')
            print(f"- {clean_item}")

if __name__ == "__main__":
    debug_response()
