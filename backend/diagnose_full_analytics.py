"""
Full Analytics Diagnostic Script
Checks data integrity, API responses, and identifies where analytics fail
"""
from app import app, db
from models.decision import Decision, Outcome
from models.user import Farmer
from services.analytics_service import AnalyticsService
from services.regional_analytics import RegionalAnalyticsService
import json

def diagnose():
    with app.app_context():
        print("=" * 60)
        print("FULL ANALYTICS DIAGNOSTIC")
        print("=" * 60)
        
        # Find demo user
        demo_user = Farmer.query.filter_by(phone_number='22222222').first()
        if not demo_user:
            print("❌ Demo user (22222222) not found!")
            return
        
        print(f"\n✅ Demo User Found: ID={demo_user.id}, Gov={demo_user.governorate}")
        
        # 1. Basic Counts
        print("\n" + "=" * 60)
        print("1. DATA COUNTS")
        print("=" * 60)
        
        total_decisions = Decision.query.filter_by(farmer_id=demo_user.id).count()
        print(f"Total Decisions: {total_decisions}")
        
        # Count outcomes
        outcomes_query = db.session.query(Outcome).join(Decision).filter(
            Decision.farmer_id == demo_user.id
        )
        total_outcomes = outcomes_query.count()
        print(f"Total Outcomes: {total_outcomes}")
        
        # Count by outcome type
        successes = outcomes_query.filter(Outcome.outcome == 'success').count()
        failures = outcomes_query.filter(Outcome.outcome == 'failure').count()
        print(f"  - Successes: {successes}")
        print(f"  - Failures: {failures}")
        
        # Check advice_status
        followed = Decision.query.filter_by(
            farmer_id=demo_user.id,
            advice_status='followed'
        ).count()
        ignored = Decision.query.filter_by(
            farmer_id=demo_user.id,
            advice_status='ignored'
        ).count()
        pending = Decision.query.filter_by(
            farmer_id=demo_user.id,
            advice_status='pending'
        ).count()
        
        print(f"\nAdvice Status Distribution:")
        print(f"  - Followed: {followed}")
        print(f"  - Ignored: {ignored}")
        print(f"  - Pending: {pending}")
        
        # 2. Regional Analytics Tests
        print("\n" + "=" * 60)
        print("2. REGIONAL ANALYTICS SERVICE")
        print("=" * 60)
        
        try:
            gsi = RegionalAnalyticsService.calculate_gsi(demo_user.governorate)
            print(f"GSI Result: {json.dumps(gsi, indent=2)}")
        except Exception as e:
            print(f"❌ GSI Failed: {e}")
        
        try:
            pbd = RegionalAnalyticsService.calculate_pbd(demo_user.id, demo_user.governorate)
            print(f"\nPBD Result: {json.dumps(pbd, indent=2)}")
        except Exception as e:
            print(f"❌ PBD Failed: {e}")
        
        # 3. Full Analytics Service Test
        print("\n" + "=" * 60)
        print("3. ANALYTICS SERVICE (FULL DASHBOARD)")
        print("=" * 60)
        
        try:
            analytics_service = AnalyticsService()
            dashboard_data = analytics_service.get_dashboard_data(demo_user.id, 'monthly')
            
            print("\nDashboard Data Structure:")
            print(json.dumps(dashboard_data, indent=2, default=str))
            
            # Check for None/empty values
            print("\n" + "-" * 60)
            print("Checking for empty/None values:")
            
            def check_nested(data, path=""):
                issues = []
                if isinstance(data, dict):
                    for key, value in data.items():
                        new_path = f"{path}.{key}" if path else key
                        if value is None:
                            issues.append(f"  ⚠️  {new_path} = None")
                        elif value == 0 and key in ['aes', 'success_rate', 'gsi']:
                            issues.append(f"  ⚠️  {new_path} = 0 (suspicious)")
                        elif isinstance(value, (dict, list)):
                            issues.extend(check_nested(value, new_path))
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        issues.extend(check_nested(item, f"{path}[{i}]"))
                return issues
            
            issues = check_nested(dashboard_data)
            if issues:
                print("\n".join(issues))
            else:
                print("  ✅ No suspicious None/0 values found")
                
        except Exception as e:
            import traceback
            print(f"❌ Analytics Service Failed:")
            print(traceback.format_exc())
        
        # 4. Database Health
        print("\n" + "=" * 60)
        print("4. DATABASE HEALTH")
        print("=" * 60)
        
        # Check for NULL weather data
        null_weather = Decision.query.filter(
            Decision.farmer_id == demo_user.id,
            Decision.weather_temp_avg.is_(None)
        ).count()
        print(f"Decisions without weather data: {null_weather}/{total_decisions}")
        
        # Check decision-outcome linkage
        decisions_without_outcomes = db.session.query(Decision).filter(
            Decision.farmer_id == demo_user.id
        ).outerjoin(Outcome).filter(
            Outcome.id.is_(None)
        ).count()
        print(f"Decisions without outcomes: {decisions_without_outcomes}/{total_decisions}")
        
        # 5. Sample Data Inspection
        print("\n" + "=" * 60)
        print("5. SAMPLE DATA (First 3 Decisions)")
        print("=" * 60)
        
        sample_decisions = Decision.query.filter_by(
            farmer_id=demo_user.id
        ).order_by(Decision.timestamp.desc()).limit(3).all()
        
        for i, decision in enumerate(sample_decisions, 1):
            print(f"\nDecision {i}:")
            print(f"  ID: {decision.id}")
            print(f"  Crop: {decision.crop.name if decision.crop else 'N/A'}")
            print(f"  Recommendation: {decision.recommendation}")
            print(f"  Advice Status: {decision.advice_status}")
            print(f"  Weather Temp: {decision.weather_temp_avg}")
            
            outcome = Outcome.query.filter_by(decision_id=decision.id).first()
            if outcome:
                print(f"  Outcome: {outcome.outcome}")
                print(f"  Yield: {outcome.yield_kg} kg")
            else:
                print(f"  ❌ No outcome linked!")
        
        print("\n" + "=" * 60)
        print("DIAGNOSIS COMPLETE")
        print("=" * 60)

if __name__ == '__main__':
    diagnose()
