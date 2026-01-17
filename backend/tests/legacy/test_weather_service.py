"""
Weather service tests
"""
import pytest
from unittest.mock import patch, MagicMock
from services.weather_service import WeatherService


class TestWeatherService:
    """Test weather service functionality"""
    
    def test_init_without_api_key(self, monkeypatch):
        """Test initialization without API key"""
        monkeypatch.delenv('OPENWEATHER_API_KEY', raising=False)
        service = WeatherService()
        assert service.API_KEY is None
    
    def test_init_with_api_key(self, monkeypatch):
        """Test initialization with API key"""
        monkeypatch.setenv('OPENWEATHER_API_KEY', 'test_key')
        service = WeatherService()
        assert service.API_KEY == 'test_key'
    
    @patch('requests.get')
    def test_get_forecast_success(self, mock_get):
        """Test successful forecast retrieval"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'list': [
                {
                    'dt_txt': '2024-03-15 12:00:00',
                    'main': {
                        'temp': 20.0,
                        'temp_min': 15.0,
                        'temp_max': 25.0,
                        'humidity': 60
                    },
                    'wind': {'speed': 12.0},
                    'weather': [{'main': 'Clear'}],
                    'rain': {}
                }
            ]
        }
        mock_get.return_value = mock_response
        
        service = WeatherService()
        service.API_KEY = 'test_key'
        forecast = service.get_forecast('Tunis', days=1)
        
        assert len(forecast) == 1
        assert forecast[0]['date'] == '2024-03-15'
        assert forecast[0]['temp_avg'] == 20.0
    
    def test_get_forecast_fallback_to_mock(self):
        """Test fallback to mock data when API fails"""
        service = WeatherService()
        service.API_KEY = None
        
        forecast = service.get_forecast('Tunis', days=7)
        
        assert len(forecast) == 7
        assert all('date' in day for day in forecast)
        assert all('temp_avg' in day for day in forecast)
    
    def test_get_mock_data(self):
        """Test mock data generation"""
        service = WeatherService()
        mock_data = service._get_mock_data(5)
        
        assert len(mock_data) == 5
        for day in mock_data:
            assert 'date' in day
            assert 'temp_min' in day
            assert 'temp_max' in day
            assert 'temp_avg' in day
            assert 'humidity' in day
            assert 'wind' in day
            assert 'rainfall' in day
    
    def test_governorate_coordinates(self):
        """Test all governorates have coordinates"""
        service = WeatherService()
        
        governorates = [
            'Tunis', 'Ariana', 'Ben Arous', 'Manouba', 'Nabeul', 'Zaghouan',
            'Bizerte', 'Beja', 'Jendouba', 'Kef', 'Siliana', 'Kairouan',
            'Kasserine', 'Sidi Bouzid', 'Sousse', 'Monastir', 'Mahdia',
            'Sfax', 'Gabes', 'Medenine', 'Tataouine', 'Gafsa', 'Tozeur', 'Kebili'
        ]
        
        for gov in governorates:
            assert gov in service.GOV_COORDS
            assert 'lat' in service.GOV_COORDS[gov]
            assert 'lon' in service.GOV_COORDS[gov]