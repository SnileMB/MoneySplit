#!/usr/bin/env python3
"""Comprehensive test suite for MoneySplit"""

import sys
from api.main import app
from fastapi.testclient import TestClient


def test_backend_modules():
    """Test all backend modules can be imported"""
    print("🧪 Testing Backend Modules...")
    try:
        from DB import setup
        from Logic import validators, pdf_generator, forecasting
        from api import main, models

        # ProgramBackend uses MoneySplit prefix which is fine
        print("   ✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Module import failed: {e}")
        return False


def test_database_schema():
    """Test database schema"""
    print("\n🧪 Testing Database Schema...")
    try:
        from DB import setup

        conn = setup.get_conn()
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ["tax_records", "people", "tax_brackets"]
        for table in required_tables:
            if table not in tables:
                print(f"   ❌ Missing table: {table}")
                return False

        conn.close()
        print("   ✅ Database schema correct")
        return True
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    try:
        client = TestClient(app)

        # Test root
        response = client.get("/")
        assert response.status_code == 200, "Root endpoint failed"

        # Test statistics
        response = client.get("/api/reports/statistics")
        assert response.status_code == 200, "Statistics endpoint failed"

        # Test records
        response = client.get("/api/records")
        assert response.status_code == 200, "Records endpoint failed"

        print("   ✅ All API endpoints responding")
        return True
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False


def test_project_creation():
    """Test creating a project via API"""
    print("\n🧪 Testing Project Creation...")
    try:
        client = TestClient(app)

        project_data = {
            "num_people": 2,
            "revenue": 10000,
            "costs": [1000, 500],
            "country": "US",
            "tax_type": "Individual",
            "people": [
                {"name": "Alice", "work_share": 0.6},
                {"name": "Bob", "work_share": 0.4},
            ],
        }

        response = client.post("/api/projects", json=project_data)
        assert (
            response.status_code == 201
        ), f"Project creation failed: {response.status_code}"

        result = response.json()
        assert "record_id" in result, "Missing record_id in response"

        print(f"   ✅ Project created (ID: {result['record_id']})")
        return True
    except Exception as e:
        print(f"   ❌ Project creation failed: {e}")
        return False


def test_forecasting():
    """Test forecasting functionality"""
    print("\n🧪 Testing Forecasting...")
    try:
        from Logic import forecasting

        # Test tax optimization
        result = forecasting.tax_optimization_analysis()
        assert "tax_comparison" in result, "Missing tax_comparison"
        assert "recommendations" in result, "Missing recommendations"

        # Test comprehensive forecast
        result = forecasting.comprehensive_forecast()
        assert "revenue_forecast" in result, "Missing revenue_forecast"
        assert "tax_optimization" in result, "Missing tax_optimization"

        print("   ✅ Forecasting functions working")
        return True
    except Exception as e:
        print(f"   ❌ Forecasting test failed: {e}")
        return False


def test_pdf_generation():
    """Test PDF generation"""
    print("\n🧪 Testing PDF Generation...")
    try:
        from Logic import pdf_generator
        from DB import setup

        records = setup.fetch_last_records(1)
        if records:
            record = setup.get_record_by_id(records[0][0])
            people = setup.fetch_people_by_record(records[0][0])

            # Test project PDF
            filepath = pdf_generator.generate_project_pdf(
                record, people, "reports/test_project.pdf"
            )

            print(f"   ✅ PDF generation working")
            return True
        else:
            print("   ℹ️  No records for PDF test (OK)")
            return True
    except Exception as e:
        print(f"   ❌ PDF test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 MoneySplit Comprehensive Test Suite")
    print("=" * 60)

    tests = [
        test_backend_modules,
        test_database_schema,
        test_api_endpoints,
        test_project_creation,
        test_forecasting,
        test_pdf_generation,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed! Your application is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
