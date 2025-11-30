# 🤑 MoneySplit

**Commission-Based Income Splitting with Tax Calculations**

A full-stack application for managing commission-based income splitting among team members with automatic tax calculations, forecasting, and professional reporting.

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
- 💡 **Tax Optimization**: Smart recommendations for Individual vs Business tax
- 📉 **Trend Analysis**: Revenue, cost, and profit trends with seasonality detection
- 🎯 **Profitability Analysis**: ROI, profit margins, and project performance metrics

### Export Options
- 📄 **PDF Reports**: Professional reports for projects, summaries, and forecasts
- 📊 **CSV/JSON Export**: Data export for further analysis
- 🌐 **HTML Visualizations**: Interactive charts that open in browser

### Interfaces
- 💻 **CLI Application**: Full-featured command-line interface
- 🌐 **REST API**: FastAPI backend with 20+ endpoints
- 🎨 **Web Frontend**: Modern React TypeScript UI

---

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Modern REST API framework
- **SQLite** - Database
- **Pydantic** - Data validation
- **Plotly** - Interactive visualizations
- **scikit-learn** - Machine learning forecasting
- **ReportLab** - PDF generation

### Frontend
- **React 18** with TypeScript
- **Axios** - API client
- **Recharts** - Data visualization
- **CSS3** - Styling

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Backend Setup

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Initialize database (automatically creates with default tax brackets)
python3 -m MoneySplit
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

---

## 🚀 Running the Application

### Option 1: CLI Application

```bash
# Run from project root
python3 -m MoneySplit
```

Features:
- Create new projects
- View/edit/delete records
- Manage tax brackets
- Generate reports and visualizations
- Export to PDF/CSV/JSON

### Option 2: REST API

```bash
# Start the API server
python3 -m uvicorn api.main:app --reload
```

Access:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Option 3: Web Frontend

```bash
# In frontend directory
cd frontend
npm start
```

Access: `http://localhost:3000`

**Note:** Backend API must be running for frontend to work.

### Running Full Stack

```bash
# Terminal 1: Start backend
python3 -m uvicorn api.main:app --reload

# Terminal 2: Start frontend
cd frontend && npm start
```

---

## 📁 Project Structure

```
MoneySplit/
├── DB/                         # Database layer
│   ├── setup.py               # Database operations & queries
│   └── reset.py               # Database maintenance
├── Logic/                      # Business logic
│   ├── ProgramBackend.py      # Core calculation logic
│   ├── validators.py          # Input validation
│   ├── forecasting.py         # ML forecasting engine
│   └── pdf_generator.py       # PDF report generation
├── Menus/                      # CLI interface
│   ├── project_menu.py        # Project creation
│   ├── db_menu.py             # Database operations
│   ├── tax_menu.py            # Tax bracket management
│   └── report_menu.py         # Reports & visualizations
├── api/                        # REST API
│   ├── main.py                # FastAPI application
│   └── models.py              # Pydantic models
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts      # API client
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx  # Dashboard page
│   │   │   ├── Projects.tsx   # Project creation
│   │   │   └── Reports.tsx    # Analytics
│   │   ├── App.tsx            # Main component
│   │   └── App.css            # Styles
│   └── package.json
├── reports/                    # Generated reports (auto-created)
├── example.db                  # SQLite database
├── requirements.txt            # Python dependencies
├── __main__.py                # CLI entry point
└── README.md                  # This file
```

---

## 🎯 Usage Examples

### CLI: Create a Project

```bash
python3 -m MoneySplit
# Select: 1. New Project
# Follow prompts to enter:
# - Number of people
# - Revenue and costs
# - Country and tax type
# - Team members and work shares
```

### API: Create a Project

```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "num_people": 2,
    "revenue": 10000,
    "costs": [1000, 500],
    "country": "US",
    "tax_type": "Individual",
    "people": [
      {"name": "Alice", "work_share": 0.6},
      {"name": "Bob", "work_share": 0.4}
    ]
  }'
```

### Frontend: Create a Project

