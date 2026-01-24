"""
Aggregation functions for query results.

Provides SQL-like aggregation classes: Count, Sum, Avg, Min, Max.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

from ..core.types import Record


class Agg(ABC):
    """Base class for aggregation functions."""

    def __init__(self, field: Optional[str] = None) -> None:
        """
        Initialize an aggregation.

        :param field: Field name to aggregate. None for Count() without field.
        """
        self.field = field

    @abstractmethod
    def compute(self, values: List[Any]) -> Any:
        """Compute the aggregation on a list of values."""
        ...

    def extract_values(self, records: List[Record]) -> List[Any]:
        """Extract values from records for this aggregation."""
        if self.field is None:
            # For Count() without field, return a marker for each record
            return [1 for _ in records]
        return [rec.get(self.field) for rec in records]


class Count(Agg):
    """
    Count aggregation.

    Count() - counts all records
    Count("field") - counts non-None values in field
    """

    def __init__(self, field: Optional[str] = None) -> None:
        super().__init__(field)

    def compute(self, values: List[Any]) -> int:
        if self.field is None:
            # Count all records
            return len(values)
        # Count non-None values
        return sum(1 for v in values if v is not None)


class Sum(Agg):
    """Sum aggregation for numeric fields."""

    def __init__(self, field: str) -> None:
        super().__init__(field)

    def compute(self, values: List[Any]) -> Optional[float]:
        nums = [v for v in values if v is not None]
        if not nums:
            return None
        total: float = sum(nums)
        return total


class Avg(Agg):
    """Average aggregation for numeric fields."""

    def __init__(self, field: str) -> None:
        super().__init__(field)

    def compute(self, values: List[Any]) -> Optional[float]:
        nums = [v for v in values if v is not None]
        if not nums:
            return None
        total: float = sum(nums)
        return total / len(nums)


class Min(Agg):
    """Minimum value aggregation."""

    def __init__(self, field: str) -> None:
        super().__init__(field)

    def compute(self, values: List[Any]) -> Optional[Any]:
        nums = [v for v in values if v is not None]
        if not nums:
            return None
        return min(nums)


class Max(Agg):
    """Maximum value aggregation."""

    def __init__(self, field: str) -> None:
        super().__init__(field)

    def compute(self, values: List[Any]) -> Optional[Any]:
        nums = [v for v in values if v is not None]
        if not nums:
            return None
        return max(nums)


def compute_aggregations(
    records: List[Record],
    aggregations: Dict[str, Agg],
) -> Dict[str, Any]:
    """
    Compute aggregations on a list of records.

    :param records: List of records to aggregate.
    :param aggregations: Dict mapping result key to Agg instance.
    :return: Dict with aggregation results.
    """
    result: Dict[str, Any] = {}
    for result_key, agg in aggregations.items():
        values = agg.extract_values(records)
        result[result_key] = agg.compute(values)
    return result


def group_and_aggregate(
    records: List[Record],
    group_by: Union[str, List[str]],
    aggregations: Dict[str, Agg],
) -> List[Record]:
    """
    Group records by fields and compute aggregations for each group.

    :param records: List of records to group and aggregate.
    :param group_by: Field name or list of field names to group by.
    :param aggregations: Dict mapping result key to Agg instance.
    :return: List of result records with group keys and aggregation values.
    """
    if isinstance(group_by, str):
        group_by = [group_by]

    # Group records by key
    groups: Dict[tuple[Any, ...], List[Record]] = defaultdict(list)
    for rec in records:
        key = tuple(rec.get(field) for field in group_by)
        groups[key].append(rec)

    # Compute aggregations for each group
    results: List[Record] = []
    for key, group_records in groups.items():
        row: Record = {}
        # Add group-by fields
        for i, field in enumerate(group_by):
            row[field] = key[i]
        # Add aggregations
        agg_results = compute_aggregations(group_records, aggregations)
        row.update(agg_results)
        results.append(row)

    return results
