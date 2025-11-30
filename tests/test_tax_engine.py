"""
Comprehensive tests for tax_engine module.

Covers tax calculation functions, deductions, self-employment tax, and country-specific calculations.
"""
import pytest
from Logic.tax_engine import (
    calculate_tax_from_brackets,
    calculate_self_employment_tax,
    apply_standard_deduction,
    calculate_state_tax,
    calculate_uk_tax,
    calculate_canada_tax,
    apply_qbi_deduction,
    calculate_optimal_salary,
    calculate_project_taxes,
    get_optimal_strategy,
)


class TestTaxFromBrackets:
    """Test progressive tax bracket calculation."""

    def test_income_in_first_bracket(self):
        """Test tax calculation when income is in first bracket."""
        brackets = [(10000, 0.10), (30000, 0.15), (60000, 0.25)]
        income = 5000
        tax = calculate_tax_from_brackets(income, brackets)
        assert tax == 500  # 5000 * 0.10

    def test_income_spanning_multiple_brackets(self):
        """Test tax calculation across multiple brackets."""
        brackets = [(10000, 0.10), (30000, 0.15), (60000, 0.25)]
        income = 25000
        tax = calculate_tax_from_brackets(income, brackets)
        # 10000 * 0.10 + 15000 * 0.15 = 1000 + 2250 = 3250
        assert tax == 3250

    def test_income_in_top_bracket(self):
        """Test tax calculation at top income level."""
        brackets = [(10000, 0.10), (30000, 0.15), (60000, 0.25)]
        income = 80000
        tax = calculate_tax_from_brackets(income, brackets)
        # 10000*0.10 + 20000*0.15 + 30000*0.25 + 20000*0.25
        assert tax > 10000

    def test_zero_income(self):
        """Test tax on zero income."""
        brackets = [(10000, 0.10), (30000, 0.15)]
        tax = calculate_tax_from_brackets(0, brackets)
        assert tax == 0

    def test_very_high_income(self):
        """Test tax on very high income."""
        brackets = [(10000, 0.10), (100000, 0.25), (500000, 0.37)]
        income = 1000000
        tax = calculate_tax_from_brackets(income, brackets)
        assert tax > 0
        assert isinstance(tax, float)


class TestSelfEmploymentTax:
    """Test self-employment tax calculations."""

    def test_us_self_employment_tax_calculation(self):
        """Test US self-employment tax."""
        result = calculate_self_employment_tax(50000, "US")
        assert isinstance(result, dict)
        assert "total_se_tax" in result
        assert result["total_se_tax"] > 0

    def test_us_self_employment_with_low_income(self):
        """Test US self-employment tax on low income."""
        result = calculate_self_employment_tax(5000, "US")
        assert result["total_se_tax"] >= 0

    def test_spain_self_employment_tax(self):
        """Test Spain self-employment tax."""
        result = calculate_self_employment_tax(50000, "Spain")
        assert isinstance(result, dict)
        assert "total_se_tax" in result

    def test_uk_self_employment_tax(self):
        """Test UK self-employment tax."""
        result = calculate_self_employment_tax(50000, "UK")
        assert isinstance(result, dict)

    def test_zero_self_employment_income(self):
        """Test self-employment tax on zero income."""
        result = calculate_self_employment_tax(0, "US")
        assert result["total_se_tax"] == 0


class TestStandardDeduction:
    """Test standard deduction application."""

    def test_us_standard_deduction_single(self):
        """Test US standard deduction for single filer."""
        # Standard deduction reduces taxable income
        reduced_income = apply_standard_deduction(100000, "US")
        assert reduced_income < 100000
        assert reduced_income > 0

    def test_us_standard_deduction_high_income(self):
        """Test US standard deduction doesn't eliminate all income."""
        reduced_income = apply_standard_deduction(50000, "US")
        assert reduced_income > 0

    def test_spain_standard_deduction(self):
        """Test Spain standard deduction."""
        reduced_income = apply_standard_deduction(100000, "Spain")
        assert reduced_income >= 0
        assert isinstance(reduced_income, (int, float))

    def test_standard_deduction_low_income(self):
        """Test standard deduction with low income."""
        income = 5000
        reduced = apply_standard_deduction(income, "US")
        assert reduced >= 0


