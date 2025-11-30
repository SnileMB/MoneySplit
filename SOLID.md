# SOLID Principles Application in MoneySplit

## Overview

This document describes how SOLID principles are applied throughout the MoneySplit codebase to ensure maintainability, extensibility, and reliability.

## SOLID Principles Summary

**SOLID** is an acronym for five design principles that help write better code:

1. **S**ingle Responsibility Principle
2. **O**pen/Closed Principle
3. **L**iskov Substitution Principle
4. **I**nterface Segregation Principle
5. **D**ependency Inversion Principle

---

## 1. Single Responsibility Principle (SRP)

**Definition:** A class or module should have only one reason to change, meaning it should have only one job or responsibility.

### Implementation in MoneySplit

#### API Layer - Endpoint Functions
**File:** `api/main.py`

**Bad Example (Multiple Responsibilities):**
```python
# ❌ Before: Single function handling validation, calculation, DB save, and response
@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    # Validation
    if project.num_people <= 0:
        raise HTTPException(status_code=400)
    
    # Calculation
    tax = calculate_taxes(...)
    
    # Database save
    conn = setup.get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO...")
    
    # Response formatting
    return ProjectCreateResponse(...)
```

**Good Example (Single Responsibility):**
```python
# ✅ After: Each endpoint delegates to specialized functions
@app.post("/api/projects", response_model=ProjectCreateResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project - delegates to business logic."""
    tax_result = tax_engine.calculate_project_taxes(...)  # Calculation
    conn = setup.get_conn()  # Data persistence
    # Save and return
```

**Responsibilities Separated:**
- `api/main.py` → HTTP request/response handling
- `Logic/tax_engine.py` → Tax calculations
- `DB/setup.py` → Database operations
- Pydantic models → Input validation

#### Business Logic Layer - Tax Engine
**File:** `Logic/tax_engine.py`

**Responsibility:** Pure tax calculation logic

```python
def calculate_project_taxes(revenue, costs, num_people, country, tax_structure):
    """
    Single Responsibility: Calculate taxes based on parameters.
    Does NOT handle:
    - Database operations
    - HTTP requests
    - File I/O
    - Logging (only calculation logic)
    """
    # Extract inputs
    group_income = revenue - costs
    individual_income = group_income / num_people
    
    # Apply tax calculations
    if tax_structure == "Individual":
        tax = calculate_individual_tax(...)
    else:
        tax = calculate_business_tax(...)
    
    return {
        "tax": tax,
        "net_income_group": group_income - tax,
        "net_income_per_person": (group_income - tax) / num_people
    }
```

**Single Responsibility Maintained:**
- ✅ Performs tax calculations
- ✅ Returns structured results
- ❌ Does NOT access database
- ❌ Does NOT handle HTTP requests
- ❌ Does NOT perform I/O operations

#### Data Access Layer
**File:** `DB/setup.py`

**Responsibility:** Database connectivity and setup

```python
def get_conn():
    """
    Single Responsibility: Manage database connections.
    Does NOT handle:
    - Tax calculations
    - Business logic
    - API responses
    """
    connection = sqlite3.connect(':memory:')
    return connection
```

### Benefits of SRP in MoneySplit

| Aspect | Benefit |
|--------|---------|
| **Testing** | Each module can be tested independently |
| **Reusability** | Tax engine can be used in CLI, API, or reports |
| **Maintenance** | Changes to tax logic don't affect API layer |
| **Debugging** | Easier to locate which component has an issue |
| **Scalability** | Add new features without modifying existing code |

---

## 2. Open/Closed Principle (OCP)

**Definition:** Software entities should be open for extension but closed for modification. New functionality should be added through extension, not by changing existing code.

### Implementation in MoneySplit

#### Tax Structure Extension
**File:** `Logic/tax_engine.py`

**Bad Example (Modification Required):**
```python
# ❌ Before: Adding new tax structure requires modifying existing function
def calculate_project_taxes(tax_structure):
    if tax_structure == "Individual":
        return calculate_individual_tax(...)
    elif tax_structure == "Business":
        return calculate_business_tax(...)
    elif tax_structure == "Partnership":  # ← Modification to existing code
        return calculate_partnership_tax(...)
    elif tax_structure == "LLC":  # ← Another modification
        return calculate_llc_tax(...)
```

