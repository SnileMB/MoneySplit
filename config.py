"""
Configuration module for MoneySplit application.
Centralizes hardcoded values, magic numbers, and environment-specific settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# API Configuration
# ============================================================================
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", 8000))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
API_URL = f"http://{API_HOST}:{API_PORT}"

# Frontend configuration
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "localhost")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", 3000))
FRONTEND_URL = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"

# CORS settings
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")

# ============================================================================
# Database Configuration
# ============================================================================
DB_PATH = os.getenv("DB_PATH", "example.db")
DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", 5))

# ============================================================================
# Tax Configuration Constants
# ============================================================================

# US Tax Constants
US_STANDARD_DEDUCTION_2024 = 13850  # Single filer
US_STANDARD_DEDUCTION_MFJ_2024 = 27700  # Married filing jointly

# Self-Employment Tax Rates (2024)
SE_TAX_RATE = 0.153  # 15.3% (12.4% Social Security + 2.9% Medicare)
SE_SOCIAL_SECURITY_RATE = 0.124  # 12.4%
SE_MEDICARE_RATE = 0.029  # 2.9%
SE_SOCIAL_SECURITY_WAGE_BASE = 168600  # 2024

# Deductions and Credits
SE_DEDUCTION_PERCENTAGE = 0.5  # Can deduct 50% of SE tax
QUALIFIED_BUSINESS_INCOME_DEDUCTION = 0.20  # 20% QBI deduction

# Dividend Tax Rates
LONG_TERM_CAPITAL_GAINS_RATE_15 = 0.15  # 15% for most
LONG_TERM_CAPITAL_GAINS_RATE_20 = 0.20  # 20% for high earners

# Corporate Tax
CORPORATE_TAX_RATE = 0.21  # Federal corporate tax rate

# State Tax Brackets (examples - would typically come from DB)
STATE_TAX_RATES = {
    "CA": 0.093,  # California
    "NY": 0.0685,  # New York
    "TX": 0.0,  # Texas (no state income tax)
    "FL": 0.0,  # Florida (no state income tax)
}

# ============================================================================
# Forecasting Configuration
# ============================================================================
FORECASTING_MIN_DATA_POINTS = 2
FORECASTING_MOVING_AVERAGE_WINDOW = 3
FORECAST_MONTHS_DEFAULT = 3
FORECAST_MONTHS_MAX = 24

# ============================================================================
# PDF Export Configuration
# ============================================================================
PDF_MARGIN_TOP = 40
PDF_MARGIN_BOTTOM = 40
PDF_MARGIN_LEFT = 40
PDF_MARGIN_RIGHT = 40
PDF_PAGE_WIDTH = 595
PDF_PAGE_HEIGHT = 842

# ============================================================================
# Application Settings
# ============================================================================
APP_NAME = "MoneySplit"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Commission-Based Income Splitting with Tax Calculations"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "app.log")

# ============================================================================
# Monitoring & Metrics
# ============================================================================
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
PROMETHEUS_METRICS_PORT = int(os.getenv("PROMETHEUS_METRICS_PORT", 8001))

# ============================================================================
# Validation Rules
# ============================================================================
MIN_REVENUE = 0.01
MAX_REVENUE = 999999999.99
MIN_PEOPLE = 1
MAX_PEOPLE = 1000
MIN_COST = 0.0
MAX_COST = 999999999.99

# Work share precision (2 decimal places minimum)
WORK_SHARE_DECIMALS = 2

# ============================================================================
# Error Messages
# ============================================================================
ERROR_RECORD_NOT_FOUND = "Record not found"
ERROR_INVALID_INPUT = "Invalid input provided"
ERROR_DATABASE_ERROR = "Database error occurred"
ERROR_CALCULATION_ERROR = "Calculation error occurred"
ERROR_FORECASTING_ERROR = "Unable to generate forecast"

# ============================================================================
# Success Messages
# ============================================================================
SUCCESS_RECORD_CREATED = "Record created successfully"
SUCCESS_RECORD_UPDATED = "Record updated successfully"
SUCCESS_RECORD_DELETED = "Record deleted successfully"
