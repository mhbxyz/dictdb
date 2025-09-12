import threading
import time
from typing import List

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
    assert order.index("W_exit") < order.index("R2_enter"), "Writer should proceed before new reader"

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
    assert not w2_entered.is_set(), "Second writer entered concurrently with first writer"

    w1_release.set()
    wait_for(w2_entered)
    t1.join(1)
    t2.join(1)

