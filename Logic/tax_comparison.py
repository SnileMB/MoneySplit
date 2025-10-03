"""
Tax Comparison and Optimization Module
Compares Individual vs Business tax strategies and shows real take-home amounts.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DB import setup

# Dividend tax rates by country
DIVIDEND_TAX_RATES = {
    "US": 0.15,      # Qualified dividends
    "Spain": 0.19    # Dividends tax rate
}


def calculate_all_tax_scenarios(revenue: float, costs: float, num_people: int, country: str):
    """
    Calculate tax for ALL possible scenarios and return comparison data.

    Returns dict with:
    - individual: Individual tax scenario
    - business_salary: Business with salary distribution
    - business_dividend: Business with dividend distribution
    - business_reinvest: Business with reinvestment
    - recommendation: Which option is best
    """

    income = revenue - costs
    individual_income = income / num_people if num_people > 0 else 0

    # ===== INDIVIDUAL TAX (Freelancer/Contractor) =====
    individual_tax = setup.calculate_tax_from_db(individual_income, country, "Individual")
    individual_take_home = individual_income - individual_tax
    individual_total = individual_take_home * num_people

    individual_scenario = {
        "type": "Individual",
        "description": "Self-Employed / Freelancer",
        "gross_income": individual_income,
        "tax_paid": individual_tax,
        "take_home_per_person": individual_take_home,
        "take_home_total": individual_total,
        "effective_rate": (individual_tax / individual_income * 100) if individual_income > 0 else 0,
        "tax_breakdown": [
            {"label": "Personal Income Tax", "amount": individual_tax}
        ]
    }

    # ===== BUSINESS TAX (Corporation) =====
    corporate_tax = setup.calculate_tax_from_db(income, country, "Business")
    after_corp_tax = income - corporate_tax

    # Option 1: Pay yourself as SALARY
    salary_personal_tax = setup.calculate_tax_from_db(after_corp_tax, country, "Individual")
    salary_take_home = after_corp_tax - salary_personal_tax
    salary_per_person = salary_take_home / num_people if num_people > 0 else 0

    business_salary_scenario = {
        "type": "Business - Salary",
        "description": "Corporation paying salary to owners",
        "gross_income": income,
        "corporate_tax": corporate_tax,
        "after_corp_tax": after_corp_tax,
        "personal_tax": salary_personal_tax,
        "total_tax": corporate_tax + salary_personal_tax,
        "take_home_per_person": salary_per_person,
        "take_home_total": salary_take_home,
        "effective_rate": ((corporate_tax + salary_personal_tax) / income * 100) if income > 0 else 0,
        "tax_breakdown": [
            {"label": "Corporate Tax", "amount": corporate_tax},
            {"label": "Personal Income Tax (on salary)", "amount": salary_personal_tax}
        ]
    }

    # Option 2: Pay yourself as DIVIDENDS
    dividend_rate = DIVIDEND_TAX_RATES.get(country, 0.15)
    dividend_tax = after_corp_tax * dividend_rate
    dividend_take_home = after_corp_tax - dividend_tax
    dividend_per_person = dividend_take_home / num_people if num_people > 0 else 0

    business_dividend_scenario = {
        "type": "Business - Dividend",
        "description": "Corporation paying dividends to owners",
        "gross_income": income,
        "corporate_tax": corporate_tax,
        "after_corp_tax": after_corp_tax,
        "dividend_tax": dividend_tax,
        "total_tax": corporate_tax + dividend_tax,
        "take_home_per_person": dividend_per_person,
        "take_home_total": dividend_take_home,
        "effective_rate": ((corporate_tax + dividend_tax) / income * 100) if income > 0 else 0,
        "tax_breakdown": [
            {"label": "Corporate Tax", "amount": corporate_tax},
            {"label": f"Dividend Tax ({dividend_rate*100}%)", "amount": dividend_tax}
        ]
    }

    # Option 3: REINVEST in company
    business_reinvest_scenario = {
        "type": "Business - Reinvest",
        "description": "Keep profits in company for growth",
        "gross_income": income,
        "corporate_tax": corporate_tax,
        "after_corp_tax": after_corp_tax,
        "personal_tax": 0,
        "total_tax": corporate_tax,
        "take_home_per_person": 0,
        "take_home_total": 0,
        "company_retained": after_corp_tax,
        "effective_rate": (corporate_tax / income * 100) if income > 0 else 0,
        "tax_breakdown": [
            {"label": "Corporate Tax", "amount": corporate_tax},
            {"label": "Personal Tax", "amount": 0, "note": "Deferred until distribution"}
        ],
        "note": "No personal income now - money stays in company"
    }

    # ===== DETERMINE BEST OPTION =====
    scenarios = [
        ("individual", individual_scenario),
        ("business_salary", business_salary_scenario),
        ("business_dividend", business_dividend_scenario)
    ]

    # Sort by take_home_total (highest first)
    scenarios.sort(key=lambda x: x[1]["take_home_total"], reverse=True)

    best_option = scenarios[0][0]
    best_scenario = scenarios[0][1]
    worst_scenario = scenarios[-1][1]

    savings = best_scenario["take_home_total"] - worst_scenario["take_home_total"]

    # Generate recommendation
    if best_option == "individual":
        recommendation = {
            "choice": "Individual Tax",
            "reason": f"You'll take home ${best_scenario['take_home_total']:,.2f} (vs ${worst_scenario['take_home_total']:,.2f} with worst option)",
            "savings": savings,
            "warning": None
        }
    elif best_option == "business_dividend":
        recommendation = {
            "choice": "Business Tax with Dividend Distribution",
            "reason": f"Lower tax burden than salary - save ${savings:,.2f}",
            "savings": savings,
            "warning": "⚠️ Remember: Corporate + Dividend tax = double taxation"
        }
    else:
        recommendation = {
            "choice": "Business Tax with Salary",
            "reason": f"Best option for this income level - save ${savings:,.2f}",
            "savings": savings,
            "warning": "⚠️ Remember: Corporate + Personal tax = double taxation"
        }

    return {
        "individual": individual_scenario,
        "business_salary": business_salary_scenario,
        "business_dividend": business_dividend_scenario,
        "business_reinvest": business_reinvest_scenario,
        "recommendation": recommendation,
        "all_scenarios_sorted": scenarios
    }


def get_tax_optimization_summary(revenue: float, costs: float, num_people: int, country: str, selected_type: str):
    """
    Get a summary showing what user selected vs optimal choice.
    Used for displaying warnings/insights after project creation.
    """
    comparison = calculate_all_tax_scenarios(revenue, costs, num_people, country)

    if selected_type == "Individual":
        selected = comparison["individual"]
    elif selected_type == "Business":
        # For now, assume salary distribution (we can make this dynamic later)
        selected = comparison["business_salary"]
    else:
        selected = comparison["individual"]

    best = comparison["all_scenarios_sorted"][0][1]

    is_optimal = selected["take_home_total"] == best["take_home_total"]

    if is_optimal:
        return {
            "is_optimal": True,
            "message": f"✅ Great choice! {selected['type']} is the best option for this project.",
            "selected": selected,
            "savings": 0
        }
    else:
        potential_savings = best["take_home_total"] - selected["take_home_total"]
        return {
            "is_optimal": False,
            "message": f"💡 You could save ${potential_savings:,.2f} by using {best['type']} instead",
            "selected": selected,
            "optimal": best,
            "savings": potential_savings
        }