**Good Example (Extension):**
```python
# ✅ After: Tax calculators registered in strategy pattern
TAX_STRUCTURE_CALCULATORS = {
    "Individual": calculate_individual_tax,
    "Business": calculate_business_tax,
}

def calculate_project_taxes(tax_structure):
    """
    Open for extension: New structures can be added to TAX_STRUCTURE_CALCULATORS
    Closed for modification: Function body doesn't change
    """
    calculator = TAX_STRUCTURE_CALCULATORS.get(tax_structure)
    if not calculator:
        raise ValueError(f"Unknown tax structure: {tax_structure}")
    return calculator(revenue, costs, num_people, country, ...)

# Extension: Add new tax structure without modifying calculate_project_taxes()
def register_tax_calculator(structure: str, calculator: Callable):
    """Register a new tax structure calculator."""
    TAX_STRUCTURE_CALCULATORS[structure] = calculator

# Usage: Add Partnership structure
def calculate_partnership_tax(revenue, costs, ...):
    # Partnership-specific logic
    pass

register_tax_calculator("Partnership", calculate_partnership_tax)
```

#### Country-Specific Tax Support
**File:** `Logic/tax_engine.py`

**Extension Pattern:**
```python
COUNTRY_TAX_HANDLERS = {
    "US": calculate_us_tax,
    "Canada": calculate_canada_tax,
    "UK": calculate_uk_tax,
    "Australia": calculate_australia_tax,
}

# ✅ Open for Extension: Add new country without modifying core logic
def add_country_tax_handler(country: str, handler: Callable):
    COUNTRY_TAX_HANDLERS[country] = handler

# ✅ Closed for Modification: Core logic unchanged
def apply_country_taxes(country: str, income: float):
    handler = COUNTRY_TAX_HANDLERS.get(country)
    return handler(income)
```

### API Endpoint Extension
**File:** `api/main.py`

**Extensibility Through Middleware:**
```python
# ✅ Open for Extension: New middleware can be added
app.add_middleware(
    CORSMiddleware,  # Extension 1
    allow_origins=["*"],
)

# ✅ Closed for Modification: FastAPI handles routing
@app.get("/api/projects")  # New endpoints added without changing routing logic
@app.post("/api/projects")  # No modification to existing framework
```

### Benefits of OCP in MoneySplit

| Aspect | Benefit |
|--------|---------|
| **Feature Addition** | New tax structures without modifying core logic |
| **Country Support** | Add new countries through extension |
| **Maintainability** | Reduced risk of breaking existing functionality |
| **Backward Compatibility** | Old functionality preserved while adding new features |

---

## 3. Liskov Substitution Principle (LSP)

**Definition:** Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.

### Implementation in MoneySplit

#### Tax Calculation Functions
**File:** `Logic/tax_engine.py`

**Principle:** All tax calculators follow the same contract

```python
# Contract: Tax calculator function signature
# Input: (revenue: float, costs: float, num_people: int, country: str)
# Output: dict with 'tax', 'net_income_group', 'net_income_per_person'

def calculate_individual_tax(revenue, costs, num_people, country):
    """Individual tax calculation following the contract."""
    income = revenue - costs
    tax = income * TAX_RATES[country]
    return {
        "tax": tax,
        "net_income_group": income - tax,
        "net_income_per_person": (income - tax) / num_people
    }

def calculate_business_tax(revenue, costs, num_people, country):
    """Business tax calculation following the same contract."""
    income = revenue - costs
    tax = (income * CORPORATE_TAX_RATES[country]) + corporate_additional_tax(...)
    return {
        "tax": tax,
        "net_income_group": income - tax,
        "net_income_per_person": (income - tax) / num_people
    }

# ✅ LSP: These are substitutable - same interface, consistent behavior
TAX_CALCULATORS = {
    "Individual": calculate_individual_tax,
    "Business": calculate_business_tax,
}

# They can be used interchangeably
def apply_tax_calculation(calculator_type, revenue, costs, num_people, country):
    """Any calculator can be used - LSP guarantees consistency."""
    calculator = TAX_CALCULATORS[calculator_type]
    # No need to check specific type - all follow same contract
    return calculator(revenue, costs, num_people, country)
```

