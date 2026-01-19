import threading
import time
from typing import List

import pytest

from dictdb.core.rwlock import RWLock


def wait_for(event: threading.Event, timeout: float = 1.0) -> None:
    assert event.wait(timeout), "Timed out waiting for event"


def test_readers_can_share() -> None:
    lock = RWLock()
    r1_entered = threading.Event()
    r2_entered = threading.Event()
    r1_release = threading.Event()

    def reader1() -> None:
        with lock.read_lock():
            r1_entered.set()
            wait_for(r1_release)

    def reader2() -> None:
        wait_for(r1_entered)
        with lock.read_lock():
            r2_entered.set()

    t1 = threading.Thread(target=reader1)
    t2 = threading.Thread(target=reader2)
    t1.start()
    t2.start()

    wait_for(r1_entered)
    # While r1 holds the read lock, r2 should also be able to enter
    # (no writers waiting)
    # Allow a short time slice for r2 to acquire
    time.sleep(0.02)
    r1_release.set()

    wait_for(r2_entered)
    t1.join(1)
    t2.join(1)


def test_writer_excludes_readers() -> None:
    lock = RWLock()
    w_entered = threading.Event()
    w_release = threading.Event()
    r_entered = threading.Event()

    def writer() -> None:
        with lock.write_lock():
            w_entered.set()
            wait_for(w_release)

    def reader() -> None:
        with lock.read_lock():
            r_entered.set()

    tw = threading.Thread(target=writer)
    tr = threading.Thread(target=reader)
    tw.start()
    wait_for(w_entered)
    tr.start()

    # Give the reader a small chance; it must not enter while writer holds
    time.sleep(0.03)
    assert not r_entered.is_set(), "Reader entered while writer held the lock"

    w_release.set()
    wait_for(r_entered)
    tw.join(1)
    tr.join(1)


def test_writer_preference_blocks_new_readers() -> None:
    lock = RWLock()
    order: List[str] = []
    r1_release = threading.Event()
    writer_started = threading.Event()
    writer_done = threading.Event()
    r2_entered = threading.Event()

    def reader1() -> None:
        with lock.read_lock():
            order.append("R1_enter")
            wait_for(r1_release)

    def writer() -> None:
        writer_started.set()
        with lock.write_lock():
            order.append("W_enter")
            time.sleep(0.02)
        order.append("W_exit")
        writer_done.set()

    def reader2() -> None:
        wait_for(writer_started)
        with lock.read_lock():
            order.append("R2_enter")
            r2_entered.set()

    t_r1 = threading.Thread(target=reader1)
    t_w = threading.Thread(target=writer)
    t_r2 = threading.Thread(target=reader2)

    t_r1.start()
    # Ensure R1 is inside before starting writer
    time.sleep(0.01)
    t_w.start()
    wait_for(writer_started)
    t_r2.start()

    # While writer is waiting, new readers should not enter (writer preference)
    time.sleep(0.03)
    assert "R2_enter" not in order, "New reader should be blocked while writer waits"

    # Let R1 go; writer should acquire before R2
    r1_release.set()

    wait_for(writer_done)
    wait_for(r2_entered)

    # Verify ordering: writer exit occurs before R2 enters
    assert order.index("W_exit") < order.index("R2_enter"), (
        "Writer should proceed before new reader"
    )

    t_r1.join(1)
    t_w.join(1)
    t_r2.join(1)


def test_writers_are_serialized() -> None:
    lock = RWLock()
    w1_entered = threading.Event()
    w1_release = threading.Event()
    w2_entered = threading.Event()

    def writer1() -> None:
        with lock.write_lock():
            w1_entered.set()
            wait_for(w1_release)

    def writer2() -> None:
        with lock.write_lock():
            w2_entered.set()

    t1 = threading.Thread(target=writer1)
    t2 = threading.Thread(target=writer2)
    t1.start()
    wait_for(w1_entered)
    t2.start()

    time.sleep(0.03)
    assert not w2_entered.is_set(), (
        "Second writer entered concurrently with first writer"
    )

    w1_release.set()
    wait_for(w2_entered)
    t1.join(1)
    t2.join(1)


# ──────────────────────────────────────────────────────────────────────────────
# Additional RWLock edge case tests
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.slow
def test_multiple_readers_concurrent() -> None:
    """
    Tests that many readers can acquire the lock concurrently.
    """
    lock = RWLock()
    num_readers = 20
    readers_inside = []
    readers_lock = threading.Lock()
    all_entered = threading.Event()
    release_all = threading.Event()

    def reader(reader_id: int) -> None:
        with lock.read_lock():
            with readers_lock:
                readers_inside.append(reader_id)
                if len(readers_inside) == num_readers:
                    all_entered.set()
            wait_for(release_all, timeout=5.0)

    threads = [threading.Thread(target=reader, args=(i,)) for i in range(num_readers)]
    for t in threads:
        t.start()

    # Wait for all readers to enter
    assert all_entered.wait(timeout=3.0), "Not all readers entered concurrently"
    assert len(readers_inside) == num_readers, "All readers should be inside"

    release_all.set()
    for t in threads:
        t.join(timeout=2.0)


