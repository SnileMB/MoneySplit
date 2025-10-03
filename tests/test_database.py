"""Tests for database operations."""

import pytest
import sqlite3
import os
from DB import setup


class TestDatabaseOperations:
    """Test database CRUD operations."""

    def test_insert_and_fetch_record(self):
        """Test inserting and fetching a tax record."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Insert a test record
        cursor.execute("""
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 10000, 1500, 8500, 4250, "US", "Individual", 500, 3750, 8000))

        record_id = cursor.lastrowid
        conn.commit()

        # Fetch the record
        cursor.execute("SELECT * FROM tax_records WHERE id = ?", (record_id,))
        record = cursor.fetchone()

        assert record is not None
        assert record[2] == 10000  # revenue
        assert record[3] == 1500   # total_costs

        conn.close()

    def test_delete_record(self):
        """Test deleting a record."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Insert
        cursor.execute("""
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """)
        record_id = cursor.lastrowid
        conn.commit()

        # Delete
        cursor.execute("DELETE FROM tax_records WHERE id = ?", (record_id,))
        conn.commit()

        # Verify deleted
        cursor.execute("SELECT * FROM tax_records WHERE id = ?", (record_id,))
        assert cursor.fetchone() is None

        conn.close()

    def test_update_record(self):
        """Test updating a record."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Insert
        cursor.execute("""
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """)
        record_id = cursor.lastrowid
        conn.commit()

        # Update
        cursor.execute("UPDATE tax_records SET revenue = ? WHERE id = ?", (6000, record_id))
        conn.commit()

        # Verify updated
        cursor.execute("SELECT revenue FROM tax_records WHERE id = ?", (record_id,))
        updated_revenue = cursor.fetchone()[0]
        assert updated_revenue == 6000

        conn.close()


class TestPeopleTable:
    """Test people table operations."""

    def test_insert_person(self):
        """Test adding a person to a record."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Create a tax record first
        cursor.execute("""
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """)
        record_id = cursor.lastrowid

        # Insert person
        cursor.execute("""
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (record_id, "Alice", 1.0, 4500, 450, 4050))

        conn.commit()

        # Verify
        cursor.execute("SELECT * FROM people WHERE record_id = ?", (record_id,))
        person = cursor.fetchone()

        assert person is not None
        assert person[2] == "Alice"
        assert person[3] == 1.0

        conn.close()

    def test_multiple_people_per_record(self):
        """Test adding multiple people to one record."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Create record
        cursor.execute("""
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (2, 10000, 1000, 9000, 4500, "US", "Individual", 900, 4050, 8100)
        """)
        record_id = cursor.lastrowid

        # Insert multiple people
        people = [
            (record_id, "Alice", 0.6, 5400, 540, 4860),
            (record_id, "Bob", 0.4, 3600, 360, 3240)
        ]

        cursor.executemany("""
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """, people)

        conn.commit()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM people WHERE record_id = ?", (record_id,))
        count = cursor.fetchone()[0]
        assert count == 2

        cursor.execute("SELECT SUM(work_share) FROM people WHERE record_id = ?", (record_id,))
        total_share = cursor.fetchone()[0]
        assert abs(total_share - 1.0) < 0.01  # Should sum to 1.0

        conn.close()


class TestTaxBrackets:
    """Test tax brackets table."""

    def test_fetch_tax_brackets(self):
        """Test fetching tax brackets."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Fetch US Individual brackets
        cursor.execute("""
            SELECT income_limit, rate FROM tax_brackets
            WHERE country = 'US' AND tax_type = 'Individual'
            ORDER BY income_limit
        """)

        brackets = cursor.fetchall()
        assert len(brackets) > 0

        # First bracket should have lowest rate
        assert brackets[0][1] <= brackets[-1][1]

        conn.close()

    def test_tax_bracket_ordering(self):
        """Test that tax brackets are ordered correctly."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT income_limit FROM tax_brackets
            WHERE country = 'US' AND tax_type = 'Individual'
            ORDER BY income_limit
        """)

        limits = [row[0] for row in cursor.fetchall()]

        # Verify ascending order
        for i in range(len(limits) - 1):
            assert limits[i] < limits[i + 1]

        conn.close()


class TestDataIntegrity:
    """Test data integrity and constraints."""

    def test_foreign_key_constraint(self):
        """Test that foreign key constraints are enforced."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Try to insert person with non-existent record_id
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (99999, "NonExistent", 1.0, 1000, 100, 900))
            conn.commit()

        conn.close()

    def test_cascade_delete(self):
        """Test that deleting a record requires deleting people first (FK constraint)."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Create record with person
        cursor.execute("""
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """)
        record_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (record_id, "Test", 1.0, 4500, 450, 4050))

        conn.commit()

        # Delete people first, then record (FK constraint prevents direct delete)
        cursor.execute("DELETE FROM people WHERE record_id = ?", (record_id,))
        cursor.execute("DELETE FROM tax_records WHERE id = ?", (record_id,))
        conn.commit()

        # Verify both deleted
        cursor.execute("SELECT COUNT(*) FROM people WHERE record_id = ?", (record_id,))
        assert cursor.fetchone()[0] == 0

        cursor.execute("SELECT COUNT(*) FROM tax_records WHERE id = ?", (record_id,))
        assert cursor.fetchone()[0] == 0

        conn.close()


class TestDatabaseQueries:
    """Test complex database queries."""

    def test_aggregate_revenue_by_month(self):
        """Test aggregating revenue by month."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT strftime('%Y-%m', created_at) as month,
                   SUM(revenue) as total_revenue,
                   COUNT(*) as num_records
            FROM tax_records
            GROUP BY month
            ORDER BY month
        """)

        results = cursor.fetchall()

        if len(results) > 0:
            # Each result should have month, revenue, count
            for row in results:
                assert len(row) == 3
                assert row[1] > 0  # revenue should be positive
                assert row[2] > 0  # count should be positive

        conn.close()

    def test_top_earners_query(self):
        """Test querying top earners."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name,
                   SUM(gross_income) as total_earned,
                   COUNT(*) as projects
            FROM people
            GROUP BY name
            ORDER BY total_earned DESC
            LIMIT 5
        """)

        results = cursor.fetchall()

        if len(results) > 0:
            # Results should be ordered by earnings (descending)
            for i in range(len(results) - 1):
                assert results[i][1] >= results[i + 1][1]

        conn.close()

    def test_tax_rate_calculation(self):
        """Test calculating average tax rates."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tax_origin,
                   tax_option,
                   AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate,
                   COUNT(*) as count
            FROM tax_records
            WHERE group_income > 0
            GROUP BY tax_origin, tax_option
        """)

        results = cursor.fetchall()

        for row in results:
            country, tax_type, avg_rate, count = row
            # Tax rate should be reasonable (0-50%)
            assert 0 <= avg_rate <= 50

        conn.close()
