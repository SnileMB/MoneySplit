import sqlite3
import sys

def _pb():
    """Return already-loaded ProgramBackend module without re-importing it."""
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

def get_record_by_id(record_id: int):
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tax_origin, tax_option,
               revenue, total_costs,
               tax_amount, net_income_group, net_income_per_person, created_at
        FROM tax_records
        WHERE id = ?
    """, (record_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_record(record_id: int):
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tax_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Record {record_id} deleted (if it existed).")

def update_record(record_id: int, field: str, new_value):
    """
    Update a record by ID. If revenue/total_costs/num_people changes,
    automatically recalc group_income, individual_income, tax, and net values.
    """
    allowed_fields = {
        "num_people", "revenue", "total_costs",
        "group_income", "individual_income",
        "tax_origin", "tax_option",
        "tax_amount", "net_income_per_person", "net_income_group"
    }

    if field not in allowed_fields:
        raise ValueError(f"Invalid field: {field}. Allowed: {', '.join(allowed_fields)}")

    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    cursor.execute(f"UPDATE tax_records SET {field} = ? WHERE id = ?", (new_value, record_id))

    cursor.execute("""
        SELECT num_people, revenue, total_costs, tax_origin, tax_option
        FROM tax_records WHERE id = ?
    """, (record_id,))
    row = cursor.fetchone()

    if row:
        num_people, revenue, total_costs, origin, option = row
        try:
            revenue = float(revenue)
            total_costs = float(total_costs)
            num_people = int(num_people)
        except Exception:
            conn.commit()
            conn.close()
            return

        income = revenue - total_costs
        group_income = income
        individual_income = income / num_people if num_people > 0 else 0

        from MoneySplit.Logic import ProgramBackend
        if origin == "US":
            if option == "Individual":
                tax = ProgramBackend.us_individual_tax(individual_income)
            else:
                tax = ProgramBackend.us_business_tax(group_income)
        else:  # Spain
            if option == "Individual":
                tax = ProgramBackend.spain_individual_tax(individual_income)
            else:
                tax = ProgramBackend.spain_business_tax(group_income)

        if option == "Individual":
            net_income_per_person = individual_income - tax
            net_income_group = net_income_per_person * num_people
        else:
            net_income_group = group_income - tax
            net_income_per_person = net_income_group / num_people if num_people > 0 else 0

        cursor.execute("""
            UPDATE tax_records
            SET group_income=?, individual_income=?, tax_amount=?, 
                net_income_per_person=?, net_income_group=?
            WHERE id=?
        """, (group_income, individual_income, tax, net_income_per_person, net_income_group, record_id))

    conn.commit()
    conn.close()
    print(f"✏️ Record {record_id} updated and recalculated ({field} → {new_value})")
