"""
This module contains unit tests for the BackupManager, which provides an automatic
backup system for DictDB. Tests verify both periodic and manual backup triggering.
"""

import time
from pathlib import Path

import pytest

from dictdb import DictDB, BackupManager


@pytest.mark.slow
def test_manual_backup(tmp_path: Path, test_db: DictDB) -> None:
    """
    Tests that a manual backup (triggered by notify_change) creates a backup file.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :param test_db: A DictDB fixture for testing.
    :type test_db: DictDB
    :return: None
    :rtype: None
    """
    backup_dir = tmp_path / "manual_backup"
    manager = BackupManager(test_db, backup_dir, backup_interval=60, file_format="json")
    manager.notify_change()
    # Wait briefly to ensure the backup file is written.
    time.sleep(0.5)
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) >= 1, "Manual backup did not create a backup file."


@pytest.mark.slow
def test_periodic_backup(tmp_path: Path, test_db: DictDB) -> None:
    """
    Tests that the periodic backup thread creates backup files over time.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :param test_db: A DictDB fixture for testing.
    :type test_db: DictDB
    :return: None
    :rtype: None
    """
    backup_dir = tmp_path / "periodic_backup"
    # Set a short interval for testing purposes.
    manager = BackupManager(test_db, backup_dir, backup_interval=1, file_format="json")
    manager.start()
    # Wait long enough for at least one backup to occur.
    time.sleep(2.5)
    manager.stop()
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) >= 1, "Periodic backup did not create any backup files."


@pytest.mark.slow
def test_stop_backup_manager(tmp_path: Path, test_db: DictDB) -> None:
    """
    Tests that the backup manager stops its periodic backup thread properly.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :param test_db: A DictDB fixture for testing.
    :type test_db: DictDB
    :return: None
    :rtype: None
    """
    backup_dir = tmp_path / "stop_backup"
    manager = BackupManager(test_db, backup_dir, backup_interval=1, file_format="json")
    manager.start()
    # Allow the backup to run for a short period.
    time.sleep(1.5)
    manager.stop()
    # Ensure the backup thread has stopped.
    assert not manager._backup_thread.is_alive(), "Backup manager thread did not stop."


def test_backup_now_handles_failure(
    tmp_path: Path, log_capture: list[str], failing_db: "DictDB"
) -> None:
    """
    Tests that backup_now() handles save failures gracefully and logs them.

    :param tmp_path: A temporary directory provided by pytest.
    :param log_capture: Fixture that captures log messages.
    :param failing_db: A DictDB instance that raises on save().
    """
    backup_dir = tmp_path / "fail_backup"
    manager = BackupManager(
        failing_db, backup_dir, backup_interval=60, file_format="json"
    )
    # Should not raise, and should log the error
    manager.backup_now()
    messages = "\n".join(log_capture)
    assert "Backup failed (1 consecutive):" in messages, "Failure should be logged"


@pytest.mark.slow
def test_notify_change_debouncing(tmp_path: Path, test_db: DictDB) -> None:
    """
    Tests that notify_change() skips backup if called within min_backup_interval.

    :param tmp_path: A temporary directory provided by pytest.
    :param test_db: A DictDB fixture for testing.
    """
    backup_dir = tmp_path / "debounce_backup"
    manager = BackupManager(
        test_db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        min_backup_interval=2.0,
    )

    # First call should create a backup
    manager.notify_change()
    time.sleep(0.1)
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) == 1, "First notify_change should create a backup."

    # Immediate second call should be skipped (debounced)
    manager.notify_change()
    time.sleep(0.1)
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) == 1, "Second notify_change should be debounced."

    # Wait for debounce interval to pass
    time.sleep(2.0)
    manager.notify_change()
    time.sleep(0.1)
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) == 2, (
        "Third notify_change after interval should create backup."
    )


def test_backup_creates_unique_filenames(tmp_path: Path, test_db: DictDB) -> None:
    """
    Tests that rapid backups create unique filenames (no collisions).

    :param tmp_path: A temporary directory provided by pytest.
    :param test_db: A DictDB fixture for testing.
    """
    backup_dir = tmp_path / "unique_backup"
    manager = BackupManager(test_db, backup_dir, backup_interval=60, file_format="json")

    # Call backup_now() multiple times rapidly
    for _ in range(5):
        manager.backup_now()

    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) == 5, "Each backup_now() should create a unique file."


