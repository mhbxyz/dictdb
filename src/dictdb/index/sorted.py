from bisect import bisect_left, insort
from typing import Any, List, Set

from .base import IndexBase


class SortedIndex(IndexBase):
    """
    A simple sorted index that uses a sorted list to simulate B-tree behavior.
    Not as efficient as a real B-tree for large datasets, but useful for demonstration.
    """

    def __init__(self) -> None:
        # Store tuples of (value, pk) in a sorted list.
        self.sorted_list: List[tuple[Any, Any]] = []

    def insert(self, pk: Any, value: Any) -> None:
        insort(self.sorted_list, (value, pk))

    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        self.delete(pk, old_value)
        self.insert(pk, new_value)

    def delete(self, pk: Any, value: Any) -> None:
        index = bisect_left(self.sorted_list, (value, pk))
        if index < len(self.sorted_list) and self.sorted_list[index] == (value, pk):
            self.sorted_list.pop(index)

    def search(self, value: Any) -> Set[Any]:
        result: Set[Any] = set()
        index = bisect_left(self.sorted_list, (value, -float("inf")))
        while index < len(self.sorted_list) and self.sorted_list[index][0] == value:
            result.add(self.sorted_list[index][1])
            index += 1
        return result
