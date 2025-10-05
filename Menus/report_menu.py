from MoneySplit.DB import setup
from MoneySplit.Logic import pdf_generator, forecasting
import csv
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import webbrowser
import os

def summary_report():
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tax_origin, tax_option,
               COUNT(*), SUM(revenue), SUM(total_costs), SUM(tax_amount),
               SUM(net_income_group)
        FROM tax_records
        GROUP BY tax_origin, tax_option
    """)
    rows = cursor.fetchall()
    conn.close()

    print("\n=== Summary Report ===")
    print(f"{'Origin':<8} | {'Option':<10} | {'Records':<7} | {'Revenue':>12} | {'Costs':>12} | {'Tax':>12} | {'Net Group':>12}")
    print("-" * 75)
    for origin, option, cnt, rev, cost, tax, net in rows:
        print(f"{origin:<8} | {option:<10} | {cnt:<7} | {rev:>12,.2f} | {cost:>12,.2f} | {tax:>12,.2f} | {net:>12,.2f}")


def person_report():
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, SUM(gross_income), SUM(tax_paid), SUM(net_income)
        FROM people
        GROUP BY name
        ORDER BY SUM(gross_income) DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    print("\n=== Per-Person Report ===")
    print(f"{'Name':<12} | {'Gross':>12} | {'Tax Paid':>12} | {'Net':>12}")
    print("-" * 55)
    for name, gross, tax, net in rows:
        print(f"{name:<12} | {gross:>12,.2f} | {tax:>12,.2f} | {net:>12,.2f}")


def record_stats():
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*), AVG(revenue), AVG(tax_amount), MIN(net_income_group), MAX(net_income_group)
        FROM tax_records
    """)
    total, avg_rev, avg_tax, min_net, max_net = cursor.fetchone()
    conn.close()

    print("\n=== Record Statistics ===")
    print(f"Total Records: {total}")
    print(f"Average Revenue: {avg_rev:,.2f}")
    print(f"Average Tax: {avg_tax:,.2f}")
    print(f"Min Net Income (Group): {min_net:,.2f}")
    print(f"Max Net Income (Group): {max_net:,.2f}")


def show_report_menu():
    while True:
        print("\n=== Reports 📊 ===")
        print("1. Summary Report")
        print("2. Per-Person Report")
        print("3. Record Statistics")
        print("4. Back")

        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            summary_report()
        elif choice == "2":
            person_report()
        elif choice == "3":
            record_stats()
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice.")

def export_to_csv(filename, headers, rows):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"📄 Exported report → {filename}")

def revenue_summary_report():
    rows = setup.get_revenue_summary()
    if not rows:
        print("❌ No data found.")
        return

    # Extract data
    years = [row[0] for row in rows]
    revenues = [row[1] for row in rows]
    costs = [row[2] for row in rows]
    net_incomes = [row[3] for row in rows]

    # Create interactive chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Revenue & Costs by Year", "Net Income by Year"),
        vertical_spacing=0.15
    )

    # Revenue and Costs
    fig.add_trace(
        go.Bar(name="Revenue", x=years, y=revenues, marker_color='rgb(55, 83, 109)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name="Costs", x=years, y=costs, marker_color='rgb(219, 64, 82)'),
        row=1, col=1
    )

    # Net Income
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

    # Save and open
    filepath = "reports/revenue_summary.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")

    # Also print text summary
    print("\n=== Revenue Summary (Text) ===")
    print(f"{'Year':<6} | {'Total Revenue':>15} | {'Total Costs':>15} | {'Net Income':>15}")
    print("-" * 60)
    for year, rev, cost, net in rows:
        print(f"{year:<6} | {rev:>15,.2f} | {cost:>15,.2f} | {net:>15,.2f}")

    choice = input("\nExport to CSV? (y/n): ").strip().lower()
    if choice == "y":
        filename = input("Enter filename (default: report_revenue_summary.csv): ").strip()
        if not filename:
            filename = "report_revenue_summary.csv"
        elif not filename.endswith(".csv"):
            filename += ".csv"
        headers = ["Year", "Total Revenue", "Total Costs", "Net Income"]
        export_to_csv(filename, headers, rows)

