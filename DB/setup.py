import json
import sqlite3
import sys
import csv
import os
from datetime import datetime

# Editable fields at project level
ALLOWED_FIELDS = {
    "num_people", "revenue", "total_costs",
    "tax_origin", "tax_option"
    # other fields are derived → recalculated automatically
}

# -----------------------------
# Init
# -----------------------------

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
    """Initialize tax_records, people, and tax_brackets tables."""
    conn = get_conn()
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tax_brackets (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          country TEXT NOT NULL,
          tax_type TEXT NOT NULL,
          income_limit REAL NOT NULL,
          rate REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def seed_default_brackets():
    """Insert default US & Spain brackets if table is empty."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tax_brackets")
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        return

    defaults = [
        # US Individual
        ("US", "Individual", 10275, 0.10),
        ("US", "Individual", 41775, 0.12),
        ("US", "Individual", 89075, 0.22),
        ("US", "Individual", 170050, 0.24),
        ("US", "Individual", 215950, 0.32),
        ("US", "Individual", 539900, 0.35),
        ("US", "Individual", float("inf"), 0.37),
        # US Business
        ("US", "Business", float("inf"), 0.21),
        # Spain Individual
        ("Spain", "Individual", 12450, 0.19),
        ("Spain", "Individual", 20200, 0.24),
        ("Spain", "Individual", 35200, 0.30),
        ("Spain", "Individual", 60000, 0.37),
        ("Spain", "Individual", 300000, 0.45),
        ("Spain", "Individual", float("inf"), 0.47),
        # Spain Business
        ("Spain", "Business", float("inf"), 0.25),
    ]

    cursor.executemany("""
        INSERT INTO tax_brackets (country, tax_type, income_limit, rate)
        VALUES (?, ?, ?, ?)
    """, defaults)

    conn.commit()
    conn.close()


init_db()
seed_default_brackets()

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
               tax_amount, net_income_group, net_income_per_person, created_at,
               num_people, group_income, individual_income
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
               tax_amount, net_income_group, net_income_per_person, created_at,
               num_people, group_income, individual_income
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
        raise ValueError(f"Invalid field: {field}. Allowed: {', '.join(sorted(ALLOWED_FIELDS))}")

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE tax_records SET {field} = ? WHERE id = ?", (new_value, record_id))

    # fetch values for recalculation
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

        # Calculate tax using DB-driven tax brackets
        if option == "Individual":
            tax = calculate_tax_from_db(individual_income, origin, option)
        else:
            tax = calculate_tax_from_db(group_income, origin, option)

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
    person_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"👤 Added person {name} (ID: {person_id}) to record {record_id}.")
    return person_id


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

# -----------------------------
# DB Maintenance
# -----------------------------

def reset_db():
    """⚠️ Drop and recreate all tables. Use for testing only."""
    choice = input("Do you want to create a backup before reset? (y/n): ").strip().lower()
    if choice == "y":
        backup_db_to_csv()

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS people")
    cursor.execute("DROP TABLE IF EXISTS tax_records")
    cursor.execute("DROP TABLE IF EXISTS tax_brackets")

    conn.commit()
    conn.close()

    print("🗑️ All tables dropped. Reinitializing...")
    init_db()
    seed_default_brackets()
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


# -----------------------------
# Tax brackets management
# -----------------------------

def calculate_tax_from_db(income: float, country: str, tax_type: str) -> float:
    """Generic tax calculator that fetches brackets from DB."""
    brackets = get_tax_brackets(country, tax_type)
    if not brackets:
        raise ValueError(f"No tax brackets found for {country} {tax_type}")

    tax = 0
    prev = 0
    for limit, rate in brackets:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break
    return tax


def get_tax_brackets(country: str, tax_type: str, include_id: bool = False):
    conn = get_conn()
    cursor = conn.cursor()
    if include_id:
        cursor.execute("""
            SELECT id, income_limit, rate
            FROM tax_brackets
            WHERE country=? AND tax_type=?
            ORDER BY income_limit ASC
        """, (country, tax_type))
    else:
        cursor.execute("""
            SELECT income_limit, rate
            FROM tax_brackets
            WHERE country=? AND tax_type=?
            ORDER BY income_limit ASC
        """, (country, tax_type))
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_tax_brackets_from_csv(country: str, tax_type: str, filepath: str):
    """Upload multiple tax brackets from a CSV file with columns: income_limit, rate"""
    if not os.path.exists(filepath):
        print("❌ File not found.")
        return

    conn = get_conn()
    cursor = conn.cursor()
    added, skipped = 0, 0

    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        if "income_limit" not in reader.fieldnames or "rate" not in reader.fieldnames:
            print("❌ CSV must contain 'income_limit' and 'rate'.")
            conn.close()
            return

        for row in reader:
            try:
                limit_raw = row.get("income_limit", "").strip()
                rate_raw = row.get("rate", "").strip()

                if not limit_raw or not rate_raw:
                    skipped += 1
                    continue

                income_limit = float("inf") if limit_raw.lower() == "inf" else float(limit_raw)
                rate = float(rate_raw)

                cursor.execute("""
                    INSERT INTO tax_brackets (country, tax_type, income_limit, rate)
                    VALUES (?, ?, ?, ?)
                """, (country, tax_type, income_limit, rate))
                added += 1
            except Exception as e:
                print(f"⚠️ Skipping row {row}: {e}")
                skipped += 1

    conn.commit()
    conn.close()
    print(f"✅ Imported {added} brackets for {country} {tax_type} ({skipped} skipped).")


def update_tax_bracket(bracket_id: int, field: str, new_value):
    allowed = {"country", "tax_type", "income_limit", "rate"}
    if field not in allowed:
        raise ValueError(f"Invalid field. Allowed: {', '.join(allowed)}")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE tax_brackets SET {field}=? WHERE id=?", (new_value, bracket_id))
    conn.commit()
    conn.close()
    print(f"✏️ Bracket {bracket_id} updated: {field} → {new_value}")


def delete_tax_bracket(bracket_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tax_brackets WHERE id=?", (bracket_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Deleted tax bracket {bracket_id}")


def reset_tax_brackets():
    """Delete all brackets and re-seed defaults (US + Spain)."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tax_brackets")
    conn.commit()
    conn.close()
    print("🗑️ All tax brackets deleted.")
    seed_default_brackets()
    print("✅ Default tax brackets restored.")


