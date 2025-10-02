"""
Maintenance tool for MoneySplit DB.
- Backup DB tables to CSV
- Reset DB with optional backup
- Restore DB from CSV backup
- Reset only tax brackets
- Export tax bracket CSV template
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


def reset_tax_brackets():
    """Reset only the tax_brackets table, with auto-backup."""
    confirm = input("⚠️ This will DELETE ALL TAX BRACKETS. Type 'RESET' to confirm: ").strip()
    if confirm != "RESET":
        print("❌ Reset canceled.")
        return

    conn = setup.get_conn()
    cursor = conn.cursor()

    # Backup current brackets before deleting
    cursor.execute("SELECT * FROM tax_brackets")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]

    if rows:  # Only back up if something exists
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"tax_brackets_{timestamp}.csv")
        with open(backup_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"📦 Tax brackets backed up → {backup_file}")
    else:
        print("ℹ️ No existing tax brackets found to back up.")

    # Delete and reseed defaults
    cursor.execute("DELETE FROM tax_brackets")
    conn.commit()
    conn.close()

    setup.seed_default_brackets()
    print("✅ Tax brackets reset and reseeded with defaults.")

def restore_tax_brackets():
    """Restore tax brackets from a CSV backup."""
    filepath = input("Enter path to tax_brackets CSV backup: ").strip()

    if not os.path.exists(filepath):
        print("❌ File not found.")
        return

    conn = setup.get_conn()
    cursor = conn.cursor()

    # Reset table before restoring
    cursor.execute("DELETE FROM tax_brackets")

    with open(filepath, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)  # skip header
        for row in reader:
            cursor.execute(f"""
                INSERT INTO tax_brackets ({','.join(headers)})
                VALUES ({','.join(['?']*len(headers))})
            """, row)

    conn.commit()
    conn.close()
    print(f"✅ Tax brackets restored from {filepath}")


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


def export_tax_template():
    """Export a blank tax bracket CSV template into backups/ folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    template_file = os.path.join(BACKUP_DIR, f"tax_bracket_template_{timestamp}.csv")

    headers = ["income_limit", "rate"]

    with open(template_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        # add one example row so user sees format
        writer.writerow([10000, 0.10])
        writer.writerow([40000, 0.20])
        writer.writerow([float("inf"), 0.30])

    print(f"📄 Tax bracket template exported → {template_file}")
    print("💡 Edit this CSV and then upload it back through the Tax Menu (Upload from CSV).")

def main():
    while True:
        print("\n=== DB Maintenance Tool ===")
        print("1. Backup database to CSV")
        print("2. Reset database ⚠️")
        print("3. Restore database from CSV")
        print("4. Reset tax brackets ⚠️")
        print("5. Restore tax brackets from backup")
        print("6. Export tax bracket CSV template")
        print("7. Back to main menu")

        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            backup()
        elif choice == "2":
            reset()
        elif choice == "3":
            restore()
        elif choice == "4":
            reset_tax_brackets()
        elif choice == "5":
            restore_tax_brackets()
        elif choice == "6":
            export_tax_template()
        elif choice == "7":
            print("👋 Returning to main menu.")
            break
        else:
            print("❌ Invalid choice. Please enter 1-7.")
