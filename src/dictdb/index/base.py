from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Set


class IndexBase(ABC):
    """
    Abstract base class for an index.
    """

    # Indicates if this index supports range queries
    supports_range: bool = False

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
        Searches for all primary keys with the given field value (equality).

        :param value: The value to search for.
        :return: A set of primary keys that match the value.
        """
        raise NotImplementedError

    def search_multi(self, values: Set[Any]) -> Set[Any]:
        """
        Searches for all primary keys matching any of the given values.
        Default implementation does multiple lookups.

        :param values: Set of values to search for.
        :return: A set of primary keys that match any value.
        """
        result: Set[Any] = set()
        for value in values:
            result.update(self.search(value))
        return result

    def search_lt(self, value: Any) -> Set[Any]:
        """
        Searches for all primary keys with field value < given value.
        Only supported by indexes with supports_range=True.

        :param value: The upper bound (exclusive).
        :return: A set of primary keys.
        :raises NotImplementedError: If index doesn't support range queries.
        """
        raise NotImplementedError("This index does not support range queries")

    def search_lte(self, value: Any) -> Set[Any]:
        """
        Searches for all primary keys with field value <= given value.
        Only supported by indexes with supports_range=True.

        :param value: The upper bound (inclusive).
        :return: A set of primary keys.
        :raises NotImplementedError: If index doesn't support range queries.
        """
        raise NotImplementedError("This index does not support range queries")

    def search_gt(self, value: Any) -> Set[Any]:
        """
        Searches for all primary keys with field value > given value.
        Only supported by indexes with supports_range=True.

        :param value: The lower bound (exclusive).
        :return: A set of primary keys.
        :raises NotImplementedError: If index doesn't support range queries.
        """
        raise NotImplementedError("This index does not support range queries")

    def search_gte(self, value: Any) -> Set[Any]:
        """
        Searches for all primary keys with field value >= given value.
        Only supported by indexes with supports_range=True.

        :param value: The lower bound (inclusive).
        :return: A set of primary keys.
        :raises NotImplementedError: If index doesn't support range queries.
        """
        raise NotImplementedError("This index does not support range queries")
