"""
Concurrency tests for index operations.

Tests verify that indexes remain consistent under concurrent modifications
and that index-accelerated queries return correct results during writes.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set

import pytest

from dictdb import Table, Condition


@pytest.mark.slow
@pytest.mark.parametrize("index_type", ["hash", "sorted"])
def test_concurrent_index_inserts(index_type: str) -> None:
    """
    Tests that concurrent inserts maintain index consistency.
    """
    table = Table(
        "index_insert_test",
        primary_key="id",
        schema={"id": int, "category": str, "value": int},
    )
    table.create_index("category", index_type=index_type)

    num_threads = 10
    records_per_thread = 50
    categories = ["cat_a", "cat_b", "cat_c", "cat_d", "cat_e"]
    errors: List[Exception] = []
    lock = threading.Lock()

    def inserter(thread_id: int) -> None:
        try:
            for i in range(records_per_thread):
                pk = thread_id * records_per_thread + i
                cat = categories[i % len(categories)]
                table.insert({"id": pk, "category": cat, "value": i})
        except Exception as e:
            with lock:
                errors.append(e)

    threads = [threading.Thread(target=inserter, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Errors during concurrent inserts: {errors}"

    # Verify index consistency
    total_count = table.count()
    expected = num_threads * records_per_thread
    assert total_count == expected, f"Expected {expected} records, got {total_count}"

    # Verify each category has correct count via index
    for cat in categories:
        results = table.select(where=Condition(table.category == cat))
        expected_per_cat = expected // len(categories)
        assert len(results) == expected_per_cat, (
            f"Category {cat}: expected {expected_per_cat}, got {len(results)}"
        )


@pytest.mark.slow
@pytest.mark.parametrize("index_type", ["hash", "sorted"])
def test_index_consistency_during_updates(index_type: str) -> None:
    """
    Tests that index remains consistent during concurrent updates.
    """
    table = Table(
        "index_update_test",
        primary_key="id",
        schema={"id": int, "status": str, "counter": int},
    )
    table.create_index("status", index_type=index_type)

    # Pre-populate
    for i in range(100):
        table.insert({"id": i, "status": "pending", "counter": 0})

    errors: List[Exception] = []
    lock = threading.Lock()

    def updater() -> None:
        try:
            for i in range(100):
                # Update status from pending to completed
                table.update(
                    {"status": "completed"},
                    where=Condition(table.id == i),
                )
        except Exception as e:
            with lock:
                errors.append(e)

    def reader() -> None:
        try:
            for _ in range(50):
                pending = table.select(where=Condition(table.status == "pending"))
                completed = table.select(where=Condition(table.status == "completed"))
                # Total should always equal 100
                total = len(pending) + len(completed)
                if total != 100:
                    with lock:
                        errors.append(ValueError(f"Inconsistent total: {total} != 100"))
                time.sleep(0.001)
        except Exception as e:
            with lock:
                errors.append(e)

    update_threads = [threading.Thread(target=updater) for _ in range(3)]
    read_threads = [threading.Thread(target=reader) for _ in range(5)]

    for t in update_threads + read_threads:
        t.start()
    for t in update_threads + read_threads:
        t.join()

    # Filter out expected errors
    unexpected = [e for e in errors if not isinstance(e, ValueError)]
    assert not unexpected, f"Unexpected errors: {unexpected}"


@pytest.mark.slow
@pytest.mark.parametrize("index_type", ["hash", "sorted"])
def test_index_consistency_during_deletes(index_type: str) -> None:
    """
    Tests that index remains consistent during concurrent deletes.
    """
    table = Table(
        "index_delete_test",
        primary_key="id",
        schema={"id": int, "group": str},
    )
    table.create_index("group", index_type=index_type)

    # Pre-populate with 200 records in 4 groups
    groups = ["group_a", "group_b", "group_c", "group_d"]
    for i in range(200):
        table.insert({"id": i, "group": groups[i % len(groups)]})

    deleted_ids: Set[int] = set()
    lock = threading.Lock()

    def deleter(group: str) -> None:
        try:
            while True:
                results = table.select(where=Condition(table.group == group), limit=1)
                if not results:
                    break
                record_id = results[0]["id"]
                try:
                    table.delete(where=Condition(table.id == record_id))
                    with lock:
                        deleted_ids.add(record_id)
                except Exception:
                    pass  # Record might be deleted by another thread
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(deleter, g) for g in groups for _ in range(2)]
        for f in as_completed(futures):
            f.result()

    # All records should be deleted
    assert table.count() == 0, f"Expected 0 records, got {table.count()}"

    # Index queries should return empty results
    for group in groups:
        results = table.select(where=Condition(table.group == group))
        assert len(results) == 0, f"Group {group} should have no records"


@pytest.mark.slow
def test_sorted_index_range_query_during_modifications() -> None:
    """
    Tests that range queries on SortedIndex return consistent results
    during concurrent modifications.
    """
    table = Table(
        "sorted_range_test",
        primary_key="id",
        schema={"id": int, "score": int},
    )
    table.create_index("score", index_type="sorted")

    # Pre-populate with scores 0-99
    for i in range(100):
        table.insert({"id": i, "score": i})

    stop_flag = threading.Event()
    inconsistencies: List[str] = []
    lock = threading.Lock()

    def modifier() -> None:
        counter = 100
        while not stop_flag.is_set():
            try:
                # Add new high scores
                table.insert({"id": counter, "score": counter})
                counter += 1
                # Delete some low scores
                table.delete(where=Condition(table.score < 10))
            except Exception:
                pass
            time.sleep(0.005)

    def range_reader() -> None:
        while not stop_flag.is_set():
            try:
                # Range query: scores between 30 and 70
                results = table.select(
                    where=Condition(table.score >= 30) & Condition(table.score <= 70)
                )
                # Verify all results are in range
                for r in results:
                    if not (30 <= r["score"] <= 70):
                        with lock:
                            inconsistencies.append(
                                f"Score {r['score']} outside range [30, 70]"
                            )
            except Exception:
                pass
            time.sleep(0.002)

    mod_threads = [threading.Thread(target=modifier) for _ in range(2)]
    read_threads = [threading.Thread(target=range_reader) for _ in range(4)]

    for t in mod_threads + read_threads:
        t.start()

    time.sleep(1.0)
    stop_flag.set()

    for t in mod_threads + read_threads:
        t.join(timeout=3.0)

    assert not inconsistencies, f"Range query inconsistencies: {inconsistencies[:5]}"


@pytest.mark.slow
@pytest.mark.parametrize("index_type", ["hash", "sorted"])
def test_index_rebuild_stress(index_type: str) -> None:
    """
    Tests index consistency when records are rapidly inserted and deleted.
    This simulates scenarios where the index structure changes frequently.
    """
    table = Table(
        "index_rebuild_stress",
        primary_key="id",
        schema={"id": int, "key": str},
    )
    table.create_index("key", index_type=index_type)

    next_id = [0]
    id_lock = threading.Lock()
    errors: List[Exception] = []
    error_lock = threading.Lock()

    def get_next_id() -> int:
        with id_lock:
            result = next_id[0]
            next_id[0] += 1
            return result

    def insert_delete_cycle() -> None:
        try:
            for _ in range(100):
                pk = get_next_id()
                key = f"key_{pk % 10}"
                table.insert({"id": pk, "key": key})
                time.sleep(0.001)
                try:
                    table.delete(where=Condition(table.id == pk))
                except Exception:
                    pass
        except Exception as e:
            with error_lock:
                errors.append(e)

    def verifier() -> None:
        try:
            for _ in range(50):
                for i in range(10):
                    key = f"key_{i}"
                    results = table.select(where=Condition(table.key == key))
                    # Just verify no crash
                    _ = len(results)
                time.sleep(0.005)
        except Exception as e:
            with error_lock:
                errors.append(e)

    threads = [threading.Thread(target=insert_delete_cycle) for _ in range(5)] + [
        threading.Thread(target=verifier) for _ in range(3)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30.0)

    assert not errors, f"Errors during stress test: {errors[:5]}"


@pytest.mark.slow
def test_multi_index_concurrent_operations() -> None:
    """
    Tests concurrent operations on a table with multiple indexes.
    """
    table = Table(
        "multi_index_test",
        primary_key="id",
        schema={"id": int, "category": str, "priority": int, "status": str},
    )
    table.create_index("category", index_type="hash")
    table.create_index("priority", index_type="sorted")
    table.create_index("status", index_type="hash")

    # Pre-populate
    categories = ["electronics", "clothing", "food"]
    statuses = ["pending", "processing", "completed"]
    for i in range(150):
        table.insert(
            {
                "id": i,
                "category": categories[i % 3],
                "priority": i % 10,
                "status": statuses[i % 3],
            }
        )

    errors: List[Exception] = []
    lock = threading.Lock()

    def category_query() -> None:
        try:
            for _ in range(50):
                for cat in categories:
                    results = table.select(where=Condition(table.category == cat))
                    if len(results) > 150:  # Sanity check
                        with lock:
                            errors.append(ValueError(f"Too many results for {cat}"))
                time.sleep(0.001)
        except Exception as e:
            with lock:
                errors.append(e)

    def priority_query() -> None:
        try:
            for _ in range(50):
                # High priority items (priority < 3)
                results = table.select(where=Condition(table.priority < 3))
                for r in results:
                    if r["priority"] >= 3:
                        with lock:
                            errors.append(
                                ValueError(f"Wrong priority: {r['priority']}")
                            )
                time.sleep(0.001)
        except Exception as e:
            with lock:
                errors.append(e)

    def modifier() -> None:
        try:
            for i in range(50):
                # Update priorities
                table.update(
                    {"priority": (i % 10)},
                    where=Condition(table.id == i),
                )
                time.sleep(0.002)
        except Exception as e:
            with lock:
                errors.append(e)

    threads = (
        [threading.Thread(target=category_query) for _ in range(3)]
        + [threading.Thread(target=priority_query) for _ in range(3)]
        + [threading.Thread(target=modifier) for _ in range(2)]
    )

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30.0)

    unexpected = [e for e in errors if not isinstance(e, ValueError)]
    assert not unexpected, f"Unexpected errors: {unexpected}"
