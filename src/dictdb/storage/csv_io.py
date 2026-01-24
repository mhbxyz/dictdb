"""
CSV import/export utilities for DictDB.

This module provides functions to read and write CSV files, with support for
type inference, schema validation, and configurable delimiters.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Optional

from ..core.types import Record


def _try_parse_value(value: str, target_type: type) -> Any:
    """
    Try to parse a string value to the target type.

    :param value: The string value to parse.
    :param target_type: The type to convert to.
    :return: The converted value.
    :raises ValueError: If conversion fails.
    """
    if target_type is str:
        return value
    if target_type is int:
        return int(value)
    if target_type is float:
        return float(value)
    if target_type is bool:
        lower = value.lower()
        if lower in ("true", "1", "yes"):
            return True
        if lower in ("false", "0", "no"):
            return False
        raise ValueError(f"Cannot parse '{value}' as bool")
    # Fallback: try calling the type directly
    return target_type(value)


def _infer_value_type(value: str) -> type:
    """
    Infer the type of a string value.

    Tries int -> float -> str.

    :param value: The string value to analyze.
    :return: The inferred type.
    """
    if not value:
        return str

    # Try int
    try:
        int(value)
        return int
    except ValueError:
        pass

    # Try float
    try:
        float(value)
        return float
    except ValueError:
        pass

    # Default to str
    return str


def infer_types(records: list[Record]) -> dict[str, type]:
    """
    Infer column types from a list of records.

    Analyzes all values in each column and picks the most specific type
    that can represent all values (int < float < str).

    :param records: List of record dictionaries.
    :return: Dictionary mapping column names to inferred types.
    """
    if not records:
        return {}

    # Collect all columns
    columns: set[str] = set()
    for rec in records:
        columns.update(rec.keys())

    type_priority = {int: 0, float: 1, str: 2}
    column_types: dict[str, type] = {}

    for col in columns:
        max_type: type = int  # Start with most specific
        for rec in records:
            value = rec.get(col)
            if value is None or value == "":
                continue
            if isinstance(value, str):
                inferred = _infer_value_type(value)
                if type_priority.get(inferred, 2) > type_priority.get(max_type, 0):
                    max_type = inferred
        column_types[col] = max_type

    return column_types


def read_csv(
    filepath: str | Path,
    *,
    delimiter: str = ",",
    has_header: bool = True,
    encoding: str = "utf-8",
    schema: Optional[dict[str, type]] = None,
    infer_types_enabled: bool = True,
) -> tuple[list[str], list[Record]]:
    """
    Read a CSV file and return column names and records.

    :param filepath: Path to the CSV file.
    :param delimiter: Field delimiter character.
    :param has_header: Whether the first row contains column names.
    :param encoding: File encoding.
    :param schema: Optional schema for type conversion.
    :param infer_types_enabled: If True and no schema, infer types automatically.
    :return: Tuple of (column_names, records).
    """
    filepath = Path(filepath)
    records: list[Record] = []
    columns: list[str] = []

    with filepath.open("r", encoding=encoding, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)

        # Get header or generate column names
        if has_header:
            columns = next(reader, [])
        else:
            # Peek at first row to determine column count
            first_row = next(reader, None)
            if first_row is None:
                return [], []
            columns = [f"col_{i}" for i in range(len(first_row))]
            # Process first row as data
            records.append(dict(zip(columns, first_row)))

        # Read remaining rows
        for row in reader:
            if len(row) != len(columns):
                # Skip malformed rows or pad with empty strings
                row = row[: len(columns)] + [""] * (len(columns) - len(row))
            records.append(dict(zip(columns, row)))

    # Apply type conversion
    if schema:
        records = _apply_schema(records, schema)
    elif infer_types_enabled and records:
        inferred = infer_types(records)
        records = _apply_schema(records, inferred)

    return columns, records


def _apply_schema(records: list[Record], schema: dict[str, type]) -> list[Record]:
    """
    Apply type conversion to records based on schema.

    :param records: List of records with string values.
    :param schema: Mapping of column names to target types.
    :return: List of records with converted values.
    """
    converted: list[Record] = []
    for rec in records:
        new_rec: Record = {}
        for key, value in rec.items():
            if key in schema and isinstance(value, str):
                target_type = schema[key]
                if value == "":
                    # Keep empty strings as None for non-string types
                    new_rec[key] = None if target_type is not str else ""
                else:
                    try:
                        new_rec[key] = _try_parse_value(value, target_type)
                    except (ValueError, TypeError):
                        # Keep original value if conversion fails
                        new_rec[key] = value
            else:
                new_rec[key] = value
        converted.append(new_rec)
    return converted


def write_csv(
    filepath: str | Path,
    records: list[Record],
    *,
    columns: Optional[list[str]] = None,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> int:
    """
    Write records to a CSV file.

    :param filepath: Path to the output CSV file.
    :param records: List of record dictionaries to write.
    :param columns: Column names and order. If None, derived from records.
    :param delimiter: Field delimiter character.
    :param encoding: File encoding.
    :return: Number of rows written (excluding header).
    """
    filepath = Path(filepath)

    if not records:
        # Write empty file with header if columns provided
        if columns:
            with filepath.open("w", encoding=encoding, newline="") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(columns)
        return 0

    # Determine columns from records if not provided
    if columns is None:
        # Collect all keys preserving order from first record
        seen: set[str] = set()
        columns = []
        for rec in records:
            for key in rec.keys():
                if key not in seen:
                    seen.add(key)
                    columns.append(key)

    with filepath.open("w", encoding=encoding, newline="") as f:
        dict_writer: csv.DictWriter[str] = csv.DictWriter(
            f,
            fieldnames=columns,
            delimiter=delimiter,
            extrasaction="ignore",
        )
        dict_writer.writeheader()
        dict_writer.writerows(records)

    return len(records)
