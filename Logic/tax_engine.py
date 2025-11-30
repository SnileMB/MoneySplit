"""
Enhanced Tax Calculation Engine
Handles all tax scenarios: Individual, Business with Salary/Dividend/Mixed/Reinvest
"""
import sys
import os
from typing import Dict, List, Tuple, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DB import setup

# Dividend tax rates by country
DIVIDEND_TAX_RATES: Dict[str, float] = {
    "US": 0.15,  # Qualified dividends
    "Spain": 0.19,  # Dividends tax rate
}

# Standard deductions by country (2023 tax year)
STANDARD_DEDUCTIONS: Dict[str, int] = {
    "US": 13850,  # Single filer 2023
    "Spain": 5550,  # Minimum personal allowance
}

# Self-employment tax rates (US only)
SE_TAX_RATES = {
    "social_security": 0.124,  # 12.4%
    "ss_wage_base": 160200,  # 2023 wage base limit
    "medicare": 0.029,  # 2.9%
    "additional_medicare": 0.009,  # 0.9%
    "additional_medicare_threshold": 200000,  # Additional Medicare threshold
}

# Corporate tax rates by country
UK_CORPORATE_TAX_RATE = 0.19  # 19% UK corporation tax
CANADA_CORPORATE_TAX_RATE = 0.15  # 15% federal (simplified, provinces add more)

# QBI (Qualified Business Income) Deduction (US only)
QBI_DEDUCTION_RATE = 0.20  # 20% deduction on qualified business income

# State tax rates (US) - simplified progressive rates
STATE_TAX_RATES = {
    "CA": {  # California
        "brackets": [
            (10099, 0.01),
            (23942, 0.02),
            (37788, 0.04),
            (52455, 0.06),
            (66295, 0.08),
            (338639, 0.093),
            (406364, 0.103),
            (677275, 0.113),
            (float("inf"), 0.133),
        ],
        "standard_deduction": 5202,
    },
    "NY": {  # New York
        "brackets": [
            (8500, 0.04),
            (11700, 0.045),
            (13900, 0.0525),
            (80650, 0.055),
            (215400, 0.06),
            (1077550, 0.0685),
            (5000000, 0.0965),
            (25000000, 0.103),
            (float("inf"), 0.109),
        ],
        "standard_deduction": 8000,
    },
    "TX": {  # Texas - No state income tax
        "brackets": [(float("inf"), 0)],
        "standard_deduction": 0,
    },
    "FL": {  # Florida - No state income tax
        "brackets": [(float("inf"), 0)],
        "standard_deduction": 0,
    },
}

# UK tax brackets (2023/24)
UK_TAX_BRACKETS = [
    (12570, 0),  # Personal allowance
    (50270, 0.20),  # Basic rate
    (125140, 0.40),  # Higher rate
    (float("inf"), 0.45),  # Additional rate
]

# Canada federal tax brackets (2023)
CANADA_FEDERAL_BRACKETS = [
    (53359, 0.15),
    (106717, 0.205),
    (165430, 0.26),
    (235675, 0.29),
    (float("inf"), 0.33),
]

# Canada provincial tax - Ontario example (most common)
CANADA_ONTARIO_BRACKETS = [
    (49231, 0.0505),
    (98463, 0.0915),
    (150000, 0.1116),
    (220000, 0.1216),
    (float("inf"), 0.1316),
]


def calculate_tax_from_brackets(
    income: float, brackets: list[tuple[float, float]]
) -> float:
    """
    Calculate tax from progressive tax brackets using standard algorithm.

    This is a DRY (Don't Repeat Yourself) helper function to eliminate duplicate
    bracket calculation code throughout the module.

    Args:
        income: The income amount to calculate tax on
        brackets: List of (limit, rate) tuples representing tax brackets

    Returns:
        Total tax calculated

    Example:
        >>> brackets = [(11000, 0.10), (44725, 0.12), (95375, 0.22)]
        >>> calculate_tax_from_brackets(50000, brackets)
        6037.0
    """
    tax = 0
    prev = 0
    for limit, rate in brackets:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break
    return tax


