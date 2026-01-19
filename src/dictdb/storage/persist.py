from __future__ import annotations

import json
import pickle
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Union, BinaryIO, Optional

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


def _save_json_streaming(db: DictDB, file_path: str) -> None:
    """
    Save database to JSON using streaming to reduce memory spikes.

    Instead of building the complete state dict and serializing it all at once,
    this writes JSON incrementally to reduce peak memory by ~2-3x.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write('{\n    "tables": {')
        # Snapshot table names to avoid iteration races
        table_items = list(db.tables.items())
        for i, (table_name, table) in enumerate(table_items):
            if i > 0:
                f.write(",")
            f.write(f"\n        {json.dumps(table_name)}: {{\n")
            f.write(f'            "primary_key": {json.dumps(table.primary_key)},\n')

            # Serialize schema
            if table.schema is not None:
                schema_dict = {
                    field: serialize_schema_type(typ)
                    for field, typ in table.schema.items()
                }
                f.write(f'            "schema": {json.dumps(schema_dict)},\n')
            else:
                f.write('            "schema": null,\n')

            # Stream records directly without building intermediate list
            f.write('            "records": [')
            with table._lock.read_lock():
                records_iter = iter(table.records.values())
                try:
                    first_record = next(records_iter)
                    f.write(f"\n                {json.dumps(first_record)}")
                    for record in records_iter:
                        f.write(f",\n                {json.dumps(record)}")
                except StopIteration:
                    pass  # Empty table
            f.write("\n            ]\n        }")
        f.write("\n    }\n}\n")


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
            _save_json_streaming(db, validated_path)
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


# ──────────────────────────────────────────────────────────────────────────────
# Incremental backup (delta) support
# ──────────────────────────────────────────────────────────────────────────────


def has_changes(db: DictDB) -> bool:
    """
    Check if the database has any uncommitted changes since the last backup.

    :param db: The DictDB instance to check.
    :return: True if any table has dirty or deleted records.
    """
    return any(table.has_changes() for table in db.tables.values())


def save_delta(
    db: DictDB,
    filename: Union[str, Path],
    allowed_dir: Optional[Path] = None,
    clear_tracking: bool = True,
) -> bool:
    """
    Save only the changes (delta) since the last backup.

    The delta file contains upserted records and deleted primary keys for each
    table that has changes. This is much smaller than a full backup when only
    a few records have changed.

    :param db: The DictDB instance to back up.
    :param filename: Path to the delta file.
    :param allowed_dir: If provided, ensures path is within this directory.
    :param clear_tracking: If True, clears dirty tracking after successful save.
    :return: True if a delta was saved, False if no changes to save.
    """
    validated_path = _validate_path(filename, allowed_dir)

    # Collect deltas from all tables
    delta_data: Dict[str, Dict[str, List[Any]]] = {}
    tables_with_changes: List[Table] = []

    for table_name, table in db.tables.items():
        if not table.has_changes():
            continue
        tables_with_changes.append(table)
        delta_data[table_name] = {
            "upserts": table.get_dirty_records(),
            "deletes": table.get_deleted_pks(),
        }

    if not delta_data:
        return False

    # Write delta file
    delta_doc = {
        "type": "delta",
        "timestamp": time.time(),
        "tables": delta_data,
    }
    with open(validated_path, "w", encoding="utf-8") as f:
        json.dump(delta_doc, f, indent=2)

    # Clear tracking after successful write
    if clear_tracking:
        for table in tables_with_changes:
            table.clear_dirty_tracking()

    return True


def apply_delta(
    db: DictDB,
    filename: Union[str, Path],
    allowed_dir: Optional[Path] = None,
) -> int:
    """
    Apply a delta file to the database.

    Upserts (inserts or updates) the dirty records and deletes the deleted PKs.

    :param db: The DictDB instance to update.
    :param filename: Path to the delta file.
    :param allowed_dir: If provided, ensures path is within this directory.
    :return: Total number of records affected (upserts + deletes).
    :raises ValueError: If the file is not a valid delta file.
    """
    validated_path = _validate_path(filename, allowed_dir)

    with open(validated_path, "r", encoding="utf-8") as f:
        delta_doc = json.load(f)

    if delta_doc.get("type") != "delta":
        raise ValueError(f"File '{filename}' is not a valid delta file.")

    affected = 0
    for table_name, changes in delta_doc["tables"].items():
        if table_name not in db.tables:
            # Table doesn't exist, skip (or could create it)
            continue

        table = db.tables[table_name]
        pk_field = table.primary_key

        # Apply upserts
        for record in changes.get("upserts", []):
            pk = record.get(pk_field)
            if pk is not None and pk in table.records:
                # Update existing record
                with table._lock.write_lock():
                    table.records[pk].update(record)
            else:
                # Insert new record (bypass validation for restore)
                with table._lock.write_lock():
                    if pk is None:
                        pk = table._next_pk
                        table._next_pk += 1
                        record[pk_field] = pk
                    table.records[pk] = record
            affected += 1

        # Apply deletes
        for pk in changes.get("deletes", []):
            if pk in table.records:
                with table._lock.write_lock():
                    del table.records[pk]
                affected += 1

    return affected
