import pytest
from dictdb import DictDB, Table, Query, DuplicateKeyError, RecordNotFoundError


# ----------------------------
# Tests for Field, Condition, and Query functionality
# ----------------------------

def test_field_equality(table: Table) -> None:
    # Wrap the condition in Query so that it can be used without triggering
    # implicit boolean conversion errors.
    condition = Query(table.name == "Alice")
    record = {"name": "Alice"}
    assert condition(record) is True
    record = {"name": "Bob"}
    assert condition(record) is False


def test_comparison_operators(table: Table) -> None:
    eq_cond = Query(table.age == 30)
    ne_cond = Query(table.age != 30)
    lt_cond = Query(table.age < 30)
    le_cond = Query(table.age <= 30)
    gt_cond = Query(table.age > 30)
    ge_cond = Query(table.age >= 30)

    record = {"age": 30}
    assert eq_cond(record)
    assert not ne_cond(record)
    assert not lt_cond(record)
    assert le_cond(record)
    assert not gt_cond(record)
    assert ge_cond(record)

    record = {"age": 25}
    assert not eq_cond(record)
    assert ne_cond(record)
    assert lt_cond(record)
    assert le_cond(record)
    assert not gt_cond(record)
    assert not ge_cond(record)


def test_logical_operators(table: Table) -> None:
    # Logical AND: (name == "Alice") AND (age > 25)
    condition = Query((table.name == "Alice") & (table.age > 25))
    record = {"name": "Alice", "age": 30}
    assert condition(record)
    record = {"name": "Alice", "age": 20}
    assert not condition(record)

    # Logical OR: (name == "Alice") OR (age > 25)
    condition = Query((table.name == "Alice") | (table.age > 25))
    record = {"name": "Bob", "age": 30}
    assert condition(record)
    record = {"name": "Alice", "age": 20}
    assert condition(record)
    record = {"name": "Bob", "age": 20}
    assert not condition(record)

    # Logical NOT: NOT (name == "Alice")
    condition = Query(~(table.name == "Alice"))
    record = {"name": "Bob"}
    assert condition(record)
    record = {"name": "Alice"}
    assert not condition(record)


# ----------------------------
# Tests for Table CRUD Operations
# ----------------------------

def test_insert_valid_record(table: Table) -> None:
    table.insert_record({"id": 3, "name": "Charlie", "age": 40})
    records = table.select_records()
    assert len(records) == 3


def test_insert_missing_primary_key(table: Table) -> None:
    with pytest.raises(ValueError):
        table.insert_record({"name": "David", "age": 35})


def test_insert_duplicate_key(table: Table) -> None:
    with pytest.raises(DuplicateKeyError):
        table.insert_record({"id": 1, "name": "Eve", "age": 28})


def test_select_no_where(table: Table) -> None:
    records = table.select_records()
    assert len(records) == 2


def test_select_with_where(table: Table) -> None:
    condition = Query(table.name == "Alice")
    records = table.select_records(where=condition)
    assert len(records) == 1
    assert records[0]["name"] == "Alice"


def test_select_with_columns(table: Table) -> None:
    records = table.select_records(columns=["name"], where=Query(table.age >= 25))
    for rec in records:
        assert "name" in rec
        assert "age" not in rec


def test_update_records(table: Table) -> None:
    updated = table.update_records({"age": 26}, where=Query(table.name == "Bob"))
    assert updated == 1
    records = table.select_records(where=Query(table.name == "Bob"))
    assert records[0]["age"] == 26


def test_update_no_match(table: Table) -> None:
    with pytest.raises(RecordNotFoundError):
        table.update_records({"age": 35}, where=Query(table.name == "Nonexistent"))


def test_delete_records(table: Table) -> None:
    deleted = table.delete_records(where=Query(table.name == "Bob"))
    assert deleted == 1
    records = table.select_records()
    assert len(records) == 1


def test_delete_no_match(table: Table) -> None:
    with pytest.raises(RecordNotFoundError):
        table.delete_records(where=Query(table.name == "Nonexistent"))


# ----------------------------
# Tests for DictDB Operations
# ----------------------------

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
    users.insert_record({"id": 1, "name": "Alice"})
    products = db.get_table("products")
    products.insert_record({"id": 101, "name": "Widget"})
    assert len(users.select_records()) == 1
    assert len(products.select_records()) == 1
