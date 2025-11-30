"""
Input validation utilities for MoneySplit.
"""


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_positive_number(value: float, field_name: str) -> float:
    """Validate that a number is positive."""
    if value < 0:
        raise ValidationError(f"{field_name} must be positive, got {value}")
    return value


def validate_work_shares(shares: list[float]) -> None:
    """Validate that work shares sum to 1.0 (with small tolerance)."""
    total = sum(shares)
    if abs(total - 1.0) > 0.01:
        raise ValidationError(f"Work shares must sum to 1.0, got {total:.2f}")


def validate_work_share(share: float) -> float:
    """Validate a single work share is between 0 and 1."""
    if not 0 <= share <= 1:
        raise ValidationError(f"Work share must be between 0 and 1, got {share}")
    return share


def validate_non_empty_string(value: str, field_name: str) -> str:
    """Validate that a string is not empty."""
    value = value.strip()
    if not value:
        raise ValidationError(f"{field_name} cannot be empty")
    return value


def validate_country(country: str) -> str:
    """Validate country name (allows any non-empty string)."""
    country = country.strip()
    if not country:
        raise ValidationError("Country cannot be empty")
    return country


def validate_tax_type(tax_type: str) -> str:
    """Validate tax type."""
    valid_types = ["Individual", "Business"]
    tax_type = tax_type.strip().title()
    if tax_type not in valid_types:
        raise ValidationError(
            f"Tax type must be one of {valid_types}, got '{tax_type}'"
        )
    return tax_type


def validate_tax_rate(rate: float) -> float:
    """Validate tax rate is between 0 and 1."""
    if not 0 <= rate <= 1:
        raise ValidationError(f"Tax rate must be between 0 and 1, got {rate}")
    return rate


def safe_float_input(
    prompt: str, field_name: str = "Value", allow_negative: bool = False
) -> float:
    """Safely get float input from user with validation."""
    while True:
        try:
            value = float(input(prompt))
            if not allow_negative:
                validate_positive_number(value, field_name)
            return value
        except ValueError:
            print(f"❌ Invalid number. Please enter a valid number for {field_name}.")
        except ValidationError as e:
            print(f"❌ {e}")


def safe_int_input(
    prompt: str, field_name: str = "Value", min_value: int = None, max_value: int = None
) -> int:
    """Safely get integer input from user with validation."""
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f"❌ {field_name} must be at least {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"❌ {field_name} must be at most {max_value}.")
                continue
            return value
        except ValueError:
            print(f"❌ Invalid integer. Please enter a valid integer for {field_name}.")


def safe_string_input(prompt: str, field_name: str = "Value") -> str:
    """Safely get non-empty string input from user."""
    while True:
        try:
            value = input(prompt).strip()
            return validate_non_empty_string(value, field_name)
        except ValidationError as e:
            print(f"❌ {e}")
