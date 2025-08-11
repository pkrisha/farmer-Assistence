// Weather Card Live Update Script
// This script updates the weather card with live data

// OpenWeatherMap API configuration
const WEATHER_API_KEY = '784f5def8f7fa2ca1966b061ef80c2fe';
const WEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5';

// Default coordinates (can be changed to user's default location)
const DEFAULT_LAT = 6.1285;  // Lomé, Togo
const DEFAULT_LNG = 1.2255;

// Function to initialize weather updates
function initWeatherCard() {
    // Attempt to get user's location if supported
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // Success callback
            (position) => {
                fetchWeatherForCard(position.coords.latitude, position.coords.longitude);
            },
            // Error callback
            (error) => {
                console.log("Geolocation error or permission denied:", error);
                // Fall back to default location
                fetchWeatherForCard(DEFAULT_LAT, DEFAULT_LNG);
            }
        );
    } else {
        // Geolocation not supported, use default
        fetchWeatherForCard(DEFAULT_LAT, DEFAULT_LNG);
    }
    
    // Set up automatic refresh every 30 minutes
    setInterval(() => {
        refreshWeatherCard();
    }, 30 * 60 * 1000);
}

// Function to refresh weather data
function refreshWeatherCard() {
    // Use last known coordinates or default back to default location
    const lat = localStorage.getItem('weather_lat') || DEFAULT_LAT;
    const lng = localStorage.getItem('weather_lng') || DEFAULT_LNG;
    fetchWeatherForCard(lat, lng);
}

// Function to fetch weather data for the card
function fetchWeatherForCard(lat, lng) {
    // Store coordinates for future refreshes
    localStorage.setItem('weather_lat', lat);
    localStorage.setItem('weather_lng', lng);
    
    // Fetch current weather
    const currentWeatherUrl = `${WEATHER_BASE_URL}/weather?lat=${lat}&lon=${lng}&units=metric&appid=${WEATHER_API_KEY}`;
    
    fetch(currentWeatherUrl)
        .then(response => response.json())
        .then(data => {
            updateWeatherCard(data);
        })
        .catch(error => {
            console.error('Error fetching weather data:', error);
        });
}

// Function to update the weather card with new data
function updateWeatherCard(data) {
    // Update temperature
    const temp = Math.round(data.main.temp);
    document.querySelector('.current-temp').textContent = `${temp}°C`;
    
    // Update condition
    document.querySelector('.weather-condition').textContent = data.weather[0].main;
    
    // Update humidity
    document.querySelector('.weather-item:nth-child(1) .weather-value').textContent = `${data.main.humidity}%`;
    
    // Update wind speed (convert from m/s to km/h)
    const windSpeed = Math.round(data.wind.speed * 3.6);
    document.querySelector('.weather-item:nth-child(2) .weather-value').textContent = `${windSpeed} km/h`;
    
    // Calculate approximate chance of rain based on weather condition
    const rainChance = calculateRainChance(data.weather[0].id);
    document.querySelector('.weather-item:nth-child(3) .weather-value').textContent = `${rainChance}%`;
    
    // Update weather icon based on condition
    updateWeatherIcon(data.weather[0].id);
}

// Function to calculate an approximate chance of rain based on weather conditions
function calculateRainChance(conditionId) {
    // Based on OpenWeatherMap condition codes
    // https://openweathermap.org/weather-conditions
    
    // Thunderstorm
    if (conditionId >= 200 && conditionId < 300) {
        return 80;
    }
    // Drizzle
    else if (conditionId >= 300 && conditionId < 400) {
        return 60;
    }
    // Rain
    else if (conditionId >= 500 && conditionId < 600) {
        return conditionId >= 520 ? 90 : 70;
    }
    // Snow
    else if (conditionId >= 600 && conditionId < 700) {
        return 50;
    }
    // Atmosphere (fog, mist, etc.)
    else if (conditionId >= 700 && conditionId < 800) {
        return 20;
    }
    // Clear
    else if (conditionId === 800) {
        return 0;
    }
    // Clouds
    else if (conditionId > 800) {
        return conditionId === 801 ? 10 : (conditionId === 802 ? 20 : 30);
    }
    
    // Default
    return 0;
}

// Function to update the weather icon based on condition code
function updateWeatherIcon(conditionId) {
    let iconClass = '';
    
    // Based on OpenWeatherMap condition codes
    // Thunderstorm
    if (conditionId >= 200 && conditionId < 300) {
        iconClass = 'fa-bolt';
    }
    // Drizzle
    else if (conditionId >= 300 && conditionId < 400) {
        iconClass = 'fa-cloud-rain';
    }
    // Rain
    else if (conditionId >= 500 && conditionId < 600) {
        iconClass = conditionId === 511 ? 'fa-snowflake' : 'fa-cloud-showers-heavy';
    }
    // Snow
    else if (conditionId >= 600 && conditionId < 700) {
        iconClass = 'fa-snowflake';
    }
    // Atmosphere (fog, mist, etc.)
    else if (conditionId >= 700 && conditionId < 800) {
        iconClass = 'fa-smog';
    }
    // Clear
    else if (conditionId === 800) {
        iconClass = 'fa-sun';
    }
    // Clouds
    else if (conditionId > 800) {
        iconClass = conditionId === 801 ? 'fa-cloud-sun' : 'fa-cloud';
    }
    
    // Update icon class
    const iconElement = document.querySelector('.weather-card .card-icon i');
    iconElement.className = `fas ${iconClass}`;
}

// Initialize the weather card on page load
document.addEventListener('DOMContentLoaded', initWeatherCard);