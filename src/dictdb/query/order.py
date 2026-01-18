import heapq
from typing import Any, Callable, List, Optional, Sequence, Union

from ..core.types import Record


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
    :param limit: Maximum number of records after offset.
    :param offset: Number of records to skip.
    :return: Ordered list of records (may be partial if limit optimization applied).
    """
    if not order_by:
        return list(records)

    # If no limit, fall back to standard sort
    if limit is None:
        return _sort_records(records, order_by)

    # Calculate how many records we need
    needed = offset + limit

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


def _sort_records(
    records: List[Record], order_by: Union[str, Sequence[str]]
) -> List[Record]:
    """
    Internal function to sort records by multiple fields.

    :param records: List of records to sort.
    :param order_by: Field name or list of field names to sort by.
    :return: Sorted list of records.
    """
    fields = [order_by] if isinstance(order_by, str) else list(order_by)

    def _make_key(field_name: str) -> Callable[[Record], Any]:
        def _key_fn(r: Record) -> Any:
            return r.get(field_name)

        return _key_fn

    result = list(records)
    for field in reversed(fields):
        desc = False
        fname = field
        if field.startswith("-"):
            desc = True
            fname = field[1:]
        result.sort(key=_make_key(fname), reverse=desc)
    return result
