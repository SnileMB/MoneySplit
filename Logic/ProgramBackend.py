# ProgramBackend.py
from MoneySplit.DB import setup

# - Inputs -
num_people = int(input("Enter the number of people: "))
revenue = float(input("Enter the revenue: "))

num_costs = int(input("Enter the number of different costs: "))
total_costs = 0
for i in range(num_costs):
    cost = float(input(f"Enter cost {i + 1}: "))
    total_costs += cost

print("Total costs:", total_costs)

income = revenue - total_costs
group_income = income
individual_income = income / num_people if num_people > 0 else 0

tax_origin = int(input("Enter the country (1 for US, 2 for Spain): "))
tax_option = int(input("Enter tax option (1 for individual, 2 for business): "))

# Convert numeric input to strings for DB-driven brackets
country = "US" if tax_origin == 1 else "Spain"
tax_type = "Individual" if tax_option == 1 else "Business"


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

for i in range(num_people):
    name = input(f"Name of person {i + 1}: ").strip()
    work_share = float(input(f"Work share for {name} (0.0–1.0): "))
    total_work_share += work_share

    if tax_option == 1:  # Individual
        gross_income = individual_income * work_share * num_people
        tax_paid = tax * work_share
        net_income = gross_income - tax_paid
    else:  # Business → distributed after company tax
        gross_income = group_income * work_share
        tax_paid = tax * work_share
        net_income = gross_income - tax_paid

    setup.add_person(record_id, name, work_share, gross_income, tax_paid, net_income)

# After all people are added
if abs(total_work_share - 1.0) > 0.01:  # allow slight float tolerance
    print(f"⚠️ Warning: total work share = {total_work_share:.2f}, not 1.0")
else:
    print("✅ Work shares add up to 1.0")
