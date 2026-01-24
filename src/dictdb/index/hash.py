"""Hash-based index implementation for O(1) equality lookups.

This module provides :class:`HashIndex`, a hash map-based index that offers
constant-time complexity for equality lookups. It is ideal for columns with
high cardinality where exact match queries are common.
"""

from typing import Any, Set

from .base import IndexBase


class HashIndex(IndexBase):
    """Hash map index for O(1) equality lookups.

    Uses a Python dict to map indexed values to sets of primary keys.
    Best suited for equality queries (``=``) on columns with many distinct values.

    Example::

        index = HashIndex()
        index.insert(pk=1, value="alice")
        index.insert(pk=2, value="bob")
        index.search("alice")  # returns {1}
    """

    def __init__(self) -> None:
        """Initialize an empty hash index."""
        self.index: dict[Any, Set[Any]] = {}

    def insert(self, pk: Any, value: Any) -> None:
        """Insert a primary key for a given indexed value.

        :param pk: The primary key of the record.
        :param value: The indexed field value.
        """
        self.index.setdefault(value, set()).add(pk)

    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        """Update the index when a record's indexed value changes.

        Removes the primary key from the old value's set and adds it to the
        new value's set. Cleans up empty sets automatically.

        :param pk: The primary key of the record.
        :param old_value: The previous indexed field value.
        :param new_value: The new indexed field value.
        """
        if old_value in self.index:
            self.index[old_value].discard(pk)
            if not self.index[old_value]:
                del self.index[old_value]
        self.insert(pk, new_value)

    def delete(self, pk: Any, value: Any) -> None:
        """Remove a primary key from the index.

        Cleans up empty sets automatically.

        :param pk: The primary key of the record to remove.
        :param value: The indexed field value.
        """
        if value in self.index:
            self.index[value].discard(pk)
            if not self.index[value]:
                del self.index[value]

    def search(self, value: Any) -> Set[Any]:
        """Search for records with an exact matching value.

        Time complexity: O(1) average case.

        :param value: The value to search for.
        :return: A set of primary keys matching the value.
        """
        return self.index.get(value, set())