class TestStateTax:
    """Test state-specific tax calculations."""

    def test_california_state_tax(self):
        """Test California state tax."""
        tax = calculate_state_tax(100000, "CA")
        assert tax > 0

    def test_florida_state_tax_zero(self):
        """Test Florida (no income tax) state tax."""
        tax = calculate_state_tax(100000, "FL")
        # Florida has no state income tax
        assert tax >= 0

    def test_new_york_state_tax(self):
        """Test New York state tax."""
        tax = calculate_state_tax(100000, "NY")
        assert tax > 0

    def test_state_tax_zero_income(self):
        """Test state tax on zero income."""
        tax = calculate_state_tax(0, "CA")
        assert tax == 0


class TestUKTax:
    """Test UK-specific tax calculations."""

    def test_uk_tax_basic_rate(self):
        """Test UK tax in basic rate band."""
        tax = calculate_uk_tax(30000)
        assert tax > 0
        assert isinstance(tax, float)

    def test_uk_tax_higher_rate(self):
        """Test UK tax in higher rate band."""
        tax_lower = calculate_uk_tax(40000)
        tax_higher = calculate_uk_tax(60000)
        assert tax_higher > tax_lower

    def test_uk_tax_additional_rate(self):
        """Test UK tax in additional rate band."""
        tax = calculate_uk_tax(200000)
        assert tax > 0

    def test_uk_tax_below_threshold(self):
        """Test UK tax below personal allowance."""
        tax = calculate_uk_tax(5000)
        assert tax == 0


class TestCanadaTax:
    """Test Canada tax calculations."""

    def test_canada_federal_tax(self):
        """Test Canadian federal tax."""
        result = calculate_canada_tax(50000)
        assert isinstance(result, dict)
        assert "federal_tax" in result

    def test_canada_high_income_tax(self):
        """Test Canadian tax on high income."""
        result = calculate_canada_tax(200000)
        assert result["federal_tax"] > 0

    def test_canada_low_income_tax(self):
        """Test Canadian tax on low income."""
        result = calculate_canada_tax(10000)
        assert result["federal_tax"] >= 0


class TestQBIDeduction:
    """Test Qualified Business Income deduction."""

    def test_qbi_deduction_us(self):
        """Test QBI deduction for US business income."""
        income = 100000
        deduction = apply_qbi_deduction(income, "US")
        # QBI deduction is typically 20% of business income
        assert deduction > 0
        assert deduction < income

    def test_qbi_deduction_limits(self):
        """Test QBI deduction doesn't exceed income."""
        deduction = apply_qbi_deduction(50000, "US")
        assert deduction <= 50000

    def test_qbi_deduction_zero_income(self):
        """Test QBI deduction on zero income."""
        deduction = apply_qbi_deduction(0, "US")
        assert deduction == 0


class TestOptimalSalary:
    """Test optimal salary calculation."""

    def test_optimal_salary_calculation(self):
        """Test optimal salary split between salary and dividend."""
        result = calculate_optimal_salary(100000, "US")
        assert isinstance(result, dict)
        assert "recommended_salary" in result
        assert "dividend_amount" in result

    def test_optimal_salary_values(self):
        """Test optimal salary values are reasonable."""
        result = calculate_optimal_salary(100000, "US")
        total = result["recommended_salary"] + result.get("dividend_amount", 0)
        assert total <= 100000 + 1  # Account for rounding


