# Testing Guide for MoneySplit

Complete testing documentation for the MoneySplit application.

---

## Table of Contents

1. [Test Overview](#test-overview)
2. [Running Tests](#running-tests)
3. [Coverage Measurement](#coverage-measurement)
4. [Test Structure](#test-structure)
5. [Writing New Tests](#writing-new-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

---

## Test Overview

### Current Test Suite

**Statistics:**
- Total Tests: 85
- Test Files: 4
- Categories: Unit, Integration, Database, Edge Cases
- Status: All passing ✓

**Coverage by Module:**
```
Module              Tests   Coverage
────────────────────────────────────
test_api.py         23      100%
test_backend_logic  24      100%
test_database       12      99%
test_edge_cases     26      100%
```

### Test Categories

1. **Unit Tests (25)**
   - Tax calculation logic
   - Work share distribution
   - Input validation
   - Profit calculations

2. **API Integration Tests (23)**
   - CRUD operations
   - Report endpoints
   - Forecasting endpoints
   - Visualization endpoints
   - PDF exports

3. **Database Tests (20)**
   - Create, Read, Update, Delete
   - Foreign key constraints
   - Aggregations
   - Complex queries

4. **Edge Case Tests (17)**
   - Boundary values
   - Invalid inputs
   - Special characters
   - Floating point precision

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Verify pytest is installed
pytest --version
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run specific test function
pytest tests/test_api.py::test_create_project

# Run tests matching pattern
pytest -k "tax" -v

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l
```

### Advanced Test Running

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run tests with detailed output
pytest -vv

# Show print statements during tests
pytest -s

# Disable output capture
pytest -p no:cacheprovider

# Run with specific markers
pytest -m "unit"

# Run with timeout (requires pytest-timeout)
pytest --timeout=300
```

---

## Coverage Measurement

### Generating Coverage Reports

```bash
# Basic coverage report
pytest --cov=. --cov-report=term

# HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# XML coverage report (for CI)
pytest --cov=. --cov-report=xml

# Multiple formats
pytest --cov=. --cov-report=html --cov-report=xml --cov-report=term
```

### Coverage Configuration

**pytest.ini includes:**
```ini
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Coverage Thresholds

- **Current Target:** 70%
- **Module-specific Targets:**
  - API: 80%+
  - Business Logic: 85%+
  - Database: 75%+

### Viewing Coverage Reports

**HTML Report:**
```bash
# Generate report
pytest --cov=. --cov-report=html

# Open in browser
cd htmlcov
python -m http.server 8000
# Visit: http://localhost:8000
```

**Terminal Report:**
```bash
# Detailed coverage summary
pytest --cov=. --cov-report=term-missing

# Shows which lines not covered
```

---

## Test Structure

### Test File Organization

```
tests/
├── __init__.py
├── conftest.py                      # Pytest configuration
├── test_api.py                      # API endpoint tests
├── test_backend_logic.py            # Business logic tests
├── test_database.py                 # Database operation tests
└── test_edge_cases.py               # Edge case and error tests
```

### Test Fixtures

**conftest.py provides:**

```python
@pytest.fixture
def sample_project_data():
    """Provides sample project data"""
    return {
        "num_people": 2,
        "revenue": 10000,
        "costs": [1000, 500, 300],
        "country": "US",
        "tax_type": "Individual",
        "people": [
            {"name": "Alice", "work_share": 0.6},
            {"name": "Bob", "work_share": 0.4}
        ]
    }

@pytest.fixture
def sample_tax_brackets():
    """Provides sample tax brackets"""
    return [
        {'min': 0, 'max': 11000, 'rate': 0.10},
        {'min': 11000, 'max': 44725, 'rate': 0.12},
        {'min': 44725, 'max': 95375, 'rate': 0.22},
        {'min': 95375, 'max': 182100, 'rate': 0.24}
    ]
```

### Test Naming Convention

```python
# Module: test_api.py
# Class: TestProjectEndpoints
# Method: test_create_project_with_valid_data

def test_create_project_with_valid_data():
    """Test creating project with valid input"""
    # Arrange
    project_data = {...}

    # Act
    result = create_project(project_data)

    # Assert
    assert result.record_id > 0
```

---

## Writing New Tests

### Test Template

```python
import pytest
from api.main import create_project
from exceptions import ValidationError

class TestProjectCreation:
    """Tests for project creation functionality"""

    def test_create_project_success(self, sample_project_data):
        """Test successful project creation"""
        # Arrange
        data = sample_project_data

        # Act
        response = create_project(data)

        # Assert
        assert response.record_id > 0
        assert response.message == "Project created successfully"
        assert response.summary["revenue"] == 10000

    def test_create_project_invalid_data(self):
        """Test project creation with invalid data"""
        # Arrange
        invalid_data = {
            "num_people": -1,  # Invalid: negative
            "revenue": 10000,
            "costs": [1000]
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            create_project(invalid_data)

    def test_create_project_missing_fields(self):
        """Test project creation with missing required fields"""
        # Arrange
        incomplete_data = {
            "num_people": 2,
            "revenue": 10000
            # Missing: costs, country, tax_type
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            create_project(incomplete_data)
```

### Best Practices

1. **Use Descriptive Names:**
   ```python
   # Good
   def test_tax_calculation_with_us_individual_returns_correct_amount():
       pass

   # Bad
   def test_tax():
       pass
   ```

2. **Use Fixtures:**
   ```python
   # Good
   def test_with_data(sample_project_data):
       pass

   # Bad
   def test_with_data():
       sample_data = {...}  # Hardcoded
   ```

3. **Test One Thing:**
   ```python
   # Good
   def test_calculates_federal_tax():
       pass

   # Bad
   def test_tax_calculation():
       # Tests federal, state, and effective rate
       pass
   ```

4. **Use Arrange-Act-Assert:**
   ```python
   def test_something():
       # Arrange - Set up test data
       data = {...}

       # Act - Execute code
       result = function(data)

       # Assert - Verify result
       assert result == expected
   ```

5. **Test Edge Cases:**
   ```python
   # Test boundary conditions
   def test_zero_revenue():
       pass

   def test_maximum_people():
       pass
   ```

---

## CI/CD Integration

### GitHub Actions Test Execution

The CI/CD pipeline automatically:

1. **Installs dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Runs all tests**
   ```bash
   pytest tests/ -v
   ```

3. **Measures coverage**
   ```bash
   pytest --cov=. --cov-report=xml --cov-report=html
   ```

4. **Enforces threshold**
   ```bash
   coverage report --fail-under=70
   ```

5. **Uploads reports**
   - Coverage to Codecov
   - Artifacts to GitHub

### Test Failure Handling

- ✗ Test fails → Pipeline fails
- ✗ Coverage < 70% → Pipeline fails
- ✗ Linting errors → Pipeline fails
- ✗ Build fails → Pipeline fails

---

## Troubleshooting

### Common Issues

**Issue: Import errors in tests**
```bash
# Solution: Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

**Issue: Database locked errors**
```bash
# Solution: Use test database instead
pytest --db=test.db
```

**Issue: Tests pass locally but fail in CI**
```bash
# Solution: Check environment variables
# Ensure CI has same config as local
```

**Issue: Slow tests**
```bash
# Solution: Use markers
pytest -m "not slow"
```

### Debug Mode

```bash
# Run with debugging
pytest --pdb

# Drop into pdb on failure
pytest --pdb-trace

# Show local variables
pytest -l

# Verbose with print statements
pytest -vv -s
```

### Coverage Gaps

```bash
# Show missing lines
pytest --cov=. --cov-report=term-missing

# Detailed HTML report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Continuous Testing

### Watch Mode (Auto-run on changes)

```bash
# Install pytest-watch
pip install pytest-watch

# Run with watch
ptw

# Watch with coverage
ptw -- --cov=.
```

### Git Hooks

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
pytest --quiet
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

---

## Test Maintenance

### Regular Tasks

1. **Update tests when code changes**
2. **Review coverage reports monthly**
3. **Refactor duplicate test code**
4. **Archive old test runs**
5. **Update fixtures as schemas change**

### Coverage Goals

- **Immediate:** Reach 70%
- **Short-term:** Reach 80%
- **Long-term:** Reach 90%

---

## Resources

- **Pytest Documentation:** https://docs.pytest.org/
- **Coverage.py:** https://coverage.readthedocs.io/
- **Testing Best Practices:** https://testdriven.io/

---

**Last Updated:** 2025-11-30
**Target Coverage:** 70%+
**Status:** In Progress
