"""
Integration tests - Full workflow scenarios
"""
import pytest
import json
from unittest.mock import patch


class TestCompleteUserJourney:
    """Test complete user journey from registration to getting advice"""
    
    @patch('services.weather_service.WeatherService.get_forecast')
    @patch('services.ai_service.AIService.generate_explanation')
    def test_complete_flow(self, mock_ai, mock_weather, client, db_session):
        """Test: Register -> Login -> Get Advice -> View History"""
        
        # Mock external services
        mock_weather.return_value = [{
            'date': '2024-03-15',
            'temp_min': 15.0,
            'temp_max': 25.0,
            'temp_avg': 20.0,
            'humidity': 60,
            'wind': 12.0,
            'rainfall': 0.0,
            'description': 'Clear'
        }]
        mock_ai.return_value = 'Good time to plant tomatoes.'
        
        # Step 1: Register
        register_response = client.post('/api/auth/register', json={
            'phone_number': '21655555555',
            'password': 'TestPass123',
            'governorate': 'Tunis',
            'farm_type': 'rain_fed'
        })
        assert register_response.status_code == 201
        
        # Step 2: Login
        login_response = client.post('/api/auth/login', json={
            'phone': '21655555555',
            'password': 'TestPass123'
        })
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['token']
        
        # Step 3: Get Crops
        crops_response = client.get('/api/crops/')
        assert crops_response.status_code == 200
        crops = json.loads(crops_response.data)
        tomato = next(c for c in crops if c['name'] == 'Tomato')
        
        # Step 4: Get Advice
        advice_response = client.post('/api/decisions/get-advice',
            headers={'Authorization': f'Bearer {token}'},
            json={'crop_id': tomato['id']}
        )
        assert advice_response.status_code == 200
        advice_data = json.loads(advice_response.data)
        assert 'data' in advice_data
        assert 'decision' in advice_data['data']
        
        # Step 5: View History
        history_response = client.get('/api/decisions/history',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert history_response.status_code == 200
        history_data = json.loads(history_response.data)
        assert len(history_data['decisions']) > 0
        
        # Step 6: Record Outcome
        decision_id = history_data['decisions'][0]['id']
        outcome_response = client.post('/api/decisions/record-outcome',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'decision_id': decision_id,
                'outcome': 'success',
                'yield_kg': 500.0,
                'revenue_tnd': 2500.0
            }
        )
        assert outcome_response.status_code == 200
        
        # Step 7: Check Analytics
        analytics_response = client.get('/api/analytics/personal',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert analytics_response.status_code == 200
        analytics_data = json.loads(analytics_response.data)
        assert analytics_data['total_decisions'] >= 1


class TestAPIErrorHandling:
    """Test API error handling scenarios"""
    
    def test_404_endpoint_not_found(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method"""
        response = client.delete('/api/crops/')
        assert response.status_code == 405
    
    def test_401_unauthorized_access(self, client):
        """Test 401 for protected endpoint without token"""
        response = client.post('/api/decisions/get-advice', json={
            'crop_id': 1
        })
        assert response.status_code == 401
    
    def test_400_invalid_json(self, client, auth_token):
        """Test 400 for invalid JSON"""
        response = client.post('/api/decisions/get-advice',
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            },
            data='invalid json'
        )
        assert response.status_code in [400, 422]


class TestConcurrentRequests:
    """Test handling of concurrent requests"""
    
    @patch('services.weather_service.WeatherService.get_forecast')
    @patch('services.ai_service.AIService.generate_explanation')
    def test_multiple_advice_requests(self, mock_ai, mock_weather, client, auth_token):
        """Test multiple simultaneous advice requests"""
        mock_weather.return_value = []
        mock_ai.return_value = 'Test explanation'
        
        responses = []
        for crop_id in range(1, 4):
            response = client.post('/api/decisions/get-advice',
                headers={'Authorization': f'Bearer {auth_token}'},
                json={'crop_id': crop_id}
            )
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)