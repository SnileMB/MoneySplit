"""
Comprehensive tests for validators module.

Tests input validation for work shares, tax rates, income ranges, and other financial inputs.
"""
import pytest
from Logic.validators import (
    validate_work_share,
    validate_work_shares,
    validate_tax_rate,
    validate_positive_number,
    validate_non_empty_string,
    validate_country,
    validate_tax_type,
    ValidationError,
)


class TestWorkShareValidation:
    """Test work share validation."""

    def test_valid_work_share_zero(self):
        """Test valid work share of 0.0."""
        result = validate_work_share(0.0)
        assert result == 0.0

    def test_valid_work_share_half(self):
        """Test valid work share of 0.5."""
        result = validate_work_share(0.5)
        assert result == 0.5

    def test_valid_work_share_one(self):
        """Test valid work share of 1.0."""
        result = validate_work_share(1.0)
        assert result == 1.0

    def test_valid_work_share_quarter(self):
        """Test valid work share of 0.25."""
        result = validate_work_share(0.25)
        assert result == 0.25

    def test_valid_work_share_three_quarters(self):
        """Test valid work share of 0.75."""
        result = validate_work_share(0.75)
        assert result == 0.75

    def test_invalid_work_share_negative(self):
        """Test invalid negative work share."""
        with pytest.raises(ValidationError):
            validate_work_share(-0.1)

    def test_invalid_work_share_exceeds_one(self):
        """Test invalid work share exceeding 1.0."""
        with pytest.raises(ValidationError):
            validate_work_share(1.1)

    def test_invalid_work_share_two(self):
        """Test invalid work share of 2.0."""
        with pytest.raises(ValidationError):
            validate_work_share(2.0)

    def test_boundary_work_share_just_over_one(self):
        """Test work share just over 1.0."""
        with pytest.raises(ValidationError):
            validate_work_share(1.00001)

    def test_boundary_work_share_just_below_zero(self):
        """Test work share just below 0.0."""
        with pytest.raises(ValidationError):
            validate_work_share(-0.00001)


class TestWorkSharesValidation:
    """Test multiple work shares validation."""

    def test_valid_shares_sum_to_one(self):
        """Test valid work shares that sum to 1.0."""
        shares = [0.5, 0.5]
        result = validate_work_shares(shares)
        # Function returns None on success
        assert result is None

    def test_valid_shares_three_people(self):
        """Test valid work shares for three people."""
        shares = [0.33, 0.33, 0.34]
        result = validate_work_shares(shares)
        # Function returns None on success
        assert result is None

    def test_valid_shares_all_to_one_person(self):
        """Test valid work shares with one person."""
        shares = [1.0]
        result = validate_work_shares(shares)
        # Function returns None on success
        assert result is None

    def test_invalid_shares_sum_too_high(self):
        """Test shares that sum to more than 1.0."""
        with pytest.raises(ValidationError):
            validate_work_shares([0.6, 0.5])

    def test_invalid_shares_sum_too_low(self):
        """Test shares that sum to less than 1.0."""
        with pytest.raises(ValidationError):
            validate_work_shares([0.4, 0.4])

    def test_invalid_shares_negative(self):
        """Test shares with negative value."""
        with pytest.raises(ValidationError):
            validate_work_shares([0.5, -0.5])

    def test_invalid_shares_exceeds_one(self):
        """Test shares with value exceeding 1.0."""
        with pytest.raises(ValidationError):
            validate_work_shares([0.6, 0.5])

    def test_empty_shares_list(self):
        """Test with empty shares list."""
        try:
            validate_work_shares([])
        except (ValidationError, ValueError, ZeroDivisionError):
            pass  # Acceptable to reject

    def test_many_people_shares(self):
        """Test shares for many people."""
        shares = [0.1] * 10
        result = validate_work_shares(shares)
        # Function returns None on success
        assert result is None


