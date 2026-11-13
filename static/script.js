// static/script.js - Robust Frontend Functionality for Weather App with AQI

// 1. Grab HTML elements by their IDs
const cityInput = document.getElementById("city-input");
const searchBtn = document.getElementById("search-btn");
const loadingDiv = document.getElementById("loading");
const errorDiv = document.getElementById("error-message");
const currentWeatherSection = document.getElementById("current-weather");
const forecastSection = document.getElementById("forecast-section");
const forecastContainer = document.getElementById("forecast-container");

// Elements for Recent Searches
const recentContainer = document.getElementById("recent-container");
const recentChips = document.getElementById("recent-chips");

// Unit Toggle Buttons
const unitCBtn = document.getElementById("unit-c");
const unitFBtn = document.getElementById("unit-f");

// Elements inside Current Weather
const cityNameEl = document.getElementById("city-name");
const weatherEmojiEl = document.getElementById("weather-emoji");
const temperatureEl = document.getElementById("temperature");
const weatherDescEl = document.getElementById("weather-desc");
const humidityEl = document.getElementById("humidity");
const windSpeedEl = document.getElementById("wind-speed");
const aqiBadgeEl = document.getElementById("aqi-badge");

// 2. Global State Variables
let currentUnit = "C";
let lastWeatherData = null;


// 3. Helper function to format temperatures in either °C or °F
function formatTemp(tempC) {
    if (tempC === null || tempC === undefined) {
        return "--";
    }

    if (currentUnit === "F") {
        const tempF = (tempC * 9 / 5) + 32;
        const roundedF = Math.round(tempF * 10) / 10;
        return `${roundedF} °F`;
    }

    return `${tempC} °C`;
}


// 4. Helper function to toggle between °C and °F
function setUnit(unit) {
    if (currentUnit === unit) return;

    currentUnit = unit;

    unitCBtn.classList.toggle("active", currentUnit === "C");
    unitFBtn.classList.toggle("active", currentUnit === "F");

    if (lastWeatherData) {
        displayCurrentWeather(lastWeatherData.city, lastWeatherData.current);
        displayForecast(lastWeatherData.forecast);
    }
}


// 5. Helper function to reset UI visibility
function resetUI() {
    loadingDiv.classList.add("hidden");
    errorDiv.classList.add("hidden");
    errorDiv.textContent = "";
    currentWeatherSection.classList.add("hidden");
    forecastSection.classList.add("hidden");
    forecastContainer.innerHTML = "";
}


// 6. Load and display recent search chips from /api/history
async function loadRecentSearches() {
    try {
        const response = await fetch("/api/history");
        const data = await response.json();

        if (response.ok && data.history && data.history.length > 0) {
            recentChips.innerHTML = "";

            data.history.forEach((item) => {
                const chip = document.createElement("button");
                chip.className = "chip";
                chip.type = "button";
                chip.textContent = item.country ? `${item.city}, ${item.country}` : item.city;

                chip.addEventListener("click", () => {
                    cityInput.value = item.city;
                    fetchWeather(item.city);
                });

                recentChips.appendChild(chip);
            });

            recentContainer.classList.remove("hidden");
        } else {
            recentContainer.classList.add("hidden");
        }
    } catch (err) {
        console.error("Could not load recent searches:", err);
    }
}


// 7. Main function to fetch weather data with edge-case protection
async function fetchWeather(city) {
    const trimmedCity = city ? city.trim() : "";

    if (!trimmedCity) {
        resetUI();
        errorDiv.textContent = "Please enter a city name.";
        errorDiv.classList.remove("hidden");
        return;
    }

    if (trimmedCity.length > 100) {
        resetUI();
        errorDiv.textContent = "City name is too long (maximum 100 characters).";
        errorDiv.classList.remove("hidden");
        return;
    }

    resetUI();
    loadingDiv.classList.remove("hidden");

    searchBtn.disabled = true;
    searchBtn.textContent = "Searching...";

    try {
        const response = await fetch(`/api/weather?city=${encodeURIComponent(trimmedCity)}`);
        const data = await response.json();

        if (!response.ok) {
            errorDiv.textContent = data.error || "Unable to fetch weather data.";
            errorDiv.classList.remove("hidden");
            return;
        }

        lastWeatherData = data;

        displayCurrentWeather(data.city, data.current);
        displayForecast(data.forecast);

        loadRecentSearches();

    } catch (err) {
        errorDiv.textContent = "Network error: Unable to reach the server. Please check your internet connection.";
        errorDiv.classList.remove("hidden");
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = "Search";
        loadingDiv.classList.add("hidden");
    }
}


// 8. Function to fill in Current Weather & AQI details
function displayCurrentWeather(city, current) {
    const locationParts = [city.name];
    if (city.admin1 && city.admin1.toLowerCase() !== city.name.toLowerCase()) {
        locationParts.push(city.admin1);
    }
    if (city.country) {
        locationParts.push(city.country);
    }

    cityNameEl.textContent = locationParts.join(", ");
    weatherEmojiEl.textContent = current.emoji;
    temperatureEl.textContent = ` ${formatTemp(current.temperature)}`;
    weatherDescEl.textContent = current.description;
    humidityEl.textContent = current.humidity;
    windSpeedEl.textContent = current.wind_speed;

    // Display Air Quality Index badge
    if (current.aqi && current.aqi.value !== null) {
        aqiBadgeEl.textContent = `${current.aqi.value} • ${current.aqi.category}`;
        aqiBadgeEl.style.backgroundColor = current.aqi.color;
        // Moderate (yellow) looks better with dark text for readability
        if (current.aqi.category === "Moderate") {
            aqiBadgeEl.style.color = "#212529";
        } else {
            aqiBadgeEl.style.color = "#ffffff";
        }
    } else {
        aqiBadgeEl.textContent = "Unavailable";
        aqiBadgeEl.style.backgroundColor = "#6c757d";
        aqiBadgeEl.style.color = "#ffffff";
    }

    currentWeatherSection.classList.remove("hidden");
}


// 9. Function to build the 7-day forecast cards
function displayForecast(forecastDays) {
    forecastContainer.innerHTML = "";

    forecastDays.forEach((day) => {
        const card = document.createElement("div");
        card.className = "forecast-card";

        const minFormatted = formatTemp(day.min_temp);
        const maxFormatted = formatTemp(day.max_temp);

        card.innerHTML = `
            <div class="date">${day.date}</div>
            <div class="emoji">${day.emoji}</div>
            <div class="desc">${day.description}</div>
            <div class="temps">
                <span>${minFormatted}</span> / <strong>${maxFormatted}</strong>
            </div>
        `;

        forecastContainer.appendChild(card);
    });

    forecastSection.classList.remove("hidden");
}


// 10. Event Listeners

searchBtn.addEventListener("click", () => {
    fetchWeather(cityInput.value);
});

cityInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        fetchWeather(cityInput.value);
    }
});

unitCBtn.addEventListener("click", () => setUnit("C"));
unitFBtn.addEventListener("click", () => setUnit("F"));

document.addEventListener("DOMContentLoaded", () => {
    loadRecentSearches();
});
