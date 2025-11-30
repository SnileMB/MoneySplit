"""Edge case and boundary testing."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from Logic.tax_calculator import calculate_tax, split_work_shares, calculate_profit
from Logic.validators import ValidationError, validate_work_shares, validate_tax_rate

client = TestClient(app)


class TestBoundaryValues:
    """Test boundary and extreme values."""

    def test_very_large_revenue(self):
        """Test handling of very large revenue values."""
        payload = {
            "num_people": 1,
            "revenue": 10000000,  # 10 million
            "costs": [1000000],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Millionaire", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201

    def test_very_small_revenue(self):
        """Test handling of very small revenue values."""
        payload = {
            "num_people": 1,
            "revenue": 0.01,  # 1 cent
            "costs": [0.001],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Penny", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201

    def test_zero_revenue(self):
        """Test handling of zero revenue."""
        payload = {
            "num_people": 1,
            "revenue": 0,
            "costs": [0],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Zero", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        # Should either accept or reject gracefully
        assert response.status_code in [201, 400, 422]

    def test_many_people(self):
        """Test handling of many people in a project."""
        num_people = 50
        payload = {
            "num_people": num_people,
            "revenue": 100000,
            "costs": [1000],
            "country": "US",
            "tax_type": "Individual",
            "people": [
                {"name": f"Person{i}", "work_share": 1.0 / num_people}
                for i in range(num_people)
            ],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201

    def test_single_person_project(self):
        """Test single person project."""
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Solo", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201


class TestInvalidInputs:
    """Test invalid input handling."""

    def test_negative_num_people(self):
        """Test negative number of people."""
        payload = {
            "num_people": -1,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Individual",
            "people": [],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 422  # Validation error

    def test_empty_people_list(self):
        """Test empty people list."""
        payload = {
            "num_people": 2,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Individual",
            "people": [],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code in [400, 422]

    def test_mismatched_num_people(self):
        """Test mismatch between num_people and actual people list."""
        payload = {
            "num_people": 5,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Individual",
            "people": [
                {"name": "Person1", "work_share": 0.5},
                {"name": "Person2", "work_share": 0.5},
            ],  # Only 2 people but num_people=5
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code in [400, 422]

    def test_invalid_country(self):
        """Test invalid country code."""
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [500],
            "country": "",  # Empty country
            "tax_type": "Individual",
            "people": [{"name": "Test", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code in [400, 422]

    def test_invalid_tax_type(self):
        """Test invalid tax type."""
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Corporate",  # Invalid type
            "people": [{"name": "Test", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code in [400, 422]


class TestWorkShareEdgeCases:
    """Test work share edge cases."""

    def test_work_shares_sum_to_zero(self):
        """Test work shares that sum to zero."""
        with pytest.raises(ValidationError):
            validate_work_shares([0.0, 0.0])

    def test_work_shares_sum_slightly_off(self):
        """Test work shares that sum to almost 1.0."""
        # Should pass with small tolerance
        validate_work_shares([0.33, 0.33, 0.34])  # Sums to 1.0
        validate_work_shares([0.333, 0.333, 0.334])  # Sums to 1.0

    def test_work_shares_very_unequal(self):
        """Test very unequal work shares."""
        payload = {
            "num_people": 2,
            "revenue": 10000,
            "costs": [1000],
            "country": "US",
            "tax_type": "Individual",
            "people": [
                {"name": "Leader", "work_share": 0.99},
                {"name": "Helper", "work_share": 0.01},
            ],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201

    def test_all_work_to_one_person(self):
        """Test when one person does all work."""
        profit = 10000
        work_shares = [1.0, 0.0, 0.0]

        distribution = split_work_shares(profit, work_shares)

        assert distribution[0] == 10000
        assert distribution[1] == 0
        assert distribution[2] == 0


class TestCostsEdgeCases:
    """Test costs edge cases."""

    def test_costs_exceed_revenue(self):
        """Test when costs exceed revenue (negative profit)."""
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [6000],  # Costs > revenue
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Loss", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        # Should handle negative profit scenario
        assert response.status_code in [201, 400]

    def test_many_small_costs(self):
        """Test many small cost items."""
        costs = [0.01] * 1000  # 1000 costs of 1 cent each

        payload = {
            "num_people": 1,
            "revenue": 20,
            "costs": costs,
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Penny", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201

    def test_zero_costs(self):
        """Test project with zero costs."""
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [],  # No costs
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "NoCost", "work_share": 1.0}],
        }

        response = client.post("/api/projects", json=payload)
        assert response.status_code == 201


class TestTaxCalculationEdgeCases:
    """Test tax calculation edge cases."""

    def test_income_at_bracket_boundary(self):
        """Test income exactly at bracket boundary."""
        brackets = [(10000, 0.10), (50000, 0.20)]
        tax = calculate_tax(10000, brackets)  # Exactly at boundary

        # 10000 at 10% = 1000
        assert abs(tax - 1000) < 0.01

    def test_zero_income_tax(self):
        """Test tax on zero income."""
        brackets = [(10000, 0.10), (50000, 0.20)]
        tax = calculate_tax(0, brackets)

        assert tax == 0

    def test_income_in_top_bracket(self):
        """Test very high income in top bracket."""
        brackets = [(10000, 0.10), (50000, 0.20), (100000, 0.30)]
        tax = calculate_tax(500000, brackets)

        # Should use all brackets
        assert tax > 0


class TestAPIEdgeCases:
    """Test API edge cases."""

    def test_get_nonexistent_record_various_ids(self):
        """Test getting records with various nonexistent IDs."""
        for record_id in [0, -1, 999999, "abc"]:
            response = client.get(f"/api/records/{record_id}")
            assert response.status_code in [404, 422]

    def test_concurrent_project_creation(self):
        """Test creating multiple projects rapidly."""
        payload = {
            "num_people": 1,
            "revenue": 5000,
            "costs": [500],
            "country": "US",
            "tax_type": "Individual",
            "people": [{"name": "Concurrent", "work_share": 1.0}],
        }

        # Create 10 projects rapidly
        responses = []
        for i in range(10):
            payload["people"][0]["name"] = f"Person{i}"
            response = client.post("/api/projects", json=payload)
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 201

    def test_special_characters_in_names(self):
        """Test special characters in person names."""
        special_names = [
            "José García",
            "李明",
            "Müller",
            "O'Brien",
            "Jean-Pierre",
            "Владимир",
        ]

        for name in special_names:
            payload = {
                "num_people": 1,
                "revenue": 5000,
                "costs": [500],
                "country": "US",
                "tax_type": "Individual",
                "people": [{"name": name, "work_share": 1.0}],
            }

            response = client.post("/api/projects", json=payload)
            assert response.status_code == 201


class TestCalculationAccuracy:
    """Test calculation accuracy."""

    def test_floating_point_precision(self):
        """Test floating point precision in calculations."""
        profit = 10000.33
        work_shares = [0.333, 0.333, 0.334]

        distribution = split_work_shares(profit, work_shares)

        # Sum should equal original (within floating point tolerance)
        total = sum(distribution)
        assert abs(total - profit) < 0.01

    def test_profit_calculation_precision(self):
        """Test profit calculation precision."""
        revenue = 10000.99
        costs = [1000.33, 500.22, 300.11]

        profit = calculate_profit(revenue, costs)

        expected = revenue - sum(costs)
        assert abs(profit - expected) < 0.01
