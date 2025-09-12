"""
This module implements efficient index data structures for DictDB.
It defines an abstract base class for indices and provides two implementations:
HashIndex (using a hash map) and SortedIndex (a simple sorted index using bisect).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from bisect import bisect_left, insort
from typing import Any, List, Set


class IndexBase(ABC):
    """
    Abstract base class for an index.
    """

    @abstractmethod
    def insert(self, pk: Any, value: Any) -> None:
        """
        Inserts a key-value pair into the index.

        :param pk: The primary key of the record.
        :param value: The value of the field being indexed.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        """
        Updates the index when a record's field value changes.

        :param pk: The primary key of the record.
        :param old_value: The old value of the field.
        :param new_value: The new value of the field.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, pk: Any, value: Any) -> None:
        """
        Removes a record from the index.

        :param pk: The primary key of the record.
        :param value: The value of the field being indexed.
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, value: Any) -> Set[Any]:
        """
        Searches for all primary keys with the given field value.

        :param value: The value to search for.
        :return: A set of primary keys that match the value.
        """
        raise NotImplementedError


class HashIndex(IndexBase):
    """
    An index implementation using a hash map (Python dict).
    """

    def __init__(self) -> None:
        self.index: dict[Any, Set[Any]] = {}

    def insert(self, pk: Any, value: Any) -> None:
        self.index.setdefault(value, set()).add(pk)

    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        if old_value in self.index:
            self.index[old_value].discard(pk)
            if not self.index[old_value]:
                del self.index[old_value]
        self.insert(pk, new_value)

    def delete(self, pk: Any, value: Any) -> None:
        if value in self.index:
            self.index[value].discard(pk)
            if not self.index[value]:
                del self.index[value]

    def search(self, value: Any) -> Set[Any]:
        return self.index.get(value, set())


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
