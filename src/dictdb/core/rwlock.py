"""
Minimal reader-writer lock used to guard table operations.

Design
- Concurrency: multiple readers may enter concurrently; writers get exclusive access.
- Writer preference: new readers block while any writer is waiting to avoid writer starvation.
- Fairness: simple, not strictly fair; under heavy write load readers may be delayed.
- Scope: thread-level only (single process). Not re-entrant.

Implementation Notes
- Backed by a single `Condition` and counters guarding three states:
  - `_readers`: active reader count
  - `_writer`: whether a writer holds the lock
  - `_writers_waiting`: waiting writers (to prioritize writers)
- `acquire_read()` waits while a writer is active OR any writer is waiting.
- `acquire_write()` increments waiting count, then waits until no readers and no writer.
- Context managers `read_lock()` and `write_lock()` provide ergonomic usage:
    with rwlock.read_lock():
        ...  # read-only critical section
    with rwlock.write_lock():
        ...  # mutating critical section
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator


class RWLock:
    """
    Reader-writer lock with writer preference.

    Invariants
    - While `_writer` is True, `_readers == 0`.
    - Readers can enter concurrently only when `_writer` is False and no writer is waiting.
    - Writers are serialized and exclude readers.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._readers = 0
        self._writer = False
        self._writers_waiting = 0

    def acquire_read(self) -> None:
        """Acquire a shared/read lock.

        Blocks if a writer holds the lock or if any writers are waiting
        (writer preference to reduce writer starvation).
        """
        with self._lock:
            # Prefer writers: block if a writer is active or waiting
            while self._writer or self._writers_waiting > 0:
                self._cond.wait()
            self._readers += 1

    def release_read(self) -> None:
        """Release a previously acquired read lock."""
        with self._lock:
            self._readers -= 1
            if self._readers == 0 and self._writers_waiting > 0:
                # Wake one waiting writer (avoids thundering herd)
                self._cond.notify()

    def acquire_write(self) -> None:
        """Acquire an exclusive/write lock.

        Increments the waiting-writer count to block new readers, then
        waits until all readers and writers have exited.
        """
        with self._lock:
            self._writers_waiting += 1
            while self._writer or self._readers > 0:
                self._cond.wait()
            self._writers_waiting -= 1
            self._writer = True

    def release_write(self) -> None:
        """Release a previously acquired write lock and wake waiters."""
        with self._lock:
            self._writer = False
            if self._writers_waiting > 0:
                # Wake one waiting writer (avoids thundering herd)
                self._cond.notify()
            else:
                # Wake all waiting readers
                self._cond.notify_all()

    @contextmanager
    def read_lock(self) -> Iterator[None]:
        """Context manager for a read section."""
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self) -> Iterator[None]:
        """Context manager for a write section."""
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()
