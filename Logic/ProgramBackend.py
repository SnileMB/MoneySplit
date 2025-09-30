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


# - Tax Functions -
def us_individual_tax(income: float) -> float:
    brackets = [
        (10275, 0.10),
        (41775, 0.12),
        (89075, 0.22),
        (170050, 0.24),
        (215950, 0.32),
        (539900, 0.35),
        (float("inf"), 0.37),
    ]
    tax, prev = 0, 0
    for limit, rate in brackets:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break
    return tax


def us_business_tax(income: float) -> float:
    return income * 0.21


def spain_individual_tax(income: float) -> float:
    brackets = [
        (12450, 0.19),
        (20200, 0.24),
        (35200, 0.30),
        (60000, 0.37),
        (300000, 0.45),
        (float("inf"), 0.47),
    ]
    tax, prev = 0, 0
    for limit, rate in brackets:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break
    return tax


def spain_business_tax(income: float) -> float:
    return income * 0.25


def calculate_tax(individual, group, origin, option) -> float:
    if origin == 1:  # US
        if option == 1:  # Individual
            return us_individual_tax(individual)
        elif option == 2:  # Business
            return us_business_tax(group)

    elif origin == 2:  # Spain
        if option == 1:  # Individual
            return spain_individual_tax(individual)
        elif option == 2:  # Business
            return spain_business_tax(group)

    raise ValueError("Invalid tax origin or option")


# - Calculate and Display Results -
tax = calculate_tax(individual_income, group_income, tax_origin, tax_option)

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
# NEW: Collect People Information
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
        gross_income = (group_income * work_share)
        tax_paid = (tax * work_share)
        net_income = gross_income - tax_paid

    setup.add_person(record_id, name, work_share, gross_income, tax_paid, net_income)

# After all people are added
if abs(total_work_share - 1.0) > 0.01:  # allow slight float tolerance
    print(f"⚠️ Warning: total work share = {total_work_share:.2f}, not 1.0")
else:
    print("✅ Work shares add up to 1.0")
