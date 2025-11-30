# ProgramBackend.py
"""
Backend CLI for MoneySplit project processing.

Handles interactive input collection for project creation including:
- Number of participants and revenue/cost collection
- Tax calculation configuration
- Individual participant data and work share allocation
- Tax computation and result display
"""
from typing import Dict, List, Tuple, Any
from MoneySplit.DB import setup
from MoneySplit.Logic import validators


def collect_project_financials() -> Tuple[int, float, float]:
    """
    Collect project financial information from user input.

    Prompts for number of participants, revenue, and itemized costs.

    Returns:
        Tuple[int, float, float]: (num_people, revenue, total_costs)
            - num_people: Number of people in the project (1+)
            - revenue: Total project revenue
            - total_costs: Sum of all expenses

    Example:
        >>> num_people, revenue, costs = collect_project_financials()
        >>> print(f"Project: {num_people} people, ${revenue:,.2f} revenue")
    """
    num_people = validators.safe_int_input(
        "Enter the number of people: ", "Number of people", min_value=1
    )
    revenue = validators.safe_float_input("Enter the revenue: ", "Revenue")

    num_costs = validators.safe_int_input(
        "Enter the number of different costs: ", "Number of costs", min_value=0
    )
    total_costs = 0
    for i in range(num_costs):
        cost = validators.safe_float_input(f"Enter cost {i + 1}: ", f"Cost {i + 1}")
        total_costs += cost

    print("Total costs:", total_costs)
    return num_people, revenue, total_costs


def collect_tax_configuration() -> Tuple[str, str, int, int]:
    """
    Collect tax configuration from user input.

    Prompts for country and tax structure preferences.

    Returns:
        Tuple[str, str, int, int]: (country, tax_type, tax_origin, tax_option)
            - country: "US" or "Spain"
            - tax_type: "Individual" or "Business"
            - tax_origin: Original numeric input (1 or 2)
            - tax_option: Original numeric input (1 or 2)

    Example:
        >>> country, tax_type, origin, option = collect_tax_configuration()
        >>> print(f"Tax: {tax_type} in {country}")
    """
    tax_origin = validators.safe_int_input(
        "Enter the country (1 for US, 2 for Spain): ",
        "Country",
        min_value=1,
        max_value=2,
    )
    tax_option = validators.safe_int_input(
        "Enter tax option (1 for individual, 2 for business): ",
        "Tax option",
        min_value=1,
        max_value=2,
    )

    # Convert numeric input to strings for DB-driven brackets
    country = "US" if tax_origin == 1 else "Spain"
    tax_type = "Individual" if tax_option == 1 else "Business"

    return country, tax_type, tax_origin, tax_option


# - Tax Calculation Functions -
def us_individual_tax(income: float) -> float:
    return calculate_tax_from_db(income, "US", "Individual")


def us_business_tax(income: float) -> float:
    return calculate_tax_from_db(income, "US", "Business")


def spain_individual_tax(income: float) -> float:
    return calculate_tax_from_db(income, "Spain", "Individual")


def spain_business_tax(income: float) -> float:
    return calculate_tax_from_db(income, "Spain", "Business")


# - Generic Tax Function (DB-driven) -
def calculate_tax_from_db(income: float, country: str, tax_type: str) -> float:
    """
    Generic tax calculator that fetches brackets from DB.
    """
    brackets = setup.get_tax_brackets(country, tax_type)
    if not brackets:
        raise ValueError(f"No tax brackets found for {country} {tax_type}")

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


def calculate_project_tax(
    income: float, num_people: int, tax_option: int, country: str, tax_type: str
) -> float:
    """
    Calculate tax for the project based on structure.

    For individual tax: applies per-person calculation
    For business tax: applies to total group income

    Args:
        income: Group or individual income depending on tax option
        num_people: Number of people in project
        tax_option: 1 for individual, 2 for business
        country: Country for tax bracket lookup
        tax_type: "Individual" or "Business"

    Returns:
        float: Total tax amount owed
    """
    if tax_option == 1:  # Individual tax
        tax_basis = income / num_people if num_people > 0 else 0
    else:  # Business tax
        tax_basis = income

    return calculate_tax_from_db(tax_basis, country, tax_type)


def display_tax_results(
    tax: float,
    tax_option: int,
    individual_income: float,
    group_income: float,
    num_people: int,
) -> None:
    """
    Display formatted tax calculation results to console.

    Args:
        tax: Calculated tax amount
        tax_option: 1 for individual, 2 for business
        individual_income: Per-person income
        group_income: Total group income
        num_people: Number of people in project

    Example:
        >>> display_tax_results(5000, 1, 50000, 100000, 2)
    """
    if tax_option == 1:
        print(f"\nEffective tax rate: {(tax / individual_income) * 100:,.2f}%")
        print(f"\nIndividual income: ${individual_income:,.2f}")
        print(f"Tax per person: ${tax:,.2f}")
        print(f"Net income per person: ${individual_income - tax:,.2f}")
        print(f"Total tax for all people: ${tax * num_people:,.2f}")
    else:
        print(f"Effective tax rate: {(tax / group_income) * 100:,.2f}%")
        print(f"\nBusiness income: ${group_income:,.2f}")
        print(f"Business tax: ${tax:,.2f}")
        print(f"Net Business income: ${group_income - tax:,.2f}")
        print(f"\nNet income per person: {(group_income - tax) / num_people:,.2f}")