1. Navigate to "New Project"
2. Fill in the form fields
3. Add team members with work shares
4. Click "Create Project"

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term
```

### Test Coverage

The project includes 85+ tests covering:
- **Unit Tests**: Tax calculation, work share distribution, input validation
- **API Integration Tests**: All CRUD operations, reports, forecasting, visualizations
- **Database Tests**: CRUD operations, foreign keys, aggregations
- **Edge Case Tests**: Boundary values, invalid inputs, special characters

**Current Coverage**: 32% (expanding in progress)
**Target Coverage**: 70%+

View coverage reports:
```bash
# Generate HTML report
pytest --cov=. --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Code Quality Tools

```bash
# Format code with Black
black . --exclude="node_modules|.git|htmlcov"

# Check formatting
black --check .

# Lint with flake8
flake8 api/ Logic/ DB/ --max-line-length=120

# Type check with mypy
mypy api/ --ignore-missing-imports

# Security scan with bandit
bandit -r api/ Logic/ DB/
```

---

## 🐳 Docker

### Build Docker Images

```bash
# Backend API image
docker build -t moneysplit:latest .

# Frontend image
docker build -f Dockerfile.frontend -t moneysplit-frontend:latest .
```

### Run with Docker Compose

```bash
# Start all services (API, Frontend, Prometheus, Grafana)
docker-compose up

# Build before starting
docker-compose up --build

# Run in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

**Services:**
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### Docker Configuration

- **Multi-stage builds** for minimal image size
- **Non-root user** execution for security
- **Health checks** for all containers
- **Volume persistence** for data and logs
- **Custom networking** for service communication

---

## 🔍 Health Checks & Monitoring

### Health Check Endpoints

```bash
# Basic health status
curl http://localhost:8000/health

# Readiness check (includes database)
curl http://localhost:8000/health/ready

# Detailed status (system info, metrics)
curl http://localhost:8000/health/detailed
```

### Prometheus Metrics

Access metrics at: `http://localhost:8000/metrics`

**Available Metrics:**
- `moneysplit_requests_total` - Total requests by endpoint/method/status
- `moneysplit_request_duration_seconds` - Request latency
- `moneysplit_errors_total` - Error count by type
- `moneysplit_projects_created_total` - Projects created
- `moneysplit_tax_calculations_total` - Tax calculations by country/type
- `moneysplit_db_query_duration_seconds` - Database query latency
- `moneysplit_db_records_total` - Total database records
- `moneysplit_active_requests` - Currently active requests

### Grafana Dashboards

1. Open Grafana: http://localhost:3001
2. Login with `admin` / `admin`
3. Import dashboards from `/monitoring` directory
4. View real-time metrics and trends

### Prometheus Configuration

Prometheus is configured to scrape metrics from the API every 10 seconds.

Config file: `monitoring/prometheus.yml`

---

## 📊 API Endpoints

### Projects
- `POST /api/projects` - Create new project
- `GET /api/records` - Get recent records
- `GET /api/records/{id}` - Get specific record
- `PUT /api/records/{id}` - Update record
- `DELETE /api/records/{id}` - Delete record

### Reports
- `GET /api/reports/statistics` - Overall statistics
- `GET /api/reports/revenue-summary` - Revenue by year
- `GET /api/reports/top-people` - Top contributors

### Forecasting
- `GET /api/forecast/revenue?months=3` - Revenue predictions
- `GET /api/forecast/comprehensive` - Full forecast with insights
- `GET /api/forecast/tax-optimization` - Tax recommendations
- `GET /api/forecast/trends` - Trend analysis

### Visualizations
- `GET /api/visualizations/revenue-summary` - Revenue chart
- `GET /api/visualizations/monthly-trends` - Monthly trends
- `GET /api/visualizations/work-distribution` - Work distribution
- `GET /api/visualizations/tax-comparison` - Tax comparison
- `GET /api/visualizations/project-profitability` - Profitability

### PDF Exports
- `GET /api/export/record/{id}/pdf` - Project PDF
- `GET /api/export/summary/pdf` - Summary PDF
- `GET /api/export/forecast/pdf` - Forecast PDF

Full documentation: `http://localhost:8000/docs`

---

## 🧪 Testing

The project includes comprehensive automated tests covering both unit and integration testing.

### Run All Tests

```bash
pytest
```

### Run Specific Test Suite

```bash
# Unit tests only
pytest tests/test_backend_logic.py

# API integration tests only
pytest tests/test_api.py
```

### Test Coverage

