"""
Weather service for fetching and processing weather data
"""
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Weather Service using Open-Meteo API (Free, no key required)
    """
    
    # Coordinates for Tunisian Governorates - Including Sfax
    GOVERNORATE_COORDS = {
        'Tunis': {'lat': 36.8065, 'lon': 10.1815},
        'Ariana': {'lat': 36.8624, 'lon': 10.1956},
        'Ben Arous': {'lat': 36.7531, 'lon': 10.2189},
        'Manouba': {'lat': 36.8083, 'lon': 10.0972},
        'Nabeul': {'lat': 36.4561, 'lon': 10.7376},
        'Zaghouan': {'lat': 36.4029, 'lon': 10.1429},
        'Bizerte': {'lat': 37.2744, 'lon': 9.8739},
        'Beja': {'lat': 36.7256, 'lon': 9.1817},
        'Jendouba': {'lat': 36.5011, 'lon': 8.7802},
        'Kef': {'lat': 36.1742, 'lon': 8.7049},
        'Siliana': {'lat': 36.084, 'lon': 9.3708},
        'Kairouan': {'lat': 35.6781, 'lon': 10.0963},
        'Kasserine': {'lat': 35.1676, 'lon': 8.8365},
        'Sidi Bouzid': {'lat': 35.0382, 'lon': 9.4849},
        'Sousse': {'lat': 35.8256, 'lon': 10.6084},
        'Monastir': {'lat': 35.7780, 'lon': 10.8262},
        'Mahdia': {'lat': 35.5047, 'lon': 11.0622},
        'Sfax': {'lat': 34.7406, 'lon': 10.7603},
        'Gafsa': {'lat': 34.4250, 'lon': 8.7842},
        'Tozeur': {'lat': 33.9197, 'lon': 8.1335},
        'Kebili': {'lat': 33.7044, 'lon': 8.9690},
        'Gabes': {'lat': 33.8815, 'lon': 10.0982},
        'Medenine': {'lat': 33.3549, 'lon': 10.5055},
        'Tataouine': {'lat': 32.9297, 'lon': 10.4518},
        # Add fallbacks/variations
        'La Manouba': {'lat': 36.8083, 'lon': 10.0972},
        'Sfax': {'lat': 34.7406, 'lon': 10.7603}
    }
    
    # Tunisia-specific weather adjustments based on local climatology
    # These corrections account for microclimates not captured by 25km grid forecasts
    WEATHER_ADJUSTMENTS = {
        # Coastal cities (maritime influence moderates temperature)
        'Sfax': {'temp': +1.0, 'humidity': +5},
        'Sousse': {'temp': +0.5, 'humidity': +8},
        'Bizerte': {'temp': +0.5, 'humidity': +10},
        'Gabes': {'temp': +2.0, 'humidity': -5},  # Drier southern coast
        'Mahdia': {'temp': +0.5, 'humidity': +7},
        'Monastir': {'temp': +0.5, 'humidity': +7},
        'Nabeul': {'temp': +0.5, 'humidity': +8},
        
        # Urban heat island effect
        'Tunis': {'temp': +1.5, 'humidity': +10},
        'Ariana': {'temp': +1.0, 'humidity': +8},
        'Ben Arous': {'temp': +1.2, 'humidity': +9},
        
        # Mountain regions (elevation cooling, increased wind)
        'Kef': {'temp': -2.0, 'wind': +15},
        'Kasserine': {'temp': -1.5, 'wind': +10},
        'Siliana': {'temp': -1.0, 'wind': +8},
        'Zaghouan': {'temp': -0.5, 'wind': +5},
        'Jendouba': {'temp': -1.0, 'wind': +8},
        
        # Desert/Sahel regions (extreme heat, very low humidity)
        'Tataouine': {'temp': +4.0, 'humidity': -25, 'wind': +5},
        'Tozeur': {'temp': +3.5, 'humidity': -20, 'wind': +5},
        'Kebili': {'temp': +3.5, 'humidity': -22, 'wind': +5},
        'Gafsa': {'temp': +2.5, 'humidity': -15},
        'Sidi Bouzid': {'temp': +1.5, 'humidity': -10},
        
        # Central/Interior (moderate continental effects)
        'Kairouan': {'temp': +1.0, 'humidity': -5},
    }

    def get_forecast(self, governorate: str, days: int = 7) -> List[Dict]:
        """
        Get 7-day weather forecast from Open-Meteo with Tunisia-specific adjustments
        """
        try:
            # Default to Tunis if governorate not found or empty
            if not governorate:
                governorate = 'Tunis'
                
            # Normalize key lookup
            gov_key = next((k for k in self.GOVERNORATE_COORDS if k.lower() == governorate.lower()), 'Tunis')
            coords = self.GOVERNORATE_COORDS.get(gov_key, self.GOVERNORATE_COORDS['Tunis'])
            
            logger.info(f"Fetching weather for {governorate} -> {gov_key} ({coords})")
            
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max,weathercode',
                'timezone': 'auto',
                'forecast_days': days
            }
            
            # Use requests without extensive retries for speed in this context, logic handles failures
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            forecast = self._process_open_meteo_data(data, days, gov_key)
            
            return forecast

        except Exception as e:
            logger.error(f"Weather API failed: {e}. Falling back to mock data.")
            return self._generate_mock_forecast(days)

    def _process_open_meteo_data(self, data: dict, days: int, governorate: str) -> List[Dict]:
        """Convert Open-Meteo response to our internal format with regional adjustments"""
        daily = data.get('daily', {})
        forecast = []
        
        times = daily.get('time', [])
        for i in range(len(times)):
            if i >= days: break
            
            t_max = daily['temperature_2m_max'][i]
            t_min = daily['temperature_2m_min'][i]
            rain = daily.get('precipitation_sum', [0]*len(times))[i]
            humidity = daily.get('relative_humidity_2m_mean', [60]*len(times))[i]
            wind = daily.get('wind_speed_10m_max', [0]*len(times))[i]
            wcode = daily.get('weathercode', [0]*len(times))[i]
            
            condition = self._map_weather_code(wcode)
            
            # Apply regional adjustments if available
            if governorate in self.WEATHER_ADJUSTMENTS:
                adj = self.WEATHER_ADJUSTMENTS[governorate]
                temp_adj = adj.get('temp', 0)
                t_max += temp_adj
                t_min += temp_adj
                humidity = max(0, min(100, humidity + adj.get('humidity', 0)))
                wind += adj.get('wind', 0)
            
            forecast.append({
                'date': times[i],
                'temp_max': round(t_max, 1),
                'temp_min': round(t_min, 1),
                'temp_avg': round((t_max + t_min) / 2, 1),
                'rainfall': round(rain, 1),
                'humidity': round(humidity, 0),
                'wind': round(wind, 1),
                'condition': condition
            })
            
        return forecast

    def _map_weather_code(self, code: int) -> str:
        """Map WMO Weather interpretation codes (0-99)"""
        if code == 0: return 'Clear'
        if code in [1, 2, 3]: return 'Cloudy'
        if code in [45, 48]: return 'Foggy'
        if code in [51, 53, 55, 56, 57]: return 'Drizzle'
        if code in [61, 63, 65, 66, 67]: return 'Rainy'
        if code in [71, 73, 75, 77]: return 'Snow'
        if code in [80, 81, 82]: return 'Heavy Rain'
        if code in [95, 96, 99]: return 'Storm'
        return 'Cloudy' # Default

    def _generate_mock_forecast(self, days):
        """Fallback mock data if API fails"""
        forecast = []
        base_date = datetime.now()
        for i in range(days):
            date_str = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            forecast.append({
                'date': date_str,
                'temp_max': 25, 'temp_min': 15, 'temp_avg': 20,
                'rainfall': 0, 'humidity': 60,
                'wind': 10,
                'condition': 'Sunny'
            })
        return forecast