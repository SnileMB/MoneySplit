# Assignment 2: Code Quality, Testing, CI/CD, Deployment & Monitoring

## Executive Summary
This assignment focuses on improving MoneySplit by enhancing code quality, implementing comprehensive testing with 70%+ coverage, establishing CI/CD pipelines, containerizing the application, and adding monitoring capabilities.

---

## Current State Analysis

### Codebase Structure
- **Backend**: Python FastAPI application (~2000+ lines)
  - `/api/main.py` - REST API endpoints
  - `/DB/setup.py` - Database operations
  - `/Logic/` - Business logic (tax calculation, forecasting, PDF generation)
  - `/Menus/` - CLI interface components

- **Frontend**: React 19 + TypeScript
  - `/frontend/src/` - React components and pages
  - Key pages: Dashboard, Projects, Reports, Analytics, TaxCalculator

- **Testing**: Existing 1200+ lines of tests
  - `tests/test_api.py` (278 lines)
  - `tests/test_backend_logic.py` (222 lines)
  - `tests/test_database.py` (335 lines)
  - `tests/test_edge_cases.py` (365 lines)

- **Dependencies**: FastAPI, SQLite, Pydantic, Plotly, scikit-learn, ReportLab, React 19

---

## Assignment 2 Implementation Plan

### 1. Code Quality & Refactoring (25%)

#### 1.1 Identify Code Smells
- [ ] Scan for code duplication (especially in tax calculation logic)
- [ ] Identify long methods (>50 lines) in business logic
- [ ] Find hardcoded values (API ports, default paths, etc.)
- [ ] Detect missing error handling in API endpoints
- [ ] Review inconsistent naming conventions

#### 1.2 Refactoring Tasks
- [ ] Extract duplicate tax calculation logic into reusable functions
- [ ] Break down long methods in `/Logic/ProgramBackend.py`
- [ ] Create configuration module for hardcoded values (ports, DB path, API URLs)
- [ ] Improve error handling and validation across API endpoints
- [ ] Add proper logging throughout the application
- [ ] Apply SOLID principles:
  - **Single Responsibility**: Each class/function should have one reason to change
  - **Open/Closed**: Extend functionality without modifying existing code
  - **Liskov Substitution**: Ensure inheritance hierarchies are correct
  - **Interface Segregation**: Create specific interfaces, not general ones
  - **Dependency Inversion**: Depend on abstractions, not concrete implementations

#### 1.3 Code Quality Tools
- [ ] Add `pylint` or `flake8` for Python linting
- [ ] Add `black` for code formatting
- [ ] Configure ESLint for TypeScript/React
- [ ] Add type hints to Python functions
- [ ] Document public APIs with docstrings

---

### 2. Testing & Coverage (20%)

#### 2.1 Enhance Test Coverage
- [ ] Achieve 70%+ overall code coverage
- [ ] Add unit tests for uncovered functions
- [ ] Add integration tests for API endpoints
- [ ] Add end-to-end tests for critical workflows
- [ ] Test error cases and edge cases thoroughly

#### 2.2 Test Improvements
- [ ] Use `pytest-cov` to measure coverage
- [ ] Generate HTML coverage reports
- [ ] Add fixtures for test data
- [ ] Implement test database setup/teardown
- [ ] Add performance/load tests for API endpoints

#### 2.3 Frontend Testing
- [ ] Add Jest tests for React components
- [ ] Improve existing test files coverage
- [ ] Mock API calls in frontend tests
- [ ] Test state management and hooks

#### 2.4 Coverage Reporting
- [ ] Generate coverage report in HTML format
- [ ] Generate coverage report in XML format (for CI)
- [ ] Include coverage badge in README
- [ ] Fail tests if coverage drops below 70%

---

### 3. Continuous Integration (CI) (20%)

