"""
Simple test to verify analytics data flow
"""
import sys
import os
sys.path.append(os.path.abspath('backend'))

from app import create_app
from models.base import db
from models.user import Farmer
from models.decision import Decision, Outcome
from models.crop import Crop
import random
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("=" * 60)
    print("ANALYTICS & HISTORY DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Get first farmer
    farmer = Farmer.query.first()
    if not farmer:
        print("❌ No farmers found")
        sys.exit(1)
    
    print(f"\n✓ Testing with: {farmer.first_name} {farmer.last_name} (ID: {farmer.id})")
    
    # Check decisions
    decisions = Decision.query.filter_by(farmer_id=farmer.id).all()
    print(f"✓ Total decisions: {len(decisions)}")
    
    # Check outcomes
    outcomes_count = Outcome.query.join(Decision).filter(Decision.farmer_id == farmer.id).count()
    print(f"✓ Total outcomes: {outcomes_count}")
    
    # Add test data if needed
    if len(decisions) < 5:
        print("\n📊 Adding 10 test decisions...")
        crops = Crop.query.limit(3).all()
        
        for i in range(10):
            crop = random.choice(crops)
            d = Decision(
                farmer_id=farmer.id,
                crop_id=crop.id,
                governorate=farmer.governorate or 'Tunis',
                recommendation=random.choice(['PLANT_NOW', 'WAIT']),
                confidence='HIGH',
                advice_status=random.choice(['followed', 'ignored']),
                actual_action='planted_now',
                weather_temp_avg=random.randint(15, 30),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            db.session.add(d)
            db.session.flush()
            
            # Add outcome
            is_success = random.choice([True, False])
            outcome = Outcome(
                decision_id=d.id,
                outcome='success' if is_success else 'failure',
                yield_kg=random.randint(500, 2000),
                revenue_tnd=random.randint(1000, 4000)
            )
            db.session.add(outcome)
        
        db.session.commit()
        print("✓ Added 10 test decisions with outcomes")
        
        # Refresh counts
        decisions = Decision.query.filter_by(farmer_id=farmer.id).all()
        outcomes_count = Outcome.query.join(Decision).filter(Decision.farmer_id == farmer.id).count()
        print(f"✓ New total decisions: {len(decisions)}")
        print(f"✓ New total outcomes: {outcomes_count}")
    
    # Test analytics
    print("\n📈 Testing Analytics Service...")
    from services.analytics_service import AnalyticsService
    analytics_service = AnalyticsService()
    
    try:
        data = analytics_service.get_dashboard_data(farmer.id, 'monthly')
        print("✓ Analytics data retrieved")
        print(f"  total_decisions: {data.get('total_decisions', 'MISSING')}")
        print(f"  success_rate: {data.get('success_rate', 'MISSING')}")
        print(f"  savings_tnd: {data.get('savings_tnd', 'MISSING')}")
        print(f"  risk_avoided_count: {data.get('risk_avoided_count', 'MISSING')}")
        
        if 'smart_summary' in data:
            summary = data['smart_summary']
            print(f"  smart_summary: {summary[:80]}..." if len(summary) > 80 else f"  smart_summary: {summary}")
        else:
            print("  smart_summary: MISSING")
            
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)
