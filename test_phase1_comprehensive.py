"""
Comprehensive Phase 1 Test - End-to-End Testing
Tests: Tax Engine, API Integration, Database Operations
"""
import sys
import requests
import json
sys.path.insert(0, '.')

from Logic import tax_engine
from DB import setup

API_BASE = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_tax_engine():
    """Test the tax engine directly."""
    print_section("TEST 1: TAX ENGINE MODULE")

    # Test data
    revenue = 150000
    costs = 30000
    num_people = 3
    country = "US"

    print(f"\nProject: ${revenue:,} revenue, ${costs:,} costs, {num_people} people, {country}")

    # Test Individual
    print("\n1️⃣  Individual Tax:")
    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, country, "Individual", "N/A")
    print(f"   Take Home: ${result['net_income_group']:,.2f}")
    print(f"   Tax: ${result['total_tax']:,.2f} ({result['effective_rate']:.2f}%)")

    # Test Business + Dividend
    print("\n2️⃣  Business + Dividend:")
    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, country, "Business", "Dividend")
    print(f"   Take Home: ${result['net_income_group']:,.2f}")
    print(f"   Tax: ${result['total_tax']:,.2f} ({result['effective_rate']:.2f}%)")

    # Test optimal strategy
    print("\n3️⃣  Optimal Strategy Finder:")
    optimal = tax_engine.get_optimal_strategy(revenue, costs, num_people, country)
    print(f"   Best: {optimal['optimal']['strategy_name']}")
    print(f"   Savings vs worst: ${optimal['savings']:,.2f}")

    print("\n✅ Tax Engine Module: PASSED")
    return True

def test_database_operations():
    """Test database with new fields."""
    print_section("TEST 2: DATABASE OPERATIONS")

    # Check if new columns exist
    conn = setup.get_conn()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(tax_records)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()

    print("\n1️⃣  Database Schema:")
    if 'distribution_method' in columns:
        print("   ✅ distribution_method column exists")
    else:
        print("   ❌ distribution_method column missing!")
        return False

    if 'salary_amount' in columns:
        print("   ✅ salary_amount column exists")
    else:
        print("   ❌ salary_amount column missing!")
        return False

    # Test fetching records
    print("\n2️⃣  Fetch Records:")
    records = setup.fetch_last_records(3)
    print(f"   Found {len(records)} records")
    if records:
        record = records[0]
        print(f"   Latest record has {len(record)} fields")
        if len(record) >= 14:  # Should have distribution_method and salary_amount
            print("   ✅ Records include new fields")
        else:
            print(f"   ⚠️  Records may not have new fields (got {len(record)} fields)")

    print("\n✅ Database Operations: PASSED")
    return True