def collect_person_work_share(name: str, num_people: int) -> float:
    """
    Collect and validate work share for a person.

    Automatically assigns 100% share if only 1 person in project.
    For multiple people, prompts for input and validates.

    Args:
        name: Person's name (for display)
        num_people: Total number of people in project

    Returns:
        float: Validated work share (0.0 to 1.0)

    Example:
        >>> share = collect_person_work_share("Alice", 2)
        >>> print(f"Work share: {share:.1%}")
    """
    # If only 1 person, auto-assign work_share = 1.0
    if num_people == 1:
        print(f"✅ {name} is the only person - automatically assigned 100% work share")
        return 1.0

    work_share = validators.safe_float_input(
        f"Work share for {name} (0.0–1.0): ", "Work share"
    )
    try:
        work_share = validators.validate_work_share(work_share)
    except validators.ValidationError as e:
        print(f"❌ {e}")
        work_share = validators.safe_float_input(
            f"Work share for {name} (0.0–1.0): ", "Work share"
        )
        work_share = validators.validate_work_share(work_share)

    return work_share


def calculate_person_financials(
    work_share: float,
    tax_option: int,
    individual_income: float,
    group_income: float,
    tax: float,
    num_people: int,
) -> Dict[str, float]:
    """
    Calculate financial breakdown for a person.

    Args:
        work_share: Person's share of work (0.0 to 1.0)
        tax_option: 1 for individual, 2 for business
        individual_income: Per-person income
        group_income: Total group income
        tax: Total tax calculated
        num_people: Number of people in project

    Returns:
        Dict[str, float]: Contains gross_income, tax_paid, net_income
    """
    if tax_option == 1:  # Individual
        gross_income = individual_income * work_share * num_people
        tax_paid = tax * work_share
    else:  # Business → distributed after company tax
        gross_income = group_income * work_share
        tax_paid = tax * work_share

    net_income = gross_income - tax_paid
    return {
        "gross_income": gross_income,
        "tax_paid": tax_paid,
        "net_income": net_income,
    }


def display_project_summary(people_data: List[Dict[str, Any]], record_id: int) -> None:
    """
    Display formatted project summary with all participants.

    Args:
        people_data: List of dicts with person_id, name, work_share, financials
        record_id: Database record ID for the project

    Example:
        >>> display_project_summary([{...}], 42)
    """
    print(f"\n📋 Project Summary (Record ID: {record_id}):")
    print(
        f"{'Person ID':<10} | {'Name':<15} | {'Work Share':>12} | {'Gross Income':>15} | {'Tax Paid':>12} | {'Net Income':>15}"
    )
    print("-" * 90)
    for person in people_data:
        print(
            f"{person['person_id']:<10} | {person['name']:<15} | {person['work_share']:>12.2%} | ${person['gross_income']:>14,.2f} | ${person['tax_paid']:>11,.2f} | ${person['net_income']:>14,.2f}"
        )


def collect_people_data(
    num_people: int,
    record_id: int,
    tax_option: int,
    individual_income: float,
    group_income: float,
    tax: float,
) -> List[Dict[str, Any]]:
    """
    Collect data for all people in the project.

    Prompts for each person's name and work share, calculates financials,
    and saves to database.

    Args:
        num_people: Number of people in project
        record_id: Database record ID
        tax_option: 1 for individual, 2 for business
        individual_income: Per-person income
        group_income: Total group income
        tax: Calculated tax amount

    Returns:
        List[Dict[str, Any]]: List of people data with financials

    Example:
        >>> people_data = collect_people_data(2, 1, 1, 50000, 100000, 5000)
    """
    print("\nNow enter details for each person:")

    people_shares = []
    people_data = []

    for i in range(num_people):
        name = validators.safe_string_input(
            f"Name of person {i + 1}: ", f"Person {i + 1} name"
        )

        work_share = collect_person_work_share(name, num_people)
        people_shares.append(work_share)

        financials = calculate_person_financials(
            work_share, tax_option, individual_income, group_income, tax, num_people
        )

        person_id = setup.add_person(
            record_id,
            name,
            work_share,
            financials["gross_income"],
            financials["tax_paid"],
            financials["net_income"],
        )
        people_data.append(
            {
                "person_id": person_id,
                "name": name,
                "work_share": work_share,
                "gross_income": financials["gross_income"],
                "tax_paid": financials["tax_paid"],
                "net_income": financials["net_income"],
            }
        )

    # After all people are added - validate total work shares
    if num_people > 1:  # Only validate if more than 1 person
        try:
            validators.validate_work_shares(people_shares)
            print("✅ Work shares add up to 1.0")
        except validators.ValidationError as e:
            print(f"⚠️ Warning: {e}")

    return people_data


# ==============================
# Main Execution Flow
# ==============================
# Step 1: Collect project financials
num_people, revenue, total_costs = collect_project_financials()

# Step 2: Calculate income and collect tax configuration
income = revenue - total_costs
group_income = income
individual_income = income / num_people if num_people > 0 else 0
country, tax_type, tax_origin, tax_option = collect_tax_configuration()

# Step 3: Calculate project tax
tax = calculate_project_tax(income, num_people, tax_option, country, tax_type)

# Step 4: Display tax results
display_tax_results(tax, tax_option, individual_income, group_income, num_people)

# Step 5: Save project to database and collect people data
record_id = setup.save_to_db()
people_data = collect_people_data(
    num_people, record_id, tax_option, individual_income, group_income, tax
)

# Step 6: Display final summary
display_project_summary(people_data, record_id)

# Export record_id for use by project_menu
LAST_RECORD_ID = record_id
