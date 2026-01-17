import sys
import os
sys.path.append(os.path.abspath('backend'))

print("Testing imports...")

try:
    from app import create_app
    print("✓ App import successful")
    
    app = create_app()
    print("✓ App created successfully")
    
    with app.app_context():
        from models.base import db
        print("✓ Database import successful")
        
        from models.user import Farmer
        print("✓ Farmer model import successful")
        
        from models.analytics import FarmerAnalytics, AnalyticsEvent
        print("✓ Analytics models import successful")
        
        from services.truthful_engine import TruthfulAnalyticsEngine
        print("✓ TruthfulAnalyticsEngine import successful")
        
        # Test a simple query
        farmer_count = Farmer.query.count()
        print(f"✓ Database query successful - {farmer_count} farmers in database")
        
        print("\n✅ ALL IMPORTS AND BASIC OPERATIONS SUCCESSFUL")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
