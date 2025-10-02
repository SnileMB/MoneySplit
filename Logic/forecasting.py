"""
Forecasting and prediction module for MoneySplit.
Provides revenue forecasting, tax optimization, and trend analysis.
"""
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DB import setup


def get_historical_data():
    """Fetch historical revenue data grouped by month."""
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

    return rows


def forecast_revenue(months_ahead=3):
    """Forecast revenue for the next N months using linear regression."""
    historical = get_historical_data()

    if len(historical) < 2:
        return {
            'success': False,
            'message': 'Not enough historical data (need at least 2 months)',
            'predictions': []
        }

    # Prepare data
    months = [i for i in range(len(historical))]
    revenues = [row[1] for row in historical]

    X = np.array(months).reshape(-1, 1)
    y = np.array(revenues)

    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Calculate R² score for confidence
    r2_score = model.score(X, y)
    confidence = "High" if r2_score > 0.7 else "Medium" if r2_score > 0.4 else "Low"

    # Predict future months
    predictions = []
    last_month = historical[-1][0]  # Format: YYYY-MM
    last_date = datetime.strptime(last_month, '%Y-%m')

    for i in range(1, months_ahead + 1):
        future_x = len(historical) + i - 1
        predicted_revenue = model.predict([[future_x]])[0]

        # Calculate next month
        next_month = last_date + timedelta(days=30*i)
        month_str = next_month.strftime('%Y-%m')

        predictions.append({
            'month': month_str,
            'revenue': max(0, predicted_revenue),  # Prevent negative predictions
            'confidence': confidence
        })

    # Calculate trend
    trend = "increasing" if model.coef_[0] > 0 else "decreasing"
    trend_strength = abs(model.coef_[0])

    return {
        'success': True,
        'predictions': predictions,
        'trend': trend,
        'trend_strength': trend_strength,
        'r2_score': r2_score,
        'confidence': confidence,
        'historical_avg': np.mean(revenues),
        'model_slope': model.coef_[0]
    }


def tax_optimization_analysis():
    """Analyze tax strategies and provide optimization recommendations."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    # Compare Individual vs Business tax for recent projects
    cursor.execute("""
        SELECT tax_option,
               AVG(tax_amount) as avg_tax,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate,
               COUNT(*) as count,
               AVG(revenue) as avg_revenue
        FROM tax_records
        GROUP BY tax_option
    """)
    tax_comparison = cursor.fetchall()

    # Get most efficient strategy per country
    cursor.execute("""
        SELECT tax_origin, tax_option,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate
        FROM tax_records
        GROUP BY tax_origin, tax_option
        ORDER BY tax_origin, avg_rate
    """)
    country_analysis = cursor.fetchall()

    conn.close()

    recommendations = []

    # Analyze tax comparison
    if len(tax_comparison) >= 2:
        individual = next((t for t in tax_comparison if t[0] == 'Individual'), None)
        business = next((t for t in tax_comparison if t[0] == 'Business'), None)

        if individual and business:
            if individual[2] < business[2]:
                savings = business[1] - individual[1]
                recommendations.append(
                    f"Individual tax is {business[2] - individual[2]:.1f}% lower on average. "
                    f"Consider Individual tax for future projects (potential savings: ${savings:,.2f} per project)"
                )
            else:
                savings = individual[1] - business[1]
                recommendations.append(
                    f"Business tax is {individual[2] - business[2]:.1f}% lower on average. "
                    f"Consider Business tax for future projects (potential savings: ${savings:,.2f} per project)"
                )

    # Country-specific recommendations
    country_dict = {}
    for row in country_analysis:
        country = row[0]
        if country not in country_dict:
            country_dict[country] = []
        country_dict[country].append((row[1], row[2]))

    for country, strategies in country_dict.items():
        if len(strategies) >= 2:
            best_strategy = min(strategies, key=lambda x: x[1])
            recommendations.append(
                f"For {country}: {best_strategy[0]} tax offers best rate ({best_strategy[1]:.1f}%)"
            )

    # General recommendations
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as overall_rate
        FROM tax_records
    """)
    overall_rate = cursor.fetchone()[0] or 0

    if overall_rate > 25:
        recommendations.append(
            f"Your average tax rate is {overall_rate:.1f}%. Consider reviewing tax brackets and deductions."
        )

    return {
        'tax_comparison': [
            {
                'type': t[0],
                'avg_tax': t[1],
                'avg_rate': t[2],
                'count': t[3],
                'avg_revenue': t[4]
            } for t in tax_comparison
        ],
        'recommendations': recommendations if recommendations else ['Your tax strategy appears optimal based on current data.']
    }