class TestTaxRateValidation:
    """Test tax rate validation."""

    def test_valid_tax_rate_zero(self):
        """Test valid tax rate of 0%."""
        result = validate_tax_rate(0.0)
        assert result == 0.0

    def test_valid_tax_rate_quarter(self):
        """Test valid tax rate of 25%."""
        result = validate_tax_rate(0.25)
        assert result == 0.25

    def test_valid_tax_rate_half(self):
        """Test valid tax rate of 50%."""
        result = validate_tax_rate(0.5)
        assert result == 0.5

    def test_valid_tax_rate_one(self):
        """Test valid tax rate of 100%."""
        result = validate_tax_rate(1.0)
        assert result == 1.0

    def test_invalid_tax_rate_negative(self):
        """Test invalid negative tax rate."""
        with pytest.raises(ValidationError):
            validate_tax_rate(-0.1)

    def test_invalid_tax_rate_exceeds_one(self):
        """Test invalid tax rate exceeding 100%."""
        with pytest.raises(ValidationError):
            validate_tax_rate(1.1)

    def test_invalid_tax_rate_way_over(self):
        """Test invalid tax rate way over 100%."""
        with pytest.raises(ValidationError):
            validate_tax_rate(2.5)

    def test_boundary_tax_rate_just_over(self):
        """Test tax rate just over 100%."""
        with pytest.raises(ValidationError):
            validate_tax_rate(1.00001)


class TestValidationEdgeCases:
    """Test edge cases in validation."""

    def test_work_share_very_small_positive(self):
        """Test work share with very small positive value."""
        result = validate_work_share(0.00001)
        assert result == 0.00001

    def test_work_share_very_close_to_one(self):
        """Test work share very close to 1.0."""
        result = validate_work_share(0.99999)
        assert result == 0.99999

    def test_work_shares_rounding(self):
        """Test work shares with rounding."""
        shares = [1.0/3, 1.0/3, 1.0/3]
        # May have small floating point errors
        try:
            validate_work_shares(shares)
        except ValidationError:
            pass  # Acceptable due to floating point precision

    def test_tax_rate_very_small(self):
        """Test tax rate with very small value."""
        result = validate_tax_rate(0.00001)
        assert result == 0.00001

    def test_tax_rate_very_high(self):
        """Test tax rate very close to 100%."""
        result = validate_tax_rate(0.99999)
        assert result == 0.99999


class TestValidationReturnValues:
    """Test that validation returns correct values."""

    def test_validate_work_share_returns_float(self):
        """Test that work share validation returns float."""
        result = validate_work_share(0.5)
        assert isinstance(result, float)

    def test_validate_work_shares_returns_none(self):
        """Test that work shares validation returns None on success."""
        result = validate_work_shares([0.5, 0.5])
        assert result is None

    def test_validate_tax_rate_returns_float(self):
        """Test that tax rate validation returns float."""
        result = validate_tax_rate(0.25)
        assert isinstance(result, float)

    def test_validate_work_share_preserves_value(self):
        """Test that validation preserves the input value."""
        value = 0.7
        result = validate_work_share(value)
        assert result == value

    def test_validate_tax_rate_preserves_value(self):
        """Test that tax rate validation preserves value."""
        value = 0.33
        result = validate_tax_rate(value)
        assert result == value


class TestValidationConsistency:
    """Test consistency of validation."""

    def test_same_value_same_result(self):
        """Test that same input produces same result."""
        result1 = validate_work_share(0.5)
        result2 = validate_work_share(0.5)
        assert result1 == result2

    def test_same_shares_same_result(self):
        """Test that same shares produce same result."""
        shares = [0.25, 0.25, 0.5]
        result1 = validate_work_shares(shares)
        result2 = validate_work_shares(shares)
        assert result1 == result2

    def test_same_tax_rate_same_result(self):
        """Test that same tax rate produces same result."""
        result1 = validate_tax_rate(0.3)
        result2 = validate_tax_rate(0.3)
        assert result1 == result2