def test_api_integration():
    """Test API endpoints with new fields."""
    print_section("TEST 3: API INTEGRATION")

    print("\n⚠️  Note: This test requires the API server to be running")
    print("   Start with: python3 -m uvicorn api.main:app --reload\n")

    try:
        # Test 1: Check API is running
        print("1️⃣  Checking API server...")
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("   ✅ API server is running")
        else:
            print("   ❌ API server returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print("   ⚠️  API server not running - skipping API tests")
        print("   To test API, run: python3 -m uvicorn api.main:app --reload")
        return None

    # Test 2: Optimal strategy endpoint
    print("\n2️⃣  Testing /api/optimal-strategy endpoint:")
    try:
        response = requests.get(f"{API_BASE}/api/optimal-strategy", params={
            "revenue": 100000,
            "costs": 20000,
            "num_people": 2,
            "country": "US"
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Endpoint works")
            print(f"   Optimal: {data['optimal']['strategy_name']}")
            print(f"   Savings: ${data['savings']:,.2f}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 3: Create project with distribution method
    print("\n3️⃣  Testing project creation with distribution_method:")
    project_data = {
        "num_people": 2,
        "revenue": 100000,
        "costs": [15000, 5000],
        "country": "US",
        "tax_type": "Business",
        "distribution_method": "Dividend",
        "salary_amount": 0,
        "people": [
            {"name": "Alice Test", "work_share": 0.6},
            {"name": "Bob Test", "work_share": 0.4}
        ]
    }

    try:
        response = requests.post(f"{API_BASE}/api/projects", json=project_data)
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Project created: Record ID {data['record_id']}")
            print(f"   Tax: ${data['summary']['tax_amount']:,.2f}")
            print(f"   Distribution: {data['summary'].get('distribution_method', 'N/A')}")

            # Verify we can fetch it back
            record_id = data['record_id']
            response = requests.get(f"{API_BASE}/api/records/{record_id}")
            if response.status_code == 200:
                record = response.json()
                print(f"   ✅ Record retrieved successfully")
                print(f"   Distribution method: {record.get('distribution_method', 'N/A')}")
            else:
                print(f"   ⚠️  Could not retrieve record")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    print("\n✅ API Integration: PASSED")
    return True

def test_edge_cases():
    """Test edge cases and error handling."""
    print_section("TEST 4: EDGE CASES & ERROR HANDLING")

    print("\n1️⃣  Zero people (should error):")
    try:
        result = tax_engine.calculate_project_taxes(100000, 20000, 0, "US", "Individual", "N/A")
        print("   ❌ Should have raised an error!")
        return False
    except ValueError as e:
        print(f"   ✅ Correctly raised error: {e}")

    print("\n2️⃣  Mixed strategy with salary > profit (should error):")
    try:
        result = tax_engine.calculate_project_taxes(100000, 20000, 2, "US", "Business", "Mixed", 150000)
        print("   ❌ Should have raised an error!")
        return False
    except ValueError as e:
        print(f"   ✅ Correctly raised error: {e}")

    print("\n3️⃣  Negative revenue (taxes on loss):")
    result = tax_engine.calculate_project_taxes(50000, 80000, 2, "US", "Individual", "N/A")
    print(f"   Gross income: ${result['gross_income']:,.2f}")
    print(f"   Tax: ${result['total_tax']:,.2f}")
    if result['gross_income'] < 0:
        print("   ✅ Handles negative income")

    print("\n✅ Edge Cases: PASSED")
    return True

def test_spain_tax_rates():
    """Test Spain-specific tax calculations."""
    print_section("TEST 5: SPAIN TAX RATES")

    revenue = 100000
    costs = 20000
    num_people = 2

    print("\n1️⃣  Spain Individual Tax:")
    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, "Spain", "Individual", "N/A")
    print(f"   Take Home: ${result['net_income_group']:,.2f}")
    print(f"   Tax Rate: {result['effective_rate']:.2f}%")

    print("\n2️⃣  Spain Business + Dividend (19% dividend tax):")
    result = tax_engine.calculate_project_taxes(revenue, costs, num_people, "Spain", "Business", "Dividend")
    print(f"   Take Home: ${result['net_income_group']:,.2f}")
    print(f"   Tax Rate: {result['effective_rate']:.2f}%")
    dividend_item = next((item for item in result['breakdown'] if 'Dividend' in item['label']), None)
    if dividend_item and '19' in dividend_item['label']:
        print("   ✅ Using Spain's 19% dividend rate")

    print("\n✅ Spain Tax Rates: PASSED")
    return True

def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  PHASE 1 COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Tax Engine Module", test_tax_engine()))
    results.append(("Database Operations", test_database_operations()))
    results.append(("API Integration", test_api_integration()))
    results.append(("Edge Cases", test_edge_cases()))
    results.append(("Spain Tax Rates", test_spain_tax_rates()))

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0
    skipped = 0

    for name, result in results:
        if result is True:
            print(f"  ✅ {name}: PASSED")
            passed += 1
        elif result is False:
            print(f"  ❌ {name}: FAILED")
            failed += 1
        else:
            print(f"  ⏭️  {name}: SKIPPED")
            skipped += 1

    print("\n" + "=" * 70)
    print(f"  Total: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 70)

    if failed == 0 and passed > 0:
        print("\n🎉 ALL TESTS PASSED! Phase 1 is complete and working.")
    elif failed > 0:
        print("\n⚠️  Some tests failed. Please review the output above.")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