def test_backup_failure_callback(tmp_path: Path, failing_db: "DictDB") -> None:
    """
    Tests that the on_backup_failure callback is invoked with exception and failure count.

    :param tmp_path: A temporary directory provided by pytest.
    :param failing_db: A DictDB instance that raises on save().
    """
    failures: list[tuple[Exception, int]] = []

    def on_failure(exc: Exception, count: int) -> None:
        failures.append((exc, count))

    backup_dir = tmp_path / "callback_backup"
    manager = BackupManager(
        failing_db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        on_backup_failure=on_failure,
    )

    # Trigger multiple failures
    manager.backup_now()
    manager.backup_now()
    manager.backup_now()

    assert len(failures) == 3, "Callback should be invoked for each failure."
    assert failures[0][1] == 1, "First failure count should be 1."
    assert failures[1][1] == 2, "Second failure count should be 2."
    assert failures[2][1] == 3, "Third failure count should be 3."
    assert manager.consecutive_failures == 3, "Consecutive failures should be 3."


def test_backup_success_resets_failure_count(tmp_path: Path, test_db: DictDB) -> None:
    """
    Tests that a successful backup resets the consecutive failure counter.
    """
    backup_dir = tmp_path / "reset_backup"
    manager = BackupManager(test_db, backup_dir, backup_interval=60, file_format="json")

    # Simulate failures by setting counter directly (since we can't easily fail then succeed)
    manager._consecutive_failures = 5

    # Successful backup should reset
    manager.backup_now()
    assert manager.consecutive_failures == 0, "Success should reset failure counter."


# ──────────────────────────────────────────────────────────────────────────────
# Incremental backup tests
# ──────────────────────────────────────────────────────────────────────────────


def test_dirty_tracking_insert() -> None:
    """Tests that insert marks records as dirty."""
    from dictdb import DictDB

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")
    assert not users.has_changes(), "Fresh table should have no changes."

    users.insert({"id": 1, "name": "Alice"})
    assert users.has_changes(), "Table should have changes after insert."

    dirty = users.get_dirty_records()
    assert len(dirty) == 1
    assert dirty[0]["name"] == "Alice"


def test_dirty_tracking_update() -> None:
    """Tests that update marks records as dirty."""
    from dictdb import DictDB, Condition

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")
    users.insert({"id": 1, "name": "Alice"})
    users.clear_dirty_tracking()

    assert not users.has_changes(), "Table should be clean after clearing."

    users.update({"name": "Alicia"}, Condition(users.id == 1))
    assert users.has_changes(), "Table should have changes after update."

    dirty = users.get_dirty_records()
    assert len(dirty) == 1
    assert dirty[0]["name"] == "Alicia"


def test_dirty_tracking_delete() -> None:
    """Tests that delete tracks deleted PKs."""
    from dictdb import DictDB, Condition

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")
    users.insert({"id": 1, "name": "Alice"})
    users.insert({"id": 2, "name": "Bob"})
    users.clear_dirty_tracking()

    users.delete(Condition(users.id == 1))
    assert users.has_changes(), "Table should have changes after delete."

    deleted = users.get_deleted_pks()
    assert 1 in deleted
    assert 2 not in deleted


def test_clear_dirty_tracking() -> None:
    """Tests that clear_dirty_tracking resets all tracking."""
    from dictdb import DictDB, Condition

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")
    users.insert({"id": 1, "name": "Alice"})
    users.delete(Condition(users.id == 1))
    users.insert({"id": 2, "name": "Bob"})

    assert users.has_changes()

    users.clear_dirty_tracking()
    assert not users.has_changes()
    assert len(users.get_dirty_records()) == 0
    assert len(users.get_deleted_pks()) == 0


def test_save_delta(tmp_path: Path) -> None:
    """Tests saving a delta file with changes."""
    from dictdb import DictDB
    from dictdb.storage.persist import save_delta, has_changes

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")
    users.insert({"id": 1, "name": "Alice"})

    assert has_changes(db)

    delta_file = tmp_path / "test_delta.json"
    result = save_delta(db, delta_file)

    assert result is True, "save_delta should return True when changes exist."
    assert delta_file.exists(), "Delta file should be created."
    assert not has_changes(db), "Changes should be cleared after save."


