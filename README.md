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
