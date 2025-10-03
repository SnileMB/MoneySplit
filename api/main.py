"""
MoneySplit FastAPI Application
RESTful API for commission-based income splitting with tax calculations.
"""
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os
import csv
import io
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DB import setup
from Logic import pdf_generator, forecasting, tax_comparison, tax_engine
from api.models import (
    ProjectCreate, ProjectCreateResponse, RecordResponse,
    RecordWithPeople, PersonResponse, TaxBracketCreate,
    TaxBracketResponse, RecordUpdate, MessageResponse
)

app = FastAPI(
    title="MoneySplit API",
    description="RESTful API for commission-based income splitting with tax calculations",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Project/Record Endpoints =====

@app.post("/api/projects", response_model=ProjectCreateResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project with people and calculate taxes using the enhanced tax engine."""
    try:
        # Calculate totals
        total_costs = sum(project.costs)
        income = project.revenue - total_costs
        group_income = income
        individual_income = income / project.num_people if project.num_people > 0 else 0

        # Use the new tax engine to calculate taxes
        tax_result = tax_engine.calculate_project_taxes(
            revenue=project.revenue,
            costs=total_costs,
            num_people=project.num_people,
            country=project.country,
            tax_structure=project.tax_type,
            distribution_method=project.distribution_method,
            salary_amount=project.salary_amount or 0
        )

        # Extract values from tax_result
        tax = tax_result['total_tax']
        net_income_group = tax_result['net_income_group']
        net_income_per_person = tax_result['net_income_per_person']

        # Save to database
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tax_records (
                num_people, revenue, total_costs, group_income, individual_income,
                tax_origin, tax_option, tax_amount,
                net_income_per_person, net_income_group,
                distribution_method, salary_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.num_people,
            project.revenue,
            total_costs,
            group_income,
            individual_income,
            project.country,
            project.tax_type,
            tax,
            net_income_per_person,
            net_income_group,
            project.distribution_method,
            project.salary_amount or 0
        ))
        record_id = cursor.lastrowid

        # Save people
        for person in project.people:
            if project.tax_type == "Individual":
                gross_income = individual_income * person.work_share * project.num_people
                tax_paid = tax * person.work_share
                net_income = gross_income - tax_paid
            else:
                gross_income = group_income * person.work_share
                tax_paid = tax * person.work_share
                net_income = net_income_group * person.work_share

            cursor.execute("""
                INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (record_id, person.name, person.work_share, gross_income, tax_paid, net_income))

        conn.commit()
        conn.close()

        return ProjectCreateResponse(
            record_id=record_id,
            message="Project created successfully",
            summary={
                "revenue": project.revenue,
                "total_costs": total_costs,
                "tax_amount": tax,
                "net_income_group": net_income_group,
                "net_income_per_person": net_income_per_person,
                "distribution_method": project.distribution_method,
                "effective_rate": tax_result['effective_rate']
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/records", response_model=List[RecordResponse])
async def get_records(limit: int = Query(10, ge=1, le=100)):
    """Get recent records (default: last 10)."""
    records = setup.fetch_last_records(limit)
    return [
        RecordResponse(
            id=r[0], tax_origin=r[1], tax_option=r[2],
            revenue=r[3], total_costs=r[4], tax_amount=r[5],
            net_income_group=r[6], net_income_per_person=r[7],
            created_at=r[8],
            num_people=r[9], group_income=r[10], individual_income=r[11],
            distribution_method=r[12] if len(r) > 12 else "N/A",
            salary_amount=r[13] if len(r) > 13 else 0
        ) for r in records
    ]


@app.get("/api/records/{record_id}", response_model=RecordWithPeople)
async def get_record(record_id: int):
    """Get a specific record with its people."""
    record = setup.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found")

    people = setup.fetch_people_by_record(record_id)

    return RecordWithPeople(
        id=record[0], tax_origin=record[1], tax_option=record[2],
        revenue=record[3], total_costs=record[4], tax_amount=record[5],
        net_income_group=record[6], net_income_per_person=record[7],
        created_at=record[8],
        num_people=record[9], group_income=record[10], individual_income=record[11],
        distribution_method=record[12] if len(record) > 12 else "N/A",
        salary_amount=record[13] if len(record) > 13 else 0,
        people=[
            PersonResponse(
                id=p[0], name=p[1], work_share=p[2],
                gross_income=p[3], tax_paid=p[4], net_income=p[5]
            ) for p in people
        ]
    )


@app.put("/api/records/{record_id}", response_model=MessageResponse)
async def update_record(record_id: int, update: RecordUpdate):
    """Update a record field."""
    try:
        setup.update_record(record_id, update.field, update.value)
        return MessageResponse(message=f"Record {record_id} updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/records/{record_id}", response_model=MessageResponse)
async def delete_record(record_id: int):
    """Delete a record and its people."""
    record = setup.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found")

    setup.delete_record(record_id)
    return MessageResponse(message=f"Record {record_id} deleted successfully")


# ===== Tax Bracket Endpoints =====

@app.get("/api/tax-brackets", response_model=List[TaxBracketResponse])
async def get_tax_brackets(country: str, tax_type: str):
    """Get tax brackets for a country and type."""
    import math
    brackets = setup.get_tax_brackets(country, tax_type, include_id=True)
    return [
        TaxBracketResponse(
            id=b[0],
            income_limit=999999999 if math.isinf(b[1]) else b[1],  # Convert inf to large number for JSON
            rate=b[2],
            country=country,
            tax_type=tax_type
        ) for b in brackets
    ]


@app.post("/api/tax-brackets", response_model=MessageResponse, status_code=201)
async def create_tax_bracket(bracket: TaxBracketCreate):
    """Add a new tax bracket."""
    try:
        setup.add_tax_bracket(bracket.country, bracket.tax_type, bracket.income_limit, bracket.rate)
        return MessageResponse(message="Tax bracket created successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/tax-brackets/{bracket_id}", response_model=MessageResponse)
async def delete_tax_bracket(bracket_id: int):
    """Delete a tax bracket."""
    try:
        setup.delete_tax_bracket(bracket_id)
        return MessageResponse(message=f"Tax bracket {bracket_id} deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== People Endpoints =====

@app.get("/api/people/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int):
    """Get a specific person by ID."""
    conn = setup.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, work_share, gross_income, tax_paid, net_income FROM people WHERE id=?", (person_id,))
    person = cursor.fetchone()
    conn.close()

    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    return PersonResponse(
        id=person[0], name=person[1], work_share=person[2],
        gross_income=person[3], tax_paid=person[4], net_income=person[5]
    )


@app.get("/api/people/history/{name}", response_model=List[dict])
async def get_person_history(name: str):
    """Get all records for a person by name."""
    records = setup.fetch_records_by_person(name)
    return [
        {
            "person_id": r[0],
            "record_id": r[1],
            "name": r[2],
            "work_share": r[3],
            "gross_income": r[4],
            "tax_paid": r[5],
            "net_income": r[6],
            "created_at": r[7]
        } for r in records
    ]


# ===== Report Endpoints =====

@app.get("/api/reports/revenue-summary")
async def revenue_summary():
    """Get revenue summary by year."""
    rows = setup.get_revenue_summary()
    return [
        {
            "year": r[0],
            "total_revenue": r[1],
            "total_costs": r[2],
            "net_income": r[3]
        } for r in rows
    ]


@app.get("/api/reports/top-people")
async def top_people(limit: int = Query(10, ge=1, le=50)):
    """Get top people by net income."""
    rows = setup.get_top_people(limit)
    return [
        {
            "name": r[0],
            "total_gross": r[1],
            "total_tax_paid": r[2],
            "total_net": r[3]
        } for r in rows
    ]


@app.get("/api/reports/statistics")
async def overall_statistics():
    """Get overall database statistics."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*),
               COALESCE(SUM(revenue), 0),
               COALESCE(SUM(total_costs), 0),
               COALESCE(SUM(tax_amount), 0),
               COALESCE(SUM(net_income_group), 0),
               COALESCE(AVG(CASE
                   WHEN group_income > 0 THEN tax_amount * 100.0 / group_income
                   ELSE 0
               END), 0)
        FROM tax_records
    """)
    result = cursor.fetchone()
    total_records = result[0] or 0
    total_rev = result[1] or 0
    total_costs = result[2] or 0
    total_tax = result[3] or 0
    total_net = result[4] or 0
    avg_rate = result[5] or 0

    cursor.execute("SELECT COUNT(*), COUNT(DISTINCT name) FROM people")
    people_result = cursor.fetchone()
    total_people_entries = people_result[0] or 0
    unique_people = people_result[1] or 0

    conn.close()

    return {
        "total_records": total_records,
        "total_revenue": float(total_rev),
        "total_costs": float(total_costs),
        "total_tax": float(total_tax),
        "total_net_income": float(total_net),
        "average_tax_rate": float(avg_rate),
        "total_people_entries": total_people_entries,
        "unique_people": unique_people
    }


# ===== Visualization Endpoints =====

def create_stunning_html(plotly_fig, title, emoji, description):
    """Wrap Plotly figure in world-class premium HTML template."""
    plot_config = {'displayModeBar': True, 'displaylogo': False}
    plotly_html = plotly_fig.to_html(include_plotlyjs='cdn', full_html=False, config=plot_config)

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - MoneySplit Analytics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0a0f;
            --bg-secondary: #13131a;
            --bg-tertiary: #1a1a24;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-tertiary: #ec4899;
            --text-primary: #ffffff;
            --text-secondary: #a1a1aa;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --glow-purple: rgba(139, 92, 246, 0.5);
            --glow-pink: rgba(236, 72, 153, 0.5);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 0;
            position: relative;
            overflow-x: hidden;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        /* ULTRA-PREMIUM MESH GRADIENT BACKGROUND */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background:
                radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139, 92, 246, 0.15), transparent),
                radial-gradient(ellipse 60% 40% at 10% 40%, rgba(99, 102, 241, 0.1), transparent),
                radial-gradient(ellipse 60% 40% at 90% 60%, rgba(236, 72, 153, 0.1), transparent);
            pointer-events: none;
        }}

        /* ANIMATED GRID PATTERN */
        body::after {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background-image:
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 50px 50px;
            mask-image: radial-gradient(ellipse 100% 100% at 50% 50%, black 40%, transparent 100%);
            pointer-events: none;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 60px 40px;
            position: relative;
            z-index: 1;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 40px 20px;
            }}
        }}

        /* NAVIGATION BAR */
        .nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            backdrop-filter: blur(20px) saturate(180%);
            background: rgba(10, 10, 15, 0.7);
            border-bottom: 1px solid var(--border-subtle);
        }}

        .nav-content {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 16px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-family: 'Poppins', sans-serif;
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
        }}

        /* HERO SECTION */
        .header {{
            margin-top: 80px;
            margin-bottom: 48px;
            text-align: center;
            animation: fadeInDown 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .emoji {{
            font-size: 80px;
            display: inline-block;
            margin-bottom: 20px;
            filter: drop-shadow(0 0 40px var(--glow-purple));
            animation: float 6s ease-in-out infinite;
        }}

        @keyframes float {{
            0%, 100% {{ transform: translateY(0) scale(1); }}
            50% {{ transform: translateY(-20px) scale(1.05); }}
        }}

        h1 {{
            font-family: 'Poppins', sans-serif;
            font-size: clamp(32px, 5vw, 64px);
            font-weight: 800;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #ffffff 0%, #a1a1aa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
            line-height: 1.1;
        }}

        .description {{
            font-size: 18px;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 32px;
            font-weight: 500;
        }}

        /* STATS BAR */
        .stats-bar {{
            display: flex;
            gap: 32px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 48px;
            animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .stat-label {{
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }}

        /* CHART CONTAINER */
        .chart-container {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 24px;
            padding: 48px;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
        }}

        .chart-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-primary), var(--accent-secondary), transparent);
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* FOOTER BRANDING */
        .branding {{
            text-align: center;
            margin-top: 60px;
            padding: 40px;
            border-top: 1px solid var(--border-subtle);
        }}

        .branding-title {{
            font-family: 'Poppins', sans-serif;
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}

        .branding-subtitle {{
            color: var(--text-secondary);
            font-size: 14px;
        }}

        .branding-links {{
            margin-top: 20px;
            display: flex;
            gap: 24px;
            justify-content: center;
        }}

        .branding-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s;
        }}

        .branding-link:hover {{
            color: var(--accent-primary);
        }}

        /* PLOTLY OVERRIDES */
        .js-plotly-plot {{
            background: transparent !important;
        }}

        .js-plotly-plot .plotly {{
            border-radius: 12px;
        }}

        /* SCROLLBAR */
        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--bg-tertiary);
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #2a2a3a;
        }}
    </style>
