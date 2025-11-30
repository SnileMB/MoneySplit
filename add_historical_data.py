#!/usr/bin/env python3
"""
Script to add historical data for forecasting testing.
Backdates some existing records to create multi-month history.
"""

import sqlite3
from datetime import datetime, timedelta
import random


def backdate_records():
    """Backdate some records to create historical data."""
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    # Get all records
    cursor.execute("SELECT id FROM tax_records ORDER BY created_at")
    records = cursor.fetchall()

    if len(records) < 6:
        print("❌ Need at least 6 records to create meaningful historical data")
        return

    # Backdate records to create 6 months of history
    # Month 1 (6 months ago): 2 records
    # Month 2 (5 months ago): 2 records
    # Month 3 (4 months ago): 2 records
    # Month 4 (3 months ago): 2 records
    # Month 5 (2 months ago): 2 records
    # Month 6 (1 month ago): 2 records
    # Current month: remaining records

    now = datetime.now()

    month_assignments = [
        (6, 2),  # 6 months ago, 2 records
        (5, 2),  # 5 months ago, 2 records
        (4, 2),  # 4 months ago, 2 records
        (3, 2),  # 3 months ago, 2 records
        (2, 2),  # 2 months ago, 2 records
        (1, 2),  # 1 month ago, 2 records
    ]

    record_idx = 0
    updates = []

    for months_ago, count in month_assignments:
        if record_idx + count > len(records):
            break

        # Calculate target month
        target_date = now - timedelta(days=30 * months_ago)

        for i in range(count):
            if record_idx >= len(records):
                break
            record_id = records[record_idx][0]

            # Random day within that month
            day = random.randint(1, 28)
            backdated = target_date.replace(day=day)

            updates.append((backdated.strftime("%Y-%m-%d %H:%M:%S"), record_id))
            record_idx += 1

    # Apply updates
    for new_date, record_id in updates:
        cursor.execute(
            "UPDATE tax_records SET created_at = ? WHERE id = ?", (new_date, record_id)
        )

    conn.commit()

    # Show results
    cursor.execute(
        """
        SELECT strftime('%Y-%m', created_at) as month,
               COUNT(*) as records,
               SUM(revenue) as total_revenue
        FROM tax_records
        GROUP BY month
        ORDER BY month
    """
    )

    print("\n✅ Historical data created successfully!\n")
    print("Month Distribution:")
    print("-" * 50)
    print(f"{'Month':<15} {'Records':<10} {'Total Revenue':<15}")
    print("-" * 50)

    for row in cursor.fetchall():
        month, count, revenue = row
        print(f"{month:<15} {count:<10} ${revenue:,.2f}")

    print("-" * 50)
    print(
        f"\n✅ You now have data across {cursor.execute('SELECT COUNT(DISTINCT strftime(\"%Y-%m\", created_at)) FROM tax_records').fetchone()[0]} months!"
    )
    print("✅ Revenue forecasting should now work!")

    conn.close()


if __name__ == "__main__":
    print("📊 Adding historical data for forecasting...")
    backdate_records()