def export_tax_template(filepath="tax_template.csv"):
    """Export a clean CSV template for tax brackets."""
    headers = ["income_limit", "rate"]
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(["12450", "0.19"])   # Example row
        writer.writerow(["20200", "0.24"])
        writer.writerow(["inf", "0.45"])
    print(f"📄 Template exported to {filepath}")


# -----------------------------
# Advanced operations
# -----------------------------

def clone_record(record_id: int):
    """Clone a record and its people into a new record with a new timestamp."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT num_people, revenue, total_costs, group_income, individual_income,
               tax_origin, tax_option, tax_amount, net_income_per_person, net_income_group
        FROM tax_records WHERE id = ?
    """, (record_id,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ Record {record_id} not found.")
        conn.close()
        return None

    cursor.execute("""
        INSERT INTO tax_records (
            num_people, revenue, total_costs, group_income, individual_income,
            tax_origin, tax_option, tax_amount,
            net_income_per_person, net_income_group
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, row)
    new_record_id = cursor.lastrowid

    cursor.execute("SELECT name, work_share, gross_income, tax_paid, net_income FROM people WHERE record_id=?", (record_id,))
    people = cursor.fetchall()
    for person in people:
        cursor.execute("""
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (new_record_id, *person))

    conn.commit()
    conn.close()
    print(f"✅ Record {record_id} cloned → New record {new_record_id}")
    return new_record_id


def copy_people(source_id: int, target_id: int):
    """Copy people from one record into another, then deduplicate."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT name, work_share, gross_income, tax_paid, net_income FROM people WHERE record_id=?", (source_id,))
    people = cursor.fetchall()
    if not people:
        print(f"❌ No people found in record {source_id}.")
        conn.close()
        return

    for person in people:
        cursor.execute("""
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (target_id, *person))

    conn.commit()
    conn.close()
    removed = deduplicate_people(target_id)
    print(f"✅ {len(people)} people copied. {removed} duplicates removed from target {target_id}.")