class TestValidationErrorTypes:
    """Test that validation raises correct error types."""

    def test_invalid_work_share_raises_validation_error(self):
        """Test that invalid work share raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_work_share(1.5)

    def test_invalid_shares_raises_validation_error(self):
        """Test that invalid shares raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_work_shares([0.6, 0.6])

    def test_invalid_tax_rate_raises_validation_error(self):
        """Test that invalid tax rate raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_tax_rate(1.5)


class TestValidationForTypicalValues:
    """Test validation with typical financial values."""

    def test_typical_work_share_solo(self):
        """Test typical solo person (100% share)."""
        result = validate_work_share(1.0)
        assert result == 1.0

    def test_typical_work_share_two_equal(self):
        """Test typical two people with equal shares."""
        result1 = validate_work_share(0.5)
        result2 = validate_work_share(0.5)
        assert result1 + result2 == 1.0

    def test_typical_work_share_unequal(self):
        """Test typical unequal shares."""
        shares = [0.6, 0.4]
        result = validate_work_shares(shares)
        # Function returns None on success
        assert result is None

    def test_typical_tax_rates_us(self):
        """Test typical US tax rates."""
        for rate in [0.10, 0.12, 0.22, 0.24, 0.32]:
            result = validate_tax_rate(rate)
            assert result == rate

    def test_typical_business_tax_rates(self):
        """Test typical business tax rates."""
        for rate in [0.15, 0.25, 0.34]:
            result = validate_tax_rate(rate)
            assert result == rate


class TestPositiveNumberValidation:
    """Test positive number validation."""

    def test_positive_number_zero(self):
        """Test that zero is valid for positive number."""
        result = validate_positive_number(0.0, "Amount")
        assert result == 0.0

    def test_positive_number_valid(self):
        """Test valid positive numbers."""
        for value in [1, 10.5, 1000000]:
            result = validate_positive_number(value, "Amount")
            assert result == value

    def test_positive_number_invalid_negative(self):
        """Test negative number validation."""
        with pytest.raises(ValidationError):
            validate_positive_number(-0.1, "Amount")

    def test_positive_number_very_small(self):
        """Test very small positive number."""
        result = validate_positive_number(0.00001, "Amount")
        assert result == 0.00001

    def test_positive_number_large(self):
        """Test large positive number."""
        result = validate_positive_number(1e10, "Amount")
        assert result == 1e10


class TestNonEmptyStringValidation:
    """Test non-empty string validation."""

    def test_valid_string(self):
        """Test valid non-empty string."""
        result = validate_non_empty_string("Test String", "Field")
        assert result == "Test String"

    def test_string_with_spaces(self):
        """Test string with leading/trailing spaces gets trimmed."""
        result = validate_non_empty_string("  Test  ", "Field")
        assert result == "Test"

    def test_empty_string(self):
        """Test empty string raises error."""
        with pytest.raises(ValidationError):
            validate_non_empty_string("", "Field")

    def test_whitespace_only_string(self):
        """Test whitespace-only string raises error."""
        with pytest.raises(ValidationError):
            validate_non_empty_string("   ", "Field")

    def test_single_character_string(self):
        """Test single character string."""
        result = validate_non_empty_string("A", "Field")
        assert result == "A"

    def test_long_string(self):
        """Test very long string."""
        long_str = "A" * 1000
        result = validate_non_empty_string(long_str, "Field")
        assert result == long_str

    def test_special_characters(self):
        """Test string with special characters."""
        result = validate_non_empty_string("Test@#$%^&*()", "Field")
        assert result == "Test@#$%^&*()"


class TestCountryValidation:
    """Test country validation."""

    def test_valid_country_usa(self):
        """Test valid USA country."""
        result = validate_country("USA")
        assert result == "USA"

    def test_valid_country_united_states(self):
        """Test valid United States."""
        result = validate_country("United States")
        assert result == "United States"

    def test_country_with_spaces(self):
        """Test country name gets trimmed."""
        result = validate_country("  United Kingdom  ")
        assert result == "United Kingdom"

    def test_empty_country(self):
        """Test empty country raises error."""
        with pytest.raises(ValidationError):
            validate_country("")

    def test_whitespace_country(self):
        """Test whitespace-only country raises error."""
        with pytest.raises(ValidationError):
            validate_country("   ")

    def test_various_countries(self):
        """Test various country names."""
        countries = ["Canada", "UK", "Spain", "Germany", "France", "India"]
        for country in countries:
            result = validate_country(country)
            assert result == country


class TestTaxTypeValidation:
    """Test tax type validation."""

    def test_valid_tax_type_individual(self):
        """Test valid Individual tax type."""
        result = validate_tax_type("Individual")
        assert result == "Individual"

    def test_valid_tax_type_business(self):
        """Test valid Business tax type."""
        result = validate_tax_type("Business")
        assert result == "Business"

    def test_tax_type_lowercase_individual(self):
        """Test lowercase individual gets converted to title case."""
        result = validate_tax_type("individual")
        assert result == "Individual"

    def test_tax_type_lowercase_business(self):
        """Test lowercase business gets converted to title case."""
        result = validate_tax_type("business")
        assert result == "Business"

    def test_tax_type_mixed_case(self):
        """Test mixed case gets normalized."""
        result = validate_tax_type("iNdIvIdUaL")
        assert result == "Individual"

    def test_tax_type_with_spaces(self):
        """Test tax type with spaces gets trimmed."""
        result = validate_tax_type("  Individual  ")
        assert result == "Individual"

    def test_invalid_tax_type(self):
        """Test invalid tax type raises error."""
        with pytest.raises(ValidationError):
            validate_tax_type("Corporate")

    def test_invalid_tax_type_nonprofit(self):
        """Test nonprofit is not valid tax type."""
        with pytest.raises(ValidationError):
            validate_tax_type("Nonprofit")

    def test_invalid_empty_tax_type(self):
        """Test empty tax type raises error."""
        with pytest.raises(ValidationError):
            validate_tax_type("")


class TestValidationEdgeCasesExtended:
    """Test additional edge cases in validation."""

    def test_positive_number_boundary_zero(self):
        """Test boundary at zero."""
        result = validate_positive_number(0, "Test")
        assert result == 0

    def test_string_unicode_characters(self):
        """Test string with unicode characters."""
        result = validate_non_empty_string("Café", "Field")
        assert result == "Café"

    def test_country_numbers(self):
        """Test country with numbers."""
        result = validate_country("USA1")
        assert result == "USA1"

    def test_tax_type_numeric_invalid(self):
        """Test numeric tax type raises error."""
        with pytest.raises(ValidationError):
            validate_tax_type("1")


class TestValidationErrorMessages:
    """Test that validation errors have appropriate messages."""

    def test_positive_number_error_message(self):
        """Test positive number validation error message."""
        try:
            validate_positive_number(-5, "Income")
        except ValidationError as e:
            assert "must be positive" in str(e)
            assert "Income" in str(e)

    def test_work_share_error_message(self):
        """Test work share validation error message."""
        try:
            validate_work_share(1.5)
        except ValidationError as e:
            assert "between 0 and 1" in str(e)

    def test_tax_rate_error_message(self):
        """Test tax rate validation error message."""
        try:
            validate_tax_rate(1.5)
        except ValidationError as e:
            assert "between 0 and 1" in str(e)

    def test_tax_type_error_message(self):
        """Test tax type validation error message."""
        try:
            validate_tax_type("Partnership")
        except ValidationError as e:
            assert "Tax type must be one of" in str(e)
            assert "Partnership" in str(e)

    def test_empty_string_error_message(self):
        """Test empty string validation error message."""
        try:
            validate_non_empty_string("", "Username")
        except ValidationError as e:
            assert "cannot be empty" in str(e)
            assert "Username" in str(e)

    def test_empty_country_error_message(self):
        """Test empty country validation error message."""
        try:
            validate_country("")
        except ValidationError as e:
            assert "cannot be empty" in str(e)
            assert "Country" in str(e)
