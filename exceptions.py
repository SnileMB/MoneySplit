"""
Custom exception classes for MoneySplit application.
Provides specific exception types for better error handling and debugging.
"""


class MoneySplitException(Exception):
    """Base exception class for all MoneySplit exceptions."""

    pass


class ValidationError(MoneySplitException):
    """Raised when input validation fails."""

    pass


class DatabaseError(MoneySplitException):
    """Raised when database operations fail."""

    pass


class TaxCalculationError(MoneySplitException):
    """Raised when tax calculation fails."""

    pass


class ForecastingError(MoneySplitException):
    """Raised when forecasting fails."""

    pass


class PDFGenerationError(MoneySplitException):
    """Raised when PDF generation fails."""

    pass


class ConfigurationError(MoneySplitException):
    """Raised when configuration is invalid."""

    pass


class NotFoundError(MoneySplitException):
    """Raised when a requested resource is not found."""

    pass


class DuplicateRecordError(MoneySplitException):
    """Raised when attempting to create a duplicate record."""

    pass


class InvalidOperationError(MoneySplitException):
    """Raised when an invalid operation is attempted."""

    pass