def break_even_analysis(revenue, costs):
    """Calculate break-even point and margin of safety."""
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0

    return {
        'revenue': revenue,
        'costs': costs,
        'profit': profit,
        'profit_margin': margin,
        'break_even_revenue': costs,
        'margin_of_safety': revenue - costs,
        'margin_of_safety_pct': margin
    }


def trend_analysis():
    """Analyze trends in revenue, costs, and profitability."""
    historical = get_historical_data()

    if len(historical) < 3:
        return {
            'success': False,
            'message': 'Need at least 3 months of data for trend analysis'
        }

    months = [row[0] for row in historical]
    revenues = [row[1] for row in historical]
    costs = [row[2] for row in historical]
    profits = [row[3] for row in historical]
    num_projects = [row[4] for row in historical]

    # Calculate trends
    revenue_trend = "increasing" if revenues[-1] > revenues[0] else "decreasing"
    cost_trend = "increasing" if costs[-1] > costs[0] else "decreasing"
    profit_trend = "increasing" if profits[-1] > profits[0] else "decreasing"

    # Calculate growth rates
    revenue_growth = ((revenues[-1] - revenues[0]) / revenues[0] * 100) if revenues[0] > 0 else 0
    cost_growth = ((costs[-1] - costs[0]) / costs[0] * 100) if costs[0] > 0 else 0
    profit_growth = ((profits[-1] - profits[0]) / profits[0] * 100) if profits[0] > 0 else 0

    # Seasonality detection (simple moving average)
    if len(revenues) >= 6:
        avg_revenue = np.mean(revenues)
        volatility = np.std(revenues) / avg_revenue if avg_revenue > 0 else 0
        seasonality = "High seasonality detected" if volatility > 0.3 else "Low seasonality" if volatility > 0.1 else "Stable"
    else:
        seasonality = "Insufficient data"

    return {
        'success': True,
        'months_analyzed': len(historical),
        'revenue_trend': revenue_trend,
        'cost_trend': cost_trend,
        'profit_trend': profit_trend,
        'revenue_growth': revenue_growth,
        'cost_growth': cost_growth,
        'profit_growth': profit_growth,
        'seasonality': seasonality,
        'avg_projects_per_month': np.mean(num_projects),
        'current_month_projects': num_projects[-1] if num_projects else 0,
        'insights': generate_insights(revenue_trend, cost_trend, profit_trend, revenue_growth, cost_growth)
    }


def generate_insights(rev_trend, cost_trend, profit_trend, rev_growth, cost_growth):
    """Generate actionable insights from trend analysis."""
    insights = []

    if rev_trend == "increasing" and cost_trend == "increasing":
        if cost_growth > rev_growth:
            insights.append("⚠️ Warning: Costs are growing faster than revenue. Review cost management.")
        else:
            insights.append("✅ Good: Revenue growth is outpacing cost growth.")

    if rev_trend == "decreasing":
        insights.append("⚠️ Revenue is declining. Consider marketing efforts or new revenue streams.")

    if profit_trend == "decreasing":
        insights.append("⚠️ Profitability is declining. Focus on cost reduction or pricing optimization.")

    if profit_trend == "increasing":
        insights.append("✅ Profitability is improving. Maintain current strategy.")

    if abs(rev_growth) < 5:
        insights.append("📊 Revenue is relatively stable. Consider growth strategies.")

    return insights if insights else ["📊 Business metrics are stable."]


def comprehensive_forecast():
    """Generate comprehensive forecast with all insights."""
    revenue_forecast = forecast_revenue(3)
    tax_optimization = tax_optimization_analysis()
    trends = trend_analysis()

    recommendations = []

    # Add revenue forecast recommendations
    if revenue_forecast['success']:
        if revenue_forecast['trend'] == 'increasing':
            recommendations.append(
                f"📈 Revenue is trending upward (+${revenue_forecast['trend_strength']:,.0f}/month). "
                f"Expected next month: ${revenue_forecast['predictions'][0]['revenue']:,.2f}"
            )
        else:
            recommendations.append(
                f"📉 Revenue is trending downward (-${revenue_forecast['trend_strength']:,.0f}/month). "
                "Consider strategies to reverse this trend."
            )

        if revenue_forecast['confidence'] == 'Low':
            recommendations.append(
                "⚠️ Low forecast confidence. Predictions may be unreliable due to data volatility."
            )

    # Add tax optimization recommendations
    recommendations.extend(tax_optimization['recommendations'])

    # Add trend insights
    if trends['success']:
        recommendations.extend(trends['insights'])

    return {
        'revenue_forecast': revenue_forecast,
        'tax_optimization': tax_optimization,
        'trend_analysis': trends,
        'recommendations': recommendations
    }
