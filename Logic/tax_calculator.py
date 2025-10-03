"""
Tax calculation module - testable functions without side effects.
"""

from DB import setup


def calculate_tax(income: float, tax_brackets: list[tuple[float, float]]) -> float:
    """
    Calculate tax using progressive tax brackets.

    Args:
        income: The income amount to calculate tax for
        tax_brackets: List of (limit, rate) tuples

    Returns:
        Total tax amount
    """
    tax = 0
    prev = 0
    for limit, rate in tax_brackets:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break
    return tax


def calculate_tax_from_db(income: float, country: str, tax_type: str) -> float:
    """
    Calculate tax by fetching brackets from database.

    Args:
        income: The income amount
        country: Country name (e.g., "US", "Spain")
        tax_type: Tax type ("Individual" or "Business")

    Returns:
        Total tax amount

    Raises:
        ValueError: If no tax brackets found for country/type
    """
    brackets = setup.get_tax_brackets(country, tax_type)
    if not brackets:
        raise ValueError(f"No tax brackets found for {country} {tax_type}")

    return calculate_tax(income, brackets)


def split_work_shares(total_amount: float, work_shares: list[float]) -> list[float]:
    """
    Distribute total amount based on work shares.

    Args:
        total_amount: Total amount to distribute
        work_shares: List of work share percentages (should sum to 1.0)

    Returns:
        List of distributed amounts
    """
    return [total_amount * share for share in work_shares]


def calculate_profit(revenue: float, costs: list[float]) -> float:
    """
    Calculate profit from revenue and costs.

    Args:
        revenue: Total revenue
        costs: List of cost amounts

    Returns:
        Profit amount (revenue - total costs)
    """
    return revenue - sum(costs)
