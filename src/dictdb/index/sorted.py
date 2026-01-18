from typing import Any, Set

from sortedcontainers import SortedList

from .base import IndexBase


class SortedIndex(IndexBase):
    """
    A sorted index using SortedList for O(log n) insert/delete/search operations.
    Useful for range queries and ordered iteration.
    """

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
        result: Set[Any] = set()
        # Use bisect_left to find the first element >= (value, -inf)
        index = self.sorted_list.bisect_left((value,))
        while index < len(self.sorted_list) and self.sorted_list[index][0] == value:
            result.add(self.sorted_list[index][1])
            index += 1
        return result
