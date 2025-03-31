"""
This module contains unit tests for the transaction management features
of DictDB, specifically testing begin_transaction(), commit_transaction(), and rollback_transaction().
"""

import pytest
from dictdb import DictDB, Table, Query
from dictdb.exceptions import TransactionError  # Updated import

def test_transaction_commit() -> None:
    """
    Tests that changes made during a transaction are persisted after commit.
    """
    db = DictDB()
    db.create_table("test")
    table: Table = db.get_table("test")
    table.insert({"id": 1, "name": "Alice", "age": 30})

    db.begin_transaction()
    # Insert a new record and update an existing one.
    table.insert({"id": 2, "name": "Bob", "age": 25})
    table.update({"age": 31}, where=Query(table.id == 1))
    db.commit_transaction()

    # Verify that the new record and update persist.
    records = table.select()
    assert len(records) == 2
    alice = next((rec for rec in records if rec["id"] == 1), None)
    assert alice is not None and alice["age"] == 31

def test_transaction_rollback() -> None:
    """
    Tests that changes made during a transaction are discarded after a rollback.
    """
    db = DictDB()
    db.create_table("test")
    table: Table = db.get_table("test")
    table.insert({"id": 1, "name": "Alice", "age": 30})

    db.begin_transaction()
    table.insert({"id": 2, "name": "Bob", "age": 25})
    table.update({"age": 31}, where=Query(table.id == 1))
    db.rollback_transaction()

    # Verify that the database state remains unchanged.
    records = table.select()
    assert len(records) == 1
    alice = records[0]
    assert alice["id"] == 1 and alice["age"] == 30

def test_transaction_commit_without_begin() -> None:
    """
    Tests that committing without an active transaction raises an error.
    """
    db = DictDB()
    with pytest.raises(TransactionError):
        db.commit_transaction()

def test_transaction_rollback_without_begin() -> None:
    """
    Tests that rolling back without an active transaction raises an error.
    """
    db = DictDB()
    with pytest.raises(TransactionError):
        db.rollback_transaction()

def test_nested_transaction_error() -> None:
    """
    Tests that beginning a new transaction while one is already in progress raises an error.
    """
    db = DictDB()
    db.begin_transaction()
    with pytest.raises(TransactionError):
        db.begin_transaction()
    db.rollback_transaction()

def test_new_table_creation_in_transaction_rollback() -> None:
    """
    Tests that a table created during a transaction is removed after a rollback.
    """
    db = DictDB()
    db.create_table("test")
    table: Table = db.get_table("test")
    table.insert({"id": 1, "name": "Alice", "age": 30})

    db.begin_transaction()
    db.create_table("new_table")
    new_table: Table = db.get_table("new_table")
    new_table.insert({"id": 1, "data": "dummy"})
    db.rollback_transaction()

    with pytest.raises(ValueError):
        db.get_table("new_table")
