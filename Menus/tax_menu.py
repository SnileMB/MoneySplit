from MoneySplit.DB import setup

def show_tax_menu():
    while True:
        print("\n=== Tax Menu ===")
        print("1. Upload tax brackets")
        print("2. Update tax bracket")
        print("3. Delete tax bracket")
        print("4. View tax brackets")
        print("5. Export CSV template")
        print("6. Reset tax brackets ⚠️")
        print("7. Back to main menu")

        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":  # Upload
            print("\n=== Upload Options ===")
            print("1. Enter manually")
            print("2. Upload from CSV")
            print("3. Back")
            sub = input("Choose an option (1-3): ").strip()

            if sub == "1":  # Manual
                country = input("Enter country (e.g. US, Spain): ").strip()
                tax_type = input("Enter type (Individual/Business): ").strip().title()
                n = int(input("How many brackets to add? "))
                for i in range(n):
                    limit = input(f"Bracket {i+1} income limit (number or 'inf'): ").strip()
                    income_limit = float("inf") if limit.lower() == "inf" else float(limit)
                    rate = float(input(f"Bracket {i+1} rate (e.g. 0.21): "))
                    setup.add_tax_bracket(country, tax_type, income_limit, rate)
                print(f"✅ Added {n} brackets for {country} {tax_type}")

            elif sub == "2":  # CSV
                country = input("Enter country (e.g. US, Spain): ").strip()
                tax_type = input("Enter type (Individual/Business): ").strip().title()
                filepath = input("Enter path to CSV file: ").strip()
                setup.add_tax_brackets_from_csv(country, tax_type, filepath)

            elif sub == "3":
                continue

        elif choice == "2":  # Update
            bracket_id = int(input("Enter bracket ID to update: "))
            field = input("Which field (country, tax_type, income_limit, rate)? ").strip()
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

        elif choice == "5":  # Export CSV template
            filepath = input("Enter filename for template (default: tax_template.csv): ").strip()
            if not filepath:
                filepath = "tax_template.csv"
            setup.export_tax_template(filepath)

        elif choice == "6":  # Reset
            confirm = input("⚠️ This will delete ALL tax brackets and restore defaults. Continue? (y/n): ").strip().lower()
            if confirm == "y":
                setup.reset_tax_brackets()
            else:
                print("❌ Reset canceled.")

        elif choice == "7":  # Back
            break
        else:
            print("❌ Invalid choice. Please enter 1-7.")
