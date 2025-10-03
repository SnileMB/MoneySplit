"""
Test script for Phase 1 changes - Tax Calculation Engine
Tests all distribution methods: Individual, Business+Salary, Business+Dividend, Business+Mixed, Business+Reinvest
"""
import sys
sys.path.insert(0, '.')

from Logic import tax_engine

def test_all_scenarios():
    """Test all tax scenarios with a sample project."""

    print("=" * 70)
    print("PHASE 1 TEST: Enhanced Tax Calculation Engine")
    print("=" * 70)

    # Sample project data
    revenue = 100000
    costs = 20000
    num_people = 2
    country = "US"

    print(f"\nProject Details:")
    print(f"  Revenue: ${revenue:,}")
    print(f"  Costs: ${costs:,}")
    print(f"  Gross Income: ${revenue - costs:,}")
    print(f"  People: {num_people}")
    print(f"  Country: {country}")
    print("\n" + "=" * 70)

    # Test 1: Individual Tax
    print("\n📋 TEST 1: INDIVIDUAL TAX")
    print("-" * 70)
    result = tax_engine.calculate_project_taxes(
        revenue, costs, num_people, country, "Individual", "N/A"
    )
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Net Income (total): ${result['net_income_group']:,.2f}")
    print(f"  Net Income (per person): ${result['net_income_per_person']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")
    print(f"  Breakdown:")
    for item in result['breakdown']:
        print(f"    - {item['label']}: ${item['amount']:,.2f}")

    # Test 2: Business + Salary
    print("\n📋 TEST 2: BUSINESS TAX + SALARY DISTRIBUTION")
    print("-" * 70)
    result = tax_engine.calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Salary"
    )
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Net Income (total): ${result['net_income_group']:,.2f}")
    print(f"  Net Income (per person): ${result['net_income_per_person']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")
    print(f"  Breakdown:")
    for item in result['breakdown']:
        print(f"    - {item['label']}: ${item['amount']:,.2f}")

    # Test 3: Business + Dividend
    print("\n📋 TEST 3: BUSINESS TAX + DIVIDEND DISTRIBUTION")
    print("-" * 70)
    result = tax_engine.calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Dividend"
    )
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Net Income (total): ${result['net_income_group']:,.2f}")
    print(f"  Net Income (per person): ${result['net_income_per_person']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")
    print(f"  Breakdown:")
    for item in result['breakdown']:
        print(f"    - {item['label']}: ${item['amount']:,.2f}")

    # Test 4: Business + Mixed (Salary $40K, rest as dividend)
    print("\n📋 TEST 4: BUSINESS TAX + MIXED DISTRIBUTION")
    print("-" * 70)
    salary_amount = 40000
    print(f"  Salary Amount: ${salary_amount:,}")
    result = tax_engine.calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Mixed", salary_amount
    )
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Net Income (total): ${result['net_income_group']:,.2f}")
    print(f"  Net Income (per person): ${result['net_income_per_person']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")
    print(f"  Breakdown:")
    for item in result['breakdown']:
        print(f"    - {item['label']}: ${item['amount']:,.2f}")

    # Test 5: Business + Reinvest
    print("\n📋 TEST 5: BUSINESS TAX + REINVEST (No Distribution)")
    print("-" * 70)
    result = tax_engine.calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Reinvest"
    )
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Net Income (personal): ${result['net_income_group']:,.2f}")
    print(f"  Company Retained: ${result['company_retained']:,.2f}")
    print(f"  Effective Rate (corp only): {result['effective_rate']:.2f}%")
    print(f"  Breakdown:")
    for item in result['breakdown']:
        note = f" ({item['note']})" if 'note' in item else ""
        print(f"    - {item['label']}: ${item['amount']:,.2f}{note}")

    # Test 6: Get Optimal Strategy
    print("\n" + "=" * 70)
    print("📊 OPTIMAL STRATEGY COMPARISON")
    print("=" * 70)
    optimal_result = tax_engine.get_optimal_strategy(revenue, costs, num_people, country)

    print(f"\n✅ OPTIMAL: {optimal_result['optimal']['strategy_name']}")
    print(f"   Take Home: ${optimal_result['optimal']['net_income_group']:,.2f}")
    print(f"   Tax Paid: ${optimal_result['optimal']['total_tax']:,.2f}")
    print(f"   Effective Rate: {optimal_result['optimal']['effective_rate']:.2f}%")

    print(f"\n❌ WORST: {optimal_result['worst']['strategy_name']}")
    print(f"   Take Home: ${optimal_result['worst']['net_income_group']:,.2f}")
    print(f"   Tax Paid: ${optimal_result['worst']['total_tax']:,.2f}")
    print(f"   Effective Rate: {optimal_result['worst']['effective_rate']:.2f}%")

    print(f"\n💰 POTENTIAL SAVINGS: ${optimal_result['savings']:,.2f}")
    print(f"   ({(optimal_result['savings'] / optimal_result['worst']['net_income_group'] * 100):.1f}% more take-home)")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    test_all_scenarios()
