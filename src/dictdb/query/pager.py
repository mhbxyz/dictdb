from typing import List, Optional

from ..core.types import Record


def slice_records(
    records: List[Record], *, limit: Optional[int], offset: int
) -> List[Record]:
    start = max(offset, 0)
    end = start + limit if isinstance(limit, int) and limit >= 0 else None
    return records[start:end]
