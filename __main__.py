from MoneySplit.Logic import ProgramBackend
from MoneySplit.DB import setup

def main():
    print("=== Running MoneySplit ===")

    setup.save_to_db()
    print("\n✅ Results saved to database.")
    print("\n✅ Calculation finished and stored in database.")

    print("\n=== Last 5 Saved Records ===")
    records = setup.fetch_last_records(5)

    header = f"{'ID':<3} | {'Origin':<6} | {'Option':<10} | {'Revenue':>12} | {'Costs':>10} | {'Tax':>10} | {'Net Group':>12} | {'Net Person':>12} | {'Created At'}"
    print(header)
    print("-" * len(header))

    for r in records:
        id, origin, option, revenue, costs, tax, net_group, net_person, created = r
        print(f"{id:<3} | {origin:<6} | {option:<10} | {float(revenue):>12,.2f} | {float(costs):>10,.2f} | {float(tax):>10,.2f} | {float(net_group):>12,.2f} | {float(net_person):>12,.2f} | {created}")

if __name__ == "__main__":
    main()
