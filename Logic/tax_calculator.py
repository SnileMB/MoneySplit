"""
Tax calculation module - testable functions without side effects.

This module provides core tax calculation functionality that is used
throughout the application. To reduce duplication, core bracket-based
calculations are imported from tax_engine.
"""

from DB import setup
from Logic.tax_engine import calculate_tax_from_brackets


def calculate_tax(income: float, tax_brackets: list[tuple[float, float]]) -> float:
    """
    Calculate tax using progressive tax brackets.

    This is now a wrapper around calculate_tax_from_brackets for backward compatibility.

    Args:
        income: The income amount to calculate tax for
        tax_brackets: List of (limit, rate) tuples

    Returns:
        Total tax amount
    """
    return calculate_tax_from_brackets(income, tax_brackets)


def calculate_tax_from_db(income: float, country: str, tax_type: str) -> float:
    """
    Calculate tax by fetching brackets from database.

    This is the primary entry point for tax calculations throughout the application.
    It fetches the appropriate tax brackets from the database based on the country
    and tax type, then applies the progressive tax bracket algorithm.

    Args:
        income (float): The income amount to calculate tax on.
        country (str): Country name (e.g., "US", "Spain"). Must match database records.
        tax_type (str): Tax type classification ("Individual" or "Business").

    Returns:
        float: Total tax amount calculated based on progressive brackets.

    Raises:
        ValueError: If no tax brackets found for the specified country/type combination.

    Example:
        >>> tax = calculate_tax_from_db(50000, "US", "Individual")
        >>> print(f"Tax owed: ${tax:,.2f}")
        Tax owed: $5,661.00

    Notes:
        - Uses progressive tax brackets (income is taxed at different rates)
        - Brackets are fetched from the tax_brackets database table
        - Applies standard deductions (if configured in tax_engine)
    """
    brackets = setup.get_tax_brackets(country, tax_type)
    if not brackets:
        raise ValueError(f"No tax brackets found for {country} {tax_type}")

    return calculate_tax(income, brackets)


def split_work_shares(total_amount: float, work_shares: list[float]) -> list[float]:
    """
    Distribute total amount based on work shares.

    Takes a total amount (income, revenue, etc.) and distributes it proportionally
    based on each person's work share percentage. Used to calculate per-person amounts
    in multi-person projects.

    Args:
        total_amount (float): Total amount to distribute (e.g., revenue, profit).
        work_shares (list[float]): List of work share percentages. Should sum to 1.0.
                                   Example: [0.6, 0.4] for 60/40 split.

    Returns:
        list[float]: List of distributed amounts in same order as work_shares.

    Example:
        >>> profit = 10000
        >>> shares = [0.6, 0.4]  # 60% and 40%
        >>> distributed = split_work_shares(profit, shares)
        >>> print(distributed)
        [6000.0, 4000.0]

    Notes:
        - Assumes work_shares sum to 1.0 (or close to it with tolerance)
        - Returns amounts in same order as input work_shares
        - Useful for distributing after-tax amounts to individuals
    """
    return [total_amount * share for share in work_shares]


def calculate_profit(revenue: float, costs: list[float]) -> float:
    """
    Calculate profit from revenue and costs.

    Computes the profit (or loss) by subtracting all costs from total revenue.
    This is the foundation amount used for tax calculations in MoneySplit.

    Args:
        revenue (float): Total revenue generated from the project/business.
        costs (list[float]): List of all expense amounts. Can be empty for zero costs.

    Returns:
        float: Profit amount (revenue - total costs). Can be negative if costs exceed revenue.

    Example:
        >>> revenue = 100000
        >>> costs = [10000, 5000, 2500]  # Various expenses
        >>> profit = calculate_profit(revenue, costs)
        >>> print(f"Profit: ${profit:,.2f}")
        Profit: $82,500.00

    Notes:
        - Profit can be negative (indicating a loss)
        - All costs must be positive values
        - No deductions or adjustments are applied here
        - Tax calculations use this as the basis (gross income)
    """
    return revenue - sum(costs)