#### 3.1 GitHub Actions Workflow
- [ ] Create `.github/workflows/ci.yml` pipeline
- [ ] Pipeline should:
  - Run on push to any branch
  - Run on pull requests to main/feature branches
  - Checkout code
  - Set up Python environment
  - Install dependencies
  - Run linting checks
  - Run unit tests
  - Run integration tests
  - Generate coverage reports
  - Build frontend
  - Fail if tests fail
  - Fail if coverage < 70%
  - Upload coverage to code coverage service (optional)

#### 3.2 CI Configuration
- [ ] Matrix builds for multiple Python versions (3.8, 3.9, 3.10)
- [ ] Separate jobs for backend and frontend
- [ ] Cache dependencies for faster builds
- [ ] Generate artifacts (coverage reports, test results)
- [ ] Add status badges to README

---

### 4. Deployment & Containerization (20%)

#### 4.1 Docker Setup
- [ ] Create `Dockerfile` for backend (multi-stage build)
- [ ] Create `Dockerfile` for frontend
- [ ] Create `docker-compose.yml` for local development
- [ ] Use environment variables for configuration
- [ ] Implement health checks in Docker

#### 4.2 Docker Optimization
- [ ] Use minimal base images (python:3.11-slim)
- [ ] Minimize layer count
- [ ] Cache dependencies in Docker layers
- [ ] Don't run as root
- [ ] Use `.dockerignore` to exclude unnecessary files

#### 4.3 Cloud Deployment (Details TBD)
- [ ] Choose cloud platform (AWS, GCP, Azure, or Heroku for simplicity)
- [ ] Create deployment configuration
- [ ] Set up secrets management for API keys, DB credentials
- [ ] Configure deployment triggers (main branch only)
- [ ] Set up rollback strategy
- [ ] Create deployment documentation

#### 4.4 Environment Management
- [ ] Create `.env.example` for required variables
- [ ] Document all environment variables
- [ ] Use `python-dotenv` for local development
- [ ] Implement different configs for dev/prod

---

### 5. Monitoring & Health Checks (15%)

#### 5.1 Health Check Endpoint
- [ ] Add `/health` endpoint to API
- [ ] Return status of:
  - API service
  - Database connection
  - Basic system info (uptime, memory)
- [ ] Add `/health/ready` for readiness probe
- [ ] Add `/health/live` for liveness probe

#### 5.2 Metrics Collection
- [ ] Add Prometheus metrics using `prometheus-client`
- [ ] Track:
  - Request count (by endpoint, method, status)
  - Request latency (by endpoint)
  - Error count (by endpoint, type)
  - Database query count and latency
  - System metrics (CPU, memory)
- [ ] Expose metrics at `/metrics` endpoint

#### 5.3 Logging
- [ ] Implement structured logging (JSON format)
- [ ] Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- [ ] Include request IDs for tracing
- [ ] Log to files and stdout
- [ ] Rotate logs for file storage

#### 5.4 Monitoring Dashboard
- [ ] Create Prometheus configuration (`prometheus.yml`)
- [ ] Create Grafana dashboard configuration (or screenshots)
- [ ] Visualize:
  - API request rates
  - Error rates and types
  - Response latencies
  - System resource usage
  - Database performance
- [ ] Set up basic alerting rules

#### 5.5 Docker Compose for Monitoring
- [ ] Add Prometheus service
- [ ] Add Grafana service (optional but recommended)
- [ ] Update `docker-compose.yml` to include monitoring

---

### 6. Documentation (Integral to all sections)

#### 6.1 Update README.md
- [ ] Add sections for:
  - How to run the application locally
  - How to run tests
  - How to measure coverage
  - How to run with Docker
  - How to deploy to production
  - Architecture overview
  - Technology stack details

#### 6.2 Create REPORT.md (5-6 pages)
- [ ] **Executive Summary**: Overview of improvements
- [ ] **Code Quality Improvements**:
  - What was refactored
  - SOLID principles applied
  - Before/after code examples
- [ ] **Testing Strategy**:
  - Coverage metrics
  - Test categories and counts
  - Critical test cases
- [ ] **CI/CD Pipeline**:
  - Workflow diagram
  - Pipeline stages and jobs
  - Build time metrics
