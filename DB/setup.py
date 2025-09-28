import sqlite3
from MoneySplit.Logic import ProgramBackend

def save_to_db():
    tax_origin = "US" if ProgramBackend.tax_origin == 1 else "Spain"
    tax_option = "Individual" if ProgramBackend.tax_option == 1 else "Business"

    if ProgramBackend.tax_option == 1:  # individual
        net_income_per_person = ProgramBackend.individual_income - ProgramBackend.tax
        net_income_group = net_income_per_person * ProgramBackend.num_people
    else:  # business
        net_income_group = ProgramBackend.group_income - ProgramBackend.tax
        net_income_per_person = net_income_group / ProgramBackend.num_people

    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      num_people INTEGER,
      revenue REAL,
      total_costs REAL,
      group_income REAL,
      individual_income REAL,
      tax_origin TEXT,
      tax_option TEXT,
      tax_amount REAL,
      net_income_per_person REAL,
      net_income_group REAL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    INSERT INTO tax_records (
        num_people, revenue, total_costs, group_income, individual_income,
        tax_origin, tax_option, tax_amount,
        net_income_per_person, net_income_group
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ProgramBackend.num_people,
        ProgramBackend.revenue,
        ProgramBackend.total_costs,
        ProgramBackend.group_income,
        ProgramBackend.individual_income,
        tax_origin,
        tax_option,
        ProgramBackend.tax,
        net_income_per_person,
        net_income_group
    ))

    conn.commit()
    conn.close()
    print("✅ Results saved to database.")

def fetch_last_records(n=5):
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tax_origin, tax_option,
               revenue, total_costs,
               tax_amount, net_income_group, net_income_per_person, created_at
        FROM tax_records
        ORDER BY created_at DESC
        LIMIT ?
    """, (n,))
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    save_to_db()
