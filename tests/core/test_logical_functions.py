"""
Unit tests for And, Or, Not logical functions.
"""

import pytest

from dictdb import Table, Condition, And, Or, Not


class TestLogicalFunctions:
    """Tests for And, Or, Not functions."""

    @pytest.fixture
    def table(self) -> Table:
        """Create a table with test data."""
        t = Table("users", primary_key="id")
        t.insert({"id": 1, "name": "Alice", "age": 30, "dept": "IT", "active": True})
        t.insert({"id": 2, "name": "Bob", "age": 25, "dept": "HR", "active": True})
        t.insert({"id": 3, "name": "Charlie", "age": 35, "dept": "IT", "active": False})
        t.insert({"id": 4, "name": "Diana", "age": 28, "dept": "Sales", "active": True})
        t.insert({"id": 5, "name": "Eve", "age": 40, "dept": "IT", "active": True})
        return t

    # --- And() tests ---

    def test_and_two_conditions(self, table: Table) -> None:
        """Test And with two conditions."""
        results = table.select(where=And(table.dept == "IT", table.active == True))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Eve"}

    def test_and_three_conditions(self, table: Table) -> None:
        """Test And with three conditions."""
        results = table.select(where=And(
            table.dept == "IT",
            table.active == True,
            table.age >= 35
        ))
        assert len(results) == 1
        assert results[0]["name"] == "Eve"

    def test_and_many_conditions(self, table: Table) -> None:
        """Test And with many conditions."""
        results = table.select(where=And(
            table.dept == "IT",
            table.active == True,
            table.age >= 30,
            table.age <= 40,
            table.name.startswith("A")
        ))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_and_no_matches(self, table: Table) -> None:
        """Test And returning no results."""
        results = table.select(where=And(table.dept == "IT", table.dept == "HR"))
        assert len(results) == 0

    def test_and_requires_two_operands(self, table: Table) -> None:
        """Test And raises error with less than 2 operands."""
        with pytest.raises(ValueError, match="requires at least 2 operands"):
            And(table.age >= 18)

    def test_and_with_zero_operands(self, table: Table) -> None:
        """Test And raises error with zero operands."""
        with pytest.raises(ValueError, match="requires at least 2 operands"):
            And()

    # --- Or() tests ---

    def test_or_two_conditions(self, table: Table) -> None:
        """Test Or with two conditions."""
        results = table.select(where=Or(table.dept == "IT", table.dept == "HR"))
        assert len(results) == 4

    def test_or_three_conditions(self, table: Table) -> None:
        """Test Or with three conditions."""
        results = table.select(where=Or(
            table.name == "Alice",
            table.name == "Bob",
            table.name == "Diana"
        ))
        assert len(results) == 3

    def test_or_one_match(self, table: Table) -> None:
        """Test Or where only one condition matches."""
        results = table.select(where=Or(table.name == "Alice", table.name == "Nobody"))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_or_no_matches(self, table: Table) -> None:
        """Test Or returning no results."""
        results = table.select(where=Or(table.name == "X", table.name == "Y"))
        assert len(results) == 0

    def test_or_requires_two_operands(self, table: Table) -> None:
        """Test Or raises error with less than 2 operands."""
        with pytest.raises(ValueError, match="requires at least 2 operands"):
            Or(table.age >= 18)

    # --- Not() tests ---

    def test_not_basic(self, table: Table) -> None:
        """Test Not with basic condition."""
        results = table.select(where=Not(table.dept == "IT"))
        assert len(results) == 2
        depts = {r["dept"] for r in results}
        assert "IT" not in depts

    def test_not_boolean(self, table: Table) -> None:
        """Test Not with boolean field."""
        results = table.select(where=Not(table.active == True))
        assert len(results) == 1
        assert results[0]["name"] == "Charlie"

    def test_not_with_comparison(self, table: Table) -> None:
        """Test Not with comparison operator."""
        results = table.select(where=Not(table.age >= 30))
        assert len(results) == 2
        ages = {r["age"] for r in results}
        assert all(age < 30 for age in ages)

    # --- Combined tests ---

    def test_and_or_combined(self, table: Table) -> None:
        """Test And containing Or."""
        results = table.select(where=And(
            Or(table.dept == "IT", table.dept == "HR"),
            table.active == True
        ))
        assert len(results) == 3
        names = {r["name"] for r in results}
        assert names == {"Alice", "Bob", "Eve"}

    def test_or_and_combined(self, table: Table) -> None:
        """Test Or containing And."""
        results = table.select(where=Or(
            And(table.dept == "IT", table.age >= 35),
            table.dept == "Sales"
        ))
        assert len(results) == 3
        names = {r["name"] for r in results}
        assert names == {"Charlie", "Diana", "Eve"}

    def test_and_with_not(self, table: Table) -> None:
        """Test And with Not."""
        results = table.select(where=And(
            table.dept == "IT",
            Not(table.active == False)
        ))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Eve"}

    def test_complex_nested(self, table: Table) -> None:
        """Test complex nested logical operations."""
        results = table.select(where=And(
            Or(table.dept == "IT", table.dept == "Sales"),
            table.age >= 28,
            Not(table.active == False)
        ))
        assert len(results) == 3
        names = {r["name"] for r in results}
        assert names == {"Alice", "Diana", "Eve"}

    def test_deeply_nested(self, table: Table) -> None:
        """Test deeply nested logical operations."""
        results = table.select(where=Or(
            And(
                table.dept == "IT",
                Or(table.age < 32, table.age > 38)
            ),
            And(
                table.dept == "Sales",
                table.active == True
            )
        ))
        assert len(results) == 3
        names = {r["name"] for r in results}
        assert names == {"Alice", "Diana", "Eve"}

    # --- With Condition wrapper tests ---

    def test_and_with_condition_operands(self, table: Table) -> None:
        """Test And accepts Condition objects."""
        cond1 = Condition(table.dept == "IT")
        cond2 = Condition(table.active == True)
        results = table.select(where=And(cond1, cond2))
        assert len(results) == 2

    def test_or_with_condition_operands(self, table: Table) -> None:
        """Test Or accepts Condition objects."""
        cond1 = Condition(table.dept == "IT")
        cond2 = Condition(table.dept == "HR")
        results = table.select(where=Or(cond1, cond2))
        assert len(results) == 4

    def test_not_with_condition_operand(self, table: Table) -> None:
        """Test Not accepts Condition object."""
        cond = Condition(table.dept == "IT")
        results = table.select(where=Not(cond))
        assert len(results) == 2

    def test_mixed_predicateexpr_and_condition(self, table: Table) -> None:
        """Test mixing PredicateExpr and Condition in same call."""
        cond = Condition(table.active == True)
        results = table.select(where=And(table.dept == "IT", cond))
        assert len(results) == 2

    # --- Error handling ---

    def test_and_invalid_type(self, table: Table) -> None:
        """Test And raises error with invalid type."""
        with pytest.raises(TypeError, match="Expected PredicateExpr or Condition"):
            And(table.age >= 18, "invalid")  # type: ignore

    def test_or_invalid_type(self, table: Table) -> None:
        """Test Or raises error with invalid type."""
        with pytest.raises(TypeError, match="Expected PredicateExpr or Condition"):
            Or("invalid", table.age >= 18)  # type: ignore

    def test_not_invalid_type(self) -> None:
        """Test Not raises error with invalid type."""
        with pytest.raises(TypeError, match="Expected PredicateExpr or Condition"):
            Not("invalid")  # type: ignore

    # --- With update/delete ---

    def test_and_in_update(self, table: Table) -> None:
        """Test And works in update."""
        count = table.update({"active": False}, where=And(table.dept == "IT", table.age < 35))
        assert count == 1
        alice = table.select(where=table.name == "Alice")[0]
        assert alice["active"] is False

    def test_or_in_delete(self, table: Table) -> None:
        """Test Or works in delete."""
        count = table.delete(where=Or(table.name == "Alice", table.name == "Bob"))
        assert count == 2
        assert table.count() == 3
