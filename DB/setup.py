import sys
import sqlite3

def _pb():
    """
    Return the already-loaded ProgramBackend module without importing it again.
    If it isn't loaded, the user hasn't run a calculation yet.
    """
    m = sys.modules.get("MoneySplit.Logic.ProgramBackend")
    if m is None:
        raise RuntimeError("ProgramBackend not loaded; run a calculation first (option 1).")
    return m

def save_to_db():
    pb = _pb()

    tax_origin = "US" if pb.tax_origin == 1 else "Spain"
    tax_option = "Individual" if pb.tax_option == 1 else "Business"

    if pb.tax_option == 1:  # individual
        net_income_per_person = pb.individual_income - pb.tax
        net_income_group = net_income_per_person * pb.num_people
    else:  # business
        net_income_group = pb.group_income - pb.tax
        net_income_per_person = net_income_group / pb.num_people

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
        pb.num_people,
        pb.revenue,
        pb.total_costs,
        pb.group_income,
        pb.individual_income,
        tax_origin,
        tax_option,
        pb.tax,
        net_income_per_person,
        net_income_group
    ))

    conn.commit()
    conn.close()

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
