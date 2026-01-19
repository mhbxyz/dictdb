from pathlib import Path
from typing import List, Iterator

import pytest
from _pytest.fixtures import FixtureRequest

from dictdb import DictDB, Table, logger


@pytest.fixture
def table() -> Table:
    """
    Returns a Table instance named 'test_table' with a primary key 'id'.
    Two records are pre-inserted for testing purposes.

    :return: A prepopulated Table instance.
    :rtype: Table
    """
    tbl = Table("test_table", primary_key="id")
    tbl.insert({"id": 1, "name": "Alice", "age": 30})
    tbl.insert({"id": 2, "name": "Bob", "age": 25})
    return tbl


@pytest.fixture
def db() -> DictDB:
    """
    Returns a DictDB instance with two tables: 'users' and 'products'.

    :return: A DictDB instance with 'users' and 'products' tables.
    :rtype: DictDB
    """
    database = DictDB()
    database.create_table("users")
    database.create_table("products")
    return database


@pytest.fixture
def log_capture() -> Iterator[List[str]]:
    """
    Creates a fixture that captures Loguru log messages in a list.

    This fixture can be used in tests to verify that certain log messages were emitted.

    :return: A list that will be populated with log messages.
    :rtype: list
    """
    logs = []

    def sink_function(message: str) -> None:
        # Each 'message' here is a loguru Message object in string form
        logs.append(str(message))

    # Remove existing sinks to avoid duplicates (important for test isolation).
    logger.remove()

    # Add the capture sink at a high level (e.g. DEBUG) so we see everything.
    logger.add(sink_function, level="DEBUG")

    yield logs

    # Remove the capture sink after test completes (cleanup).
    logger.remove()


@pytest.fixture
def test_db(tmp_path: Path) -> DictDB:
    """
    Creates a DictDB instance with a test table and a single record for backup tests.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :return: A DictDB instance.
    :rtype: DictDB
    """
    db = DictDB()
    db.create_table("backup_test")
    table = db.get_table("backup_test")
    table.insert({"id": 1, "name": "Test", "age": 100})
    return db


@pytest.fixture(params=["hash", "sorted"])
def indexed_table(request: FixtureRequest) -> Table:
    """
    Returns a Table instance prepopulated with records and an index on the 'age' field.
    The index type is parameterized to test both "hash" and "sorted" implementations.

    :param request: The pytest fixture request object.
    :return: A prepopulated Table instance.
    """
    table = Table(
        "people", primary_key="id", schema={"id": int, "name": str, "age": int}
    )
    table.insert({"id": 1, "name": "Alice", "age": 30})
    table.insert({"id": 2, "name": "Bob", "age": 25})
    table.insert({"id": 3, "name": "Charlie", "age": 30})
    table.create_index("age", index_type=request.param)
    return table


@pytest.fixture
def people_table() -> Table:
    """
    Returns a Table instance named 'people' with a schema and prepopulated records.
    Useful for tests that need a standard table setup.

    :return: A prepopulated Table instance with 3 records.
    """
    table = Table(
        "people", primary_key="id", schema={"id": int, "name": str, "age": int}
    )
    table.insert({"id": 1, "name": "Alice", "age": 30})
    table.insert({"id": 2, "name": "Bob", "age": 25})
    table.insert({"id": 3, "name": "Charlie", "age": 30})
    return table


class FailingDB(DictDB):
    """A DictDB subclass that raises RuntimeError on save() for testing failure handling."""

    def save(self, filename: str, file_format: str) -> None:  # type: ignore[override]
        raise RuntimeError("Simulated save failure")


@pytest.fixture
def failing_db() -> FailingDB:
    """
    Returns a FailingDB instance that always raises RuntimeError on save().
    Useful for testing error handling in backup operations.

    :return: A FailingDB instance.
    """
    return FailingDB()
