"""
Maintenance script for MoneySplit.
Allows resetting the database with optional backup.
"""

from MoneySplit.DB import setup

def main():
    confirm = input("⚠️ This will DELETE ALL DATA. Type 'RESET' to confirm: ").strip()
    if confirm == "RESET":
        setup.reset_db()
    else:
        print("❌ Reset canceled.")

if __name__ == "__main__":
    main()
