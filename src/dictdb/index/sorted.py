from typing import Any, Set

from .avl import AVLTree
from .base import IndexBase


class SortedIndex(IndexBase):
    """
    A sorted index using AVL tree for O(log n) insert/delete/search operations.
    Supports range queries (lt, lte, gt, gte) in addition to equality search.
    """

    supports_range: bool = True

    def __init__(self) -> None:
        # Store tuples of (value, pk) in an AVL tree for O(log n) operations.
        self._tree: AVLTree = AVLTree()

    def insert(self, pk: Any, value: Any) -> None:
        self._tree.add((value, pk))

    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        self.delete(pk, old_value)
        self.insert(pk, new_value)

    def delete(self, pk: Any, value: Any) -> None:
        self._tree.discard((value, pk))

    def search(self, value: Any) -> Set[Any]:
        """Search for exact match (equality)."""
        return {pk for _, pk in self._tree.iter_eq(value)}

    def search_lt(self, value: Any) -> Set[Any]:
        """Search for values < given value."""
        return {pk for _, pk in self._tree.iter_lt(value)}

    def search_lte(self, value: Any) -> Set[Any]:
        """Search for values <= given value."""
        return {pk for _, pk in self._tree.iter_lte(value)}

    def search_gt(self, value: Any) -> Set[Any]:
        """Search for values > given value."""
        return {pk for _, pk in self._tree.iter_gt(value)}

    def search_gte(self, value: Any) -> Set[Any]:
        """Search for values >= given value."""
        return {pk for _, pk in self._tree.iter_gte(value)}