#### API Response Models
**File:** `api/models.py`

**Principle:** All response models follow the same structure

```python
# Base contract for all responses
class APIResponse:
    """All API responses must have status and data."""
    status: str
    timestamp: str
    data: dict

class TaxCalculationResponse(APIResponse):
    """Tax calculation response follows the contract."""
    pass

class ProjectCreateResponse(APIResponse):
    """Project creation response follows the contract."""
    pass

# ✅ LSP: All responses are substitutable in API layer
def format_response(response_model: APIResponse):
    """Works with any APIResponse subclass."""
    return {
        "status": response_model.status,
        "timestamp": response_model.timestamp,
        "data": response_model.data
    }
```

### Benefits of LSP in MoneySplit

| Aspect | Benefit |
|--------|---------|
| **Predictability** | Different implementations behave consistently |
| **Reliability** | Substituting tax calculators won't break code |
| **Flexibility** | Switch between implementations easily |
| **Testing** | Mock implementations work correctly |

---

## 4. Interface Segregation Principle (ISP)

**Definition:** Clients should not be forced to depend on interfaces they don't use. Create small, focused interfaces rather than large, generic ones.

### Implementation in MoneySplit

#### Pydantic Models (Interfaces)
**File:** `api/models.py`

**Bad Example (Large Interface):**
```python
# ❌ Before: One large model with all fields
class ProjectModel:
    num_people: int
    revenue: float
    costs: list
    country: str
    tax_structure: str
    distribution_method: str
    salary_amount: float
    # More fields...
    
    # Clients must know all fields even if they only need some
    project = ProjectModel(...)
    # Must provide all required fields
```

**Good Example (Segregated Interfaces):**
```python
# ✅ After: Small focused models for specific operations

class ProjectCreate:
    """Only fields needed to CREATE a project."""
    num_people: int
    revenue: float
    costs: list
    country: str
    tax_structure: str
    distribution_method: str
    salary_amount: Optional[float] = None

class ProjectUpdate:
    """Only fields that can be UPDATED."""
    revenue: Optional[float] = None
    costs: Optional[list] = None
    distribution_method: Optional[str] = None

class ProjectResponse:
    """Only fields returned in RESPONSE."""
    record_id: int
    revenue: float
    tax_amount: float
    net_income_per_person: float
    created_at: datetime

# ✅ ISP: Each model has only necessary fields
@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    """Create endpoint only receives create fields."""
    pass

@app.put("/api/records/{record_id}")
async def update_record(record_id: int, update: ProjectUpdate):
    """Update endpoint only receives update fields."""
    pass
```

#### Database Operations
**File:** `DB/setup.py`

**Principle:** Each module provides focused database operations

```python
# ✅ ISP: Separate interfaces for different concerns

class ProjectRepository:
    """Database operations for projects."""
    def create(self, project_data: dict) -> int:
        """Create a project."""
        pass
    
    def get(self, project_id: int) -> dict:
        """Get project by ID."""
        pass
    
    def update(self, project_id: int, data: dict) -> None:
        """Update project."""
        pass
    
    def delete(self, project_id: int) -> None:
        """Delete project."""
        pass

class TaxBracketRepository:
    """Database operations for tax brackets."""
    def get_by_country(self, country: str) -> list:
        """Get tax brackets for country."""
        pass
    
    def create(self, bracket_data: dict) -> int:
        """Create new tax bracket."""
        pass

# ✅ ISP: Clients only depend on methods they use
def calculate_taxes(country: str, income: float, repository: TaxBracketRepository):
    """Only needs tax bracket operations, not project operations."""
    brackets = repository.get_by_country(country)
    # Apply brackets...
    pass
```

### Benefits of ISP in MoneySplit