def calculate_self_employment_tax(income: float, country: str) -> dict:
    """
    Calculate self-employment tax (US only - Social Security + Medicare).

    Returns dict with:
        - social_security_tax
        - medicare_tax
        - additional_medicare_tax
        - total_se_tax
    """
    if country != "US":
        return {
            "social_security_tax": 0,
            "medicare_tax": 0,
            "additional_medicare_tax": 0,
            "total_se_tax": 0,
        }

    # Net earnings from self-employment = 92.35% of income (deduct half of SE tax)
    net_se_income = income * 0.9235

    # Social Security tax (up to wage base)
    ss_income = min(net_se_income, SE_TAX_RATES["ss_wage_base"])
    social_security_tax = ss_income * SE_TAX_RATES["social_security"]

    # Medicare tax (all income)
    medicare_tax = net_se_income * SE_TAX_RATES["medicare"]

    # Additional Medicare tax (over threshold)
    additional_medicare_tax = 0
    if net_se_income > SE_TAX_RATES["additional_medicare_threshold"]:
        excess = net_se_income - SE_TAX_RATES["additional_medicare_threshold"]
        additional_medicare_tax = excess * SE_TAX_RATES["additional_medicare"]

    total_se_tax = social_security_tax + medicare_tax + additional_medicare_tax

    return {
        "social_security_tax": social_security_tax,
        "medicare_tax": medicare_tax,
        "additional_medicare_tax": additional_medicare_tax,
        "total_se_tax": total_se_tax,
    }


def apply_standard_deduction(
    income: float, country: str, state: Optional[str] = None
) -> float:
    """
    Apply standard deduction to reduce taxable income.
    Includes state deduction if applicable.
    """
    deduction = STANDARD_DEDUCTIONS.get(country, 0)

    # Add state deduction for US states
    if country == "US" and state and state in STATE_TAX_RATES:
        deduction += STATE_TAX_RATES[state].get("standard_deduction", 0)

    return max(0, income - deduction)


def calculate_state_tax(income: float, state: str) -> float:
    """
    Calculate state income tax for US states.
    """
    if state not in STATE_TAX_RATES:
        return 0

    state_data = STATE_TAX_RATES[state]
    brackets = state_data["brackets"]
    return calculate_tax_from_brackets(income, brackets)


def calculate_uk_tax(income: float) -> float:
    """
    Calculate UK income tax using UK brackets.
    """
    return calculate_tax_from_brackets(income, UK_TAX_BRACKETS)


def calculate_canada_tax(income: float) -> dict:
    """
    Calculate Canada tax (federal + provincial).
    Using Ontario as default province.
    """
    # Federal tax
    federal_tax = calculate_tax_from_brackets(income, CANADA_FEDERAL_BRACKETS)

    # Provincial tax (Ontario)
    provincial_tax = calculate_tax_from_brackets(income, CANADA_ONTARIO_BRACKETS)

    return {
        "federal_tax": federal_tax,
        "provincial_tax": provincial_tax,
        "total_tax": federal_tax + provincial_tax,
    }


def apply_qbi_deduction(business_income: float, country: str) -> float:
    """
    Apply QBI (Qualified Business Income) deduction for US businesses.
    20% deduction on qualified business income.
    """
    if country == "US" and business_income > 0:
        # QBI deduction is 20% of business income (simplified)
        qbi_deduction = business_income * QBI_DEDUCTION_RATE
        # Phase-out limits apply but we'll use simplified version
        return qbi_deduction
    return 0


