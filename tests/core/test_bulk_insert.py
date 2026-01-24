"""
Unit tests for bulk insert functionality.
"""

import pytest

from dictdb import Table, DuplicateKeyError, SchemaValidationError, Condition
from dictdb.core.types import Record


class TestBulkInsert:
    """Tests for insert() with multiple records."""

    def test_insert_empty_list(self) -> None:
        """Test inserting empty list returns empty list."""
        t = Table("test", primary_key="id")
        pks = t.insert([])
        assert pks == []
        assert t.count() == 0

    def test_insert_multiple_records(self) -> None:
        """Test inserting multiple records at once."""
        t = Table("test", primary_key="id")
        records = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
        pks = t.insert(records)
        assert len(pks) == 3
        assert t.count() == 3

    def test_insert_multiple_auto_pk(self) -> None:
        """Test that bulk insert auto-generates sequential PKs."""
        t = Table("test", primary_key="id")
        records = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        pks = t.insert(records)
        assert pks == [1, 2, 3]

    def test_insert_multiple_explicit_pks(self) -> None:
        """Test bulk insert with explicit PKs."""
        t = Table("test", primary_key="id")
        records = [
            {"id": 10, "name": "A"},
            {"id": 20, "name": "B"},
            {"id": 30, "name": "C"},
        ]
        pks = t.insert(records)
        assert pks == [10, 20, 30]

    def test_insert_multiple_mixed_pks(self) -> None:
        """Test bulk insert with mix of explicit and auto PKs."""
        t = Table("test", primary_key="id")
        records: list[Record] = [
            {"id": 5, "name": "A"},
            {"name": "B"},  # Auto-generate
            {"id": 10, "name": "C"},
            {"name": "D"},  # Auto-generate
        ]
        pks = t.insert(records)
        assert pks[0] == 5
        assert pks[2] == 10
        # Auto-generated should be > 10
        assert pks[1] > 5
        assert pks[3] > 10

    def test_insert_multiple_duplicate_pk_rollback(self) -> None:
        """Test that duplicate PK in batch rolls back all inserts."""
        t = Table("test", primary_key="id")
        t.insert({"id": 1, "name": "Existing"})

        records = [
            {"id": 2, "name": "A"},
            {"id": 3, "name": "B"},
            {"id": 1, "name": "Duplicate"},  # Conflict
        ]
        with pytest.raises(DuplicateKeyError):
            t.insert(records)

        # Should only have the original record
        assert t.count() == 1
        assert t.select()[0]["name"] == "Existing"

    def test_insert_multiple_duplicate_within_batch(self) -> None:
        """Test that duplicate PK within batch is detected."""
        t = Table("test", primary_key="id")
        records = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 1, "name": "Duplicate"},  # Duplicate within batch
        ]
        with pytest.raises(DuplicateKeyError):
            t.insert(records)

        assert t.count() == 0  # Rolled back

    def test_insert_multiple_schema_validation_rollback(self) -> None:
        """Test that schema validation failure rolls back all inserts."""
        t = Table("test", primary_key="id", schema={"id": int, "name": str})
        records: list[Record] = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": 123},  # Invalid type
        ]
        with pytest.raises(SchemaValidationError):
            t.insert(records)

        assert t.count() == 0  # Rolled back

    def test_insert_multiple_updates_indexes(self) -> None:
        """Test that bulk insert updates indexes correctly."""
        t = Table("test", primary_key="id")
        t.create_index("status", index_type="hash")

        records = [
            {"id": 1, "status": "active"},
            {"id": 2, "status": "active"},
            {"id": 3, "status": "inactive"},
        ]
        t.insert(records)

        active = t.select(where=Condition(t.status == "active"))
        inactive = t.select(where=Condition(t.status == "inactive"))
        assert len(active) == 2
        assert len(inactive) == 1

    def test_insert_multiple_dirty_tracking(self) -> None:
        """Test that bulk insert updates dirty tracking."""
        t = Table("test", primary_key="id")
        records = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        t.insert(records)

        assert t.has_changes()
        dirty = t.get_dirty_records()
        assert len(dirty) == 3

    def test_insert_single_still_works(self) -> None:
        """Test that single record insert still works as before."""
        t = Table("test", primary_key="id")
        pk = t.insert({"name": "Alice"})
        assert pk == 1
        assert t.count() == 1

    def test_insert_single_returns_scalar(self) -> None:
        """Test that single insert returns scalar, not list."""
        t = Table("test", primary_key="id")
        result = t.insert({"name": "Alice"})
        assert not isinstance(result, list)

    def test_insert_multiple_returns_list(self) -> None:
        """Test that bulk insert returns list."""
        t = Table("test", primary_key="id")
        result = t.insert([{"name": "Alice"}])
        assert isinstance(result, list)
        assert result == [1]

    def test_insert_with_batch_size(self) -> None:
        """Test that batch_size parameter works correctly."""
        t = Table("test", primary_key="id")
        records = [{"name": f"User{i}"} for i in range(100)]
        pks = t.insert(records, batch_size=25)
        assert len(pks) == 100
        assert t.count() == 100

    def test_insert_with_skip_validation(self) -> None:
        """Test that skip_validation bypasses schema checks."""
        t = Table("test", primary_key="id", schema={"id": int, "name": str})
        records: list[Record] = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": 123},  # Would fail validation
        ]
        # With skip_validation=True, this should succeed
        pks = t.insert(records, skip_validation=True)
        assert pks == [1, 2]
        assert t.count() == 2

    def test_insert_without_skip_validation_fails(self) -> None:
        """Test that validation is enforced by default."""
        t = Table("test", primary_key="id", schema={"id": int, "name": str})
        records: list[Record] = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": 123},  # Invalid type
        ]
        with pytest.raises(SchemaValidationError):
            t.insert(records, skip_validation=False)
        assert t.count() == 0

    def test_insert_single_with_skip_validation(self) -> None:
        """Test that skip_validation works for single record insert."""
        t = Table("test", primary_key="id", schema={"id": int, "name": str})
        # This would fail validation normally
        pk = t.insert({"id": 1, "name": 123}, skip_validation=True)
        assert pk == 1
        assert t.count() == 1

    def test_insert_batch_size_larger_than_records(self) -> None:
        """Test that batch_size larger than record count works."""
        t = Table("test", primary_key="id")
        records = [{"name": "A"}, {"name": "B"}]
        pks = t.insert(records, batch_size=1000)
        assert pks == [1, 2]

    def test_insert_batch_size_one(self) -> None:
        """Test that batch_size=1 processes one record at a time."""
        t = Table("test", primary_key="id")
        t.create_index("name", index_type="hash")
        records = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        pks = t.insert(records, batch_size=1)
        assert len(pks) == 3
        # Verify indexes are correct
        assert len(t.select(where=Condition(t.name == "A"))) == 1

    @pytest.mark.slow
    def test_insert_many_performance(self) -> None:
        """Test that bulk insert is faster than individual inserts."""
        import time

        n = 5000

        # Bulk insert
        t1 = Table("bulk", primary_key="id")
        records = [{"value": i} for i in range(n)]
        start = time.perf_counter()
        t1.insert(records)
        bulk_time = time.perf_counter() - start

        # Individual inserts
        t2 = Table("individual", primary_key="id")
        start = time.perf_counter()
        for i in range(n):
            t2.insert({"value": i})
        individual_time = time.perf_counter() - start

        # Bulk should be significantly faster (at least 2x)
        assert bulk_time < individual_time / 2, (
            f"Bulk: {bulk_time:.3f}s, Individual: {individual_time:.3f}s"
        )
