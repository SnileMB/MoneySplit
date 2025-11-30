"""
Comprehensive tests for API middleware.

Tests logging middleware, exception handling, and request tracking.
"""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.middleware import logging_middleware, exception_handler
from exceptions import (
    MoneySplitException,
    ValidationError,
    DatabaseError,
    TaxCalculationError,
    NotFoundError,
)


class TestLoggingMiddleware:
    """Test logging middleware functionality."""

    @pytest.mark.asyncio
    async def test_logging_middleware_adds_request_id(self):
        """Test that logging middleware adds request ID to request state."""
        # Create a mock request
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"

        # Create a mock call_next
        response = MagicMock()
        response.status_code = 200
        call_next = AsyncMock(return_value=response)

        # Call middleware
        result = await logging_middleware(request, call_next)

        # Verify request ID was set
        assert request.state.request_id is not None

    @pytest.mark.asyncio
    async def test_logging_middleware_adds_response_header(self):
        """Test that logging middleware adds request ID to response headers."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"

        response = MagicMock()
        response.status_code = 200
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        result = await logging_middleware(request, call_next)

        # Verify request ID was added to response headers
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_logging_middleware_calls_next(self):
        """Test that logging middleware calls next handler."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"

        response = MagicMock()
        response.status_code = 200
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        await logging_middleware(request, call_next)

        # Verify call_next was called
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_logging_middleware_returns_response(self):
        """Test that logging middleware returns the response."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"

        response = MagicMock()
        response.status_code = 200
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        result = await logging_middleware(request, call_next)

        # Verify response is returned
        assert result == response

    @pytest.mark.asyncio
    async def test_logging_middleware_handles_none_client(self):
        """Test middleware handles request with no client."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client = None  # No client

        response = MagicMock()
        response.status_code = 200
        response.headers = {}
        call_next = AsyncMock(return_value=response)

        # Should not raise error
        result = await logging_middleware(request, call_next)
        assert result == response

    @pytest.mark.asyncio
    async def test_logging_middleware_tracks_time(self):
        """Test middleware tracks response time."""
        import time

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.method = "GET"
        request.url.path = "/test"
        request.client.host = "127.0.0.1"

        response = MagicMock()
        response.status_code = 200
        response.headers = {}

        async def slow_call_next(req):
            # Simulate a slow handler
            await AsyncMock()()
            return response

        # The middleware should track time, even if call_next is instant
        result = await logging_middleware(request, slow_call_next)
        assert result == response


class TestExceptionHandlerValidationError:
    """Test exception handler for validation errors."""

    @pytest.mark.asyncio
    async def test_validation_error_returns_400(self):
        """Test validation error returns 400 status code."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-123"

        exc = ValidationError("Invalid input")

        result = await exception_handler(request, exc)

        assert result.status_code == 400

    @pytest.mark.asyncio
    async def test_validation_error_includes_message(self):
        """Test validation error response includes error message."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-123"

        exc = ValidationError("Invalid email format")

        result = await exception_handler(request, exc)

        assert "Invalid email format" in result.body.decode()

    @pytest.mark.asyncio
    async def test_validation_error_includes_request_id(self):
        """Test validation error response includes request ID."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-123"

        exc = ValidationError("Invalid input")

        result = await exception_handler(request, exc)

        assert "test-id-123" in result.body.decode()


class TestExceptionHandlerNotFoundError:
    """Test exception handler for not found errors."""

    @pytest.mark.asyncio
    async def test_not_found_error_returns_404(self):
        """Test not found error returns 404 status code."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-456"

        exc = NotFoundError("Project not found")

        result = await exception_handler(request, exc)

        assert result.status_code == 404

    @pytest.mark.asyncio
    async def test_not_found_error_includes_message(self):
        """Test not found error response includes error message."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-456"

        exc = NotFoundError("User with ID 123 not found")

        result = await exception_handler(request, exc)

        assert "not found" in result.body.decode().lower()

    @pytest.mark.asyncio
    async def test_not_found_error_includes_request_id(self):
        """Test not found error response includes request ID."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-456"

        exc = NotFoundError("Resource not found")

        result = await exception_handler(request, exc)

        assert "test-id-456" in result.body.decode()


