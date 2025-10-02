from MoneySplit.Menus import project_menu, db_menu, tax_menu, report_menu
from MoneySplit.DB import reset as db_reset
from MoneySplit.DB import setup

# Init DB + defaults
setup.init_db()
setup.seed_default_brackets()

def main():
    while True:
        print("\n=== MoneySplit Main Menu ===")
        print("1. New Project 📲")
        print("2. Play with DB 📊")
        print("3. Tax 📝")
        print("4. Reports 📊")
        print("5. DB Maintenance ⚙️")
        print("6. Exit 🚪")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            project_menu.run_new_project()
        elif choice == "2":
            db_menu.show_db_menu()
        elif choice == "3":
            tax_menu.show_tax_menu()
        elif choice == "4":
            report_menu.show_report_menu()
        elif choice == "5":
            db_reset.main()  # run the maintenance tool
        elif choice == "6":
            print("👋 Exiting MoneySplit. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
