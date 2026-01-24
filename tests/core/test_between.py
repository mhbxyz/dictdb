"""
Unit tests for BETWEEN range operator.
"""

import pytest

from dictdb import Table, Condition


class TestBetween:
    """Tests for Field.between() method."""

    @pytest.fixture
    def table(self) -> Table:
        """Create a table with test data."""
        t = Table("users", primary_key="id")
        t.insert({"id": 1, "name": "Alice", "age": 25})
        t.insert({"id": 2, "name": "Bob", "age": 30})
        t.insert({"id": 3, "name": "Charlie", "age": 35})
        t.insert({"id": 4, "name": "Diana", "age": 40})
        t.insert({"id": 5, "name": "Eve", "age": 45})
        return t

    def test_between_basic(self, table: Table) -> None:
        """Test basic between query."""
        results = table.select(where=Condition(table.age.between(30, 40)))
        assert len(results) == 3
        ages = {r["age"] for r in results}
        assert ages == {30, 35, 40}

    def test_between_inclusive_bounds(self, table: Table) -> None:
        """Test that between is inclusive on both ends."""
        results = table.select(where=Condition(table.age.between(25, 45)))
        assert len(results) == 5  # All records

    def test_between_single_value(self, table: Table) -> None:
        """Test between with same low and high value."""
        results = table.select(where=Condition(table.age.between(30, 30)))
        assert len(results) == 1
        assert results[0]["age"] == 30

    def test_between_no_matches(self, table: Table) -> None:
        """Test between with no matching records."""
        results = table.select(where=Condition(table.age.between(100, 200)))
        assert len(results) == 0

    def test_between_with_strings(self) -> None:
        """Test between with string values."""
        t = Table("products", primary_key="id")
        t.insert({"id": 1, "code": "A100"})
        t.insert({"id": 2, "code": "B200"})
        t.insert({"id": 3, "code": "C300"})
        t.insert({"id": 4, "code": "D400"})

        results = t.select(where=Condition(t.code.between("B", "D")))
        codes = {r["code"] for r in results}
        assert codes == {"B200", "C300"}

    def test_between_with_sorted_index(self) -> None:
        """Test that between uses sorted index for optimization."""
        t = Table("indexed", primary_key="id")
        t.create_index("value", index_type="sorted")

        for i in range(100):
            t.insert({"id": i, "value": i * 10})

        results = t.select(where=Condition(t.value.between(200, 400)))
        assert len(results) == 21  # 200, 210, ..., 400
        values = sorted(r["value"] for r in results)
        assert values[0] == 200
        assert values[-1] == 400

    def test_between_with_hash_index_fallback(self) -> None:
        """Test that between works even with hash index (no optimization)."""
        t = Table("hash_indexed", primary_key="id")
        t.create_index("value", index_type="hash")

        t.insert({"id": 1, "value": 10})
        t.insert({"id": 2, "value": 20})
        t.insert({"id": 3, "value": 30})

        # Should still work, just not use the hash index
        results = t.select(where=Condition(t.value.between(15, 25)))
        assert len(results) == 1
        assert results[0]["value"] == 20

    def test_between_with_none_values(self) -> None:
        """Test that between excludes None values."""
        t = Table("nullable", primary_key="id")
        t.insert({"id": 1, "value": 10})
        t.insert({"id": 2, "value": None})
        t.insert({"id": 3, "value": 30})

        results = t.select(where=Condition(t.value.between(0, 50)))
        assert len(results) == 2
        values = {r["value"] for r in results}
        assert values == {10, 30}

    def test_between_combined_with_other_conditions(self, table: Table) -> None:
        """Test between combined with other conditions using AND."""
        results = table.select(
            where=Condition(table.age.between(25, 40) & table.name.startswith("A"))
        )
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_between_equivalent_to_compound(self, table: Table) -> None:
        """Test that between gives same results as compound condition."""
        between_results = table.select(where=Condition(table.age.between(30, 40)))
        compound_results = table.select(
            where=Condition((table.age >= 30) & (table.age <= 40))
        )

        assert len(between_results) == len(compound_results)
        between_ids = {r["id"] for r in between_results}
        compound_ids = {r["id"] for r in compound_results}
        assert between_ids == compound_ids

    def test_between_with_dates(self) -> None:
        """Test between with date strings."""
        t = Table("orders", primary_key="id")
        t.insert({"id": 1, "date": "2024-01-15"})
        t.insert({"id": 2, "date": "2024-02-20"})
        t.insert({"id": 3, "date": "2024-03-25"})
        t.insert({"id": 4, "date": "2024-04-30"})

        results = t.select(where=Condition(t.date.between("2024-02-01", "2024-03-31")))
        assert len(results) == 2
        dates = {r["date"] for r in results}
        assert dates == {"2024-02-20", "2024-03-25"}

    def test_between_with_floats(self) -> None:
        """Test between with floating point values."""
        t = Table("measurements", primary_key="id")
        t.insert({"id": 1, "value": 1.5})
        t.insert({"id": 2, "value": 2.5})
        t.insert({"id": 3, "value": 3.5})

        results = t.select(where=Condition(t.value.between(2.0, 3.0)))
        assert len(results) == 1
        assert results[0]["value"] == 2.5
