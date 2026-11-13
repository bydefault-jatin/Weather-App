# Weather App

A lightweight, beginner-friendly full-stack weather web application built for a college project. It allows users to search for any city in the world, view real-time weather conditions, check the Air Quality Index (AQI), browse a 7-day daily forecast, toggle temperatures between Celsius and Fahrenheit, and quickly revisit past searches stored in a local SQLite database.

---

## Features

- **Global City Search**: Converts city names into geographical coordinates using Open-Meteo's Geocoding API.
- **Current Weather Conditions**: Displays temperature, weather condition description, matching emoji, humidity percentage, and wind speed.
- **Air Quality Index (AQI)**: Fetches real-time US AQI data with color-coded safety badges (Good, Moderate, Sensitive, Unhealthy, Very Unhealthy, Hazardous).
- **7-Day Daily Forecast**: Shows upcoming min/max temperatures and expected weather conditions for each day.
- **Client-Side °C / °F Unit Toggle**: Instantly converts all visible temperatures between Celsius and Fahrenheit without re-fetching from the API.
- **Persistent Search History**: Saves successful searches into an SQLite database (`weather.db`) and displays the last 5 unique cities as clickable chips.
- **Robust Edge Case Handling**:
  - Handles missing, whitespace-only, or overly long inputs (>100 characters).
  - Handles punctuation and apostrophes in city names (e.g., *St. John's*).
  - Distinguishes cities with identical names by showing state/region (e.g., *Springfield, Missouri, United States*).
  - Differentiates between non-existent cities (404) and network/timeout failures (503).
  - Disables duplicate button clicks while a request is in flight.

---

## Tech Stack

- **Backend**: Python 3, [Flask](https://flask.palletsprojects.com/) (RESTful API and static file serving)
- **Frontend**: Plain HTML5, CSS3, Vanilla JavaScript (ES6+ `async/await`, `fetch` API, no frontend frameworks)
- **Database**: [SQLite3](https://docs.python.org/3/library/sqlite3.html) (Python's built-in database module)
- **APIs**: [Open-Meteo](https://open-meteo.com/) (Free, no API key required)
  - Geocoding API: Converts city name $\rightarrow$ coordinates `(latitude, longitude)`
  - Forecast API: Retrieves current weather and 7-day forecast data
  - Air Quality API: Retrieves real-time US Air Quality Index (AQI)

---

## Folder Structure

```text
weatherapp/
├── app.py                # Main Flask entry point and API routes
├── weather_service.py    # Open-Meteo API integration and weather code mappings
├── database.py           # SQLite database connection and search history queries
├── requirements.txt      # Python dependencies (Flask, requests)
├── README.md             # Project documentation
├── templates/
│   └── index.html        # Main HTML layout
└── static/
    ├── style.css         # CSS styles and responsive layout
    └── script.js         # Client-side logic, API calls, and unit conversion
```

---

## Installation & How to Run

### Prerequisites
- Python 3.8 or higher installed on your computer.

### Step 1: Navigate to the Project Directory
```bash
cd /Users/utkarsh/Documents/weatherapp
```

### Step 2: Create and Activate a Virtual Environment
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Windows**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python3 app.py
```
*(Or the direct shortcut: `./venv/bin/python3 app.py`)*

### Step 5: Open in Your Browser
Open your browser and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## How It Works Behind the Scenes

1. **User Action**: The user enters a city name (e.g., `"Delhi"`) and clicks **Search** or presses **Enter**.
2. **Frontend Request**: Vanilla JavaScript validates the input and sends an asynchronous request to `/api/weather?city=Delhi` using the browser's `fetch()` API.
3. **Step 1 - Geocoding**: Flask calls Open-Meteo's Geocoding API to resolve the city name into coordinates (`latitude` and `longitude`), region/state, and country.
4. **Step 2 - Forecast & Air Quality**: Flask calls Open-Meteo's Forecast API and Air Quality API in tandem to fetch temperatures, humidity, wind, 7-day forecast, and the US AQI index.
5. **Database Storage**: The backend saves the search to the local SQLite database (`weather.db`) using safe SQL `?` placeholders to prevent SQL injection.
6. **Frontend Rendering**: The browser receives JSON from Flask, populates the weather cards, renders a color-coded AQI badge, and updates recent search chips.
7. **Temperature Conversion**: When the user clicks **°F** or **°C**, JavaScript mathematically converts the stored numbers in memory without triggering a new network request.
