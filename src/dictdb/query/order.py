import heapq
from typing import Any, List, Optional, Sequence, Tuple, Union

from ..core.types import Record


class _ReverseOrder:
    """Wrapper to invert comparison for descending sort."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value

    def __lt__(self, other: "_ReverseOrder") -> bool:
        result: bool = self.value > other.value
        return result

    def __le__(self, other: "_ReverseOrder") -> bool:
        result: bool = self.value >= other.value
        return result

    def __gt__(self, other: "_ReverseOrder") -> bool:
        result: bool = self.value < other.value
        return result

    def __ge__(self, other: "_ReverseOrder") -> bool:
        result: bool = self.value <= other.value
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _ReverseOrder):
            return NotImplemented
        result: bool = self.value == other.value
        return result


def order_records(
    records: List[Record], order_by: Optional[Union[str, Sequence[str]]]
) -> List[Record]:
    """
    Orders records by the specified field(s).

    :param records: List of records to order.
    :param order_by: Field name or list of field names to sort by.
                     Prefix with '-' for descending order.
    :return: Ordered list of records.
    """
    if not order_by:
        return list(records)
    return _sort_records(records, order_by)


def order_records_with_limit(
    records: List[Record],
    order_by: Optional[Union[str, Sequence[str]]],
    limit: Optional[int],
    offset: int,
) -> List[Record]:
    """
    Orders records with optimization for LIMIT queries using heapq.

    When ORDER BY and LIMIT are both specified, uses heapq.nsmallest/nlargest
    to avoid full sort: O(n log k) instead of O(n log n) where k = offset + limit.

    :param records: List of records to order.
    :param order_by: Field name or list of field names to sort by.
    :param limit: Maximum number of records after offset (negative treated as no limit).
    :param offset: Number of records to skip (negative treated as 0).
    :return: Ordered list of records (may be partial if limit optimization applied).
    """
    if not order_by:
        return list(records)

    # Normalize offset (negative treated as 0)
    effective_offset = max(offset, 0)

    # If no limit or negative limit, fall back to standard sort
    if limit is None or limit < 0:
        return _sort_records(records, order_by)

    # Calculate how many records we need
    needed = effective_offset + limit

    # If we need all or most records, standard sort is more efficient
    if needed >= len(records):
        return _sort_records(records, order_by)

    # Parse order_by fields
    fields = [order_by] if isinstance(order_by, str) else list(order_by)

    # For single field ORDER BY, use heapq optimization
    if len(fields) == 1:
        field = fields[0]
        desc = field.startswith("-")
        fname = field[1:] if desc else field

        def key_fn(r: Record) -> Any:
            return r.get(fname)

        # heapq.nsmallest for ASC, nlargest for DESC
        if desc:
            return heapq.nlargest(needed, records, key=key_fn)
        else:
            return heapq.nsmallest(needed, records, key=key_fn)

    # For multi-field ORDER BY, use standard sort (heapq doesn't help much)
    return _sort_records(records, order_by)


def _parse_order_fields(order_by: Union[str, Sequence[str]]) -> List[Tuple[str, bool]]:
    """Parse order_by into list of (field_name, descending) tuples."""
    fields = [order_by] if isinstance(order_by, str) else list(order_by)
    parsed: List[Tuple[str, bool]] = []
    for field in fields:
        if field.startswith("-"):
            parsed.append((field[1:], True))
        else:
            parsed.append((field, False))
    return parsed


def _sort_records(
    records: List[Record], order_by: Union[str, Sequence[str]]
) -> List[Record]:
    """
    Sort records by multiple fields in a single pass using tuple keys.

    Uses _ReverseOrder wrapper for descending fields to enable single-pass sort.
    Time complexity: O(n log n) regardless of number of fields.

    :param records: List of records to sort.
    :param order_by: Field name or list of field names to sort by.
    :return: Sorted list of records.
    """
    parsed = _parse_order_fields(order_by)

    def _sort_key(record: Record) -> Tuple[Any, ...]:
        key_parts: List[Any] = []
        for fname, desc in parsed:
            val = record.get(fname)
            key_parts.append(_ReverseOrder(val) if desc else val)
        return tuple(key_parts)

    return sorted(records, key=_sort_key)
