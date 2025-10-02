from MoneySplit.DB import setup

def show_last_records(n=5):
    print(f"\n=== Last {n} Saved Records ===")
    records = setup.fetch_last_records(n)

    if not records:
        print("No records found.")
        return

    header = (
        f"{'ID':<3} | {'Origin':<6} | {'Option':<10} | "
        f"{'Revenue':>12} | {'Costs':>10} | {'Tax':>10} | "
        f"{'Net Group':>12} | {'Net Person':>12} | {'Created At'}"
    )
    print(header)
    print("-" * len(header))

    for r in records:
        id, origin, option, revenue, costs, tax, net_group, net_person, created = r
        print(
            f"{id:<3} | {origin:<6} | {option:<10} | "
            f"{float(revenue):>12,.2f} | {float(costs):>10,.2f} | {float(tax):>10,.2f} | "
            f"{float(net_group):>12,.2f} | {float(net_person):>12,.2f} | {created}"
        )


def show_people_for_record():
    try:
        record_id = int(input("Enter the ID of the record to view people: "))
        people = setup.fetch_people_by_record(record_id)

        if not people:
            print(f"❌ No people found for record {record_id}.")
            return

        print(f"\n=== People for Record {record_id} ===")
        header = f"{'ID':<3} | {'Name':<10} | {'Work Share':>10} | {'Gross':>12} | {'Tax Paid':>10} | {'Net Income':>12}"
        print(header)
        print("-" * len(header))

        for p in people:
            pid, name, work_share, gross, tax_paid, net_income = p
            print(
                f"{pid:<3} | {name:<10} | {work_share:>10.2f} | "
                f"{gross:>12,.2f} | {tax_paid:>10,.2f} | {net_income:>12,.2f}"
            )

    except ValueError:
        print("❌ Invalid input. Please enter a number.")


def delete_record_menu():
    try:
        record_id = int(input("Enter the ID of the record to delete: "))
        record = setup.get_record_by_id(record_id)

        if not record:
            print(f"❌ No record found with ID {record_id}.")
            return

        confirm = input(f"Are you sure you want to delete record {record_id} (and all linked people)? (y/n): ").strip().lower()
        if confirm == "y":
            setup.delete_record(record_id)
        else:
            print("❌ Deletion canceled.")

    except ValueError:
        print("❌ Invalid ID. Please enter a number.")


def update_record_menu():
    try:
        record_id = int(input("Enter the ID of the record to update: "))
        record = setup.get_record_by_id(record_id)

        if not record:
            print(f"❌ No record found with ID {record_id}.")
            return

        print("\nYou can update the following fields:")
        for f in sorted(setup.ALLOWED_FIELDS):
            print(f" - {f}")

        field = input("\nEnter the field to update: ").strip()

        if field not in setup.ALLOWED_FIELDS:
            print(f"❌ '{field}' is not editable. Allowed: {', '.join(sorted(setup.ALLOWED_FIELDS))}")
            return

        new_value = input(f"Enter new value for {field}: ").strip()

        if field == "num_people":
            new_value = int(new_value)
        elif field in ["revenue", "total_costs"]:
            new_value = float(new_value)

        setup.update_record(record_id, field, new_value)

    except ValueError:
        print("❌ Invalid input. Please enter a number where required.")


def show_person_history():
    name = input("Enter the person's name: ").strip()
    records = setup.fetch_records_by_person(name)

    if not records:
        print(f"❌ No records found for {name}.")
        return

    print(f"\n=== Records for {name} ===")
    header = f"{'PersonID':<8} | {'RecordID':<8} | {'Work Share':>10} | {'Gross':>12} | {'Tax Paid':>10} | {'Net Income':>12} | {'Created At'}"
    print(header)
    print("-" * len(header))

    total_gross = total_tax = total_net = 0

    for r in records:
        pid, record_id, pname, work_share, gross, tax_paid, net_income, created = r
        print(
            f"{pid:<8} | {record_id:<8} | {work_share:>10.2f} | "
            f"{gross:>12,.2f} | {tax_paid:>10,.2f} | {net_income:>12,.2f} | {created}"
        )
        total_gross += gross
        total_tax += tax_paid
        total_net += net_income

    print("\n--- Totals ---")
    print(f"Total Gross: {total_gross:,.2f}")
    print(f"Total Tax:   {total_tax:,.2f}")
    print(f"Total Net:   {total_net:,.2f}")


