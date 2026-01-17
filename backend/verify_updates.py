import requests
import json

BASE_URL = 'http://localhost:5000/api'

def run_test():
    print("🚀 Starting Update/Delete Verification...")

    # 1. Register a temporary user
    user_data = {
        'phone_number': '99887766',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'governorate': 'Tunis',
        'farm_type': 'rain_fed'
    }
    
    # Try login first in case user exists from failed run
    print("\n1. Authentication...")
    session = requests.Session()
    login_resp = session.post(f'{BASE_URL}/auth/login', json={
        'phone_number': user_data['phone_number'],
        'password': user_data['password']
    })
    
    if login_resp.status_code == 200:
        token = login_resp.json()['token']
        print("   ✅ Logged in existing user")
    else:
        reg_resp = session.post(f'{BASE_URL}/auth/register', json=user_data)
        if reg_resp.status_code != 201:
            print(f"   ❌ Registration failed: {reg_resp.text}")
            return
        token = reg_resp.json()['token']
        print("   ✅ Registered new user")

    headers = {'Authorization': f'Bearer {token}'}

    # 2. Update Profile
    print("\n2. Testing Profile Update...")
    profile_update = {
        'first_name': 'UpdatedName',
        'governorate': 'Sousse'
    }
    resp = session.put(f'{BASE_URL}/auth/update-profile', json=profile_update, headers=headers)
    if resp.status_code == 200 and resp.json()['user']['first_name'] == 'UpdatedName':
        print("   ✅ Profile update success")
    else:
        print(f"   ❌ Profile update failed: {resp.text}")

    # 3. Update Preferences
    print("\n3. Testing Preferences Update...")
    pref_update = {
        'language': 'fr',
        'units': 'imperial'
    }
    resp = session.put(f'{BASE_URL}/auth/preferences', json=pref_update, headers=headers)
    if resp.status_code == 200 and resp.json()['preferences']['language'] == 'fr':
        print("   ✅ Preferences update success")
    else:
        print(f"   ❌ Preferences update failed: {resp.text}")

    # 4. Create Mock Data (Simulate)
    print("\n4. Creating Mock Data...")
    resp = session.post(f'{BASE_URL}/decisions/simulate-data', headers=headers)
    if resp.status_code == 200:
        print("   ✅ Data simulated")
    else:
        print(f"   ❌ Simulation failed: {resp.text}")
        return

    # Get a decision ID
    history_resp = session.get(f'{BASE_URL}/decisions/history?limit=1', headers=headers)
    decisions = history_resp.json()['decisions']
    if not decisions:
        print("   ❌ No history found")
        return
    
    decision_id = decisions[0]['id']
    print(f"   ℹ️  Working with decision ID: {decision_id}")

    # 5. Update Action
    print("\n5. Testing Action Update...")
    action_data = {
        'actual_action': 'waited',
        'deviation_reason': 'Testing update'
    }
    resp = session.put(f'{BASE_URL}/decisions/{decision_id}/action', json=action_data, headers=headers)
    if resp.status_code == 200 and resp.json()['data']['actual_action'] == 'waited':
        print("   ✅ Action update success")
    else:
        print(f"   ❌ Action update failed: {resp.text}")

    # 6. Update Outcome
    print("\n6. Testing Outcome Update...")
    outcome_data = {
        'notes': 'Updated Notes via Test',
        'yield_kg': 999
    }
    resp = session.put(f'{BASE_URL}/decisions/{decision_id}/outcome', json=outcome_data, headers=headers)
    if resp.status_code == 200 and resp.json()['outcome']['yield_kg'] == 999:
        print("   ✅ Outcome update success")
    else:
        # Note: Outcome might not exist if simulation logic didn't create one for this specific decision, 
        # but simulation usually does. If 404, we might need to create one first.
        print(f"   ⚠️ Outcome update response: {resp.text}")

    # 7. Delete Decision
    print("\n7. Testing Decision Delete...")
    resp = session.delete(f'{BASE_URL}/decisions/{decision_id}', headers=headers)
    if resp.status_code == 200:
        print("   ✅ Decision delete success")
    else:
        print(f"   ❌ Decision delete failed: {resp.text}")

    # Verify gone
    resp = session.get(f'{BASE_URL}/decisions/{decision_id}', headers=headers)
    if resp.status_code == 404:
        print("   ✅ Verification: Decision is gone")
    else:
        print("   ❌ Verification: Decision still exists")

    # 8. Delete Account
    print("\n8. Testing Account Delete...")
    resp = session.delete(f'{BASE_URL}/auth/account', headers=headers)
    if resp.status_code == 200:
        print("   ✅ Account delete success")
    else:
        print(f"   ❌ Account delete failed: {resp.text}")
        
    # Verify login fails
    login_resp = session.post(f'{BASE_URL}/auth/login', json={
        'phone_number': user_data['phone_number'],
        'password': user_data['password']
    })
    if login_resp.status_code == 401:
         print("   ✅ Verification: Login failed as expected")
    else:
         print("   ❌ Verification: User still exists")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Test failed with error: {e}")
