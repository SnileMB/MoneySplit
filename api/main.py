"""
MoneySplit FastAPI Application
RESTful API for commission-based income splitting with tax calculations.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DB import setup
from Logic import pdf_generator, forecasting
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
    """Create a new project with people and calculate taxes."""
    try:
        # Calculate totals
        total_costs = sum(project.costs)
        income = project.revenue - total_costs
        group_income = income
        individual_income = income / project.num_people if project.num_people > 0 else 0

        # Calculate tax
        if project.tax_type == "Individual":
            tax = setup.calculate_tax_from_db(individual_income, project.country, project.tax_type)
        else:
            tax = setup.calculate_tax_from_db(group_income, project.country, project.tax_type)

        # Calculate net incomes
        if project.tax_type == "Individual":
            net_income_per_person = individual_income - tax
            net_income_group = net_income_per_person * project.num_people
        else:
            net_income_group = group_income - tax
            net_income_per_person = net_income_group / project.num_people if project.num_people > 0 else 0

        # Save to database
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tax_records (
                num_people, revenue, total_costs, group_income, individual_income,
                tax_origin, tax_option, tax_amount,
                net_income_per_person, net_income_group
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            net_income_group
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
                net_income = gross_income - tax_paid

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
                "net_income_per_person": net_income_per_person
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
            num_people=r[9], group_income=r[10], individual_income=r[11]
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
    brackets = setup.get_tax_brackets(country, tax_type, include_id=True)
    return [
        TaxBracketResponse(
            id=b[0], income_limit=b[1], rate=b[2],
            country=country, tax_type=tax_type
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

@app.get("/api/visualizations/revenue-summary", response_class=HTMLResponse)
async def revenue_summary_viz():
    """Get revenue summary visualization as HTML."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    rows = setup.get_revenue_summary()
    if not rows:
        return HTMLResponse("<h3>No data available</h3>")

    years = [row[0] for row in rows]
    revenues = [row[1] for row in rows]
    costs = [row[2] for row in rows]
    net_incomes = [row[3] for row in rows]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Revenue & Costs by Year", "Net Income by Year"),
        vertical_spacing=0.15
    )

    fig.add_trace(
        go.Bar(name="Revenue", x=years, y=revenues, marker_color='rgb(55, 83, 109)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name="Costs", x=years, y=costs, marker_color='rgb(219, 64, 82)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name="Net Income", x=years, y=net_incomes,
                   mode='lines+markers', marker_color='rgb(50, 171, 96)',
                   line=dict(width=3)),
        row=2, col=1
    )

    fig.update_layout(
        title_text="Revenue Summary by Year",
        showlegend=True,
        height=700
    )
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
    fig.update_yaxes(title_text="Net Income ($)", row=2, col=1)

    return HTMLResponse(fig.to_html())


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

    fig.add_trace(go.Bar(name="Revenue", x=months, y=revenues, marker_color='rgb(55, 83, 109)'), row=1, col=1)
    fig.add_trace(go.Bar(name="Costs", x=months, y=costs, marker_color='rgb(219, 64, 82)'), row=1, col=1)
    fig.add_trace(go.Scatter(name="Profit", x=months, y=profits, mode='lines+markers',
                            marker_color='rgb(50, 171, 96)', line=dict(width=3)), row=2, col=1)
    fig.add_trace(go.Bar(name="# Projects", x=months, y=projects, marker_color='rgb(158, 202, 225)'), row=3, col=1)

    fig.update_layout(title_text="Monthly Trends Dashboard", showlegend=True, height=1000)
    return HTMLResponse(fig.to_html())


