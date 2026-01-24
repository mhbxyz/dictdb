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


def test_select_distinct_all_columns() -> None:
    """Test distinct=True returns unique records."""
    t = Table("t")
    t.insert({"id": 1, "dept": "IT", "role": "dev"})
    t.insert({"id": 2, "dept": "IT", "role": "dev"})
    t.insert({"id": 3, "dept": "HR", "role": "admin"})

    results = t.select(columns=["dept", "role"], distinct=True)
    assert len(results) == 2
    depts = {r["dept"] for r in results}
    assert depts == {"IT", "HR"}


def test_select_distinct_single_column() -> None:
    """Test distinct on a single column projection."""
    t = Table("t")
    for i in range(1, 6):
        t.insert({"id": i, "category": f"cat_{i % 2}"})

    results = t.select(columns=["category"], distinct=True)
    assert len(results) == 2
    categories = {r["category"] for r in results}
    assert categories == {"cat_0", "cat_1"}


def test_select_distinct_preserves_order() -> None:
    """Test distinct preserves first occurrence order."""
    t = Table("t")
    t.insert({"id": 1, "val": "a"})
    t.insert({"id": 2, "val": "b"})
    t.insert({"id": 3, "val": "a"})
    t.insert({"id": 4, "val": "c"})
    t.insert({"id": 5, "val": "b"})

    results = t.select(columns=["val"], distinct=True)
    assert [r["val"] for r in results] == ["a", "b", "c"]


def test_select_distinct_with_where() -> None:
    """Test distinct combined with where clause."""
    t = Table("t")
    t.insert({"id": 1, "status": "active", "dept": "IT"})
    t.insert({"id": 2, "status": "active", "dept": "IT"})
    t.insert({"id": 3, "status": "inactive", "dept": "HR"})
    t.insert({"id": 4, "status": "active", "dept": "HR"})

    results = t.select(
        columns=["dept"],
        where=Condition(t.status == "active"),
        distinct=True,
    )
    assert len(results) == 2
    assert {r["dept"] for r in results} == {"IT", "HR"}


def test_select_distinct_false_returns_all() -> None:
    """Test distinct=False (default) returns all records."""
    t = Table("t")
    t.insert({"id": 1, "val": "a"})
    t.insert({"id": 2, "val": "a"})

    results = t.select(columns=["val"], distinct=False)
    assert len(results) == 2

    results_default = t.select(columns=["val"])
    assert len(results_default) == 2


def test_select_distinct_with_unhashable_values() -> None:
    """Test distinct handles records with list values."""
    t = Table("t")
    t.insert({"id": 1, "tags": ["a", "b"]})
    t.insert({"id": 2, "tags": ["a", "b"]})
    t.insert({"id": 3, "tags": ["c"]})

    results = t.select(columns=["tags"], distinct=True)
    assert len(results) == 2
