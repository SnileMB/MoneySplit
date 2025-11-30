"""Unit tests for backend business logic."""

import pytest
from Logic.tax_calculator import (
    calculate_tax,
    calculate_tax_from_db,
    split_work_shares,
    calculate_profit,
)
from Logic.validators import (
    validate_positive_number,
    validate_work_shares,
    validate_work_share,
    validate_non_empty_string,
    validate_country,
    validate_tax_type,
    validate_tax_rate,
    ValidationError,
)


class TestTaxCalculations:
    """Test tax calculation logic."""

    def test_calculate_progressive_tax(self):
        """Test progressive tax calculation with mock brackets."""
        # Mock tax brackets: 10% up to 10k, 20% above 10k
        from unittest.mock import patch

        mock_brackets = [(10000, 0.10), (50000, 0.20)]

        with patch(
            "Logic.tax_calculator.setup.get_tax_brackets", return_value=mock_brackets
        ):
            # Income of 15000: (10000 * 0.10) + (5000 * 0.20) = 1000 + 1000 = 2000
            tax = calculate_tax_from_db(15000, "US", "Individual")
            assert tax == 2000.0

    def test_calculate_tax_single_bracket(self):
        """Test tax calculation within single bracket."""
        from unittest.mock import patch

        mock_brackets = [(10000, 0.10), (50000, 0.20)]

        with patch(
            "Logic.tax_calculator.setup.get_tax_brackets", return_value=mock_brackets
        ):
            # Income of 5000: entirely in first bracket
            tax = calculate_tax_from_db(5000, "US", "Individual")
            assert tax == 500.0  # 5000 * 0.10

    def test_calculate_tax_zero_income(self):
        """Test tax calculation for zero income."""
        from unittest.mock import patch

        mock_brackets = [(10000, 0.10)]

        with patch(
            "Logic.tax_calculator.setup.get_tax_brackets", return_value=mock_brackets
        ):
            tax = calculate_tax_from_db(0, "US", "Individual")
            assert tax == 0.0

    def test_calculate_tax_direct(self):
        """Test direct tax calculation without DB."""
        brackets = [(10000, 0.10), (50000, 0.20)]

        # Income of 15000: (10000 * 0.10) + (5000 * 0.20) = 1000 + 1000 = 2000
        tax = calculate_tax(15000, brackets)
        assert tax == 2000.0

        # Income of 5000: entirely in first bracket
        tax = calculate_tax(5000, brackets)
        assert tax == 500.0


class TestWorkShareDistribution:
    """Test work share distribution logic."""

    def test_equal_split_two_people(self):
        """Test equal work share split between two people."""
        profit = 10000
        work_shares = [0.5, 0.5]

        distribution = split_work_shares(profit, work_shares)

        assert len(distribution) == 2
        assert distribution[0] == 5000.0
        assert distribution[1] == 5000.0

    def test_unequal_split_three_people(self):
        """Test unequal work share split."""
        profit = 10000
        work_shares = [0.5, 0.3, 0.2]

        distribution = split_work_shares(profit, work_shares)

        assert len(distribution) == 3
        assert distribution[0] == 5000.0
        assert distribution[1] == 3000.0
        assert distribution[2] == 2000.0


class TestValidators:
    """Test input validation functions."""

    def test_validate_positive_number_valid(self):
        """Test positive number validation with valid value."""
        result = validate_positive_number(10000, "Revenue")
        assert result == 10000

    def test_validate_positive_number_zero(self):
        """Test positive number validation with zero."""
        result = validate_positive_number(0, "Revenue")
        assert result == 0

    def test_validate_positive_number_negative(self):
        """Test positive number validation with negative value."""
        with pytest.raises(ValidationError):
            validate_positive_number(-5000, "Revenue")

    def test_validate_work_shares_valid(self):
        """Test work shares validation with valid shares."""
        # Should not raise exception
        validate_work_shares([0.5, 0.5])
        validate_work_shares([0.6, 0.4])
        validate_work_shares([0.33, 0.33, 0.34])

    def test_validate_work_shares_invalid_sum(self):
        """Test work shares validation with invalid sum."""
        with pytest.raises(ValidationError):
            validate_work_shares([0.6, 0.6])  # Sums to 1.2

        with pytest.raises(ValidationError):
            validate_work_shares([0.3, 0.3])  # Sums to 0.6

    def test_validate_work_share_valid(self):
        """Test single work share validation."""
        assert validate_work_share(0.5) == 0.5
        assert validate_work_share(0.0) == 0.0
        assert validate_work_share(1.0) == 1.0

    def test_validate_work_share_invalid(self):
        """Test single work share validation with invalid values."""
        with pytest.raises(ValidationError):
            validate_work_share(-0.1)

        with pytest.raises(ValidationError):
            validate_work_share(1.5)

    def test_validate_non_empty_string_valid(self):
        """Test non-empty string validation."""
        assert validate_non_empty_string("Alice", "Name") == "Alice"
        assert validate_non_empty_string("  Bob  ", "Name") == "Bob"

    def test_validate_non_empty_string_invalid(self):
        """Test non-empty string validation with empty string."""
        with pytest.raises(ValidationError):
            validate_non_empty_string("", "Name")

        with pytest.raises(ValidationError):
            validate_non_empty_string("   ", "Name")

    def test_validate_country_valid(self):
        """Test country validation."""
        assert validate_country("US") == "US"
        assert validate_country("Spain") == "Spain"

    def test_validate_country_invalid(self):
        """Test country validation with empty string."""
        with pytest.raises(ValidationError):
            validate_country("")

    def test_validate_tax_type_valid(self):
        """Test tax type validation."""
        assert validate_tax_type("Individual") == "Individual"
        assert validate_tax_type("Business") == "Business"
        assert validate_tax_type("individual") == "Individual"  # Case insensitive

    def test_validate_tax_type_invalid(self):
        """Test tax type validation with invalid type."""
        with pytest.raises(ValidationError):
            validate_tax_type("Corporate")

    def test_validate_tax_rate_valid(self):
        """Test tax rate validation."""
        assert validate_tax_rate(0.10) == 0.10
        assert validate_tax_rate(0.0) == 0.0
        assert validate_tax_rate(1.0) == 1.0

    def test_validate_tax_rate_invalid(self):
        """Test tax rate validation with invalid values."""
        with pytest.raises(ValidationError):
            validate_tax_rate(-0.1)

        with pytest.raises(ValidationError):
            validate_tax_rate(1.5)


class TestProfitCalculations:
    """Test profit calculation logic."""

    def test_profit_calculation_basic(self):
        """Test basic profit calculation."""
        revenue = 10000
        costs = [1000, 500, 300]

        profit = calculate_profit(revenue, costs)
        assert profit == 8200

    def test_profit_calculation_no_profit(self):
        """Test profit calculation with zero profit."""
        revenue = 5000
        costs = [3000, 2000]

        profit = calculate_profit(revenue, costs)
        assert profit == 0

    def test_profit_calculation_loss(self):
        """Test profit calculation with negative profit (loss)."""
        revenue = 5000
        costs = [4000, 2000]

        profit = calculate_profit(revenue, costs)
        assert profit == -1000

    def test_profit_calculation_no_costs(self):
        """Test profit calculation with no costs."""
        revenue = 10000
        costs = []

        profit = calculate_profit(revenue, costs)
        assert profit == 10000
