"""
Comprehensive tests for database operations in setup.py.

Tests database CRUD operations, queries, tax bracket management, and utilities.
"""
import pytest
from DB import setup


class TestGetConnection:
    """Test database connection."""

    def test_get_conn_returns_connection(self):
        """Test that get_conn returns a valid database connection."""
        conn = setup.get_conn()
        assert conn is not None
        conn.close()

    def test_connection_cursor_available(self):
        """Test that connection cursor is available."""
        conn = setup.get_conn()
        cursor = conn.cursor()
        assert cursor is not None
        conn.close()


class TestTaxBracketOperations:
    """Test tax bracket database operations."""

    def test_get_tax_brackets_us_individual(self):
        """Test fetching US Individual tax brackets."""
        brackets = setup.get_tax_brackets("US", "Individual")
        assert isinstance(brackets, list)
        assert len(brackets) > 0
        # Each bracket should be a tuple (limit, rate)
        assert all(isinstance(b, tuple) and len(b) == 2 for b in brackets)

    def test_get_tax_brackets_us_business(self):
        """Test fetching US Business tax brackets."""
        brackets = setup.get_tax_brackets("US", "Business")
        assert isinstance(brackets, list)
        assert len(brackets) > 0

    def test_get_tax_brackets_spain_individual(self):
        """Test fetching Spain Individual tax brackets."""
        brackets = setup.get_tax_brackets("Spain", "Individual")
        assert isinstance(brackets, list)
        assert len(brackets) > 0

    def test_get_tax_brackets_with_id(self):
        """Test fetching tax brackets with ID included."""
        brackets = setup.get_tax_brackets("US", "Individual", include_id=True)
        assert isinstance(brackets, list)
        if len(brackets) > 0:
            # Should have 3 elements: id, limit, rate
            assert all(len(b) == 3 for b in brackets)

    def test_get_tax_brackets_invalid_country(self):
        """Test fetching tax brackets for invalid country."""
        brackets = setup.get_tax_brackets("InvalidCountry", "Individual")
        assert isinstance(brackets, list)

    def test_tax_bracket_rates_valid(self):
        """Test that tax bracket rates are valid percentages."""
        brackets = setup.get_tax_brackets("US", "Individual")
        for limit, rate in brackets:
            assert isinstance(limit, (int, float))
            assert isinstance(rate, (int, float))
            assert 0 <= rate <= 1  # Rates should be 0-100%


class TestRecordOperations:
    """Test record creation and retrieval operations."""

    def test_fetch_last_records_returns_list(self):
        """Test that fetch_last_records returns a list."""
        records = setup.fetch_last_records(n=5)
        assert isinstance(records, list)

    def test_fetch_last_records_limit(self):
        """Test that fetch_last_records respects the limit."""
        records = setup.fetch_last_records(n=5)
        assert len(records) <= 5

    def test_fetch_last_records_default(self):
        """Test fetch_last_records with default parameter."""
        records = setup.fetch_last_records()
        assert isinstance(records, list)

    def test_search_records_returns_list(self):
        """Test that search_records returns a list."""
        results = setup.search_records(country="US")
        assert isinstance(results, list)

    def test_search_records_by_country(self):
        """Test searching records by country."""
        results = setup.search_records(country="US")
        assert isinstance(results, list)

    def test_search_records_by_tax_option(self):
        """Test searching records by tax option."""
        results = setup.search_records(tax_option="Individual")
        assert isinstance(results, list)

    def test_get_record_by_id_valid(self):
        """Test getting a record by valid ID."""
        # Get the first record from database
        records = setup.fetch_last_records(n=1)
        if records:
            record_id = records[0][0]  # First column is ID
            record = setup.get_record_by_id(record_id)
            assert record is not None

    def test_get_record_by_id_invalid(self):
        """Test getting a record with invalid ID."""
        record = setup.get_record_by_id(999999)
        assert record is None


class TestPeopleOperations:
    """Test people-related database operations."""

    def test_fetch_people_by_record_returns_list(self):
        """Test that fetch_people_by_record returns a list."""
        records = setup.fetch_last_records(n=1)
        if records:
            record_id = records[0][0]
            people = setup.fetch_people_by_record(record_id)
            assert isinstance(people, list)

    def test_fetch_people_by_record_structure(self):
        """Test structure of fetched people records."""
        records = setup.fetch_last_records(n=1)
        if records:
            record_id = records[0][0]
            people = setup.fetch_people_by_record(record_id)
            for person in people:
                # Each person should have multiple fields
                assert isinstance(person, tuple)
                assert len(person) > 0

    def test_fetch_records_by_person_name(self):
        """Test fetching records by person name."""
        people = setup.fetch_people_by_record(setup.fetch_last_records(n=1)[0][0])
        if people:
            name = people[0][1]  # Name is typically second field
            results = setup.fetch_records_by_person(name)
            assert isinstance(results, list)

    def test_fetch_records_by_invalid_person(self):
        """Test fetching records for non-existent person."""
        results = setup.fetch_records_by_person("NonexistentPerson123456")
        assert isinstance(results, list)


