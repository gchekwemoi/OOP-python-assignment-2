# Object-Oriented Programming with Python – Assignment 2

**Programme:** Master of Science in Data Science  
**Academic Session:** Advent 2026  
**Chekwemoi Gloria  
**GitHub Repository:** https://github.com/gchekwemoi/OOP-python-assignment-2


## 1. Introduction

This repository contains two mini-projects developed to demonstrate Object-Oriented Programming (OOP) concepts using Python. The projects focus on solving practical problems through reusable code, modular design, exception handling and testing.

## 2. Mini-Project 1: Weather Forecast Application

The Weather Forecast Application retrieves weather information for selected locations using the Open-Meteo API. It processes JSON responses, interprets weather codes and displays forecast information.

The main functions are stored in `src/weather_utils.py`, while `project1_weather_forecast.ipynb` demonstrates their application. Sample JSON files are provided to support offline testing.

The project covers API integration, input validation, error handling and reusable Python functions.

## 3. Mini-Project 2: Uganda Tax Engine

The Uganda Tax Engine calculates selected taxes and payroll deductions using Python classes.

It includes:

- PAYE for resident and non-resident employees.
- Payroll calculations covering NSSF, annual LST and net salary.
- VAT calculations for standard-rated, zero-rated and exempt supplies.
- Corporate Income Tax at the configured standard rate of 30%.
- TaxPlanner for comparing two tax scenarios.

The `Money` class uses `Decimal` to improve the reliability of financial calculations. The abstract `Tax` class provides a common calculation interface, demonstrating inheritance and polymorphism.

The `PayrollCalculator` and `TaxPlanner` reuse existing tax classes, demonstrating composition.

### Interactive User Interface

I used **`ipywidgets`** to develop simple interactive calculators within Google Colab. This library provides text fields, dropdown menus, checkboxes and buttons.

I selected it because it works within Jupyter notebooks, does not require building a separate website and allows users to enter their own figures without changing the Python code.

The interface is separate from the calculation logic. It passes the user's inputs to the OOP classes and displays the results.

The interactive tools are demonstrated in `project2_uganda_tax_engine.ipynb`.

## 4. Tools and Libraries

| Tool/Library | Purpose |
|---|---|
| Python | Main programming language |
| Google Colab | Development and demonstrations |
| GitHub | Code storage and version control |
| Open-Meteo API | Weather forecast data |
| `Decimal` | Monetary calculations |
| `pandas` | Tabular results |
| `matplotlib` | Data visualisation |
| `ipywidgets` | Interactive tax calculator interfaces |
| `pytest` | Automated testing |
| `Hypothesis` | Property-based testing |
| GitHub Actions | Automatic test execution |

## 5. How to Run the Projects

Open either notebook in Google Colab:

- `project1_weather_forecast.ipynb`
- `project2_uganda_tax_engine.ipynb`

The notebooks include setup instructions for loading the repository and installing required libraries. Run the cells in order.

For the Uganda Tax Engine, users can enter their own figures in the interactive calculators and click the relevant calculation button.

Automated tests can be run using:

```bash
python -m pytest tests/ -v
```

## 6. Challenges and Lessons Learned

During development, I encountered errors involving imports, tax calculation methods and differences between the code and test files. GitHub Actions helped identify these problems and verify the corrections.

I also learned the importance of using `Decimal` for money, organising calculations into reusable classes and separating the user interface from the underlying tax logic.

## 7. Limitations

The Weather Forecast Application depends on external API availability.

The Uganda Tax Engine is an educational demonstration and does not cover every statutory requirement. In particular, the payroll model assumes annual LST is deducted once in July, while the VAT and corporate tax modules use simplified assumptions. The calculations should be verified against applicable legislation before real-world use.

## 8. AI-Use Declaration

I used ChatGPT to assist with understanding OOP concepts, developing and explaining code, identifying errors, preparing tests and improving documentation.

I used GitHub Actions and Google Colab to test and demonstrate the code. The project includes the Python modules, automated tests and notebooks used during development.

## 9. References

- Open-Meteo. (n.d.). *Weather forecast API*. https://open-meteo.com/en/docs
- Python Software Foundation. (n.d.). *Python documentation*. https://docs.python.org/3/
- Project Jupyter. (n.d.). *Jupyter widgets documentation*. https://ipywidgets.readthedocs.io/
- Uganda Revenue Authority. (n.d.). *Official tax information*. https://ura.go.ug/
