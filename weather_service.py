# weather_service.py - Module for fetching weather data from Open-Meteo APIs

import requests

class WeatherServiceError(Exception):
    """Raised when external API request fails due to network, timeout, or server errors."""
    pass


# Dictionary mapping WMO Weather interpretation codes to text descriptions and emojis
WEATHER_CODES = {
    0: {"description": "Clear sky", "emoji": "☀️"},
    1: {"description": "Mainly clear", "emoji": "🌤️"},
    2: {"description": "Partly cloudy", "emoji": "⛅"},
    3: {"description": "Overcast", "emoji": "☁️"},
    45: {"description": "Fog", "emoji": "🌫️"},
    48: {"description": "Depositing rime fog", "emoji": "🌫️"},
    51: {"description": "Light drizzle", "emoji": "🌦️"},
    53: {"description": "Moderate drizzle", "emoji": "🌦️"},
    55: {"description": "Dense drizzle", "emoji": "🌧️"},
    56: {"description": "Light freezing drizzle", "emoji": "🌧️"},
    57: {"description": "Dense freezing drizzle", "emoji": "🌧️"},
    61: {"description": "Slight rain", "emoji": "🌧️"},
    63: {"description": "Moderate rain", "emoji": "🌧️"},
    65: {"description": "Heavy rain", "emoji": "🌧️"},
    66: {"description": "Light freezing rain", "emoji": "🌧️"},
    67: {"description": "Heavy freezing rain", "emoji": "🌧️"},
    71: {"description": "Slight snow fall", "emoji": "🌨️"},
    73: {"description": "Moderate snow fall", "emoji": "🌨️"},
    75: {"description": "Heavy snow fall", "emoji": "❄️"},
    77: {"description": "Snow grains", "emoji": "❄️"},
    80: {"description": "Slight rain showers", "emoji": "🌦️"},
    81: {"description": "Moderate rain showers", "emoji": "🌧️"},
    82: {"description": "Violent rain showers", "emoji": "⛈️"},
    85: {"description": "Slight snow showers", "emoji": "🌨️"},
    86: {"description": "Heavy snow showers", "emoji": "❄️"},
    95: {"description": "Thunderstorm", "emoji": "⛈️"},
    96: {"description": "Thunderstorm with slight hail", "emoji": "⛈️"},
    99: {"description": "Thunderstorm with heavy hail", "emoji": "⛈️"},
}

def get_weather_description(code):
    """
    Helper function to safely get description and emoji for a weather code.
    Defaults to Unknown if code is not found in the dictionary.
    """
    return WEATHER_CODES.get(code, {"description": "Unknown", "emoji": "🌡️"})


def get_aqi_category(aqi_val):
    """
    Maps standard US AQI values (0-500) to human-readable categories and color codes.
    """
    if aqi_val is None:
        return {"category": "Unavailable", "color": "#6c757d"}
    if aqi_val <= 50:
        return {"category": "Good", "color": "#28a745"}
    elif aqi_val <= 100:
        return {"category": "Moderate", "color": "#ffc107"}
    elif aqi_val <= 150:
        return {"category": "Sensitive", "color": "#fd7e14"}
    elif aqi_val <= 200:
        return {"category": "Unhealthy", "color": "#dc3545"}
    elif aqi_val <= 300:
        return {"category": "Very Unhealthy", "color": "#6f42c1"}
    else:
        return {"category": "Hazardous", "color": "#721c24"}


def get_coordinates(city):
    """
    Calls Open-Meteo Geocoding API to convert city name into coordinates.
    Returns a dictionary with name, admin1 (state/province), country, latitude, longitude.
    Returns None if the city is not found.
    Raises WeatherServiceError if there is a network issue, timeout, or API failure.
    """
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(geocoding_url, params=params, timeout=6)
        response.raise_for_status()

        data = response.json()
        results = data.get("results")

        if not results:
            return None

        first_match = results[0]
        return {
            "name": first_match.get("name", city),
            "admin1": first_match.get("admin1", ""),
            "country": first_match.get("country", ""),
            "latitude": first_match.get("latitude"),
            "longitude": first_match.get("longitude")
        }

    except requests.Timeout:
        raise WeatherServiceError("Geocoding service timed out. Please try again.")
    except requests.ConnectionError:
        raise WeatherServiceError("Could not connect to the weather service. Please check your internet connection.")
    except (requests.RequestException, ValueError, KeyError):
        raise WeatherServiceError("An error occurred while contacting the geocoding service.")


def get_weather(lat, lon):
    """
    Calls Open-Meteo Forecast API using latitude and longitude.
    Returns current weather details and a 7-day daily forecast.
    Raises WeatherServiceError if there is a network issue, timeout, or API failure.
    """
    forecast_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }

    try:
        response = requests.get(forecast_url, params=params, timeout=6)
        response.raise_for_status()

        data = response.json()
        current_data = data.get("current", {})
        daily_data = data.get("daily", {})

        dates = daily_data.get("time", [])
        max_temps = daily_data.get("temperature_2m_max", [])
        min_temps = daily_data.get("temperature_2m_min", [])
        weather_codes = daily_data.get("weather_code", [])

        forecast = []
        for i in range(len(dates)):
            forecast.append({
                "date": dates[i],
                "max_temp": max_temps[i],
                "min_temp": min_temps[i],
                "weather_code": weather_codes[i]
            })

        return {
            "temperature": current_data.get("temperature_2m"),
            "humidity": current_data.get("relative_humidity_2m"),
            "wind_speed": current_data.get("wind_speed_10m"),
            "weather_code": current_data.get("weather_code"),
            "forecast": forecast
        }

    except requests.Timeout:
        raise WeatherServiceError("Weather forecast service timed out. Please try again.")
    except requests.ConnectionError:
        raise WeatherServiceError("Could not connect to the weather service. Please check your internet connection.")
    except (requests.RequestException, ValueError, KeyError):
        raise WeatherServiceError("An error occurred while contacting the forecast service.")


def get_aqi(lat, lon):
    """
    Calls Open-Meteo Air Quality API to fetch the current Air Quality Index (US AQI).
    Returns a dictionary with value, category, and badge color, or None if unavailable.
    """
    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "us_aqi"
    }

    try:
        response = requests.get(aqi_url, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        aqi_val = current.get("us_aqi")

        category_info = get_aqi_category(aqi_val)
        return {
            "value": aqi_val,
            "category": category_info["category"],
            "color": category_info["color"]
        }
    except Exception:
        # Graceful fallback: return None so that weather info still renders even if AQI fails
        return None


# Test block
if __name__ == "__main__":
    test_city = "Delhi"
    print(f"--- Testing Weather & AQI Service for '{test_city}' ---")
    try:
        coords = get_coordinates(test_city)
        if coords:
            print(f"Found: {coords['name']}, {coords['country']}")
            weather = get_weather(coords["latitude"], coords["longitude"])
            aqi = get_aqi(coords["latitude"], coords["longitude"])
            print("Current Temp:", weather["temperature"], "°C")
            print("AQI:", aqi)
        else:
            print("City not found.")
    except WeatherServiceError as err:
        print("Service error:", err)
