import pytest
from dictdb import DictDB, Table

@pytest.fixture
def table() -> Table:
    """
    Returns a Table instance named 'test_table' with a primary key 'id'.
    Two records are pre-inserted for testing purposes.
    """
    tbl = Table("test_table", primary_key="id")
    tbl.insert_record({"id": 1, "name": "Alice", "age": 30})
    tbl.insert_record({"id": 2, "name": "Bob", "age": 25})
    return tbl

@pytest.fixture
def db() -> DictDB:
    """
    Returns a DictDB instance with two tables: 'users' and 'products'.
    """
    database = DictDB()
    database.create_table("users")
    database.create_table("products")
    return database