def merge_records(r1: int, r2: int):
    """Merge two records into a new one with combined data + deduplicated people."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tax_records WHERE id=?", (r1,))
    rec1 = cursor.fetchone()
    cursor.execute("SELECT * FROM tax_records WHERE id=?", (r2,))
    rec2 = cursor.fetchone()
    if not rec1 or not rec2:
        print("❌ One or both records not found.")
        conn.close()
        return

    revenue = float(rec1[2]) + float(rec2[2])
    costs = float(rec1[3]) + float(rec2[3])
    num_people = int(rec1[1]) + int(rec2[1])
    income = revenue - costs
    group_income = income
    individual_income = income / num_people if num_people > 0 else 0

    origin, option = rec1[6], rec1[7]

    # Calculate tax using DB-driven tax brackets
    if option == "Individual":
        tax = calculate_tax_from_db(individual_income, origin, option)
    else:
        tax = calculate_tax_from_db(group_income, origin, option)

    if option == "Individual":
        net_income_per_person = individual_income - tax
        net_income_group = net_income_per_person * num_people
    else:
        net_income_group = group_income - tax
        net_income_per_person = net_income_group / num_people if num_people > 0 else 0

    cursor.execute("""
        INSERT INTO tax_records (
            num_people, revenue, total_costs, group_income, individual_income,
            tax_origin, tax_option, tax_amount, net_income_per_person, net_income_group
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        num_people, revenue, costs, group_income, individual_income,
        origin, option, tax, net_income_per_person, net_income_group
    ))
    new_id = cursor.lastrowid

    cursor.execute("SELECT name, work_share, gross_income, tax_paid, net_income FROM people WHERE record_id=?", (r1,))
    people1 = cursor.fetchall()
    cursor.execute("SELECT name, work_share, gross_income, tax_paid, net_income FROM people WHERE record_id=?", (r2,))
    people2 = cursor.fetchall()

    for name, ws, gross, taxp, net in people1 + people2:
        cursor.execute("""
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (new_id, name, ws, gross, taxp, net))

    conn.commit()
    conn.close()
    removed = deduplicate_people(new_id)
    print(f"✅ Records {r1} and {r2} merged → New record {new_id}. {removed} duplicates removed.")


def search_records(country=None, tax_option=None, start_date=None, end_date=None):
    """Search tax_records with optional filters."""
    conn = get_conn()
    cursor = conn.cursor()

    def _norm_date(s: str, is_end: bool) -> str:
        s = s.strip()
        return f"{s} 23:59:59" if (len(s) == 10 and is_end) else f"{s} 00:00:00" if len(s) == 10 else s

    query = """
        SELECT id, tax_origin, tax_option,
               revenue, total_costs,
               tax_amount, net_income_group, net_income_per_person, created_at
        FROM tax_records
        WHERE 1=1
    """
    params = []
    if country:
        query += " AND UPPER(tax_origin) = UPPER(?)"
        params.append(country)
    if tax_option:
        query += " AND UPPER(tax_option) = UPPER(?)"
        params.append(tax_option)
    if start_date:
        query += " AND datetime(created_at) >= datetime(?)"
        params.append(_norm_date(start_date, False))
    if end_date:
        query += " AND datetime(created_at) <= datetime(?)"
        params.append(_norm_date(end_date, True))

    query += " ORDER BY datetime(created_at) DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# -----------------------------
# Deduplication
# -----------------------------

def deduplicate_people(record_id: int) -> int:
    """Merge duplicate people in one record. Normalize work shares. Return # removed."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, work_share, gross_income, tax_paid, net_income
        FROM people WHERE record_id=?
    """, (record_id,))
    people = cursor.fetchall()
    if not people:
        conn.close()
        return 0

    merged, ids_to_delete = {}, []
    for pid, name, ws, gross, taxp, net in people:
        if name not in merged:
            merged[name] = [ws, gross, taxp, net, pid]
        else:
            merged[name][0] += ws
            merged[name][1] += gross
            merged[name][2] += taxp
            merged[name][3] += net
            ids_to_delete.append(pid)

    for name, (ws, gross, taxp, net, pid) in merged.items():
        cursor.execute("""
            UPDATE people
            SET work_share=?, gross_income=?, tax_paid=?, net_income=?
            WHERE id=?
        """, (ws, gross, taxp, net, pid))

    removed = 0
    if ids_to_delete:
        cursor.executemany("DELETE FROM people WHERE id=?", [(i,) for i in ids_to_delete])
        removed = len(ids_to_delete)

    cursor.execute("SELECT COUNT(*) FROM people WHERE record_id=?", (record_id,))
    count = cursor.fetchone()[0]
    cursor.execute("UPDATE tax_records SET num_people=? WHERE id=?", (count, record_id))

    conn.commit()
    conn.close()
    return removed


def deduplicate_all_records():
    """Run deduplication on all records in the DB and show summary."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tax_records")
    record_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    total_removed = 0
    for rid in record_ids:
        removed = deduplicate_people(rid)
        total_removed += removed

    print(f"\n✅ Global deduplication complete. "
          f"{len(record_ids)} records scanned, {total_removed} duplicates removed.")


