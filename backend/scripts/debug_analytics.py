
from app import app
from models.base import db
from services.regional_analytics import RegionalAnalyticsService
from models.user import Farmer

def debug_analytics():
    with app.app_context():
        # Get Demo User
        u = Farmer.query.filter_by(phone_number="22222222").first()
        if not u:
            print("Demo user not found!")
            return

        print(f"User ID: {u.id}, Gov: {u.governorate}")

        # Check raw counts (using internal logic of RegionalAnalyticsService)
        # 1. GSI (Governorate Success Index)
        print("\n--- GSI Debug ---")
        gsi = RegionalAnalyticsService.calculate_gsi(u.governorate)
        print(f"GSI Result: {gsi}")
        
        # 2. PBD (Personal Benchmark)
        print("\n--- PBD Debug ---")
        pbd = RegionalAnalyticsService.calculate_pbd(u.id, u.governorate)
        print(f"PBD Result: {pbd}")

        # 3. Decision Count manually
        dec_count = len(u.decisions.all())
        print(f"\nTotal Decisions for user: {dec_count}")


if __name__ == "__main__":
    debug_analytics()
