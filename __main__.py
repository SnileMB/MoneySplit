from MoneySplit.Menus import project_menu, db_menu, tax_menu

def main():
    while True:
        print("\n=== MoneySplit Main Menu ===")
        print("1. New Project")
        print("2. Play with DB")
        print("3. Tax")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            project_menu.run_new_project()
        elif choice == "2":
            db_menu.show_db_menu()
        elif choice == "3":
            tax_menu.show_tax_menu()
        elif choice == "4":
            print("👋 Exiting MoneySplit. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