def top_people_report():
    rows = setup.get_top_people()
    if not rows:
        print("❌ No data found.")
        return

    # Extract data
    names = [row[0] for row in rows]
    gross_incomes = [row[1] for row in rows]
    taxes_paid = [row[2] for row in rows]
    net_incomes = [row[3] for row in rows]

    # Create horizontal bar chart
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Net Income", "Gross Income vs Tax Paid"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )

    # Net income chart
    fig.add_trace(
        go.Bar(name="Net Income", y=names, x=net_incomes, orientation='h',
               marker_color='rgb(50, 171, 96)', text=net_incomes,
               texttemplate='$%{text:,.0f}', textposition='outside'),
        row=1, col=1
    )

    # Gross vs Tax chart
    fig.add_trace(
        go.Bar(name="Gross Income", y=names, x=gross_incomes, orientation='h',
               marker_color='rgb(55, 83, 109)'),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(name="Tax Paid", y=names, x=taxes_paid, orientation='h',
               marker_color='rgb(219, 64, 82)'),
        row=1, col=2
    )

    fig.update_layout(
        title_text="Top People by Net Income",
        showlegend=True,
        height=max(400, len(names) * 40),
        barmode='group'
    )
    fig.update_xaxes(title_text="Net Income ($)", row=1, col=1)
    fig.update_xaxes(title_text="Amount ($)", row=1, col=2)

    # Save and open
    filepath = "reports/top_people.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")

    # Also print text summary
    headers = ["Name", "Total Gross", "Total Tax Paid", "Total Net Income"]
    print("\n=== Top People by Net Income (Text) ===")
    print(f"{headers[0]:<15} | {headers[1]:>15} | {headers[2]:>15} | {headers[3]:>15}")
    print("-" * 70)
    for name, gross, tax, net in rows:
        print(f"{name:<15} | {gross:>15,.2f} | {tax:>15,.2f} | {net:>15,.2f}")

    choice = input("\nExport to CSV? (y/n): ").strip().lower()
    if choice == "y":
        filename = input("Enter filename (default: report_top_people.csv): ").strip()
        if not filename:
            filename = "report_top_people.csv"
        elif not filename.endswith(".csv"):
            filename += ".csv"
        export_to_csv(filename, headers, rows)

def show_report_menu():
    while True:
        print("\n=== Reports Menu 📊 ===")
        print("1. Revenue summary by year")
        print("2. Top people by net income")
        print("3. Back")

        choice = input("Choose an option (1-3): ").strip()
        if choice == "1":
            revenue_summary_report()
        elif choice == "2":
            top_people_report()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")


def show_summary(record_id: int):
    """Show summary for a given record."""
    rec = setup.get_record_by_id(record_id)
    if not rec:
        print(f"❌ Record {record_id} not found.")
        return

    rid, origin, option, revenue, costs, tax, net_group, net_person, created, num_people, group_income, individual_income = rec
    print(f"\n=== Summary for Record {rid} ({origin} {option}) ===")
    print(f"Revenue:        {float(revenue):,.2f}")
    print(f"Total Costs:    {float(costs):,.2f}")
    print(f"Tax Paid:       {float(tax):,.2f}")
    print(f"Net Group:      {float(net_group):,.2f}")
    print(f"Net Per Person: {float(net_person):,.2f}")


def show_top_contributors(record_id: int, top_n: int = 5):
    """Show top contributors (by net income) for a record."""
    people = setup.fetch_people_by_record(record_id)
    if not people:
        print(f"❌ No people found for record {record_id}.")
        return

    ranked = sorted(people, key=lambda x: x[5], reverse=True)  # net_income = idx 5
    print(f"\n=== Top {min(top_n, len(ranked))} Contributors (by Net Income) ===")
    for i, (pid, name, ws, gross, tax_paid, net) in enumerate(ranked[:top_n], start=1):
        print(f"{i}. {name:<12} → Net {net:,.2f} (Gross {gross:,.2f}, Tax {tax_paid:,.2f})")


def single_record_menu():
    """Menu for single record reports."""
    while True:
        print("\n=== Single Record Reports 📄 ===")
        print("1. View summary for a record")
        print("2. View top contributors for a record")
        print("3. Export record to PDF 📄")
        print("4. Back")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            try:
                record_id = int(input("Enter record ID: "))
                show_summary(record_id)
            except ValueError:
                print("❌ Invalid input.")
        elif choice == "2":
            try:
                record_id = int(input("Enter record ID: "))
                show_top_contributors(record_id)
            except ValueError:
                print("❌ Invalid input.")
        elif choice == "3":
            export_record_to_pdf()
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")