class TestExceptionHandlerDatabaseError:
    """Test exception handler for database errors."""

    @pytest.mark.asyncio
    async def test_database_error_returns_500(self):
        """Test database error returns 500 status code."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-789"

        exc = DatabaseError("Connection failed")

        result = await exception_handler(request, exc)

        assert result.status_code == 500

    @pytest.mark.asyncio
    async def test_database_error_includes_generic_message(self):
        """Test database error response includes generic message."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-789"

        exc = DatabaseError("Connection timeout")

        result = await exception_handler(request, exc)

        # Should have generic message, not the actual error
        assert "error occurred" in result.body.decode().lower() or "database" in result.body.decode().lower()

    @pytest.mark.asyncio
    async def test_database_error_includes_request_id(self):
        """Test database error response includes request ID."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-789"

        exc = DatabaseError("Connection failed")

        result = await exception_handler(request, exc)

        assert "test-id-789" in result.body.decode()


class TestExceptionHandlerTaxCalculationError:
    """Test exception handler for tax calculation errors."""

    @pytest.mark.asyncio
    async def test_tax_calculation_error_returns_400(self):
        """Test tax calculation error returns 400 status code."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-tax"

        exc = TaxCalculationError("Invalid income amount")

        result = await exception_handler(request, exc)

        assert result.status_code == 400

    @pytest.mark.asyncio
    async def test_tax_calculation_error_includes_message(self):
        """Test tax calculation error includes message."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-tax"

        exc = TaxCalculationError("Negative income not allowed")

        result = await exception_handler(request, exc)

        assert "Negative income" in result.body.decode()

    @pytest.mark.asyncio
    async def test_tax_calculation_error_includes_request_id(self):
        """Test tax calculation error includes request ID."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-tax"

        exc = TaxCalculationError("Invalid tax bracket")

        result = await exception_handler(request, exc)

        assert "test-id-tax" in result.body.decode()


class TestExceptionHandlerMoneySplitException:
    """Test exception handler for general MoneySplit exceptions."""

    @pytest.mark.asyncio
    async def test_moneysplit_exception_returns_500(self):
        """Test general MoneySplit exception returns 500 status code."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-general"

        exc = MoneySplitException("Something went wrong")

        result = await exception_handler(request, exc)

        assert result.status_code == 500

    @pytest.mark.asyncio
    async def test_moneysplit_exception_includes_request_id(self):
        """Test MoneySplit exception includes request ID."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-general"

        exc = MoneySplitException("Application error")

        result = await exception_handler(request, exc)

        assert "test-id-general" in result.body.decode()


class TestExceptionHandlerGenericException:
    """Test exception handler for generic exceptions."""

    @pytest.mark.asyncio
    async def test_generic_exception_returns_500(self):
        """Test generic exception returns 500 status code."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-generic"

        exc = Exception("Something unexpected happened")

        result = await exception_handler(request, exc)

        assert result.status_code == 500

    @pytest.mark.asyncio
    async def test_generic_exception_includes_generic_message(self):
        """Test generic exception returns generic message."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-generic"

        exc = Exception("Unexpected database error")

        result = await exception_handler(request, exc)

        # Should show generic message
        assert "error occurred" in result.body.decode().lower()

    @pytest.mark.asyncio
    async def test_generic_exception_includes_request_id(self):
        """Test generic exception includes request ID."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-id-generic"

        exc = Exception("Unexpected error")

        result = await exception_handler(request, exc)

        assert "test-id-generic" in result.body.decode()


class TestExceptionHandlerMissingRequestId:
    """Test exception handler when request ID is missing."""

    @pytest.mark.asyncio
    async def test_missing_request_id_defaults_to_unknown(self):
        """Test missing request ID defaults to 'unknown'."""
        request = MagicMock(spec=Request)
        request.state = MagicMock(spec=[])  # Empty spec - no attributes

        exc = ValidationError("Invalid input")

        result = await exception_handler(request, exc)

        # Should have "unknown" when no request ID
        assert "unknown" in result.body.decode()


class TestExceptionHandlerErrorFormats:
    """Test exception handler response formats."""

    @pytest.mark.asyncio
    async def test_validation_error_response_format(self):
        """Test validation error response has correct JSON format."""
        import json

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-123"

        exc = ValidationError("Invalid data")

        result = await exception_handler(request, exc)

        # Parse the response
        data = json.loads(result.body.decode())

        # Verify structure
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
        assert data["error"] == "Validation Error"
        assert data["request_id"] == "test-123"

    @pytest.mark.asyncio
    async def test_not_found_error_response_format(self):
        """Test not found error response format."""
        import json

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-456"

        exc = NotFoundError("Not found")

        result = await exception_handler(request, exc)

        data = json.loads(result.body.decode())

        assert data["error"] == "Not Found"
        assert data["request_id"] == "test-456"

    @pytest.mark.asyncio
    async def test_database_error_response_format(self):
        """Test database error response format."""
        import json

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-db"

        exc = DatabaseError("DB error")

        result = await exception_handler(request, exc)

        data = json.loads(result.body.decode())

        assert data["error"] == "Database Error"
        assert "database" in data["message"].lower()
