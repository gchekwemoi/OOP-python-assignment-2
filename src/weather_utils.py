"""Reusable functions for the weather forecast project."""

import pandas as pd
import requests
import time

def parse_locations(data: dict) -> list:
    """Extract matching locations from API data."""
    return data.get("results", [])


def parse_forecast(data: dict) -> pd.DataFrame:
    """Convert daily weather data into a DataFrame."""
    return pd.DataFrame(data["daily"])


def decode_weather(code: int) -> str:
    """Convert a weather code into a description."""

    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return weather_codes.get(
        code, "Unknown weather condition"
    )

class WeatherAPIError(Exception):
    """Raised when a weather API request fails."""
    pass


def safe_request(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float = 10,
    max_retries: int = 3
) -> dict:
    """Retrieve JSON data with automatic retries."""

    if max_retries < 1:
        raise ValueError("max_retries must be at least 1.")

    if timeout <= 0:
        raise ValueError("Timeout must be positive.")

    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as error:

            if isinstance(error, requests.exceptions.HTTPError):
                status = error.response.status_code

                if 400 <= status < 500 and status != 429:
                    raise WeatherAPIError(
                        f"Client error: {error}"
                    ) from error

            if attempt == max_retries - 1:
                raise WeatherAPIError(
                    f"Request failed after "
                    f"{max_retries} attempts: {error}"
                ) from error

            wait_time = 2 ** attempt

            print(
                f"Attempt {attempt + 1} failed. "
                f"Retrying in {wait_time} seconds..."
            )
            time.sleep(wait_time)

    raise WeatherAPIError("Request failed.")


def geocode(name: str) -> list:
    """Return candidate locations for a city name."""

    if not name.strip():
        return []

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": name,
        "count": 10,
        "language": "en",
        "format": "json"
    }

    data = safe_request(url, params=params)

    return parse_locations(data)


def get_forecast(
    lat: float,
    lon: float,
    days: int = 7
) -> dict:
    """Retrieve a daily weather forecast."""

    if not -90 <= lat <= 90:
        raise ValueError("Invalid latitude.")

    if not -180 <= lon <= 180:
        raise ValueError("Invalid longitude.")

    if not 1 <= days <= 16:
        raise ValueError("Forecast days must be 1 to 16.")

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
            "weather_code"
        ],
        "timezone": "auto",
        "forecast_days": days
    }

    return safe_request(url, params=params)
