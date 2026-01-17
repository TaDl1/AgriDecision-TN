
from app import create_app
from services.analytics_service import AnalyticsService
from models.user import Farmer
import json

app = create_app()
with app.app_context():
    service = AnalyticsService()
    farmers = Farmer.query.all()
    print(f"Found {len(farmers)} farmers.")
    
    for f in farmers:
        try:
            print(f"Testing User {f.id} ({f.phone_number})...", end=' ')
            data = service.get_dashboard_data(f.id)
            if 'error' in data:
                print(f"FAILED (Internal Error): {data['error']}")
            else:
                print("SUCCESS")
                # Validate some expected keys
                missing = [k for k in ['success_rate', 'savings_tnd', 'regional_data', 'personal_insights', 'crop_accuracy', 'strategic_advice', 'smart_summary'] if k not in data]
                if missing:
                    print(f"  WARNING: Missing keys: {missing}")
        except Exception as e:
            print(f"CRASHED: {e}")
            import traceback
            traceback.print_exc()