def aggregate_reports_menu():
    """Menu for aggregate reports across all data."""
    while True:
        print("\n=== Aggregate Reports 📊 ===")
        print("1. Revenue summary by year")
        print("2. Top people (across all records)")
        print("3. Tax strategy comparison")
        print("4. Overall statistics")
        print("5. Monthly trends 📈")
        print("6. Work distribution analysis 🥧")
        print("7. Person performance timeline ⏱️")
        print("8. Tax efficiency report 💡")
        print("9. Project profitability analysis 💰")
        print("10. Revenue forecasting & predictions 🔮")
        print("11. Export summary to PDF 📄")
        print("12. Back")

        choice = input("Choose an option (1-12): ").strip()

        if choice == "1":
            revenue_summary_report()
        elif choice == "2":
            top_people_report()
        elif choice == "3":
            tax_type_comparison_report()
        elif choice == "4":
            overall_statistics()
        elif choice == "5":
            monthly_trends_report()
        elif choice == "6":
            work_distribution_report()
        elif choice == "7":
            person_performance_timeline()
        elif choice == "8":
            tax_efficiency_report()
        elif choice == "9":
            project_profitability_report()
        elif choice == "10":
            show_forecast_report()
        elif choice == "11":
            export_summary_to_pdf()
        elif choice == "12":
            break
        else:
            print("❌ Invalid choice. Please enter 1-12.")


