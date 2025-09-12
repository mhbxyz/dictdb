from typing import Any

from dictdb import Table, Condition


def test_schema_primary_key_added() -> None:
    schema: dict[str, type[Any]] = {"name": str}
    t = Table("t", primary_key="id", schema=schema)
    assert t.schema is not None and "id" in t.schema and t.schema["id"] is int


def test_create_index_second_call_noop() -> None:
    t = Table("t")
    t.insert({"id": 1, "name": "a"})
    t.create_index("name", index_type="hash")
    before = set(t.indexes.keys())
    t.create_index("name", index_type="hash")
    after = set(t.indexes.keys())
    assert before == after


def test_update_indexes_on_update_no_change_branch() -> None:
    t = Table("t")
    t.insert({"id": 1, "name": "a", "age": 10})
    t.create_index("name", index_type="hash")
    # Update a non-indexed field to trigger the equality-continue branch
    updated = t.update({"age": 11}, where=Condition(t.name == "a"))
    assert updated == 1
    # Index for 'name' should remain intact
    assert "name" in t.indexes


def test_validate_record_no_schema_return() -> None:
    t = Table("t")
    # Should be a no-op and not raise
    t.validate_record({"id": 1, "x": 1})
