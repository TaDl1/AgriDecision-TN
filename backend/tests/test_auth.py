import json
import pytest

def test_registration(client):
    """Test user registration."""
    response = client.post('/api/auth/register', json={
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "21699000000",
        "password": "Password123!",
        "governorate": "Tunis",
        "farm_type": "irrigated"
    })
    
    if response.status_code != 201:
        print(f"\nDEBUG status: {response.status_code}")
        print(f"DEBUG raw data: {response.data.decode('utf-8', errors='ignore')[:1000]}")
    
    try:
        data = json.loads(response.data)
    except Exception as e:
        print(f"DEBUG: Failed to parse JSON: {e}")
        assert False, f"Server returned 500 with non-JSON body: {response.data[:200]}"

    assert response.status_code == 201
    assert data['message'] == 'User created successfully'

def test_login(client):
    """Test user login."""
    # First register
    client.post('/api/auth/register', json={
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "21699000001",
        "password": "Password123!",
        "governorate": "Tunis",
        "farm_type": "irrigated"
    })
    
    # Then login
    response = client.post('/api/auth/login', json={
        "phone": "21699000001",
        "password": "Password123!"
    })
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'token' in data
    assert 'user' in data

def test_login_invalid_credentials(client):
    """Test login with wrong password."""
    response = client.post('/api/auth/login', json={
        "phone": "21600000000",
        "password": "WrongPassword"
    })
    
    assert response.status_code == 401