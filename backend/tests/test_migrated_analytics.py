
import pytest
from services.analytics_service import AnalyticsService
from models.user import Farmer
from models.decision import Decision, Outcome
from models.crop import Crop
from models.regional import Governorate
import json

def seed_test_data(db):
    """Refactored seeding for tests"""
    # Create Farmer
    farmer = Farmer(
        phone_number='22222222',
        first_name='Demo',
        last_name='User',
        governorate='Bizerte',
        farm_type='irrigated'
    )
    farmer.set_password('secret')
    db.session.add(farmer)
    
    # Create Crop
    crop = Crop(name="Wheat", category="cereal", min_temp=5, max_temp=30, water_needs="medium")
    db.session.add(crop)
    db.session.commit()
    
    # Create Decision
    decision = Decision(
        farmer_id=farmer.id,
        crop_id=crop.id,
        governorate='Bizerte',
        recommendation='PLANT_NOW',
        confidence='HIGH',
        explanation='Test',
        period_id='P1',
        advice_status='followed',
        actual_action='planted_now'
    )
    db.session.add(decision)
    db.session.commit()
    
    # Create Outcome
    outcome = Outcome(
        decision_id=decision.id,
        outcome='success',
        yield_kg=1000,
        revenue_tnd=500,
        notes='Good'
    )
    db.session.add(outcome)
    db.session.commit()
    
    return farmer

def test_analytics_service_metrics(app):
    """Converted from test_analytics_service.py"""
    with app.app_context():
        from models.base import db
        farmer = seed_test_data(db)
        
        service = AnalyticsService()
        result = service.get_dashboard_data(farmer.id, 'monthly')
        
        # Assertions replacing print statements
        assert result is not None
        assert 'error' not in result
        assert result['success_rate'] == 100.0
        assert result['total_decisions'] == 1
        assert result['outcome_count'] == 1
        
def test_analytics_api_endpoint(client, app):
    """Converted from test_api_endpoint.py"""
    # 1. Setup Data
    with app.app_context():
        from models.base import db
        seed_test_data(db)
        # Verify user exists
        user = Farmer.query.filter_by(phone_number='22222222').first()
        assert user is not None

    # 2. Login
    login_res = client.post('/api/auth/login', json={
        "phone": "22222222", 
        "password": "secret"
    })
    assert login_res.status_code == 200
    token = login_res.json.get('token')
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Call Endpoint
    analytics_response = client.get(
        '/api/analytics/advanced',
        headers=headers
    )
    
    assert analytics_response.status_code == 200
    data = analytics_response.json
    assert 'advice_effectiveness_score' in data
    assert 'risk_avoidance_roi' in data
