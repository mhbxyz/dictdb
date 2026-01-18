import pytest

from dictdb import DictDB, Table, TableNotFoundError


def test_create_and_list_tables(db: DictDB) -> None:
    """
    Tests creating tables and listing them in the database.

    :param db: A DictDB fixture with prepopulated tables.
    :type db: DictDB
    :return: None
    :rtype: None
    """
    tables = db.list_tables()
    assert "users" in tables
    assert "products" in tables


def test_get_table(db: DictDB) -> None:
    """
    Tests retrieving a table by name from the database.

    :param db: A DictDB fixture with prepopulated tables.
    :type db: DictDB
    :return: None
    :rtype: None
    """
    users_table = db.get_table("users")
    assert isinstance(users_table, Table)


def test_drop_table(db: DictDB) -> None:
    """
    Tests dropping an existing table from the database.

    :param db: A DictDB fixture with prepopulated tables.
    :type db: DictDB
    :return: None
    :rtype: None
    """
    db.drop_table("products")
    tables = db.list_tables()
    assert "products" not in tables
    with pytest.raises(TableNotFoundError):
        db.get_table("products")


def test_drop_nonexistent_table(db: DictDB) -> None:
    """
    Tests that dropping a nonexistent table raises TableNotFoundError.

    :param db: A DictDB fixture with prepopulated tables.
    :type db: DictDB
    :return: None
    :rtype: None
    """
    with pytest.raises(TableNotFoundError):
        db.drop_table("nonexistent")


def test_multiple_tables_independence(db: DictDB) -> None:
    """
    Tests that inserting records into one table does not affect other tables in the database.

    :param db: A DictDB fixture with prepopulated tables.
    :type db: DictDB
    :return: None
    :rtype: None
    """
    users = db.get_table("users")
    users.insert({"id": 1, "name": "Alice"})
    products = db.get_table("products")
    products.insert({"id": 101, "name": "Widget"})
    assert len(users.select()) == 1
    assert len(products.select()) == 1
