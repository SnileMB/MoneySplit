"""
API Middleware for MoneySplit.
Handles logging, error handling, and request/response tracking.
"""

import time
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from typing import Callable
from exceptions import (
    MoneySplitException,
    ValidationError,
    DatabaseError,
    TaxCalculationError,
    NotFoundError,
)

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> JSONResponse:
    """
    Middleware to log all requests and responses with timing information.
    Adds request ID for tracing.
    """
    # Generate request ID for tracing
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log request
    logger.info(
        f"Incoming request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        },
    )

    # Track response time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    # Log response
    logger.info(
        f"Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": f"{process_time:.3f}s",
        },
    )

    return response


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler that converts exceptions to appropriate HTTP responses.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # Handle custom MoneySplit exceptions
    if isinstance(exc, ValidationError):
        logger.warning(
            f"Validation error: {str(exc)}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation Error",
                "message": str(exc),
                "request_id": request_id,
            },
        )

    elif isinstance(exc, NotFoundError):
        logger.warning(
            f"Resource not found: {str(exc)}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": str(exc),
                "request_id": request_id,
            },
        )

    elif isinstance(exc, DatabaseError):
        logger.error(
            f"Database error: {str(exc)}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database Error",
                "message": "An error occurred while accessing the database",
                "request_id": request_id,
            },
        )

    elif isinstance(exc, TaxCalculationError):
        logger.error(
            f"Tax calculation error: {str(exc)}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "Tax Calculation Error",
                "message": str(exc),
                "request_id": request_id,
            },
        )

    elif isinstance(exc, MoneySplitException):
        logger.error(
            f"Application error: {str(exc)}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Application Error",
                "message": str(exc),
                "request_id": request_id,
            },
        )

    # Handle generic exceptions
    else:
        logger.critical(
            f"Unhandled exception: {str(exc)}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            },
        )
