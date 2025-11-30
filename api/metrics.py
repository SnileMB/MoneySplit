"""
Prometheus metrics for MoneySplit API.
Tracks request metrics, latencies, and application statistics.
"""

from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter(
    "moneysplit_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "moneysplit_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

request_size = Histogram(
    "moneysplit_request_size_bytes",
    "Request size in bytes",
    ["method", "endpoint"],
)

response_size = Histogram(
    "moneysplit_response_size_bytes",
    "Response size in bytes",
    ["method", "endpoint", "status"],
)

# Error metrics
error_count = Counter(
    "moneysplit_errors_total",
    "Total number of errors",
    ["type", "endpoint"],
)

# Business logic metrics
projects_created = Counter(
    "moneysplit_projects_created_total",
    "Total number of projects created",
)

tax_calculations = Counter(
    "moneysplit_tax_calculations_total",
    "Total number of tax calculations performed",
    ["country", "tax_type"],
)

# Database metrics
db_query_duration = Histogram(
    "moneysplit_db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)

db_records_total = Gauge(
    "moneysplit_db_records_total",
    "Total number of records in database",
)

db_people_total = Gauge(
    "moneysplit_db_people_total",
    "Total number of people in database",
)

# Application metrics
active_requests = Gauge(
    "moneysplit_active_requests",
    "Number of currently active requests",
    ["method"],
)


def track_request(method: str, endpoint: str, status: int, duration: float):
    """Track a completed request."""
    request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def track_error(error_type: str, endpoint: str):
    """Track an error occurrence."""
    error_count.labels(type=error_type, endpoint=endpoint).inc()


def track_project_created():
    """Track a newly created project."""
    projects_created.inc()


def track_tax_calculation(country: str, tax_type: str):
    """Track a tax calculation."""
    tax_calculations.labels(country=country, tax_type=tax_type).inc()


def track_db_query(operation: str, duration: float):
    """Track a database query."""
    db_query_duration.labels(operation=operation).observe(duration)