def calculate_optimal_salary(after_corp_tax: float, country: str) -> dict:
    """
    Calculate optimal salary amount for Business+Mixed strategy.

    Strategy: Pay salary up to the top of lower tax brackets, rest as dividend.
    For US: Pay salary up to top of 12% bracket ($44,725), rest as dividend.

    Returns dict with:
        - recommended_salary
        - dividend_amount
        - reason
    """
    if country == "US":
        # US strategy: Fill up the 12% bracket, rest as dividend
        # 12% bracket ends at $44,725 for 2023
        standard_deduction = STANDARD_DEDUCTIONS.get("US", 13850)
        bracket_12_top = 44725
        optimal_salary = min(after_corp_tax, bracket_12_top + standard_deduction)

        dividend_amount = max(0, after_corp_tax - optimal_salary)

        return {
            "recommended_salary": optimal_salary,
            "dividend_amount": dividend_amount,
            "reason": f"Pay salary up to top of 12% bracket (${bracket_12_top:,}), rest as dividend to minimize tax",
        }

    elif country == "Spain":
        # Spain strategy: Similar approach with Spain brackets
        # Second bracket ends at €20,200 (24% rate)
        standard_deduction = STANDARD_DEDUCTIONS.get("Spain", 5550)
        bracket_24_top = 20200
        optimal_salary = min(after_corp_tax, bracket_24_top + standard_deduction)

        dividend_amount = max(0, after_corp_tax - optimal_salary)

        return {
            "recommended_salary": optimal_salary,
            "dividend_amount": dividend_amount,
            "reason": f"Pay salary up to top of 24% bracket (€{bracket_24_top:,}), rest as dividend",
        }

    else:
        # Default: 50/50 split
        return {
            "recommended_salary": after_corp_tax * 0.5,
            "dividend_amount": after_corp_tax * 0.5,
            "reason": "50/50 salary-dividend split (country-specific optimization not available)",
        }


