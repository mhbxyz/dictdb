"""
Unit tests for Table.upsert() method.
"""

import pytest

from dictdb import Table, Condition, DuplicateKeyError


class TestUpsert:
    """Tests for upsert operation."""

    @pytest.fixture
    def table(self) -> Table:
        """Create a table with some initial data."""
        t = Table("users", primary_key="id")
        t.insert({"id": 1, "name": "Alice", "email": "alice@old.com"})
        t.insert({"id": 2, "name": "Bob", "email": "bob@old.com"})
        return t

    def test_upsert_insert_new_record(self, table: Table) -> None:
        """Test upsert inserts when record doesn't exist."""
        pk, action = table.upsert({"id": 3, "name": "Carol", "email": "carol@new.com"})
        assert pk == 3
        assert action == "inserted"
        assert table.count() == 3
        record = table.select(columns=["name"], where=None)[2]
        assert record["name"] == "Carol"

    def test_upsert_update_existing_record(self, table: Table) -> None:
        """Test upsert updates when record exists (default behavior)."""
        pk, action = table.upsert({"id": 1, "name": "Alice", "email": "alice@new.com"})
        assert pk == 1
        assert action == "updated"
        assert table.count() == 2  # No new record
        records = table.select()
        alice = [r for r in records if r["id"] == 1][0]
        assert alice["email"] == "alice@new.com"

    def test_upsert_on_conflict_update(self, table: Table) -> None:
        """Test upsert with explicit on_conflict='update'."""
        pk, action = table.upsert(
            {"id": 1, "name": "Alice Updated"},
            on_conflict="update",
        )
        assert action == "updated"
        records = table.select()
        alice = [r for r in records if r["id"] == 1][0]
        assert alice["name"] == "Alice Updated"

    def test_upsert_on_conflict_ignore(self, table: Table) -> None:
        """Test upsert with on_conflict='ignore' keeps existing record."""
        pk, action = table.upsert(
            {"id": 1, "name": "Should Not Update"},
            on_conflict="ignore",
        )
        assert pk == 1
        assert action == "ignored"
        assert table.count() == 2
        records = table.select()
        alice = [r for r in records if r["id"] == 1][0]
        assert alice["name"] == "Alice"  # Unchanged

    def test_upsert_on_conflict_error(self, table: Table) -> None:
        """Test upsert with on_conflict='error' raises on existing record."""
        with pytest.raises(DuplicateKeyError):
            table.upsert({"id": 1, "name": "Should Fail"}, on_conflict="error")

    def test_upsert_on_conflict_error_new_record(self, table: Table) -> None:
        """Test upsert with on_conflict='error' works for new records."""
        pk, action = table.upsert(
            {"id": 99, "name": "New User"},
            on_conflict="error",
        )
        assert pk == 99
        assert action == "inserted"

    def test_upsert_without_pk_auto_generates(self, table: Table) -> None:
        """Test upsert without PK auto-generates one."""
        pk, action = table.upsert({"name": "NoID", "email": "noid@test.com"})
        assert pk is not None
        assert action == "inserted"
        assert table.count() == 3

    def test_upsert_updates_indexes(self) -> None:
        """Test that upsert properly updates indexes."""
        t = Table("indexed", primary_key="id")
        t.create_index("status", index_type="hash")
        t.insert({"id": 1, "status": "active"})

        # Update via upsert
        t.upsert({"id": 1, "status": "inactive"})

        # Index should reflect new value
        active = t.select(where=Condition(t.status == "active"))
        inactive = t.select(where=Condition(t.status == "inactive"))
        assert len(active) == 0
        assert len(inactive) == 1

    def test_upsert_with_schema_validation(self) -> None:
        """Test upsert validates against schema."""
        from dictdb import SchemaValidationError

        t = Table("typed", primary_key="id", schema={"id": int, "name": str})

        # Valid insert
        pk, action = t.upsert({"id": 1, "name": "Alice"})
        assert action == "inserted"

        # Valid update
        pk, action = t.upsert({"id": 1, "name": "Alice Updated"})
        assert action == "updated"

        # Invalid type should raise
        with pytest.raises(SchemaValidationError):
            t.upsert({"id": 2, "name": 123})

    def test_upsert_partial_update(self, table: Table) -> None:
        """Test upsert merges fields on update."""
        # Original has name and email
        pk, action = table.upsert({"id": 1, "status": "active"})
        assert action == "updated"

        records = table.select()
        alice = [r for r in records if r["id"] == 1][0]
        # Should have all fields
        assert alice["name"] == "Alice"
        assert alice["email"] == "alice@old.com"
        assert alice["status"] == "active"

    def test_upsert_returns_correct_pk_type(self) -> None:
        """Test upsert returns correct PK type."""
        t = Table("strings", primary_key="code")
        pk, action = t.upsert({"code": "ABC", "value": 1})
        assert pk == "ABC"
        assert isinstance(pk, str)
        assert action == "inserted"

        pk, action = t.upsert({"code": "ABC", "value": 2})
        assert pk == "ABC"
        assert action == "updated"
