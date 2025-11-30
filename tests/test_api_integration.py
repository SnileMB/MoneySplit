"""
Comprehensive integration tests for API endpoints.

Tests all major API routes to ensure proper functionality and error handling.
Focuses on improving overall test coverage for api/main.py
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestProjectCRUDOperations:
    """Test complete CRUD operations for projects."""

    @pytest.fixture
    def valid_project_payload(self):
        """Standard valid project payload for testing."""
        return {
            "num_people": 2,
            "revenue": 50000,
            "costs": [5000, 2500],
            "country": "US",
            "tax_type": "Individual",
            "people": [
                {"name": "Alice Smith", "work_share": 0.6},
                {"name": "Bob Jones", "work_share": 0.4},
            ],
        }

    def test_create_and_retrieve_project(self, valid_project_payload):
        """Test creating a project and retrieving it."""
        # Create
        create_resp = client.post("/api/projects", json=valid_project_payload)
        assert create_resp.status_code == 201
        record_id = create_resp.json()["record_id"]

        # Retrieve
        get_resp = client.get(f"/api/records/{record_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["revenue"] == 50000
        assert data["num_people"] == 2

    def test_create_project_business_tax(self):
        """Test creating project with business tax type."""
        payload = {
            "num_people": 3,
            "revenue": 100000,
            "costs": [20000],
            "country": "Spain",
            "tax_type": "Business",
            "people": [
                {"name": "Person1", "work_share": 0.33},
                {"name": "Person2", "work_share": 0.33},
                {"name": "Person3", "work_share": 0.34},
            ],
        }
        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "record_id" in data

    def test_create_single_person_project(self):
        """Test creating a project with a single person."""
        payload = {
            "num_people": 1,
            "revenue": 25000,
            "costs": [5000],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Solo Developer", "work_share": 1.0}],
        }
        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201
        assert response.json()["record_id"] > 0

    def test_list_all_records(self):
        """Test listing all records."""
        response = client.get("/api/records")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_records_pagination(self):
        """Test record listing with limit parameter."""
        response = client.get("/api/records?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5


class TestReportEndpoints:
    """Test report and analytics endpoints."""

    def test_statistics_endpoint(self):
        """Test /api/reports/statistics endpoint."""
        response = client.get("/api/reports/statistics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_revenue_summary_endpoint(self):
        """Test /api/reports/revenue-summary endpoint."""
        response = client.get("/api/reports/revenue-summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_top_people_endpoint(self):
        """Test /api/reports/top-people endpoint."""
        response = client.get("/api/reports/top-people")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestForecastingEndpoints:
    """Test forecasting and prediction endpoints."""

    def test_revenue_forecast_endpoint(self):
        """Test /api/forecast/revenue endpoint."""
        response = client.get("/api/forecast/revenue")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_revenue_forecast_with_months(self):
        """Test forecast with specific number of months."""
        response = client.get("/api/forecast/revenue?months=6")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_tax_optimization_endpoint(self):
        """Test /api/forecast/tax-optimization endpoint."""
        response = client.get("/api/forecast/tax-optimization")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_trends_endpoint(self):
        """Test /api/forecast/trends endpoint."""
        response = client.get("/api/forecast/trends")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_comprehensive_forecast_endpoint(self):
        """Test /api/forecast/comprehensive endpoint."""
        response = client.get("/api/forecast/comprehensive")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestVisualizationEndpoints:
    """Test visualization endpoints."""

    def test_revenue_visualization(self):
        """Test /api/visualizations/revenue-summary endpoint."""
        response = client.get("/api/visualizations/revenue-summary")
        assert response.status_code == 200
        assert len(response.text) > 0

    def test_trends_visualization(self):
        """Test /api/visualizations/monthly-trends endpoint."""
        response = client.get("/api/visualizations/monthly-trends")
        assert response.status_code == 200

    def test_work_distribution_visualization(self):
        """Test /api/visualizations/work-distribution endpoint."""
        response = client.get("/api/visualizations/work-distribution")
        assert response.status_code == 200

    def test_tax_comparison_visualization(self):
        """Test /api/visualizations/tax-comparison endpoint."""
        response = client.get("/api/visualizations/tax-comparison")
        assert response.status_code == 200

    def test_profitability_visualization(self):
        """Test /api/visualizations/project-profitability endpoint."""
        response = client.get("/api/visualizations/project-profitability")
        assert response.status_code == 200


class TestExportEndpoints:
    """Test export functionality endpoints."""

    def test_export_pdf_record(self):
        """Test PDF export of a record."""
        # First create a record
        payload = {
            "num_people": 1,
            "revenue": 10000,
            "costs": [1000],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Test", "work_share": 1.0}],
        }
        create_resp = client.post("/api/projects", json=payload)
        record_id = create_resp.json()["record_id"]

        # Export as PDF
        response = client.get(f"/api/export/record/{record_id}/pdf")
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")

    def test_export_summary_pdf(self):
        """Test PDF export of summary."""
        response = client.get("/api/export/summary/pdf")
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")

    def test_export_forecast_pdf(self):
        """Test PDF export of forecast."""
        response = client.get("/api/export/forecast/pdf")
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")


class TestErrorHandling:
    """Test error handling in API endpoints."""

    def test_invalid_record_id_returns_404(self):
        """Test that invalid record ID returns 404."""
        response = client.get("/api/records/99999999")
        assert response.status_code == 404

    def test_invalid_project_data_returns_422(self):
        """Test that invalid project data returns validation error."""
        payload = {
            "num_people": 2,
            "revenue": "invalid",  # Should be a number
            "costs": [],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Test", "work_share": 0.5}],
        }
        response = client.post("/api/projects", json=payload)
        assert response.status_code == 422

    def test_missing_required_fields(self):
        """Test that missing required fields returns error."""
        payload = {
            "num_people": 2,
            # Missing revenue, costs, country, etc.
        }
        response = client.post("/api/projects", json=payload)
        assert response.status_code == 422


class TestMetricsAndHealth:
    """Test metrics and health check endpoints."""

    def test_metrics_endpoint_format(self):
        """Test that metrics endpoint returns proper Prometheus format."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        # Should contain some metrics or be non-empty
        assert len(response.text) > 0

    def test_root_endpoint_accessible(self):
        """Test that root endpoint is accessible."""
        response = client.get("/")
        assert response.status_code == 200