def calculate_project_taxes(
    revenue: float,
    costs: float,
    num_people: int,
    country: str,
    tax_structure: str,  # "Individual" or "Business"
    distribution_method: str = "N/A",  # "N/A", "Salary", "Dividend", "Mixed", "Reinvest"
    salary_amount: float = 0,  # Only used for "Mixed"
    state: Optional[str] = None,  # US state (CA, NY, TX, FL) - optional
) -> Dict[str, Any]:
    """
    Calculate taxes for a project using the specified tax structure and distribution method.

    Returns:
        dict with:
            - gross_income: Total income before any taxes
            - corporate_tax: Corporate tax (0 if Individual)
            - personal_tax: Personal income tax (Individual or Business salary)
            - dividend_tax: Dividend tax (Business dividend only)
            - total_tax: Sum of all taxes
            - net_income_group: Total take-home for the group
            - net_income_per_person: Average take-home per person
            - effective_rate: Total tax / gross income
            - breakdown: List of tax components
    """

    gross_income = revenue - costs

    if num_people == 0:
        raise ValueError("Number of people must be greater than 0")

    # ===== INDIVIDUAL TAX (Self-Employed / Freelancer) =====
    if tax_structure == "Individual":
        individual_income = gross_income / num_people

        # Country-specific calculations
        if country == "UK":
            # UK Individual Tax
            personal_tax_per_person = calculate_uk_tax(individual_income)
            se_tax_per_person = (
                0  # UK uses National Insurance instead (simplified here)
            )
            state_tax_per_person = 0

            breakdown = [
                {
                    "label": "UK Income Tax",
                    "amount": personal_tax_per_person * num_people,
                }
            ]

        elif country == "Canada":
            # Canada Individual Tax
            canada_taxes = calculate_canada_tax(individual_income)
            personal_tax_per_person = canada_taxes["federal_tax"]
            state_tax_per_person = canada_taxes["provincial_tax"]  # Provincial tax
            se_tax_per_person = 0  # Canada has different system (simplified)

            breakdown = [
                {
                    "label": "Federal Tax (Canada)",
                    "amount": personal_tax_per_person * num_people,
                },
                {
                    "label": "Provincial Tax (Ontario)",
                    "amount": state_tax_per_person * num_people,
                },
            ]

        else:
            # US, Spain, and other countries
            # Apply standard deduction
            taxable_income = apply_standard_deduction(individual_income, country)

            # Calculate federal/national income tax on taxable income
            personal_tax_per_person = setup.calculate_tax_from_db(
                taxable_income, country, "Individual"
            )

            # Calculate self-employment tax (US only, on gross income before deduction)
            se_tax_result = calculate_self_employment_tax(individual_income, country)
            se_tax_per_person = se_tax_result["total_se_tax"]

            # Calculate state tax (US only, if state provided)
            state_tax_per_person = 0
            if country == "US" and state:
                state_tax_per_person = calculate_state_tax(individual_income, state)

            breakdown = [
                {
                    "label": "Federal Income Tax",
                    "amount": personal_tax_per_person * num_people,
                }
            ]

            # Add SE tax breakdown if applicable
            if se_tax_per_person > 0:
                breakdown.append(
                    {
                        "label": "Self-Employment Tax (SS + Medicare)",
                        "amount": se_tax_per_person * num_people,
                        "note": f"Social Security: ${se_tax_result['social_security_tax'] * num_people:,.2f}, Medicare: ${se_tax_result['medicare_tax'] * num_people:,.2f}",
                    }
                )

            # Add state tax if applicable
            if state_tax_per_person > 0:
                breakdown.append(
                    {
                        "label": f"State Tax ({state})",
                        "amount": state_tax_per_person * num_people,
                    }
                )

        # Total tax per person = income tax + SE tax + state tax
        total_tax_per_person = (
            personal_tax_per_person + se_tax_per_person + state_tax_per_person
        )
        total_personal_tax = total_tax_per_person * num_people

        net_income_per_person = individual_income - total_tax_per_person
        net_income_group = net_income_per_person * num_people

        return {
            "gross_income": gross_income,
            "corporate_tax": 0,
            "personal_tax": personal_tax_per_person * num_people,
            "se_tax": se_tax_per_person * num_people,
            "state_tax": state_tax_per_person * num_people,
            "dividend_tax": 0,
            "total_tax": total_personal_tax,
            "net_income_group": net_income_group,
            "net_income_per_person": net_income_per_person,
            "effective_rate": (total_personal_tax / gross_income * 100)
            if gross_income > 0
            else 0,
            "standard_deduction_used": STANDARD_DEDUCTIONS.get(country, 0) * num_people
            if country not in ["UK", "Canada"]
            else 0,
            "breakdown": breakdown,
        }

    # ===== BUSINESS TAX (Corporation) =====
    elif tax_structure == "Business":
        # Step 1: Apply QBI deduction for US businesses (reduces taxable income)
        qbi_deduction = apply_qbi_deduction(gross_income, country)
        taxable_business_income = gross_income - qbi_deduction

        # Step 2: Company pays corporate tax on profits (after QBI deduction)
        # For UK and Canada, use flat corporate tax rates
        if country == "UK":
            corporate_tax = taxable_business_income * UK_CORPORATE_TAX_RATE
        elif country == "Canada":
            corporate_tax = taxable_business_income * CANADA_CORPORATE_TAX_RATE
        else:
            corporate_tax = setup.calculate_tax_from_db(
                taxable_business_income, country, "Business"
            )

        after_corp_tax = gross_income - corporate_tax

        # Step 3: Distribute to owners based on distribution_method
        if distribution_method == "Salary":
            # Pay all after-tax profit as salary → triggers personal income tax
            if country == "UK":
                personal_tax = calculate_uk_tax(after_corp_tax)
            elif country == "Canada":
                canada_taxes = calculate_canada_tax(after_corp_tax)
                personal_tax = canada_taxes["total_tax"]
            else:
                # Apply standard deduction to salary
                taxable_salary = apply_standard_deduction(after_corp_tax, country)
                personal_tax = setup.calculate_tax_from_db(
                    taxable_salary, country, "Individual"
                )

            dividend_tax = 0
            net_income_group = after_corp_tax - personal_tax
            total_tax = corporate_tax + personal_tax

            breakdown = []
            if qbi_deduction > 0:
                breakdown.append(
                    {
                        "label": "QBI Deduction (20%)",
                        "amount": -qbi_deduction,
                        "note": f"Reduces taxable business income by ${qbi_deduction:,.0f}",
                    }
                )
            breakdown.extend(
                [
                    {"label": "Corporate Tax", "amount": corporate_tax},
                    {"label": "Personal Tax (on salary)", "amount": personal_tax},
                ]
            )

        elif distribution_method == "Dividend":
            # Pay all after-tax profit as dividends → triggers dividend tax
            dividend_rate = DIVIDEND_TAX_RATES.get(country, 0.15)
            dividend_tax = after_corp_tax * dividend_rate
            personal_tax = 0
            net_income_group = after_corp_tax - dividend_tax
            total_tax = corporate_tax + dividend_tax

            breakdown = []
            if qbi_deduction > 0:
                breakdown.append(
                    {
                        "label": "QBI Deduction (20%)",
                        "amount": -qbi_deduction,
                        "note": f"Reduces taxable business income by ${qbi_deduction:,.0f}",
                    }
                )
            breakdown.extend(
                [
                    {"label": "Corporate Tax", "amount": corporate_tax},
                    {
                        "label": f"Dividend Tax ({dividend_rate*100}%)",
                        "amount": dividend_tax,
                    },
                ]
            )

        elif distribution_method == "Mixed":
            # Pay some as salary, rest as dividend
            # If salary_amount is 0, auto-calculate optimal split
            if salary_amount == 0:
                optimal = calculate_optimal_salary(after_corp_tax, country)
                salary_amount = optimal["recommended_salary"]
                auto_optimized = True
            else:
                auto_optimized = False

            if salary_amount > after_corp_tax:
                raise ValueError(
                    f"Salary amount ({salary_amount}) exceeds after-tax profit ({after_corp_tax})"
                )

            # Salary portion
            if country == "UK":
                salary_tax = calculate_uk_tax(salary_amount)
            elif country == "Canada":
                canada_taxes = calculate_canada_tax(salary_amount)
                salary_tax = canada_taxes["total_tax"]
            else:
                # Apply standard deduction to salary
                taxable_salary = apply_standard_deduction(salary_amount, country)
                salary_tax = setup.calculate_tax_from_db(
                    taxable_salary, country, "Individual"
                )

            after_salary = after_corp_tax - salary_amount

            # Dividend portion
            dividend_rate = DIVIDEND_TAX_RATES.get(country, 0.15)
            dividend_tax = after_salary * dividend_rate

            net_income_group = salary_amount - salary_tax + after_salary - dividend_tax
            personal_tax = salary_tax
            total_tax = corporate_tax + salary_tax + dividend_tax

            breakdown = []
            if qbi_deduction > 0:
                breakdown.append(
                    {
                        "label": "QBI Deduction (20%)",
                        "amount": -qbi_deduction,
                        "note": f"Reduces taxable business income by ${qbi_deduction:,.0f}",
                    }
                )
            breakdown.extend(
                [
                    {"label": "Corporate Tax", "amount": corporate_tax},
                    {
                        "label": f"Personal Tax (on ${salary_amount:,.0f} salary)",
                        "amount": salary_tax,
                    },
                    {
                        "label": f"Dividend Tax ({dividend_rate*100}% on ${after_salary:,.0f})",
                        "amount": dividend_tax,
                    },
                ]
            )

            if auto_optimized:
                breakdown.append(
                    {
                        "label": "Auto-Optimized Split",
                        "amount": 0,
                        "note": calculate_optimal_salary(after_corp_tax, country)[
                            "reason"
                        ],
                    }
                )

        elif distribution_method == "Reinvest":
            # Keep money in company → no personal tax now
            personal_tax = 0
            dividend_tax = 0
            net_income_group = 0  # No personal take-home
            total_tax = corporate_tax

            breakdown = []
            if qbi_deduction > 0:
                breakdown.append(
                    {
                        "label": "QBI Deduction (20%)",
                        "amount": -qbi_deduction,
                        "note": f"Reduces taxable business income by ${qbi_deduction:,.0f}",
                    }
                )
            breakdown.extend(
                [
                    {"label": "Corporate Tax", "amount": corporate_tax},
                    {
                        "label": "Personal Tax",
                        "amount": 0,
                        "note": "Deferred until distribution",
                    },
                ]
            )

        else:
            # Default to Salary if method not specified
            personal_tax = setup.calculate_tax_from_db(
                after_corp_tax, country, "Individual"
            )
            dividend_tax = 0
            net_income_group = after_corp_tax - personal_tax
            total_tax = corporate_tax + personal_tax

            breakdown = [
                {"label": "Corporate Tax", "amount": corporate_tax},
                {"label": "Personal Tax (on salary)", "amount": personal_tax},
            ]

        net_income_per_person = net_income_group / num_people if num_people > 0 else 0

        return {
            "gross_income": gross_income,
            "corporate_tax": corporate_tax,
            "personal_tax": personal_tax,
            "dividend_tax": dividend_tax,
            "total_tax": total_tax,
            "net_income_group": net_income_group,
            "net_income_per_person": net_income_per_person,
            "effective_rate": (total_tax / gross_income * 100)
            if gross_income > 0
            else 0,
            "breakdown": breakdown,
            "company_retained": after_corp_tax
            if distribution_method == "Reinvest"
            else 0,
        }

    else:
        raise ValueError(
            f"Invalid tax_structure: {tax_structure}. Must be 'Individual' or 'Business'"
        )


