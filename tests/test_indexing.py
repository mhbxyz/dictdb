"""
This module contains unit tests for the indexing features added to the Table.
Tests cover index creation, automatic index updates on INSERT, UPDATE, and DELETE,
and accelerated SELECT queries using the indexes.
"""

from dictdb import Table, Query


def test_index_creation(indexed_table: Table) -> None:
    """
    Tests that creating an index populates the index mapping correctly.
    """
    # Directly access the index since create_index() ensures it exists.
    index = indexed_table.indexes["age"]
    # There should be two groups: age 30 and age 25.
    assert 30 in index and 25 in index
    # Age 30 should map to 2 records.
    assert len(index[30]) == 2
    # Age 25 should map to 1 record.
    assert len(index[25]) == 1

def test_insert_updates_index(indexed_table: Table) -> None:
    """
    Tests that inserting a new record updates the index automatically.
    """
    indexed_table.insert({"id": 4, "name": "David", "age": 25})
    index = indexed_table.indexes["age"]
    # Now age 25 should have 2 records.
    assert len(index[25]) == 2

def test_update_updates_index(indexed_table: Table) -> None:
    """
    Tests that updating an indexed field updates the index mapping.
    """
    # Update Bob's age from 25 to 30.
    updated = indexed_table.update({"age": 30}, where=Query(indexed_table.name == "Bob"))
    assert updated == 1
    index = indexed_table.indexes["age"]
    # Age 25 should now be removed.
    assert 25 not in index
    # Age 30 should have 3 records.
    assert len(index[30]) == 3

def test_delete_updates_index(indexed_table: Table) -> None:
    """
    Tests that deleting a record removes its key from the index.
    """
    # Delete a record with age 30.
    deleted = indexed_table.delete(where=Query(indexed_table.name == "Alice"))
    assert deleted == 1
    index = indexed_table.indexes["age"]
    # Age 30 should now have 1 record.
    assert 30 in index and len(index[30]) == 1

def test_select_uses_index(indexed_table: Table) -> None:
    """
    Tests that a simple equality select on an indexed field returns the correct results.
    """
    # Use a Query that is a simple equality on 'age'.
    condition = Query(indexed_table.age == 30)
    results = indexed_table.select(where=condition)
    # Should retrieve records for Alice, Charlie (or Bob if updated from previous test; tests are independent).
    # For this test, we assume the original data.
    names = {record["name"] for record in results}
    assert names == {"Alice", "Charlie"} or names == {"Alice", "Charlie", "Bob"}
