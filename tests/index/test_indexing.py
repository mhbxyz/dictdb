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
        assert 30 in idx_data and 25 in idx_data
        assert len(idx_data[30]) == 2
        assert len(idx_data[25]) == 1
    else:
        # SortedIndex: use search method.
        result_30 = index.search(30)
        result_25 = index.search(25)
        assert len(result_30) == 2
        assert len(result_25) == 1


def test_insert_updates_index(indexed_table: Table) -> None:
    """
    Tests that inserting a new record updates the index automatically.
    """
    indexed_table.insert({"id": 4, "name": "David", "age": 25})
    index = indexed_table.indexes["age"]
    if hasattr(index, "index"):
        assert len(index.index[25]) == 2
    else:
        result = index.search(25)
        assert len(result) == 2


def test_update_updates_index(indexed_table: Table) -> None:
    """
    Tests that updating an indexed field updates the index mapping.
    """
    # Update Bob's age from 25 to 30.
    updated = indexed_table.update(
        {"age": 30}, where=Condition(indexed_table.name == "Bob")
    )
    assert updated == 1
    index = indexed_table.indexes["age"]
    if hasattr(index, "index"):
        # For a hash index, key 25 should be removed.
        assert 25 not in index.index
        assert len(index.index[30]) == 3
    else:
        result_25 = index.search(25)
        result_30 = index.search(30)
        assert len(result_25) == 0
        assert len(result_30) == 3


def test_delete_updates_index(indexed_table: Table) -> None:
    """
    Tests that deleting a record removes its key from the index.
    """
    # Delete record for Alice (age 30).
    deleted = indexed_table.delete(where=Condition(indexed_table.name == "Alice"))
    assert deleted == 1
    index = indexed_table.indexes["age"]
    if hasattr(index, "index"):
        # For hash index, age 30 should have one record (Charlie remains).
        assert 30 in index.index and len(index.index[30]) == 1
    else:
        result = index.search(30)
        assert len(result) == 1


def test_select_uses_index(indexed_table: Table) -> None:
    """
    Tests that a simple equality select on an indexed field returns the correct results.
    """
    condition = Condition(indexed_table.age == 30)
    results = indexed_table.select(where=condition)
    names = {record["name"] for record in results}
    # Expected names from original records with age 30.
    assert names == {"Alice", "Charlie"}


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
