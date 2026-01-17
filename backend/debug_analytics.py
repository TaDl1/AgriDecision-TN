from app import create_app
from models.base import db
from services.advanced_analytics import AdvancedAnalyticsService
import traceback

app = create_app()

with app.app_context():
    user_id = 71
    print(f"Testing analytics for user {user_id}...")
    
    try:
        print("1. Calculating AES...")
        aes = AdvancedAnalyticsService.calculate_aes(user_id)
        print(f"AES Result: {aes}")
    except Exception:
        traceback.print_exc()

    try:
        print("\n2. Calculating FCI...")
        fci = AdvancedAnalyticsService.calculate_fci(user_id)
        print(f"FCI Result: {fci}")
    except Exception:
        traceback.print_exc()

    try:
        print("\n3. Calculating RAR...")
        rar = AdvancedAnalyticsService.calculate_rar(user_id)
        print(f"RAR Result: {rar}")
    except Exception:
        traceback.print_exc()

    try:
        print("\n4. Calculating CVS...")
        cvs = AdvancedAnalyticsService.calculate_cvs(user_id)
        print(f"CVS Result: {cvs}")
    except Exception:
        traceback.print_exc()

    try:
        print("\n5. Calculating TLS...")
        tls = AdvancedAnalyticsService.calculate_tls(user_id)
        print(f"TLS Result: {tls}")
    except Exception:
        traceback.print_exc()

    try:
        print("\n6. Calculating CSAA...")
        csaa = AdvancedAnalyticsService.calculate_csaa(user_id)
        print(f"CSAA Result: {csaa}")
    except Exception:
        traceback.print_exc()

    try:
        from services.regional_analytics import RegionalAnalyticsService
        from models.user import Farmer
        farmer = Farmer.query.get(user_id)
        
        print("\n7. Calculating DOI...")
        doi = RegionalAnalyticsService.calculate_doi(farmer.governorate, user_id)
        print(f"DOI Result: {doi}")
        
        print("\n8. Calculating OGA...")
        oga = RegionalAnalyticsService.calculate_oga(farmer.governorate)
        print(f"OGA Result: {oga}")
        
        print("\n9. Calculating Trends...")
        trends = AdvancedAnalyticsService.calculate_performance_trends(user_id)
        print(f"Trends Result: {trends}")
        
    except Exception:
        traceback.print_exc()