- **85 total tests** covering:
  - **Unit Tests (25)**: Tax calculation, work share distribution, input validation, profit calculations
  - **API Integration Tests (23)**: All CRUD operations, reports, forecasting, visualizations, PDF exports
  - **Database Tests (20)**: CRUD operations, foreign keys, aggregations, complex queries
  - **Edge Case Tests (17)**: Boundary values, invalid inputs, special characters, precision, floating point accuracy

### View Detailed Test Documentation

See [TESTING.md](TESTING.md) for:
- Complete test documentation
- How to run tests with coverage
- Adding new tests
- CI/CD integration examples

---

## 🚀 CI/CD Pipeline

### Automated Workflow

The project uses GitHub Actions for continuous integration and testing.

**Workflow triggers:**
- Push to `main`, `feature/*`, or `assignment-*` branches
- Pull requests to `main`

**Workflow jobs:**
1. **Backend Quality** - Python 3.8, 3.9, 3.10, 3.11 matrix
   - Install dependencies with caching
   - Black formatting checks
   - Flake8 linting
   - Mypy type checking
   - Pytest execution
   - Coverage measurement (fails if < 70%)

2. **Frontend Quality** - Node 16.x, 18.x, 20.x matrix
   - Install dependencies with caching
   - ESLint linting (strict)
   - React build
   - Jest tests

3. **Docker Build**
   - Build backend image
   - Build frontend image

4. **Security Scan**
   - Bandit vulnerability scanning
   - Report generation

5. **Status Check**
   - Consolidate all job results

**Artifacts uploaded:**
- Coverage HTML reports
- Security scan reports
- Frontend build artifacts

View workflow status: `.github/workflows/ci.yml`

---

## 🔧 Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

### Local Development

1. **Clone repository**
   ```bash
   git clone https://github.com/your-username/MoneySplit.git
   cd MoneySplit
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment (optional)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set up Node environment**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run application**
   ```bash
   # Terminal 1: Backend API
   python3 -m uvicorn api.main:app --reload

   # Terminal 2: Frontend
   cd frontend && npm start
   ```

### Code Style & Quality

```bash
# Format code
black .

# Check formatting
black --check .

# Lint code
flake8 api/ Logic/ DB/

# Type check
mypy api/

# Security scan
bandit -r api/ Logic/ DB/

# Run tests
pytest -v

# Coverage report
pytest --cov=. --cov-report=html
```

### Environment Variables

See `.env.example` for all available variables:
- `API_HOST`, `API_PORT` - API configuration
- `FRONTEND_HOST`, `FRONTEND_PORT` - Frontend configuration
- `DB_PATH` - Database location
- `LOG_LEVEL`, `LOG_FILE` - Logging configuration
- `METRICS_ENABLED` - Enable Prometheus metrics
- `ENVIRONMENT` - development/production

---

## 📦 Deployment

### Docker Deployment

1. **Build images**
   ```bash
   docker build -t moneysplit:latest .
   docker build -f Dockerfile.frontend -t moneysplit-frontend:latest .
   ```

2. **Push to registry**
   ```bash
   docker tag moneysplit:latest your-registry/moneysplit:latest
   docker push your-registry/moneysplit:latest
   ```

3. **Deploy with Docker Compose**
   ```bash
   # Use docker-compose.yml for full stack
   docker-compose up -d
   ```

### Cloud Deployment (Azure)

Azure deployment configuration is managed through:
- GitHub Secrets: `AZURE_CREDENTIALS_FOR_GITHUB_ACTIONS`, `SERVICE_PRINCIPALS_CREDENTIALS`
- GitHub Actions workflow integration
- Container registry deployment

For detailed deployment instructions, see `DEPLOYMENT.md`

### Health Checks

All containers include health checks:

```bash
# Check API health
curl http://localhost:8000/health

# Check readiness
curl http://localhost:8000/health/ready

# Check detailed status
curl http://localhost:8000/health/detailed
```

### Monitoring in Production

- **Prometheus** collects metrics from all services
- **Grafana** provides dashboard visualization
- **Health endpoints** available at `/health/*`
- **Structured logging** in JSON format

---

## 📐 Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for:
- System architecture diagram
- Component descriptions
- Data flow diagrams
- Technology stack details
- Design patterns used

---

## 📄 License

MIT

---

**Built with ❤️ for commission-based teams**
