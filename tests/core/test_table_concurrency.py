"""
Concurrency tests for Table operations.

Tests verify thread-safety of CRUD operations under concurrent access,
ensuring data consistency and proper lock behavior.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set

import pytest

from dictdb import Table, Condition, DuplicateKeyError, RecordNotFoundError


# ──────────────────────────────────────────────────────────────────────────────
# Concurrent INSERT tests
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.slow
def test_concurrent_inserts_unique_pks() -> None:
    """
    Tests that concurrent inserts with unique PKs all succeed.
    Each thread inserts records with non-overlapping IDs.
    """
    table = Table("concurrent_insert", primary_key="id")
    num_threads = 10
    records_per_thread = 100
    errors: List[Exception] = []

    def insert_records(thread_id: int) -> None:
        try:
            for i in range(records_per_thread):
                pk = thread_id * records_per_thread + i
                table.insert({"id": pk, "thread": thread_id, "value": i})
        except Exception as e:
            errors.append(e)

    threads = [
        threading.Thread(target=insert_records, args=(t,)) for t in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Unexpected errors during concurrent inserts: {errors}"
    expected_count = num_threads * records_per_thread
    assert table.count() == expected_count, (
        f"Expected {expected_count} records, got {table.count()}"
    )


@pytest.mark.slow
def test_concurrent_inserts_auto_pk() -> None:
    """
    Tests that concurrent inserts with auto-generated PKs produce unique keys.
    """
    table = Table("concurrent_auto_pk", primary_key="id")
    num_threads = 10
    records_per_thread = 50
    inserted_pks: List[int] = []
    lock = threading.Lock()

    def insert_records() -> None:
        local_pks = []
        for i in range(records_per_thread):
            record = {"value": i}
            table.insert(record)
            local_pks.append(record["id"])
        with lock:
            inserted_pks.extend(local_pks)

    threads = [threading.Thread(target=insert_records) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All PKs should be unique
    assert len(inserted_pks) == len(set(inserted_pks)), (
        "Auto-generated PKs are not unique"
    )
    assert table.count() == num_threads * records_per_thread


@pytest.mark.slow
def test_concurrent_inserts_duplicate_pk_rejected() -> None:
    """
    Tests that concurrent inserts with the same PK result in exactly one success.
    """
    table = Table("concurrent_dup", primary_key="id")
    target_pk = 42
    num_threads = 20
    successes = []
    failures = []
    lock = threading.Lock()

    def try_insert(thread_id: int) -> None:
        try:
            table.insert({"id": target_pk, "thread": thread_id})
            with lock:
                successes.append(thread_id)
        except DuplicateKeyError:
            with lock:
                failures.append(thread_id)

    threads = [
        threading.Thread(target=try_insert, args=(t,)) for t in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}"
    assert len(failures) == num_threads - 1, (
        "Other threads should fail with DuplicateKeyError"
    )
    assert table.count() == 1


# ──────────────────────────────────────────────────────────────────────────────
# Concurrent SELECT tests
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.slow
def test_concurrent_selects_consistent() -> None:
    """
    Tests that concurrent selects return consistent data.
    """
    table = Table("concurrent_select", primary_key="id")
    for i in range(100):
        table.insert({"id": i, "value": i * 10})

    results: List[int] = []
    lock = threading.Lock()

    def select_all() -> None:
        records = table.select()
        with lock:
            results.append(len(records))

    threads = [threading.Thread(target=select_all) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All selects should return 100 records
    assert all(r == 100 for r in results), (
        f"Inconsistent select results: {set(results)}"
    )


@pytest.mark.slow
def test_select_during_inserts() -> None:
    """
    Tests that selects during concurrent inserts see consistent snapshots.
    Records should not appear partially constructed.
    """
    table = Table(
        "select_during_insert",
        primary_key="id",
        schema={"id": int, "name": str, "value": int},
    )
    stop_flag = threading.Event()
    inconsistencies: List[str] = []
    lock = threading.Lock()

    def inserter() -> None:
        i = 0
        while not stop_flag.is_set():
            try:
                table.insert({"id": i, "name": f"record_{i}", "value": i * 10})
                i += 1
            except DuplicateKeyError:
                pass
            time.sleep(0.001)

    def reader() -> None:
        while not stop_flag.is_set():
            records = table.select()
            for rec in records:
                # Verify record integrity
                if "id" not in rec or "name" not in rec or "value" not in rec:
                    with lock:
                        inconsistencies.append(f"Incomplete record: {rec}")
                elif rec["value"] != rec["id"] * 10:
                    with lock:
                        inconsistencies.append(f"Inconsistent values: {rec}")
            time.sleep(0.001)

    insert_threads = [threading.Thread(target=inserter) for _ in range(3)]
    read_threads = [threading.Thread(target=reader) for _ in range(5)]

    for t in insert_threads + read_threads:
        t.start()

    time.sleep(1.0)  # Run for 1 second
    stop_flag.set()

    for t in insert_threads + read_threads:
        t.join()

    assert not inconsistencies, f"Found inconsistencies: {inconsistencies[:5]}"


# ──────────────────────────────────────────────────────────────────────────────
# Concurrent UPDATE tests
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.slow
def test_concurrent_updates_same_record() -> None:
    """
    Tests that concurrent updates to the same record are serialized.
    The final value should be from one of the updates.
    """
    table = Table("concurrent_update", primary_key="id")
    table.insert({"id": 1, "counter": 0})

    num_updates = 100
    barrier = threading.Barrier(10)

    def updater(value: int) -> None:
        barrier.wait()  # Synchronize all threads to start together
        try:
            table.update({"counter": value}, where=Condition(table.id == 1))
        except RecordNotFoundError:
            pass  # Record might be deleted by another test

    threads = [threading.Thread(target=updater, args=(i,)) for i in range(num_updates)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    records = table.select(where=Condition(table.id == 1))
    assert len(records) == 1, "Record should still exist"
    # Counter should be one of the values that was set
    assert 0 <= records[0]["counter"] < num_updates


@pytest.mark.slow
def test_concurrent_updates_different_records() -> None:
    """
    Tests that updates to different records can proceed concurrently.
    """
    table = Table("concurrent_update_diff", primary_key="id")
    num_records = 50
    for i in range(num_records):
        table.insert({"id": i, "value": 0})

    def update_record(record_id: int) -> None:
        for _ in range(10):
            table.update(
                {"value": record_id * 100},
                where=Condition(table.id == record_id),
            )

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_record, i) for i in range(num_records)]
        for f in as_completed(futures):
            f.result()  # Raise any exceptions

    # Verify all records have correct values
    for i in range(num_records):
        records = table.select(where=Condition(table.id == i))
        assert len(records) == 1
        assert records[0]["value"] == i * 100, f"Record {i} has wrong value"


@pytest.mark.slow
def test_concurrent_increment_counter() -> None:
    """
    Tests concurrent increments of a counter field.
    Due to race conditions without transactions, the final count may be less
    than expected (this documents current behavior, not a bug).
    """
    table = Table("counter_test", primary_key="id")
    table.insert({"id": 1, "counter": 0})

    num_threads = 10
    increments_per_thread = 50
    successful_increments = []
    lock = threading.Lock()

    def increment() -> None:
        local_count = 0
        for _ in range(increments_per_thread):
            try:
                records = table.select(where=Condition(table.id == 1))
                if records:
                    current = records[0]["counter"]
                    table.update(
                        {"counter": current + 1}, where=Condition(table.id == 1)
                    )
                    local_count += 1
            except (RecordNotFoundError, IndexError):
                pass
        with lock:
            successful_increments.append(local_count)

    threads = [threading.Thread(target=increment) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    records = table.select(where=Condition(table.id == 1))
    final_counter = records[0]["counter"]

    # Due to read-modify-write race, final counter <= total increments
    total_attempts = sum(successful_increments)
    assert final_counter <= total_attempts, "Counter exceeded attempted increments"
    assert final_counter > 0, "At least some increments should succeed"


# ──────────────────────────────────────────────────────────────────────────────
# Concurrent DELETE tests
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.slow
def test_concurrent_deletes_same_record() -> None:
    """
    Tests that concurrent deletes of the same record result in exactly one success.
    """
    table = Table("concurrent_delete", primary_key="id")
    table.insert({"id": 1, "value": "target"})

    num_threads = 20
    successes = []
    failures = []
    lock = threading.Lock()
    barrier = threading.Barrier(num_threads)

    def try_delete(thread_id: int) -> None:
        barrier.wait()
        try:
            deleted = table.delete(where=Condition(table.id == 1))
            with lock:
                successes.append((thread_id, deleted))
        except RecordNotFoundError:
            with lock:
                failures.append(thread_id)

    threads = [
        threading.Thread(target=try_delete, args=(t,)) for t in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(successes) == 1, (
        f"Expected exactly 1 successful delete, got {len(successes)}"
    )
    assert successes[0][1] == 1, "Successful delete should report 1 record deleted"
    assert table.count() == 0, "Table should be empty"


@pytest.mark.slow
def test_concurrent_deletes_different_records() -> None:
    """
    Tests that concurrent deletes of different records all succeed.
    """
    table = Table("concurrent_delete_diff", primary_key="id")
    num_records = 100
    for i in range(num_records):
        table.insert({"id": i, "value": i})

    deleted_ids: Set[int] = set()
    lock = threading.Lock()

    def delete_record(record_id: int) -> None:
        try:
            table.delete(where=Condition(table.id == record_id))
            with lock:
                deleted_ids.add(record_id)
        except RecordNotFoundError:
            pass

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(delete_record, i) for i in range(num_records)]
        for f in as_completed(futures):
            f.result()

    assert len(deleted_ids) == num_records, "All deletes should succeed"
    assert table.count() == 0, "Table should be empty"


# ──────────────────────────────────────────────────────────────────────────────
# Mixed CRUD operations
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.slow
def test_mixed_crud_stress() -> None:
    """
    Stress test with mixed INSERT/SELECT/UPDATE/DELETE operations.
    Verifies no crashes, deadlocks, or data corruption.
    """
    table = Table(
        "stress_test",
        primary_key="id",
        schema={"id": int, "value": int, "status": str},
    )
    # Pre-populate with some records
    for i in range(100):
        table.insert({"id": i, "value": i, "status": "initial"})

    stop_flag = threading.Event()
    errors: List[Exception] = []
    lock = threading.Lock()
    next_id = [100]  # Mutable container for next insert ID

    def inserter() -> None:
        while not stop_flag.is_set():
            try:
                with lock:
                    new_id = next_id[0]
                    next_id[0] += 1
                table.insert({"id": new_id, "value": new_id, "status": "new"})
            except Exception as e:
                with lock:
                    errors.append(e)
            time.sleep(0.001)

    def reader() -> None:
        while not stop_flag.is_set():
            try:
                records = table.select(where=Condition(table.status == "initial"))
                # Just iterate to ensure no crash
                for _ in records:
                    pass
            except Exception as e:
                with lock:
                    errors.append(e)
            time.sleep(0.001)

    def updater() -> None:
        while not stop_flag.is_set():
            try:
                table.update(
                    {"status": "updated"},
                    where=Condition(table.value < 50),
                )
            except RecordNotFoundError:
                pass  # Expected if all records already updated/deleted
            except Exception as e:
                with lock:
                    errors.append(e)
            time.sleep(0.005)

    def deleter() -> None:
        while not stop_flag.is_set():
            try:
                table.delete(where=Condition(table.value > 150))
            except RecordNotFoundError:
                pass  # Expected if no matching records
            except Exception as e:
                with lock:
                    errors.append(e)
            time.sleep(0.01)

    threads = (
        [threading.Thread(target=inserter) for _ in range(3)]
        + [threading.Thread(target=reader) for _ in range(5)]
        + [threading.Thread(target=updater) for _ in range(2)]
        + [threading.Thread(target=deleter) for _ in range(2)]
    )

    for t in threads:
        t.start()

    time.sleep(2.0)  # Run stress test for 2 seconds
    stop_flag.set()

    for t in threads:
        t.join(timeout=5.0)

    # Filter out expected errors
    unexpected_errors = [
        e for e in errors if not isinstance(e, (RecordNotFoundError, DuplicateKeyError))
    ]
    assert not unexpected_errors, f"Unexpected errors: {unexpected_errors[:5]}"


@pytest.mark.slow
def test_no_deadlock_on_multiple_tables() -> None:
    """
    Tests that operations on multiple tables don't cause deadlocks.
    """
    table1 = Table("deadlock_test_1", primary_key="id")
    table2 = Table("deadlock_test_2", primary_key="id")

    for i in range(50):
        table1.insert({"id": i, "ref": i})
        table2.insert({"id": i, "ref": i})

    deadlock_detected = threading.Event()

    def worker_a() -> None:
        for i in range(20):
            try:
                # Access table1 then table2
                table1.update({"ref": i * 2}, where=Condition(table1.id == i % 50))
                table2.update({"ref": i * 2}, where=Condition(table2.id == i % 50))
            except RecordNotFoundError:
                pass

    def worker_b() -> None:
        for i in range(20):
            try:
                # Access table2 then table1 (opposite order)
                table2.update({"ref": i * 3}, where=Condition(table2.id == i % 50))
                table1.update({"ref": i * 3}, where=Condition(table1.id == i % 50))
            except RecordNotFoundError:
                pass

    threads = [threading.Thread(target=worker_a) for _ in range(5)] + [
        threading.Thread(target=worker_b) for _ in range(5)
    ]

    for t in threads:
        t.start()

    # Wait with timeout to detect deadlock
    for t in threads:
        t.join(timeout=10.0)
        if t.is_alive():
            deadlock_detected.set()
            break

    assert not deadlock_detected.is_set(), (
        "Deadlock detected - threads did not complete"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Read consistency tests
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.slow
def test_select_returns_copy_not_reference() -> None:
    """
    Tests that select() returns copies of records, not references.
    Modifications to returned records should not affect table data.
    """
    table = Table("copy_test", primary_key="id")
    table.insert({"id": 1, "value": "original"})

    def modifier() -> None:
        for _ in range(100):
            records = table.select(where=Condition(table.id == 1))
            if records:
                records[0]["value"] = "modified_by_reader"

    def verifier() -> None:
        for _ in range(100):
            records = table.select(where=Condition(table.id == 1))
            if records:
                # Value should still be original unless properly updated
                assert records[0]["value"] in ("original", "modified_by_reader")

    threads = [threading.Thread(target=modifier) for _ in range(5)] + [
        threading.Thread(target=verifier) for _ in range(5)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Table data should be unchanged (because select returns copies by default)
    records = table.select(where=Condition(table.id == 1))
    assert records[0]["value"] == "original", "Table data was unexpectedly modified"


@pytest.mark.slow
def test_iteration_stability() -> None:
    """
    Tests that iterating over select results is stable even during modifications.
    """
    table = Table("iteration_test", primary_key="id")
    for i in range(100):
        table.insert({"id": i, "value": i})

    iteration_errors: List[str] = []
    lock = threading.Lock()

    def iterator() -> None:
        try:
            records = table.select()
            total = 0
            for rec in records:
                total += rec["value"]
                time.sleep(0.0001)  # Slow iteration
            # Total should be consistent for the snapshot we got
        except Exception as e:
            with lock:
                iteration_errors.append(str(e))

    def modifier() -> None:
        for i in range(50):
            try:
                table.update({"value": i * 1000}, where=Condition(table.id == i))
            except RecordNotFoundError:
                pass

    iter_threads = [threading.Thread(target=iterator) for _ in range(5)]
    mod_threads = [threading.Thread(target=modifier) for _ in range(3)]

    for t in iter_threads + mod_threads:
        t.start()
    for t in iter_threads + mod_threads:
        t.join()

    assert not iteration_errors, f"Iteration errors: {iteration_errors}"
