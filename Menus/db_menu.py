from MoneySplit.DB import setup
from MoneySplit.Logic import validators

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
        id, origin, option, revenue, costs, tax, net_group, net_person, created, num_people, group_income, individual_income = r
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
        record_id = validators.safe_int_input("Enter the ID of the record to update: ", "Record ID", min_value=1)
        record = setup.get_record_by_id(record_id)

        if not record:
            print(f"❌ No record found with ID {record_id}.")
            return

        print("\nYou can update the following fields:")
        for f in sorted(setup.ALLOWED_FIELDS):
            print(f" - {f}")

        field = validators.safe_string_input("\nEnter the field to update: ", "Field name")

        if field not in setup.ALLOWED_FIELDS:
            print(f"❌ '{field}' is not editable. Allowed: {', '.join(sorted(setup.ALLOWED_FIELDS))}")
            return

        if field == "num_people":
            new_value = validators.safe_int_input(f"Enter new value for {field}: ", field, min_value=1)
        elif field in ["revenue", "total_costs"]:
            new_value = validators.safe_float_input(f"Enter new value for {field}: ", field)
        else:
            new_value = validators.safe_string_input(f"Enter new value for {field}: ", field)

        setup.update_record(record_id, field, new_value)

    except validators.ValidationError as e:
        print(f"❌ {e}")


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
        person_id = validators.safe_int_input("Enter the ID of the person to update: ", "Person ID", min_value=1)
        print("\nYou can update the following fields:")
        print(" - name")
        print(" - work_share")

        field = validators.safe_string_input("Enter the field to update: ", "Field name")

        if field == "work_share":
            new_value = validators.safe_float_input(f"Enter new value for {field} (0.0-1.0): ", field)
            new_value = validators.validate_work_share(new_value)
        elif field == "name":
            new_value = validators.safe_string_input(f"Enter new value for {field}: ", field)
        else:
            print(f"❌ Invalid field. Only 'name' and 'work_share' can be updated.")
            return

        setup.update_person(person_id, field, new_value)

    except validators.ValidationError as e:
        print(f"❌ {e}")


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


def deduplicate_people_menu():
    try:
        record_id = int(input("Enter the record ID to deduplicate people: "))
        setup.deduplicate_people(record_id)
    except ValueError:
        print("❌ Invalid input. Please enter a number.")


# --- Maintenance ---
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


# --- Advanced ---
def clone_record_menu():
    try:
        record_id = int(input("Enter the ID of the record to clone: "))
        setup.clone_record(record_id)
    except ValueError:
        print("❌ Invalid input. Please enter a number.")


def copy_people_menu():
    try:
        source_id = int(input("Enter source record ID: "))
        target_id = int(input("Enter target record ID: "))
        setup.copy_people(source_id, target_id)

        # 🔄 Auto-update num_people in target
        people = setup.fetch_people_by_record(target_id)
        new_count = len(people)
        setup.update_record(target_id, "num_people", new_count)

        # 🔄 Run deduplication
        removed = setup.deduplicate_people(target_id)
        print(f"🔄 Target record {target_id} updated. num_people = {new_count}. "
              f"Deduplicated {removed} duplicate(s).")

    except ValueError:
        print("❌ Invalid input. Please enter numbers.")


def advanced_options_menu():
    while True:
        print("\n=== Advanced DB Options ===")
        print("1. Clone a record")
        print("2. Copy people between records")
        print("3. Back")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            clone_record_menu()
        elif choice == "2":
            copy_people_menu()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")


