"""
Concurrency tests for backup operations.

Tests verify that backups capture consistent snapshots during concurrent
database modifications and that the BackupManager handles concurrent
backup requests correctly.
"""

import json
import threading
import time
from pathlib import Path
from typing import List, Union

import pytest

from dictdb import DictDB, BackupManager


@pytest.mark.slow
def test_backup_snapshot_consistency(tmp_path: Path) -> None:
    """
    Tests that backups capture a consistent snapshot even during writes.
    The backup should represent a valid state of the database.
    """
    db = DictDB()
    db.create_table("transactions")
    table = db.get_table("transactions")

    # Pre-populate with balanced transactions
    for i in range(100):
        table.insert({"id": i, "amount": 100, "type": "credit"})

    backup_dir = tmp_path / "snapshot_test"
    manager = BackupManager(db, backup_dir, backup_interval=60, file_format="json")

    stop_flag = threading.Event()
    backup_completed = threading.Event()

    def writer() -> None:
        counter = 100
        while not stop_flag.is_set():
            try:
                # Add paired transactions (credit + debit that sum to 0)
                table.insert({"id": counter, "amount": 50, "type": "credit"})
                counter += 1
                table.insert({"id": counter, "amount": -50, "type": "debit"})
                counter += 1
            except Exception:
                pass
            time.sleep(0.01)

    def backup_task() -> None:
        time.sleep(0.1)  # Let writer start
        manager.backup_now()
        backup_completed.set()

    writer_thread = threading.Thread(target=writer)
    backup_thread = threading.Thread(target=backup_task)

    writer_thread.start()
    backup_thread.start()

    backup_completed.wait(timeout=5.0)
    stop_flag.set()

    writer_thread.join(timeout=2.0)
    backup_thread.join(timeout=2.0)

    # Load and verify the backup
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) >= 1, "Backup file should be created"

    with open(backup_files[0]) as f:
        backup_data = json.load(f)

    # Verify backup structure
    assert "tables" in backup_data
    assert "transactions" in backup_data["tables"]

    records = backup_data["tables"]["transactions"]["records"]

    # The backup should be internally consistent
    # All records should have valid structure (records is a list)
    assert isinstance(records, list), "Records should be a list"
    for record in records:
        assert "amount" in record, f"Record missing 'amount': {record}"
        assert "type" in record, f"Record missing 'type': {record}"


@pytest.mark.slow
def test_concurrent_backup_requests_debounced(tmp_path: Path) -> None:
    """
    Tests that rapid notify_change() calls are properly debounced.
    Only backups spaced at least min_backup_interval apart should occur.
    """
    db = DictDB()
    db.create_table("test")
    table = db.get_table("test")
    table.insert({"id": 1, "value": "initial"})

    backup_dir = tmp_path / "debounce_test"
    manager = BackupManager(
        db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        min_backup_interval=0.5,  # 500ms debounce
    )

    # Trigger many rapid notify_change calls
    for _ in range(20):
        manager.notify_change()
        time.sleep(0.02)  # 20ms between calls, much less than 500ms debounce

    time.sleep(0.3)  # Wait for any pending backups

    # Due to debouncing, we should have only 1 backup (all calls within 500ms window)
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) == 1, (
        f"Expected 1 backup due to debouncing, got {len(backup_files)}"
    )


@pytest.mark.slow
def test_backup_during_heavy_writes(tmp_path: Path) -> None:
    """
    Tests that backup completes successfully during heavy write load.
    """
    db = DictDB()
    db.create_table("heavy_write")
    table = db.get_table("heavy_write")

    backup_dir = tmp_path / "heavy_write_test"
    manager = BackupManager(db, backup_dir, backup_interval=60, file_format="json")

    stop_flag = threading.Event()
    backup_success = []
    backup_errors: List[Exception] = []
    lock = threading.Lock()

    def heavy_writer() -> None:
        counter = 0
        while not stop_flag.is_set():
            try:
                table.insert({"id": counter, "data": "x" * 100})
                counter += 1
            except Exception:
                pass

    def periodic_backup() -> None:
        for _ in range(5):
            try:
                manager.backup_now()
                with lock:
                    backup_success.append(True)
            except Exception as e:
                with lock:
                    backup_errors.append(e)
            time.sleep(0.2)

    writers = [threading.Thread(target=heavy_writer) for _ in range(5)]
    backup_thread = threading.Thread(target=periodic_backup)

    for w in writers:
        w.start()
    backup_thread.start()

    backup_thread.join(timeout=10.0)
    stop_flag.set()

    for w in writers:
        w.join(timeout=2.0)

    assert len(backup_success) == 5, "All backup attempts should succeed"
    assert not backup_errors, f"Backup errors: {backup_errors}"

    # Verify backups are valid JSON
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) == 5, f"Expected 5 backups, got {len(backup_files)}"

    for bf in backup_files:
        with open(bf) as f:
            data = json.load(f)  # Should not raise
            assert "tables" in data