def get_optimal_strategy(
    revenue: float,
    costs: float,
    num_people: int,
    country: str,
    state: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate all possible tax strategies and return the optimal one.

    Returns dict with:
        - all_strategies: List of all calculated strategies
        - optimal: The strategy with highest net_income_group
        - savings: Money saved vs worst strategy
    """

    strategies = []

    # Individual
    individual = calculate_project_taxes(
        revenue, costs, num_people, country, "Individual", "N/A", 0, state
    )
    individual["strategy_name"] = "Individual Tax"
    strategies.append(individual)

    # Business - Salary
    business_salary = calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Salary", 0, state
    )
    business_salary["strategy_name"] = "Business + Salary"
    strategies.append(business_salary)

    # Business - Dividend
    business_dividend = calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Dividend", 0, state
    )
    business_dividend["strategy_name"] = "Business + Dividend"
    strategies.append(business_dividend)

    # Business - Mixed (Auto-Optimized)
    business_mixed = calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Mixed", 0, state
    )
    business_mixed["strategy_name"] = "Business + Mixed (Optimized)"
    strategies.append(business_mixed)

    # Business - Reinvest
    business_reinvest = calculate_project_taxes(
        revenue, costs, num_people, country, "Business", "Reinvest", 0, state
    )
    business_reinvest["strategy_name"] = "Business + Reinvest"
    strategies.append(business_reinvest)

    # Find optimal (highest net income for strategies that give cash now)
    cashflow_strategies = [s for s in strategies if s["net_income_group"] > 0]
    optimal = max(cashflow_strategies, key=lambda x: x["net_income_group"])
    worst = min(cashflow_strategies, key=lambda x: x["net_income_group"])

    savings = optimal["net_income_group"] - worst["net_income_group"]

    return {
        "all_strategies": strategies,
        "optimal": optimal,
        "worst": worst,
        "savings": savings,
    }
