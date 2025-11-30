"""
Migration script to add distribution_method and salary_amount fields to existing database.
Run this once to update your existing database.
"""
import sqlite3
import os


def migrate_database():
    """Add distribution_method and salary_amount columns to tax_records table."""
    db_name = "example.db"

    if not os.path.exists(db_name):
        print(f"❌ Database '{db_name}' not found. No migration needed.")
        return

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(tax_records)")
    columns = [row[1] for row in cursor.fetchall()]

    migrations_run = []

    # Add distribution_method if it doesn't exist
    if "distribution_method" not in columns:
        cursor.execute(
            """
            ALTER TABLE tax_records
            ADD COLUMN distribution_method TEXT DEFAULT 'N/A'
        """
        )
        migrations_run.append("distribution_method")
        print("✅ Added 'distribution_method' column")
    else:
        print("⏭️  'distribution_method' column already exists")

    # Add salary_amount if it doesn't exist
    if "salary_amount" not in columns:
        cursor.execute(
            """
            ALTER TABLE tax_records
            ADD COLUMN salary_amount REAL DEFAULT 0
        """
        )
        migrations_run.append("salary_amount")
        print("✅ Added 'salary_amount' column")
    else:
        print("⏭️  'salary_amount' column already exists")

    # Set default values for existing records based on tax_option
    if migrations_run:
        # Individual tax → distribution_method = 'N/A'
        cursor.execute(
            """
            UPDATE tax_records
            SET distribution_method = 'N/A'
            WHERE tax_option = 'Individual' AND distribution_method IS NULL
        """
        )

        # Business tax → distribution_method = 'Salary' (default assumption)
        cursor.execute(
            """
            UPDATE tax_records
            SET distribution_method = 'Salary'
            WHERE tax_option = 'Business' AND (distribution_method IS NULL OR distribution_method = 'N/A')
        """
        )

        print("✅ Set default distribution methods for existing records")

    conn.commit()
    conn.close()

    if migrations_run:
        print(f"\n🎉 Migration complete! Added {len(migrations_run)} new column(s).")
    else:
        print("\n✅ Database already up to date. No migration needed.")


if __name__ == "__main__":
    print("🔄 Starting database migration...\n")
    migrate_database()
