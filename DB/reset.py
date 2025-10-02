"""
Maintenance tool for MoneySplit DB.
- Backup DB tables to CSV
- Reset DB with optional backup
- Restore DB from CSV backup
"""

from MoneySplit.DB import setup
import csv
import os
from datetime import datetime

BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup():
    """Backup tax_records and people to timestamped CSVs."""
    conn = setup.get_conn()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Backup tax_records
    cursor.execute("SELECT * FROM tax_records")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    tax_file = os.path.join(BACKUP_DIR, f"tax_records_{timestamp}.csv")
    with open(tax_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    # Backup people
    cursor.execute("SELECT * FROM people")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    people_file = os.path.join(BACKUP_DIR, f"people_{timestamp}.csv")
    with open(people_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()
    print(f"📦 Backup complete → {tax_file}, {people_file}")


def reset():
    """Reset DB after optional backup."""
    confirm = input("⚠️ This will DELETE ALL DATA. Type 'RESET' to confirm: ").strip()
    if confirm != "RESET":
        print("❌ Reset canceled.")
        return

    choice = input("Do you want to create a backup before reset? (y/n): ").strip().lower()
    if choice == "y":
        backup()

    setup.reset_db()


def restore():
    """Restore DB from CSV backups in /backups/"""
    tax_file = input("Enter path to tax_records CSV: ").strip()
    people_file = input("Enter path to people CSV: ").strip()

    if not os.path.exists(tax_file) or not os.path.exists(people_file):
        print("❌ One or both CSV files not found.")
        return

    setup.reset_db()  # start fresh

    conn = setup.get_conn()
    cursor = conn.cursor()

    # Restore tax_records
    with open(tax_file, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)  # skip header
        for row in reader:
            cursor.execute(f"""
                INSERT INTO tax_records ({','.join(headers)})
                VALUES ({','.join(['?']*len(headers))})
            """, row)

    # Restore people
    with open(people_file, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            cursor.execute(f"""
                INSERT INTO people ({','.join(headers)})
                VALUES ({','.join(['?']*len(headers))})
            """, row)

    conn.commit()
    conn.close()
    print("✅ Database restored from CSV.")


def main():
    while True:
        print("\n=== DB Maintenance Tool ===")
        print("1. Backup database to CSV")
        print("2. Reset database ⚠️")
        print("3. Restore database from CSV")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            backup()
        elif choice == "2":
            reset()
        elif choice == "3":
            restore()
        elif choice == "4":
            print("👋 Exiting DB maintenance tool.")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