# -----------------------------
# Data Import / Export
# -----------------------------

def export_to_csv(basepath="export"):
    """Export tax_records and people into two CSV files."""
    conn = get_conn()
    cursor = conn.cursor()

    # Export records
    cursor.execute("SELECT * FROM tax_records")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    rec_file = f"{basepath}_records.csv"
    with open(rec_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    # Export people
    cursor.execute("SELECT * FROM people")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    ppl_file = f"{basepath}_people.csv"
    with open(ppl_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()
    print(f"✅ Exported → {rec_file}, {ppl_file}")


def export_to_json(filepath="export.json"):
    """Export everything to a single JSON file with nested structure."""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tax_records")
    records = cursor.fetchall()
    rec_headers = [d[0] for d in cursor.description]

    data = []
    for rec in records:
        rec_dict = dict(zip(rec_headers, rec))
        rec_id = rec_dict["id"]

        cursor.execute("SELECT * FROM people WHERE record_id=?", (rec_id,))
        people = cursor.fetchall()
        ppl_headers = [d[0] for d in cursor.description]
        rec_dict["people"] = [dict(zip(ppl_headers, p)) for p in people]

        data.append(rec_dict)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    conn.close()
    print(f"✅ Exported → {filepath}")


def import_from_csv(records_file: str, people_file: str):
    """Import data from CSV files with auto-backup."""
    # 📦 Create backup before import
    backup_db_to_csv()
    print("📦 Backup created before CSV import.")

    if not os.path.exists(records_file):
        print(f"❌ Records file not found: {records_file}")
        return

    if not os.path.exists(people_file):
        print(f"❌ People file not found: {people_file}")
        return

    conn = get_conn()
    cursor = conn.cursor()

    # Import records
    with open(records_file, "r", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers:
            print("❌ Records CSV has no headers.")
            conn.close()
            return

        placeholders = ",".join(["?"] * len(headers))
        for row in reader:
            cursor.execute(
                f"INSERT INTO tax_records ({','.join(headers)}) VALUES ({placeholders})",
                [row[h] for h in headers],
            )

    # Import people
    with open(people_file, "r", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers:
            print("❌ People CSV has no headers.")
            conn.close()
            return

        placeholders = ",".join(["?"] * len(headers))
        for row in reader:
            cursor.execute(
                f"INSERT INTO people ({','.join(headers)}) VALUES ({placeholders})",
                [row[h] for h in headers],
            )

    conn.commit()
    conn.close()
    print(f"✅ Imported CSV from {records_file} and {people_file}")

def import_from_json(filepath: str):
    """Import data from JSON with auto-backup."""
    # 📦 Create backup before import
    backup_db_to_csv()
    print("📦 Backup created before JSON import.")

    if not os.path.exists(filepath):
        print("❌ File not found.")
        return

    with open(filepath, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("❌ JSON must contain a list of record objects.")
        return

    conn = get_conn()
    cursor = conn.cursor()

    for record in data:
        people = record.pop("people", [])  # Extract people from record

        # Insert record
        rec_keys = [k for k in record.keys() if k != "id"]  # Skip id, let it auto-increment
        rec_values = [record[k] for k in rec_keys]
        placeholders = ",".join(["?"] * len(rec_keys))
        cursor.execute(
            f"INSERT INTO tax_records ({','.join(rec_keys)}) VALUES ({placeholders})",
            rec_values
        )
        new_record_id = cursor.lastrowid

        # Insert people for this record
        for person in people:
            person["record_id"] = new_record_id  # Update to new record_id
            ppl_keys = [k for k in person.keys() if k != "id"]  # Skip id
            ppl_values = [person[k] for k in ppl_keys]
            placeholders = ",".join(["?"] * len(ppl_keys))
            cursor.execute(
                f"INSERT INTO people ({','.join(ppl_keys)}) VALUES ({placeholders})",
                ppl_values
            )

    conn.commit()
    conn.close()
    print(f"✅ Imported JSON from {filepath}")

def get_revenue_summary():
    """Aggregate revenue, costs, and net income by year."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y', created_at) as year,
               SUM(revenue), SUM(total_costs),
               SUM(net_income_group)
        FROM tax_records
        GROUP BY year
        ORDER BY year DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_top_people(limit=10):
    """Top people ranked by total net income."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name,
               SUM(gross_income),
               SUM(tax_paid),
               SUM(net_income)
        FROM people
        GROUP BY name
        ORDER BY SUM(net_income) DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