- [ ] **Deployment Process**:
  - Containerization approach
  - Cloud platform selection and reasoning
  - Deployment flow
- [ ] **Monitoring & Observability**:
  - Metrics collected
  - Dashboard screenshots
  - Alert thresholds
- [ ] **Lessons Learned & Future Improvements**

#### 6.3 Additional Documentation
- [ ] `TESTING.md` - Detailed testing documentation
- [ ] `DEPLOYMENT.md` - Deployment instructions
- [ ] `MONITORING.md` - Monitoring setup guide
- [ ] `ARCHITECTURE.md` - System architecture (update if exists)

---

## Implementation Approach

### Phase 1: Code Quality & Testing Foundation
1. Run code analysis tools (pylint, flake8)
2. Refactor identified code smells
3. Enhance test coverage to 70%+
4. Generate coverage reports

### Phase 2: CI/CD Pipeline
1. Set up GitHub Actions workflow
2. Configure matrix builds
3. Add artifact generation
4. Test pipeline with sample runs

### Phase 3: Containerization
1. Create Docker configurations
2. Test locally with Docker Compose
3. Optimize Docker images
4. Document Docker setup

### Phase 4: Deployment
1. Choose cloud platform
2. Create deployment configuration
3. Set up secrets management
4. Configure main-branch-only deployments

### Phase 5: Monitoring
1. Add health check endpoints
2. Implement Prometheus metrics
3. Create monitoring configurations
4. Set up Grafana dashboards

### Phase 6: Documentation
1. Update README with comprehensive instructions
2. Create REPORT.md with 5-6 pages of detail
3. Add supporting documentation files
4. Include metrics and screenshots

---

## Success Criteria

- ✅ Code coverage ≥ 70%
- ✅ All tests passing in CI
- ✅ CI pipeline runs on every push/PR
- ✅ Application runs in Docker
- ✅ Health check endpoint responds
- ✅ Prometheus metrics exposed
- ✅ Deployment automated for main branch
- ✅ Comprehensive documentation in README
- ✅ 5-6 page REPORT.md with improvements documented
- ✅ Meaningful commit messages throughout
- ✅ Repository runnable by others

---

## File Structure After Completion

```
MoneySplit/
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI/CD pipeline
├── Dockerfile                         # Backend containerization
├── Dockerfile.frontend               # Frontend containerization
├── docker-compose.yml                # Local dev with monitoring
├── monitoring/
│   ├── prometheus.yml                # Prometheus config
│   └── grafana-dashboard.json        # Grafana dashboard
├── .env.example                      # Environment template
├── requirements-dev.txt              # Dev dependencies (pytest-cov, etc.)
├── assignment2.md                    # This plan (done)
├── REPORT.md                         # Comprehensive report
├── TESTING.md                        # Testing documentation
├── DEPLOYMENT.md                     # Deployment guide
├── MONITORING.md                     # Monitoring setup
├── README.md                         # Updated with all instructions
├── tests/                            # Enhanced test suite
├── api/
│   ├── main.py                       # Refactored with health checks
│   ├── models.py
│   └── middleware.py                 # Logging, metrics middleware
├── Logic/                            # Refactored modules
├── DB/                               # Database layer
└── frontend/                         # React app with tests
```

---

## Notes

- **Commit Strategy**: Create meaningful commits for each significant change
- **Branch**: All work on `assignment-2` branch
- **Testing**: Tests should be added progressively with code changes
- **Documentation**: Document as you go, not at the end
- **Cloud Platform**: Details will be provided later
- **CI Pipeline**: Details will be provided later

---

## Estimated Task Breakdown

| Component | Tasks | Subtasks |
|-----------|-------|----------|
| Code Quality | 3 | 13 |
| Testing | 4 | 16 |
| CI/CD | 2 | 10 |
| Deployment | 4 | 16 |
| Monitoring | 5 | 18 |
| Documentation | 3 | 8 |
| **TOTAL** | **21** | **81** |
