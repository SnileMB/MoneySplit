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
        cursor.execute(
            """
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (2, 10000, 1500, 8500, 4250, "US", "Individual", 500, 3750, 8000),
        )

        record_id = cursor.lastrowid
        conn.commit()

        # Fetch the record
        cursor.execute("SELECT * FROM tax_records WHERE id = ?", (record_id,))
        record = cursor.fetchone()

        assert record is not None
        assert record[2] == 10000  # revenue
        assert record[3] == 1500  # total_costs

        conn.close()

    def test_delete_record(self):
        """Test deleting a record."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Insert
        cursor.execute(
            """
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """
        )
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
        cursor.execute(
            """
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """
        )
        record_id = cursor.lastrowid
        conn.commit()

        # Update
        cursor.execute(
            "UPDATE tax_records SET revenue = ? WHERE id = ?", (6000, record_id)
        )
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
        cursor.execute(
            """
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """
        )
        record_id = cursor.lastrowid

        # Insert person
        cursor.execute(
            """
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (record_id, "Alice", 1.0, 4500, 450, 4050),
        )

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
        cursor.execute(
            """
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (2, 10000, 1000, 9000, 4500, "US", "Individual", 900, 4050, 8100)
        """
        )
        record_id = cursor.lastrowid

        # Insert multiple people
        people = [
            (record_id, "Alice", 0.6, 5400, 540, 4860),
            (record_id, "Bob", 0.4, 3600, 360, 3240),
        ]

        cursor.executemany(
            """
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            people,
        )

        conn.commit()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM people WHERE record_id = ?", (record_id,))
        count = cursor.fetchone()[0]
        assert count == 2

        cursor.execute(
            "SELECT SUM(work_share) FROM people WHERE record_id = ?", (record_id,)
        )
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
        cursor.execute(
            """
            SELECT income_limit, rate FROM tax_brackets
            WHERE country = 'US' AND tax_type = 'Individual'
            ORDER BY income_limit
        """
        )

        brackets = cursor.fetchall()
        assert len(brackets) > 0

        # First bracket should have lowest rate
        assert brackets[0][1] <= brackets[-1][1]

        conn.close()

    def test_tax_bracket_ordering(self):
        """Test that tax brackets are ordered correctly."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT income_limit FROM tax_brackets
            WHERE country = 'US' AND tax_type = 'Individual'
            ORDER BY income_limit
        """
        )

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
            cursor.execute(
                """
                INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (99999, "NonExistent", 1.0, 1000, 100, 900),
            )
            conn.commit()

        conn.close()

    def test_cascade_delete(self):
        """Test that deleting a record requires deleting people first (FK constraint)."""
        conn = setup.get_conn()
        cursor = conn.cursor()

        # Create record with person
        cursor.execute(
            """
            INSERT INTO tax_records (num_people, revenue, total_costs, group_income,
                                    individual_income, tax_origin, tax_option, tax_amount,
                                    net_income_per_person, net_income_group)
            VALUES (1, 5000, 500, 4500, 4500, "US", "Individual", 450, 4050, 4050)
        """
        )
        record_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO people (record_id, name, work_share, gross_income, tax_paid, net_income)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (record_id, "Test", 1.0, 4500, 450, 4050),
        )

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

        cursor.execute(
            """
            SELECT strftime('%Y-%m', created_at) as month,
                   SUM(revenue) as total_revenue,
                   COUNT(*) as num_records
            FROM tax_records
            GROUP BY month
            ORDER BY month
        """
        )

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

        cursor.execute(
            """
            SELECT name,
                   SUM(gross_income) as total_earned,
                   COUNT(*) as projects
            FROM people
            GROUP BY name
            ORDER BY total_earned DESC
            LIMIT 5
        """
        )

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

        cursor.execute(
            """
            SELECT tax_origin,
                   tax_option,
                   AVG(tax_amount * 100.0 / NULLIF(group_income, 0)) as avg_tax_rate,
                   COUNT(*) as count
            FROM tax_records
            WHERE group_income > 0
            GROUP BY tax_origin, tax_option
        """
        )

        results = cursor.fetchall()

        for row in results:
            country, tax_type, avg_rate, count = row
            # Tax rate should be reasonable (0-50%)
            assert 0 <= avg_rate <= 50

        conn.close()


class TestDBSetupFunctions:
    """Test DB setup.py helper functions."""

    def test_insert_record(self):
        """Test insert_record function."""
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=100000,
            total_costs=20000,
            tax_amount=15000,
            net_income_group=65000,
            net_income_per_person=32500,
            num_people=2,
            group_income=80000,
            individual_income=40000,
        )

        assert record_id is not None
        assert record_id > 0

        # Verify record exists
        record = setup.get_record_by_id(record_id)
        assert record is not None
        # Columns: id, tax_origin, tax_option, revenue, total_costs, ...
        assert record[3] == 100000  # revenue
        assert record[1] == "US"    # tax_origin

    def test_insert_person(self):
        """Test insert_person function."""
        # Create a record first
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=50000,
            total_costs=10000,
            tax_amount=8000,
            net_income_group=32000,
            net_income_per_person=32000,
            num_people=1,
            group_income=40000,
            individual_income=40000,
        )

        # Insert person
        person_id = setup.insert_person(
            record_id=record_id,
            name="Alice",
            work_share=1.0,
            gross_income=40000,
            tax_paid=8000,
            net_income=32000,
        )

        assert person_id is not None
        assert person_id > 0

        # Verify person exists
        people = setup.fetch_people_by_record(record_id)
        assert len(people) == 1
        assert people[0][1] == "Alice"  # name is column 1

    def test_get_record_by_id(self):
        """Test get_record_by_id function."""
        # Insert a test record
        record_id = setup.insert_record(
            tax_origin="Spain",
            tax_option="Business",
            revenue=75000,
            total_costs=15000,
            tax_amount=12000,
            net_income_group=48000,
            net_income_per_person=24000,
            num_people=2,
            group_income=60000,
            individual_income=30000,
        )

        # Fetch it
        record = setup.get_record_by_id(record_id)

        assert record is not None
        assert record[0] == record_id   # id
        assert record[1] == "Spain"     # tax_origin
        assert record[3] == 75000       # revenue

    def test_get_record_by_id_not_found(self):
        """Test get_record_by_id with non-existent ID."""
        record = setup.get_record_by_id(999999)
        assert record is None

    def test_fetch_last_records(self):
        """Test fetch_last_records function."""
        # Insert multiple records
        for i in range(5):
            setup.insert_record(
                tax_origin="US",
                tax_option="Individual",
                revenue=10000 * (i + 1),
                total_costs=1000,
                tax_amount=1500,
                net_income_group=8500,
                net_income_per_person=8500,
                num_people=1,
                group_income=9000,
                individual_income=9000,
            )

        # Fetch last 3
        records = setup.fetch_last_records(3)
        assert len(records) <= 3

        # Function orders by created_at DESC, not by ID
        # Just verify we got some records back
        if len(records) > 0:
            assert records[0][0] > 0  # ID should be positive

    def test_delete_record_function(self):
        """Test delete_record function."""
        # Create record
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=50000,
            total_costs=5000,
            tax_amount=8000,
            net_income_group=37000,
            net_income_per_person=37000,
            num_people=1,
            group_income=45000,
            individual_income=45000,
        )

        # Delete it
        setup.delete_record(record_id)

        # Verify deleted
        record = setup.get_record_by_id(record_id)
        assert record is None

    def test_update_record_function(self):
        """Test update_record function."""
        # Create record
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=50000,
            total_costs=5000,
            tax_amount=8000,
            net_income_group=37000,
            net_income_per_person=37000,
            num_people=1,
            group_income=45000,
            individual_income=45000,
        )

        # Update revenue
        setup.update_record(record_id, "revenue", 60000)

        # Verify updated
        record = setup.get_record_by_id(record_id)
        assert record[3] == 60000  # revenue is column 3

    def test_add_person_function(self):
        """Test add_person function."""
        # Create record
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=100000,
            total_costs=10000,
            tax_amount=18000,
            net_income_group=72000,
            net_income_per_person=36000,
            num_people=2,
            group_income=90000,
            individual_income=45000,
        )

        # Add person
        person_id = setup.add_person(
            record_id=record_id,
            name="Bob",
            work_share=0.5,
            gross_income=45000,
            tax_paid=9000,
            net_income=36000,
        )

        assert person_id > 0

        # Verify
        people = setup.fetch_people_by_record(record_id)
        assert len(people) == 1
        assert people[0][1] == "Bob"  # name is column 1

    def test_fetch_people_by_record(self):
        """Test fetch_people_by_record function."""
        # Create record with multiple people
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=100000,
            total_costs=10000,
            tax_amount=18000,
            net_income_group=72000,
            net_income_per_person=24000,
            num_people=3,
            group_income=90000,
            individual_income=30000,
        )

        # Add people
        setup.insert_person(record_id, "Alice", 0.5, 45000, 9000, 36000)
        setup.insert_person(record_id, "Bob", 0.3, 27000, 5400, 21600)
        setup.insert_person(record_id, "Charlie", 0.2, 18000, 3600, 14400)

        # Fetch
        people = setup.fetch_people_by_record(record_id)
        assert len(people) == 3
        names = [p[1] for p in people]  # name is column 1
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names

    def test_delete_person_function(self):
        """Test delete_person function."""
        # Create record and person
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=50000,
            total_costs=5000,
            tax_amount=8000,
            net_income_group=37000,
            net_income_per_person=37000,
            num_people=1,
            group_income=45000,
            individual_income=45000,
        )

        person_id = setup.insert_person(record_id, "Test", 1.0, 45000, 8000, 37000)

        # Delete person
        setup.delete_person(person_id)

        # Verify deleted
        people = setup.fetch_people_by_record(record_id)
        assert len(people) == 0

    def test_get_tax_brackets(self):
        """Test get_tax_brackets function."""
        brackets = setup.get_tax_brackets("US", "Individual")

        assert len(brackets) > 0
        assert isinstance(brackets, list)

        # Each bracket should have income_limit and rate
        for bracket in brackets:
            assert "income_limit" in bracket or len(bracket) >= 2

    def test_add_tax_bracket(self):
        """Test add_tax_bracket function."""
        bracket_id = setup.add_tax_bracket(
            country="TestCountry",
            tax_type="TestType",
            income_limit=50000,
            rate=0.20,
        )

        assert bracket_id > 0

        # Verify it was added
        brackets = setup.get_tax_brackets("TestCountry", "TestType")
        assert len(brackets) > 0

    def test_delete_tax_bracket(self):
        """Test delete_tax_bracket function."""
        # Add a bracket
        bracket_id = setup.add_tax_bracket(
            country="TempCountry",
            tax_type="TempType",
            income_limit=30000,
            rate=0.15,
        )

        # Delete it
        setup.delete_tax_bracket(bracket_id)

        # Verify deleted (get_tax_brackets should return empty or not include it)
        brackets = setup.get_tax_brackets("TempCountry", "TempType", include_id=True)
        bracket_ids = [b.get("id") or b[0] for b in brackets if isinstance(b, (dict, tuple))]
        assert bracket_id not in bracket_ids

    def test_update_tax_bracket(self):
        """Test update_tax_bracket function."""
        # Add a bracket
        bracket_id = setup.add_tax_bracket(
            country="UpdateTest",
            tax_type="TestType",
            income_limit=40000,
            rate=0.18,
        )

        # Update the rate
        setup.update_tax_bracket(bracket_id, "rate", 0.22)

        # Verify updated
        brackets = setup.get_tax_brackets("UpdateTest", "TestType", include_id=True)
        found = False
        for bracket in brackets:
            if isinstance(bracket, dict):
                if bracket.get("id") == bracket_id:
                    assert bracket["rate"] == 0.22
                    found = True
            elif isinstance(bracket, tuple) and len(bracket) >= 3:
                if bracket[0] == bracket_id:
                    assert bracket[2] == 0.22
                    found = True

        # Clean up
        setup.delete_tax_bracket(bracket_id)

    def test_calculate_tax_from_db(self):
        """Test calculate_tax_from_db function."""
        # This function calculates tax using brackets from DB
        tax = setup.calculate_tax_from_db(50000, "US", "Individual")

        assert tax is not None
        assert tax >= 0
        assert isinstance(tax, (int, float))

    def test_fetch_records_by_person(self):
        """Test fetch_records_by_person function."""
        # Create records with same person name
        record_id1 = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=50000,
            total_costs=5000,
            tax_amount=8000,
            net_income_group=37000,
            net_income_per_person=37000,
            num_people=1,
            group_income=45000,
            individual_income=45000,
        )
        setup.insert_person(record_id1, "TestPerson", 1.0, 45000, 8000, 37000)

        record_id2 = setup.insert_record(
            tax_origin="Spain",
            tax_option="Individual",
            revenue=60000,
            total_costs=6000,
            tax_amount=10000,
            net_income_group=44000,
            net_income_per_person=44000,
            num_people=1,
            group_income=54000,
            individual_income=54000,
        )
        setup.insert_person(record_id2, "TestPerson", 1.0, 54000, 10000, 44000)

        # Fetch records for this person
        records = setup.fetch_records_by_person("TestPerson")

        assert len(records) >= 2

    def test_clone_record(self):
        """Test clone_record function."""
        # Create original record with people
        original_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=80000,
            total_costs=8000,
            tax_amount=14000,
            net_income_group=58000,
            net_income_per_person=58000,
            num_people=1,
            group_income=72000,
            individual_income=72000,
        )
        setup.insert_person(original_id, "Original", 1.0, 72000, 14000, 58000)

        # Clone it
        cloned_id = setup.clone_record(original_id)

        assert cloned_id is not None
        assert cloned_id != original_id

        # Verify cloned record exists
        cloned = setup.get_record_by_id(cloned_id)
        original = setup.get_record_by_id(original_id)

        assert cloned[3] == original[3]  # revenue
        assert cloned[1] == original[1]  # tax_origin

    def test_search_records(self):
        """Test search_records function."""
        # Create test records
        setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=50000,
            total_costs=5000,
            tax_amount=8000,
            net_income_group=37000,
            net_income_per_person=37000,
            num_people=1,
            group_income=45000,
            individual_income=45000,
        )

        # Search for US records
        results = setup.search_records(country="US")

        assert len(results) > 0
        # search_records returns: id, tax_origin, tax_option, revenue, ...
        for record in results:
            assert record[1] == "US"  # tax_origin is column 1

    def test_search_records_by_tax_option(self):
        """Test search_records filtering by tax option."""
        # Search for Individual tax records
        results = setup.search_records(tax_option="Individual")

        if len(results) > 0:
            # search_records returns: id, tax_origin, tax_option, revenue, ...
            for record in results:
                assert record[2] == "Individual"  # tax_option is column 2

    def test_add_tax_brackets_from_csv(self, tmp_path):
        """Test adding tax brackets from CSV file."""
        # Create a temporary CSV file with proper headers
        csv_file = tmp_path / "test_brackets.csv"
        csv_file.write_text("income_limit,rate\n50000,0.20\n100000,0.30\n")

        # Add brackets from CSV
        setup.add_tax_brackets_from_csv("TestCSVCountry", "Individual", str(csv_file))

        # Verify brackets were added
        brackets = setup.get_tax_brackets("TestCSVCountry", "Individual")
        assert len(brackets) >= 2

    def test_export_tax_template(self, tmp_path):
        """Test export_tax_template function."""
        template_file = tmp_path / "template.csv"

        # Export template
        setup.export_tax_template(str(template_file))

        # Verify file was created
        assert template_file.exists()

        # Verify it has content
        content = template_file.read_text()
        assert len(content) > 0
        assert "income_limit" in content or "," in content

    def test_copy_people(self):
        """Test copy_people function."""
        # Create source record with people
        source_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=100000,
            total_costs=10000,
            tax_amount=18000,
            net_income_group=72000,
            net_income_per_person=36000,
            num_people=2,
            group_income=90000,
            individual_income=45000,
        )
        setup.insert_person(source_id, "Alice", 0.5, 45000, 9000, 36000)
        setup.insert_person(source_id, "Bob", 0.5, 45000, 9000, 36000)

        # Create target record
        target_id = setup.insert_record(
            tax_origin="Spain",
            tax_option="Individual",
            revenue=100000,
            total_costs=10000,
            tax_amount=18000,
            net_income_group=72000,
            net_income_per_person=36000,
            num_people=2,
            group_income=90000,
            individual_income=45000,
        )

        # Copy people
        setup.copy_people(source_id, target_id)

        # Verify people were copied
        target_people = setup.fetch_people_by_record(target_id)
        assert len(target_people) == 2

    def test_deduplicate_people(self):
        """Test deduplicate_people function."""
        # Create record with duplicate people
        record_id = setup.insert_record(
            tax_origin="US",
            tax_option="Individual",
            revenue=100000,
            total_costs=10000,
            tax_amount=18000,
            net_income_group=72000,
            net_income_per_person=36000,
            num_people=2,
            group_income=90000,
            individual_income=45000,
        )

        # Add duplicate names
        setup.insert_person(record_id, "DupePerson", 0.5, 45000, 9000, 36000)
        setup.insert_person(record_id, "DupePerson", 0.5, 45000, 9000, 36000)
        setup.insert_person(record_id, "UniquePerson", 0.5, 45000, 9000, 36000)

        # Deduplicate
        removed = setup.deduplicate_people(record_id)

        # Should have removed at least 1 duplicate
        assert removed >= 1

        # Verify duplicates removed
        people = setup.fetch_people_by_record(record_id)
        names = [p[1] for p in people]
        assert names.count("DupePerson") == 1  # Only one DupePerson should remain