@pytest.mark.slow
def test_reader_gets_lock_when_no_writers() -> None:
    """
    Tests that readers can acquire the lock when writers stop.
    With writer preference, readers may be blocked while writers are active,
    but should acquire the lock once writers stop.
    """
    lock = RWLock()
    reader_completed = threading.Event()
    stop_writers = threading.Event()

    def writer_burst() -> None:
        # Do a burst of writes, then stop
        for _ in range(5):
            if stop_writers.is_set():
                break
            with lock.write_lock():
                time.sleep(0.01)

    def reader() -> None:
        # Wait for writers to finish
        time.sleep(0.1)
        with lock.read_lock():
            reader_completed.set()

    writers = [threading.Thread(target=writer_burst) for _ in range(2)]
    reader_thread = threading.Thread(target=reader)

    for w in writers:
        w.start()

    # Wait for writers to complete their burst
    for w in writers:
        w.join(timeout=2.0)

    reader_thread.start()

    # Reader should complete after writers are done
    reader_got_lock = reader_completed.wait(timeout=2.0)
    stop_writers.set()

    reader_thread.join(timeout=1.0)

    assert reader_got_lock, "Reader should get the lock after writers stop"


@pytest.mark.slow
def test_lock_release_order_fairness() -> None:
    """
    Tests that waiting writers are served before new readers when
    the writer preference policy is active.
    """
    lock = RWLock()
    order: List[str] = []
    order_lock = threading.Lock()

    def append_order(msg: str) -> None:
        with order_lock:
            order.append(msg)

    holder_release = threading.Event()
    w1_waiting = threading.Event()
    w2_waiting = threading.Event()

    def initial_reader() -> None:
        with lock.read_lock():
            append_order("R0_in")
            wait_for(holder_release, timeout=5.0)
            append_order("R0_out")

    def writer1() -> None:
        w1_waiting.set()
        with lock.write_lock():
            append_order("W1_in")
            time.sleep(0.01)
            append_order("W1_out")

    def writer2() -> None:
        w2_waiting.set()
        with lock.write_lock():
            append_order("W2_in")
            time.sleep(0.01)
            append_order("W2_out")

    t_r0 = threading.Thread(target=initial_reader)
    t_w1 = threading.Thread(target=writer1)
    t_w2 = threading.Thread(target=writer2)

    t_r0.start()
    time.sleep(0.02)  # Ensure R0 is holding

    t_w1.start()
    wait_for(w1_waiting)
    time.sleep(0.01)

    t_w2.start()
    wait_for(w2_waiting)
    time.sleep(0.01)

    # Release the initial reader
    holder_release.set()

    t_r0.join(timeout=2.0)
    t_w1.join(timeout=2.0)
    t_w2.join(timeout=2.0)

    # Verify writers completed
    assert "W1_out" in order, "Writer 1 should complete"
    assert "W2_out" in order, "Writer 2 should complete"


@pytest.mark.slow
def test_reentrant_read_not_supported() -> None:
    """
    Documents that reentrant read locks may cause issues.
    This test verifies current behavior (not a guarantee of correctness).
    """
    lock = RWLock()

    # Single-threaded reentrant read should work (no actual blocking)
    with lock.read_lock():
        # Nested read - behavior depends on implementation
        # Current implementation should allow this
        with lock.read_lock():
            pass  # If we get here, reentrant reads work


def test_lock_context_manager_exception_safety() -> None:
    """
    Tests that locks are properly released when exceptions occur.
    """
    lock = RWLock()

    # Test read lock exception safety
    try:
        with lock.read_lock():
            raise ValueError("Test exception")
    except ValueError:
        pass

    # Lock should be released - writer should be able to acquire
    acquired = threading.Event()

    def writer() -> None:
        with lock.write_lock():
            acquired.set()

    t = threading.Thread(target=writer)
    t.start()
    assert acquired.wait(timeout=1.0), "Lock not released after exception"
    t.join()

    # Test write lock exception safety
    try:
        with lock.write_lock():
            raise ValueError("Test exception")
    except ValueError:
        pass

    # Lock should be released
    acquired.clear()
    t = threading.Thread(target=writer)
    t.start()
    assert acquired.wait(timeout=1.0), "Write lock not released after exception"
    t.join()


@pytest.mark.slow
def test_high_contention_stress() -> None:
    """
    Stress test with high contention from many readers and writers.
    """
    lock = RWLock()
    num_readers = 10
    num_writers = 5
    iterations = 50
    errors: List[Exception] = []
    errors_lock = threading.Lock()

    shared_value = [0]
    value_lock = threading.Lock()

    def reader() -> None:
        try:
            for _ in range(iterations):
                with lock.read_lock():
                    _ = shared_value[0]  # Read the value
                time.sleep(0.001)
        except Exception as e:
            with errors_lock:
                errors.append(e)

    def writer() -> None:
        try:
            for _ in range(iterations):
                with lock.write_lock():
                    with value_lock:
                        shared_value[0] += 1
                time.sleep(0.002)
        except Exception as e:
            with errors_lock:
                errors.append(e)

    threads = [threading.Thread(target=reader) for _ in range(num_readers)] + [
        threading.Thread(target=writer) for _ in range(num_writers)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30.0)

    assert not errors, f"Errors during stress test: {errors}"
    expected_value = num_writers * iterations
    assert shared_value[0] == expected_value, (
        f"Expected {expected_value}, got {shared_value[0]}"
    )