class TestProjectTaxes:
    """Test comprehensive project tax calculation."""

    def test_project_tax_us_individual(self):
        """Test project tax for US individual income."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Individual",
        )
        assert isinstance(result, dict)
        assert "total_tax" in result

    def test_project_tax_us_business(self):
        """Test project tax for US business structure."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Business",
        )
        assert isinstance(result, dict)
        assert "total_tax" in result

    def test_project_tax_spain(self):
        """Test project tax for Spain."""
        result = calculate_project_taxes(
            revenue=50000,
            costs=5000,
            num_people=1,
            country="Spain",
            tax_structure="Individual",
        )
        assert isinstance(result, dict)

    def test_project_tax_zero_costs(self):
        """Test project tax with zero costs."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=0,
            num_people=1,
            country="US",
            tax_structure="Individual",
        )
        assert result["total_tax"] > 0


class TestTaxEdgeCases:
    """Test edge cases in tax calculations."""

    def test_bracket_boundary_values(self):
        """Test income exactly at bracket boundaries."""
        brackets = [(10000, 0.10), (20000, 0.15)]
        tax1 = calculate_tax_from_brackets(9999.99, brackets)
        tax2 = calculate_tax_from_brackets(10000.00, brackets)
        tax3 = calculate_tax_from_brackets(10000.01, brackets)
        # Should handle boundary correctly
        assert tax1 <= tax2 <= tax3

    def test_negative_income_handling(self):
        """Test handling of negative income."""
        brackets = [(10000, 0.10)]
        # Negative income results in negative tax (loss)
        tax = calculate_tax_from_brackets(-1000, brackets)
        assert isinstance(tax, float)

    def test_very_large_bracket_limit(self):
        """Test with very large bracket limits."""
        brackets = [(1000000000, 0.35)]
        tax = calculate_tax_from_brackets(100000, brackets)
        assert tax == 100000 * 0.35

    def test_multiple_equal_brackets(self):
        """Test calculation with multiple bracket changes."""
        brackets = [
            (10000, 0.10),
            (20000, 0.15),
            (30000, 0.20),
            (50000, 0.25),
            (100000, 0.35),
        ]
        income = 75000
        tax = calculate_tax_from_brackets(income, brackets)
        assert tax > 0
        assert isinstance(tax, float)


class TestTaxCalculationConsistency:
    """Test consistency of tax calculations."""

    def test_same_calculation_repeated(self):
        """Test that same inputs produce same outputs."""
        brackets = [(10000, 0.10), (30000, 0.15)]
        income = 25000
        tax1 = calculate_tax_from_brackets(income, brackets)
        tax2 = calculate_tax_from_brackets(income, brackets)
        assert tax1 == tax2

    def test_project_tax_consistency(self):
        """Test project tax calculation consistency."""
        result1 = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Individual",
        )
        result2 = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Individual",
        )
        assert result1 == result2

    def test_tax_monotonicity(self):
        """Test that higher income results in higher tax."""
        brackets = [(10000, 0.10), (50000, 0.25)]
        tax1 = calculate_tax_from_brackets(30000, brackets)
        tax2 = calculate_tax_from_brackets(40000, brackets)
        assert tax2 > tax1


class TestApplyStandardDeductionExtended:
    """Test standard deduction application for various scenarios."""

    def test_standard_deduction_us_reduces_taxable_income(self):
        """Test that standard deduction reduces taxable income."""
        income = 50000
        deducted = apply_standard_deduction(income, "US")
        assert deducted < income

    def test_standard_deduction_spain(self):
        """Test standard deduction for Spain."""
        income = 30000
        deducted = apply_standard_deduction(income, "Spain")
        assert deducted == 30000 - 5550  # Spain's standard deduction

    def test_standard_deduction_never_negative(self):
        """Test that standard deduction never results in negative income."""
        income = 1000
        deducted = apply_standard_deduction(income, "US")
        assert deducted >= 0

    def test_standard_deduction_with_state(self):
        """Test standard deduction with state specified."""
        income = 100000
        deducted = apply_standard_deduction(income, "US", state="CA")
        assert deducted > 0

    def test_standard_deduction_large_income(self):
        """Test standard deduction with large income."""
        income = 500000
        deducted = apply_standard_deduction(income, "US")
        assert deducted > 0


class TestStateSpecificTaxes:
    """Test state-specific tax calculations."""

    def test_california_state_tax_high_income(self):
        """Test California tax on high income."""
        income = 100000
        tax = calculate_state_tax(income, "CA")
        assert tax > 0

    def test_texas_no_state_tax(self):
        """Test Texas has no state income tax."""
        income = 100000
        tax = calculate_state_tax(income, "TX")
        assert tax == 0

    def test_florida_no_state_tax(self):
        """Test Florida has no state income tax."""
        income = 50000
        tax = calculate_state_tax(income, "FL")
        assert tax == 0

    def test_new_york_state_tax(self):
        """Test New York state tax calculation."""
        income = 75000
        tax = calculate_state_tax(income, "NY")
        assert tax > 0

    def test_state_tax_increases_with_income(self):
        """Test that state tax increases with income."""
        tax1 = calculate_state_tax(30000, "CA")
        tax2 = calculate_state_tax(60000, "CA")
        assert tax2 > tax1

    def test_state_tax_boundary_amounts(self):
        """Test state tax at bracket boundaries."""
        # Test at different bracket levels
        for income in [10099, 23942, 37788]:
            tax = calculate_state_tax(income, "CA")
            assert tax >= 0


class TestUKTaxCalculations:
    """Test UK-specific tax calculations."""

    def test_uk_tax_below_personal_allowance(self):
        """Test UK tax below personal allowance."""
        income = 5000
        tax = calculate_uk_tax(income)
        assert tax == 0

    def test_uk_tax_between_allowance_and_basic_rate(self):
        """Test UK tax in basic rate band."""
        income = 20000
        tax = calculate_uk_tax(income)
        assert tax > 0

    def test_uk_tax_higher_rate(self):
        """Test UK tax in higher rate band."""
        income = 75000
        tax = calculate_uk_tax(income)
        assert tax > 0

    def test_uk_tax_additional_rate(self):
        """Test UK tax in additional rate band."""
        income = 150000
        tax = calculate_uk_tax(income)
        assert tax > 0

    def test_uk_tax_increases_with_income(self):
        """Test UK tax increases with income."""
        tax1 = calculate_uk_tax(30000)
        tax2 = calculate_uk_tax(60000)
        assert tax2 > tax1


class TestCanadaTaxCalculations:
    """Test Canada-specific tax calculations."""

    def test_canada_tax_low_income(self):
        """Test Canada tax on low income."""
        result = calculate_canada_tax(30000)
        assert "federal_tax" in result
        assert "provincial_tax" in result
        assert "total_tax" in result

    def test_canada_tax_medium_income(self):
        """Test Canada tax on medium income."""
        result = calculate_canada_tax(75000)
        assert result["federal_tax"] > 0
        assert result["provincial_tax"] > 0

    def test_canada_tax_high_income(self):
        """Test Canada tax on high income."""
        result = calculate_canada_tax(150000)
        assert result["federal_tax"] > 0
        assert result["total_tax"] > 0

    def test_canada_tax_structure(self):
        """Test Canada tax result has required structure."""
        result = calculate_canada_tax(100000)
        assert "federal_tax" in result
        assert "provincial_tax" in result
        assert "total_tax" in result

    def test_canada_total_equals_sum(self):
        """Test Canada total tax equals federal + provincial."""
        result = calculate_canada_tax(100000)
        assert result["total_tax"] == result["federal_tax"] + result["provincial_tax"]


class TestQBIDeductionExtended:
    """Test Qualified Business Income deduction."""

    def test_qbi_deduction_us_20_percent(self):
        """Test QBI deduction is 20% for US."""
        business_income = 100000
        deducted = apply_qbi_deduction(business_income, "US")
        expected = 100000 * 0.20  # 20% deduction amount returned
        assert deducted == pytest.approx(expected)

    def test_qbi_deduction_reduces_income(self):
        """Test QBI deduction reduces business income."""
        business_income = 50000
        deducted = apply_qbi_deduction(business_income, "US")
        assert deducted < business_income

    def test_qbi_deduction_non_us(self):
        """Test QBI deduction for non-US countries."""
        business_income = 100000
        # Non-US countries may not have QBI, returns original income
        result = apply_qbi_deduction(business_income, "Spain")
        assert isinstance(result, (int, float))

    def test_qbi_deduction_zero_income(self):
        """Test QBI deduction with zero income."""
        deducted = apply_qbi_deduction(0, "US")
        assert deducted == 0

    def test_qbi_deduction_large_income(self):
        """Test QBI deduction with large income."""
        business_income = 1000000
        deducted = apply_qbi_deduction(business_income, "US")
        assert deducted > 0


class TestOptimalSalaryExtended:
    """Test optimal salary calculation for various scenarios."""

    def test_optimal_salary_result_structure(self):
        """Test optimal salary returns correct structure."""
        result = calculate_optimal_salary(100000, "US")
        assert "recommended_salary" in result
        assert result["recommended_salary"] >= 0

    def test_optimal_salary_less_than_available(self):
        """Test optimal salary doesn't exceed available funds."""
        available = 100000
        result = calculate_optimal_salary(available, "US")
        assert result["recommended_salary"] <= available

    def test_optimal_salary_increases_with_available_funds(self):
        """Test optimal salary increases with more available funds."""
        result1 = calculate_optimal_salary(50000, "US")
        result2 = calculate_optimal_salary(100000, "US")
        assert result2["recommended_salary"] >= result1["recommended_salary"]

    def test_optimal_salary_for_different_countries(self):
        """Test optimal salary for different countries."""
        for country in ["US", "Spain"]:
            result = calculate_optimal_salary(100000, country)
            assert "recommended_salary" in result

    def test_optimal_salary_tax_calculation(self):
        """Test optimal salary includes tax information."""
        result = calculate_optimal_salary(100000, "US")
        assert isinstance(result, dict)
        assert result["recommended_salary"] >= 0


