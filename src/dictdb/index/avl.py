"""
Pure Python AVL tree implementation for SortedIndex.

This module provides an AVL tree that stores (value, pk) tuples in sorted order,
supporting O(log n) insert, delete, and range queries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Optional


@dataclass
class AVLNode:
    """A node in the AVL tree storing a (value, pk) tuple."""

    key: tuple[Any, Any]  # (value, pk)
    left: Optional[AVLNode] = None
    right: Optional[AVLNode] = None
    height: int = 1
    size: int = 1  # Subtree size for O(log n) bisect


class AVLTree:
    """
    AVL tree implementation storing (value, pk) tuples in sorted order.

    Supports O(log n) insert, delete, and bisect operations.
    Provides range iterators for efficient range queries.
    """

    def __init__(self) -> None:
        self._root: Optional[AVLNode] = None

    def __len__(self) -> int:
        """Return the number of elements in the tree."""
        return self._size(self._root)

    def __iter__(self) -> Iterator[tuple[Any, Any]]:
        """Iterate over all elements in sorted order."""
        yield from self._inorder(self._root)

    def add(self, key: tuple[Any, Any]) -> None:
        """Insert a (value, pk) tuple into the tree."""
        self._root = self._insert(self._root, key)

    def discard(self, key: tuple[Any, Any]) -> None:
        """Remove a (value, pk) tuple from the tree if it exists."""
        self._root = self._delete(self._root, key)

    def bisect_left(self, key: tuple[Any, ...]) -> int:
        """
        Return the index where key would be inserted to keep order.

        For equal elements, returns the leftmost position.
        Accepts partial keys like (value,) for searching by value only.
        """
        return self._bisect_left(self._root, key)

    def bisect_right(self, key: tuple[Any, ...]) -> int:
        """
        Return the index after all elements equal to key.

        Accepts partial keys like (value,) for searching by value only.
        """
        return self._bisect_right(self._root, key)

    def iter_lt(self, value: Any) -> Iterator[tuple[Any, Any]]:
        """Iterate over all elements with value < given value."""
        yield from self._iter_lt(self._root, value)

    def iter_lte(self, value: Any) -> Iterator[tuple[Any, Any]]:
        """Iterate over all elements with value <= given value."""
        yield from self._iter_lte(self._root, value)

    def iter_gt(self, value: Any) -> Iterator[tuple[Any, Any]]:
        """Iterate over all elements with value > given value."""
        yield from self._iter_gt(self._root, value)

    def iter_gte(self, value: Any) -> Iterator[tuple[Any, Any]]:
        """Iterate over all elements with value >= given value."""
        yield from self._iter_gte(self._root, value)

    def iter_eq(self, value: Any) -> Iterator[tuple[Any, Any]]:
        """Iterate over all elements with value == given value."""
        yield from self._iter_eq(self._root, value)

    # --- Internal methods ---

    def _height(self, node: Optional[AVLNode]) -> int:
        """Return the height of a node (0 for None)."""
        return node.height if node else 0

    def _size(self, node: Optional[AVLNode]) -> int:
        """Return the size of a subtree (0 for None)."""
        return node.size if node else 0

    def _balance_factor(self, node: AVLNode) -> int:
        """Return the balance factor (left height - right height)."""
        return self._height(node.left) - self._height(node.right)

    def _update(self, node: AVLNode) -> None:
        """Update the height and size of a node."""
        node.height = 1 + max(self._height(node.left), self._height(node.right))
        node.size = 1 + self._size(node.left) + self._size(node.right)

    def _rotate_left(self, node: AVLNode) -> AVLNode:
        """Perform a left rotation."""
        right = node.right
        assert right is not None
        node.right = right.left
        right.left = node
        self._update(node)
        self._update(right)
        return right

    def _rotate_right(self, node: AVLNode) -> AVLNode:
        """Perform a right rotation."""
        left = node.left
        assert left is not None
        node.left = left.right
        left.right = node
        self._update(node)
        self._update(left)
        return left

    def _rebalance(self, node: AVLNode) -> AVLNode:
        """Rebalance the node if needed and return the new root."""
        self._update(node)
        balance = self._balance_factor(node)

        # Left-heavy
        if balance > 1:
            assert node.left is not None
            if self._balance_factor(node.left) < 0:
                # Left-Right case
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right-heavy
        if balance < -1:
            assert node.right is not None
            if self._balance_factor(node.right) > 0:
                # Right-Left case
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _insert(self, node: Optional[AVLNode], key: tuple[Any, Any]) -> AVLNode:
        """Recursively insert a key and rebalance."""
        if node is None:
            return AVLNode(key)

        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        # If key == node.key, it's a duplicate - don't insert

        return self._rebalance(node)

    def _find_min(self, node: AVLNode) -> AVLNode:
        """Find the minimum node in a subtree."""
        while node.left is not None:
            node = node.left
        return node

    def _delete(
        self, node: Optional[AVLNode], key: tuple[Any, Any]
    ) -> Optional[AVLNode]:
        """Recursively delete a key and rebalance."""
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            # Found the node to delete
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # Node has two children: replace with successor
            successor = self._find_min(node.right)
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)

        return self._rebalance(node)

    def _inorder(self, node: Optional[AVLNode]) -> Iterator[tuple[Any, Any]]:
        """In-order traversal yielding all keys."""
        if node is not None:
            yield from self._inorder(node.left)
            yield node.key
            yield from self._inorder(node.right)

    def _bisect_left(self, node: Optional[AVLNode], key: tuple[Any, ...]) -> int:
        """Find the leftmost position for key."""
        if node is None:
            return 0

        if key <= node.key[: len(key)]:
            return self._bisect_left(node.left, key)
        else:
            return self._size(node.left) + 1 + self._bisect_left(node.right, key)

    def _bisect_right(self, node: Optional[AVLNode], key: tuple[Any, ...]) -> int:
        """Find the rightmost position after key."""
        if node is None:
            return 0

        if key < node.key[: len(key)]:
            return self._bisect_right(node.left, key)
        else:
            return self._size(node.left) + 1 + self._bisect_right(node.right, key)

    def _iter_lt(
        self, node: Optional[AVLNode], value: Any
    ) -> Iterator[tuple[Any, Any]]:
        """Yield all elements with value < given value."""
        if node is None:
            return

        node_value = node.key[0]
        if node_value < value:
            yield from self._inorder(node.left)
            yield node.key
            yield from self._iter_lt(node.right, value)
        else:
            yield from self._iter_lt(node.left, value)

    def _iter_lte(
        self, node: Optional[AVLNode], value: Any
    ) -> Iterator[tuple[Any, Any]]:
        """Yield all elements with value <= given value."""
        if node is None:
            return

        node_value = node.key[0]
        if node_value <= value:
            yield from self._inorder(node.left)
            yield node.key
            yield from self._iter_lte(node.right, value)
        else:
            yield from self._iter_lte(node.left, value)

    def _iter_gt(
        self, node: Optional[AVLNode], value: Any
    ) -> Iterator[tuple[Any, Any]]:
        """Yield all elements with value > given value."""
        if node is None:
            return

        node_value = node.key[0]
        if node_value > value:
            yield from self._iter_gt(node.left, value)
            yield node.key
            yield from self._inorder(node.right)
        else:
            yield from self._iter_gt(node.right, value)

    def _iter_gte(
        self, node: Optional[AVLNode], value: Any
    ) -> Iterator[tuple[Any, Any]]:
        """Yield all elements with value >= given value."""
        if node is None:
            return

        node_value = node.key[0]
        if node_value >= value:
            yield from self._iter_gte(node.left, value)
            yield node.key
            yield from self._inorder(node.right)
        else:
            yield from self._iter_gte(node.right, value)

    def _iter_eq(
        self, node: Optional[AVLNode], value: Any
    ) -> Iterator[tuple[Any, Any]]:
        """Yield all elements with value == given value."""
        if node is None:
            return

        node_value = node.key[0]
        if node_value == value:
            yield from self._iter_eq(node.left, value)
            yield node.key
            yield from self._iter_eq(node.right, value)
        elif node_value < value:
            yield from self._iter_eq(node.right, value)
        else:
            yield from self._iter_eq(node.left, value)