def tax_type_comparison_report():
    """Compare Individual vs Business tax strategies."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tax_origin, tax_option,
               COUNT(*) as records,
               AVG(revenue) as avg_revenue,
               AVG(tax_amount) as avg_tax,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate,
               SUM(net_income_group) as total_net
        FROM tax_records
        GROUP BY tax_origin, tax_option
        ORDER BY tax_origin, tax_option
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ No data found.")
        return

    # Extract data
    labels = [f"{row[0]} - {row[1]}" for row in rows]
    avg_revenues = [row[3] for row in rows]
    avg_taxes = [row[4] for row in rows]
    avg_rates = [row[5] for row in rows]
    total_nets = [row[6] for row in rows]

    # Create comparison charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Average Tax Rate (%)", "Total Net Income",
                       "Average Revenue vs Tax", "Record Distribution"),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "pie"}]]
    )

    # Avg tax rate
    fig.add_trace(
        go.Bar(x=labels, y=avg_rates, name="Avg Tax Rate",
               marker_color='rgb(219, 64, 82)', text=avg_rates,
               texttemplate='%{text:.2f}%', textposition='outside'),
        row=1, col=1
    )

    # Total net income
    fig.add_trace(
        go.Bar(x=labels, y=total_nets, name="Total Net",
               marker_color='rgb(50, 171, 96)', text=total_nets,
               texttemplate='$%{text:,.0f}', textposition='outside'),
        row=1, col=2
    )

    # Avg revenue vs tax
    fig.add_trace(
        go.Bar(x=labels, y=avg_revenues, name="Avg Revenue",
               marker_color='rgb(55, 83, 109)'),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=labels, y=avg_taxes, name="Avg Tax",
               marker_color='rgb(219, 64, 82)'),
        row=2, col=1
    )

    # Record distribution pie
    record_counts = [row[2] for row in rows]
    fig.add_trace(
        go.Pie(labels=labels, values=record_counts, textinfo='label+percent+value'),
        row=2, col=2
    )

    fig.update_layout(
        title_text="Tax Strategy Comparison",
        showlegend=True,
        height=800
    )
    fig.update_yaxes(title_text="Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Net Income ($)", row=1, col=2)
    fig.update_yaxes(title_text="Amount ($)", row=2, col=1)

    # Save and open
    filepath = "reports/tax_strategy_comparison.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")

    # Also print text summary
    print("\n=== Tax Strategy Comparison (Text) ===")
    print(f"{'Origin':<8} | {'Strategy':<10} | {'Records':<7} | {'Avg Revenue':>12} | {'Avg Tax':>12} | {'Avg Rate':>9} | {'Total Net':>12}")
    print("-" * 90)
    for origin, option, cnt, avg_rev, avg_tax, avg_rate, total_net in rows:
        print(f"{origin:<8} | {option:<10} | {cnt:<7} | {avg_rev:>12,.2f} | {avg_tax:>12,.2f} | {avg_rate:>8.2f}% | {total_net:>12,.2f}")


def overall_statistics():
    """Show overall database statistics."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    # Records stats
    cursor.execute("""
        SELECT COUNT(*),
               SUM(revenue),
               SUM(total_costs),
               SUM(tax_amount),
               SUM(net_income_group),
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0))
        FROM tax_records
    """)
    total_records, total_rev, total_costs, total_tax, total_net, avg_rate = cursor.fetchone()

    # People stats
    cursor.execute("SELECT COUNT(*), COUNT(DISTINCT name) FROM people")
    total_people_entries, unique_people = cursor.fetchone()

    conn.close()

    if total_records == 0:
        print("❌ No data found.")
        return

    # Create dashboard with multiple visualizations
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Financial Breakdown", "Revenue Flow (Sankey)",
                       "Database Overview", "Tax Efficiency"),
        specs=[[{"type": "pie"}, {"type": "sankey"}],
               [{"type": "indicator"}, {"type": "indicator"}]]
    )

    # Pie chart - Financial breakdown
    fig.add_trace(
        go.Pie(labels=["Net Income", "Tax Paid", "Costs"],
               values=[total_net, total_tax, total_costs],
               marker_colors=['rgb(50, 171, 96)', 'rgb(219, 64, 82)', 'rgb(255, 165, 0)'],
               textinfo='label+percent+value',
               texttemplate='%{label}<br>$%{value:,.0f}<br>%{percent}'),
        row=1, col=1
    )

    # Sankey diagram - Revenue flow
    fig.add_trace(
        go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=["Revenue", "Costs", "Income", "Tax", "Net Income"],
                color=['rgb(55, 83, 109)', 'rgb(255, 165, 0)', 'rgb(100, 150, 200)',
                       'rgb(219, 64, 82)', 'rgb(50, 171, 96)']
            ),
            link=dict(
                source=[0, 0, 2, 2],
                target=[1, 2, 3, 4],
                value=[total_costs, total_rev - total_costs, total_tax, total_net]
            )
        ),
        row=1, col=2
    )

    # Indicator - Database stats
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=total_records,
            title={"text": f"Total Records<br><span style='font-size:0.8em'>People: {unique_people} unique / {total_people_entries} total</span>"},
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=2, col=1
    )

    # Indicator - Tax efficiency
    net_percentage = (total_net / total_rev * 100) if total_rev > 0 else 0
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=net_percentage,
            title={"text": "Net Income Efficiency<br><span style='font-size:0.8em'>(Net / Revenue %)</span>"},
            delta={'reference': 70, 'increasing': {'color': 'green'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': 'rgb(50, 171, 96)'},
                'steps': [
                    {'range': [0, 50], 'color': 'rgb(255, 200, 200)'},
                    {'range': [50, 70], 'color': 'rgb(255, 255, 200)'},
                    {'range': [70, 100], 'color': 'rgb(200, 255, 200)'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=2, col=2
    )

    fig.update_layout(
        title_text=f"Overall Statistics Dashboard<br><sub>Total Revenue: ${total_rev:,.0f} | Avg Tax Rate: {avg_rate:.2f}%</sub>",
        showlegend=False,
        height=900
    )

    # Save and open
    filepath = "reports/overall_statistics.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")

    # Also print text summary
    print("\n=== Overall Statistics (Text) ===")
    print(f"Total Records:        {total_records}")
    print(f"Total People Entries: {total_people_entries}")
    print(f"Unique People:        {unique_people}")
    print(f"\nTotal Revenue:        ${total_rev:,.2f}")
    print(f"Total Costs:          ${total_costs:,.2f}")
    print(f"Total Tax Paid:       ${total_tax:,.2f}")
    print(f"Total Net Income:     ${total_net:,.2f}")
    print(f"Average Tax Rate:     {avg_rate:.2f}%")
    print(f"Net Efficiency:       {net_percentage:.2f}%")


def monthly_trends_report():
    """Show monthly revenue, costs, and profit trends."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', created_at) as month,
               COUNT(*) as num_projects,
               SUM(revenue) as total_revenue,
               SUM(total_costs) as total_costs,
               SUM(net_income_group) as total_profit,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate
        FROM tax_records
        GROUP BY month
        ORDER BY month DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ No data found.")
        return

    # Extract data
    months = [row[0] for row in rows]
    num_projects = [row[1] for row in rows]
    revenues = [row[2] for row in rows]
    costs = [row[3] for row in rows]
    profits = [row[4] for row in rows]
    tax_rates = [row[5] or 0 for row in rows]

    # Reverse for chronological order
    months.reverse()
    num_projects.reverse()
    revenues.reverse()
    costs.reverse()
    profits.reverse()
    tax_rates.reverse()

    # Create visualization
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Monthly Revenue & Costs", "Monthly Profit", "Number of Projects & Avg Tax Rate"),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": True}]],
        vertical_spacing=0.1
    )

    # Revenue & Costs
    fig.add_trace(
        go.Scatter(name="Revenue", x=months, y=revenues, mode='lines+markers',
                   line=dict(color='rgb(55, 83, 109)', width=3), fill='tozeroy'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name="Costs", x=months, y=costs, mode='lines+markers',
                   line=dict(color='rgb(219, 64, 82)', width=3)),
        row=1, col=1
    )

    # Profit
    fig.add_trace(
        go.Scatter(name="Profit", x=months, y=profits, mode='lines+markers',
                   line=dict(color='rgb(50, 171, 96)', width=4),
                   fill='tozeroy'),
        row=2, col=1
    )

    # Projects (bar)
    fig.add_trace(
        go.Bar(name="# Projects", x=months, y=num_projects,
               marker_color='rgb(158, 202, 225)'),
        row=3, col=1, secondary_y=False
    )

    # Tax Rate (line on secondary axis)
    fig.add_trace(
        go.Scatter(name="Avg Tax Rate", x=months, y=tax_rates, mode='lines+markers',
                   line=dict(color='rgb(255, 127, 14)', width=3)),
        row=3, col=1, secondary_y=True
    )

    fig.update_layout(
        title_text="Monthly Trends Analysis",
        showlegend=True,
        height=1000
    )
    fig.update_xaxes(title_text="Month", row=3, col=1)
    fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
    fig.update_yaxes(title_text="Profit ($)", row=2, col=1)
    fig.update_yaxes(title_text="# Projects", row=3, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Tax Rate (%)", row=3, col=1, secondary_y=True)

    # Save and open
    filepath = "reports/monthly_trends.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")


def work_distribution_report():
    """Show work distribution pie chart and leaderboard."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name,
               SUM(work_share) as total_work_share,
               COUNT(*) as num_projects,
               SUM(gross_income) as total_gross,
               SUM(net_income) as total_net
        FROM people
        GROUP BY name
        ORDER BY total_net DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ No data found.")
        return

    names = [row[0] for row in rows]
    work_shares = [row[1] for row in rows]
    num_projects = [row[2] for row in rows]
    gross_incomes = [row[3] for row in rows]
    net_incomes = [row[4] for row in rows]

    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Work Distribution", "Leaderboard (Net Income)",
                       "Projects Participated", "Gross vs Net Income"),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )

    # Work distribution pie
    fig.add_trace(
        go.Pie(labels=names, values=work_shares, textinfo='label+percent'),
        row=1, col=1
    )

    # Leaderboard
    fig.add_trace(
        go.Bar(name="Net Income", x=names, y=net_incomes,
               marker_color='rgb(50, 171, 96)', text=net_incomes,
               texttemplate='$%{text:,.0f}', textposition='outside'),
        row=1, col=2
    )

    # Projects participated
    fig.add_trace(
        go.Bar(name="# Projects", x=names, y=num_projects,
               marker_color='rgb(158, 202, 225)'),
        row=2, col=1
    )

    # Gross vs Net
    fig.add_trace(
        go.Bar(name="Gross", x=names, y=gross_incomes,
               marker_color='rgb(55, 83, 109)'),
        row=2, col=2
    )
    fig.add_trace(
        go.Bar(name="Net", x=names, y=net_incomes,
               marker_color='rgb(50, 171, 96)'),
        row=2, col=2
    )

    fig.update_layout(
        title_text="Team Performance & Work Distribution",
        showlegend=True,
        height=900
    )

    filepath = "reports/work_distribution.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")


