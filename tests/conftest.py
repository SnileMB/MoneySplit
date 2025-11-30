"""Pytest configuration and fixtures."""

import pytest
import os
import sys
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Use same database as production for school project
# os.environ['TESTING'] = '1'
# os.environ['TEST_DB'] = 'test_example.db'


@pytest.fixture(scope="session", autouse=True)
def test_database():
    """Use production database for school project."""
    # No test database setup - using production database
    yield "example.db"


@pytest.fixture
def sample_project_data():
    """Provide sample project data for tests."""
    return {
        "num_people": 2,
        "revenue": 10000,
        "costs": [1000, 500, 300],
        "country": "US",
        "tax_type": "Individual",
        "people": [
            {"name": "Alice", "work_share": 0.6},
            {"name": "Bob", "work_share": 0.4},
        ],
    }


@pytest.fixture
def sample_tax_brackets():
    """Provide sample tax brackets for tests."""
    return [
        {"min": 0, "max": 11000, "rate": 0.10},
        {"min": 11000, "max": 44725, "rate": 0.12},
        {"min": 44725, "max": 95375, "rate": 0.22},
        {"min": 95375, "max": 182100, "rate": 0.24},
    ]