def test_save_delta_no_changes(tmp_path: Path) -> None:
    """Tests that save_delta returns False when no changes."""
    from dictdb import DictDB
    from dictdb.storage.persist import save_delta

    db = DictDB()
    db.create_table("users")  # Empty table, no changes

    delta_file = tmp_path / "empty_delta.json"
    result = save_delta(db, delta_file)

    assert result is False, "save_delta should return False when no changes."
    assert not delta_file.exists(), "No file should be created."


def test_apply_delta(tmp_path: Path) -> None:
    """Tests applying a delta file to restore changes."""
    import json
    from dictdb import DictDB
    from dictdb.storage.persist import apply_delta

    # Create a delta file manually
    delta_file = tmp_path / "manual_delta.json"
    delta_content = {
        "type": "delta",
        "timestamp": 12345.0,
        "tables": {
            "users": {
                "upserts": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
                "deletes": [],
            }
        },
    }
    with open(delta_file, "w") as f:
        json.dump(delta_content, f)

    # Apply to a fresh DB with existing table
    db = DictDB()
    db.create_table("users")
    db.get_table("users").clear_dirty_tracking()

    affected = apply_delta(db, delta_file)

    assert affected == 2, "Two records should be affected."
    users = db.get_table("users")
    assert users.count() == 2


def test_apply_delta_with_deletes(tmp_path: Path) -> None:
    """Tests applying a delta file with deletions."""
    import json
    from dictdb import DictDB
    from dictdb.storage.persist import apply_delta

    # Create DB with existing records
    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")
    users.insert({"id": 1, "name": "ToDelete"})
    users.insert({"id": 2, "name": "ToKeep"})
    users.clear_dirty_tracking()

    # Create delta that deletes id=1
    delta_file = tmp_path / "delete_delta.json"
    delta_content = {
        "type": "delta",
        "timestamp": 12345.0,
        "tables": {
            "users": {
                "upserts": [],
                "deletes": [1],
            }
        },
    }
    with open(delta_file, "w") as f:
        json.dump(delta_content, f)

    affected = apply_delta(db, delta_file)

    assert affected == 1
    assert users.count() == 1
    assert users.select()[0]["name"] == "ToKeep"


def test_incremental_backup_mode(tmp_path: Path) -> None:
    """Tests BackupManager in incremental mode creates delta files."""
    from dictdb import DictDB

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")

    backup_dir = tmp_path / "incremental"
    manager = BackupManager(
        db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        incremental=True,
        max_deltas_before_full=5,
    )

    # Make a change and backup
    users.insert({"id": 1, "name": "Alice"})

    manager.backup_now()

    delta_files = list(backup_dir.glob("dictdb_delta_*.json"))
    assert len(delta_files) == 1, "Should create one delta file."
    assert manager.deltas_since_full == 1


def test_incremental_backup_compaction(tmp_path: Path) -> None:
    """Tests that incremental mode triggers full backup after max deltas."""
    from dictdb import DictDB

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")

    backup_dir = tmp_path / "compaction"
    manager = BackupManager(
        db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        incremental=True,
        max_deltas_before_full=3,
    )

    # Create 3 deltas
    for i in range(3):
        users.insert({"id": i, "name": f"User{i}"})
        manager.backup_now()

    assert manager.deltas_since_full == 3
    delta_files = list(backup_dir.glob("dictdb_delta_*.json"))
    assert len(delta_files) == 3

    # Next backup should trigger full backup (compaction)
    users.insert({"id": 100, "name": "TriggerFull"})
    manager.backup_now()

    assert manager.deltas_since_full == 0, "Full backup should reset delta counter."
    full_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(full_files) == 1, "Should create one full backup file."


def test_incremental_backup_no_changes_skipped(tmp_path: Path) -> None:
    """Tests that incremental backup skips when no changes."""
    from dictdb import DictDB

    db = DictDB()
    db.create_table("users")  # No inserts, so no changes

    backup_dir = tmp_path / "no_changes"
    manager = BackupManager(
        db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        incremental=True,
    )

    # Backup with no changes
    manager.backup_now()

    delta_files = list(backup_dir.glob("dictdb_delta_*.json"))
    assert len(delta_files) == 0, "No delta file should be created without changes."