def person_performance_timeline():
    """Show individual performance over time."""
    name = input("Enter person's name: ").strip()

    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m-%d', t.created_at) as date,
               p.gross_income,
               p.tax_paid,
               p.net_income,
               p.work_share,
               t.id as record_id
        FROM people p
        JOIN tax_records t ON p.record_id = t.id
        WHERE LOWER(p.name) = LOWER(?)
        ORDER BY t.created_at
    """, (name,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"❌ No data found for {name}.")
        return

    dates = [row[0] for row in rows]
    gross = [row[1] for row in rows]
    tax = [row[2] for row in rows]
    net = [row[3] for row in rows]
    work_shares = [row[4] * 100 for row in rows]  # Convert to percentage

    # Create visualization
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f"{name}'s Income Over Time", f"{name}'s Work Share %"),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
        vertical_spacing=0.15
    )

    # Income timeline
    fig.add_trace(
        go.Scatter(name="Gross Income", x=dates, y=gross, mode='lines+markers',
                   line=dict(color='rgb(55, 83, 109)', width=3)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name="Tax Paid", x=dates, y=tax, mode='lines+markers',
                   line=dict(color='rgb(219, 64, 82)', width=3)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name="Net Income", x=dates, y=net, mode='lines+markers',
                   line=dict(color='rgb(50, 171, 96)', width=4), fill='tozeroy'),
        row=1, col=1
    )

    # Work share timeline
    fig.add_trace(
        go.Scatter(name="Work Share %", x=dates, y=work_shares, mode='lines+markers',
                   line=dict(color='rgb(128, 0, 128)', width=3),
                   fill='tozeroy'),
        row=2, col=1
    )

    # Calculate totals
    total_gross = sum(gross)
    total_tax = sum(tax)
    total_net = sum(net)

    fig.update_layout(
        title_text=f"{name}'s Performance Timeline<br><sub>Total: Gross ${total_gross:,.0f} | Tax ${total_tax:,.0f} | Net ${total_net:,.0f}</sub>",
        showlegend=True,
        height=800
    )
    fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
    fig.update_yaxes(title_text="Work Share (%)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    filepath = f"reports/performance_{name.replace(' ', '_')}.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")


def tax_efficiency_report():
    """Show tax efficiency - how much people keep vs pay."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name,
               SUM(gross_income) as total_gross,
               SUM(tax_paid) as total_tax,
               SUM(net_income) as total_net,
               (SUM(net_income) * 100.0 / NULLIF(SUM(gross_income), 0)) as efficiency_pct
        FROM people
        GROUP BY name
        HAVING total_gross > 0
        ORDER BY efficiency_pct DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ No data found.")
        return

    names = [row[0] for row in rows]
    gross = [row[1] for row in rows]
    tax = [row[2] for row in rows]
    net = [row[3] for row in rows]
    efficiency = [row[4] for row in rows]

    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Tax Efficiency % (Higher = Better)", "Tax Burden by Person",
                       "Income Breakdown", "Efficiency Gauge"),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "indicator"}]]
    )

    # Efficiency ranking
    fig.add_trace(
        go.Bar(name="Efficiency %", x=names, y=efficiency,
               marker_color='rgb(50, 171, 96)', text=efficiency,
               texttemplate='%{text:.1f}%', textposition='outside'),
        row=1, col=1
    )

    # Tax burden
    fig.add_trace(
        go.Bar(name="Tax Paid", x=names, y=tax,
               marker_color='rgb(219, 64, 82)', text=tax,
               texttemplate='$%{text:,.0f}', textposition='outside'),
        row=1, col=2
    )

    # Income breakdown (stacked)
    fig.add_trace(
        go.Bar(name="Net Income", x=names, y=net,
               marker_color='rgb(50, 171, 96)'),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(name="Tax", x=names, y=tax,
               marker_color='rgb(219, 64, 82)'),
        row=2, col=1
    )

    # Overall efficiency gauge
    overall_efficiency = (sum(net) / sum(gross) * 100) if sum(gross) > 0 else 0
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=overall_efficiency,
            title={"text": "Overall Team Efficiency %"},
            delta={'reference': 75, 'increasing': {'color': 'green'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': 'rgb(50, 171, 96)'},
                'steps': [
                    {'range': [0, 50], 'color': 'rgb(255, 200, 200)'},
                    {'range': [50, 75], 'color': 'rgb(255, 255, 200)'},
                    {'range': [75, 100], 'color': 'rgb(200, 255, 200)'}
                ]
            }
        ),
        row=2, col=2
    )

    fig.update_layout(
        title_text="Tax Efficiency Analysis",
        showlegend=True,
        height=900,
        barmode='stack'
    )
    fig.update_yaxes(title_text="Efficiency (%)", row=1, col=1)
    fig.update_yaxes(title_text="Tax Paid ($)", row=1, col=2)

    filepath = "reports/tax_efficiency.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")

    # Also print text summary
    print(f"\n📊 Overall Tax Efficiency: {overall_efficiency:.2f}%")
    print(f"Total Gross Income: ${sum(gross):,.2f}")
    print(f"Total Tax Paid: ${sum(tax):,.2f}")
    print(f"Total Net Income: ${sum(net):,.2f}")