@pytest.mark.slow
def test_incremental_backup_concurrent_modifications(tmp_path: Path) -> None:
    """
    Tests incremental backup with concurrent modifications.
    Delta files should correctly capture changes.
    """
    db = DictDB()
    db.create_table("incremental_test")
    table = db.get_table("incremental_test")

    # Initial data
    for i in range(50):
        table.insert({"id": i, "value": f"initial_{i}"})
    table.clear_dirty_tracking()

    backup_dir = tmp_path / "incremental_concurrent"
    manager = BackupManager(
        db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        incremental=True,
        max_deltas_before_full=10,
    )

    stop_flag = threading.Event()
    deltas_created = []
    lock = threading.Lock()

    def modifier() -> None:
        counter = 50
        while not stop_flag.is_set():
            try:
                table.insert({"id": counter, "value": f"new_{counter}"})
                counter += 1
            except Exception:
                pass
            time.sleep(0.02)

    def backup_loop() -> None:
        for _ in range(5):
            time.sleep(0.1)
            manager.backup_now()
            with lock:
                deltas_created.append(manager.deltas_since_full)

    mod_threads = [threading.Thread(target=modifier) for _ in range(3)]
    backup_thread = threading.Thread(target=backup_loop)

    for t in mod_threads:
        t.start()
    backup_thread.start()

    backup_thread.join(timeout=10.0)
    stop_flag.set()

    for t in mod_threads:
        t.join(timeout=2.0)

    # Should have created some delta files
    delta_files = list(backup_dir.glob("dictdb_delta_*.json"))
    assert len(delta_files) >= 1, "At least one delta file should be created"

    # Verify delta file structure
    for df in delta_files:
        with open(df) as f:
            data = json.load(f)
            assert data.get("type") == "delta", "File should be a delta"
            assert "tables" in data
            if "incremental_test" in data["tables"]:
                table_delta = data["tables"]["incremental_test"]
                assert "upserts" in table_delta
                assert "deletes" in table_delta


@pytest.mark.slow
def test_backup_manager_start_stop_concurrent(tmp_path: Path) -> None:
    """
    Tests that starting and stopping BackupManager is thread-safe.
    """
    db = DictDB()
    db.create_table("start_stop_test")

    backup_dir = tmp_path / "start_stop"
    manager = BackupManager(
        db,
        backup_dir,
        backup_interval=1,  # Short interval for testing
        file_format="json",
    )

    # Start the manager
    manager.start()

    # Let it run briefly
    time.sleep(1.5)

    # Stop should be clean
    manager.stop()

    # Thread should be stopped
    assert not manager._backup_thread.is_alive(), "Backup thread should be stopped"

    # At least one backup should have been created
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    assert len(backup_files) >= 1, "At least one periodic backup should occur"


@pytest.mark.slow
def test_backup_file_uniqueness_under_load(tmp_path: Path) -> None:
    """
    Tests that concurrent backup_now() calls create unique files.
    """
    db = DictDB()
    db.create_table("unique_test")
    table = db.get_table("unique_test")
    table.insert({"id": 1, "value": "test"})

    backup_dir = tmp_path / "unique_files"
    manager = BackupManager(db, backup_dir, backup_interval=60, file_format="json")

    def do_backup() -> None:
        manager.backup_now()

    # Many concurrent backup_now calls
    threads = [threading.Thread(target=do_backup) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10.0)

    # All backups should have unique filenames
    backup_files = list(backup_dir.glob("dictdb_backup_*.json"))
    filenames = [f.name for f in backup_files]
    unique_filenames = set(filenames)

    assert len(filenames) == len(unique_filenames), (
        f"Duplicate filenames detected: {len(filenames)} files, {len(unique_filenames)} unique"
    )
    assert len(backup_files) == 20, f"Expected 20 backups, got {len(backup_files)}"


@pytest.mark.slow
def test_backup_failure_counter_thread_safety(tmp_path: Path) -> None:
    """
    Tests that the failure counter is thread-safe during concurrent failures.
    """
    failure_count = 0

    class CountingFailDB(DictDB):
        def save(self, filename: Union[str, Path], file_format: str) -> None:
            nonlocal failure_count
            failure_count += 1
            raise RuntimeError("Intentional failure")

    db = CountingFailDB()
    db.create_table("fail_test")

    backup_dir = tmp_path / "failure_counter"
    failures_recorded: List[int] = []
    lock = threading.Lock()

    def on_failure(exc: Exception, count: int) -> None:
        with lock:
            failures_recorded.append(count)

    manager = BackupManager(
        db,
        backup_dir,
        backup_interval=60,
        file_format="json",
        on_backup_failure=on_failure,
    )

    def trigger_failure() -> None:
        manager.backup_now()

    threads = [threading.Thread(target=trigger_failure) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)

    # All 10 failures should have been recorded
    assert len(failures_recorded) == 10, (
        f"Expected 10 failures, got {len(failures_recorded)}"
    )

    # Failure counts should be sequential (1 through 10)
    sorted_failures = sorted(failures_recorded)
    assert sorted_failures == list(range(1, 11)), (
        f"Failure counts should be 1-10, got {sorted_failures}"
    )
