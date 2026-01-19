"""
This module contains unit tests for the indexing features added to the Table.
Tests cover index creation, automatic index updates on INSERT, UPDATE, and DELETE,
and accelerated SELECT queries using the indexes.
"""

from typing import Dict, Any

import pytest

from dictdb import Table, Condition


def test_index_creation(indexed_table: Table) -> None:
    """
    Tests that creating an index populates the index mapping correctly.
    """
    index = indexed_table.indexes["age"]
    # For a hash index, check the internal dict; for sorted, use search().
    if hasattr(index, "index"):
        # HashIndex: verify internal mapping.
        idx_data: Dict[Any, Any] = index.index
        assert 30 in idx_data and 25 in idx_data, "Index should contain ages 30 and 25"
        assert len(idx_data[30]) == 2, "Age 30 should have 2 records (Alice, Charlie)"
        assert len(idx_data[25]) == 1, "Age 25 should have 1 record (Bob)"
    else:
        # SortedIndex: use search method.
        result_30 = index.search(30)
        result_25 = index.search(25)
        assert len(result_30) == 2, "SortedIndex search for 30 should find 2 records"
        assert len(result_25) == 1, "SortedIndex search for 25 should find 1 record"


def test_insert_updates_index(indexed_table: Table) -> None:
    """
    Tests that inserting a new record updates the index automatically.
    """
    indexed_table.insert({"id": 4, "name": "David", "age": 25})
    index = indexed_table.indexes["age"]
    if hasattr(index, "index"):
        assert len(index.index[25]) == 2, (
            "Index should reflect new insert (2 records at age 25)"
        )
    else:
        result = index.search(25)
        assert len(result) == 2, "SortedIndex should reflect new insert"


def test_update_updates_index(indexed_table: Table) -> None:
    """
    Tests that updating an indexed field updates the index mapping.
    """
    # Update Bob's age from 25 to 30.
    updated = indexed_table.update(
        {"age": 30}, where=Condition(indexed_table.name == "Bob")
    )
    assert updated == 1, "UPDATE should affect exactly 1 record"
    index = indexed_table.indexes["age"]
    if hasattr(index, "index"):
        # For a hash index, key 25 should be removed.
        assert 25 not in index.index, "Age 25 should be removed from index after update"
        assert len(index.index[30]) == 3, "Age 30 should now have 3 records"
    else:
        result_25 = index.search(25)
        result_30 = index.search(30)
        assert len(result_25) == 0, "No records should remain at age 25"
        assert len(result_30) == 3, "Age 30 should now have 3 records"


def test_delete_updates_index(indexed_table: Table) -> None:
    """
    Tests that deleting a record removes its key from the index.
    """
    # Delete record for Alice (age 30).
    deleted = indexed_table.delete(where=Condition(indexed_table.name == "Alice"))
    assert deleted == 1, "DELETE should affect exactly 1 record"
    index = indexed_table.indexes["age"]
    if hasattr(index, "index"):
        # For hash index, age 30 should have one record (Charlie remains).
        assert 30 in index.index and len(index.index[30]) == 1, (
            "Age 30 should have 1 record remaining (Charlie)"
        )
    else:
        result = index.search(30)
        assert len(result) == 1, "SortedIndex should have 1 record at age 30"


def test_select_uses_index(indexed_table: Table) -> None:
    """
    Tests that a simple equality select on an indexed field returns the correct results.
    """
    condition = Condition(indexed_table.age == 30)
    results = indexed_table.select(where=condition)
    names = {record["name"] for record in results}
    # Expected names from original records with age 30.
    assert names == {"Alice", "Charlie"}


# --- Tests for extended index optimizations ---


def test_sorted_index_range_queries() -> None:
    """Test range queries (<, <=, >, >=) on SortedIndex."""
    table = Table("employees", primary_key="id")
    for i in range(1, 11):
        table.insert({"id": i, "salary": i * 10000})
    table.create_index("salary", index_type="sorted")

    # Test < (less than)
    results = table.select(where=Condition(table.salary < 30000))
    salaries = {r["salary"] for r in results}
    assert salaries == {10000, 20000}

    # Test <= (less than or equal)
    results = table.select(where=Condition(table.salary <= 30000))
    salaries = {r["salary"] for r in results}
    assert salaries == {10000, 20000, 30000}

    # Test > (greater than)
    results = table.select(where=Condition(table.salary > 80000))
    salaries = {r["salary"] for r in results}
    assert salaries == {90000, 100000}

    # Test >= (greater than or equal)
    results = table.select(where=Condition(table.salary >= 80000))
    salaries = {r["salary"] for r in results}
    assert salaries == {80000, 90000, 100000}


