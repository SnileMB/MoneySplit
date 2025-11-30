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
from typing import List, Dict, Tuple, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DB import setup


def get_historical_data() -> List[Tuple[str, float, float, float, int, float]]:
    """
    Fetch historical revenue data grouped by month.

    Returns:
        List of tuples: (month, total_revenue, total_costs, total_profit, num_projects, avg_tax_rate)
    """
    conn = setup.get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT strftime('%Y-%m', created_at) as month,
               SUM(revenue) as total_revenue,
               SUM(total_costs) as total_costs,
               SUM(net_income_group) as total_profit,
               COUNT(*) as num_projects,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate
        FROM tax_records
        GROUP BY month
        ORDER BY month
    """
    )
    rows = cursor.fetchall()
    conn.close()

    return rows


def forecast_revenue(months_ahead: int = 3) -> Dict[str, Any]:
    """
    Forecast revenue using an enhanced algorithm.

    Uses polynomial regression when enough data is available (better for non-linear trends).
    Falls back to linear regression for smaller datasets.
    Includes moving average smoothing to reduce noise.
    """
    historical = get_historical_data()

    if len(historical) < 2:
        return {
            "success": False,
            "message": "Not enough historical data (need at least 2 months)",
            "predictions": [],
            "explanation": "Create more projects across different months to enable AI forecasting.",
        }

    # Prepare data
    revenues = np.array([row[1] for row in historical])
    num_projects = np.array([row[4] for row in historical])

    # Apply moving average smoothing for datasets with enough data
    # IMPORTANT: Use 'valid' mode to avoid data leakage (no look-ahead bias)
    if len(revenues) >= 4:
        # 3-point moving average - 'valid' mode loses 2 data points but prevents leakage
        smoothed_revenues = np.convolve(revenues, np.ones(3) / 3, mode="valid")
        y = smoothed_revenues
        # Adjust indices to match smoothed data length (starts from index 1)
        months_indices = np.array(
            [i + 1 for i in range(len(smoothed_revenues))]
        ).reshape(-1, 1)
    else:
        y = revenues
        months_indices = np.array([i for i in range(len(revenues))]).reshape(-1, 1)

    # Choose model based on data size
    if len(historical) >= 6:
        # Polynomial regression for better curve fitting
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(months_indices)
        model = LinearRegression()
        model.fit(X_poly, y)
        r2_score = model.score(X_poly, y)
        model_type = "Polynomial (curved trend)"
    else:
        # Linear regression for smaller datasets
        model = LinearRegression()
        model.fit(months_indices, y)
        r2_score = model.score(months_indices, y)
        model_type = "Linear (straight trend)"

    # Enhanced confidence scoring
    if r2_score > 0.8:
        confidence = "High"
        confidence_desc = "Very reliable - strong pattern detected"
    elif r2_score > 0.6:
        confidence = "Medium-High"
        confidence_desc = "Reliable - clear pattern with minor variation"
    elif r2_score > 0.4:
        confidence = "Medium"
        confidence_desc = "Moderate - pattern exists but with some variability"
    elif r2_score > 0.2:
        confidence = "Low-Medium"
        confidence_desc = "Less reliable - high variability in data"
    else:
        confidence = "Low"
        confidence_desc = "Unreliable - very inconsistent data"

    # Predict future months
    predictions = []
    last_month = historical[-1][0]  # Format: YYYY-MM
    last_date = datetime.strptime(last_month, "%Y-%m")

    for i in range(1, months_ahead + 1):
        future_index = len(historical) + i - 1

        if len(historical) >= 6:
            future_x_poly = poly_features.transform([[future_index]])
            predicted_revenue = model.predict(future_x_poly)[0]
        else:
            predicted_revenue = model.predict([[future_index]])[0]

        # Prevent negative predictions
        predicted_revenue = max(0, predicted_revenue)

        # Calculate next month
        next_month = last_date + timedelta(days=30 * i)
        month_str = next_month.strftime("%B %Y")  # e.g., "November 2025"

        # Calculate confidence interval (95%)
        std_error = np.std(
            y - model.predict(X_poly if len(historical) >= 6 else months_indices)
        )
        lower_bound = max(0, predicted_revenue - 1.96 * std_error)
        upper_bound = predicted_revenue + 1.96 * std_error

        predictions.append(
            {
                "month": month_str,
                "revenue": predicted_revenue,
                "confidence": confidence,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "range": f"${lower_bound:,.0f} - ${upper_bound:,.0f}",
            }
        )

    # Calculate trend with clearer description
    if len(historical) >= 6:
        slope = revenues[-1] - revenues[0]
    else:
        slope = model.coef_[0] if len(model.coef_) == 1 else model.coef_[1]

    if slope > 100:
        trend = "Strongly Increasing"
    elif slope > 0:
        trend = "Growing"
    elif slope < -100:
        trend = "Declining"
    else:
        trend = "Stable"

    trend_strength = abs(slope / len(historical)) if len(historical) > 0 else 0

    # Generate plain English explanation
    avg_revenue = np.mean(revenues)
    last_revenue = revenues[-1]
    growth_rate = (
        ((last_revenue - revenues[0]) / revenues[0] * 100) if revenues[0] > 0 else 0
    )

    explanation = f"""📊 What this means:

Your business has {len(historical)} months of data. The AI analyzed this and found a {trend.lower()} pattern.

• Average monthly revenue: ${avg_revenue:,.0f}
• Last month: ${last_revenue:,.0f}
• Overall growth: {growth_rate:+.1f}%
• Confidence level: {confidence} ({confidence_desc})
• Prediction model: {model_type}

📈 Next month prediction: ${predictions[0]['revenue']:,.0f}
(Range: {predictions[0]['range']})

💡 The AI is {r2_score*100:.0f}% confident in this pattern. {
        "This is very reliable!" if r2_score > 0.7 else
        "Add more data over time for better accuracy." if r2_score < 0.5 else
        "Predictions are reasonably accurate."
    }"""

    return {
        "success": True,
        "predictions": predictions,
        "trend": trend,
        "trend_strength": trend_strength,
        "r2_score": r2_score,
        "confidence": confidence,
        "confidence_description": confidence_desc,
        "historical_avg": avg_revenue,
        "model_slope": slope,
        "growth_rate": growth_rate,
        "model_type": model_type,
        "explanation": explanation.strip(),
        "data_quality": "Excellent"
        if len(historical) >= 10
        else "Good"
        if len(historical) >= 6
        else "Fair",
    }


def tax_optimization_analysis() -> Dict[str, Any]:
    """Analyze tax strategies and provide optimization recommendations."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    # Compare Individual vs Business tax for recent projects
    cursor.execute(
        """
        SELECT tax_option,
               AVG(tax_amount) as avg_tax,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate,
               COUNT(*) as count,
               AVG(revenue) as avg_revenue
        FROM tax_records
        GROUP BY tax_option
    """
    )
    tax_comparison = cursor.fetchall()

    # Get most efficient strategy per country
    cursor.execute(
        """
        SELECT tax_origin, tax_option,
               AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_rate
        FROM tax_records
        GROUP BY tax_origin, tax_option
        ORDER BY tax_origin, avg_rate
    """
    )
    country_analysis = cursor.fetchall()

    # Get overall rate before closing connection
    cursor.execute(
        """
        SELECT AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as overall_rate
        FROM tax_records
    """
    )
    overall_rate = cursor.fetchone()[0] or 0

    conn.close()

    recommendations = []

    # Analyze tax comparison
    if len(tax_comparison) >= 2:
        individual = next((t for t in tax_comparison if t[0] == "Individual"), None)
        business = next((t for t in tax_comparison if t[0] == "Business"), None)

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
    if overall_rate > 25:
        recommendations.append(
            f"Your average tax rate is {overall_rate:.1f}%. Consider reviewing tax brackets and deductions."
        )

    return {
        "tax_comparison": [
            {
                "type": t[0],
                "avg_tax": t[1],
                "avg_rate": t[2],
                "count": t[3],
                "avg_revenue": t[4],
            }
            for t in tax_comparison
        ],
        "recommendations": recommendations
        if recommendations
        else ["Your tax strategy appears optimal based on current data."],
    }


