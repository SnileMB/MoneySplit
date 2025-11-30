"""
Comprehensive data generation script for MoneySplit.
Creates realistic historical data across 12 months with various patterns.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Tuple

# Database connection
DB_PATH = "example.db"

# Realistic team member names
TEAM_MEMBERS = [
    "Alice Johnson",
    "Bob Smith",
    "Carol Williams",
    "David Brown",
    "Emma Davis",
    "Frank Miller",
    "Grace Wilson",
    "Henry Moore",
    "Isabel Taylor",
    "Jack Anderson",
    "Kate Thomas",
    "Leo Jackson",
]

# Countries with their tax types
COUNTRIES = [
    ("US", "Individual"),
    ("US", "Business"),
    ("Spain", "Individual"),
    ("Spain", "Business"),
    ("UK", "Individual"),
    ("Canada", "Individual"),
]


def get_seasonal_multiplier(month: int) -> float:
    """
    Get revenue multiplier based on month (seasonal patterns).
    Q4 typically higher, Q1 lower.
    """
    seasonal_patterns = {
        1: 0.7,  # January - Post-holiday slowdown
        2: 0.75,  # February - Still slow
        3: 0.85,  # March - Picking up
        4: 0.9,  # April - Spring growth
        5: 0.95,  # May
        6: 1.0,  # June - Summer projects
        7: 1.05,  # July
        8: 1.0,  # August
        9: 1.1,  # September - Back to business
        10: 1.2,  # October - Q4 push
        11: 1.3,  # November - Holiday prep
        12: 1.25,  # December - Year-end deals
    }
    return seasonal_patterns.get(month, 1.0)


def generate_project_data(
    month: int, year: int, base_revenue: float, trend: str = "increasing"
) -> dict:
    """
    Generate realistic project data with trends and seasonality.

    Args:
        month: Month number (1-12)
        year: Year
        base_revenue: Base revenue amount
        trend: "increasing", "decreasing", or "stable"
    """
    # Apply trend
    trend_multiplier = 1.0
    if trend == "increasing":
        # 5-15% growth per month
        months_from_start = (year - 2025) * 12 + month - 1
        trend_multiplier = 1.0 + (months_from_start * random.uniform(0.05, 0.15))
    elif trend == "decreasing":
        months_from_start = (year - 2025) * 12 + month - 1
        trend_multiplier = 1.0 - (months_from_start * random.uniform(0.03, 0.08))
        trend_multiplier = max(0.5, trend_multiplier)  # Don't go below 50%
    else:  # stable
        trend_multiplier = random.uniform(0.9, 1.1)

    # Apply seasonality
    seasonal_mult = get_seasonal_multiplier(month)

    # Calculate revenue
    revenue = base_revenue * trend_multiplier * seasonal_mult
    revenue = round(revenue, 2)

    # Generate costs (20-40% of revenue)
    num_costs = random.randint(2, 5)
    total_cost_ratio = random.uniform(0.2, 0.4)
    costs = []
    for i in range(num_costs):
        if i == num_costs - 1:
            # Last cost - use remaining budget
            remaining = total_cost_ratio - sum(costs) / revenue
            costs.append(round(revenue * remaining, 2))
        else:
            cost = revenue * random.uniform(0.05, 0.15)
            costs.append(round(cost, 2))

    # Number of people (2-6)
    num_people = random.randint(2, 6)

    # Generate team members with work shares that sum to 1.0
    people = []
    remaining_share = 1.0
    selected_members = random.sample(TEAM_MEMBERS, num_people)

    for i in range(num_people):
        if i == num_people - 1:
            # Last person gets remaining share
            share = remaining_share
        else:
            # Random share between 0.1 and remaining_share - 0.1 * (num_people - i - 1)
            max_share = remaining_share - 0.1 * (num_people - i - 1)
            share = random.uniform(0.1, max_share)
            remaining_share -= share

        people.append({"name": selected_members[i], "work_share": round(share, 2)})

    # Normalize shares to exactly 1.0
    total_share = sum(p["work_share"] for p in people)
    for person in people:
        person["work_share"] = round(person["work_share"] / total_share, 2)

    # Ensure total is exactly 1.0 (adjust last person for rounding)
    current_total = sum(p["work_share"] for p in people[:-1])
    people[-1]["work_share"] = round(1.0 - current_total, 2)

    # Random country and tax type
    country, tax_type = random.choice(COUNTRIES)

    return {
        "revenue": revenue,
        "costs": costs,
        "num_people": num_people,
        "people": people,
        "country": country,
        "tax_type": tax_type,
    }


def get_tax_brackets(conn, country: str, tax_type: str) -> List[Tuple[float, float]]:
    """Get tax brackets from database."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT income_limit, rate
        FROM tax_brackets
        WHERE country = ? AND tax_type = ?
        ORDER BY income_limit
    """,
        (country, tax_type),
    )
    return cursor.fetchall()


def calculate_tax(income: float, brackets: List[Tuple[float, float]]) -> float:
    """Calculate progressive tax."""
    tax = 0
    prev_limit = 0
    for limit, rate in brackets:
        if income > limit:
            tax += (limit - prev_limit) * rate
            prev_limit = limit
        else:
            tax += (income - prev_limit) * rate
            break
    return tax


def calculate_and_insert_project(conn, project_data: dict, target_date: datetime):
    """Calculate taxes and insert project into database."""
    cursor = conn.cursor()

    revenue = project_data["revenue"]
    costs = project_data["costs"]
    total_costs = sum(costs)
    group_income = revenue - total_costs
    num_people = project_data["num_people"]
    individual_income = group_income / num_people

    # Get tax brackets
    brackets = get_tax_brackets(conn, project_data["country"], project_data["tax_type"])

    # Calculate tax
    tax_amount = calculate_tax(individual_income, brackets)

    # Calculate net incomes
    net_income_per_person = individual_income - tax_amount
    net_income_group = group_income - (tax_amount * num_people)

    # Insert tax record
    cursor.execute(
        """
        INSERT INTO tax_records (
            num_people, revenue, total_costs, group_income,
            individual_income, tax_origin, tax_option, tax_amount,
            net_income_per_person, net_income_group, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            num_people,
            revenue,
            total_costs,
            group_income,
            individual_income,
            project_data["country"],
            project_data["tax_type"],
            tax_amount,
            net_income_per_person,
            net_income_group,
            target_date.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    record_id = cursor.lastrowid

    # Calculate individual incomes based on work shares
    for person in project_data["people"]:
        gross_income = group_income * person["work_share"]
        tax_paid = calculate_tax(gross_income, brackets)
        net_income = gross_income - tax_paid

        cursor.execute(
            """
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                record_id,
                person["name"],
                person["work_share"],
                gross_income,
                tax_paid,
                net_income,
            ),
        )

    conn.commit()
    return record_id


def generate_historical_data():
    """Generate comprehensive historical data for the past 12 months."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🚀 Starting comprehensive data generation...")
    print("=" * 60)

    # Define base revenue for different business scenarios
    scenarios = [
        {
            "name": "Growing Startup",
            "base": 8000,
            "trend": "increasing",
            "projects_per_month": (3, 6),
        },
        {
            "name": "Stable Business",
            "base": 15000,
            "trend": "stable",
            "projects_per_month": (2, 4),
        },
        {
            "name": "Seasonal Service",
            "base": 12000,
            "trend": "increasing",
            "projects_per_month": (2, 5),
        },
    ]

    # Generate data for past 24 months (2 full years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    total_projects = 0
    monthly_stats = {}

    for scenario in scenarios:
        print(f"\n📊 Generating data for: {scenario['name']}")
        print(f"   Base Revenue: ${scenario['base']:,}")
        print(f"   Trend: {scenario['trend']}")
        print("-" * 60)

        current_date = start_date

        while current_date <= end_date:
            year = current_date.year
            month = current_date.month

            # Number of projects this month
            min_proj, max_proj = scenario["projects_per_month"]
            num_projects = random.randint(min_proj, max_proj)

            month_key = f"{year}-{month:02d}"
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {"count": 0, "revenue": 0}

            for i in range(num_projects):
                # Spread projects throughout the month
                day = random.randint(1, 28)
                hour = random.randint(9, 17)
                minute = random.randint(0, 59)

                project_date = current_date.replace(
                    day=day, hour=hour, minute=minute, second=0, microsecond=0
                )

                # Generate project
                project_data = generate_project_data(
                    month, year, scenario["base"], scenario["trend"]
                )

                # Insert into DB
                try:
                    record_id = calculate_and_insert_project(
                        conn, project_data, project_date
                    )
                    total_projects += 1
                    monthly_stats[month_key]["count"] += 1
                    monthly_stats[month_key]["revenue"] += project_data["revenue"]

                    if i == 0:  # Print first project of each month
                        print(
                            f"   {month_key}: Created project #{record_id} - ${project_data['revenue']:,.2f}"
                        )
                except Exception as e:
                    print(f"   ❌ Error creating project: {e}")

            # Move to next month
            if month == 12:
                current_date = current_date.replace(year=year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=month + 1, day=1)

    print("\n" + "=" * 60)
    print("✅ DATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\n📈 STATISTICS:")
    print(f"   Total Projects Created: {total_projects}")
    print(f"\n📅 MONTHLY BREAKDOWN:")
    print(f"   {'Month':<12} {'Projects':<12} {'Total Revenue'}")
    print("   " + "-" * 50)

    total_revenue = 0
    for month_key in sorted(monthly_stats.keys()):
        stats = monthly_stats[month_key]
        print(f"   {month_key:<12} {stats['count']:<12} ${stats['revenue']:,.2f}")
        total_revenue += stats["revenue"]

    print("   " + "-" * 50)
    print(f"   {'TOTAL':<12} {total_projects:<12} ${total_revenue:,.2f}")
    print(
        f"   {'AVERAGE/MONTH':<12} {total_projects/12:.1f} projects  ${total_revenue/12:,.2f}"
    )

    # Show team member distribution
    cursor.execute(
        """
        SELECT name, COUNT(*) as project_count, SUM(gross_income) as total_income
        FROM people
        GROUP BY name
        ORDER BY total_income DESC
        LIMIT 10
    """
    )

    print(f"\n👥 TOP 10 CONTRIBUTORS:")
    print(f"   {'Name':<20} {'Projects':<12} {'Total Income'}")
    print("   " + "-" * 50)
    for row in cursor.fetchall():
        print(f"   {row[0]:<20} {row[1]:<12} ${row[2]:,.2f}")

    conn.close()
    print("\n🎉 Database populated with realistic historical data!")


if __name__ == "__main__":
    generate_historical_data()
