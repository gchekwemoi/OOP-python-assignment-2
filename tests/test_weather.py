
"""Offline tests for the weather forecast project."""

import json
from pathlib import Path

from src.weather_utils import (
    parse_locations,
    parse_forecast,
    decode_weather
)

# Locate the sample_data folder
BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = BASE_DIR / "sample_data"


def load_json(filename: str) -> dict:
    """Load saved JSON data for offline testing."""
    with open(SAMPLE_DIR / filename, "r") as file:
        return json.load(file)


# Test 1: Valid city
def test_valid_city():
    data = load_json("locations.json")
    result = parse_locations(data)

    assert result[0]["name"] == "Kampala"


# Test 2: Empty locations
def test_empty_locations():
    assert parse_locations({"results": []}) == []


# Test 3: Missing results key
def test_missing_results():
    assert parse_locations({}) == []


# Test 4: Weather descriptions
def test_weather_codes():
    assert decode_weather(0) == "Clear sky"
    assert decode_weather(3) == "Overcast"
    assert decode_weather(95) == "Thunderstorm"
    assert decode_weather(999) == "Unknown weather condition"


# Test 5: Forecast parsing
def test_forecast_parsing():
    data = load_json("forecast.json")
    result = parse_forecast(data)

    assert len(result) == 2
    assert result["temperature_2m_max"].iloc[0] == 25.6
    assert result["precipitation_sum"].iloc[1] == 2.0