</head>
<body>
    <!-- NAVIGATION -->
    <nav class="nav">
        <div class="nav-content">
            <div class="logo">
                <span>💰</span>
                <span>MoneySplit</span>
            </div>
            <div class="badge">Analytics</div>
        </div>
    </nav>

    <div class="container">
        <!-- HERO HEADER -->
        <div class="header">
            <div class="emoji">{emoji}</div>
            <h1>{title}</h1>
            <p class="description">{description}</p>
        </div>

        <!-- STATS BAR -->
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">Real-time</div>
                <div class="stat-label">Data</div>
            </div>
            <div class="stat">
                <div class="stat-value">Interactive</div>
                <div class="stat-label">Charts</div>
            </div>
            <div class="stat">
                <div class="stat-value">ML-Powered</div>
                <div class="stat-label">Insights</div>
            </div>
        </div>

        <!-- CHART VISUALIZATION -->
        <div class="chart-container">
            {plotly_html}
        </div>

        <!-- FOOTER BRANDING -->
        <div class="branding">
            <div class="branding-title">💰 MoneySplit</div>
            <div class="branding-subtitle">Enterprise-grade Commission Splitting & Tax Analytics Platform</div>
            <div class="branding-links">
                <a href="http://localhost:8000/docs" class="branding-link">API Documentation</a>
                <a href="http://localhost:3000" class="branding-link">Dashboard</a>
                <a href="http://localhost:8000" class="branding-link">More Reports</a>
            </div>
        </div>
    </div>
