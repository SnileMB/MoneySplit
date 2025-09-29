def show_tax_menu():
    while True:
        print("\n=== Tax Menu ===")
        print("1. Upload tax brackets (coming soon)")
        print("2. Update tax brackets (coming soon)")
        print("3. Delete tax bracket (coming soon)")
        print("4. Back to main menu")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            print("⬆️ Upload tax brackets - not implemented yet")
        elif choice == "2":
            print("✏️ Update tax brackets - not implemented yet")
        elif choice == "3":
            print("🗑️ Delete tax bracket - not implemented yet")
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice.")
