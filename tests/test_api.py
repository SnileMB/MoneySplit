"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestProjectEndpoints:
    """Test project CRUD endpoints."""

    def test_create_project_success(self):
        """Test successful project creation."""
        payload = {
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

        response = client.post("/api/projects", json=payload)

        assert response.status_code == 201  # FastAPI returns 201 for created
        data = response.json()
        assert "record_id" in data
        assert data["message"] == "Project created successfully"

    def test_create_project_invalid_work_shares(self):
        """Test project creation with invalid work shares."""
        payload = {
            "num_people": 2,
            "revenue": 10000,
            "costs": [1000],
            "country": "US",
            "tax_type": "Individual",
            "people": [
                {"name": "Alice", "work_share": 0.7},
                {"name": "Bob", "work_share": 0.7},  # Sums to 1.4
            ],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 422  # FastAPI validation error

    def test_create_project_negative_revenue(self):
        """Test project creation with negative revenue."""
        payload = {
            "num_people": 1,
            "revenue": -5000,
            "costs": [1000],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Alice", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 422  # Validation error

    def test_get_recent_records(self):
        """Test fetching recent records."""
        response = client.get("/api/records")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_record_by_id(self):
        """Test fetching specific record by ID."""
        # First create a record
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Test User", "work_share": 1.0}],
        }

        create_response = client.post("/api/projects", json=payload)
        record_id = create_response.json()["record_id"]

        # Fetch the record
        response = client.get(f"/api/records/{record_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == record_id  # API uses "id" not "record_id"

    def test_get_nonexistent_record(self):
        """Test fetching a non-existent record."""
        response = client.get("/api/records/999999")

        assert response.status_code == 404


class TestReportEndpoints:
    """Test report and statistics endpoints."""

    def test_get_statistics(self):
        """Test overall statistics endpoint."""
        response = client.get("/api/reports/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "total_revenue" in data
        assert "total_records" in data  # API uses "total_records" not "total_projects"
        assert "total_tax" in data  # API uses "total_tax" not "total_tax_paid"

    def test_get_revenue_summary(self):
        """Test revenue summary by year."""
        response = client.get("/api/reports/revenue-summary")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_top_people(self):
        """Test top contributors endpoint."""
        response = client.get("/api/reports/top-people")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "name" in data[0]
            assert "total_gross" in data[0]  # API uses "total_gross" not "total_earned"


class TestForecastingEndpoints:
    """Test forecasting and ML endpoints."""

    def test_revenue_forecast_default(self):
        """Test revenue forecasting with default months."""
        response = client.get("/api/forecast/revenue")

        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        # May not have enough data, so just check structure exists

    def test_revenue_forecast_custom_months(self):
        """Test revenue forecasting with custom months."""
        response = client.get("/api/forecast/revenue?months=6")

        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        # May be empty if insufficient data

    def test_comprehensive_forecast(self):
        """Test comprehensive forecast endpoint."""
        response = client.get("/api/forecast/comprehensive")

        assert response.status_code == 200
        data = response.json()
        assert "revenue_forecast" in data
        assert "recommendations" in data  # API uses "recommendations" directly

    def test_tax_optimization(self):
        """Test tax optimization recommendations."""
        response = client.get("/api/forecast/tax-optimization")

        assert response.status_code == 200
        data = response.json()
        assert "tax_comparison" in data  # API structure is different
        assert "recommendations" in data

    def test_trends_analysis(self):
        """Test trend analysis endpoint."""
        response = client.get("/api/forecast/trends")

        assert response.status_code == 200
        data = response.json()
        # May not have enough data, check for success or message
        assert "success" in data or "message" in data


class TestVisualizationEndpoints:
    """Test visualization endpoints."""

    def test_revenue_summary_visualization(self):
        """Test revenue summary visualization."""
        response = client.get("/api/visualizations/revenue-summary")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert b"Revenue Summary" in response.content

    def test_monthly_trends_visualization(self):
        """Test monthly trends visualization."""
        response = client.get("/api/visualizations/monthly-trends")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_work_distribution_visualization(self):
        """Test work distribution visualization."""
        response = client.get("/api/visualizations/work-distribution")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_tax_comparison_visualization(self):
        """Test tax comparison visualization."""
        response = client.get("/api/visualizations/tax-comparison")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_profitability_visualization(self):
        """Test project profitability visualization."""
        response = client.get("/api/visualizations/project-profitability")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestPDFExportEndpoints:
    """Test PDF export endpoints."""

    def test_export_record_pdf(self):
        """Test exporting a record as PDF."""
        # First create a record
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "PDF Test User", "work_share": 1.0}],
        }

        create_response = client.post("/api/projects", json=payload)
        record_id = create_response.json()["record_id"]

        # Export as PDF
        response = client.get(f"/api/export/record/{record_id}/pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_export_summary_pdf(self):
        """Test exporting summary as PDF."""
        response = client.get("/api/export/summary/pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_export_forecast_pdf(self):
        """Test exporting forecast as PDF."""
        response = client.get("/api/export/forecast/pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


class TestHealthCheck:
    """Test health check endpoint."""

    def test_root_endpoint(self):
        """Test API root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        # Root may return HTML, not JSON
        assert response.text is not None
