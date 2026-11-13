# app.py - Flask backend server for Weather App

from flask import Flask, render_template, request, jsonify
from weather_service import get_coordinates, get_weather, get_weather_description, get_aqi, WeatherServiceError
from database import init_db, insert_search, get_recent_searches

# Initialize Flask application
app = Flask(__name__)

# Automatically create the database table on startup
init_db()


@app.route('/')
def index():
    """
    Renders the main HTML page (templates/index.html).
    """
    return render_template('index.html')


@app.route('/api/weather')
def weather_api():
    """
    API endpoint: /api/weather?city=<name>
    Fetches coordinates, weather information, and AQI for the specified city.
    """
    raw_city = request.args.get('city')

    # Edge Case 1: Missing or whitespace-only input
    if not raw_city or not raw_city.strip():
        return jsonify({
            "success": False,
            "error": "City name is required. Example: /api/weather?city=Delhi"
        }), 400

    city_name = raw_city.strip()

    # Edge Case 2: Very long input
    if len(city_name) > 100:
        return jsonify({
            "success": False,
            "error": "City name is too long (maximum 100 characters)."
        }), 400

    # Edge Case 3: Input contains only symbols / punctuation
    if not any(char.isalnum() for char in city_name):
        return jsonify({
            "success": False,
            "error": "City name must contain at least one letter or number."
        }), 400

    try:
        # Step 1: Geocoding lookup
        coords = get_coordinates(city_name)

        if not coords:
            return jsonify({
                "success": False,
                "error": f"City '{city_name}' could not be found. Please check spelling."
            }), 404

        # Step 2: Forecast lookup
        weather = get_weather(coords["latitude"], coords["longitude"])

        # Step 3: Air Quality Index (AQI) lookup
        aqi_data = get_aqi(coords["latitude"], coords["longitude"])

        # Save successful search to SQLite database
        location_descriptor = coords["country"]
        if coords.get("admin1") and coords["admin1"].lower() != coords["name"].lower():
            location_descriptor = f"{coords['admin1']}, {coords['country']}" if coords["country"] else coords["admin1"]

        insert_search(coords["name"], location_descriptor)

        # Look up text description and emoji for current weather code
        current_condition = get_weather_description(weather["weather_code"])

        # Format 7-day forecast
        formatted_forecast = []
        for day in weather["forecast"]:
            day_condition = get_weather_description(day["weather_code"])
            formatted_forecast.append({
                "date": day["date"],
                "max_temp": day["max_temp"],
                "min_temp": day["min_temp"],
                "weather_code": day["weather_code"],
                "description": day_condition["description"],
                "emoji": day_condition["emoji"]
            })

        # Return full payload with HTTP 200 (OK)
        return jsonify({
            "success": True,
            "city": coords,
            "current": {
                "temperature": weather["temperature"],
                "humidity": weather["humidity"],
                "wind_speed": weather["wind_speed"],
                "weather_code": weather["weather_code"],
                "description": current_condition["description"],
                "emoji": current_condition["emoji"],
                "aqi": aqi_data
            },
            "forecast": formatted_forecast
        }), 200

    except WeatherServiceError as service_err:
        return jsonify({
            "success": False,
            "error": str(service_err)
        }), 503

    except Exception:
        return jsonify({
            "success": False,
            "error": "An unexpected server error occurred."
        }), 500


@app.route('/api/history')
def history_api():
    """
    API endpoint: /api/history
    Returns the last 5 unique recent searches from the database as JSON.
    """
    try:
        recent_searches = get_recent_searches(limit=5)
        return jsonify({
            "success": True,
            "history": recent_searches
        }), 200
    except Exception:
        return jsonify({
            "success": False,
            "error": "Failed to load search history."
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