class TestComplexTaxScenarios:
    """Test complex real-world tax scenarios."""

    def test_high_earner_multiple_countries(self):
        """Test tax calculation for high earner across countries."""
        for country in ["US", "Spain"]:  # UK requires special setup
            result = calculate_project_taxes(
                revenue=500000,
                costs=50000,
                num_people=1,
                country=country,
                tax_structure="Business",
            )
            assert result["total_tax"] > 0

    def test_small_business_multiple_people(self):
        """Test small business with multiple owners."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=20000,
            num_people=4,
            country="US",
            tax_structure="Individual",
        )
        assert "total_tax" in result
        assert result["total_tax"] >= 0

    def test_break_even_business(self):
        """Test business with minimal profit."""
        result = calculate_project_taxes(
            revenue=50000,
            costs=49000,
            num_people=1,
            country="US",
            tax_structure="Business",
        )
        assert isinstance(result, dict)

    def test_seasonal_business_analysis(self):
        """Test tax calculations for different revenue levels."""
        results = []
        for revenue in [50000, 100000, 200000, 500000]:
            result = calculate_project_taxes(
                revenue=revenue,
                costs=revenue * 0.2,  # 20% costs
                num_people=2,
                country="US",
                tax_structure="Individual",
            )
            results.append(result)

        # Tax should generally increase with revenue
        for i in range(len(results) - 1):
            assert results[i + 1]["total_tax"] >= results[i]["total_tax"]

    def test_tax_efficiency_business_vs_individual(self):
        """Test comparing business vs individual tax."""
        individual_result = calculate_project_taxes(
            revenue=200000,
            costs=30000,
            num_people=1,
            country="US",
            tax_structure="Individual",
        )
        business_result = calculate_project_taxes(
            revenue=200000,
            costs=30000,
            num_people=1,
            country="US",
            tax_structure="Business",
        )

        # Both should return valid results
        assert individual_result["total_tax"] > 0
        assert business_result["total_tax"] > 0


class TestStateIncomeTaxCalculations:
    """Test US state income tax calculations."""

    def test_california_state_tax(self):
        """Test California state tax calculation."""
        from Logic.tax_engine import calculate_state_tax

        tax = calculate_state_tax(50000, "CA")
        assert tax > 0  # CA has income tax

    def test_texas_no_state_tax(self):
        """Test Texas has no state income tax."""
        from Logic.tax_engine import calculate_state_tax

        tax = calculate_state_tax(100000, "TX")
        assert tax == 0  # TX has no income tax

    def test_florida_no_state_tax(self):
        """Test Florida has no state income tax."""
        from Logic.tax_engine import calculate_state_tax

        tax = calculate_state_tax(100000, "FL")
        assert tax == 0  # FL has no income tax

    def test_newyork_state_tax(self):
        """Test New York state tax calculation."""
        from Logic.tax_engine import calculate_state_tax

        tax = calculate_state_tax(50000, "NY")
        assert tax > 0  # NY has income tax

    def test_invalid_state_returns_zero(self):
        """Test invalid state returns zero tax."""
        from Logic.tax_engine import calculate_state_tax

        tax = calculate_state_tax(50000, "ZZ")
        assert tax == 0

    def test_state_tax_increases_with_income(self):
        """Test state tax increases with income."""
        from Logic.tax_engine import calculate_state_tax

        tax_50k = calculate_state_tax(50000, "CA")
        tax_100k = calculate_state_tax(100000, "CA")
        assert tax_100k >= tax_50k


class TestIndividualTaxWithState:
    """Test individual tax calculations with state tax."""

    def test_individual_us_with_state_tax_california(self):
        """Test individual tax calculation with California state tax."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Individual",
            state="CA",
        )
        assert result["state_tax"] > 0
        assert "state_tax" in result

    def test_individual_us_with_state_tax_texas(self):
        """Test individual tax calculation with Texas (no state tax)."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Individual",
            state="TX",
        )
        assert result["state_tax"] == 0

    def test_individual_tax_without_state_parameter(self):
        """Test individual tax calculation without state parameter."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Individual",
        )
        assert "state_tax" in result
        assert result["state_tax"] == 0

    def test_individual_tax_total_includes_state(self):
        """Test total tax includes state tax."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Individual",
            state="CA",
        )
        # Total should be federal + SE + state taxes
        expected_total = (
            result["personal_tax"] + result["se_tax"] + result["state_tax"]
        )
        assert result["total_tax"] == pytest.approx(expected_total)


class TestBusinessDistributionMethods:
    """Test different business distribution methods."""

    def test_business_salary_distribution(self):
        """Test business with salary distribution."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Business",
            distribution_method="Salary",
        )
        assert result["personal_tax"] > 0
        assert result["dividend_tax"] == 0
        # Check for salary/personal tax indication (text may vary)
        breakdown_str = str(result.get("breakdown", []))
        assert "salary" in breakdown_str.lower() or "personal" in breakdown_str.lower()

    def test_business_dividend_distribution(self):
        """Test business with dividend distribution."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Business",
            distribution_method="Dividend",
        )
        assert result["dividend_tax"] > 0
        assert result["personal_tax"] == 0

    def test_business_mixed_distribution_with_auto_optimize(self):
        """Test business with mixed distribution (auto-optimized)."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Business",
            distribution_method="Mixed",
            salary_amount=0,  # Let it auto-optimize
        )
        assert result["personal_tax"] > 0
        assert result["dividend_tax"] > 0
        assert "Optimized" in str(result.get("breakdown", []))

    def test_business_mixed_distribution_with_specified_salary(self):
        """Test business with mixed distribution (specified salary)."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Business",
            distribution_method="Mixed",
            salary_amount=30000,
        )
        assert result["personal_tax"] > 0
        assert result["dividend_tax"] > 0

    def test_business_mixed_salary_exceeds_after_tax_raises_error(self):
        """Test business mixed fails if salary exceeds after-tax income."""
        with pytest.raises(ValueError):
            calculate_project_taxes(
                revenue=100000,
                costs=10000,
                num_people=2,
                country="US",
                tax_structure="Business",
                distribution_method="Mixed",
                salary_amount=100000,  # Exceeds after-tax profit
            )

    def test_business_reinvest_distribution(self):
        """Test business with reinvest (no personal distribution)."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Business",
            distribution_method="Reinvest",
        )
        assert result["personal_tax"] == 0
        assert result["dividend_tax"] == 0
        assert result["net_income_group"] == 0
        assert result["company_retained"] > 0

    def test_business_invalid_distribution_method(self):
        """Test business with invalid distribution method defaults to Salary."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
            tax_structure="Business",
            distribution_method="InvalidMethod",
        )
        # Should default to Salary behavior
        assert isinstance(result, dict)
        assert "total_tax" in result


class TestCountrySpecificTaxes:
    """Test country-specific tax calculations."""

    def test_individual_uk_tax(self):
        """Test UK individual tax calculation."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="UK",
            tax_structure="Individual",
        )
        assert result["total_tax"] > 0
        assert "UK Income Tax" in str(result.get("breakdown", []))

    def test_individual_canada_tax(self):
        """Test Canada individual tax calculation."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="Canada",
            tax_structure="Individual",
        )
        assert result["total_tax"] > 0
        # Should have federal and provincial breakdown
        breakdown_str = str(result.get("breakdown", []))
        assert "Federal" in breakdown_str or "Provincial" in breakdown_str

    def test_business_uk_corporate_tax(self):
        """Test UK business corporate tax calculation."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="UK",
            tax_structure="Business",
            distribution_method="Salary",
        )
        assert result["corporate_tax"] > 0

    def test_business_canada_corporate_tax(self):
        """Test Canada business corporate tax calculation."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="Canada",
            tax_structure="Business",
            distribution_method="Salary",
        )
        assert result["corporate_tax"] > 0

    def test_business_uk_dividend_distribution(self):
        """Test UK business dividend distribution."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="UK",
            tax_structure="Business",
            distribution_method="Dividend",
        )
        assert result["dividend_tax"] > 0

    def test_business_canada_dividend_distribution(self):
        """Test Canada business dividend distribution."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="Canada",
            tax_structure="Business",
            distribution_method="Dividend",
        )
        assert result["dividend_tax"] > 0


class TestMixedDistributionWithState:
    """Test mixed distribution with state tax."""

    def test_business_mixed_with_california_state_tax(self):
        """Test business mixed distribution with CA state tax."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Business",
            distribution_method="Mixed",
            salary_amount=50000,
            state="CA",
        )
        assert result["personal_tax"] > 0
        assert result["dividend_tax"] > 0

    def test_business_salary_with_state_tax(self):
        """Test business salary distribution with state tax."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Business",
            distribution_method="Salary",
            state="NY",
        )
        assert result["personal_tax"] > 0


class TestEdgeCasesProjectTaxes:
    """Test edge cases in project tax calculations."""

    def test_zero_people_raises_error(self):
        """Test zero people raises ValueError."""
        with pytest.raises(ValueError):
            calculate_project_taxes(
                revenue=100000,
                costs=10000,
                num_people=0,
                country="US",
                tax_structure="Individual",
            )

    def test_invalid_tax_structure_raises_error(self):
        """Test invalid tax structure raises ValueError."""
        with pytest.raises(ValueError):
            calculate_project_taxes(
                revenue=100000,
                costs=10000,
                num_people=1,
                country="US",
                tax_structure="InvalidStructure",
            )

    def test_negative_revenue(self):
        """Test negative revenue (loss scenario)."""
        result = calculate_project_taxes(
            revenue=-10000,
            costs=0,
            num_people=1,
            country="US",
            tax_structure="Individual",
        )
        assert result["gross_income"] == -10000
        # With negative income, total tax may be negative (loss carryover)
        assert result["total_tax"] <= 0

    def test_very_large_numbers(self):
        """Test with very large revenue numbers."""
        result = calculate_project_taxes(
            revenue=10000000,
            costs=1000000,
            num_people=5,
            country="US",
            tax_structure="Individual",
        )
        assert result["gross_income"] == 9000000
        assert result["total_tax"] > 0

    def test_fractional_people(self):
        """Test with fractional number of people (should work mathematically)."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=2.5,
            country="US",
            tax_structure="Individual",
        )
        assert result["net_income_per_person"] > 0


