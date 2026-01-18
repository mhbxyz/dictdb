from typing import Any, Set

from sortedcontainers import SortedList

from .base import IndexBase


class SortedIndex(IndexBase):
    """
    A sorted index using SortedList for O(log n) insert/delete/search operations.
    Supports range queries (lt, lte, gt, gte) in addition to equality search.
    """

    supports_range: bool = True

    def __init__(self) -> None:
        # Store tuples of (value, pk) in a SortedList for O(log n) operations.
        self.sorted_list: SortedList[tuple[Any, Any]] = SortedList()

    def insert(self, pk: Any, value: Any) -> None:
        self.sorted_list.add((value, pk))

    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        self.delete(pk, old_value)
        self.insert(pk, new_value)

    def delete(self, pk: Any, value: Any) -> None:
        self.sorted_list.discard((value, pk))

    def search(self, value: Any) -> Set[Any]:
        """Search for exact match (equality)."""
        result: Set[Any] = set()
        # Use bisect to find starting position
        idx = self.sorted_list.bisect_left((value,))
        while idx < len(self.sorted_list):
            v, pk = self.sorted_list[idx]
            if v == value:
                result.add(pk)
                idx += 1
            elif v > value:
                break
            else:
                idx += 1
        return result

    def search_lt(self, value: Any) -> Set[Any]:
        """Search for values < given value."""
        result: Set[Any] = set()
        for v, pk in self.sorted_list:
            if v < value:
                result.add(pk)
            elif v >= value:
                break
        return result

    def search_lte(self, value: Any) -> Set[Any]:
        """Search for values <= given value."""
        result: Set[Any] = set()
        for v, pk in self.sorted_list:
            if v <= value:
                result.add(pk)
            elif v > value:
                break
        return result

    def search_gt(self, value: Any) -> Set[Any]:
        """Search for values > given value."""
        result: Set[Any] = set()
        # Use bisect to find starting position (after value)
        idx = self.sorted_list.bisect_right((value,))
        # Move forward to skip any entries that equal value
        while idx < len(self.sorted_list):
            v, pk = self.sorted_list[idx]
            if v > value:
                break
            idx += 1
        # Collect all entries from this point
        while idx < len(self.sorted_list):
            v, pk = self.sorted_list[idx]
            result.add(pk)
            idx += 1
        return result

    def search_gte(self, value: Any) -> Set[Any]:
        """Search for values >= given value."""
        result: Set[Any] = set()
        # Use bisect to find starting position
        idx = self.sorted_list.bisect_left((value,))
        while idx < len(self.sorted_list):
            v, pk = self.sorted_list[idx]
            if v >= value:
                result.add(pk)
            idx += 1
        return result
