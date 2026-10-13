# OOP with Python — Assignment 2

**Programme:** Master of Science in Data Science  
**Semester:** Advent 2026

## Project Overview

This repository contains two Python mini-projects developed for the Object-Oriented Programming with Python course.

### Mini-Project 1: Weather Forecasting Using Python APIs

The application retrieves weather forecasts using Open-Meteo and MET Norway APIs.

Main features include:

- Geocoding city names into geographical coordinates.
- Retrieving daily temperature, rainfall and wind speed forecasts.
- Organising weather information using pandas DataFrames.
- Creating weather visualisations using Matplotlib.
- Comparing forecasts from two weather providers.
- Handling invalid inputs, network failures and API timeouts.
- Running automated offline tests with pytest.

### Mini-Project 2: Uganda Tax Engine

This mini-project will implement an object-oriented calculator for Ugandan taxes, including PAYE, NSSF, VAT and corporate income tax.

**Status:** Not yet implemented.

## Repository Structure

```text
OOP-python-assignment-2/
├── project1_weather_forecast.ipynb
├── src/
│   └── weather_utils.py
├── tests/
│   └── test_weather.py
├── sample_data/
│   ├── locations.json
│   └── forecast.json
├── requirements.txt
└── README.md
```

## Setup and Execution

1. Open the Jupyter Notebook in Google Colab.
2. Install the dependencies listed in `requirements.txt` if necessary.
3. In the notebook configuration cell, specify the city, forecast days and a genuine contact email for MET Norway.
4. Run the notebook from top to bottom.
5. Review the forecast tables, charts and weather comparison.

An internet connection is required for live API requests. The automated parsing tests use saved JSON data and can run offline.

## Testing

Run the tests from the repository's main directory:

```bash
python -m pytest tests/ -v
```

The weather project includes five tests covering location parsing, empty and missing results, weather-code descriptions and forecast-data parsing.

## Summary of Findings

The weather application successfully retrieved forecasts for Kampala, Uganda, from Open-Meteo and MET Norway.

The two providers produced different temperature predictions on some dates, demonstrating that forecast results can vary between providers. These differences do not establish which provider is more accurate without comparison against observed weather data.

The project also demonstrated how exception handling, request retries and offline testing improve application reliability.

## Data Sources

- Open-Meteo: https://open-meteo.com/
- MET Norway: https://api.met.no/

## AI Use Declaration

AI assistance was used to explain programming concepts, suggest code structures, support debugging, develop test examples and improve documentation. The code was executed and tested using Google Colab and GitHub. I remain responsible for understanding, verifying and explaining the submitted work.