def test_is_in_uses_index() -> None:
    """Test that is_in condition uses index for multiple lookups."""
    table = Table("products", primary_key="id")
    for i in range(1, 21):
        table.insert({"id": i, "category": f"cat_{i % 5}"})
    table.create_index("category", index_type="hash")

    # is_in should use the index
    results = table.select(where=Condition(table.category.is_in(["cat_0", "cat_1"])))
    categories = {r["category"] for r in results}
    assert categories == {"cat_0", "cat_1"}, (
        "is_in should return only specified categories"
    )
    assert len(results) == 8, "Expected 8 records (4 per category)"


def test_and_condition_uses_index() -> None:
    """Test that AND conditions use index for the first indexable condition."""
    table = Table("orders", primary_key="id")
    for i in range(1, 101):
        table.insert(
            {
                "id": i,
                "status": "pending" if i % 2 == 0 else "completed",
                "amount": i * 10,
            }
        )
    table.create_index("status", index_type="hash")

    # AND condition: status == 'pending' AND amount > 500
    # Should use index on status first, then filter by amount
    cond = Condition(table.status == "pending") & Condition(table.amount > 500)
    results = table.select(where=cond)
    assert all(r["status"] == "pending" and r["amount"] > 500 for r in results)
    # pending = even ids (50 records), amount > 500 = id > 50, so even ids 52-100 = 25
    assert len(results) == 25


def test_update_uses_index() -> None:
    """Test that UPDATE uses index for faster filtering."""
    table = Table("users", primary_key="id")
    for i in range(1, 101):
        table.insert(
            {"id": i, "role": "user" if i % 10 != 0 else "admin", "active": True}
        )
    table.create_index("role", index_type="hash")

    # Update using indexed condition
    count = table.update({"active": False}, where=Condition(table.role == "admin"))
    assert count == 10

    # Verify the update
    admins = table.select(where=Condition(table.role == "admin"))
    assert all(not r["active"] for r in admins)


def test_delete_uses_index() -> None:
    """Test that DELETE uses index for faster filtering."""
    table = Table("logs", primary_key="id")
    for i in range(1, 101):
        table.insert({"id": i, "level": "error" if i % 10 == 0 else "info"})
    table.create_index("level", index_type="hash")

    initial_count = table.count()
    assert initial_count == 100

    # Delete using indexed condition
    count = table.delete(where=Condition(table.level == "error"))
    assert count == 10

    # Verify the deletion
    remaining = table.select(where=Condition(table.level == "error"))
    assert len(remaining) == 0
    assert table.count() == 90


def test_range_query_update() -> None:
    """Test UPDATE with range condition on SortedIndex."""
    table = Table("inventory", primary_key="id")
    for i in range(1, 51):
        table.insert({"id": i, "quantity": i, "reorder": False})
    table.create_index("quantity", index_type="sorted")

    # Update items with quantity < 10 to set reorder flag
    count = table.update({"reorder": True}, where=Condition(table.quantity < 10))
    assert count == 9

    # Verify
    low_stock = table.select(where=Condition(table.quantity < 10))
    assert all(r["reorder"] for r in low_stock)


def test_range_query_delete() -> None:
    """Test DELETE with range condition on SortedIndex."""
    table = Table("temp_data", primary_key="id")
    for i in range(1, 51):
        table.insert({"id": i, "score": i})
    table.create_index("score", index_type="sorted")

    # Delete records with score <= 5
    count = table.delete(where=Condition(table.score <= 5))
    assert count == 5
    assert table.count() == 45


def test_index_creation_failure_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that if index creation fails, the system falls back to full table scans.

    This is simulated by monkeypatching HashIndex.insert to always raise an exception.
    After attempting to create an index on 'age', the table should not include the index,
    and queries using the condition on 'age' must still return the correct results.
    """
    from dictdb import Table, Condition
    from dictdb.index import HashIndex

    # Create a new table with schema and two records.
    table = Table(
        "test_failure", primary_key="id", schema={"id": int, "name": str, "age": int}
    )
    table.insert({"id": 1, "name": "Alice", "age": 30})
    table.insert({"id": 2, "name": "Bob", "age": 25})

    # Monkeypatch HashIndex.insert to always raise an exception.
    original_insert = HashIndex.insert

    def failing_insert(self: HashIndex, pk: int, value: int) -> None:
        raise Exception("Simulated index creation failure")

    monkeypatch.setattr(HashIndex, "insert", failing_insert)

    # Attempt to create an index on 'age' with the "hash" type.
    table.create_index("age", index_type="hash")

    # Verify that the index was not added (fallback to full scan).
    assert "age" not in table.indexes, (
        "Index should not be present after creation failure."
    )

    # Restore the original method.
    monkeypatch.setattr(HashIndex, "insert", original_insert)

    # Test that select still returns the correct result using a full scan.
    condition = Condition(table.age == 30)
    results = table.select(where=condition)
    assert len(results) == 1 and results[0]["name"] == "Alice"
