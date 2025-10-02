# MoneySplit RESTful API

Commission-based income splitting with tax calculations - RESTful API built with FastAPI.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run the API Server
```bash
# From the MoneySplit directory
python3 -m uvicorn api.main:app --reload
```

### 3. Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Homepage**: http://localhost:8000

---

## 📡 API Endpoints

### **Projects & Records**

#### Create Project
```http
POST /api/projects
Content-Type: application/json

{
  "num_people": 3,
  "revenue": 10000,
  "costs": [1000, 500, 300],
  "country": "US",
  "tax_type": "Individual",
  "people": [
    {"name": "Alice", "work_share": 0.5},
    {"name": "Bob", "work_share": 0.3},
    {"name": "Charlie", "work_share": 0.2}
  ]
}
```

#### Get Records
```http
GET /api/records?limit=10
```

#### Get Record by ID
```http
GET /api/records/{record_id}
```

#### Update Record
```http
PUT /api/records/{record_id}
Content-Type: application/json

{
  "field": "revenue",
  "value": 12000
}
```

#### Delete Record
```http
DELETE /api/records/{record_id}
```

---

### **Tax Brackets**

#### Get Tax Brackets
```http
GET /api/tax-brackets?country=US&tax_type=Individual
```

#### Create Tax Bracket
```http
POST /api/tax-brackets
Content-Type: application/json

{
  "country": "US",
  "tax_type": "Individual",
  "income_limit": 50000,
  "rate": 0.22
}
```

#### Delete Tax Bracket
```http
DELETE /api/tax-brackets/{bracket_id}
```

---

### **People**

#### Get Person by ID
```http
GET /api/people/{person_id}
```

#### Get Person History
```http
GET /api/people/history/{name}
```

---

### **Reports & Analytics**

#### Revenue Summary by Year
```http
GET /api/reports/revenue-summary
```

#### Top People by Net Income
```http
GET /api/reports/top-people?limit=10
```

#### Overall Statistics
```http
GET /api/reports/statistics
```

---

### **Visualizations**

#### Revenue Summary Visualization (HTML)
```http
GET /api/visualizations/revenue-summary
```

---

## 📊 Example Usage with cURL

### Create a Project
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "num_people": 2,
    "revenue": 5000,
    "costs": [500, 300],
    "country": "US",
    "tax_type": "Business",
    "people": [
      {"name": "John", "work_share": 0.6},
      {"name": "Jane", "work_share": 0.4}
    ]
  }'
```

### Get Statistics
```bash
curl "http://localhost:8000/api/reports/statistics"
```

### Get Tax Brackets
```bash
curl "http://localhost:8000/api/tax-brackets?country=US&tax_type=Individual"
```

---

## 🐍 Example Usage with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Create a project
project_data = {
    "num_people": 3,
    "revenue": 15000,
    "costs": [2000, 1000, 500],
    "country": "Spain",
    "tax_type": "Individual",
    "people": [
        {"name": "Maria", "work_share": 0.5},
        {"name": "Carlos", "work_share": 0.3},
        {"name": "Ana", "work_share": 0.2}
    ]
}

response = requests.post(f"{BASE_URL}/projects", json=project_data)
print(response.json())

# Get records
records = requests.get(f"{BASE_URL}/records?limit=5")
print(records.json())

# Get statistics
stats = requests.get(f"{BASE_URL}/reports/statistics")
print(stats.json())
```

---

## 🔧 Response Models

### Project Creation Response
```json
{
  "record_id": 1,
  "message": "Project created successfully",
  "summary": {
    "revenue": 10000,
    "total_costs": 1800,
    "tax_amount": 1640.8,
    "net_income_group": 6559.2,
    "net_income_per_person": 2186.4
  }
}
```

### Record Response
```json
{
  "id": 1,
  "num_people": 3,
  "revenue": 10000,
  "total_costs": 1800,
  "tax_origin": "US",
  "tax_option": "Individual",
  "tax_amount": 1640.8,
  "net_income_group": 6559.2,
  "net_income_per_person": 2186.4,
  "created_at": "2025-10-02 16:30:00"
}
```

---

## ✅ Validation Rules

- **Work shares** must sum to 1.0
- **Revenue/costs** must be non-negative
- **Country** must be "US" or "Spain"
- **Tax type** must be "Individual" or "Business"
- **Tax rates** must be between 0 and 1
- **Number of people** must match people array length

---

## 🌐 CORS Support

CORS is enabled for all origins. For production, update the allowed origins in `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 Notes

- API runs on port **8000** by default
- All endpoints return JSON (except visualizations)
- Interactive docs auto-generated at `/docs`
- All database operations use existing MoneySplit backend
- Plotly visualizations accessible via API

---

## 🎯 For Your Teacher

This API provides:
- ✅ RESTful architecture (GET, POST, PUT, DELETE)
- ✅ Auto-generated interactive documentation
- ✅ Input validation with Pydantic
- ✅ Proper HTTP status codes
- ✅ JSON request/response format
- ✅ CRUD operations for all entities
- ✅ Advanced reporting endpoints
- ✅ Embedded visualizations

Perfect for demonstrating modern web API development! 🚀