</body>
</html>
    """


@app.get("/api/visualizations/revenue-summary", response_class=HTMLResponse)
async def revenue_summary_viz(view: str = Query("yearly", regex="^(yearly|monthly)$")):
    """Get revenue summary visualization as HTML (yearly or monthly view)."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    if view == "monthly":
        # Monthly view
        cursor.execute("""
            SELECT strftime('%Y-%m', created_at) as period,
                   SUM(revenue) as total_revenue,
                   SUM(total_costs) as total_costs,
                   SUM(net_income_group) as net_income,
                   COUNT(*) as num_projects
            FROM tax_records
            GROUP BY period
            ORDER BY period ASC
        """)
        title_suffix = "by Month"
        x_label = "Month"
    else:
        # Yearly view
        cursor.execute("""
            SELECT strftime('%Y', created_at) as period,
                   SUM(revenue) as total_revenue,
                   SUM(total_costs) as total_costs,
                   SUM(net_income_group) as net_income,
                   COUNT(*) as num_projects
            FROM tax_records
            GROUP BY period
            ORDER BY period ASC
        """)
        title_suffix = "by Year"
        x_label = "Year"

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return HTMLResponse("<h3>No data available</h3>")

    periods = [row[0] for row in rows]
    revenues = [row[1] for row in rows]
    costs = [row[2] for row in rows]
    net_incomes = [row[3] for row in rows]
    num_projects = [row[4] for row in rows]

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(f"Revenue & Costs {title_suffix}", f"Net Income {title_suffix}", f"Number of Projects {title_suffix}"),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # Revenue & Costs
    fig.add_trace(
        go.Bar(name="Revenue", x=periods, y=revenues, marker_color='rgb(102, 126, 234)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name="Costs", x=periods, y=costs, marker_color='rgb(239, 68, 68)'),
        row=1, col=1
    )

    # Net Income
    fig.add_trace(
        go.Scatter(name="Net Income", x=periods, y=net_incomes,
                   mode='lines+markers', marker_color='rgb(16, 185, 129)',
                   line=dict(width=4), fill='tozeroy'),
        row=2, col=1
    )

    # Number of Projects
    fig.add_trace(
        go.Bar(name="Projects", x=periods, y=num_projects,
               marker_color='rgb(251, 191, 36)', showlegend=False),
        row=3, col=1
    )

    fig.update_layout(
        title_text="",
        showlegend=True,
        height=1000,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 12, 41, 0.3)',
        font=dict(color='white', size=14),
        legend=dict(bgcolor='rgba(15, 12, 41, 0.8)', bordercolor='rgba(102, 126, 234, 0.3)', borderwidth=2)
    )
    fig.update_xaxes(title_text=x_label, gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(title_text="Amount ($)", row=1, col=1, gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(title_text="Net Income ($)", row=2, col=1, gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(title_text="Projects", row=3, col=1, gridcolor='rgba(255, 255, 255, 0.1)')

    description = f"Comprehensive {view} revenue analysis showing total earnings, operational costs, net income trends, and project volume. Data sorted chronologically from oldest to newest."

    return HTMLResponse(create_stunning_html(
        fig,
        f"Revenue Summary ({view.title()})",
        "📈",
        description
    ))


@app.get("/api/visualizations/monthly-trends", response_class=HTMLResponse)
async def monthly_trends_viz():
    """Get monthly trends visualization as HTML."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', created_at) as month,
               SUM(revenue) as total_revenue,
               SUM(total_costs) as total_costs,
               SUM(net_income_group) as total_profit,
               COUNT(*) as num_projects,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate
        FROM tax_records
        GROUP BY month
        ORDER BY month
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return HTMLResponse("<h3>No data available</h3>")

    months = [row[0] for row in rows]
    revenues = [row[1] for row in rows]
    costs = [row[2] for row in rows]
    profits = [row[3] for row in rows]
    projects = [row[4] for row in rows]
    tax_rates = [row[5] for row in rows]

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Revenue & Costs Over Time", "Profit Trend", "Projects & Tax Rate"),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": True}]]
    )

    fig.add_trace(go.Bar(name="Revenue", x=months, y=revenues, marker_color='#667eea'), row=1, col=1)
    fig.add_trace(go.Bar(name="Costs", x=months, y=costs, marker_color='#ef4444'), row=1, col=1)
    fig.add_trace(go.Scatter(name="Profit", x=months, y=profits, mode='lines+markers',
                            marker_color='#10b981', line=dict(width=3)), row=2, col=1)
    fig.add_trace(go.Bar(name="# Projects", x=months, y=projects, marker_color='#f093fb'), row=3, col=1)

    fig.update_layout(
        title_text="",
        showlegend=True,
        height=1000,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 12, 41, 0.3)',
        font=dict(color='white', size=14),
        legend=dict(bgcolor='rgba(15, 12, 41, 0.8)', bordercolor='rgba(102, 126, 234, 0.3)', borderwidth=2)
    )
    fig.update_xaxes(gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)')

    return HTMLResponse(create_stunning_html(
        fig,
        "Monthly Trends",
        "📊",
        "Detailed month-over-month analysis tracking revenue, costs, profit trends, and project activity patterns."
    ))


@app.get("/api/visualizations/work-distribution", response_class=HTMLResponse)
async def work_distribution_viz():
    """Get work distribution visualization as HTML with detailed team analytics."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    # Get overall team stats
    cursor.execute("""
        SELECT name, COUNT(*) as num_projects,
               SUM(gross_income) as total_gross, SUM(net_income) as total_net,
               SUM(tax_paid) as total_tax, AVG(work_share) as avg_work_share
        FROM people GROUP BY name ORDER BY total_net DESC
        LIMIT 12
    """)
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return HTMLResponse("<h3>No data available</h3>")

    names = [row[0] for row in rows]
    projects = [row[1] for row in rows]
    gross_incomes = [row[2] for row in rows]
    net_incomes = [row[3] for row in rows]
    tax_paid = [row[4] for row in rows]
    avg_shares = [row[5] * 100 for row in rows]  # Convert to percentage

    # Get monthly performance for top contributor
    top_person = names[0]
    cursor.execute("""
        SELECT strftime('%Y-%m', t.created_at) as month,
               SUM(p.net_income) as monthly_income
        FROM people p
        JOIN tax_records t ON p.record_id = t.id
        WHERE p.name = ?
        GROUP BY month
        ORDER BY month
    """, (top_person,))
    monthly_data = cursor.fetchall()
    months = [row[0] for row in monthly_data]
    monthly_income = [row[1] for row in monthly_data]

    conn.close()

    # Create comprehensive 6-chart layout
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "💰 Total Earnings Leaderboard",
            "📊 Projects per Person",
            "💸 Tax Paid by Person",
            "🎯 Average Work Share %",
            f"📈 {top_person}'s Monthly Income",
            "💵 Gross vs Net Income"
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # 1. Earnings leaderboard
    fig.add_trace(
        go.Bar(x=names, y=net_incomes, marker_color='#10b981',
               text=[f'${v:,.0f}' for v in net_incomes], textposition='outside'),
        row=1, col=1
    )

    # 2. Projects per person
    fig.add_trace(
        go.Bar(x=names, y=projects, marker_color='#667eea',
               text=projects, textposition='outside'),
        row=1, col=2
    )

    # 3. Tax paid
    fig.add_trace(
        go.Bar(x=names, y=tax_paid, marker_color='#ef4444',
               text=[f'${v:,.0f}' for v in tax_paid], textposition='outside'),
        row=2, col=1
    )

    # 4. Average work share
    fig.add_trace(
        go.Bar(x=names, y=avg_shares, marker_color='#f59e0b',
               text=[f'{v:.1f}%' for v in avg_shares], textposition='outside'),
        row=2, col=2
    )

    # 5. Top person monthly income
    fig.add_trace(
        go.Scatter(x=months, y=monthly_income, mode='lines+markers',
                   line=dict(color='#8b5cf6', width=3), marker=dict(size=10),
                   fill='tozeroy'),
        row=3, col=1
    )

    # 6. Gross vs Net comparison
    fig.add_trace(
        go.Bar(name='Gross', x=names, y=gross_incomes, marker_color='#667eea'),
        row=3, col=2
    )
    fig.add_trace(
        go.Bar(name='Net', x=names, y=net_incomes, marker_color='#10b981'),
        row=3, col=2
    )

    fig.update_layout(
        title_text="",
        showlegend=True,
        height=1400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 12, 41, 0.3)',
        font=dict(color='white', size=13),
        legend=dict(bgcolor='rgba(15, 12, 41, 0.8)', bordercolor='rgba(102, 126, 234, 0.3)', borderwidth=2)
    )

    # Update all axes
    fig.update_xaxes(gridcolor='rgba(255, 255, 255, 0.1)', tickangle=-45)
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)')

    # Add labels
    fig.update_yaxes(title_text="Net Income ($)", row=1, col=1)
    fig.update_yaxes(title_text="Projects", row=1, col=2)
    fig.update_yaxes(title_text="Tax Paid ($)", row=2, col=1)
    fig.update_yaxes(title_text="Work Share (%)", row=2, col=2)
    fig.update_yaxes(title_text="Income ($)", row=3, col=1)
    fig.update_yaxes(title_text="Amount ($)", row=3, col=2)

    return HTMLResponse(create_stunning_html(
        fig,
        "Team Performance Analytics",
        "👥",
        "Comprehensive team performance dashboard showing earnings, project distribution, tax burden, work shares, and individual performance trends."
    ))


@app.get("/api/visualizations/tax-comparison", response_class=HTMLResponse)
async def tax_comparison_viz():
    """Get comprehensive tax analysis visualization with 6 detailed comparison charts."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    # 1. Get tax strategy comparison by country and type
    cursor.execute("""
        SELECT tax_origin, tax_option, COUNT(*) as records,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate,
               SUM(tax_amount * num_people) as total_tax_paid,
               SUM(net_income_group) as total_net_income
        FROM tax_records
        GROUP BY tax_origin, tax_option
        ORDER BY tax_origin, tax_option
    """)
    strategy_data = cursor.fetchall()

    # 2. Get Individual vs Business comparison
    cursor.execute("""
        SELECT tax_option,
               COUNT(*) as count,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate,
               SUM(tax_amount * num_people) as total_tax,
               AVG(net_income_per_person) as avg_net_per_person
        FROM tax_records
        GROUP BY tax_option
        ORDER BY tax_option
    """)
    ind_vs_bus = cursor.fetchall()

    # 3. Get tax burden over time (monthly)
    cursor.execute("""
        SELECT strftime('%Y-%m', created_at) as month,
               tax_option,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate
        FROM tax_records
        GROUP BY month, tax_option
        ORDER BY month ASC, tax_option
    """)
    monthly_tax = cursor.fetchall()

    # 4. Get country-specific breakdown
    cursor.execute("""
        SELECT tax_origin,
               COUNT(*) as projects,
               SUM(tax_amount * num_people) as total_tax,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate
        FROM tax_records
        GROUP BY tax_origin
        ORDER BY total_tax DESC
    """)
    country_breakdown = cursor.fetchall()

    # 5. Get effective tax rate distribution
    cursor.execute("""
        SELECT tax_origin || ' - ' || tax_option as strategy,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate,
               MIN(tax_amount * 100.0 / NULLIF(group_income, 0)) as min_rate,
               MAX(tax_amount * 100.0 / NULLIF(group_income, 0)) as max_rate
        FROM tax_records
        GROUP BY tax_origin, tax_option
        ORDER BY avg_rate
    """)
    rate_distribution = cursor.fetchall()

    conn.close()

    if not strategy_data:
        return HTMLResponse("<h3>No tax data available</h3>")

    # Create 6-chart comprehensive dashboard
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "📊 Average Tax Rate by Strategy",
            "💰 Individual vs Business Tax Comparison",
            "📈 Tax Rate Trend Over Time",
            "🌍 Total Tax Paid by Country",
            "🎯 Effective Tax Rate Range",
            "💸 Net Income After Tax by Strategy"
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # Chart 1: Average Tax Rate by Strategy (with labels)
    strategies = [f"{row[0]} - {row[1]}" for row in strategy_data]
    avg_rates = [row[3] for row in strategy_data]
    colors_1 = ['#10b981' if rate < 20 else '#f59e0b' if rate < 30 else '#ef4444' for rate in avg_rates]

    fig.add_trace(
        go.Bar(
            x=strategies,
            y=avg_rates,
            marker_color=colors_1,
            text=[f'{rate:.1f}%' for rate in avg_rates],
            textposition='outside',
            name='Avg Tax Rate'
        ),
        row=1, col=1
    )

    # Chart 2: Individual vs Business Direct Comparison
    if len(ind_vs_bus) >= 2:
        tax_types = [row[0] for row in ind_vs_bus]
        avg_rates_comp = [row[2] for row in ind_vs_bus]
        avg_net = [row[4] for row in ind_vs_bus]

        fig.add_trace(
            go.Bar(
                name='Avg Tax Rate %',
                x=tax_types,
                y=avg_rates_comp,
                marker_color='#ef4444',
                text=[f'{v:.1f}%' for v in avg_rates_comp],
                textposition='outside',
                yaxis='y'
            ),
            row=1, col=2
        )

        fig.add_trace(
            go.Bar(
                name='Avg Net Income/Person',
                x=tax_types,
                y=avg_net,
                marker_color='#10b981',
                text=[f'${v:,.0f}' for v in avg_net],
                textposition='outside',
                yaxis='y2'
            ),
            row=1, col=2
        )

    # Chart 3: Tax Rate Trend Over Time (monthly)
    if monthly_tax:
        # Group by tax_option
        individual_data = [(row[0], row[2]) for row in monthly_tax if row[1] == 'Individual']
        business_data = [(row[0], row[2]) for row in monthly_tax if row[1] == 'Business']

        if individual_data:
            months_ind, rates_ind = zip(*individual_data)
            fig.add_trace(
                go.Scatter(
                    name='Individual Tax',
                    x=list(months_ind),
                    y=list(rates_ind),
                    mode='lines+markers',
                    marker_color='#667eea',
                    line=dict(width=3)
                ),
                row=2, col=1
            )

        if business_data:
            months_bus, rates_bus = zip(*business_data)
            fig.add_trace(
                go.Scatter(
                    name='Business Tax',
                    x=list(months_bus),
                    y=list(rates_bus),
                    mode='lines+markers',
                    marker_color='#f093fb',
                    line=dict(width=3)
                ),
                row=2, col=1
            )

    # Chart 4: Total Tax Paid by Country
    countries = [row[0] for row in country_breakdown]
    total_taxes = [row[2] for row in country_breakdown]
    fig.add_trace(
        go.Bar(
            x=countries,
            y=total_taxes,
            marker_color='#667eea',
            text=[f'${v:,.0f}' for v in total_taxes],
            textposition='outside',
            name='Total Tax Paid'
        ),
        row=2, col=2
    )

    # Chart 5: Effective Tax Rate Range (min-max)
    rate_strategies = [row[0] for row in rate_distribution]
    avg_rates_dist = [row[1] for row in rate_distribution]
    min_rates = [row[2] for row in rate_distribution]
    max_rates = [row[3] for row in rate_distribution]

    fig.add_trace(
        go.Bar(
            name='Average Rate',
            x=rate_strategies,
            y=avg_rates_dist,
            marker_color='#10b981',
            text=[f'{v:.1f}%' for v in avg_rates_dist],
            textposition='outside'
        ),
        row=3, col=1
    )

    # Chart 6: Net Income After Tax by Strategy
    net_incomes = [row[5] for row in strategy_data]
    fig.add_trace(
        go.Bar(
            x=strategies,
            y=net_incomes,
            marker_color='#10b981',
            text=[f'${v:,.0f}' for v in net_incomes],
            textposition='outside',
            name='Total Net Income'
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        title_text="",
        showlegend=True,
        height=1400,  # Taller for 6 charts
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 12, 41, 0.3)',
        font=dict(color='white', size=12),
        legend=dict(
            bgcolor='rgba(15, 12, 41, 0.8)',
            bordercolor='rgba(102, 126, 234, 0.3)',
            borderwidth=2
        )
    )

    # Update all axes
    fig.update_xaxes(gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)')

    # Specific axis labels
    fig.update_yaxes(title_text="Tax Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Tax Rate (%)", row=1, col=2)
    fig.update_yaxes(title_text="Tax Rate (%)", row=2, col=1)
    fig.update_yaxes(title_text="Total Tax ($)", row=2, col=2)
    fig.update_yaxes(title_text="Tax Rate (%)", row=3, col=1)
    fig.update_yaxes(title_text="Net Income ($)", row=3, col=2)

    return HTMLResponse(create_stunning_html(
        fig,
        "Tax Strategy Comparison",
        "💼",
        "Comprehensive tax analysis with 6 detailed charts comparing tax strategies, rates, trends, and net income across countries and tax types."
    ))


@app.get("/api/visualizations/person-performance/{name}", response_class=HTMLResponse)
async def person_performance_viz(name: str):
    """Get person performance timeline visualization as HTML."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m-%d', t.created_at) as date, p.gross_income, p.tax_paid,
               p.net_income, p.work_share, t.id as record_id
        FROM people p JOIN tax_records t ON p.record_id = t.id
        WHERE p.name = ? ORDER BY t.created_at
    """, (name,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return HTMLResponse(f"<h3>No data found for {name}</h3>")

    dates = [row[0] for row in rows]
    gross = [row[1] for row in rows]
    net = [row[3] for row in rows]
    work_shares = [row[4] * 100 for row in rows]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f"{name}'s Income Over Time", f"{name}'s Work Share Percentage"),
        vertical_spacing=0.15
    )

    fig.add_trace(go.Scatter(name="Gross Income", x=dates, y=gross, mode='lines+markers',
                            marker_color='#667eea', line=dict(width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(name="Net Income", x=dates, y=net, mode='lines+markers',
                            marker_color='#10b981', line=dict(width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(name="Work Share %", x=dates, y=work_shares, mode='lines+markers',
                            marker_color='#f093fb', line=dict(width=3)), row=2, col=1)

    fig.update_layout(
        title_text="",
        showlegend=True,
        height=800,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 12, 41, 0.3)',
        font=dict(color='white', size=14),
        legend=dict(bgcolor='rgba(15, 12, 41, 0.8)', bordercolor='rgba(102, 126, 234, 0.3)', borderwidth=2)
    )
    fig.update_xaxes(title_text="Date", gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(title_text="Income ($)", row=1, col=1, gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(title_text="Work Share (%)", row=2, col=1, gridcolor='rgba(255, 255, 255, 0.1)')

    return HTMLResponse(create_stunning_html(
        fig,
        f"Performance Timeline - {name}",
        "🎯",
        f"Individual performance tracking for {name}, displaying income progression and work contribution over time."
    ))


@app.get("/api/visualizations/project-profitability", response_class=HTMLResponse)
async def project_profitability_viz():
    """Get project profitability analysis visualization as HTML."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, revenue, total_costs, net_income_group, tax_amount, num_people,
               (net_income_group * 100.0 / NULLIF(revenue - total_costs, 0)) as profit_margin,
               (net_income_group * 100.0 / NULLIF(total_costs, 0)) as roi
        FROM tax_records WHERE revenue > 0 ORDER BY created_at
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return HTMLResponse("<h3>No data available</h3>")

    record_ids = [f"#{row[0]}" for row in rows]
    profit_margins = [row[6] if row[6] else 0 for row in rows]
    rois = [row[7] if row[7] else 0 for row in rows]
    revenues = [row[1] for row in rows]
    costs = [row[2] for row in rows]
    profits = [row[3] for row in rows]
    team_sizes = [row[5] for row in rows]

    colors = ['#10b981' if pm > 30 else '#f093fb' if pm > 10 else '#ef4444' for pm in profit_margins]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Profit Margins (%)", "ROI (%)", "Revenue Breakdown", "Profit vs Team Size"),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "scatter"}]]
    )

    fig.add_trace(go.Bar(x=record_ids, y=profit_margins, marker_color=colors), row=1, col=1)
    fig.add_trace(go.Bar(x=record_ids, y=rois, marker_color='#667eea'), row=1, col=2)
    fig.add_trace(go.Bar(name="Costs", x=record_ids, y=costs, marker_color='#ef4444'), row=2, col=1)
    fig.add_trace(go.Bar(name="Profit", x=record_ids, y=profits, marker_color='#10b981'), row=2, col=1)
    fig.add_trace(go.Scatter(x=team_sizes, y=profits, mode='markers',
                            marker=dict(size=12, color='#f093fb', line=dict(width=2, color='white'))), row=2, col=2)

    fig.update_layout(
        title_text="",
        showlegend=True,
        height=900,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 12, 41, 0.3)',
        font=dict(color='white', size=14),
        legend=dict(bgcolor='rgba(15, 12, 41, 0.8)', bordercolor='rgba(102, 126, 234, 0.3)', borderwidth=2)
    )
    fig.update_xaxes(gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)')

    return HTMLResponse(create_stunning_html(
        fig,
        "Project Profitability",
        "💰",
        "Comprehensive profitability analysis displaying profit margins, ROI, revenue breakdown, and team size correlation for all projects."
    ))


