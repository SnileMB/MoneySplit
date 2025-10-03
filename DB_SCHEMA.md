# MoneySplit Database Schema

This document describes the SQLite database structure for MoneySplit.

## Overview

The database consists of three main tables:
1. **tax_records** - Project/record financial data
2. **people** - Individual team members per project
3. **tax_brackets** - Tax calculation rules by country and type

---

## Tables

### 1. `tax_records`

Stores project financial data including revenue, costs, taxes, and net income.

```sql
CREATE TABLE tax_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` - Unique record identifier
- `num_people` - Number of people working on the project
- `revenue` - Total project revenue
- `total_costs` - Sum of all project costs
- `group_income` - Revenue minus costs (before tax)
- `individual_income` - Group income divided by num_people
- `tax_origin` - Country for tax calculation (e.g., "US", "Spain")
- `tax_option` - Tax type: "Individual" or "Business"
- `tax_amount` - Calculated tax per person
- `net_income_per_person` - Income after tax per person
- `net_income_group` - Total net income for the group
- `created_at` - Timestamp of record creation

**Relationships:**
- One-to-many with `people` table (one record has many people)

---

### 2. `people`

Stores individual team member data for each project.

```sql
CREATE TABLE people (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  record_id INTEGER,
  name TEXT NOT NULL,
  work_share REAL,
  gross_income REAL,
  tax_paid REAL,
  net_income REAL,
  FOREIGN KEY (record_id) REFERENCES tax_records(id) ON DELETE CASCADE
);
```

**Fields:**
- `id` - Unique person entry identifier
- `record_id` - Foreign key to tax_records
- `name` - Person's name
- `work_share` - Percentage of work done (0.0 to 1.0)
- `gross_income` - Income before tax
- `tax_paid` - Tax amount paid
- `net_income` - Income after tax

**Relationships:**
- Many-to-one with `tax_records` (CASCADE DELETE - deleting a record deletes all associated people)

---

### 3. `tax_brackets`

Stores tax calculation rules for different countries and tax types.

```sql
CREATE TABLE tax_brackets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  country TEXT NOT NULL,
  tax_type TEXT NOT NULL,
  income_limit REAL NOT NULL,
  rate REAL NOT NULL
);
```

**Fields:**
- `id` - Unique bracket identifier
- `country` - Country name (e.g., "US", "Spain")
- `tax_type` - "Individual" or "Business"
- `income_limit` - Upper income threshold for this bracket
- `rate` - Tax rate as decimal (e.g., 0.22 for 22%)

**How Tax Brackets Work:**
Tax is calculated progressively. Income is taxed at different rates as it crosses each threshold.

**Example (US Individual):**
```
Income: $50,000
Brackets:
  $0 - $10,275:   10% → $1,027.50
  $10,275 - $41,775: 12% → $3,780.00
  $41,775 - $50,000: 22% → $1,809.50
Total tax: $6,617.00 (13.2% effective rate)
```

---

## Default Data

### US Tax Brackets (2024)

**Individual:**
- $10,275: 10%
- $41,775: 12%
- $89,075: 22%
- $170,050: 24%
- $215,950: 32%
- $539,900: 35%
- ∞: 37%

**Business:**
- Flat 21% corporate tax rate

### Spain Tax Brackets (2024)

**Individual (Autónomo):**
- $12,450: 19%
- $20,200: 24%
- $35,200: 30%
- $60,000: 37%
- $300,000: 45%
- ∞: 47%

**Business (SL):**
- $300,000: 23%
- ∞: 25%

---

## Relationships Diagram

```
tax_records (1) ────< (N) people
     │
     │ (uses)
     ▼
tax_brackets (lookup table)
```

---

## Indexes

Current schema has no explicit indexes beyond primary keys. For large datasets, consider adding:

```sql
CREATE INDEX idx_tax_records_created_at ON tax_records(created_at);
CREATE INDEX idx_tax_records_country ON tax_records(tax_origin);
CREATE INDEX idx_people_record_id ON people(record_id);
CREATE INDEX idx_people_name ON people(name);
CREATE INDEX idx_tax_brackets_country_type ON tax_brackets(country, tax_type);
```

---

## Notes

1. **Cascade Deletion**: Deleting a `tax_records` entry automatically deletes all associated `people` entries
2. **Tax Calculation**: Tax is calculated using the `tax_brackets` table based on `tax_origin` and `tax_option`
3. **Derived Fields**: Fields like `group_income`, `individual_income`, `net_income_per_person`, and `net_income_group` are calculated, not user-input
4. **Work Share**: Must sum to 1.0 for all people in a project (e.g., 0.33, 0.33, 0.34 for 3 people)
5. **Currency**: All monetary values are in USD equivalent
