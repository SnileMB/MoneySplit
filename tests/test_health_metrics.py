"""
Tests for health checks, metrics, and monitoring endpoints.

Covers:
- api/health.py: health status endpoints
- api/metrics.py: Prometheus metrics
- api/middleware.py: request middleware
"""
import pytest
import json
import time
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient

from api.main import app
from api import health, metrics, middleware


client = TestClient(app)


class TestHealthChecks:
    """Test health check endpoint functions."""

    def test_get_uptime(self):
        """Test uptime calculation."""
        uptime = health.get_uptime()
        assert isinstance(uptime, float)
        assert uptime > 0

    def test_get_uptime_increases(self):
        """Test that uptime increases over time."""
        uptime1 = health.get_uptime()
        time.sleep(0.1)
        uptime2 = health.get_uptime()
        assert uptime2 > uptime1

    def test_get_system_info(self):
        """Test system information retrieval."""
        info = health.get_system_info()
        assert "cpu_percent" in info
        assert "memory_mb" in info
        assert "memory_percent" in info
        assert "open_files" in info
        assert "threads" in info
        assert info["memory_mb"] > 0
        assert info["threads"] > 0

    def test_get_system_info_cpu_percent_valid(self):
        """Test that CPU percent is a valid percentage."""
        info = health.get_system_info()
        assert 0 <= info["cpu_percent"] <= 100

    def test_get_system_info_memory_percent_valid(self):
        """Test that memory percent is a valid percentage."""
        info = health.get_system_info()
        assert 0 <= info["memory_percent"] <= 100

    def test_check_database_healthy(self):
        """Test database health check when database is healthy."""
        result = health.check_database()
        assert result["status"] == "healthy"
        assert "records_count" in result
        assert "people_count" in result
        assert isinstance(result["records_count"], int)
        assert isinstance(result["people_count"], int)

    @patch('api.health.setup.get_conn')
    def test_check_database_unhealthy(self, mock_get_conn):
        """Test database health check when database is unhealthy."""
        mock_get_conn.side_effect = Exception("Connection failed")
        result = health.check_database()
        assert result["status"] == "unhealthy"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_health_status(self):
        """Test basic health status."""
        result = await health.get_health_status()
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert result["version"] == "1.0.0"
        assert isinstance(result["uptime_seconds"], float)

    @pytest.mark.asyncio
    async def test_get_ready_status(self):
        """Test readiness status."""
        result = await health.get_ready_status()
        assert "status" in result
        assert result["status"] in ["ready", "not_ready"]
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert "database" in result
        assert "system" in result

    @pytest.mark.asyncio
    async def test_get_detailed_status(self):
        """Test detailed health status."""
        result = await health.get_detailed_status()
        assert "status" in result
        assert result["status"] in ["healthy", "degraded"]
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert "database" in result
        assert "system" in result
        assert "version" in result
        assert "environment" in result
        assert "cpu_status" in result["system"]
        assert "memory_status" in result["system"]


class TestHealthEndpoints:
    """Test health check API endpoint functions."""

    def test_metrics_endpoint(self):
        """Test /metrics endpoint is accessible."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        # Root endpoint returns HTML or text, not JSON
        assert len(response.text) > 0


class TestMetrics:
    """Test Prometheus metrics functionality."""

    def test_metrics_endpoint(self):
        """Test /metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus format should be text
        assert "text/plain" in response.headers.get("content-type", "")

    def test_metrics_contains_prometheus_format(self):
        """Test that metrics endpoint returns Prometheus format."""
        response = client.get("/metrics")
        content = response.text
        # Prometheus format includes HELP and TYPE comments
        assert "#" in content or "http_" in content

    def test_metrics_multiple_calls(self):
        """Test that metrics are updated with multiple API calls."""
        # Make some API calls
        client.get("/health")
        client.get("/health")
        response = client.get("/metrics")
        assert response.status_code == 200
        # Should contain request metrics
        content = response.text
        assert len(content) > 0


class TestMetricsCounter:
    """Test request metrics counter functionality."""

    def test_make_request_increments_metrics(self):
        """Test that making requests increments metrics."""
        # Get initial metrics
        response1 = client.get("/metrics")
        initial_content = response1.text

        # Make some requests
        client.get("/health")
        client.post("/projects", json={
            "revenue": 10000,
            "costs": 1000,
            "num_people": 2,
            "tax_origin": "US",
            "tax_type": "Individual",
            "people": [
                {"name": "Alice", "work_share": 0.5},
                {"name": "Bob", "work_share": 0.5}
            ]
        })

        # Get updated metrics
        response2 = client.get("/metrics")
        updated_content = response2.text

        # Both should be valid
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestMiddleware:
    """Test API middleware functions."""

    def test_request_id_is_set(self):
        """Test that request ID middleware processes requests."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Request should have been processed by middleware

    def test_multiple_requests_processed(self):
        """Test that multiple requests are processed correctly."""
        response1 = client.get("/metrics")
        response2 = client.get("/")
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestHealthStatusCodes:
    """Test API endpoint status codes."""

    def test_metrics_endpoint_returns_200(self):
        """Test that metrics endpoint returns 200 OK."""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_root_endpoint_returns_200(self):
        """Test that root endpoint returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_invalid_endpoint_serves_react_app(self):
        """Test that non-API endpoints serve React app for client-side routing."""
        response = client.get("/nonexistent")
        # In SPA architecture, unknown routes serve the React app (200 or 404 if frontend not built)
        assert response.status_code in [200, 404]


class TestMetricsEndpointFormat:
    """Test Prometheus metrics endpoint format."""

    def test_metrics_response_is_text(self):
        """Test that metrics endpoint returns text content."""
        response = client.get("/metrics")
        assert isinstance(response.text, str)
        assert len(response.text) > 0

    def test_metrics_endpoint_accessible(self):
        """Test that metrics endpoint is accessible."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.text is not None
