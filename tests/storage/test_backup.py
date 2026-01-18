"""
This module contains unit tests for the BackupManager, which provides an automatic
backup system for DictDB. Tests verify both periodic and manual backup triggering.
"""

import time
from pathlib import Path

from dictdb import DictDB, BackupManager


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


def test_backup_now_handles_failure(tmp_path: Path, log_capture: list[str]) -> None:
    class FailingDB(DictDB):
        def save(self, filename: str, file_format: str) -> None:  # type: ignore[override]
            raise RuntimeError("boom")

    # Configure a capture sink via log_capture fixture
    backup_dir = tmp_path / "fail_backup"
    manager = BackupManager(
        FailingDB(), backup_dir, backup_interval=60, file_format="json"
    )
    # Should not raise, and should log the error
    manager.backup_now()
    messages = "\n".join(log_capture)
    assert "Backup failed (1 consecutive):" in messages


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


def test_backup_failure_callback(tmp_path: Path) -> None:
    """
    Tests that the on_backup_failure callback is invoked with exception and failure count.
    """

    class FailingDB(DictDB):
        def save(self, filename: str, file_format: str) -> None:  # type: ignore[override]
            raise RuntimeError("boom")

    failures: list[tuple[Exception, int]] = []

    def on_failure(exc: Exception, count: int) -> None:
        failures.append((exc, count))

    backup_dir = tmp_path / "callback_backup"
    manager = BackupManager(
        FailingDB(),
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
    assert manager.consecutive_failures == 3


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
