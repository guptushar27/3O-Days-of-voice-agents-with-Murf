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
        # Support both WeatherAPI.com and OpenWeatherMap
        self.weather_api_key = api_key or os.environ.get('WEATHER_API_KEY')
        self.openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')

        # Prefer WeatherAPI.com as it's more reliable
        self.api_key = self.weather_api_key or self.openweather_api_key

        # Set base URL based on which API key is available
        if self.weather_api_key:
            self.base_url = "http://api.weatherapi.com/v1"
            self.service_type = "weatherapi"
        elif self.openweather_api_key:
            self.base_url = "http://api.openweathermap.org/data/2.5"
            self.service_type = "openweather"
        else:
            self.base_url = None
            self.service_type = None

    def get_comprehensive_weather_analysis(self, city: str, date_context: str = None) -> Dict[str, Any]:
        """Get comprehensive weather analysis for a city"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'Weather API key not configured. Please add WEATHER_API_KEY or OPENWEATHER_API_KEY to your environment.',
                    'current_conditions': {},
                    'forecast': []
                }

            # Use WeatherAPI.com if available (preferred)
            if self.service_type == "weatherapi":
                return self._get_weather_from_weatherapi(city)
            # Fallback to OpenWeatherMap
            elif self.service_type == "openweather":
                return self._get_weather_from_openweather(city)
            else:
                return {
                    'success': False,
                    'error': 'No valid weather API service configured',
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

    def _get_weather_from_weatherapi(self, city: str) -> Dict[str, Any]:
        """Get weather from WeatherAPI.com"""
        try:
            # Clean and validate city name
            clean_city = self._clean_city_name(city)
            
            current_url = f"{self.base_url}/current.json"
            params = {
                'key': self.weather_api_key,
                'q': clean_city,
                'aqi': 'no'
            }

            logger.info(f"🌤️ WeatherAPI request for city: '{clean_city}' (original: '{city}')")
            response = requests.get(current_url, params=params, timeout=10)
            logger.info(f"🌤️ WeatherAPI response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                actual_city = data['location']['name']
                actual_region = data['location']['region']
                actual_country = data['location']['country']
                
                # Log for debugging
                logger.info(f"🌤️ Weather data retrieved for: {actual_city}, {actual_region}, {actual_country}")
                
                return {
                    'success': True,
                    'current_conditions': {
                        'temperature': data['current']['temp_c'],
                        'feels_like': data['current']['feelslike_c'],
                        'humidity': data['current']['humidity'],
                        'description': data['current']['condition']['text'],
                        'city': actual_city,
                        'region': actual_region,
                        'country': actual_country,
                        'wind_speed': data['current']['wind_kph'],
                        'visibility': data['current']['vis_km']
                    },
                    'forecast': [],
                    'service_used': 'WeatherAPI.com'
                }
            else:
                error_msg = f'WeatherAPI.com error: {response.status_code}'
                if response.status_code == 400:
                    error_msg += f' - City "{clean_city}" not found. Please check the city name spelling.'
                elif response.status_code == 401:
                    error_msg += ' - Invalid API key'
                elif response.status_code == 403:
                    error_msg += ' - API key quota exceeded'
                logger.error(f"🌤️ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'current_conditions': {},
                    'forecast': []
                }

        except Exception as e:
            logger.error(f"🌤️ WeatherAPI request failed: {str(e)}")
            return {
                'success': False,
                'error': f'WeatherAPI.com request failed: {str(e)}',
                'current_conditions': {},
                'forecast': []
            }

    def _get_weather_from_openweather(self, city: str) -> Dict[str, Any]:
        """Get weather from OpenWeatherMap (fallback)"""
        try:
            current_url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.openweather_api_key,
                'units': 'metric'
            }

            response = requests.get(current_url, params=params, timeout=10)

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
                        'country': data['sys']['country'],
                        'wind_speed': data['wind']['speed'],
                        'visibility': data.get('visibility', 0) / 1000 if data.get('visibility') else 'N/A'
                    },
                    'forecast': [],
                    'service_used': 'OpenWeatherMap'
                }
            else:
                return {
                    'success': False,
                    'error': f'OpenWeatherMap error: {response.status_code} - Check your API key and city name',
                    'current_conditions': {},
                    'forecast': []
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'OpenWeatherMap request failed: {str(e)}',
                'current_conditions': {},
                'forecast': []
            }

    def _clean_city_name(self, city: str) -> str:
        """Clean and validate city name for API requests"""
        if not city:
            return ""
        
        # Remove extra whitespace and normalize
        city = city.strip()
        
        # Handle specific country/state requests
        city_lower = city.lower()
        if 'delhi' in city_lower and 'india' in city_lower:
            return "Delhi,India"
        elif 'mumbai' in city_lower and 'india' in city_lower:
            return "Mumbai,India"
        elif 'bangalore' in city_lower and 'india' in city_lower:
            return "Bangalore,India"
        
        # Handle common misspellings and variations
        city_corrections = {
            'New Yourk': 'New York',
            'Dellhi': 'Delhi,India',
            'Mumbay': 'Mumbai,India',
            'Bangalor': 'Bangalore,India',
            'Chenai': 'Chennai,India',
            'Japur': 'Jaipur,India',
            'Calcuta': 'Kolkata,India',
            'Hydrabad': 'Hyderabad,India',
            'Poon': 'Pune,India',
            'Ahmadabad': 'Ahmedabad,India'
        }
        
        # Check for corrections first
        city_title = city.title()
        if city_title in city_corrections:
            city = city_corrections[city_title]
            logger.info(f"🌤️ Corrected city name to: {city}")
            return city
        
        # For Indian cities, default to India if no country specified
        indian_cities = ['delhi', 'mumbai', 'bangalore', 'kolkata', 'chennai', 'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'bhopal', 'visakhapatnam', 'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra']
        
        if city_lower in indian_cities and 'india' not in city_lower:
            return f"{city.title()},India"
        
        # Remove common words that shouldn't be part of city name
        unwanted_words = ['weather', 'temperature', 'forecast', 'city', 'and']
        words = city.split()
        cleaned_words = []
        
        for word in words:
            if word.lower() not in unwanted_words:
                cleaned_words.append(word)
        
        return ','.join(cleaned_words) if ',' in city else ' '.join(cleaned_words)

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
        region = conditions.get('region', '')
        country = conditions.get('country', '')

        # Create location string with proper formatting
        location_parts = [city]
        if region and region != city:
            location_parts.append(region)
        if country:
            location_parts.append(country)
        full_location = ', '.join(location_parts)

        if persona == 'pirate':
            return f"Arrr! The weather at {full_location} be {description} with a temperature of {temp}°C (feels like {feels_like}°C), humidity at {humidity}%. The winds be tellin' tales of the sea, matey!"
        else:
            return f"The weather in {full_location} is {description} with a temperature of {temp}°C (feels like {feels_like}°C) and humidity at {humidity}%."

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

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city with enhanced error handling and fallback"""
        try:
            logger.info(f"🌤️ Getting weather for: {city}")

            if not self.api_key:
                logger.warning("Weather API key not configured")
                return {
                    'success': False,
                    'error': 'Weather API key not configured',
                    'fallback_response': f"I'd love to help you check the weather in {city}, but I need a weather API key to be configured. You can set this up in the API settings panel or add WEATHER_API_KEY to your environment variables."
                }

            # Clean and format city name
            city = city.strip().title()

            # Try WeatherAPI.com first, then OpenWeatherMap as fallback
            weather_data = self._try_weatherapi_com(city)

            if not weather_data['success'] and self._has_openweather_fallback():
                logger.info("🌤️ Trying OpenWeatherMap as fallback")
                weather_data = self._try_openweathermap(city)

            return weather_data

        except Exception as e:
            logger.error(f"Weather service error: {str(e)}")
            return {
                'success': False,
                'error': f'Weather service error: {str(e)}',
                'fallback_response': f"I apologize, but I'm having trouble getting weather information for {city} right now. The weather service might be temporarily unavailable. Please try again in a moment."
            }

    def _try_weatherapi_com(self, city: str) -> Dict[str, Any]:
        """Try WeatherAPI.com for weather data"""
        try:
            # Construct API URL for WeatherAPI.com
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': city,
                'aqi': 'yes'  # Include air quality data
            }

            logger.info(f"🌤️ Making WeatherAPI.com request to: {url}")
            logger.info(f"🌤️ Request params: q={city}, aqi=yes")

            response = requests.get(url, params=params, timeout=10)
            logger.info(f"🌤️ WeatherAPI.com response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                logger.info("🌤️ Successfully fetched weather data from WeatherAPI.com")

                return {
                    'success': True,
                    'location': {
                        'name': data['location']['name'],
                        'region': data['location']['region'],
                        'country': data['location']['country'],
                        'localtime': data['location']['localtime']
                    },
                    'current': {
                        'temperature': data['current']['temp_c'],
                        'temperature_f': data['current']['temp_f'],
                        'condition': data['current']['condition']['text'],
                        'humidity': data['current']['humidity'],
                        'wind_speed': data['current']['wind_kph'],
                        'wind_direction': data['current']['wind_dir'],
                        'feels_like': data['current']['feelslike_c'],
                        'uv_index': data['current']['uv'],
                        'visibility': data['current']['vis_km']
                    },
                    'air_quality': data.get('current', {}).get('air_quality', {}),
                    'api_used': 'WeatherAPI.com'
                }
            else:
                logger.error(f"WeatherAPI.com error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'WeatherAPI.com error: {response.status_code}',
                    'details': response.text[:200]
                }

        except requests.exceptions.Timeout:
            logger.error("WeatherAPI.com request timed out")
            return {
                'success': False,
                'error': 'WeatherAPI.com service timed out'
            }
        except requests.exceptions.ConnectionError:
            logger.error("WeatherAPI.com connection error")
            return {
                'success': False,
                'error': 'Unable to connect to WeatherAPI.com'
            }
        except Exception as e:
            logger.error(f"WeatherAPI.com service error: {str(e)}")
            return {
                'success': False,
                'error': f'WeatherAPI.com service error: {str(e)}'
            }

    def _has_openweather_fallback(self) -> bool:
        """Check if OpenWeatherMap fallback is available"""
        # Check if we have an OpenWeatherMap API key as fallback
        openweather_key = os.environ.get('OPENWEATHER_API_KEY')
        return openweather_key is not None

    def _try_openweathermap(self, city: str) -> Dict[str, Any]:
        """Try OpenWeatherMap as fallback"""
        try:
            openweather_key = os.environ.get('OPENWEATHER_API_KEY')
            if not openweather_key:
                return {
                    'success': False,
                    'error': 'OpenWeatherMap fallback not configured'
                }

            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': openweather_key,
                'units': 'metric'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info("🌤️ Successfully fetched weather data from OpenWeatherMap")

                return {
                    'success': True,
                    'location': {
                        'name': data['name'],
                        'region': '',
                        'country': data['sys']['country'],
                        'localtime': ''
                    },
                    'current': {
                        'temperature': data['main']['temp'],
                        'temperature_f': (data['main']['temp'] * 9/5) + 32,
                        'condition': data['weather'][0]['description'].title(),
                        'humidity': data['main']['humidity'],
                        'wind_speed': data.get('wind', {}).get('speed', 0) * 3.6,  # Convert m/s to km/h
                        'wind_direction': '',
                        'feels_like': data['main']['feels_like'],
                        'uv_index': 0,  # Not available in basic OpenWeather
                        'visibility': data.get('visibility', 0) / 1000  # Convert m to km
                    },
                    'air_quality': {},
                    'api_used': 'OpenWeatherMap (Fallback)'
                }
            else:
                return {
                    'success': False,
                    'error': f'OpenWeatherMap error: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"OpenWeatherMap fallback error: {str(e)}")
            return {
                'success': False,
                'error': f'OpenWeatherMap fallback error: {str(e)}'
            }

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
            current = self.get_current_weather(coords['name'])
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
                    'temperature': round(current['current']['temperature']),
                    'feels_like': round(current['current']['feels_like']),
                    'description': current['current']['condition'],
                    'humidity': current['current']['humidity'],
                    'pressure': 0, # Not available in current response structure for weatherapi
                    'visibility': current['current']['visibility'],
                    'wind_speed': current['current']['wind_speed'],
                    'wind_direction': current['current']['wind_direction'],
                    'uv_index': current['current']['uv_index'],
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
            if location.get('state'):
                response += f", {location['state']}"
            if location.get('country'):
                response += f" in {location['country']}"
            response += "!\n\n"

            response += f"🌡️ Current conditions: {current['temperature']}°C, feelin' like {current['feels_like']}°C\n"
            response += f"☁️ Sky conditions: {current['description']}\n"
            response += f"💨 Wind blowin' at {current['wind_speed']} kph\n"
            response += f"💧 Humidity: {current['humidity']}%\n\n"

        else:
            response = f"Weather Report for {location['city']}"
            if location.get('state'):
                response += f", {location['state']}"
            if location.get('country'):
                response += f", {location['country']}"
            response += "\n\n"

            response += f"🌡️ Current: {current['temperature']}°C (feels like {current['feels_like']}°C)\n"
            response += f"☁️ Conditions: {current['description']}\n"
            response += f"💨 Wind: {current['wind_speed']} kph\n"
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
