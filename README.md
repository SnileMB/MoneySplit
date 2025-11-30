# 🤑 MoneySplit

**Commission-Based Income Splitting with Tax Calculations**

[![CI/CD Pipeline](https://github.com/SnileMB/MoneySplit/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/SnileMB/MoneySplit/actions)
[![Coverage](https://img.shields.io/badge/coverage-63%25-yellow)](https://github.com/SnileMB/MoneySplit)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A production-ready full-stack application for managing commission-based income splitting among team members with automatic tax calculations, forecasting, and professional reporting. Built with modern CI/CD practices, comprehensive testing, and monitoring.

**Live Demo:** [https://moneysplit-app-96aca02a2d13.herokuapp.com/](https://moneysplit-app-96aca02a2d13.herokuapp.com/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Testing](#-testing)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

---

## 🌟 Features

### Core Functionality
- ✅ **Project Management**: Create projects with multiple team members and work share distribution
- ✅ **Tax Calculations**: Progressive tax calculation with Individual/Business options
- ✅ **Multi-Country Support**: US, Spain, and custom tax brackets for any country
- ✅ **Work Share Distribution**: Flexible percentage allocation among team members

### Analytics & Reporting
- 📊 **Interactive Visualizations**: 6+ different chart types using Plotly
- 📈 **Revenue Forecasting**: ML-powered predictions using scikit-learn
- 💡 **Tax Optimization**: Smart recommendations for Individual vs Business tax structures
- 📉 **Trend Analysis**: Revenue, cost, and profit trends with seasonality detection
- 🎯 **Profitability Analysis**: ROI, profit margins, and project performance metrics

### Export Options
- 📄 **PDF Reports**: Professional reports for projects, summaries, and forecasts
- 📊 **CSV/JSON Export**: Data export for further analysis
- 🌐 **HTML Visualizations**: Interactive charts that open in browser

### Interfaces
- 💻 **CLI Application**: Full-featured command-line interface
- 🌐 **REST API**: FastAPI backend with 20+ endpoints
- 🎨 **Web Frontend**: Modern React TypeScript UI with responsive design

### Production Features (Assignment 2)
- 🔄 **CI/CD Pipeline**: Automated testing, linting, and deployment via GitHub Actions
- 🐳 **Docker Support**: Full containerization with docker-compose orchestration
- 📊 **Monitoring**: Prometheus metrics and Grafana dashboards
- 🏥 **Health Checks**: Comprehensive health endpoints for production readiness
- 🔒 **Code Quality**: Black, Flake8, Mypy, and comprehensive test coverage
- 🚀 **Cloud Deployment**: Live on Heroku with automatic deployments

---

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI** - Modern, high-performance REST API framework
- **SQLite** - Lightweight database for development and production
- **Pydantic** - Data validation and settings management
- **Plotly** - Interactive visualizations
- **scikit-learn** - Machine learning forecasting
- **ReportLab** - Professional PDF generation
- **Prometheus** - Metrics and monitoring

### Frontend
- **React 18** with TypeScript
- **Axios** - HTTP client for API communication
- **Recharts** - Data visualization components
- **React Router** - Client-side routing
- **CSS3** - Modern responsive styling

### DevOps & Quality
- **GitHub Actions** - CI/CD pipeline
- **Docker** & **docker-compose** - Containerization
- **pytest** - Testing framework with 547+ tests
- **Black** - Code formatting
- **Flake8** - Linting
- **Mypy** - Static type checking
- **Grafana** - Monitoring dashboards
- **Heroku** - Cloud platform deployment

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker & docker-compose (optional, for full stack)

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/SnileMB/MoneySplit.git
cd MoneySplit
```

#### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Database initializes automatically on first run
```

#### 3. Frontend Setup
```bash
cd frontend
npm install --legacy-peer-deps
```

### Running the Application

#### Option 1: Full Stack with Docker (Recommended)
```bash
# Start all services (API, Frontend, Prometheus, Grafana)
docker-compose up -d

# Access:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Option 2: Backend API Only
```bash
# Run FastAPI server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access:
# - API: http://localhost:8000
# - Interactive Docs: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

#### Option 3: Frontend Development Server
```bash
cd frontend
npm start

# Access: http://localhost:3000
```

#### Option 4: CLI Application
```bash
# Run from project root
python -m MoneySplit

# Features:
# - Create new projects
# - View/edit/delete records
# - Manage tax brackets
# - Generate reports and visualizations
# - Export to PDF/CSV/JSON
```

---

## 🧪 Testing

### Run All Tests
```bash
# Backend tests with coverage
pytest

# With coverage report
pytest --cov=. --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html
```

### Test Coverage
- **Current Coverage**: 63% (547 tests passing)
- **Target**: 70% (Assignment 2 requirement)

**Test Breakdown:**
- **Unit Tests**: Tax calculations, validation, business logic
- **Integration Tests**: API endpoints, database operations
- **Edge Case Tests**: Boundary values, error handling

### Frontend Tests
```bash
cd frontend
npm test

# With coverage
npm test -- --coverage --watchAll=false
```

### Run Specific Test Suites
```bash
# API tests only
pytest tests/test_api.py -v

# Database tests only
pytest tests/test_database.py -v

# Tax calculation tests
pytest tests/test_backend_logic.py -v
```

### Code Quality Checks
```bash
# Format code with Black
black api/ Logic/ DB/ tests/

# Lint with Flake8
flake8 api/ Logic/ DB/ --max-line-length=120

# Type check with Mypy
mypy api/ --ignore-missing-imports
```

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

**Triggers:**
- Push to `main`, `feature/*`, `assignment-*` branches
- Pull requests to `main`

**Jobs:**

1. **Backend Quality** (Python 3.9, 3.10, 3.11, 3.12)
   - Install dependencies with pip caching
   - Lint with Flake8
   - Format check with Black
   - Type check with Mypy
   - Run pytest with coverage
   - **Fail if coverage < 70%**
   - Upload coverage reports to Codecov

2. **Frontend Quality** (Node 18.x, 20.x, 22.x)
   - Install dependencies with npm caching
   - Lint with ESLint (max warnings = 0)
   - Build React application
   - Run Jest tests with coverage
   - Upload build artifacts

3. **Docker Build**
   - Build backend Docker image
   - Build frontend Docker image
   - Verify images are buildable

4. **Security Scanning**
   - Run Bandit security scanner
   - Generate vulnerability reports

5. **Status Check**
   - Consolidate all job results
   - **Pipeline fails if any job fails**

**View Pipeline:** [GitHub Actions](https://github.com/SnileMB/MoneySplit/actions)

---

## 📦 Deployment

### Heroku Deployment (Production)

**Live App:** https://moneysplit-app-96aca02a2d13.herokuapp.com/

#### Automatic Deployment
- Connected to `assignment-2` branch
- Auto-deploys on push via Heroku dashboard
- Uses **Node.js + Python buildpacks**

#### Manual Deployment
```bash
# Login to Heroku
heroku login

# Add Heroku remote (if not already added)
heroku git:remote -a moneysplit-app-96aca02a2d13

# Deploy
git push heroku assignment-2:main

# View logs
heroku logs --tail

# Open app
heroku open
```

#### Heroku Configuration
- **Buildpacks** (in order):
  1. `heroku/nodejs` (builds React frontend)
  2. `heroku/python` (runs FastAPI backend)
- **Procfile**: `web: uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Python version**: 3.11 (specified in `.python-version`)

### Docker Deployment

#### Build Images
```bash
# Backend
docker build -t moneysplit:latest .

# Frontend
docker build -f Dockerfile.frontend -t moneysplit-frontend:latest .
```

#### Run with Docker Compose
```bash
# Start full stack
docker-compose up -d

# Scale services
docker-compose up -d --scale api=3

# View status
docker-compose ps

# Stop all
docker-compose down

# Clean up volumes
docker-compose down -v
```

---

## 📊 Monitoring

### Health Endpoints

```bash
# Basic health check
curl https://moneysplit-app-96aca02a2d13.herokuapp.com/health

# Detailed health with component status
curl https://moneysplit-app-96aca02a2d13.herokuapp.com/health/detailed

# Readiness check
curl https://moneysplit-app-96aca02a2d13.herokuapp.com/health/ready

# Liveness check
curl https://moneysplit-app-96aca02a2d13.herokuapp.com/health/live
```

### Prometheus Metrics

**Metrics Endpoint:** `/metrics`

**Exposed Metrics:**
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Active requests
- `http_exceptions_total` - Exception count by type
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage

**Access Metrics:**
```bash
curl https://moneysplit-app-96aca02a2d13.herokuapp.com/metrics
```

### Grafana Dashboard

When running with Docker Compose:
1. Access Grafana at http://localhost:3001
2. Login: `admin` / `admin`
3. Pre-configured dashboard: "MoneySplit Dashboard"
4. Datasource: Prometheus (auto-configured)

**Dashboard Panels:**
- Request rate over time
- Error rate (4xx, 5xx)
- Response time percentiles (P50, P95, P99)
- Active requests gauge
- Top endpoints by request count
- Status code distribution

### Monitoring Configuration

**Files:**
- `monitoring/prometheus.yml` - Prometheus scrape config
- `monitoring/grafana-provisioning/` - Auto-provisioned dashboards and datasources
- `docker-compose.yml` - Full monitoring stack orchestration

See [MONITORING.md](MONITORING.md) for detailed setup instructions.

---

## 📖 API Documentation

### Interactive Documentation

**Swagger UI:** https://moneysplit-app-96aca02a2d13.herokuapp.com/docs
**ReDoc:** https://moneysplit-app-96aca02a2d13.herokuapp.com/redoc

### Key Endpoints

#### Projects
- `POST /api/projects` - Create new project with people and tax calculations
- `GET /api/records` - Get all records (with pagination)
- `GET /api/records/{id}` - Get specific record with people
- `PUT /api/records/{id}` - Update record field
- `DELETE /api/records/{id}` - Delete record and associated people

#### Tax Brackets
- `GET /api/tax-brackets` - Get tax brackets by country and type
- `POST /api/tax-brackets` - Add custom tax bracket
- `DELETE /api/tax-brackets/{id}` - Remove tax bracket

#### Analytics
- `GET /api/reports/statistics` - Get summary statistics
- `GET /api/forecast/revenue` - ML-powered revenue predictions
- `GET /api/forecast/tax-optimization` - Tax strategy recommendations

#### Export
- `GET /api/export/record/{id}/pdf` - Export project to PDF
- `GET /api/export/summary/pdf` - Export summary report
- `GET /api/export-csv` - Export all data to CSV
- `GET /api/export-json` - Export all data to JSON

#### Visualizations
- `GET /api/visualizations/revenue-summary` - Revenue summary chart
- `GET /api/visualizations/monthly-trends` - Trends dashboard
- `GET /api/visualizations/tax-comparison` - Tax strategy comparison

---

## 📁 Project Structure

```
MoneySplit/
├── api/                    # FastAPI application
│   ├── main.py            # Main API with all endpoints
│   ├── models.py          # Pydantic models for validation
│   ├── health.py          # Health check endpoints
│   ├── metrics.py         # Prometheus metrics setup
│   └── middleware.py      # Logging and error handling
├── DB/                    # Database layer
│   └── setup.py          # CRUD operations and schema
├── Logic/                 # Business logic
│   ├── tax_engine.py     # Tax calculation engine
│   ├── forecasting.py    # ML forecasting models
│   ├── pdf_generator.py  # PDF report generation
│   ├── validators.py     # Input validation
│   └── tax_comparison.py # Tax strategy comparison
├── frontend/              # React TypeScript app
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── api/          # API client
│   │   └── App.tsx       # Main app component
│   ├── public/
│   └── package.json
├── tests/                 # Test suite (547+ tests)
│   ├── test_api.py       # API integration tests
│   ├── test_backend_logic.py  # Business logic tests
│   ├── test_database.py  # Database tests
│   └── test_validators.py    # Validation tests
├── monitoring/            # Monitoring configuration
│   ├── prometheus.yml
│   └── grafana-provisioning/
├── .github/
│   └── workflows/
│       └── ci.yml        # CI/CD pipeline
├── docker-compose.yml     # Multi-container orchestration
├── Dockerfile             # Backend container
├── Dockerfile.frontend    # Frontend container
├── Procfile              # Heroku deployment config
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── README.md             # This file
├── REPORT.md             # Assignment 2 report
├── SOLID.md              # Code quality documentation
├── TESTING.md            # Testing documentation
└── MONITORING.md         # Monitoring setup guide
```

---

## 📊 Assignment 2 Deliverables

### ✅ Code Quality & Refactoring (25%)
- [x] Removed code smells (documented in [SOLID.md](SOLID.md))
- [x] Applied SOLID principles throughout codebase
- [x] Centralized configuration in `config.py`
- [x] Custom exception hierarchy
- [x] Comprehensive error handling and logging

### ✅ Testing & Coverage (20%)
- [x] 547 automated tests (unit + integration)
- [x] Current coverage: 63% (target: 70%)
- [x] Tests for all critical paths
- [x] Coverage reports in `htmlcov/`
- [x] Documentation in [TESTING.md](TESTING.md)

### ✅ CI/CD Pipeline (20%)
- [x] GitHub Actions workflow in `.github/workflows/ci.yml`
- [x] Matrix testing (Python 3.9-3.12, Node 18-22)
- [x] Automated testing, linting, type checking
- [x] Coverage measurement with failure threshold
- [x] Docker image builds
- [x] Security scanning with Bandit

### ✅ Deployment & Containerization (20%)
- [x] Docker support with `Dockerfile` + `Dockerfile.frontend`
- [x] docker-compose orchestration
- [x] Deployed to Heroku: https://moneysplit-app-96aca02a2d13.herokuapp.com/
- [x] Environment-based configuration
- [x] Health checks for containers

### ✅ Monitoring & Documentation (15%)
- [x] `/health`, `/health/detailed`, `/health/ready`, `/health/live` endpoints
- [x] Prometheus metrics at `/metrics`
- [x] Grafana dashboard configuration
- [x] Comprehensive README (this file)
- [x] Assignment report in [REPORT.md](REPORT.md)
- [x] Monitoring guide in [MONITORING.md](MONITORING.md)

---

## 🤝 Contributing

### Development Workflow

1. **Clone and Setup**
   ```bash
   git clone https://github.com/SnileMB/MoneySplit.git
   cd MoneySplit
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write code following existing patterns
   - Add tests for new functionality
   - Update documentation as needed

4. **Run Quality Checks**
   ```bash
   # Format code
   black api/ Logic/ DB/

   # Run tests
   pytest --cov=. --cov-report=term

   # Lint
   flake8 api/ Logic/ DB/ --max-line-length=120
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "[Feature] Description of changes"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Open PR against `main` branch
   - CI pipeline will run automatically
   - Address any failing checks

### Coding Standards
- **Python**: PEP 8, Black formatting, type hints
- **TypeScript**: ESLint, consistent naming
- **Tests**: Minimum 70% coverage for new code
- **Commits**: Descriptive messages with [Type] prefix

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

Built for Software Engineering II - Assignment 2
Technologies: FastAPI, React, Docker, GitHub Actions, Prometheus, Grafana
Deployed on: Heroku

---

**Questions or Issues?** [Open an issue](https://github.com/SnileMB/MoneySplit/issues)

**Live Demo:** [https://moneysplit-app-96aca02a2d13.herokuapp.com/](https://moneysplit-app-96aca02a2d13.herokuapp.com/)
