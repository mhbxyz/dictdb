from typing import Any, Set

from .base import IndexBase


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
