
"""Offline tests for the weather forecast project."""

from src.weather_utils import (
    parse_locations,
    parse_forecast,
    decode_weather
)


# Test 1: Valid city
def test_valid_city():
    sample = {
        "results": [{"name": "Kampala"}]
    }

    result = parse_locations(sample)

    assert result[0]["name"] == "Kampala"


# Test 2: Empty locations
def test_empty_locations():
    sample = {"results": []}

    assert parse_locations(sample) == []


# Test 3: Missing results key
def test_missing_results():
    sample = {}

    assert parse_locations(sample) == []


# Test 4: Weather descriptions
def test_weather_codes():
    assert decode_weather(0) == "Clear sky"
    assert decode_weather(3) == "Overcast"
    assert decode_weather(95) == "Thunderstorm"
    assert decode_weather(999) == "Unknown weather condition"


# Test 5: Forecast parsing
def test_forecast_parsing():
    sample = {
        "daily": {
            "time": ["2026-10-12", "2026-10-13"],
            "temperature_2m_max": [25.6, 25.3],
            "precipitation_sum": [2.2, 2.0]
        }
    }

    result = parse_forecast(sample)

    assert len(result) == 2
    assert result["temperature_2m_max"].iloc[0] == 25.6
    assert result["precipitation_sum"].iloc[1] == 2.0
