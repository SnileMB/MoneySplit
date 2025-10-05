# ProgramBackend.py
from MoneySplit.DB import setup
from MoneySplit.Logic import validators

# - Inputs -
num_people = validators.safe_int_input("Enter the number of people: ", "Number of people", min_value=1)
revenue = validators.safe_float_input("Enter the revenue: ", "Revenue")

num_costs = validators.safe_int_input("Enter the number of different costs: ", "Number of costs", min_value=0)
total_costs = 0
for i in range(num_costs):
    cost = validators.safe_float_input(f"Enter cost {i + 1}: ", f"Cost {i + 1}")
    total_costs += cost

print("Total costs:", total_costs)

income = revenue - total_costs
group_income = income
individual_income = income / num_people if num_people > 0 else 0

tax_origin = validators.safe_int_input("Enter the country (1 for US, 2 for Spain): ", "Country", min_value=1, max_value=2)
tax_option = validators.safe_int_input("Enter tax option (1 for individual, 2 for business): ", "Tax option", min_value=1, max_value=2)

# Convert numeric input to strings for DB-driven brackets
country = "US" if tax_origin == 1 else "Spain"
tax_type = "Individual" if tax_option == 1 else "Business"


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


# - Calculate and Display Results -
if tax_option == 1:  # Individual tax
    tax = calculate_tax_from_db(individual_income, country, tax_type)
else:  # Business tax
    tax = calculate_tax_from_db(group_income, country, tax_type)

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


# ==============================
# Collect People Information
# ==============================
print("\nNow enter details for each person:")

record_id = setup.save_to_db()  # Save project-level data first
total_work_share = 0.0

people_shares = []
people_data = []  # Store person ID and details

for i in range(num_people):
    name = validators.safe_string_input(f"Name of person {i + 1}: ", f"Person {i + 1} name")

    # If only 1 person, auto-assign work_share = 1.0
    if num_people == 1:
        work_share = 1.0
        print(f"✅ {name} is the only person - automatically assigned 100% work share")
    else:
        work_share = validators.safe_float_input(f"Work share for {name} (0.0–1.0): ", "Work share")
        try:
            work_share = validators.validate_work_share(work_share)
        except validators.ValidationError as e:
            print(f"❌ {e}")
            work_share = validators.safe_float_input(f"Work share for {name} (0.0–1.0): ", "Work share")
            work_share = validators.validate_work_share(work_share)

    total_work_share += work_share
    people_shares.append(work_share)

    if tax_option == 1:  # Individual
        gross_income = individual_income * work_share * num_people
        tax_paid = tax * work_share
        net_income = gross_income - tax_paid
    else:  # Business → distributed after company tax
        gross_income = group_income * work_share
        tax_paid = tax * work_share
        net_income = gross_income - tax_paid

    person_id = setup.add_person(record_id, name, work_share, gross_income, tax_paid, net_income)
    people_data.append({
        'person_id': person_id,
        'name': name,
        'work_share': work_share,
        'gross_income': gross_income,
        'tax_paid': tax_paid,
        'net_income': net_income
    })

# After all people are added - validate total work shares
if num_people > 1:  # Only validate if more than 1 person
    try:
        validators.validate_work_shares(people_shares)
        print("✅ Work shares add up to 1.0")
    except validators.ValidationError as e:
        print(f"⚠️ Warning: {e}")

# Display summary of created people
print(f"\n📋 Project Summary (Record ID: {record_id}):")
print(f"{'Person ID':<10} | {'Name':<15} | {'Work Share':>12} | {'Gross Income':>15} | {'Tax Paid':>12} | {'Net Income':>15}")
print("-" * 90)
for person in people_data:
    print(f"{person['person_id']:<10} | {person['name']:<15} | {person['work_share']:>12.2%} | ${person['gross_income']:>14,.2f} | ${person['tax_paid']:>11,.2f} | ${person['net_income']:>14,.2f}")

# Export record_id for use by project_menu
LAST_RECORD_ID = record_id
