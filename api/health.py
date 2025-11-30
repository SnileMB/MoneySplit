"""
Health check endpoints for MoneySplit API.
Provides liveness, readiness, and detailed status information.
"""

import os
import psutil
import time
from datetime import datetime
from typing import Dict, Any
from DB import setup

# Track application start time
_start_time = time.time()


def get_uptime() -> float:
    """Get application uptime in seconds."""
    return time.time() - _start_time


def get_system_info() -> Dict[str, Any]:
    """Get system resource information."""
    process = psutil.Process(os.getpid())

    return {
        "cpu_percent": process.cpu_percent(interval=0.1),
        "memory_mb": process.memory_info().rss / (1024 * 1024),
        "memory_percent": process.memory_percent(),
        "open_files": len(process.open_files()),
        "threads": process.num_threads(),
    }


def check_database() -> Dict[str, Any]:
    """Check database connectivity and basic stats."""
    try:
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Count records
        cursor.execute("SELECT COUNT(*) FROM tax_records")
        record_count = cursor.fetchone()[0]

        # Count people
        cursor.execute("SELECT COUNT(*) FROM people")
        people_count = cursor.fetchone()[0]

        conn.close()

        return {
            "status": "healthy",
            "records_count": record_count,
            "people_count": people_count,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def get_health_status() -> Dict[str, Any]:
    """Get basic health status (liveness probe)."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": get_uptime(),
        "version": "1.0.0",
    }


async def get_ready_status() -> Dict[str, Any]:
    """Get detailed readiness status (readiness probe)."""
    database_health = check_database()
    system_info = get_system_info()

    is_ready = database_health["status"] == "healthy"

    return {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": get_uptime(),
        "database": database_health,
        "system": system_info,
    }


async def get_detailed_status() -> Dict[str, Any]:
    """Get comprehensive health and status information."""
    database_health = check_database()
    system_info = get_system_info()

    # Determine overall health
    is_healthy = database_health["status"] == "healthy"
    memory_ok = system_info["memory_percent"] < 90
    cpu_ok = system_info["cpu_percent"] < 95

    overall_status = "healthy" if (is_healthy and memory_ok and cpu_ok) else "degraded"

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": overall_status,
        "uptime_seconds": get_uptime(),
        "database": database_health,
        "system": {
            **system_info,
            "cpu_status": "ok" if cpu_ok else "high",
            "memory_status": "ok" if memory_ok else "high",
        },
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }
