from __future__ import annotations

import json
import pickle
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Dict, Union, BinaryIO, Optional

from .database import DictDB
from ..core.table import Table
from ..core.types import parse_schema_type, serialize_schema_type


# Whitelist of classes allowed for pickle deserialization.
# This prevents arbitrary code execution from malicious pickle files.
_PICKLE_ALLOWED_MODULES: Dict[str, set[str]] = {
    "builtins": {
        "dict",
        "list",
        "set",
        "frozenset",
        "tuple",
        "str",
        "int",
        "float",
        "bool",
        "bytes",
        "type",
    },
    "dictdb.storage.database": {"DictDB"},
    "dictdb.core.table": {"Table"},
}


class _RestrictedUnpickler(pickle.Unpickler):
    """Unpickler that only allows whitelisted classes to prevent RCE attacks."""

    def find_class(self, module: str, name: str) -> Any:
        allowed_names = _PICKLE_ALLOWED_MODULES.get(module, set())
        if name in allowed_names:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(
            f"Deserialization of '{module}.{name}' is not allowed. "
            "Only whitelisted classes can be loaded from pickle files."
        )


def _safe_pickle_load(f: BinaryIO) -> Any:
    """Load a pickle file using the restricted unpickler."""
    return _RestrictedUnpickler(f).load()


def _validate_path(
    filename: Union[str, Path], allowed_dir: Optional[Path] = None
) -> str:
    """
    Validate and resolve a file path, optionally checking it's within an allowed directory.

    :param filename: The file path to validate.
    :param allowed_dir: If provided, ensures the path is within this directory.
    :raises ValueError: If the path is outside the allowed directory.
    :return: The resolved path as a string.
    """
    path = Path(filename).resolve()
    if allowed_dir is not None:
        allowed = allowed_dir.resolve()
        if not str(path).startswith(str(allowed) + "/") and path != allowed:
            raise ValueError(
                f"Path '{filename}' is outside the allowed directory '{allowed_dir}'."
            )
    return str(path)


def save(
    db: DictDB,
    filename: Union[str, Path],
    file_format: str,
    allowed_dir: Optional[Path] = None,
) -> None:
    validated_path = _validate_path(filename, allowed_dir)
    file_format = file_format.lower()

    match file_format:
        case "json":
            state: Dict[str, Any] = {"tables": {}}
            # Snapshot the table mapping to avoid iteration races if tables are added/removed
            for table_name, table in list(db.tables.items()):
                schema = None
                if table.schema is not None:
                    schema = {
                        field: serialize_schema_type(typ)
                        for field, typ in table.schema.items()
                    }
                state["tables"][table_name] = {
                    "primary_key": table.primary_key,
                    "schema": schema,
                    "records": table.all(),
                }
            s = StringIO()
            json.dump(state, s, indent=4)
            json_content: str = s.getvalue()
            with open(validated_path, "w", encoding="utf-8") as f:
                f.write(json_content)
        case "pickle":
            b = BytesIO()
            pickle.dump(db, b)
            pickled_content: bytes = b.getvalue()
            with open(validated_path, "wb") as f:
                f.write(pickled_content)
        case _:
            raise ValueError("Unsupported file_format. Please use 'json' or 'pickle'.")


def load(
    filename: Union[str, Path],
    file_format: str,
    allowed_dir: Optional[Path] = None,
) -> DictDB:
    validated_path = _validate_path(filename, allowed_dir)
    file_format = file_format.lower()

    from .database import DictDB  # Local import to avoid circular import at module load

    match file_format:
        case "json":
            with open(validated_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            new_db = DictDB()
            for table_name, table_data in state["tables"].items():
                primary_key = table_data["primary_key"]
                schema_data = table_data["schema"]
                schema = None
                if schema_data is not None:
                    schema = {
                        field: parse_schema_type(type_name)
                        for field, type_name in schema_data.items()
                    }
                new_table = Table(table_name, primary_key=primary_key, schema=schema)
                for record in table_data["records"]:
                    new_table.insert(record)
                new_db.tables[table_name] = new_table
            return new_db
        case "pickle":
            with open(validated_path, "rb") as f:
                loaded_db: DictDB = _safe_pickle_load(f)
            return loaded_db
        case _:
            raise ValueError("Unsupported file_format. Please use 'json' or 'pickle'.")