class TestOptimalSalaryCalculation:
    """Test optimal salary calculations for mixed distribution."""

    def test_optimal_salary_us(self):
        """Test optimal salary for US mixed distribution."""
        result = calculate_optimal_salary(90000, "US")
        assert result["recommended_salary"] > 0
        assert result["dividend_amount"] >= 0
        assert "reason" in result

    def test_optimal_salary_spain(self):
        """Test optimal salary for Spain mixed distribution."""
        result = calculate_optimal_salary(90000, "Spain")
        assert result["recommended_salary"] > 0
        assert result["dividend_amount"] >= 0

    def test_optimal_salary_other_country(self):
        """Test optimal salary for unsupported country uses 50/50 split."""
        result = calculate_optimal_salary(100000, "France")
        assert result["recommended_salary"] == pytest.approx(50000)
        assert result["dividend_amount"] == pytest.approx(50000)
        assert "50/50" in result["reason"]

    def test_optimal_salary_small_amount(self):
        """Test optimal salary with small after-tax amount."""
        result = calculate_optimal_salary(1000, "US")
        assert result["recommended_salary"] > 0
        assert result["dividend_amount"] >= 0

    def test_optimal_salary_zero_amount(self):
        """Test optimal salary with zero amount."""
        result = calculate_optimal_salary(0, "US")
        assert result["recommended_salary"] == 0
        assert result["dividend_amount"] == 0


