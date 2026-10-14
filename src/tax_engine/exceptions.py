
"""Custom exceptions for the Uganda Tax Engine."""


class TaxError(Exception):
    """Base exception for tax-related errors."""
    pass


class InvalidIncomeError(TaxError):
    """Raised when income is invalid."""
    pass


class NoScheduleForDateError(TaxError):
    """Raised when no tax schedule exists for a date."""
    pass
