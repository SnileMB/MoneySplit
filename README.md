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
- **CSS3** - Styling with gradient themes

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
│   ├── main.py                # FastAPI application (1600+ lines)
│   └── models.py              # Pydantic models
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts      # API client
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx  # Dashboard with statistics
│   │   │   ├── Projects.tsx   # Project creation form
│   │   │   ├── Reports.tsx    # Analytics & charts
│   │   │   ├── RecordsManagement.tsx
│   │   │   └── TaxBracketsManagement.tsx
│   │   ├── App.tsx            # Main app with navigation
│   │   └── App.css            # Gradient theme styles
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

1. Navigate to "New Project" (📁 icon in sidebar)
2. Fill in project details (revenue, costs, country, tax type)
3. Add team members with work shares (must sum to 1.0)
4. Click "Create Project"
5. View results in Dashboard

---

## 📊 API Endpoints

### Projects & Records
- `POST /api/projects` - Create new project
- `GET /api/records` - Get recent records (default: 10)
- `GET /api/records/{id}` - Get specific record with people
- `PUT /api/records/{id}` - Update record field
- `DELETE /api/records/{id}` - Delete record

### Reports & Statistics
- `GET /api/reports/statistics` - Overall statistics (total revenue, tax, net income)
- `GET /api/reports/revenue-summary` - Revenue grouped by year
- `GET /api/reports/top-people` - Top contributors by net income

### Forecasting & Analysis
- `GET /api/forecast/revenue?months=3` - Revenue predictions
- `GET /api/forecast/comprehensive` - Full forecast with insights
- `GET /api/forecast/tax-optimization` - Tax recommendations
- `GET /api/forecast/trends` - Trend analysis with seasonality

### Visualizations
- `GET /api/visualizations/revenue-summary` - Revenue chart (HTML)
- `GET /api/visualizations/monthly-trends` - Monthly trends chart
- `GET /api/visualizations/work-distribution` - Work distribution pie chart
- `GET /api/visualizations/tax-comparison` - Tax comparison bar chart
- `GET /api/visualizations/project-profitability` - Profitability scatter plot
- `GET /api/visualizations/combined-dashboard` - All charts combined

### PDF Exports
- `GET /api/export/record/{id}/pdf` - Project PDF report
- `GET /api/export/summary/pdf` - Summary PDF report
- `GET /api/export/forecast/pdf` - Forecast PDF report

### Tax Brackets
- `GET /api/tax-brackets/{country}` - Get tax brackets for country
- `POST /api/tax-brackets` - Add new tax bracket
- `DELETE /api/tax-brackets/{id}` - Delete tax bracket

Full interactive documentation: `http://localhost:8000/docs`

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

## 📐 Architecture

### Database Schema

**tax_records** table:
- `id` (PRIMARY KEY)
- `num_people`, `revenue`, `total_costs`
- `group_income`, `individual_income`
- `tax_origin` (country), `tax_option` (Individual/Business)
- `tax_amount`, `net_income_per_person`, `net_income_group`
- `created_at` (timestamp)

**people** table:
- `id` (PRIMARY KEY)
- `record_id` (FOREIGN KEY → tax_records)
- `name`, `work_share`
- `gross_income`, `tax_paid`, `net_income`

**tax_brackets** table:
- `id` (PRIMARY KEY)
- `country`, `tax_type`
- `income_limit`, `rate`

### Key Design Patterns

- **Repository Pattern**: `DB/setup.py` handles all database operations
- **MVC Architecture**: Separation of business logic, API, and UI
- **REST API**: Stateless HTTP endpoints with JSON
- **Component-Based UI**: React functional components with hooks
- **Validation Layer**: Pydantic models for type safety and validation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture diagrams and component descriptions.

---

## 🎨 Frontend Features

### Pages
- **Dashboard** (📊): Statistics cards, recent projects table
- **New Project** (📁): Multi-step form with validation
- **Reports** (📈): Analytics with chart visualizations
- **Records Management**: View, edit, delete records
- **Tax Brackets Management**: CRUD operations for tax rates

### UI/UX
- Gradient purple theme (`#667eea` → `#764ba2`)
- Responsive sidebar navigation
- Collapsible menu on mobile
- Success/error alert messages
- Loading states and error handling
- Real-time form validation

### Build & Deploy

```bash
cd frontend
npm run build
# Creates optimized production build in frontend/build/
```

Bundle size: ~90 KB (gzipped)

---

## 📄 License

MIT