def update_person_menu():
    try:
        person_id = int(input("Enter the ID of the person to update: "))
        print("\nYou can update the following fields:")
        print(" - name")
        print(" - work_share")

        field = input("Enter the field to update: ").strip()
        new_value = input(f"Enter new value for {field}: ").strip()

        if field == "work_share":
            new_value = float(new_value)

        setup.update_person(person_id, field, new_value)

    except ValueError:
        print("❌ Invalid input. Please enter a number where required.")


def delete_person_menu():
    try:
        person_id = int(input("Enter the ID of the person to delete: "))
        confirm = input(f"Are you sure you want to delete person {person_id}? (y/n): ").strip().lower()
        if confirm == "y":
            setup.delete_person(person_id)
        else:
            print("❌ Deletion canceled.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")


def reset_db_menu():
    confirm = input("⚠️ This will DELETE ALL tax records and people. Type 'RESET' to confirm: ").strip()
    if confirm == "RESET":
        setup.reset_db()
    else:
        print("❌ Reset canceled.")


def reset_tax_brackets_menu():
    confirm = input("⚠️ This will DELETE ALL tax brackets and restore defaults. Type 'RESET' to confirm: ").strip()
    if confirm == "RESET":
        setup.reset_tax_brackets()
    else:
        print("❌ Reset canceled.")


def export_template_menu():
    filepath = input("Enter filename for template (default: tax_template.csv): ").strip()
    if not filepath:
        filepath = "tax_template.csv"
    setup.export_tax_template(filepath)


def view_tax_brackets_menu():
    country = input("Enter country (e.g. US, Spain): ").strip()
    tax_type = input("Enter type (Individual/Business): ").strip().title()
    rows = setup.get_tax_brackets(country, tax_type, include_id=True)
    if not rows:
        print("❌ No brackets found.")
    else:
        print(f"\nBrackets for {country} {tax_type}:")
        print(f"{'ID':<4} | {'Income Limit':>15} | {'Rate':>8}")
        print("-" * 35)
        for bid, limit, rate in rows:
            limit_txt = "∞" if limit == float("inf") else f"{limit:,.0f}"
            print(f"{bid:<4} | {limit_txt:>15} | {rate*100:>7.2f}%")


def show_db_menu():
    while True:
        print("\n=== DB Menu ===")
        print("1. View last 5 records")
        print("2. View people for a record")
        print("3. View person history across all records")
        print("4. Update record by ID")
        print("5. Update person by ID")
        print("6. Delete record by ID")
        print("7. Delete person by ID")
        print("8. Reset database ⚠️")
        print("9. Reset tax brackets ⚠️")
        print("10. Export CSV template")
        print("11. View tax brackets")
        print("12. Back to main menu")

        choice = input("Choose an option (1-12): ").strip()

        if choice == "1":
            show_last_records(5)
        elif choice == "2":
            show_people_for_record()
        elif choice == "3":
            show_person_history()
        elif choice == "4":
            update_record_menu()
        elif choice == "5":
            update_person_menu()
        elif choice == "6":
            delete_record_menu()
        elif choice == "7":
            delete_person_menu()
        elif choice == "8":
            reset_db_menu()
        elif choice == "9":
            reset_tax_brackets_menu()
        elif choice == "10":
            export_template_menu()
        elif choice == "11":
            view_tax_brackets_menu()
        elif choice == "12":
            break
        else:
            print("❌ Invalid choice. Please enter 1-12.")
