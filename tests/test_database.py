import pytest

from dictdb import DictDB, Table


def test_create_and_list_tables(db: DictDB) -> None:
    tables = db.list_tables()
    assert "users" in tables
    assert "products" in tables


def test_get_table(db: DictDB) -> None:
    users_table = db.get_table("users")
    assert isinstance(users_table, Table)


def test_drop_table(db: DictDB) -> None:
    db.drop_table("products")
    tables = db.list_tables()
    assert "products" not in tables
    with pytest.raises(ValueError):
        db.get_table("products")


def test_drop_nonexistent_table(db: DictDB) -> None:
    with pytest.raises(ValueError):
        db.drop_table("nonexistent")


def test_multiple_tables_independence(db: DictDB) -> None:
    users = db.get_table("users")
    users.insert({"id": 1, "name": "Alice"})
    products = db.get_table("products")
    products.insert({"id": 101, "name": "Widget"})
    assert len(users.select()) == 1
    assert len(products.select()) == 1