# ===== PDF Export Endpoints =====

@app.get("/api/export/record/{record_id}/pdf", response_class=FileResponse)
async def export_record_pdf(record_id: int):
    """Export a specific record to PDF."""
    record = setup.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found")

    people = setup.fetch_people_by_record(record_id)

    filepath = pdf_generator.generate_project_pdf(
        record, people,
        filepath=f"reports/project_{record_id}.pdf"
    )
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"project_{record_id}.pdf"
    )


@app.get("/api/export/summary/pdf", response_class=FileResponse)
async def export_summary_pdf(limit: int = Query(20, ge=1, le=100)):
    """Export summary report to PDF."""
    records = setup.fetch_last_records(limit)

    # Get statistics
    conn = setup.get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*),
               COALESCE(SUM(revenue), 0),
               COALESCE(SUM(total_costs), 0),
               COALESCE(SUM(tax_amount), 0),
               COALESCE(SUM(net_income_group), 0),
               COALESCE(AVG(CASE
                   WHEN group_income > 0 THEN tax_amount * 100.0 / group_income
                   ELSE 0
               END), 0)
        FROM tax_records
    """)
    result = cursor.fetchone()

    cursor.execute("SELECT COUNT(DISTINCT name) FROM people")
    unique_people = cursor.fetchone()[0] or 0
    conn.close()

    stats = {
        'total_records': result[0],
        'total_revenue': result[1],
        'total_costs': result[2],
        'total_tax': result[3],
        'total_net_income': result[4],
        'average_tax_rate': result[5],
        'unique_people': unique_people
    }

    filepath = pdf_generator.generate_summary_pdf(records, stats)
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="summary_report.pdf"
    )


@app.get("/api/export/forecast/pdf", response_class=FileResponse)
async def export_forecast_pdf():
    """Export forecast report to PDF."""
    forecast = forecasting.forecast_revenue(3)
    filepath = pdf_generator.generate_forecast_pdf(forecast)
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="forecast_report.pdf"
    )


# ===== Forecasting Endpoints =====

@app.get("/api/forecast/revenue")
async def forecast_revenue_endpoint(months: int = Query(3, ge=1, le=12)):
    """Get revenue forecast for next N months."""
    forecast = forecasting.forecast_revenue(months)
    return forecast


@app.get("/api/forecast/comprehensive")
async def comprehensive_forecast_endpoint():
    """Get comprehensive forecast with all insights."""
    forecast = forecasting.comprehensive_forecast()
    return forecast


@app.get("/api/forecast/tax-optimization")
async def tax_optimization_endpoint():
    """Get tax optimization recommendations."""
    analysis = forecasting.tax_optimization_analysis()
    return analysis


@app.get("/api/forecast/trends")
async def trend_analysis_endpoint():
    """Get trend analysis."""
    trends = forecasting.trend_analysis()
    return trends


# ===== Tax Comparison Endpoints =====

@app.get("/api/tax-comparison")
async def compare_tax_strategies(
    revenue: float = Query(..., description="Project revenue"),
    costs: float = Query(..., description="Total project costs"),
    num_people: int = Query(..., description="Number of people"),
    country: str = Query(..., description="Country (US or Spain)")
):
    """
    Compare all tax strategies (Individual vs Business with different distributions).
    Returns detailed breakdown showing which option saves the most money.
    """
    comparison = tax_comparison.calculate_all_tax_scenarios(revenue, costs, num_people, country)
    return comparison


@app.get("/api/optimal-strategy")
async def get_optimal_strategy(
    revenue: float = Query(..., description="Project revenue"),
    costs: float = Query(..., description="Total project costs"),
    num_people: int = Query(..., description="Number of people"),
    country: str = Query(..., description="Country"),
    state: str = Query(None, description="US State (CA, NY, TX, FL) - optional")
):
    """
    Get the optimal tax strategy using the enhanced tax engine.
    Returns all strategies with the optimal one highlighted.
    Supports US state taxes, UK, and Canada calculations.
    """
    try:
        result = tax_engine.get_optimal_strategy(revenue, costs, num_people, country, state)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/tax-optimization")
async def get_tax_optimization(
    revenue: float,
    costs: float,
    num_people: int,
    country: str,
    selected_type: str = Query(..., description="Individual or Business")
):
    """
    Get optimization summary showing if user's choice is optimal.
    """
    summary = tax_comparison.get_tax_optimization_summary(revenue, costs, num_people, country, selected_type)
    return summary


# ===== Root Endpoint =====

@app.get("/", response_class=HTMLResponse)
async def root():
    """API documentation homepage."""
    return HTMLResponse("""
    <html>
        <head>
            <title>MoneySplit API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #2c3e50; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .endpoint { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>🤑 MoneySplit API</h1>
            <p>RESTful API for commission-based income splitting with tax calculations.</p>

            <h2>📚 Documentation</h2>
            <div class="endpoint">
                <a href="/docs" target="_blank">Interactive API Documentation (Swagger UI)</a>
            </div>
            <div class="endpoint">
                <a href="/redoc" target="_blank">Alternative API Documentation (ReDoc)</a>
            </div>

            <h2>🚀 Quick Start</h2>
            <p>Base URL: <code>http://localhost:8000/api</code></p>

            <h3>Main Endpoints:</h3>
            <ul>
                <li><code>POST /api/projects</code> - Create new project</li>
                <li><code>GET /api/records</code> - Get records</li>
                <li><code>GET /api/tax-brackets</code> - Get tax brackets</li>
                <li><code>GET /api/reports/statistics</code> - Get statistics</li>
            </ul>

            <h3>Visualization Endpoints:</h3>
            <ul>
                <li><code>GET /api/visualizations/revenue-summary</code> - Revenue summary chart</li>
                <li><code>GET /api/visualizations/monthly-trends</code> - Monthly trends dashboard</li>
                <li><code>GET /api/visualizations/work-distribution</code> - Work distribution analysis</li>
                <li><code>GET /api/visualizations/tax-comparison</code> - Tax strategy comparison</li>
                <li><code>GET /api/visualizations/person-performance/{name}</code> - Person timeline</li>
                <li><code>GET /api/visualizations/project-profitability</code> - Profitability analysis</li>
            </ul>

            <h3>PDF Export Endpoints:</h3>
            <ul>
                <li><code>GET /api/export/record/{record_id}/pdf</code> - Export project to PDF</li>
                <li><code>GET /api/export/summary/pdf</code> - Export summary to PDF</li>
                <li><code>GET /api/export/forecast/pdf</code> - Export forecast to PDF</li>
            </ul>

            <h3>Forecasting Endpoints:</h3>
            <ul>
                <li><code>GET /api/forecast/revenue?months=3</code> - Revenue predictions</li>
                <li><code>GET /api/forecast/comprehensive</code> - Full forecast with insights</li>
                <li><code>GET /api/forecast/tax-optimization</code> - Tax optimization analysis</li>
                <li><code>GET /api/forecast/trends</code> - Trend analysis</li>
            </ul>
        </body>
    </html>
    """)


@app.get("/api/forecast/tax-impact")
async def forecast_with_tax_impact(
    current_revenue: float = Query(..., description="Current quarterly revenue"),
    growth_rate: float = Query(0.1, description="Expected growth rate (0.1 = 10%)"),
    quarters: int = Query(4, description="Number of quarters to forecast"),
    country: str = Query("US", description="Country"),
    state: str = Query(None, description="US State (optional)")
):
    """
    Forecast revenue with tax impact analysis and strategy recommendations.
    Shows when to switch tax structures based on revenue thresholds.
    """
    forecasts = []

    for q in range(1, quarters + 1):
        projected_revenue = current_revenue * ((1 + growth_rate) ** q)
        costs = projected_revenue * 0.2  # Assume 20% costs

        # Calculate all strategies for this revenue level
        result = tax_engine.get_optimal_strategy(projected_revenue, costs, 2, country, state)

        # Find breakeven points
        individual = next((s for s in result['all_strategies'] if s['strategy_name'] == 'Individual Tax'), None)
        business_mixed = next((s for s in result['all_strategies'] if 'Mixed' in s['strategy_name']), None)

        recommendation = ""
        if business_mixed and individual:
            if business_mixed['net_income_group'] > individual['net_income_group']:
                savings = business_mixed['net_income_group'] - individual['net_income_group']
                recommendation = f"Switch to Business+Mixed - save ${savings:,.0f}/quarter"
            else:
                recommendation = "Stay with Individual tax"

        forecasts.append({
            "quarter": q,
            "projected_revenue": projected_revenue,
            "optimal_strategy": result['optimal']['strategy_name'],
            "take_home": result['optimal']['net_income_group'],
            "total_tax": result['optimal']['total_tax'],
            "effective_rate": result['optimal']['effective_rate'],
            "recommendation": recommendation,
            "all_strategies": result['all_strategies']
        })

    return {
        "current_revenue": current_revenue,
        "growth_rate": growth_rate * 100,
        "forecasts": forecasts
    }


@app.get("/api/breakeven-analysis")
async def breakeven_analysis(
    min_revenue: float = Query(50000, description="Minimum revenue to test"),
    max_revenue: float = Query(300000, description="Maximum revenue to test"),
    step: float = Query(10000, description="Revenue increment"),
    country: str = Query("US"),
    state: str = Query(None)
):
    """
    Find revenue breakeven points where tax strategies become optimal.
    Returns revenue thresholds for switching between Individual and Business tax.
    """
    results = []
    previous_optimal = None
    breakeven_points = []

    revenue = min_revenue
    while revenue <= max_revenue:
        costs = revenue * 0.2
        result = tax_engine.get_optimal_strategy(revenue, costs, 2, country, state)

        optimal_name = result['optimal']['strategy_name']

        # Detect strategy change
        if previous_optimal and previous_optimal != optimal_name:
            breakeven_points.append({
                "revenue_threshold": revenue,
                "switch_from": previous_optimal,
                "switch_to": optimal_name,
                "savings": result['savings']
            })

        results.append({
            "revenue": revenue,
            "optimal_strategy": optimal_name,
            "take_home": result['optimal']['net_income_group'],
            "effective_rate": result['optimal']['effective_rate']
        })

        previous_optimal = optimal_name
        revenue += step

    return {
        "breakeven_points": breakeven_points,
        "analysis": results
    }


@app.get("/api/analytics/year-over-year")
async def year_over_year_analysis():
    """
    Analyze project performance year-over-year.
    Groups projects by year and compares revenue, taxes, and strategy choices.
    """
    records = setup.fetch_last_records(100)

    years = {}
    for r in records:
        created_at = r[8] if len(r) > 8 else "2024-01-01"
        year = created_at[:4]

        if year not in years:
            years[year] = {
                "year": year,
                "total_revenue": 0,
                "total_tax": 0,
                "total_net_income": 0,
                "project_count": 0,
                "strategies": {},
                "avg_effective_rate": 0
            }

        revenue = r[3]
        tax = r[5]
        net = r[6]
        strategy = f"{r[1]} {r[2]}"

        years[year]["total_revenue"] += revenue
        years[year]["total_tax"] += tax
        years[year]["total_net_income"] += net
        years[year]["project_count"] += 1
        years[year]["strategies"][strategy] = years[year]["strategies"].get(strategy, 0) + 1

    # Calculate averages
    for year_data in years.values():
        if year_data["total_revenue"] > 0:
            year_data["avg_effective_rate"] = (year_data["total_tax"] / year_data["total_revenue"]) * 100

    return {
        "years": sorted(years.values(), key=lambda x: x["year"]),
        "comparison": [
            {
                "year": y["year"],
                "revenue": y["total_revenue"],
                "tax_paid": y["total_tax"],
                "take_home": y["total_net_income"],
                "projects": y["project_count"],
                "effective_rate": y["avg_effective_rate"]
            }
            for y in sorted(years.values(), key=lambda x: x["year"])
        ]
    }


@app.get("/api/analytics/strategy-effectiveness")
async def strategy_effectiveness():
    """
    Compare effectiveness of different tax strategies across all projects.
    Shows which strategies saved the most money.
    """
    records = setup.fetch_last_records(100)

    strategies = {}

    for r in records:
        strategy = f"{r[1]} {r[2]}"
        distribution = r[12] if len(r) > 12 else "N/A"
        if distribution != "N/A":
            strategy = f"{strategy} ({distribution})"

        if strategy not in strategies:
            strategies[strategy] = {
                "strategy": strategy,
                "count": 0,
                "total_revenue": 0,
                "total_tax": 0,
                "total_take_home": 0,
                "avg_effective_rate": 0
            }

        strategies[strategy]["count"] += 1
        strategies[strategy]["total_revenue"] += r[3]
        strategies[strategy]["total_tax"] += r[5]
        strategies[strategy]["total_take_home"] += r[6]

    # Calculate averages and rank
    for strat in strategies.values():
        if strat["total_revenue"] > 0:
            strat["avg_effective_rate"] = (strat["total_tax"] / strat["total_revenue"]) * 100
            strat["avg_take_home"] = strat["total_take_home"] / strat["count"]

    ranked = sorted(strategies.values(), key=lambda x: x["avg_effective_rate"])

    return {
        "strategies": ranked,
        "best_strategy": ranked[0] if ranked else None,
        "worst_strategy": ranked[-1] if ranked else None
    }


@app.get("/api/analytics/summary")
async def analytics_summary():
    """
    Overall analytics dashboard summary.
    Total projects, revenue, taxes, savings, and trends.
    """
    records = setup.fetch_last_records(100)

    if not records:
        return {
            "total_projects": 0,
            "total_revenue": 0,
            "total_tax_paid": 0,
            "total_take_home": 0,
            "avg_effective_rate": 0,
            "top_strategy": None
        }

    total_revenue = sum(r[3] for r in records)
    total_tax = sum(r[5] for r in records)
    total_take_home = sum(r[6] for r in records)

    # Find most used strategy
    strategy_counts = {}
    for r in records:
        strategy = f"{r[1]} {r[2]}"
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

    top_strategy = max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else None

    return {
        "total_projects": len(records),
        "total_revenue": total_revenue,
        "total_tax_paid": total_tax,
        "total_take_home": total_take_home,
        "avg_effective_rate": (total_tax / total_revenue * 100) if total_revenue > 0 else 0,
        "top_strategy": top_strategy,
        "avg_project_revenue": total_revenue / len(records),
        "avg_tax_per_project": total_tax / len(records)
    }


@app.get("/api/export-csv")
async def export_projects_csv(limit: int = Query(100, description="Number of records to export")):
    """
    Export projects to CSV format.
    Returns CSV file with all project data.
    """
    records = setup.fetch_last_records(limit)

    csv_lines = []
    csv_lines.append("id,country,tax_type,revenue,costs,tax_amount,net_income,created_at,num_people,distribution_method")

    for r in records:
        record_id = r[0]
        country = r[1]
        tax_type = r[2]
        revenue = r[3]
        costs = r[4]
        tax_amount = r[5]
        net_income = r[6]
        created_at = r[8] if len(r) > 8 else ""
        num_people = r[9] if len(r) > 9 else 0
        distribution = r[12] if len(r) > 12 else "N/A"

        csv_lines.append(f"{record_id},{country},{tax_type},{revenue},{costs},{tax_amount},{net_income},{created_at},{num_people},{distribution}")

    csv_content = "\n".join(csv_lines)

    from fastapi.responses import Response
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=moneysplit_export.csv"
        }
    )


@app.get("/api/export-json")
async def export_projects_json(limit: int = Query(100)):
    """
    Export projects to JSON format with full details.
    """
    records = setup.fetch_last_records(limit)

    projects = []
    for r in records:
        projects.append({
            "id": r[0],
            "country": r[1],
            "tax_type": r[2],
            "revenue": r[3],
            "costs": r[4],
            "tax_amount": r[5],
            "net_income": r[6],
            "net_income_per_person": r[7] if len(r) > 7 else 0,
            "created_at": r[8] if len(r) > 8 else "",
            "num_people": r[9] if len(r) > 9 else 0,
            "gross_income": r[10] if len(r) > 10 else 0,
            "distribution_method": r[12] if len(r) > 12 else "N/A"
        })

    return {
        "total_projects": len(projects),
        "export_date": datetime.now().isoformat(),
        "projects": projects
    }


@app.get("/api/compare-projects")
async def compare_projects(
    project_ids: str = Query(..., description="Comma-separated project IDs (e.g., 1,2,3)")
):
    """
    Compare multiple projects side-by-side.
    Shows tax differences, savings, and strategy effectiveness.
    """
    ids = [int(id.strip()) for id in project_ids.split(',')]

    comparisons = []
    for project_id in ids:
        record = setup.get_record_by_id(project_id)
        if not record:
            continue

        comparisons.append({
            "id": record[0],
            "country": record[1],
            "tax_type": record[2],
            "revenue": record[3],
            "costs": record[4],
            "gross_income": record[3] - record[4],
            "tax_amount": record[5],
            "net_income": record[6],
            "effective_rate": (record[5] / (record[3] - record[4]) * 100) if (record[3] - record[4]) > 0 else 0,
            "num_people": record[9] if len(record) > 9 else 0,
            "distribution": record[12] if len(record) > 12 else "N/A",
            "created_at": record[8] if len(record) > 8 else ""
        })

    if not comparisons:
        raise HTTPException(status_code=404, detail="No projects found")

    # Find best and worst
    best = max(comparisons, key=lambda x: x["net_income"])
    worst = min(comparisons, key=lambda x: x["net_income"])

    return {
        "projects": comparisons,
        "best_project": best,
        "worst_project": worst,
        "max_savings": best["net_income"] - worst["net_income"],
        "comparison_count": len(comparisons)
    }


@app.post("/api/import-csv-text")
async def import_projects_csv_text(csv_content: str):
    """
    Import multiple projects from CSV text content.

    Send CSV as plain text in request body.

    CSV Format:
    project_name,revenue,costs,country,tax_type,distribution_method,person1_name,person1_share,person2_name,person2_share
    """
    try:
        csv_data = io.StringIO(csv_content)
        reader = csv.DictReader(csv_data)

        imported_count = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
            try:
                # Parse people
                people = []
                for i in range(1, 10):  # Support up to 9 people
                    name_key = f"person{i}_name"
                    share_key = f"person{i}_share"

                    if name_key in row and row[name_key]:
                        people.append({
                            "name": row[name_key],
                            "work_share": float(row[share_key])
                        })

                if not people:
                    errors.append(f"Row {row_num}: No people defined")
                    continue

                # Create project
                project_data = ProjectCreate(
                    tax_origin=row['country'],
                    tax_option=row['tax_type'],
                    revenue=float(row['revenue']),
                    total_costs=float(row['costs']),
                    people=people,
                    distribution_method=row.get('distribution_method', 'N/A'),
                    project_name=row.get('project_name', f"Imported {datetime.now().strftime('%Y-%m-%d')}")
                )

                # Calculate taxes
                result = tax_engine.calculate_project_taxes(
                    revenue=project_data.revenue,
                    costs=project_data.total_costs,
                    num_people=len(people),
                    country=project_data.tax_origin,
                    tax_structure=project_data.tax_option,
                    distribution_method=project_data.distribution_method
                )

                # Store in database
                record_id = setup.insert_record(
                    tax_origin=project_data.tax_origin,
                    tax_option=project_data.tax_option,
                    revenue=project_data.revenue,
                    total_costs=project_data.total_costs,
                    tax_amount=result['total_tax'],
                    net_income_group=result['net_income_group'],
                    net_income_per_person=result['net_income_per_person'],
                    num_people=len(people),
                    group_income=result['gross_income'],
                    individual_income=result['gross_income'] / len(people),
                    distribution_method=project_data.distribution_method,
                    salary_amount=0
                )

                # Insert people
                for person in people:
                    person_income = result['gross_income'] * (person['work_share'] / 100)
                    person_tax = result['total_tax'] * (person['work_share'] / 100)
                    person_net = person_income - person_tax

                    setup.insert_person(
                        record_id=record_id,
                        name=person['name'],
                        work_share=person['work_share'],
                        gross_income=person_income,
                        tax_paid=person_tax,
                        net_income=person_net
                    )

                imported_count += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        return {
            "success": True,
            "imported_count": imported_count,
            "errors": errors if errors else None,
            "message": f"Successfully imported {imported_count} project(s)"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
