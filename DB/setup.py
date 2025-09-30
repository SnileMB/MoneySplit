import sqlite3
import sys
import csv
from datetime import datetime

# Editable fields at project level
ALLOWED_FIELDS = {
    "num_people", "revenue", "total_costs",
    "tax_origin", "tax_option"
    # other fields are derived → recalculated automatically
}


def _pb():
    """Return already-loaded ProgramBackend module without re-importing it."""
    m = sys.modules.get("MoneySplit.Logic.ProgramBackend")
    if m is None:
        raise RuntimeError("ProgramBackend not loaded; run a calculation first (option 1).")
    return m


def get_conn():
    """Get a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect("example.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initialize both tax_records and people tables if they don’t exist."""
    conn = get_conn()
    cursor = conn.cursor()

    # Main project-level table
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

    # People-level table (cascade delete enabled)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          record_id INTEGER,
          name TEXT NOT NULL,
          work_share REAL,
          gross_income REAL,
          tax_paid REAL,
          net_income REAL,
          FOREIGN KEY (record_id) REFERENCES tax_records(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------------
# CRUD for tax_records
# -----------------------------

def save_to_db():
    """Save the current ProgramBackend calculation to tax_records."""
    pb = _pb()

    tax_origin = "US" if pb.tax_origin == 1 else "Spain"
    tax_option = "Individual" if pb.tax_option == 1 else "Business"

    if pb.tax_option == 1:  # individual
        net_income_per_person = pb.individual_income - pb.tax
        net_income_group = net_income_per_person * pb.num_people
    else:  # business
        net_income_group = pb.group_income - pb.tax
        net_income_per_person = net_income_group / pb.num_people

    conn = get_conn()
    cursor = conn.cursor()

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

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return record_id


def fetch_last_records(n=5):
    conn = get_conn()
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
    conn = get_conn()
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
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tax_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Record {record_id} and linked people deleted.")


def update_record(record_id: int, field: str, new_value):
    """Update a record by ID. Only base fields can be edited; derived fields recalculated."""
    if field not in ALLOWED_FIELDS:
        raise ValueError(
            f"Invalid field: {field}. Allowed fields: {', '.join(sorted(ALLOWED_FIELDS))}"
        )

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"UPDATE tax_records SET {field} = ? WHERE id = ?", (new_value, record_id))

    cursor.execute("""
        SELECT num_people, revenue, total_costs, tax_origin, tax_option
        FROM tax_records WHERE id = ?
    """, (record_id,))
    row = cursor.fetchone()

    if row:
        num_people, revenue, total_costs, origin, option = row
        revenue, total_costs, num_people = float(revenue), float(total_costs), int(num_people)
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


# -----------------------------
# CRUD for people
# -----------------------------

def add_person(record_id: int, name: str, work_share: float,
               gross_income: float, tax_paid: float, net_income: float):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (record_id, name, work_share, gross_income, tax_paid, net_income))
    conn.commit()
    conn.close()
    print(f"👤 Added person {name} to record {record_id}.")


def fetch_people_by_record(record_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, work_share, gross_income, tax_paid, net_income
        FROM people
        WHERE record_id = ?
    """, (record_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_person(person_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM people WHERE id=?", (person_id,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ No person found with ID {person_id}.")
        conn.close()
        return
    name = row[0]
    cursor.execute("DELETE FROM people WHERE id=?", (person_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Deleted person {person_id} ({name}).")


def fetch_records_by_person(name: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.record_id, p.name, p.work_share, 
               p.gross_income, p.tax_paid, p.net_income, t.created_at
        FROM people p
        JOIN tax_records t ON p.record_id = t.id
        WHERE LOWER(p.name) = LOWER(?)
        ORDER BY t.created_at DESC
    """, (name,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_person(person_id: int, field: str, new_value):
    allowed_fields = {"name", "work_share"}
    if field not in allowed_fields:
        raise ValueError(f"Invalid field: {field}. Allowed: {', '.join(allowed_fields)}")

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT record_id FROM people WHERE id = ?", (person_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        print(f"❌ Person {person_id} not found.")
        return
    record_id = row[0]

    if field == "name":
        cursor.execute("UPDATE people SET name=? WHERE id=?", (new_value, person_id))
        conn.commit()
        conn.close()
        print(f"✏️ Person {person_id} name updated → {new_value}")
        return

    if field == "work_share":
        new_value = float(new_value)
        cursor.execute("UPDATE people SET work_share=? WHERE id=?", (new_value, person_id))

        cursor.execute("""
            SELECT num_people, revenue, total_costs, tax_origin, tax_option
            FROM tax_records WHERE id = ?
        """, (record_id,))
        record = cursor.fetchone()
        if not record:
            conn.commit()
            conn.close()
            return

        num_people, revenue, total_costs, origin, option = record
        revenue, total_costs, num_people = float(revenue), float(total_costs), int(num_people)
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

        # Recalculate all people (fixed indent)
        cursor.execute("SELECT id, work_share FROM people WHERE record_id=?", (record_id,))
        people = cursor.fetchall()

        total_work_share = 0.0
        for pid, ws in people:
            total_work_share += ws
            if option == "Individual":
                gross = individual_income * ws * num_people
                tax_paid = tax * ws
                net = gross - tax_paid
            else:
                gross = group_income * ws
                tax_paid = tax * ws
                net = gross - tax_paid

            cursor.execute("""
                UPDATE people
                SET gross_income=?, tax_paid=?, net_income=?
                WHERE id=?
            """, (gross, tax_paid, net, pid))

        conn.commit()
        conn.close()
        print(f"✏️ Person {person_id} work_share updated → {new_value}, all people recalculated")
        if abs(total_work_share - 1.0) > 0.01:
            print(f"⚠️ Warning: total work share = {total_work_share:.2f}, not 1.0")
        else:
            print("✅ Work shares add up to 1.0")

def reset_db():
    """⚠️ Drop and recreate all tables. Use for testing only."""
    choice = input("Do you want to create a backup before reset? (y/n): ").strip().lower()
    if choice == "y":
        backup_db_to_csv()

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS people")
    cursor.execute("DROP TABLE IF EXISTS tax_records")

    conn.commit()
    conn.close()

    print("🗑️ All tables dropped. Reinitializing...")
    init_db()
    print("✅ Database reset complete.")


def backup_db_to_csv():
    """Backup tax_records and people tables into CSV files."""
    conn = get_conn()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Backup tax_records
    cursor.execute("SELECT * FROM tax_records")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]

    with open(f"backup_tax_records_{timestamp}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    # Backup people
    cursor.execute("SELECT * FROM people")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]

    with open(f"backup_people_{timestamp}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()
    print(f"📦 Backup complete → backup_tax_records_{timestamp}.csv, backup_people_{timestamp}.csv")