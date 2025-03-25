import pytest
from dictdb import DictDB, Table, Query, DuplicateKeyError, RecordNotFoundError, SchemaValidationError


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
    """
    Inserting a record with an explicit primary key should still work.
    """
    table.insert({"id": 3, "name": "Charlie", "age": 40})
    records = table.select()
    assert len(records) == 3


def test_insert_auto_assign_primary_key(table: Table) -> None:
    """
    Inserts a record without a primary key and checks that an auto-assigned key is added.
    In the fixture, the table already has keys 1 and 2, so the new record should be assigned key 3.
    """
    new_record = {"name": "David", "age": 35}
    table.insert(new_record)
    # Verify that the primary key was auto-assigned.
    assert "id" in new_record
    assert new_record["id"] == 3
    # Confirm the record is retrievable via the auto-assigned key.
    records = table.select(where=Query(table.id == new_record["id"]))
    assert len(records) == 1


def test_insert_duplicate_key(table: Table) -> None:
    """
    Inserting a record with an explicit duplicate primary key should raise a DuplicateKeyError.
    """
    with pytest.raises(DuplicateKeyError):
        table.insert({"id": 1, "name": "Eve", "age": 28})


def test_select_no_where(table: Table) -> None:
    records = table.select()
    assert len(records) == 2


def test_select_with_where(table: Table) -> None:
    condition = Query(table.name == "Alice")
    records = table.select(where=condition)
    assert len(records) == 1
    assert records[0]["name"] == "Alice"


def test_select_with_columns(table: Table) -> None:
    records = table.select(columns=["name"], where=Query(table.age >= 25))
    for rec in records:
        assert "name" in rec
        assert "age" not in rec


def test_update_records(table: Table) -> None:
    updated = table.update({"age": 26}, where=Query(table.name == "Bob"))
    assert updated == 1
    records = table.select(where=Query(table.name == "Bob"))
    assert records[0]["age"] == 26


def test_update_no_match(table: Table) -> None:
    with pytest.raises(RecordNotFoundError):
        table.update({"age": 35}, where=Query(table.name == "Nonexistent"))


def test_delete_records(table: Table) -> None:
    deleted = table.delete(where=Query(table.name == "Bob"))
    assert deleted == 1
    records = table.select()
    assert len(records) == 1


def test_delete_no_match(table: Table) -> None:
    with pytest.raises(RecordNotFoundError):
        table.delete(where=Query(table.name == "Nonexistent"))


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
    users.insert({"id": 1, "name": "Alice"})
    products = db.get_table("products")
    products.insert({"id": 101, "name": "Widget"})
    assert len(users.select()) == 1
    assert len(products.select()) == 1


# ----------------------------
# New Tests for Schema Validation
# ----------------------------

def test_insert_valid_record_with_schema() -> None:
    """
    Test inserting a valid record into a table with a defined schema.
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    table.insert({"id": 1, "name": "Alice", "age": 30})
    records = table.select()
    assert len(records) == 1

def test_insert_missing_field_in_schema() -> None:
    """
    Test inserting a record missing a field defined in the schema.
    Expect SchemaValidationError.
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    with pytest.raises(SchemaValidationError):
        table.insert({"id": 1, "name": "Alice"})  # Missing 'age'

def test_insert_extra_field_not_in_schema() -> None:
    """
    Test inserting a record with an extra field not defined in the schema.
    Expect SchemaValidationError.
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    with pytest.raises(SchemaValidationError):
        table.insert({"id": 1, "name": "Alice", "age": 30, "extra": "value"})

def test_insert_wrong_type_field_in_schema() -> None:
    """
    Test inserting a record where a field does not match the expected type.
    Expect SchemaValidationError.
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    with pytest.raises(SchemaValidationError):
        table.insert({"id": 1, "name": "Alice", "age": "30"})  # 'age' should be int

def test_auto_assign_primary_key_with_schema() -> None:
    """
    Test auto-assignment of the primary key for a table with a defined schema.
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    new_record = {"name": "Bob", "age": 25}
    table.insert(new_record)
    assert "id" in new_record and isinstance(new_record["id"], int)
    records = table.select(where=Query(table.id == new_record["id"]))
    assert len(records) == 1
