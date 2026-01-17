
import sys
import os
import traceback
from app import create_app
from services.analytics_service import AnalyticsService
from models.user import Farmer
from models.decision import Decision

app = create_app()
service = AnalyticsService()

with app.app_context():
    print("--- STARTING ROBUST ANALYTICS TEST ---")
    users = Farmer.query.all()
    print(f"Found {len(users)} users.")
    
    success_count = 0
    fail_count = 0
    
    for user in users:
        print(f"\nUser {user.id} ({user.governorate}):")
        
        # Check raw data
        decisions = Decision.query.filter_by(farmer_id=user.id).count()
        print(f"  Decisions (Raw): {decisions}")
        
        try:
            data = service.get_dashboard_data(user.id, 'monthly')
            if not data:
                print("  -> FAILED (Returned empty dict/None)")
                fail_count += 1
            else:
                print(f"  -> SUCCESS. Keys: {list(data.keys())}")
                print(f"     AES: {data.get('advice_effectiveness_score')}")
                success_count += 1
        except Exception:
            print("  -> CRASHED:")
            traceback.print_exc()
            fail_count += 1
            
    print(f"\n--- SUMMARY: Success={success_count}, Failed={fail_count} ---")
