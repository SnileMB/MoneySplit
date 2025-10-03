"""
Test script for improved tax logic:
- Self-Employment Tax (Social Security + Medicare)
- Standard Deductions
- Optimal Salary Calculator for Business+Mixed
"""
import sys
sys.path.insert(0, '.')

from Logic import tax_engine

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_improved_calculations():
    """Test all improvements with same $100K revenue, $20K costs example."""

    revenue = 100000
    costs = 20000
    num_people = 2
    country = "US"

    print_section("IMPROVED TAX LOGIC TEST - US Example")
    print(f"\nProject: ${revenue:,} revenue, ${costs:,} costs, {num_people} people")
    print(f"Gross Income: ${revenue - costs:,}\n")

    # Test 1: Individual Tax (WITH self-employment tax + standard deduction)
    print_section("1️⃣  INDIVIDUAL TAX (Self-Employed)")
    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, country, "Individual", "N/A")

    print(f"\n📊 Results:")
    print(f"  Total Take Home: ${result['net_income_group']:,.2f}")
    print(f"  Take Home Per Person: ${result['net_income_per_person']:,.2f}")
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")
    print(f"  Standard Deduction Used: ${result.get('standard_deduction_used', 0):,.2f}")

    print(f"\n💰 Tax Breakdown:")
    for item in result['breakdown']:
        note = f" ({item['note']})" if 'note' in item else ""
        print(f"  • {item['label']}: ${item['amount']:,.2f}{note}")

    # Test 2: Business + Dividend (WITH standard deduction on salary if any)
    print_section("2️⃣  BUSINESS + DIVIDEND")
    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, country, "Business", "Dividend")

    print(f"\n📊 Results:")
    print(f"  Total Take Home: ${result['net_income_group']:,.2f}")
    print(f"  Take Home Per Person: ${result['net_income_per_person']:,.2f}")
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")

    print(f"\n💰 Tax Breakdown:")
    for item in result['breakdown']:
        print(f"  • {item['label']}: ${item['amount']:,.2f}")

    # Test 3: Business + Mixed (AUTO-OPTIMIZED)
    print_section("3️⃣  BUSINESS + MIXED (AUTO-OPTIMIZED)")
    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, country, "Business", "Mixed", 0)

    print(f"\n📊 Results:")
    print(f"  Total Take Home: ${result['net_income_group']:,.2f}")
    print(f"  Take Home Per Person: ${result['net_income_per_person']:,.2f}")
    print(f"  Total Tax: ${result['total_tax']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")

    print(f"\n💰 Tax Breakdown:")
    for item in result['breakdown']:
        note = f"\n      ℹ️  {item['note']}" if 'note' in item else ""
        print(f"  • {item['label']}: ${item['amount']:,.2f}{note}")

    # Test 4: Get Optimal Strategy (now includes Mixed)
    print_section("4️⃣  OPTIMAL STRATEGY COMPARISON (5 Strategies)")
    optimal = tax_engine.get_optimal_strategy(revenue, costs, num_people, country)

    print(f"\n🏆 All Strategies Ranked:")
    sorted_strategies = sorted(optimal['all_strategies'], key=lambda x: x['net_income_group'], reverse=True)

    for i, strategy in enumerate(sorted_strategies):
        if strategy['net_income_group'] == 0:
            continue  # Skip Reinvest for ranking

        emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        is_optimal = strategy == optimal['optimal']
        marker = " ⭐ OPTIMAL" if is_optimal else ""

        print(f"\n{emoji} {strategy['strategy_name']}{marker}")
        print(f"   Take Home: ${strategy['net_income_group']:,.2f}")
        print(f"   Tax Paid: ${strategy['total_tax']:,.2f}")
        print(f"   Effective Rate: {strategy['effective_rate']:.2f}%")

    print(f"\n💡 Savings:")
    print(f"   Best vs Worst: ${optimal['savings']:,.2f}")
    print(f"   That's {(optimal['savings'] / optimal['worst']['net_income_group'] * 100):.1f}% more money!")

    # Test 5: Compare Before vs After Improvements
    print_section("5️⃣  BEFORE vs AFTER IMPROVEMENTS")

    print(f"\n🔴 OLD Individual Calculation (No SE Tax, No Deduction):")
    print(f"   Income Tax Only: ~$9,189")
    print(f"   Take Home: ~$70,811")
    print(f"   Effective Rate: ~11.49%")

    individual = optimal['all_strategies'][0]  # Individual is first
    print(f"\n🟢 NEW Individual Calculation (WITH SE Tax + Deduction):")
    print(f"   Total Tax: ${individual['total_tax']:,.2f}")
    print(f"   Take Home: ${individual['net_income_group']:,.2f}")
    print(f"   Effective Rate: {individual['effective_rate']:.2f}%")

    difference = 70811 - individual['net_income_group']
    print(f"\n📉 Difference: ${difference:,.2f} less take-home (more accurate!)")
    print(f"   Old calculation was understating tax by ${difference:,.2f}")

    print("\n" + "=" * 80)
    print("✅ IMPROVED TAX LOGIC TEST COMPLETE")
    print("=" * 80)


def test_spain_comparison():
    """Test Spain to show standard deduction impact."""

    print_section("SPAIN COMPARISON TEST")

    revenue = 100000
    costs = 20000
    num_people = 2

    print(f"\nProject: €{revenue:,} revenue, €{costs:,} costs, {num_people} people\n")

    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, "Spain", "Individual", "N/A")

    print(f"Individual Tax (Spain):")
    print(f"  Take Home: €{result['net_income_group']:,.2f}")
    print(f"  Tax: €{result['total_tax']:,.2f}")
    print(f"  Effective Rate: {result['effective_rate']:.2f}%")
    print(f"  Standard Deduction: €{result.get('standard_deduction_used', 0):,.2f}")


if __name__ == "__main__":
    test_improved_calculations()
    test_spain_comparison()
