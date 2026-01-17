"""
Get full analytics response to see exact data structure
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Login
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"phone": "22222222", "password": "password123"}
)

token = login_response.json()['token']

# Get analytics
analytics_response = requests.get(
    f"{BASE_URL}/api/decisions/advanced-analytics?timeframe=monthly",
    headers={"Authorization": f"Bearer {token}"}
)

print("=" * 80)
print("FULL ANALYTICS API RESPONSE")
print("=" * 80)
print(json.dumps(analytics_response.json(), indent=2, default=str))
print("\n" + "=" * 80)

# Save to file for inspection
with open('analytics_response.json', 'w') as f:
    json.dump(analytics_response.json(), f, indent=2, default=str)
    
print("\nSaved to analytics_response.json")
