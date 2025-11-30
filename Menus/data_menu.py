from MoneySplit.DB import setup


def data_menu():
    while True:
        print("\n=== Data Menu 💾 ===")
        print("1. Export data to CSV")
        print("2. Export data to JSON")
        print("3. Import data from CSV")
        print("4. Import data from JSON")
        print("5. Back")

        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            filepath = (
                input("Enter base filename (default: export): ").strip() or "export"
            )
            setup.export_to_csv(filepath)
        elif choice == "2":
            filepath = (
                input("Enter filename (default: export.json): ").strip()
                or "export.json"
            )
            setup.export_to_json(filepath)
        elif choice == "3":
            rec_file = (
                input(
                    "Enter records CSV filename (default: export_records.csv): "
                ).strip()
                or "export_records.csv"
            )
            ppl_file = (
                input(
                    "Enter people CSV filename (default: export_people.csv): "
                ).strip()
                or "export_people.csv"
            )
            setup.import_from_csv(rec_file, ppl_file)
        elif choice == "4":
            filepath = (
                input("Enter JSON filename (default: export.json): ").strip()
                or "export.json"
            )
            setup.import_from_json(filepath)
        elif choice == "5":
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")