def break_even_analysis(revenue, costs):
    """Calculate break-even point and margin of safety."""
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0

    return {
        "revenue": revenue,
        "costs": costs,
        "profit": profit,
        "profit_margin": margin,
        "break_even_revenue": costs,
        "margin_of_safety": revenue - costs,
        "margin_of_safety_pct": margin,
    }


def trend_analysis():
    """Analyze trends in revenue, costs, and profitability."""
    historical = get_historical_data()

    if len(historical) < 3:
        return {
            "success": False,
            "message": "Need at least 3 months of data for trend analysis",
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
    revenue_growth = (
        ((revenues[-1] - revenues[0]) / revenues[0] * 100) if revenues[0] > 0 else 0
    )
    cost_growth = ((costs[-1] - costs[0]) / costs[0] * 100) if costs[0] > 0 else 0
    profit_growth = (
        ((profits[-1] - profits[0]) / profits[0] * 100) if profits[0] > 0 else 0
    )

    # Seasonality detection (simple moving average)
    if len(revenues) >= 6:
        avg_revenue = np.mean(revenues)
        volatility = np.std(revenues) / avg_revenue if avg_revenue > 0 else 0
        seasonality = (
            "High seasonality detected"
            if volatility > 0.3
            else "Low seasonality"
            if volatility > 0.1
            else "Stable"
        )
    else:
        seasonality = "Insufficient data"

    return {
        "success": True,
        "months_analyzed": len(historical),
        "revenue_trend": revenue_trend,
        "cost_trend": cost_trend,
        "profit_trend": profit_trend,
        "revenue_growth": revenue_growth,
        "cost_growth": cost_growth,
        "profit_growth": profit_growth,
        "seasonality": seasonality,
        "avg_projects_per_month": np.mean(num_projects),
        "current_month_projects": num_projects[-1] if num_projects else 0,
        "insights": generate_insights(
            revenue_trend, cost_trend, profit_trend, revenue_growth, cost_growth
        ),
    }


def generate_insights(rev_trend, cost_trend, profit_trend, rev_growth, cost_growth):
    """Generate actionable insights from trend analysis."""
    insights = []

    if rev_trend == "increasing" and cost_trend == "increasing":
        if cost_growth > rev_growth:
            insights.append(
                "⚠️ Warning: Costs are growing faster than revenue. Review cost management."
            )
        else:
            insights.append("✅ Good: Revenue growth is outpacing cost growth.")

    if rev_trend == "decreasing":
        insights.append(
            "⚠️ Revenue is declining. Consider marketing efforts or new revenue streams."
        )

    if profit_trend == "decreasing":
        insights.append(
            "⚠️ Profitability is declining. Focus on cost reduction or pricing optimization."
        )

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
    if revenue_forecast["success"]:
        if revenue_forecast["trend"] == "increasing":
            recommendations.append(
                f"📈 Revenue is trending upward (+${revenue_forecast['trend_strength']:,.0f}/month). "
                f"Expected next month: ${revenue_forecast['predictions'][0]['revenue']:,.2f}"
            )
        else:
            recommendations.append(
                f"📉 Revenue is trending downward (-${revenue_forecast['trend_strength']:,.0f}/month). "
                "Consider strategies to reverse this trend."
            )

        if revenue_forecast["confidence"] == "Low":
            recommendations.append(
                "⚠️ Low forecast confidence. Predictions may be unreliable due to data volatility."
            )

    # Add tax optimization recommendations
    recommendations.extend(tax_optimization["recommendations"])

    # Add trend insights
    if trends["success"]:
        recommendations.extend(trends["insights"])

    return {
        "revenue_forecast": revenue_forecast,
        "tax_optimization": tax_optimization,
        "trend_analysis": trends,
        "recommendations": recommendations,
    }