def project_profitability_report():
    """Analyze project profitability - profit margins, ROI, etc."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,
               revenue,
               total_costs,
               tax_amount,
               net_income_group,
               num_people,
               created_at,
               (net_income_group * 100.0 / NULLIF(revenue, 0)) as profit_margin,
               (net_income_group * 100.0 / NULLIF(total_costs, 0)) as roi
        FROM tax_records
        WHERE revenue > 0
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ No data found.")
        return

    record_ids = [f"P{row[0]}" for row in rows]
    revenues = [row[1] for row in rows]
    costs = [row[2] for row in rows]
    taxes = [row[3] for row in rows]
    profits = [row[4] for row in rows]
    num_people = [row[5] for row in rows]
    profit_margins = [row[7] or 0 for row in rows]
    rois = [row[8] or 0 for row in rows]

    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Profit Margin % by Project", "ROI % by Project",
                       "Revenue Breakdown", "Profit vs Team Size"),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )

    # Profit margins
    colors = ['rgb(50, 171, 96)' if pm > 30 else 'rgb(255, 165, 0)' if pm > 10 else 'rgb(219, 64, 82)' for pm in profit_margins]
    fig.add_trace(
        go.Bar(name="Profit Margin %", x=record_ids, y=profit_margins,
               marker_color=colors, text=profit_margins,
               texttemplate='%{text:.1f}%', textposition='outside'),
        row=1, col=1
    )

    # ROI
    fig.add_trace(
        go.Bar(name="ROI %", x=record_ids, y=rois,
               marker_color='rgb(128, 0, 128)', text=rois,
               texttemplate='%{text:.0f}%', textposition='outside'),
        row=1, col=2
    )

    # Revenue breakdown (stacked)
    fig.add_trace(
        go.Bar(name="Profit", x=record_ids, y=profits,
               marker_color='rgb(50, 171, 96)'),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(name="Tax", x=record_ids, y=taxes,
               marker_color='rgb(219, 64, 82)'),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(name="Costs", x=record_ids, y=costs,
               marker_color='rgb(255, 165, 0)'),
        row=2, col=1
    )

    # Scatter: profit vs team size
    fig.add_trace(
        go.Scatter(name="Profit vs Team Size", x=num_people, y=profits,
                   mode='markers', marker=dict(size=12, color=profits,
                   colorscale='Viridis', showscale=True)),
        row=2, col=2
    )

    fig.update_layout(
        title_text="Project Profitability Analysis",
        showlegend=True,
        height=900,
        barmode='stack'
    )
    fig.update_yaxes(title_text="Margin (%)", row=1, col=1)
    fig.update_yaxes(title_text="ROI (%)", row=1, col=2)
    fig.update_xaxes(title_text="Team Size", row=2, col=2)
    fig.update_yaxes(title_text="Profit ($)", row=2, col=2)

    filepath = "reports/project_profitability.html"
    os.makedirs("reports", exist_ok=True)
    fig.write_html(filepath)
    webbrowser.open('file://' + os.path.abspath(filepath))
    print(f"📊 Visualization opened in browser: {filepath}")

    # Text summary
    avg_margin = sum(profit_margins) / len(profit_margins) if profit_margins else 0
    avg_roi = sum(rois) / len(rois) if rois else 0
    print(f"\n📊 Average Profit Margin: {avg_margin:.2f}%")
    print(f"📊 Average ROI: {avg_roi:.2f}%")


def export_record_to_pdf():
    """Export a single record to PDF."""
    try:
        record_id = int(input("Enter record ID to export: "))
        record = setup.get_record_by_id(record_id)

        if not record:
            print(f"❌ Record {record_id} not found.")
            return

        people = setup.fetch_people_by_record(record_id)

        filepath = pdf_generator.generate_project_pdf(record, people)
        print(f"✅ PDF exported successfully: {filepath}")

        # Auto-open
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(filepath))
    except ValueError:
        print("❌ Invalid record ID.")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")


def export_summary_to_pdf():
    """Export summary report to PDF."""
    try:
        records = setup.fetch_last_records(20)

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
        print(f"✅ Summary PDF exported successfully: {filepath}")

        # Auto-open
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(filepath))
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")


def show_forecast_report():
    """Display revenue forecasting and predictions."""
    print("\n" + "=" * 60)
    print("🔮 Revenue Forecasting & Tax Optimization")
    print("=" * 60)

    forecast = forecasting.comprehensive_forecast()

    # Revenue Forecast
    if forecast['revenue_forecast']['success']:
        rf = forecast['revenue_forecast']
        print("\n📈 Revenue Predictions (Next 3 Months):")
        print(f"{'Month':<12} | {'Predicted Revenue':>18} | {'Confidence':<10}")
        print("-" * 50)
        for pred in rf['predictions']:
            print(f"{pred['month']:<12} | ${pred['revenue']:>17,.2f} | {pred['confidence']:<10}")

        print(f"\n📊 Trend: {rf['trend'].upper()} (${rf['trend_strength']:,.0f}/month)")
        print(f"📊 Forecast Confidence: {rf['confidence']} (R² = {rf['r2_score']:.2f})")
        print(f"📊 Historical Average: ${rf['historical_avg']:,.2f}")
    else:
        print(f"\n⚠️ {forecast['revenue_forecast']['message']}")

    # Tax Optimization
    print("\n💰 Tax Optimization Analysis:")
    tax_opt = forecast['tax_optimization']
    if tax_opt['tax_comparison']:
        print(f"\n{'Tax Type':<12} | {'Avg Tax':>12} | {'Avg Rate':>10} | {'Projects':>8}")
        print("-" * 50)
        for tc in tax_opt['tax_comparison']:
            print(f"{tc['type']:<12} | ${tc['avg_tax']:>11,.2f} | {tc['avg_rate']:>9.2f}% | {tc['count']:>8}")

    # Trend Analysis
    if forecast['trend_analysis']['success']:
        ta = forecast['trend_analysis']
        print(f"\n📊 Trend Analysis ({ta['months_analyzed']} months):")
        print(f"  • Revenue: {ta['revenue_trend']} ({ta['revenue_growth']:+.1f}%)")
        print(f"  • Costs: {ta['cost_trend']} ({ta['cost_growth']:+.1f}%)")
        print(f"  • Profit: {ta['profit_trend']} ({ta['profit_growth']:+.1f}%)")
        print(f"  • Seasonality: {ta['seasonality']}")

    # Recommendations
    print("\n💡 Recommendations:")
    for i, rec in enumerate(forecast['recommendations'], 1):
        print(f"  {i}. {rec}")

    # Option to export
    print("\n" + "=" * 60)
    export = input("Export forecast to PDF? (y/n): ").strip().lower()
    if export == 'y':
        try:
            filepath = pdf_generator.generate_forecast_pdf(forecast['revenue_forecast'])
            print(f"✅ Forecast PDF exported: {filepath}")
            webbrowser.open('file://' + os.path.abspath(filepath))
        except Exception as e:
            print(f"❌ Error exporting PDF: {e}")


def show_report_menu(auto=False, record_id=None):
    """
    Main reporting menu.
    - auto=True, record_id set → show summary + top contributors immediately.
    - auto=False → show interactive two-tier menu.
    """
    if auto:
        if record_id is None:
            print("❌ Auto-report needs a record_id.")
            return
        show_summary(record_id)
        show_top_contributors(record_id)
        return

    # Interactive mode - two-tier menu
    while True:
        print("\n=== Reports Menu 📊 ===")
        print("1. Single Record Reports 📄")
        print("2. Aggregate Reports 📈")
        print("3. Back")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            single_record_menu()
        elif choice == "2":
            aggregate_reports_menu()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")
