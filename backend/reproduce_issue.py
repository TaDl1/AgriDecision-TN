
import os
import sys
import json
from app import create_app
from models.base import db
from models.user import Farmer
from services.init_db import init_database

def reproduce():
    # Setup app
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        # Reset DB for clean state (using in-memory sqlite for testing config usually, 
        # but here we might be using the actual dev db if not careful. 
        # But 'testing' config should use a separate DB or in-memory.)
        # Let's just suppress errors if we can't drop/create.
        try:
            db.create_all()
            try:
                init_database()
            except:
                pass # Already seeded
        except Exception as e:
            print(f"DB Setup error: {e}")

        # Create test client
        client = app.test_client()

        # Register/Login User
        phone = "21611111111"
        password = "TestPass123"
        
        # Check if user exists
        user = Farmer.query.filter_by(phone_number=phone).first()
        if not user:
            # Register
            resp = client.post('/api/auth/register', json={
                "phone_number": phone,
                "password": password,
                "governorate": "Tunis",
                "farm_type": "rain_fed"
            })
            print(f"Register status: {resp.status_code}")
        
        # Login
        resp = client.post('/api/auth/login', json={
            "phone": phone,
            "password": password
        })
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.data}")
            return
            
        token = resp.json['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        with open('results.txt', 'w') as f:
            print("\n--- Testing /get-advice ---")
            
            # 1. Invalid payload (missing crop_id)
            resp = client.post('/api/decisions/get-advice', headers=headers, json={})
            f.write(f"Missing Payload: Status={resp.status_code}\n")

            # 2. Invalid crop_id (out of range)
            resp = client.post('/api/decisions/get-advice', headers=headers, json={"crop_id": 99})
            f.write(f"Invalid crop_id: Status={resp.status_code}\n")
            
            # 3. Valid payload (assuming crop 1 exists)
            resp = client.post('/api/decisions/get-advice', headers=headers, json={"crop_id": 1, "governorate": "Tunis"})
            f.write(f"Valid Payload: Status={resp.status_code}\n")
            if resp.status_code != 200:
                f.write(f"Body: {resp.json}\n")

            print("\n--- Testing /history ---")
            # 4. Valid params
            resp = client.get('/api/decisions/history?limit=20&offset=0', headers=headers)
            f.write(f"History (Valid): Status={resp.status_code}\n")
            if resp.status_code != 200:
                f.write(f"Body: {resp.json}\n")
                
            # 5. Invalid params types
            resp = client.get('/api/decisions/history?limit=abc', headers=headers)
            f.write(f"History (Invalid limit=abc): Status={resp.status_code}\n")

if __name__ == "__main__":
    reproduce()
