import pytest
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
def log_capture():
    """
    Creates a fixture that captures Loguru log messages in a list.

    This fixture can be used in tests to verify that certain log messages were emitted.

    :return: A list that will be populated with log messages.
    :rtype: list
    """
    logs = []

    def sink_function(message):
        # Each 'message' here is a loguru Message object in string form
        logs.append(str(message))

    # Remove existing sinks to avoid duplicates (important for test isolation).
    logger.remove()

    # Add the capture sink at a high level (e.g. DEBUG) so we see everything.
    logger.add(sink_function, level="DEBUG")

    yield logs

    # Remove the capture sink after test completes (cleanup).
    logger.remove()
