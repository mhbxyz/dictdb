"""
This module implements an automatic backup system for DictDB.
It provides the BackupManager class which automatically saves the current state
of a DictDB instance periodically and/or after significant changes.
"""

import threading
import time
from pathlib import Path
from typing import Union

from .database import DictDB
from .logging import logger


class BackupManager:
    """
    Manages automatic backups for a DictDB instance.

    The BackupManager supports periodic backups and immediate backups after
    significant changes.
    """

    def __init__(
        self,
        db: DictDB,
        backup_dir: Union[str, Path],
        backup_interval: int = 300,
        file_format: str = "json"
    ) -> None:
        """
        Initializes the BackupManager.

        :param db: The DictDB instance to back up.
        :type db: DictDB
        :param backup_dir: The directory where backup files will be stored.
        :type backup_dir: Union[str, Path]
        :param backup_interval: The interval in seconds between periodic backups.
                                Default is 300 seconds.
        :type backup_interval: int
        :param file_format: The file format for backups ("json" or "pickle").
                            Default is "json".
        :type file_format: str
        """
        self.db = db
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_interval = backup_interval
        self.file_format = file_format.lower()
        self._stop_event = threading.Event()
        self._backup_thread = threading.Thread(
            target=self._run_periodic_backup, daemon=True
        )

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

        The backup file is named with a timestamp and saved in the backup directory.

        :return: None
        :rtype: None
        """
        timestamp = int(time.time())
        filename = self.backup_dir / f"dictdb_backup_{timestamp}.{self.file_format}"
        logger.info(f"Performing immediate backup to {filename}.")
        try:
            self.db.save(str(filename), self.file_format)
            logger.info(f"Backup saved successfully to {filename}.")
        except Exception as e:
            logger.error(f"Backup failed: {e}")

    def notify_change(self) -> None:
        """
        Notifies the BackupManager of a significant change, triggering an immediate backup.

        :return: None
        :rtype: None
        """
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
