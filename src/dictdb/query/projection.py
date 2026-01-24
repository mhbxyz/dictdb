from typing import Any, Dict, List, Optional, Tuple, Union, cast

from ..core.types import Record

ColumnsArg = Optional[
    Union[
        List[str],
        Dict[str, str],
        List[Tuple[str, str]],
    ]
]


def project_records(records: List[Record], columns: ColumnsArg) -> List[Record]:
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

    Handles unhashable types by converting them to hashable equivalents.
    """
    seen: set[Any] = set()
    result: List[Record] = []
    for rec in records:
        key = tuple(sorted((k, _make_hashable(v)) for k, v in rec.items()))
        if key not in seen:
            seen.add(key)
            result.append(rec)
    return result
