
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.analytics_service import AnalyticsService
from app import app
from models.base import db
from models.user import Farmer

def verify_analytics():
    with app.app_context():
        # Ensure we have a farmer
        farmer = Farmer.query.first()
        if not farmer:
            print("No farmer found to test with.")
            return

        print(f"Testing with Farmer ID: {farmer.id}")
        
        service = AnalyticsService()
        data = service.get_dashboard_data(farmer.id)
        
        if "error" in data:
            print(f"Error returned: {data['error']}")
            return

        # Check Strategic Advice
        if "strategic_advice" in data:
            print("[PASS] strategic_advice is present.")
            advice = data['strategic_advice']
            print(f"  - Financial Tips: {len(advice.get('financial', []))}")
        else:
            print("[FAIL] strategic_advice is MISSING.")
            
        # Check Interpretation logic
        interp = data.get('interpretation')
        print(f"Top-level Interpretation: {interp}")
        
        # Check RAR results in metrics
        if 'metrics' in data and 'savings_rar' in data['metrics']:
            rar = data['metrics']['savings_rar']
            print("RAR Results in metrics:", rar)
        else:
            print("RAR Results MISSING from metrics.")
            
        print("Verification Complete.")
        
        # --- NEW VERIFICATION ---
        print("\n--- Verifying Agrarian Trends ---")
        trends = service.calculate_performance_trends(farmer.id, timeframe='agrarian')
        print(f"Agrarian Trends Result Type: {type(trends)}")
        if isinstance(trends, dict) and 'data' in trends:
            print(f"Data Points Found: {len(trends['data'])}")
            print(f"First Period: {trends['data'][0] if trends['data'] else 'None'}")
        
        print("\n--- Verifying Dynamic Growth Targets ---")
        if "strategic_advice" in data and "strategy" in data["strategic_advice"]:
            growth_advice = data["strategic_advice"]["strategy"]
            print(f"Growth Advice Items ({len(growth_advice)}):")
            for i, item in enumerate(growth_advice):
                print(f"[{i}] {item[:100]}...") # Print start of item
            
            # Look for PATH
            for item in growth_advice:
                if "GROWTH PATH" in item:
                    print(f"Found Growth Path item:\n{item}")
                    if "Target 80%" in item:
                        print("[WARNING] 'Target 80%' found - verify if this is appropriate for current SR.")
                    break

if __name__ == "__main__":
    verify_analytics()
