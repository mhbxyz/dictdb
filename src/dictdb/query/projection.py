"""
Column projection and deduplication utilities for query results.

This module provides functions for selecting specific columns from records
(projection) and removing duplicate records, similar to SQL SELECT and
DISTINCT operations.

Example::

    from dictdb.query.projection import project_records, deduplicate_records

    records = [{"id": 1, "name": "Alice", "age": 30}]
    projected = project_records(records, ["name", "age"])
    # Returns [{"name": "Alice", "age": 30}]

    # With aliasing
    projected = project_records(records, {"user_name": "name"})
    # Returns [{"user_name": "Alice"}]
"""

from typing import Any, Dict, List, Optional, Tuple, Union, cast

from ..core.types import Record

#: Type alias for column selection arguments.
#:
#: Supports three formats:
#:     - ``List[str]``: Simple column names (e.g., ``["name", "age"]``)
#:     - ``Dict[str, str]``: Alias to field mapping (e.g., ``{"user_name": "name"}``)
#:     - ``List[Tuple[str, str]]``: List of (alias, field) pairs
#:     - ``None``: Select all columns (no projection)
ColumnsArg = Optional[
    Union[
        List[str],
        Dict[str, str],
        List[Tuple[str, str]],
    ]
]


def project_records(records: List[Record], columns: ColumnsArg) -> List[Record]:
    """
    Project records to include only specified columns, optionally with aliasing.

    :param records: The list of records to project.
    :param columns: Column specification. See :data:`ColumnsArg` for formats.
        If None, returns records unchanged.
    :return: A new list of records containing only the specified columns.
    """

    def project(rec: Record) -> Record:
        if columns is None:
            return rec
        if isinstance(columns, dict):
            return {alias: rec.get(field) for alias, field in columns.items()}
        if columns and isinstance(columns[0], tuple):
            pairs = cast(List[Tuple[str, str]], columns)
            return {alias: rec.get(field) for (alias, field) in pairs}
        names = cast(List[str], columns)
        return {col: rec.get(col) for col in names}

    return [project(r) for r in records]


def _make_hashable(value: Any) -> Any:
    """Convert a value to a hashable type for deduplication."""
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    if isinstance(value, list):
        return tuple(_make_hashable(v) for v in value)
    if isinstance(value, set):
        return frozenset(_make_hashable(v) for v in value)
    return value


def deduplicate_records(records: List[Record]) -> List[Record]:
    """
    Remove duplicate records while preserving order (first occurrence kept).

    Handles unhashable types (dicts, lists, sets) by converting them to
    hashable equivalents for comparison.

    :param records: The list of records to deduplicate.
    :return: A new list with duplicates removed, preserving the order of
        first occurrences.
    """
    seen: set[Any] = set()
    result: List[Record] = []
    for rec in records:
        key = tuple(sorted((k, _make_hashable(v)) for k, v in rec.items()))
        if key not in seen:
            seen.add(key)
            result.append(rec)
    return result
