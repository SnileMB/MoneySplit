"""
Comprehensive tests for tax comparison module.

Tests tax scenario comparison, optimization analysis, and recommendation generation.
"""
import pytest
from Logic.tax_comparison import (
    calculate_all_tax_scenarios,
    get_tax_optimization_summary,
    DIVIDEND_TAX_RATES,
)


class TestTaxScenarioCalculation:
    """Test tax scenario calculation."""

    def test_calculate_all_tax_scenarios_basic(self):
        """Test basic tax scenario calculation."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        assert isinstance(result, dict)
        assert "individual" in result
        assert "business_salary" in result
        assert "business_dividend" in result
        assert "business_reinvest" in result
        assert "recommendation" in result
        assert "all_scenarios_sorted" in result

    def test_individual_scenario_structure(self):
        """Test individual scenario has correct structure."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        individual = result["individual"]

        assert individual["type"] == "Individual"
        assert "gross_income" in individual
        assert "tax_paid" in individual
        assert "take_home_per_person" in individual
        assert "take_home_total" in individual
        assert "effective_rate" in individual
        assert "tax_breakdown" in individual

    def test_business_scenarios_structure(self):
        """Test business scenarios have correct structure."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")

        for scenario_key in ["business_salary", "business_dividend", "business_reinvest"]:
            scenario = result[scenario_key]
            assert "type" in scenario
            assert "description" in scenario
            assert "gross_income" in scenario
            assert "total_tax" in scenario
            assert "take_home_total" in scenario
            assert "effective_rate" in scenario

    def test_recommendation_structure(self):
        """Test recommendation has correct structure."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        rec = result["recommendation"]

        assert "choice" in rec
        assert "reason" in rec
        assert "savings" in rec

    def test_single_person_scenario(self):
        """Test scenario with single person."""
        result = calculate_all_tax_scenarios(50000, 5000, 1, "US")
        assert result["individual"]["gross_income"] == 45000

    def test_multiple_people_scenario(self):
        """Test scenario with multiple people."""
        result = calculate_all_tax_scenarios(100000, 10000, 5, "US")
        individual = result["individual"]

        # Income is split among people
        expected_per_person = (100000 - 10000) / 5
        assert individual["gross_income"] == expected_per_person

    def test_zero_costs_scenario(self):
        """Test scenario with zero costs."""
        result = calculate_all_tax_scenarios(100000, 0, 2, "US")
        assert result["individual"]["gross_income"] == 50000

    def test_high_costs_scenario(self):
        """Test scenario with very high costs."""
        result = calculate_all_tax_scenarios(100000, 90000, 2, "US")
        assert result["individual"]["gross_income"] == 5000

    def test_very_small_revenue(self):
        """Test scenario with very small revenue."""
        result = calculate_all_tax_scenarios(1000, 100, 1, "US")
        assert isinstance(result, dict)
        assert result["individual"]["gross_income"] == 900

    def test_very_large_revenue(self):
        """Test scenario with very large revenue."""
        result = calculate_all_tax_scenarios(10000000, 1000000, 5, "US")
        assert isinstance(result, dict)
        assert result["individual"]["gross_income"] == 1800000

    def test_zero_people_handling(self):
        """Test scenario with zero people (edge case)."""
        result = calculate_all_tax_scenarios(100000, 10000, 0, "US")
        assert result["individual"]["gross_income"] == 0
        assert result["individual"]["take_home_per_person"] == 0

    def test_different_countries(self):
        """Test scenarios with different countries."""
        for country in ["US", "Spain"]:
            result = calculate_all_tax_scenarios(100000, 10000, 2, country)
            assert result["individual"]["type"] == "Individual"

    def test_take_home_calculations_individual(self):
        """Test take-home calculations for individual."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        individual = result["individual"]

        # Verify take_home = gross - tax
        expected_per_person = individual["gross_income"] - individual["tax_paid"]
        assert individual["take_home_per_person"] == pytest.approx(expected_per_person)

    def test_take_home_calculations_business(self):
        """Test take-home calculations for business scenarios."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")

        for scenario_key in ["business_salary", "business_dividend"]:
            scenario = result[scenario_key]
            assert scenario["take_home_total"] >= 0

    def test_reinvest_scenario_no_personal_tax(self):
        """Test reinvest scenario has no personal tax."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        reinvest = result["business_reinvest"]

        assert reinvest["take_home_per_person"] == 0
        assert reinvest["take_home_total"] == 0
        assert "company_retained" in reinvest

    def test_scenarios_sorted_by_take_home(self):
        """Test that scenarios are sorted by take-home amount."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        scenarios = result["all_scenarios_sorted"]

        # Should be sorted in descending order
        for i in range(len(scenarios) - 1):
            current_take_home = scenarios[i][1]["take_home_total"]
            next_take_home = scenarios[i + 1][1]["take_home_total"]
            assert current_take_home >= next_take_home

    def test_recommendation_is_best_scenario(self):
        """Test that recommendation matches best scenario."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        best_scenario = result["all_scenarios_sorted"][0][1]

        # Recommendation should have savings based on difference from worst
        worst_scenario = result["all_scenarios_sorted"][-1][1]
        expected_savings = best_scenario["take_home_total"] - worst_scenario["take_home_total"]

        assert result["recommendation"]["savings"] == pytest.approx(expected_savings)


class TestDividendTaxRates:
    """Test dividend tax rate constants."""

    def test_dividend_tax_rates_us(self):
        """Test US dividend tax rate."""
        assert DIVIDEND_TAX_RATES["US"] == 0.15

    def test_dividend_tax_rates_spain(self):
        """Test Spain dividend tax rate."""
        assert DIVIDEND_TAX_RATES["Spain"] == 0.19

    def test_dividend_rates_are_reasonable(self):
        """Test all dividend rates are between 0 and 1."""
        for country, rate in DIVIDEND_TAX_RATES.items():
            assert 0 <= rate <= 1


class TestBusinessDividendScenario:
    """Test business dividend scenario calculations."""

    def test_dividend_tax_calculation(self):
        """Test dividend tax is calculated correctly."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        dividend = result["business_dividend"]

        # Tax should be calculated on after-corporate-tax income
        expected_tax = dividend["after_corp_tax"] * 0.15
        assert dividend["dividend_tax"] == pytest.approx(expected_tax)

    def test_dividend_vs_salary_comparison(self):
        """Test dividend vs salary scenarios are different."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")

        salary_take_home = result["business_salary"]["take_home_total"]
        dividend_take_home = result["business_dividend"]["take_home_total"]

        # One should be higher than the other (not equal)
        assert salary_take_home != dividend_take_home

    def test_dividend_warning_present(self):
        """Test dividend scenario includes warning."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        dividend = result["business_dividend"]

        assert "description" in dividend
        assert dividend["description"] == "Corporation paying dividends to owners"


