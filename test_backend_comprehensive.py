import sys
import os
import requests
import json

sys.path.append(os.path.abspath('backend'))

print("=" * 60)
print("COMPREHENSIVE BACKEND TEST")
print("=" * 60)

# Test 1: Check if backend is running
print("\n1. Testing Backend Server Connection...")
try:
    response = requests.get('http://localhost:5000/api/health', timeout=2)
    print(f"   ✓ Server is running (Status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("   ✗ Server is NOT running on port 5000")
    print("   → Please start the backend: cd backend && python app.py")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Test model imports
print("\n2. Testing Model Imports...")
try:
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from models.user import Farmer
        from models.decision import Decision, Outcome
        from models.analytics import FarmerAnalytics, AnalyticsEvent, RegionalBenchmarks, CropSpecificDefaults
        from services.truthful_engine import TruthfulAnalyticsEngine
        
        print("   ✓ All models imported successfully")
        
        # Test database connection
        farmer_count = Farmer.query.count()
        print(f"   ✓ Database connected ({farmer_count} farmers)")
        
except Exception as e:
    print(f"   ✗ Import Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test API endpoints
print("\n3. Testing API Endpoints...")

# You'll need a valid token for this - let's just test public endpoints
endpoints_to_test = [
    ('GET', '/api/health', None),
]

for method, endpoint, data in endpoints_to_test:
    try:
        url = f'http://localhost:5000{endpoint}'
        if method == 'GET':
            response = requests.get(url, timeout=2)
        else:
            response = requests.post(url, json=data, timeout=2)
        
        print(f"   {endpoint}: {response.status_code}")
        
        # Try to parse JSON
        try:
            json_data = response.json()
            print(f"      ✓ Valid JSON response")
        except:
            print(f"      ✗ Invalid JSON response")
            print(f"      Response text: {response.text[:100]}")
            
    except Exception as e:
        print(f"   {endpoint}: ✗ Error - {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
