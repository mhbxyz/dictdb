from typing import Set

from dictdb import Table


def test_columns_with_schema() -> None:
    schema = {"id": int, "name": str, "age": int}
    table = Table("people", primary_key="id", schema=schema)
    # With a schema, columns are derived from the schema keys
    cols = set(table.columns())
    assert cols == set(schema.keys())


def test_columns_without_schema(table: Table) -> None:
    # No schema: columns are derived from records; expect union of keys
    cols: Set[str] = set(table.columns())
    assert cols == {"id", "name", "age"}


def test_count_records_and_len(table: Table) -> None:
    assert table.count() == 2
    assert len(table) == 2
    table.insert({"id": 3, "name": "Charlie", "age": 40})
    assert table.count() == 3
    assert len(table) == 3


def test_indexed_fields_and_has_index(indexed_table: Table) -> None:
    indexed = set(indexed_table.indexed_fields())
    assert indexed == {"age"}
    assert indexed_table.has_index("age") is True
    assert indexed_table.has_index("name") is False


def test_schema_fields_and_primary_key() -> None:
    schema = {"user_id": int, "name": str}
    t = Table("users", primary_key="user_id", schema=schema)
    assert set(t.schema_fields()) == set(schema.keys())
    assert t.primary_key_name() == "user_id"


def test_schema_fields_no_schema(table: Table) -> None:
    # When schema is not provided, schema_fields() should be empty
    assert table.schema_fields() == []
