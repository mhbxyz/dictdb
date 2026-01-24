"""
Pagination utilities for query results.

This module provides functions for implementing LIMIT/OFFSET style pagination
on record lists, similar to SQL pagination clauses.

Example::

    from dictdb.query.pager import slice_records

    records = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]
    page = slice_records(records, limit=2, offset=1)
    # Returns [{"id": 2}, {"id": 3}]
"""

from typing import List, Optional

from ..core.types import Record


def slice_records(
    records: List[Record], *, limit: Optional[int], offset: int
) -> List[Record]:
    """
    Apply LIMIT/OFFSET pagination to a list of records.

    :param records: The list of records to paginate.
    :param limit: Maximum number of records to return. If None or negative,
        no limit is applied.
    :param offset: Number of records to skip from the beginning. Negative
        values are treated as 0.
    :return: A new list containing the paginated subset of records.
    """
    start = max(offset, 0)
    end = start + limit if isinstance(limit, int) and limit >= 0 else None
    return records[start:end]
