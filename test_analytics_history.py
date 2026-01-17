"""
Test script to verify analytics and history functionality
"""
import sys
import os
sys.path.append(os.path.abspath('backend'))

from app import create_app
from models.base import db
from models.user import Farmer
from models.decision import Decision, Outcome
from models.crop import Crop
from services.analytics_service import AnalyticsService
import random
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("=" * 60)
    print("TESTING ANALYTICS & HISTORY FUNCTIONALITY")
    print("=" * 60)
    
    # Get first farmer
    farmer = Farmer.query.first()
    if not farmer:
        print("❌ No farmers found in database")
        sys.exit(1)
    
    print(f"\n✓ Testing with farmer: {farmer.first_name} {farmer.last_name} (ID: {farmer.id})")
    
    # Check existing decisions
    existing_decisions = Decision.query.filter_by(farmer_id=farmer.id).count()
    print(f"✓ Existing decisions: {existing_decisions}")
    
    # Add some test data if needed
    if existing_decisions < 5:
        print("\n📊 Adding test data...")
        crops = Crop.query.limit(3).all()
        
        for i in range(10):
            crop = random.choice(crops)
            recommendation = random.choice(['PLANT_NOW', 'WAIT', 'NOT_RECOMMENDED'])
            advice_status = random.choice(['followed', 'ignored'])
            
            d = Decision(
                farmer_id=farmer.id,
                crop_id=crop.id,
                governorate=farmer.governorate or 'Tunis',
                recommendation=recommendation,
                confidence='HIGH',
                advice_status=advice_status,
                actual_action='planted_now' if advice_status == 'followed' else 'waited',
                weather_temp_avg=random.randint(15, 30),
                seedling_cost_tnd=random.uniform(50, 200),
                market_price_tnd=random.uniform(1.5, 3.5),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            db.session.add(d)
            db.session.flush()
            
            # Add outcome
            is_success = (advice_status == 'followed' and recommendation == 'PLANT_NOW')
            outcome = Outcome(
                decision_id=d.id,
                outcome='success' if is_success else 'failure',
                yield_kg=random.randint(500, 2000) if is_success else random.randint(0, 500),
                revenue_tnd=random.randint(1000, 4000) if is_success else random.randint(0, 1000),
                notes=f"Test outcome {i+1}"
            )
            db.session.add(outcome)
        
        db.session.commit()
        print(f"✓ Added 10 test decisions with outcomes")
    
    # Test analytics service
    print("\n📈 Testing Analytics Service...")
    analytics_service = AnalyticsService()
    
    try:
        dashboard_data = analytics_service.get_dashboard_data(farmer.id, 'monthly')
        print(f"✓ Analytics data retrieved successfully")
        print(f"  - Total decisions: {dashboard_data.get('total_decisions', 0)}")
        print(f"  - Success rate: {dashboard_data.get('success_rate', 0)}%")
        print(f"  - Savings TND: {dashboard_data.get('savings_tnd', 0)}")
        print(f"  - Risks avoided: {dashboard_data.get('risk_avoided_count', 0)}")
        
        # Check if smart_summary exists
        if 'smart_summary' in dashboard_data:
            print(f"  - Smart summary: {dashboard_data['smart_summary'][:100]}...")
        else:
            print("  ⚠️ No smart_summary in response")
            
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test decision endpoints
    print("\n📝 Testing Decision Management...")
    test_decision = Decision.query.filter_by(farmer_id=farmer.id).first()
    
    if test_decision:
        print(f"✓ Found decision ID {test_decision.id} for testing")
        print(f"  - Crop: {test_decision.crop.name if test_decision.crop else 'Unknown'}")
        print(f"  - Recommendation: {test_decision.recommendation}")
        
        # Check if decision has outcomes relationship
        has_outcome = hasattr(test_decision, 'outcomes') and len(test_decision.outcomes) > 0
        print(f"  - Has outcome: {has_outcome}")
        
        if has_outcome:
            outcome = test_decision.outcomes[0]
            print(f"  - Outcome status: {outcome.outcome}")
            print(f"  - Yield: {outcome.yield_kg} kg")
            print(f"  - Revenue: {outcome.revenue_tnd} TND")

    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 60)
