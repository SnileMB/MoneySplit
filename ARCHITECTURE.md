# MoneySplit Architecture Documentation

## Overview

MoneySplit is a full-stack application for commission-based income splitting with comprehensive tax calculations, analytics, and reporting. The system is designed with a clear separation between backend API, frontend interface, and database layer.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│                   (Port 3000)                                │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼──────────────┐
        │  API Gateway / Reverse    │
        │  Proxy (if needed)        │
        └────────────┬──────────────┘
                     │
┌────────────────────▼──────────────────────────────────────┐
│              FastAPI Backend                               │
│              (Port 8000)                                   │
│  ├─ API Endpoints (/api/*)                                │
│  ├─ Health Checks (/health, /health/ready, /health/live) │
│  ├─ Metrics (/metrics)                                    │
│  └─ Visualizations (/api/visualizations/*)               │
└────────────────────┬──────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────────┐
│Database │   │Monitoring│   │Tax Engine &  │
│(SQLite) │   │(Prometheus) │ Logic Layer │
│         │   │(Grafana)    │             │
└─────────┘   └──────────┘   └──────────────┘
```

## Architecture Layers

### 1. Frontend Layer (React)
**Location:** `/frontend/src`

**Responsibilities:**
- User interface and user experience
- Interactive dashboards and visualizations
- Form handling and data collection
- Real-time updates via API calls

**Key Features:**
- React components for project management
- Tax visualization and comparison tools
- Export functionality (PDF, CSV)
- Analytics and reporting dashboard

### 2. API Layer (FastAPI)
**Location:** `/api/main.py` and supporting modules

**Responsibilities:**
- RESTful API endpoints for all business operations
- Request validation and error handling
- Authentication and authorization (if applicable)
- Response formatting and CORS handling

**Key Endpoints:**
- `/api/projects` - Project CRUD operations
- `/api/records` - Record management
- `/api/tax-brackets` - Tax bracket configuration
- `/api/reports/*` - Analytics and reporting
- `/api/visualizations/*` - Dynamic chart generation
- `/api/export/*` - PDF/CSV export
- `/health*` - Health check endpoints
- `/metrics` - Prometheus metrics

**Middleware:**
- CORS middleware for cross-origin requests
- Prometheus middleware for metrics collection

### 3. Business Logic Layer
**Location:** `/Logic/`

**Components:**

#### tax_engine.py
- **Purpose:** Core tax calculation engine
- **Functions:**
  - `calculate_project_taxes()` - Main calculation function
  - `calculate_individual_tax()` - Individual-specific calculations
  - `calculate_business_tax()` - Business tax calculations
  - Supports multiple countries (US, Canada, UK, Australia)
  - Implements different distribution methods (Salary, Dividend, Mixed)

#### forecasting.py
- **Purpose:** Revenue and tax forecasting
- **Functions:**
  - Predict future revenue trends
  - Forecast tax impacts
  - Trend analysis

#### tax_comparison.py
- **Purpose:** Compare different tax strategies
- **Functions:**
  - Compare individual vs. business structures
  - Evaluate salary vs. dividend distributions
  - Optimize tax outcomes

#### pdf_generator.py
- **Purpose:** Generate PDF reports
- **Functions:**
  - Tax calculation reports
  - Summary reports
  - Forecasting reports

### 4. Data Access Layer
**Location:** `/DB/`

**Components:**

#### setup.py
- **Purpose:** Database initialization and connection management
- **Functions:**
  - `get_conn()` - Get database connection
  - Database schema creation
  - Data migration

#### models.py
- **Purpose:** SQLite table definitions and schema
- **Tables:**
  - `tax_records` - Project and tax calculation records
  - `tax_brackets` - Tax bracket configurations
  - `people` - Individual person records
  - `tax_history` - Historical tax data

### 5. Monitoring & Observability
**Location:** `/monitoring/`

**Components:**

#### Prometheus
- **Metrics collected:**
  - HTTP request rate, latency, error rate
  - Database operation metrics
  - Tax calculation metrics
  - Business metrics (projects created, etc.)

#### Grafana
- **Dashboard:** MoneySplit Monitoring Dashboard
- **Panels:**
  - Request rate and latency
  - Error tracking
  - Database performance
  - Business metrics

#### Health Checks
- **Endpoints:**
  - `/health` - Basic health status
  - `/health/ready` - Readiness probe (database connectivity)
  - `/health/live` - Liveness probe (process alive)

## Data Models

### Tax Record
```python
{
    "record_id": int,
    "num_people": int,
    "revenue": float,
    "total_costs": float,
    "group_income": float,
    "individual_income": float,
    "tax_origin": str,  # Country
    "tax_option": str,  # Tax structure type
    "tax_amount": float,
    "net_income_per_person": float,
    "net_income_group": float,
    "distribution_method": str,
    "salary_amount": float
}
```

### Tax Bracket
```python
{
    "bracket_id": int,
    "country": str,
    "income_min": float,
    "income_max": float,
    "tax_rate": float
}
```

### Person
```python
{
    "person_id": int,
    "name": str,
    "percentage": float,
    "revenue_assigned": float
}
```

## API Request Flow

```
1. Frontend sends HTTP request
   ├─ Includes authentication headers (if applicable)
   └─ Includes request payload (JSON)

2. FastAPI server receives request
   ├─ CORS middleware validates origin
   ├─ Prometheus middleware records metrics
   └─ Route handler processes request

3. Route handler processes business logic
   ├─ Validates input using Pydantic models
   ├─ Calls business logic layer (Logic/)
   └─ Queries database via Data Access layer (DB/)

4. Business logic executes
   ├─ Tax engine calculates taxes
   ├─ Forecasting models predict trends
   └─ Comparison algorithms optimize strategies

5. Data Access layer executes database operations
   ├─ Queries tax records, brackets, people
   └─ Returns results to business logic

6. Response returned to frontend
   ├─ JSON formatted response
   ├─ HTTP status code
   └─ Error details (if applicable)

7. Frontend displays results
   └─ Updates UI with data
```

## Database Schema

### tax_records Table
```sql
CREATE TABLE tax_records (
    record_id INTEGER PRIMARY KEY,
    num_people INTEGER,
    revenue REAL,
    total_costs REAL,
    group_income REAL,
    individual_income REAL,
    tax_origin TEXT,
    tax_option TEXT,
    tax_amount REAL,
    net_income_per_person REAL,
    net_income_group REAL,
    distribution_method TEXT,
    salary_amount REAL,
    created_at TIMESTAMP
)
```

### tax_brackets Table
```sql
CREATE TABLE tax_brackets (
    bracket_id INTEGER PRIMARY KEY,
    country TEXT,
    income_min REAL,
    income_max REAL,
    tax_rate REAL
)
```

### people Table
```sql
CREATE TABLE people (
    person_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    percentage REAL,
    revenue_assigned REAL
)
```

## Deployment Architecture

### Development
- **API:** Uvicorn development server (auto-reload)
- **Frontend:** React development server
- **Database:** SQLite (local file)
- **Monitoring:** Docker Compose stack (optional)

### Production
- **API:** Uvicorn with multiple worker processes (via Gunicorn)
- **Frontend:** Built React app served by web server (Nginx)
- **Database:** SQLite or managed database (PostgreSQL)
- **Monitoring:** Prometheus + Grafana stack
- **Reverse Proxy:** Nginx for SSL/TLS and routing

## Configuration Management

### Environment Variables
- `API_HOST` - API server host (default: 0.0.0.0)
- `API_PORT` - API server port (default: 8000)
- `API_DEBUG` - Debug mode (default: false)
- `PROMETHEUS_PORT` - Prometheus port (default: 9090)
- `GRAFANA_PORT` - Grafana port (default: 3001)
- `GRAFANA_PASSWORD` - Grafana admin password

**Loading:** Environment variables loaded from `.env` file using `python-dotenv`

## Error Handling

### API Error Responses
```python
{
    "detail": "Error message describing what went wrong"
}
```

**Status Codes:**
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (health check failure)

## Security Considerations

### Current Implementation
- CORS enabled for all origins (configurable)
- Input validation via Pydantic models
- SQLite for local development

### Production Recommendations
1. **Authentication:** Implement JWT or OAuth2
2. **HTTPS:** Use TLS/SSL certificates
3. **Database:** Use managed PostgreSQL or MySQL
4. **Input Validation:** Enhance Pydantic models
5. **Rate Limiting:** Implement rate limiting middleware
6. **SQL Injection Protection:** Use parameterized queries (already implemented)
7. **CORS:** Restrict to specific origins
8. **Secrets Management:** Use environment variables or secrets manager

## Performance Optimization

### Current Optimizations
- Database connection pooling (via get_conn())
- Efficient tax calculation algorithms
- Prometheus metrics for monitoring

### Potential Improvements
1. **Caching:** Redis for frequently accessed data
2. **Database Indexing:** Index on frequently queried columns
3. **API Response Compression:** Gzip compression
4. **CDN:** Content delivery network for static assets
5. **Async Database Operations:** Use async/await for I/O

## Monitoring & Observability

### Metrics Tracked
- `http_requests_total` - Total requests by endpoint
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_error_total` - Error count by type
- `database_operations_total` - Database operation count
- `tax_calculations_total` - Tax calculation operations
- `projects_created_total` - Business metric

### Health Checks
- **Readiness:** Checks database connectivity
- **Liveness:** Verifies process is running
- **Basic Health:** Returns application status

### Logging
- Structured JSON logging
- Configurable log levels
- Log rotation (daily)

## Scaling Considerations

### Horizontal Scaling
1. **Stateless API:** API servers can be scaled independently
2. **Load Balancer:** Distribute requests across API instances
3. **Shared Database:** Use PostgreSQL with connection pooling
4. **Cache Layer:** Redis for session and data caching

### Vertical Scaling
- Optimize database queries
- Increase server resources (CPU, memory)
- Implement database indexing

## Testing Architecture

### Test Organization
- **Unit Tests:** `/tests/unit/` - Test individual functions
- **Integration Tests:** `/tests/integration/` - Test API endpoints
- **Test Coverage:** Target 70%+ code coverage

### CI/CD Pipeline
- Run tests on every commit
- Generate coverage reports (HTML, XML)
- Build Docker image
- Deploy to staging/production

## Development Workflow

### Local Development
```bash
# 1. Install dependencies
pip install -r requirements.txt
npm install --prefix frontend

# 2. Start services
python3 -m uvicorn api.main:app --reload
npm start --prefix frontend

# 3. Run tests
python -m pytest

# 4. Check coverage
python -m pytest --cov=. --cov-report=html
```

### Docker Development
```bash
# Start complete stack
docker-compose up

# Access services:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001
```

## Code Organization Best Practices

### Module Imports
- Absolute imports preferred over relative imports
- Group imports: stdlib, third-party, local
- Use meaningful import names

### Code Style
- PEP 8 compliance
- Type hints for function signatures
- Docstrings for modules, classes, functions

### API Design
- RESTful principles
- Consistent endpoint naming
- Proper HTTP status codes
- Clear error messages

## Future Architecture Improvements

1. **Microservices:** Split into separate services (tax engine, reporting, etc.)
2. **Event-Driven:** Implement event streaming for real-time updates
3. **GraphQL:** Consider GraphQL for more flexible queries
4. **WebSockets:** Real-time dashboard updates
5. **Machine Learning:** Predictive tax optimization models
6. **Mobile App:** Native mobile application
7. **Internationalization:** Support multiple languages and currencies

---

**Last Updated:** 2025-11-30
**Version:** 1.0.0
