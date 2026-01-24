"""Sorted index implementation using AVL tree for O(log n) range queries.

This module provides :class:`SortedIndex`, a tree-based index that maintains
sorted order and supports efficient range queries (``<``, ``<=``, ``>``, ``>=``)
in addition to equality lookups.
"""

from typing import Any, Set

from .avl import AVLTree
from .base import IndexBase


class SortedIndex(IndexBase):
    """AVL tree-based index for O(log n) range and equality queries.

    Stores (value, pk) tuples in a self-balancing AVL tree, enabling efficient
    range queries in addition to equality lookups. Best suited for columns
    where range queries are common (e.g., numeric or date fields).

    Example::

        index = SortedIndex()
        index.insert(pk=1, value=25)
        index.insert(pk=2, value=30)
        index.insert(pk=3, value=20)
        index.search_gte(25)  # returns {1, 2}
    """

    supports_range: bool = True

    def __init__(self) -> None:
        """Initialize an empty sorted index with an AVL tree."""
        self._tree: AVLTree = AVLTree()

    def insert(self, pk: Any, value: Any) -> None:
        """Insert a primary key for a given indexed value.

        Time complexity: O(log n).

        :param pk: The primary key of the record.
        :param value: The indexed field value.
        """
        self._tree.add((value, pk))

    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        """Update the index when a record's indexed value changes.

        Removes the old (value, pk) tuple and inserts the new one.
        Time complexity: O(log n).

        :param pk: The primary key of the record.
        :param old_value: The previous indexed field value.
        :param new_value: The new indexed field value.
        """
        self.delete(pk, old_value)
        self.insert(pk, new_value)

    def delete(self, pk: Any, value: Any) -> None:
        """Remove a primary key from the index.

        Time complexity: O(log n).

        :param pk: The primary key of the record to remove.
        :param value: The indexed field value.
        """
        self._tree.discard((value, pk))

    def search(self, value: Any) -> Set[Any]:
        """Search for records with an exact matching value.

        Time complexity: O(log n + k) where k is the number of matches.

        :param value: The value to search for.
        :return: A set of primary keys matching the value.
        """
        return {pk for _, pk in self._tree.iter_eq(value)}

    def search_lt(self, value: Any) -> Set[Any]:
        """Search for records with values strictly less than the given value.

        Time complexity: O(log n + k) where k is the number of matches.

        :param value: The upper bound (exclusive).
        :return: A set of primary keys with indexed values < value.
        """
        return {pk for _, pk in self._tree.iter_lt(value)}

    def search_lte(self, value: Any) -> Set[Any]:
        """Search for records with values less than or equal to the given value.

        Time complexity: O(log n + k) where k is the number of matches.

        :param value: The upper bound (inclusive).
        :return: A set of primary keys with indexed values <= value.
        """
        return {pk for _, pk in self._tree.iter_lte(value)}

    def search_gt(self, value: Any) -> Set[Any]:
        """Search for records with values strictly greater than the given value.

        Time complexity: O(log n + k) where k is the number of matches.

        :param value: The lower bound (exclusive).
        :return: A set of primary keys with indexed values > value.
        """
        return {pk for _, pk in self._tree.iter_gt(value)}

    def search_gte(self, value: Any) -> Set[Any]:
        """Search for records with values greater than or equal to the given value.

        Time complexity: O(log n + k) where k is the number of matches.

        :param value: The lower bound (inclusive).
        :return: A set of primary keys with indexed values >= value.
        """
        return {pk for _, pk in self._tree.iter_gte(value)}

    def search_between(self, low: Any, high: Any) -> Set[Any]:
        """Search for records with values in the inclusive range [low, high].

        Time complexity: O(log n + k) where k is the number of matches.

        :param low: The lower bound (inclusive).
        :param high: The upper bound (inclusive).
        :return: A set of primary keys with indexed values in [low, high].
        """
        return {pk for _, pk in self._tree.iter_between(low, high)}