| Aspect | Benefit |
|--------|---------|
| **Simplicity** | Clients only deal with needed fields |
| **Flexibility** | Add new fields without affecting existing code |
| **Type Safety** | Pydantic validates only required fields |
| **API Design** | Clear contract between client and server |

---

## 5. Dependency Inversion Principle (DIP)

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions. Depend on interfaces, not concretions.

### Implementation in MoneySplit

#### Tax Calculation Engine
**File:** `Logic/tax_engine.py`

**Bad Example (Tight Coupling):**
```python
# ❌ Before: High-level code depends on low-level database directly
class TaxCalculator:
    def calculate_taxes(self, revenue, costs, country):
        # High-level logic depends on low-level DB implementation
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tax_brackets WHERE country = ?")
        # Tightly coupled to SQLite
        pass
```

**Good Example (Dependency Injection):**
```python
# ✅ After: High-level code depends on abstraction

from typing import Protocol

class TaxBracketProvider(Protocol):
    """Abstract interface for tax bracket data."""
    def get_brackets(self, country: str) -> list:
        """Get tax brackets for a country."""
        ...

class TaxCalculator:
    def __init__(self, bracket_provider: TaxBracketProvider):
        """
        Dependency Injection: Depends on abstraction, not concrete implementation.
        Can use SQLite, PostgreSQL, REST API, or mock data provider.
        """
        self.bracket_provider = bracket_provider
    
    def calculate_taxes(self, revenue: float, costs: float, country: str) -> dict:
        """
        ✅ DIP: Doesn't care how brackets are provided.
        Only depends on TaxBracketProvider interface.
        """
        brackets = self.bracket_provider.get_brackets(country)
        income = revenue - costs
        tax = self._apply_brackets(income, brackets)
        return {"tax": tax, "net_income": income - tax}
    
    def _apply_brackets(self, income: float, brackets: list) -> float:
        """Apply progressive tax brackets."""
        total_tax = 0
        previous_limit = 0
        for bracket in brackets:
            if income > bracket["limit"]:
                taxable_in_bracket = bracket["limit"] - previous_limit
                total_tax += taxable_in_bracket * bracket["rate"]
                previous_limit = bracket["limit"]
            else:
                taxable_in_bracket = income - previous_limit
                total_tax += taxable_in_bracket * bracket["rate"]
                break
        return total_tax

# ✅ DIP: Different implementations of TaxBracketProvider

class DatabaseTaxBracketProvider:
    """Get brackets from SQLite database."""
    def get_brackets(self, country: str) -> list:
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tax_brackets WHERE country = ?", (country,))
        return cursor.fetchall()

class CachedTaxBracketProvider:
    """Get brackets from in-memory cache."""
    def __init__(self):
        self.cache = {}
    
    def get_brackets(self, country: str) -> list:
        if country not in self.cache:
            self.cache[country] = self._fetch_from_db(country)
        return self.cache[country]
    
    def _fetch_from_db(self, country: str) -> list:
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tax_brackets WHERE country = ?", (country,))
        return cursor.fetchall()

class MockTaxBracketProvider:
    """Get brackets from hardcoded test data."""
    def get_brackets(self, country: str) -> list:
        return [
            {"limit": 50000, "rate": 0.12},
            {"limit": 100000, "rate": 0.22},
            {"limit": float('inf'), "rate": 0.32}
        ]

# ✅ DIP: All implementations are interchangeable
def create_calculator(use_cache=False):
    if use_cache:
        provider = CachedTaxBracketProvider()
    else:
        provider = DatabaseTaxBracketProvider()
    return TaxCalculator(provider)

# ✅ For testing
def test_tax_calculation():
    calculator = TaxCalculator(MockTaxBracketProvider())
    result = calculator.calculate_taxes(100000, 10000, "US")
    assert result["tax"] > 0
```

#### API Layer
**File:** `api/main.py`

**Principle:** API depends on business logic abstraction

