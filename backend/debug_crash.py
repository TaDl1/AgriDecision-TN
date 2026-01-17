from app import create_app
from services.regional_analytics import RegionalAnalyticsService
from services.success_condition_analysis import SuccessConditionService
from models.user import Farmer
import traceback

app = create_app()

with app.app_context():
    # Use a known user ID (e.g., 71 from previous logs, or fetch first user)
    farmer = Farmer.query.first()
    if not farmer:
        print("No farmer found!")
        exit()
        
    user_id = farmer.id
    print(f"Testing for User ID: {user_id}, Gov: {farmer.governorate}")

    print("\n--- Testing Regional Benchmark ---")
    try:
        print("1. GSI...")
        RegionalAnalyticsService.calculate_gsi(farmer.governorate)
        print("2. PBD...")
        RegionalAnalyticsService.calculate_pbd(user_id, farmer.governorate)
        print("3. Top Crops (likely valid)...")
        RegionalAnalyticsService.get_top_crops_for_region(farmer.governorate)
        print("4. RRAP...")
        RegionalAnalyticsService.calculate_regional_risk_adjusted_performance(farmer.governorate)
        print("Regional Benchmark OK")
    except Exception:
        print("!!! Regional Benchmark CRASH !!!")
        traceback.print_exc()

    print("\n--- Testing Personal Insights ---")
    try:
        print("1. OCI...")
        SuccessConditionService.calculate_oci(user_id)
        print("2. MFSP...")
        SuccessConditionService.find_mfsp(user_id)
        print("Personal Insights OK")
    except Exception:
        print("!!! Personal Insights CRASH !!!")
        traceback.print_exc()
