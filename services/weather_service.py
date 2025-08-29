"""
Enhanced Weather Service with OpenWeatherMap API
Provides comprehensive weather data including current conditions, forecasts, and alerts
"""
import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key: str = None):
        """Initialize weather service with API key"""
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY') or os.environ.get('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def get_comprehensive_weather_analysis(self, city: str, date_context: str = None) -> Dict[str, Any]:
        """Get comprehensive weather analysis for a city"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'Weather API key not configured',
                    'current_conditions': {},
                    'forecast': []
                }

            # Get current weather
            current_url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(current_url, params=params)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'current_conditions': {
                        'temperature': data['main']['temp'],
                        'feels_like': data['main']['feels_like'],
                        'humidity': data['main']['humidity'],
                        'description': data['weather'][0]['description'],
                        'city': data['name'],
                        'country': data['sys']['country']
                    },
                    'forecast': []
                }
            else:
                return {
                    'success': False,
                    'error': f'Weather API error: {response.status_code}',
                    'current_conditions': {},
                    'forecast': []
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Weather service error: {str(e)}',
                'current_conditions': {},
                'forecast': []
            }

    def format_weather_analysis_response(self, weather_data: Dict[str, Any], persona: str = None) -> str:
        """Format weather analysis response based on persona"""
        if not weather_data['success']:
            if persona == 'pirate':
                return f"Arrr! The weather winds be blowin' against us, matey! {weather_data.get('error', 'Unknown error')}"
            else:
                return f"I'm sorry, I couldn't get the weather information: {weather_data.get('error', 'Unknown error')}"

        conditions = weather_data['current_conditions']
        temp = conditions.get('temperature', 'N/A')
        feels_like = conditions.get('feels_like', 'N/A')
        humidity = conditions.get('humidity', 'N/A')
        description = conditions.get('description', 'N/A')
        city = conditions.get('city', 'Unknown')

        if persona == 'pirate':
            return f"Arrr! The weather at {city} be {description} with a temperature of {temp}°C (feels like {feels_like}°C), humidity at {humidity}%. The winds be tellin' tales of the sea, matey!"
        else:
            return f"The weather in {city} is {description} with a temperature of {temp}°C (feels like {feels_like}°C) and humidity at {humidity}%."

    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return bool(self.api_key)

    def set_api_key(self, api_key: str):
        """Set the API key dynamically"""
        self.api_key = api_key

    def get_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a city using geocoding API"""
        try:
            url = f"{self.geo_url}/direct"
            params = {
                'q': city,
                'limit': 1,
                'appid': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'lat': data[0]['lat'],
                        'lon': data[0]['lon'],
                        'name': data[0]['name'],
                        'country': data[0].get('country', ''),
                        'state': data[0].get('state', '')
                    }
            return None
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather conditions"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Current weather API error: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Current weather error: {e}")
            return {}

    def get_hourly_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get hourly weather forecast"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Forecast API error: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Hourly forecast error: {e}")
            return {}

    def get_weather_alerts(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Get weather alerts for the location"""
        try:
            url = f"{self.base_url}/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'exclude': 'minutely'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get('alerts', [])
            else:
                logger.error(f"Alerts API error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Weather alerts error: {e}")
            return []

    def get_comprehensive_weather(self, city: str, report_type: str = 'current') -> Dict[str, Any]:
        """
        Get comprehensive weather report for a city

        Args:
            city: City name
            report_type: 'current', 'hourly', 'daily', or 'detailed'

        Returns:
            Comprehensive weather data
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Weather API key not configured'
            }

        try:
            # Get coordinates
            coords = self.get_coordinates(city)
            if not coords:
                return {
                    'success': False,
                    'error': f'City "{city}" not found'
                }

            # Get current weather
            current = self.get_current_weather(coords['lat'], coords['lon'])
            if not current:
                return {
                    'success': False,
                    'error': 'Failed to fetch current weather'
                }

            result = {
                'success': True,
                'location': {
                    'city': coords['name'],
                    'country': coords['country'],
                    'state': coords.get('state', ''),
                    'coordinates': f"{coords['lat']:.2f}, {coords['lon']:.2f}"
                },
                'current': {
                    'temperature': round(current['main']['temp']),
                    'feels_like': round(current['main']['feels_like']),
                    'description': current['weather'][0]['description'].title(),
                    'humidity': current['main']['humidity'],
                    'pressure': current['main']['pressure'],
                    'visibility': current.get('visibility', 0) / 1000,  # Convert to km
                    'wind_speed': current['wind']['speed'],
                    'wind_direction': current['wind'].get('deg', 0),
                    'uv_index': current.get('uvi', 'N/A'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'report_type': report_type
            }

            # Add forecast data based on report type
            if report_type in ['hourly', 'daily', 'detailed']:
                forecast = self.get_hourly_forecast(coords['lat'], coords['lon'])
                if forecast:
                    result['forecast'] = self._process_forecast(forecast, report_type)

            # Add alerts for detailed reports
            if report_type == 'detailed':
                alerts = self.get_weather_alerts(coords['lat'], coords['lon'])
                result['alerts'] = alerts

            return result

        except Exception as e:
            logger.error(f"Comprehensive weather error: {e}")
            return {
                'success': False,
                'error': f'Weather service error: {str(e)}'
            }

    def _process_forecast(self, forecast_data: Dict, report_type: str) -> Dict[str, Any]:
        """Process forecast data based on report type"""
        try:
            forecasts = forecast_data.get('list', [])

            if report_type == 'hourly':
                # Next 12 hours
                hourly = []
                for item in forecasts[:4]:  # 12 hours (3-hour intervals)
                    hourly.append({
                        'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                        'temperature': round(item['main']['temp']),
                        'description': item['weather'][0]['description'].title(),
                        'precipitation': item.get('rain', {}).get('3h', 0)
                    })
                return {'hourly': hourly}

            elif report_type == 'daily':
                # Next 5 days
                daily = []
                current_date = None
                for item in forecasts:
                    date = datetime.fromtimestamp(item['dt']).date()
                    if date != current_date:
                        daily.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'day': date.strftime('%A'),
                            'high': round(item['main']['temp_max']),
                            'low': round(item['main']['temp_min']),
                            'description': item['weather'][0]['description'].title()
                        })
                        current_date = date
                        if len(daily) >= 5:
                            break
                return {'daily': daily}

            elif report_type == 'detailed':
                # Both hourly and daily
                hourly_data = self._process_forecast(forecast_data, 'hourly')
                daily_data = self._process_forecast(forecast_data, 'daily')
                return {**hourly_data, **daily_data}

        except Exception as e:
            logger.error(f"Forecast processing error: {e}")
            return {}

    def format_weather_response(self, weather_data: Dict[str, Any], persona: str = 'default') -> str:
        """Format weather data into natural language response"""
        if not weather_data['success']:
            if persona == 'pirate':
                return f"Arrr! {weather_data['error']} The weather seas be rough today, matey!"
            else:
                return f"I'm sorry, {weather_data['error']}"

        location = weather_data['location']
        current = weather_data['current']
        report_type = weather_data['report_type']

        if persona == 'pirate':
            response = f"Ahoy! Here be the weather report for {location['city']}"
            if location['state']:
                response += f", {location['state']}"
            if location['country']:
                response += f" in {location['country']}"
            response += "!\n\n"

            response += f"🌡️ Current conditions: {current['temperature']}°C, feelin' like {current['feels_like']}°C\n"
            response += f"☁️ Sky conditions: {current['description']}\n"
            response += f"💨 Wind blowin' at {current['wind_speed']} m/s\n"
            response += f"💧 Humidity: {current['humidity']}%\n\n"

        else:
            response = f"Weather Report for {location['city']}"
            if location['state']:
                response += f", {location['state']}"
            if location['country']:
                response += f", {location['country']}"
            response += "\n\n"

            response += f"🌡️ Current: {current['temperature']}°C (feels like {current['feels_like']}°C)\n"
            response += f"☁️ Conditions: {current['description']}\n"
            response += f"💨 Wind: {current['wind_speed']} m/s\n"
            response += f"💧 Humidity: {current['humidity']}%\n"
            response += f"👁️ Visibility: {current['visibility']} km\n\n"

        # Add forecast information
        if 'forecast' in weather_data:
            forecast = weather_data['forecast']

            if 'hourly' in forecast:
                response += "📅 Next 12 Hours:\n"
                for hour in forecast['hourly']:
                    response += f"  {hour['time']}: {hour['temperature']}°C, {hour['description']}\n"
                response += "\n"

            if 'daily' in forecast:
                response += "📊 5-Day Forecast:\n"
                for day in forecast['daily']:
                    response += f"  {day['day']}: {day['high']}°C/{day['low']}°C, {day['description']}\n"
                response += "\n"

        # Add alerts
        if 'alerts' in weather_data and weather_data['alerts']:
            response += "⚠️ Weather Alerts:\n"
            for alert in weather_data['alerts'][:2]:  # Show max 2 alerts
                response += f"  • {alert.get('event', 'Weather Alert')}\n"
            response += "\n"

        if persona == 'pirate':
            response += "Stay safe on the seas, matey! ⚓"
        else:
            response += "Stay safe and prepared! 🌟"

        return response