class TestTaxOptimizationSummary:
    """Test tax optimization summary functionality."""

    def test_get_optimization_summary_individual_optimal(self):
        """Test optimization summary when individual is optimal."""
        # Create scenario where individual is likely optimal
        result = get_tax_optimization_summary(50000, 5000, 1, "US", "Individual")

        assert isinstance(result, dict)
        assert "is_optimal" in result
        assert "message" in result
        assert "selected" in result
        assert "savings" in result

    def test_get_optimization_summary_business_optimal(self):
        """Test optimization summary when business is optimal."""
        result = get_tax_optimization_summary(500000, 50000, 1, "US", "Business")

        assert isinstance(result, dict)
        assert "is_optimal" in result
        assert "message" in result

    def test_optimization_summary_shows_savings_if_not_optimal(self):
        """Test savings are shown if selection is not optimal."""
        # Test with large revenue where business might be better
        result = get_tax_optimization_summary(1000000, 100000, 1, "US", "Individual")

        if not result["is_optimal"]:
            assert "optimal" in result
            assert result["savings"] > 0

    def test_optimization_summary_zero_savings_if_optimal(self):
        """Test zero savings if selection is optimal."""
        result = get_tax_optimization_summary(50000, 5000, 1, "US", "Individual")

        if result["is_optimal"]:
            assert result["savings"] == 0

    def test_optimization_summary_different_countries(self):
        """Test optimization summary with different countries."""
        for country in ["US", "Spain"]:
            result = get_tax_optimization_summary(100000, 10000, 2, country, "Individual")
            assert "is_optimal" in result

    def test_optimization_summary_single_person(self):
        """Test optimization summary with single person."""
        result = get_tax_optimization_summary(100000, 10000, 1, "US", "Individual")
        assert isinstance(result, dict)

    def test_optimization_summary_multiple_people(self):
        """Test optimization summary with multiple people."""
        result = get_tax_optimization_summary(100000, 10000, 5, "US", "Individual")
        assert isinstance(result, dict)

    def test_optimization_includes_selected_details(self):
        """Test that optimization summary includes selected scenario details."""
        result = get_tax_optimization_summary(100000, 10000, 2, "US", "Individual")

        selected = result["selected"]
        assert "type" in selected
        assert "take_home_total" in selected
        assert "effective_rate" in selected

    def test_optimization_handles_invalid_type(self):
        """Test optimization summary handles invalid tax type."""
        # Invalid type should default to individual
        result = get_tax_optimization_summary(100000, 10000, 2, "US", "InvalidType")

        assert isinstance(result, dict)
        assert "selected" in result


