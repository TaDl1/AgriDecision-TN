"""
Decision endpoint tests
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestGetAdvice:
    """Test get advice endpoint"""
    
    @patch('services.weather_service.WeatherService.get_forecast')
    @patch('services.ai_service.AIService.generate_explanation')
    def test_get_advice_success(self, mock_ai, mock_weather, client, auth_token, test_crop):
        """Test getting advice successfully"""
        # Mock weather service
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
        
        # Mock AI service
        mock_ai.return_value = 'Good time to plant tomatoes.'
        
        response = client.post('/api/decisions/get-advice',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'crop_id': test_crop.id}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'decision' in data['data']
        assert 'weather_forecast' in data['data']
        assert 'explanation' in data['data']
    
    def test_get_advice_no_token(self, client, test_crop):
        """Test getting advice without authentication"""
        response = client.post('/api/decisions/get-advice',
            json={'crop_id': test_crop.id}
        )
        
        assert response.status_code == 401
    
    def test_get_advice_invalid_crop(self, client, auth_token):
        """Test getting advice for non-existent crop"""
        response = client.post('/api/decisions/get-advice',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'crop_id': 9999}
        )
        
        assert response.status_code == 404
    
    def test_get_advice_missing_crop_id(self, client, auth_token):
        """Test getting advice without crop_id"""
        response = client.post('/api/decisions/get-advice',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={}
        )
        
        assert response.status_code == 400
    
    @patch('services.weather_service.WeatherService.get_forecast')
    @patch('services.ai_service.AIService.generate_explanation')
    def test_get_advice_custom_governorate(self, mock_ai, mock_weather, client, auth_token, test_crop):
        """Test getting advice with custom governorate"""
        mock_weather.return_value = []
        mock_ai.return_value = 'Test explanation'
        
        response = client.post('/api/decisions/get-advice',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'crop_id': test_crop.id,
                'governorate': 'Sfax'
            }
        )
        
        assert response.status_code == 200
        # Verify weather service was called with correct governorate
        mock_weather.assert_called_once()


class TestDecisionHistory:
    """Test decision history endpoint"""
    
    def test_get_history_success(self, client, auth_token, test_decision):
        """Test getting decision history"""
        response = client.get('/api/decisions/history',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'decisions' in data
        assert 'total' in data
        assert isinstance(data['decisions'], list)
    
    def test_get_history_pagination(self, client, auth_token):
        """Test history pagination"""
        response = client.get('/api/decisions/history?limit=5&offset=0',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['limit'] == 5
        assert data['offset'] == 0
    
    def test_get_history_no_token(self, client):
        """Test getting history without authentication"""
        response = client.get('/api/decisions/history')
        
        assert response.status_code == 401


class TestRecordOutcome:
    """Test record outcome endpoint"""
    
    def test_record_outcome_success(self, client, auth_token, test_decision):
        """Test recording outcome successfully"""
        response = client.post('/api/decisions/record-outcome',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'decision_id': test_decision.id,
                'outcome': 'success',
                'yield_kg': 450.5,
                'revenue_tnd': 2250.0,
                'notes': 'Excellent harvest'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'recorded'
        assert 'outcome_id' in data
    
    def test_record_outcome_invalid_decision(self, client, auth_token):
        """Test recording outcome for non-existent decision"""
        response = client.post('/api/decisions/record-outcome',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'decision_id': 9999,
                'outcome': 'success'
            }
        )
        
        assert response.status_code == 404
    
    def test_record_outcome_invalid_outcome_type(self, client, auth_token, test_decision):
        """Test recording outcome with invalid type"""
        response = client.post('/api/decisions/record-outcome',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'decision_id': test_decision.id,
                'outcome': 'invalid_outcome'
            }
        )
        
        assert response.status_code == 400
    
    def test_record_outcome_minimal_data(self, client, auth_token, test_decision):
        """Test recording outcome with minimal data"""
        response = client.post('/api/decisions/record-outcome',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'decision_id': test_decision.id,
                'outcome': 'unknown'
            }
        )
        
        assert response.status_code == 200


class TestDecisionDetails:
    """Test get decision details endpoint"""
    
    def test_get_decision_details_success(self, client, auth_token, test_decision):
        """Test getting decision details"""
        response = client.get(f'/api/decisions/{test_decision.id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_decision.id
        assert 'outcomes' in data
    
    def test_get_decision_details_not_found(self, client, auth_token):
        """Test getting non-existent decision"""
        response = client.get('/api/decisions/9999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 404


class TestDecisionStats:
    """Test decision statistics endpoint"""
    
    def test_get_decision_stats(self, client, auth_token, test_decision):
        """Test getting decision statistics"""
        response = client.get('/api/decisions/stats',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'by_recommendation' in data
        assert 'top_crops' in data