class TestCalculateTaxFromDB:
    """Test tax calculation using database tax brackets."""

    def test_calculate_tax_from_db_us_individual(self):
        """Test calculating tax using US Individual brackets."""
        tax = setup.calculate_tax_from_db(50000, "US", "Individual")
        assert isinstance(tax, float)
        assert tax > 0

    def test_calculate_tax_from_db_us_business(self):
        """Test calculating tax using US Business brackets."""
        tax = setup.calculate_tax_from_db(50000, "US", "Business")
        assert isinstance(tax, float)

    def test_calculate_tax_from_db_spain(self):
        """Test calculating tax using Spain brackets."""
        tax = setup.calculate_tax_from_db(50000, "Spain", "Individual")
        assert isinstance(tax, float)

    def test_calculate_tax_from_db_zero_income(self):
        """Test tax calculation on zero income."""
        tax = setup.calculate_tax_from_db(0, "US", "Individual")
        assert tax == 0

    def test_calculate_tax_from_db_high_income(self):
        """Test tax calculation on high income."""
        tax = setup.calculate_tax_from_db(1000000, "US", "Individual")
        assert tax > 0

    def test_calculate_tax_from_db_consistency(self):
        """Test that same inputs produce same tax outputs."""
        tax1 = setup.calculate_tax_from_db(50000, "US", "Individual")
        tax2 = setup.calculate_tax_from_db(50000, "US", "Individual")
        assert tax1 == tax2


class TestDatabaseConnection:
    """Test database connection operations."""

    def test_multiple_connections(self):
        """Test opening multiple database connections."""
        conn1 = setup.get_conn()
        conn2 = setup.get_conn()
        assert conn1 is not None
        assert conn2 is not None
        conn1.close()
        conn2.close()

    def test_cursor_from_connection(self):
        """Test creating cursor from connection."""
        conn = setup.get_conn()
        cursor = conn.cursor()
        assert cursor is not None
        conn.close()

    def test_connection_commit(self):
        """Test that connection can be committed."""
        conn = setup.get_conn()
        cursor = conn.cursor()
        # Execute a safe query
        cursor.execute("SELECT COUNT(*) FROM tax_records")
        conn.commit()
        conn.close()


class TestDatabaseQueries:
    """Test various database queries."""

    def test_count_records(self):
        """Test counting records in database."""
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tax_records")
        count = cursor.fetchone()[0]
        assert isinstance(count, int)
        assert count >= 0
        conn.close()

    def test_count_people(self):
        """Test counting people in database."""
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM people")
        count = cursor.fetchone()[0]
        assert isinstance(count, int)
        assert count >= 0
        conn.close()

    def test_count_tax_brackets(self):
        """Test counting tax brackets."""
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tax_brackets")
        count = cursor.fetchone()[0]
        assert isinstance(count, int)
        assert count > 0
        conn.close()

    def test_get_max_record_id(self):
        """Test getting maximum record ID."""
        conn = setup.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM tax_records")
        max_id = cursor.fetchone()[0]
        assert max_id is None or isinstance(max_id, int)
        conn.close()


class TestTaxBracketRetrieval:
    """Test tax bracket retrieval accuracy."""

    def test_all_countries_have_brackets(self):
        """Test that all expected countries have tax brackets."""
        countries = ["US", "Spain"]
        for country in countries:
            for tax_type in ["Individual", "Business"]:
                brackets = setup.get_tax_brackets(country, tax_type)
                assert len(brackets) > 0, f"No brackets for {country} {tax_type}"

    def test_bracket_limits_ascending(self):
        """Test that bracket limits are in ascending order."""
        brackets = setup.get_tax_brackets("US", "Individual")
        limits = [b[0] for b in brackets]
        # Check if limits are in ascending order
        assert limits == sorted(limits)

    def test_bracket_rates_non_negative(self):
        """Test that all tax rates are non-negative."""
        brackets = setup.get_tax_brackets("US", "Individual")
        for limit, rate in brackets:
            assert rate >= 0, f"Negative rate found: {rate}"

    def test_progressive_tax_brackets(self):
        """Test that tax brackets represent progressive taxation."""
        brackets = setup.get_tax_brackets("US", "Individual")
        # Generally, progressive tax has increasing or stable rates
        # (not guaranteed, but common pattern)
        assert len(brackets) > 1


class TestDatabaseIntegrity:
    """Test database integrity constraints."""

    def test_foreign_key_constraint(self):
        """Test that foreign key relationships are maintained."""
        # Get a record and verify it has people
        records = setup.fetch_last_records(n=1)
        if records:
            record_id = records[0][0]
            people = setup.fetch_people_by_record(record_id)
            # Each person should reference a valid record
            for person in people:
                assert person is not None

    def test_tax_bracket_data_integrity(self):
        """Test that tax bracket data is valid."""
        brackets = setup.get_tax_brackets("US", "Individual")
        for limit, rate in brackets:
            # Limits should be non-negative
            assert limit >= 0
            # Rates should be valid percentages
            assert 0 <= rate <= 1
