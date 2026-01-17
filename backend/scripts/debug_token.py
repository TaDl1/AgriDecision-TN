"""
Debug JWT token response
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def debug_login():
    print("=" * 70)
    print("DEBUGGING LOGIN RESPONSE")
    print("=" * 70)
    
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "phone": "22222222",
            "password": "password123"
        }
    )
    
    print(f"\nStatus: {login_response.status_code}")
    print(f"\nFull Response:")
    print(json.dumps(login_response.json(), indent=2))
    
    data = login_response.json()
    
    print(f"\nToken fields found:")
    for key in data.keys():
        if 'token' in key.lower() or 'access' in key.lower():
            print(f"  - {key}: {data[key][:50] if isinstance(data[key], str) else data[key]}...")
    
    # Try different token fields
    possible_tokens = [
        data.get('access_token'),
        data.get('token'),
        data.get('data', {}).get('access_token'),
        data.get('data', {}).get('token'),
    ]
    
    print(f"\nPossible tokens:")
    for i, token in enumerate(possible_tokens):
        if token:
            print(f"  {i+1}. Found: {token[:50]}...")
            
            # Test this token
            print(f"\n  Testing token {i+1}...")
            test_response = requests.get(
                f"{BASE_URL}/api/decisions/advanced-analytics",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"    Status: {test_response.status_code}")
            if test_response.status_code != 200:
                print(f"    Error: {test_response.text[:200]}")
            else:
                print(f"    SUCCESS!")
                return token
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    debug_login()
