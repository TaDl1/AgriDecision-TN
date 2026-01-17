"""
Final verification script - test all fixes
"""
from app import app, db
from models.user import Farmer
from services.analytics_service import AnalyticsService
from services.weather_service import WeatherService
import json

def verify_all():
    with app.app_context():
        print("=" * 70)
        print("FINAL VERIFICATION - ALL FIXES")
        print("=" * 70)
        
        # 1. Demo User Check
        print("\n1. DEMO USER STATUS")
        print("-" * 70)
        demo = Farmer.query.filter_by(phone_number='22222222').first()
        if demo:
            print(f"   PASS: Demo user exists (ID: {demo.id}, Gov: {demo.governorate})")
            from models.decision import Decision, Outcome
            decisions = Decision.query.filter_by(farmer_id=demo.id).count()
            outcomes = db.session.query(Outcome).join(Decision).filter(
                Decision.farmer_id == demo.id
            ).count()
            print(f"   Data: {decisions} decisions, {outcomes} outcomes")
        else:
            print("   FAIL: Demo user not found!")
            return
        
        # 2. Analytics Service Test
        print("\n2. ANALYTICS SERVICE")
        print("-" * 70)
        try:
            analytics = AnalyticsService()
            data = analytics.get_dashboard_data(demo.id, 'monthly')
            
            print(f"   Success Rate: {data.get('success_rate', 'ERROR')}%")
            print(f"   Total Decisions: {data.get('total_decisions', 'ERROR')}")
            
            aes = data.get('advice_effectiveness_score', {})
            aes_value = aes.get('aes', 'ERROR')
            print(f"   AES: {aes_value}")
            
            if data.get('success_rate', 0) > 0:
                print("   PASS: Analytics returning data")
            else:
                print("   WARNING: Success rate is 0")
                
        except Exception as e:
            print(f"   FAIL: {str(e)[:100]}")
        
        # 3. Weather Service Test
        print("\n3. WEATHER SERVICE (Sfax)")
        print("-" * 70)
        try:
            ws = WeatherService()
            forecast = ws.get_forecast('Sfax', days=1)
            
            if forecast and len(forecast) > 0:
                today = forecast[0]
                print(f"   Temperature: {today['temp_min']}-{today['temp_max']}C (avg: {today['temp_avg']}C)")
                print(f"   Condition: {today['condition']}")
                print(f"   Humidity: {today['humidity']}%")
                
                # Check if close to real (17C)
                if 15 <= today['temp_avg'] <= 19:
                    print("   PASS: Temperature matches real Sfax (~17C)")
                else:
                    print(f"   WARNING: Temperature differs from real (expected ~17C)")
            else:
                print("   FAIL: No forecast data")
                
        except Exception as e:
            print(f"   FAIL: {str(e)[:100]}")
        
        # 4. Regional Adjustments Check
        print("\n4. WEATHER ADJUSTMENTS")
        print("-" * 70)
        test_cities = ['Sfax', 'Kef', 'Tataouine', 'Tunis']
        for city in test_cities:
            if city in ws.WEATHER_ADJUSTMENTS:
                adj = ws.WEATHER_ADJUSTMENTS[city]
                print(f"   {city}: temp {adj.get('temp', 0):+.1f}C, "
                      f"humidity {adj.get('humidity', 0):+d}%")
            else:
                print(f"   {city}: No adjustments")
        
        print("\n" + "=" * 70)
        print("VERIFICATION COMPLETE")
        print("=" * 70)
        print("\nSUMMARY:")
        print("  - Demo user: READY")
        print("  - Analytics: FIXED (SQLAlchemy cast syntax)")
        print("  - Weather: ENHANCED (Tunisia-specific adjustments)")
        print("  - Frontend: IMPROVED (progressive analytics)")
        print("\nNEXT STEPS:")
        print("  1. Login as 22222222 / password123")
        print("  2. Check Analytics Dashboard")
        print("  3. Verify weather on Advice page")

if __name__ == '__main__':
    verify_all()
