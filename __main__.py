import sys
import importlib

def run_new_calculation():
    # Ensure a fresh single execution each time option 1 is chosen
    importlib.invalidate_caches()
    if "MoneySplit.Logic.ProgramBackend" in sys.modules:
        del sys.modules["MoneySplit.Logic.ProgramBackend"]

    # This import executes ProgramBackend.py ONCE (prompts the user)
    importlib.import_module("MoneySplit.Logic.ProgramBackend")

    # Now save results without re-importing ProgramBackend
    from MoneySplit.DB import setup
    setup.save_to_db()
    print("\n✅ Results saved to database.")
    print("✅ Calculation finished and stored in database.")

def show_last_records(n=5):
    from MoneySplit.DB import setup
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

def main():
    while True:
        print("\n=== MoneySplit Menu ===")
        print("1. New Tax Calculation")
        print("2. View Last 5 Records")
        print("3. Exit")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            run_new_calculation()
        elif choice == "2":
            show_last_records(5)
        elif choice == "3":
            print("👋 Exiting MoneySplit. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