class TestDataIntegrity:
    """Test that data integrity is maintained across operations."""

    def test_multiple_projects_independent(self):
        """Test that multiple projects don't interfere with each other."""
        # Create first project
        payload1 = {
            "num_people": 1,
            "revenue": 10000,
            "costs": [1000],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Alice", "work_share": 1.0}],
        }
        resp1 = client.post("/api/projects", json=payload1)
        id1 = resp1.json()["record_id"]

        # Create second project with different data
        payload2 = {
            "num_people": 2,
            "revenue": 50000,
            "costs": [5000],
            "country": "Spain",
            "tax_type": "Business",
            "people": [
                {"name": "Bob", "work_share": 0.5},
                {"name": "Charlie", "work_share": 0.5},
            ],
        }
        resp2 = client.post("/api/projects", json=payload2)
        id2 = resp2.json()["record_id"]

        # Verify data integrity
        get1 = client.get(f"/api/records/{id1}").json()
        get2 = client.get(f"/api/records/{id2}").json()

        assert get1["revenue"] == 10000
        assert get2["revenue"] == 50000
        assert get1["id"] != get2["id"]

    def test_project_consistency_across_endpoints(self):
        """Test that project data is consistent across different endpoints."""
        payload = {
            "num_people": 1,
            "revenue": 30000,
            "costs": [3000],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Developer", "work_share": 1.0}],
        }
        resp = client.post("/api/projects", json=payload)
        record_id = resp.json()["record_id"]

        # Get from records endpoint
        record = client.get(f"/api/records/{record_id}").json()
        assert record["revenue"] == 30000

        # List should contain this record
        list_resp = client.get("/api/records").json()
        assert any(r["id"] == record_id for r in list_resp)
