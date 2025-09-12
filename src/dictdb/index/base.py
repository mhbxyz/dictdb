from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Set


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