class TestEffectiveTaxRates:
    """Test effective tax rate calculations."""

    def test_individual_effective_rate_is_valid(self):
        """Test individual effective tax rate is between 0 and 100%."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        rate = result["individual"]["effective_rate"]

        assert 0 <= rate <= 100

    def test_business_effective_rates_are_valid(self):
        """Test business effective tax rates are between 0 and 100%."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")

        for scenario_key in ["business_salary", "business_dividend", "business_reinvest"]:
            rate = result[scenario_key]["effective_rate"]
            assert 0 <= rate <= 100

    def test_effective_rate_calculation_individual(self):
        """Test effective rate calculation for individual."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        individual = result["individual"]

        if individual["gross_income"] > 0:
            expected_rate = (individual["tax_paid"] / individual["gross_income"]) * 100
            assert individual["effective_rate"] == pytest.approx(expected_rate)

    def test_zero_income_effective_rate(self):
        """Test effective rate with zero income."""
        result = calculate_all_tax_scenarios(1000, 1000, 1, "US")
        individual = result["individual"]

        # With zero income, effective rate should be 0
        assert individual["effective_rate"] == 0


class TestTaxBreakdown:
    """Test tax breakdown information."""

    def test_individual_tax_breakdown_format(self):
        """Test individual tax breakdown format."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        breakdown = result["individual"]["tax_breakdown"]

        assert isinstance(breakdown, list)
        assert len(breakdown) > 0

        for item in breakdown:
            assert "label" in item
            assert "amount" in item

    def test_business_salary_tax_breakdown_includes_two_layers(self):
        """Test business salary breakdown includes corporate and personal tax."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        breakdown = result["business_salary"]["tax_breakdown"]

        # Should have corporate tax and personal tax
        assert len(breakdown) >= 2
        labels = [item["label"] for item in breakdown]
        assert any("Corporate" in label for label in labels)
        assert any("Personal" in label or "salary" in label for label in labels)

    def test_business_reinvest_breakdown_includes_note(self):
        """Test reinvest breakdown includes deferred tax note."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        breakdown = result["business_reinvest"]["tax_breakdown"]

        # Should indicate deferred tax
        assert any("Deferred" in str(item.get("note", "")) for item in breakdown)


class TestRecommendationLogic:
    """Test recommendation logic."""

    def test_recommendation_choice_is_valid_type(self):
        """Test recommendation choice is a valid scenario type."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        choice = result["recommendation"]["choice"]

        # Should be one of the scenario types
        valid_choices = [
            "Individual Tax",
            "Business Tax with Dividend Distribution",
            "Business Tax with Salary",
        ]
        assert choice in valid_choices

    def test_recommendation_savings_is_non_negative(self):
        """Test recommendation savings is non-negative."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        savings = result["recommendation"]["savings"]

        assert savings >= 0

    def test_recommendation_reason_includes_amounts(self):
        """Test recommendation reason includes financial amounts."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        reason = result["recommendation"]["reason"]

        # Should contain dollar signs or numbers
        assert "$" in reason or any(char.isdigit() for char in reason)

    def test_warning_present_for_double_taxation_scenarios(self):
        """Test warning is present for business scenarios."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        warning = result["recommendation"]["warning"]

        # Warning may be None for individual tax
        if warning is not None:
            assert "double taxation" in warning.lower() or "Double taxation" in warning


class TestEdgeCases:
    """Test edge cases in tax comparison."""

    def test_very_small_income(self):
        """Test with very small income."""
        result = calculate_all_tax_scenarios(100, 10, 1, "US")
        assert result["individual"]["gross_income"] == 90

    def test_very_large_income(self):
        """Test with very large income."""
        result = calculate_all_tax_scenarios(100000000, 10000000, 10, "US")
        assert isinstance(result, dict)

    def test_costs_equal_revenue(self):
        """Test when costs equal revenue (zero profit)."""
        result = calculate_all_tax_scenarios(100000, 100000, 2, "US")

        assert result["individual"]["gross_income"] == 0
        assert result["individual"]["take_home_per_person"] == 0

    def test_many_people_split(self):
        """Test income split among many people."""
        result = calculate_all_tax_scenarios(100000, 10000, 100, "US")
        individual = result["individual"]

        expected_per_person = (100000 - 10000) / 100
        assert individual["gross_income"] == expected_per_person

    def test_fractional_revenue_and_costs(self):
        """Test with fractional revenue and costs."""
        result = calculate_all_tax_scenarios(100000.50, 10000.25, 2, "US")
        assert isinstance(result, dict)
        assert result["individual"]["gross_income"] > 0


class TestCountryVariations:
    """Test behavior with different countries."""

    def test_us_dividend_rate_applied(self):
        """Test US dividend rate is applied correctly."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "US")
        dividend = result["business_dividend"]

        # Should use 15% dividend rate for US
        expected_rate = 0.15
        actual_rate = dividend["dividend_tax"] / dividend["after_corp_tax"] if dividend["after_corp_tax"] > 0 else 0
        assert actual_rate == pytest.approx(expected_rate)

    def test_spain_dividend_rate_applied(self):
        """Test Spain dividend rate is applied correctly."""
        result = calculate_all_tax_scenarios(100000, 10000, 2, "Spain")
        dividend = result["business_dividend"]

        # Should use 19% dividend rate for Spain
        expected_rate = 0.19
        actual_rate = dividend["dividend_tax"] / dividend["after_corp_tax"] if dividend["after_corp_tax"] > 0 else 0
        assert actual_rate == pytest.approx(expected_rate)

    def test_unsupported_country_raises_error(self):
        """Test unsupported country raises error."""
        # Unsupported country should raise error since no tax brackets exist
        with pytest.raises(ValueError):
            calculate_all_tax_scenarios(100000, 10000, 2, "UnsupportedCountry")
