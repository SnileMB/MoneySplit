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

def delete_record_menu():
    try:
        record_id = int(input("Enter the ID of the record to delete: "))
        record = setup.get_record_by_id(record_id)

        if not record:
            print(f"❌ No record found with ID {record_id}.")
            return

        # Show the record details before deleting
        id, origin, option, revenue, costs, tax, net_group, net_person, created = record
        print("\nRecord details:")
        print(f"ID: {id}, Origin: {origin}, Option: {option}, "
              f"Revenue: {float(revenue):,.2f}, Costs: {float(costs):,.2f}, "
              f"Tax: {float(tax):,.2f}, Net Group: {float(net_group):,.2f}, "
              f"Net Person: {float(net_person):,.2f}, Created At: {created}")

        confirm = input("Are you sure you want to delete this record? (y/n): ").strip().lower()
        if confirm == "y":
            setup.delete_record(record_id)
        else:
            print("❌ Deletion canceled.")

    except ValueError:
        print("❌ Invalid ID. Please enter a number.")

def show_db_menu():
    while True:
        print("\n=== DB Menu ===")
        print("1. View last 5 records")
        print("2. Update record by ID")
        print("3. Delete record by ID")
        print("4. Back to main menu")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            show_last_records(5)
        elif choice == "2":
            update_record_menu()
        elif choice == "3":
            delete_record_menu()
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")


def update_record_menu():
    try:
        record_id = int(input("Enter the ID of the record to update: "))
        record = setup.get_record_by_id(record_id)

        if not record:
            print(f"❌ No record found with ID {record_id}.")
            return

        # Show current record
        id, origin, option, revenue, costs, tax, net_group, net_person, created = record
        print("\nCurrent record details:")
        print(f"ID: {id}, Origin: {origin}, Option: {option}, "
              f"Revenue: {float(revenue):,.2f}, Costs: {float(costs):,.2f}, "
              f"Tax: {float(tax):,.2f}, Net Group: {float(net_group):,.2f}, "
              f"Net Person: {float(net_person):,.2f}, Created At: {created}")

        # Ask what to update
        field = input("Enter the field to update (e.g. revenue, total_costs, tax_amount): ").strip()
        new_value = input(f"Enter new value for {field}: ").strip()

        # Try to cast numeric fields to float/int automatically
        if field in ["num_people"]:
            new_value = int(new_value)
        elif field not in ["tax_origin", "tax_option"]:  # these stay as text
            try:
                new_value = float(new_value)
            except ValueError:
                pass  # keep as text if conversion fails

        setup.update_record(record_id, field, new_value)

    except ValueError:
        print("❌ Invalid input. Please enter a number where required.")
