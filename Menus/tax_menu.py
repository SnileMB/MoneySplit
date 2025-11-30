from MoneySplit.DB import setup
from MoneySplit.Logic import validators


def manage_brackets_menu():
    while True:
        print("\n=== Manage Tax Brackets 📊 ===")
        print("1. Upload tax brackets")
        print("2. Update tax bracket")
        print("3. Delete tax bracket")
        print("4. View tax brackets")
        print("5. Back")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":  # Upload
            print("\n=== Upload Options ===")
            print("1. Enter manually")
            print("2. Upload from CSV")
            print("3. Back")
            sub = input("Choose an option (1-3): ").strip()

            if sub == "1":  # Manual entry
                try:
                    country = validators.validate_country(
                        input("Enter country (US/Spain): ").strip()
                    )
                    tax_type = validators.validate_tax_type(
                        input("Enter type (Individual/Business): ").strip()
                    )
                    n = validators.safe_int_input(
                        "How many brackets to add? ", "Number of brackets", min_value=1
                    )
                    for i in range(n):
                        limit = input(
                            f"Bracket {i+1} income limit (number or 'inf'): "
                        ).strip()
                        income_limit = (
                            float("inf")
                            if limit.lower() == "inf"
                            else validators.safe_float_input(
                                f"Re-enter bracket {i+1} income limit: ", "Income limit"
                            )
                        )
                        rate = validators.safe_float_input(
                            f"Bracket {i+1} rate (0.0-1.0, e.g. 0.21): ", "Tax rate"
                        )
                        rate = validators.validate_tax_rate(rate)
                        setup.add_tax_bracket(country, tax_type, income_limit, rate)
                    print(f"✅ Added {n} brackets for {country} {tax_type}")
                except validators.ValidationError as e:
                    print(f"❌ {e}")

            elif sub == "2":  # CSV
                try:
                    country = validators.validate_country(
                        input("Enter country (US/Spain): ").strip()
                    )
                    tax_type = validators.validate_tax_type(
                        input("Enter type (Individual/Business): ").strip()
                    )
                    filepath = validators.safe_string_input(
                        "Enter path to CSV file: ", "File path"
                    )
                    setup.add_tax_brackets_from_csv(country, tax_type, filepath)
                except validators.ValidationError as e:
                    print(f"❌ {e}")

            elif sub == "3":
                continue

        elif choice == "2":  # Update
            bracket_id = int(input("Enter bracket ID to update: "))
            field = input(
                "Which field (country, tax_type, income_limit, rate)? "
            ).strip()
            new_value = input("Enter new value: ").strip()
            if field in ("income_limit", "rate") and new_value.lower() != "inf":
                new_value = float(new_value)
            elif new_value.lower() == "inf":
                new_value = float("inf")
            setup.update_tax_bracket(bracket_id, field, new_value)

        elif choice == "3":  # Delete
            bracket_id = int(input("Enter bracket ID to delete: "))
            setup.delete_tax_bracket(bracket_id)

        elif choice == "4":  # View
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

        elif choice == "5":  # Back
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


def maintenance_menu():
    while True:
        print("\n=== Tax Maintenance ⚙️ ===")
        print("1. Reset tax brackets ⚠️")
        print("2. Export CSV template")
        print("3. Back")

        choice = input("Choose an option (1-3): ").strip()
        if choice == "1":
            setup.reset_tax_brackets()
        elif choice == "2":
            setup.export_tax_template()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")


def show_tax_menu():
    while True:
        print("\n=== Tax Menu ===")
        print("1. Manage Brackets 📊")
        print("2. Maintenance ⚙️")
        print("3. Back to main menu")

        choice = input("Choose an option (1-3): ").strip()
        if choice == "1":
            manage_brackets_menu()
        elif choice == "2":
            maintenance_menu()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")
