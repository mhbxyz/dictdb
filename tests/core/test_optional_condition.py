"""
Unit tests for optional Condition wrapper feature.

Tests that PredicateExpr can be passed directly to where= parameters
without wrapping in Condition().
"""

import pytest

from dictdb import Table, Condition, Count


class TestOptionalCondition:
    """Tests for using PredicateExpr directly in queries."""

    @pytest.fixture
    def table(self) -> Table:
        """Create a table with test data."""
        t = Table("users", primary_key="id")
        t.insert({"id": 1, "name": "Alice", "age": 30, "department": "IT"})
        t.insert({"id": 2, "name": "Bob", "age": 25, "department": "HR"})
        t.insert({"id": 3, "name": "Charlie", "age": 35, "department": "IT"})
        t.insert({"id": 4, "name": "Diana", "age": 28, "department": "Sales"})
        return t

    # --- select() tests ---

    def test_select_without_condition_wrapper(self, table: Table) -> None:
        """Test select with PredicateExpr directly (no Condition wrapper)."""
        results = table.select(where=table.age >= 30)
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Charlie"}

    def test_select_with_condition_wrapper(self, table: Table) -> None:
        """Test select with Condition wrapper still works."""
        results = table.select(where=Condition(table.age >= 30))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Charlie"}

    def test_select_compound_without_wrapper(self, table: Table) -> None:
        """Test compound conditions without Condition wrapper."""
        results = table.select(where=(table.department == "IT") & (table.age >= 30))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Charlie"}

    def test_select_or_without_wrapper(self, table: Table) -> None:
        """Test OR conditions without Condition wrapper."""
        results = table.select(
            where=(table.department == "IT") | (table.department == "HR")
        )
        assert len(results) == 3

    def test_select_not_without_wrapper(self, table: Table) -> None:
        """Test NOT conditions without Condition wrapper."""
        results = table.select(where=~(table.department == "IT"))
        assert len(results) == 2
        departments = {r["department"] for r in results}
        assert "IT" not in departments

    def test_select_is_in_without_wrapper(self, table: Table) -> None:
        """Test is_in without Condition wrapper."""
        results = table.select(where=table.department.is_in(["IT", "Sales"]))
        assert len(results) == 3

    def test_select_between_without_wrapper(self, table: Table) -> None:
        """Test between without Condition wrapper."""
        results = table.select(where=table.age.between(25, 30))
        assert len(results) == 3

    def test_select_like_without_wrapper(self, table: Table) -> None:
        """Test like without Condition wrapper."""
        results = table.select(where=table.name.like("A%"))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_select_iequals_without_wrapper(self, table: Table) -> None:
        """Test iequals without Condition wrapper."""
        results = table.select(where=table.name.iequals("ALICE"))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    # --- update() tests ---

    def test_update_without_condition_wrapper(self, table: Table) -> None:
        """Test update with PredicateExpr directly."""
        count = table.update(
            {"department": "Engineering"}, where=table.department == "IT"
        )
        assert count == 2
        results = table.select(where=table.department == "Engineering")
        assert len(results) == 2

    def test_update_with_condition_wrapper(self, table: Table) -> None:
        """Test update with Condition wrapper still works."""
        count = table.update(
            {"department": "Engineering"}, where=Condition(table.department == "IT")
        )
        assert count == 2

    # --- delete() tests ---

    def test_delete_without_condition_wrapper(self, table: Table) -> None:
        """Test delete with PredicateExpr directly."""
        count = table.delete(where=table.department == "Sales")
        assert count == 1
        assert table.count() == 3

    def test_delete_with_condition_wrapper(self, table: Table) -> None:
        """Test delete with Condition wrapper still works."""
        count = table.delete(where=Condition(table.department == "Sales"))
        assert count == 1

    # --- aggregate() tests ---

    def test_aggregate_without_condition_wrapper(self, table: Table) -> None:
        """Test aggregate with PredicateExpr directly."""
        result = table.aggregate(where=table.department == "IT", count=Count())
        assert isinstance(result, dict)
        assert result["count"] == 2

    def test_aggregate_with_condition_wrapper(self, table: Table) -> None:
        """Test aggregate with Condition wrapper still works."""
        result = table.aggregate(
            where=Condition(table.department == "IT"), count=Count()
        )
        assert isinstance(result, dict)
        assert result["count"] == 2

    # --- Error handling ---

    def test_invalid_where_type_raises_error(self, table: Table) -> None:
        """Test that invalid where type raises TypeError."""
        with pytest.raises(TypeError, match="must be a Condition or PredicateExpr"):
            table.select(where="invalid")  # type: ignore

    def test_invalid_where_type_in_update(self, table: Table) -> None:
        """Test that invalid where type in update raises TypeError."""
        with pytest.raises(TypeError, match="must be a Condition or PredicateExpr"):
            table.update({"name": "Test"}, where=123)  # type: ignore

    def test_invalid_where_type_in_delete(self, table: Table) -> None:
        """Test that invalid where type in delete raises TypeError."""
        with pytest.raises(TypeError, match="must be a Condition or PredicateExpr"):
            table.delete(where=[1, 2, 3])  # type: ignore

    # --- Index optimization still works ---

    def test_index_optimization_without_wrapper(self, table: Table) -> None:
        """Test that index optimization works without Condition wrapper."""
        table.create_index("department", "hash")
        results = table.select(where=table.department == "IT")
        assert len(results) == 2

    def test_sorted_index_range_without_wrapper(self, table: Table) -> None:
        """Test that sorted index range queries work without wrapper."""
        table.create_index("age", "sorted")
        results = table.select(where=table.age >= 30)
        assert len(results) == 2
