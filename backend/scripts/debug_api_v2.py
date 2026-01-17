
from app import create_app
from services.analytics_service import AnalyticsService
import json

app = create_app()
with app.app_context():
    service = AnalyticsService()
    # Find a user with some data if possible
    from models.user import Farmer
    farmer = Farmer.query.first()
    if not farmer:
        print("No farmer found.")
    else:
        print(f"User ID: {farmer.id}")
        data = service.get_dashboard_data(farmer.id)
        print("Response Keys:", list(data.keys()))
        if 'error' in data:
            print("ERROR found in response:", data['error'])
        else:
            print("Success Rate:", data.get('success_rate'))
            print("Regional Data Keys:", list(data.get('regional_data', {}).keys()))
            print("Savings TND:", data.get('savings_tnd'))