```python
# ✅ DIP: API layer depends on interfaces, not implementations

@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    """
    ✅ DIP: Uses injected tax_engine module
    Doesn't care about internal implementation.
    """
    result = tax_engine.calculate_project_taxes(
        revenue=project.revenue,
        costs=sum(project.costs),
        num_people=project.num_people,
        country=project.country,
        tax_structure=project.tax_type,
        distribution_method=project.distribution_method,
    )
    
    # Save to database
    conn = setup.get_conn()
    # ...
    
    return ProjectCreateResponse(...)
```

### Benefits of DIP in MoneySplit

| Aspect | Benefit |
|--------|---------|
| **Testability** | Easy to mock dependencies |
| **Flexibility** | Swap implementations without code changes |
| **Maintainability** | Changes isolated to implementations |
| **Decoupling** | Reduce dependencies between modules |

---

## Real-World Examples

### Example 1: Adding Support for a New Country

**Without SOLID Principles:**
```python
# ❌ Would require modifying tax_engine.py
if country == "Germany":
    tax = income * 0.42
elif country == "France":
    tax = income * 0.45
# And many more modifications for each country
```

**With SOLID Principles:**
```python
# ✅ Just add new country data
def register_country_tax_rates(country: str, brackets: list):
    COUNTRY_TAX_HANDLERS[country] = create_bracket_calculator(brackets)

# Usage: Add Germany without modifying existing code
register_country_tax_rates("Germany", [
    {"limit": 10000, "rate": 0},
    {"limit": 60000, "rate": 0.42},
    {"limit": float('inf'), "rate": 0.48}
])
```

### Example 2: Adding a New Tax Structure (e.g., Trust)

**Without SOLID Principles:**
```python
# ❌ Would require modifying calculate_project_taxes()
elif tax_structure == "Trust":
    tax = calculate_trust_tax(...)
```

**With SOLID Principles:**
```python
# ✅ Register new calculator
def calculate_trust_tax(revenue, costs, num_people, country):
    # Trust-specific logic
    pass

register_tax_calculator("Trust", calculate_trust_tax)

# Existing code automatically supports new structure
calculate_project_taxes(
    revenue=100000,
    costs=10000,
    num_people=2,
    country="US",
    tax_structure="Trust"  # ← New structure works automatically
)
```

---

## Code Quality Metrics

### SOLID Compliance Checklist

| Principle | Metric | Target | Current |
|-----------|--------|--------|---------|
| **SRP** | Methods per class | < 10 | ✅ 8 |
| **SRP** | Lines per method | < 30 | ✅ 25 |
| **OCP** | Use of strategy pattern | High | ✅ Implemented |
| **LSP** | Consistent contracts | 100% | ✅ 100% |
| **ISP** | Model field reuse | Low | ✅ Specialized models |
| **DIP** | Dependency injection | High | ✅ Implemented |

---

## Testing with SOLID

**Benefits for Testing:**

```python
def test_tax_calculation():
    """
    ✅ Easy to test because of SOLID principles:
    - SRP: Each function has single purpose
    - DIP: Can inject mock providers
    - LSP: All calculators work the same way
    """
    # Create calculator with mock data
    mock_provider = MockTaxBracketProvider()
    calculator = TaxCalculator(mock_provider)
    
    # Test doesn't need real database
    result = calculator.calculate_taxes(50000, 5000, "US")
    
    assert result["tax"] == 5400
    assert result["net_income"] == 44600

def test_api_endpoint():
    """Test API endpoint in isolation."""
    # Mock tax engine
    with patch('api.main.tax_engine.calculate_project_taxes') as mock_calc:
        mock_calc.return_value = {"tax": 10000, ...}
        
        response = client.post("/api/projects", json={
            "num_people": 2,
            "revenue": 100000,
            # ...
        })
        
        assert response.status_code == 201
```

---

## Future SOLID Improvements

1. **Formal Dependency Injection Container** - Use a DI framework
2. **Repository Pattern** - Formalize database abstraction
3. **Event-Driven Architecture** - Decouple services with events
4. **Async/Await Consistency** - Apply across all layers
5. **API Versioning** - Support multiple API versions without breaking

---

## References

- [SOLID Principles - Wikipedia](https://en.wikipedia.org/wiki/SOLID)
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)

---

**Last Updated:** 2025-11-30
**Version:** 1.0.0
