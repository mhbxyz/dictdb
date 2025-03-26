import pytest

from dictdb import Table, Query, DuplicateKeyError, RecordNotFoundError, SchemaValidationError


def test_insert_valid_record(table: Table) -> None:
    """
    Tests inserting a record with an explicit primary key.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    table.insert({"id": 3, "name": "Charlie", "age": 40})
    records = table.select()
    assert len(records) == 3


def test_insert_auto_assign_primary_key(table: Table) -> None:
    """
    Tests inserting a record without a primary key, verifying auto-assignment of the key.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
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
    Tests that inserting a record with a duplicate primary key raises DuplicateKeyError.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    with pytest.raises(DuplicateKeyError):
        table.insert({"id": 1, "name": "Eve", "age": 28})


def test_select_no_where(table: Table) -> None:
    """
    Tests selecting all records from a table without a condition.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    records = table.select()
    assert len(records) == 2


def test_select_with_where(table: Table) -> None:
    """
    Tests selecting records from a table that match a specified condition.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    condition = Query(table.name == "Alice")
    records = table.select(where=condition)
    assert len(records) == 1
    assert records[0]["name"] == "Alice"


def test_select_with_columns(table: Table) -> None:
    """
    Tests selecting specific columns from records that satisfy a condition.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    records = table.select(columns=["name"], where=Query(table.age >= 25))
    for rec in records:
        assert "name" in rec
        assert "age" not in rec


def test_update_records(table: Table) -> None:
    """
    Tests updating records that match a condition.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    updated = table.update({"age": 26}, where=Query(table.name == "Bob"))
    assert updated == 1
    records = table.select(where=Query(table.name == "Bob"))
    assert records[0]["age"] == 26


def test_update_no_match(table: Table) -> None:
    """
    Tests that an update on records with no matches raises RecordNotFoundError.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    with pytest.raises(RecordNotFoundError):
        table.update({"age": 35}, where=Query(table.name == "Nonexistent"))


def test_delete_records(table: Table) -> None:
    """
    Tests deleting records that match a condition.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    deleted = table.delete(where=Query(table.name == "Bob"))
    assert deleted == 1
    records = table.select()
    assert len(records) == 1


def test_delete_no_match(table: Table) -> None:
    """
    Tests that deleting records with no matches raises RecordNotFoundError.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    with pytest.raises(RecordNotFoundError):
        table.delete(where=Query(table.name == "Nonexistent"))


def test_insert_valid_record_with_schema() -> None:
    """
    Tests inserting a valid record into a table with a defined schema.

    :return: None
    :rtype: None
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    table.insert({"id": 1, "name": "Alice", "age": 30})
    records = table.select()
    assert len(records) == 1


def test_insert_missing_field_in_schema() -> None:
    """
    Tests that inserting a record missing a field defined in the schema raises SchemaValidationError.

    :return: None
    :rtype: None
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    with pytest.raises(SchemaValidationError):
        table.insert({"id": 1, "name": "Alice"})  # Missing 'age'


def test_insert_extra_field_not_in_schema() -> None:
    """
    Tests that inserting a record containing extra fields not defined in the schema raises SchemaValidationError.

    :return: None
    :rtype: None
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    with pytest.raises(SchemaValidationError):
        table.insert({"id": 1, "name": "Alice", "age": 30, "extra": "value"})


def test_insert_wrong_type_field_in_schema() -> None:
    """
    Tests that inserting a record with a field of the wrong type raises SchemaValidationError.

    :return: None
    :rtype: None
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    with pytest.raises(SchemaValidationError):
        table.insert({"id": 1, "name": "Alice", "age": "30"})  # 'age' should be int


def test_auto_assign_primary_key_with_schema() -> None:
    """
    Tests auto-assigning a primary key in a table with a defined schema.

    :return: None
    :rtype: None
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("schema_table", primary_key="id", schema=schema)
    new_record = {"name": "Bob", "age": 25}
    table.insert(new_record)
    assert "id" in new_record and isinstance(new_record["id"], int)
    records = table.select(where=Query(table.id == new_record["id"]))
    assert len(records) == 1


def test_update_atomicity_partial_failure(monkeypatch):
    """
    Tests that if one record fails schema validation during an update, all changes are rolled back.

    :param monkeypatch: Pytest fixture for dynamically modifying or mocking code.
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :return: None
    :rtype: None
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("atomic_test", primary_key="id", schema=schema)
    table.insert({"id": 1, "name": "Alice", "age": 30})
    table.insert({"id": 2, "name": "Bob", "age": 25})

    # Capture the initial state using the new copy() method.
    original_records = table.copy()

    # Store the original validate_record method.
    original_validate = table.validate_record

    # Monkeypatch validate_record to simulate a failure for record with id 2.
    def fake_validate(record):
        if record["id"] == 2:
            raise SchemaValidationError("Simulated failure for record 2")
        else:
            original_validate(record)

    monkeypatch.setattr(table, "validate_record", fake_validate)

    # Attempt to update all records. Expect a SchemaValidationError.
    with pytest.raises(SchemaValidationError):
        table.update({"age": 99})

    # Verify that both records remain unchanged.
    for key, original in original_records.items():
        assert table.copy()[key] == original


def test_update_atomicity_success():
    """
    Tests that a successful update applies to all matching records atomically.

    :return: None
    :rtype: None
    """
    schema = {"id": int, "name": str, "age": int}
    table = Table("atomic_success", primary_key="id", schema=schema)
    table.insert({"id": 1, "name": "Alice", "age": 30})
    table.insert({"id": 2, "name": "Bob", "age": 25})

    updated = table.update({"age": 40})
    assert updated == 2

    # Verify that the update was applied.
    for record in table.all():
        assert record["age"] == 40
