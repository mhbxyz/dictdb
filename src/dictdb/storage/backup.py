"""
This module implements an automatic backup system for DictDB.
It provides the BackupManager class which automatically saves the current state
of a DictDB instance periodically and/or after significant changes.

Supports both full backups and incremental (delta) backups for reduced I/O.
"""

import threading
import time
from pathlib import Path
from typing import Union, Callable, Optional

from .database import DictDB
from .persist import save_delta, has_changes
from ..obs.logging import logger


class BackupManager:
    """
    Manages automatic backups for a DictDB instance.

    The BackupManager supports periodic backups and immediate backups after
    significant changes. In incremental mode, only changes since the last
    backup are saved (delta files), with periodic full backups for compaction.
    """

    def __init__(
        self,
        db: DictDB,
        backup_dir: Union[str, Path],
        backup_interval: int = 300,
        file_format: str = "json",
        min_backup_interval: float = 5.0,
        on_backup_failure: Optional[Callable[[Exception, int], None]] = None,
        incremental: bool = False,
        max_deltas_before_full: int = 10,
    ) -> None:
        """
        Initializes the BackupManager.

        :param db: The DictDB instance to back up.
        :param backup_dir: The directory where backup files will be stored.
        :param backup_interval: The interval in seconds between periodic backups.
                                Default is 300 seconds.
        :param file_format: The file format for backups ("json" or "pickle").
                            Default is "json".
        :param min_backup_interval: Minimum interval in seconds between backups
                                    triggered by notify_change(). Default is 5.0.
        :param on_backup_failure: Optional callback invoked when a backup fails.
                                  Receives the exception and consecutive failure count.
        :param incremental: If True, use delta backups instead of full backups.
                           Periodic full backups still occur for compaction.
        :param max_deltas_before_full: Maximum number of delta files before
                                       forcing a full backup (compaction).
        """
        self.db = db
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_interval = backup_interval
        self.file_format = file_format.lower()
        self.min_backup_interval = min_backup_interval
        self._on_backup_failure = on_backup_failure
        self.incremental = incremental
        self.max_deltas_before_full = max_deltas_before_full
        self._stop_event = threading.Event()
        self._backup_thread = threading.Thread(
            target=self._run_periodic_backup, daemon=True
        )
        # Lock to serialize backup operations and prevent race conditions
        self._backup_lock = threading.Lock()
        # Track last backup time for debouncing notify_change() calls
        self._last_backup_time: float = 0.0
        # Track consecutive backup failures for alerting
        self._consecutive_failures: int = 0
        # Track deltas since last full backup for compaction
        self._deltas_since_full: int = 0

    def start(self) -> None:
        """
        Starts the automatic periodic backup thread.

        :return: None
        :rtype: None
        """
        logger.info("Starting automatic backup manager.")
        self._backup_thread.start()

    def stop(self) -> None:
        """
        Stops the automatic backup thread gracefully.

        :return: None
        :rtype: None
        """
        logger.info("Stopping automatic backup manager.")
        self._stop_event.set()
        self._backup_thread.join()

    def backup_now(self) -> None:
        """
        Performs an immediate backup of the current DictDB state.

        In incremental mode, saves a delta file if there are changes.
        Falls back to full backup if max_deltas_before_full is reached.
        In non-incremental mode, always performs a full backup.

        :return: None
        """
        if self.incremental:
            # Check if we need a full backup (compaction)
            if self._deltas_since_full >= self.max_deltas_before_full:
                self.backup_full()
            else:
                self.backup_delta()
        else:
            self.backup_full()

    def backup_full(self) -> None:
        """
        Performs a full backup of the entire database.

        The backup file is named with a timestamp (microsecond precision) and
        saved in the backup directory. Uses a lock to prevent concurrent backups.
        Resets the delta counter after successful backup.

        :return: None
        """
        with self._backup_lock:
            # Use microsecond precision to avoid filename collisions
            timestamp = f"{time.time():.6f}".replace(".", "_")
            filename = self.backup_dir / f"dictdb_backup_{timestamp}.{self.file_format}"
            logger.info(f"Performing full backup to {filename.name}.")
            try:
                self.db.save(str(filename), self.file_format)
                self._last_backup_time = time.time()
                self._consecutive_failures = 0
                self._deltas_since_full = 0
                logger.info(f"Full backup saved successfully to {filename.name}.")
            except Exception as e:
                self._consecutive_failures += 1
                logger.error(
                    f"Backup failed ({self._consecutive_failures} consecutive): {e}"
                )
                if self._on_backup_failure is not None:
                    try:
                        self._on_backup_failure(e, self._consecutive_failures)
                    except Exception as callback_err:
                        logger.error(f"Backup failure callback raised: {callback_err}")

    def backup_delta(self) -> None:
        """
        Performs an incremental (delta) backup of only changed records.

        Only saves changes since the last backup (inserts, updates, deletes).
        If there are no changes, the backup is skipped.
        Uses a lock to prevent concurrent backups.

        :return: None
        """
        with self._backup_lock:
            if not has_changes(self.db):
                logger.debug("No changes to backup, skipping delta.")
                return

            timestamp = f"{time.time():.6f}".replace(".", "_")
            filename = self.backup_dir / f"dictdb_delta_{timestamp}.json"
            logger.info(f"Performing delta backup to {filename.name}.")
            try:
                saved = save_delta(self.db, filename, clear_tracking=True)
                if saved:
                    self._last_backup_time = time.time()
                    self._consecutive_failures = 0
                    self._deltas_since_full += 1
                    logger.info(
                        f"Delta backup saved successfully to {filename.name} "
                        f"({self._deltas_since_full}/{self.max_deltas_before_full})."
                    )
                else:
                    logger.debug("No changes to backup after collection.")
            except Exception as e:
                self._consecutive_failures += 1
                logger.error(
                    f"Delta backup failed ({self._consecutive_failures} consecutive): {e}"
                )
                if self._on_backup_failure is not None:
                    try:
                        self._on_backup_failure(e, self._consecutive_failures)
                    except Exception as callback_err:
                        logger.error(f"Backup failure callback raised: {callback_err}")

    @property
    def consecutive_failures(self) -> int:
        """Returns the number of consecutive backup failures."""
        return self._consecutive_failures

    @property
    def deltas_since_full(self) -> int:
        """Returns the number of delta backups since the last full backup."""
        return self._deltas_since_full

    def notify_change(self) -> None:
        """
        Notifies the BackupManager of a significant change, triggering an immediate backup.

        Implements debouncing: if a backup occurred within min_backup_interval seconds,
        the backup is skipped to avoid excessive I/O from rapid changes.

        :return: None
        :rtype: None
        """
        with self._backup_lock:
            elapsed = time.time() - self._last_backup_time
            if elapsed < self.min_backup_interval:
                logger.debug(
                    f"Skipping backup, only {elapsed:.1f}s since last backup "
                    f"(min interval: {self.min_backup_interval}s)."
                )
                return
        logger.debug("Significant change detected. Triggering immediate backup.")
        self.backup_now()

    def _run_periodic_backup(self) -> None:
        """
        Internal method that runs in a background thread to perform periodic backups.

        :return: None
        :rtype: None
        """
        logger.info(
            f"Periodic backup thread started with interval {self.backup_interval} seconds."
        )
        while not self._stop_event.wait(self.backup_interval):
            logger.debug("Periodic backup triggered.")
            self.backup_now()