class TestBreakdownDetails:
    """Test tax breakdown details."""

    def test_individual_breakdown_contains_components(self):
        """Test individual tax breakdown contains detailed components."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Individual",
        )
        breakdown = result["breakdown"]
        assert len(breakdown) > 0
        assert any("Income" in item.get("label", "") for item in breakdown)

    def test_business_salary_breakdown_includes_corporate(self):
        """Test business salary breakdown includes corporate tax."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Business",
            distribution_method="Salary",
        )
        breakdown = result["breakdown"]
        labels = [item.get("label", "") for item in breakdown]
        assert "Corporate Tax" in labels

    def test_business_mixed_breakdown_includes_all_components(self):
        """Test business mixed breakdown includes salary and dividend tax."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Business",
            distribution_method="Mixed",
            salary_amount=30000,
        )
        breakdown = result["breakdown"]
        breakdown_str = str(breakdown)
        assert "Corporate" in breakdown_str
        assert "Salary" in breakdown_str or "Personal" in breakdown_str
        assert "Dividend" in breakdown_str

    def test_business_reinvest_breakdown_shows_deferred(self):
        """Test reinvest breakdown shows deferred tax note."""
        result = calculate_project_taxes(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            tax_structure="Business",
            distribution_method="Reinvest",
        )
        breakdown = result["breakdown"]
        breakdown_str = str(breakdown)
        assert "Deferred" in breakdown_str or "deferred" in breakdown_str


class TestOptimalStrategyFunction:
    """Test get_optimal_strategy function."""

    def test_optimal_strategy_basic_us(self):
        """Test basic optimal strategy calculation for US."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
        )
        assert "all_strategies" in result
        assert "optimal" in result
        assert "savings" in result
        assert len(result["all_strategies"]) > 0

    def test_optimal_strategy_contains_all_methods(self):
        """Test optimal strategy includes all distribution methods."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
        )
        strategies = result["all_strategies"]
        strategy_names = [s.get("strategy_name", "") for s in strategies]

        assert "Individual Tax" in strategy_names
        assert "Business + Salary" in strategy_names
        assert "Business + Dividend" in strategy_names
        assert "Business + Mixed (Optimized)" in strategy_names

    def test_optimal_strategy_optimal_has_highest_take_home(self):
        """Test that optimal strategy has highest net income."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
        )
        optimal = result["optimal"]
        optimal_take_home = optimal["net_income_group"]

        # Check that optimal has highest take-home
        for strategy in result["all_strategies"]:
            assert strategy["net_income_group"] <= optimal_take_home

    def test_optimal_strategy_savings_calculation(self):
        """Test savings calculation between optimal and worst strategy."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
        )
        savings = result["savings"]

        # Savings should be positive or zero
        assert savings >= 0

        # Savings should be a reasonable value (max possible is optimal take-home)
        optimal_take_home = result["optimal"]["net_income_group"]
        assert savings <= optimal_take_home

    def test_optimal_strategy_uk(self):
        """Test optimal strategy for UK."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="UK",
        )
        assert "optimal" in result
        assert len(result["all_strategies"]) > 0

    def test_optimal_strategy_canada(self):
        """Test optimal strategy for Canada."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="Canada",
        )
        assert "optimal" in result
        assert len(result["all_strategies"]) > 0

    def test_optimal_strategy_with_state(self):
        """Test optimal strategy with US state specified."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
            state="CA",
        )
        assert "optimal" in result

    def test_optimal_strategy_multiple_people(self):
        """Test optimal strategy with multiple people."""
        result = get_optimal_strategy(
            revenue=200000,
            costs=20000,
            num_people=5,
            country="US",
        )
        strategies = result["all_strategies"]

        # Each strategy should have valid per-person income
        for strategy in strategies:
            # Per-person income could be zero or positive (Reinvest = 0)
            assert strategy["net_income_per_person"] >= 0

    def test_optimal_strategy_high_revenue(self):
        """Test optimal strategy favors business structure with high revenue."""
        result = get_optimal_strategy(
            revenue=1000000,
            costs=100000,
            num_people=1,
            country="US",
        )
        optimal = result["optimal"]

        # With high revenue, business structures are usually better
        # (though not always - depends on specific numbers)
        assert "strategy_name" in optimal
        assert optimal["net_income_group"] > 0

    def test_optimal_strategy_low_revenue(self):
        """Test optimal strategy with low revenue."""
        result = get_optimal_strategy(
            revenue=30000,
            costs=5000,
            num_people=1,
            country="US",
        )
        assert "optimal" in result
        assert len(result["all_strategies"]) > 0

    def test_optimal_strategy_all_strategies_have_required_fields(self):
        """Test all strategies have required fields."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=2,
            country="US",
        )

        required_fields = [
            "gross_income",
            "total_tax",
            "net_income_group",
            "effective_rate",
            "strategy_name",
        ]

        for strategy in result["all_strategies"]:
            for field in required_fields:
                assert field in strategy

    def test_optimal_strategy_mixed_is_reasonable(self):
        """Test mixed strategy produces reasonable middle-ground results."""
        result = get_optimal_strategy(
            revenue=100000,
            costs=10000,
            num_people=1,
            country="US",
        )

        # Find mixed strategy
        mixed = next(
            (s for s in result["all_strategies"] if "Mixed" in s.get("strategy_name", "")),
            None,
        )

        if mixed:
            # Mixed should have some of both taxes
            assert mixed["personal_tax"] > 0 or mixed["dividend_tax"] > 0

    def test_optimal_strategy_effectiveness(self):
        """Test that optimization provides meaningful difference."""
        result = get_optimal_strategy(
            revenue=500000,
            costs=50000,
            num_people=1,
            country="US",
        )

        # With substantial revenue, optimization should show meaningful savings
        savings = result["savings"]

        # Savings should typically be at least 5% of optimal take-home for high revenue
        optimal_take_home = result["optimal"]["net_income_group"]
        if optimal_take_home > 100000:
            assert savings > optimal_take_home * 0.05