@app.get("/api/visualizations/work-distribution", response_class=HTMLResponse)
async def work_distribution_viz():
    """Get work distribution visualization as HTML."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, SUM(work_share) as total_work_share, COUNT(*) as num_projects,
               SUM(gross_income) as total_gross, SUM(net_income) as total_net
        FROM people GROUP BY name ORDER BY total_net DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return HTMLResponse("<h3>No data available</h3>")

    names = [row[0] for row in rows]
    work_shares = [row[1] for row in rows]
    net_incomes = [row[4] for row in rows]
    gross_incomes = [row[3] for row in rows]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Work Distribution", "Leaderboard", "Projects", "Gross vs Net"),
        specs=[[{"type": "pie"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
    )

    fig.add_trace(go.Pie(labels=names, values=work_shares, textinfo='label+percent'), row=1, col=1)
    fig.add_trace(go.Bar(name="Net Income", x=names, y=net_incomes, marker_color='rgb(50, 171, 96)'), row=1, col=2)
    fig.add_trace(go.Bar(name="Gross", x=names, y=gross_incomes, marker_color='rgb(55, 83, 109)'), row=2, col=2)
    fig.add_trace(go.Bar(name="Net", x=names, y=net_incomes, marker_color='rgb(50, 171, 96)'), row=2, col=2)

    fig.update_layout(title_text="Work Distribution & Team Performance", showlegend=True, height=900)
    return HTMLResponse(fig.to_html())


@app.get("/api/visualizations/tax-comparison", response_class=HTMLResponse)
async def tax_comparison_viz():
    """Get tax type comparison visualization as HTML."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tax_origin, tax_option, COUNT(*) as records, AVG(revenue) as avg_revenue,
               AVG(tax_amount) as avg_tax, AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate,
               SUM(net_income_group) as total_net
        FROM tax_records GROUP BY tax_origin, tax_option ORDER BY tax_origin, tax_option
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return HTMLResponse("<h3>No data available</h3>")

    labels = [f"{row[0]} - {row[1]}" for row in rows]
    avg_rates = [row[5] for row in rows]
    total_nets = [row[6] for row in rows]
    record_counts = [row[2] for row in rows]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Avg Tax Rate", "Total Net Income", "Revenue vs Tax", "Distribution"),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "pie"}]]
    )

    fig.add_trace(go.Bar(x=labels, y=avg_rates, marker_color='rgb(219, 64, 82)'), row=1, col=1)
    fig.add_trace(go.Bar(x=labels, y=total_nets, marker_color='rgb(50, 171, 96)'), row=1, col=2)
    fig.add_trace(go.Pie(labels=labels, values=record_counts, textinfo='label+percent'), row=2, col=2)

    fig.update_layout(title_text="Tax Strategy Comparison", showlegend=True, height=800)
    return HTMLResponse(fig.to_html())


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

    fig.add_trace(go.Scatter(name="Gross Income", x=dates, y=gross, mode='lines+markers'), row=1, col=1)
    fig.add_trace(go.Scatter(name="Net Income", x=dates, y=net, mode='lines+markers'), row=1, col=1)
    fig.add_trace(go.Scatter(name="Work Share %", x=dates, y=work_shares, mode='lines+markers',
                            marker_color='rgb(158, 202, 225)'), row=2, col=1)

    fig.update_layout(title_text=f"Performance Timeline: {name}", showlegend=True, height=800)
    return HTMLResponse(fig.to_html())


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

    colors = ['green' if pm > 30 else 'orange' if pm > 10 else 'red' for pm in profit_margins]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Profit Margins (%)", "ROI (%)", "Revenue Breakdown", "Profit vs Team Size"),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "scatter"}]]
    )

    fig.add_trace(go.Bar(x=record_ids, y=profit_margins, marker_color=colors), row=1, col=1)
    fig.add_trace(go.Bar(x=record_ids, y=rois, marker_color='rgb(55, 83, 109)'), row=1, col=2)
    fig.add_trace(go.Bar(name="Costs", x=record_ids, y=costs, marker_color='rgb(219, 64, 82)'), row=2, col=1)
    fig.add_trace(go.Bar(name="Profit", x=record_ids, y=profits, marker_color='rgb(50, 171, 96)'), row=2, col=1)
    fig.add_trace(go.Scatter(x=team_sizes, y=profits, mode='markers', marker=dict(size=10)), row=2, col=2)

    fig.update_layout(title_text="Project Profitability Analysis", showlegend=True, height=900)
    return HTMLResponse(fig.to_html())


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
