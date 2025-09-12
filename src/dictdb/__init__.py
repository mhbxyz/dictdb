from importlib.metadata import PackageNotFoundError, version as _pkg_version

from .storage.backup import BackupManager
from .core.condition import Condition
from .core.table import Table
from .storage.database import DictDB
from .exceptions import DuplicateKeyError, RecordNotFoundError, SchemaValidationError
from .obs.logging import logger, configure_logging

# Expose the installed package version dynamically to avoid duplication.
try:
    __version__ = _pkg_version("dictdb")
except (
    PackageNotFoundError
):  # pragma: no cover - during editable installs or local runs
    __version__ = "0.0.0"

__all__ = [
    "DictDB",
    "Table",
    "Condition",
    "DuplicateKeyError",
    "RecordNotFoundError",
    "SchemaValidationError",
    "logger",
    "configure_logging",
    "BackupManager",
    "__version__",
]