# --- Submenus ---
def search_records_menu():
    print("\n=== Search Filters ===")
    country = input("Country (leave blank to skip): ").strip() or None
    tax_option = input("Tax option (Individual/Business, leave blank to skip): ").strip().title() or None
    start_date = input("Start date (YYYY-MM-DD, leave blank to skip): ").strip() or None
    end_date = input("End date (YYYY-MM-DD, leave blank to skip): ").strip() or None

    rows = setup.search_records(country, tax_option, start_date, end_date)
    if not rows:
        print("❌ No matching records found.")
        return

    print(f"\nFound {len(rows)} matching records:")
    header = (
        f"{'ID':<3} | {'Origin':<6} | {'Option':<10} | "
        f"{'Revenue':>12} | {'Costs':>10} | {'Tax':>10} | "
        f"{'Net Group':>12} | {'Net Person':>12} | {'Created At'}"
    )
    print(header)
    print("-" * len(header))

    for r in rows:
        id, origin, option, revenue, costs, tax, net_group, net_person, created, num_people, group_income, individual_income = r
        print(
            f"{id:<3} | {origin:<6} | {option:<10} | "
            f"{float(revenue):>12,.2f} | {float(costs):>10,.2f} | {float(tax):>10,.2f} | "
            f"{float(net_group):>12,.2f} | {float(net_person):>12,.2f} | {created}"
        )


def merge_records_menu():
    try:
        r1 = int(input("Enter the first record ID: "))
        r2 = int(input("Enter the second record ID: "))
        new_id = setup.merge_records(r1, r2)

        # 🔄 Run deduplication
        removed = setup.deduplicate_people(new_id)
        print(f"🔄 Merged into record {new_id}. Deduplicated {removed} duplicate(s).")

    except ValueError:
        print("❌ Invalid input. Please enter numbers.")

def records_menu():
    while True:
        print("\n=== Records Menu 📑 ===")
        print("1. View last 5 records")
        print("2. Search records")
        print("3. Clone record")
        print("4. Merge records")
        print("5. Update record by ID")
        print("6. Delete record by ID")
        print("7. Advanced options ⚙️")
        print("8. Back")

        choice = input("Choose an option (1-8): ").strip()
        if choice == "1":
            show_last_records(5)
        elif choice == "2":
            search_records_menu()
        elif choice == "3":
            clone_record_menu()
        elif choice == "4":
            merge_records_menu()
        elif choice == "5":
            update_record_menu()
        elif choice == "6":
            delete_record_menu()
        elif choice == "7":
            advanced_options_menu()
        elif choice == "8":
            break
        else:
            print("❌ Invalid choice. Please enter 1-8.")


def people_menu():
    while True:
        print("\n=== People Menu 👥 ===")
        print("1. View people for a record")
        print("2. View person history")
        print("3. Update person by ID")
        print("4. Delete person by ID")
        print("5. Deduplicate people in record 🧹")
        print("6. Back")

        choice = input("Choose an option (1-6): ").strip()
        if choice == "1":
            show_people_for_record()
        elif choice == "2":
            show_person_history()
        elif choice == "3":
            update_person_menu()
        elif choice == "4":
            delete_person_menu()
        elif choice == "5":
            deduplicate_people_menu()
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")


def maintenance_menu():
    while True:
        print("\n=== Maintenance Menu ⚙️ ===")
        print("1. Reset database ⚠️")
        print("2. Reset tax brackets ⚠️")
        print("3. Export CSV template")
        print("4. View tax brackets")
        print("5. Global deduplication 👥")
        print("6. Back")

        choice = input("Choose an option (1-6): ").strip()
        if choice == "1":
            reset_db_menu()
        elif choice == "2":
            reset_tax_brackets_menu()
        elif choice == "3":
            export_template_menu()
        elif choice == "4":
            view_tax_brackets_menu()
        elif choice == "5":
            setup.deduplicate_all_records()
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")



# --- Main ---
def show_db_menu():
    while True:
        print("\n=== DB Menu ===")
        print("1. Records 📑")
        print("2. People 👥")
        print("3. Maintenance ⚙️")
        print("4. Back to main menu")

        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            records_menu()
        elif choice == "2":
            people_menu()
        elif choice == "3":
            maintenance_menu()
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")
