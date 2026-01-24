"""
Unit tests for the AVL tree implementation.
"""

import pytest

from dictdb.index.avl import AVLTree, AVLNode


class TestAVLBasicOperations:
    """Tests for basic AVL tree operations."""

    def test_avl_add_single(self) -> None:
        """Test adding a single element."""
        tree = AVLTree()
        tree.add((10, 1))
        assert len(tree) == 1
        assert list(tree) == [(10, 1)]

    def test_avl_add_multiple_maintains_order(self) -> None:
        """Test that multiple additions maintain sorted order."""
        tree = AVLTree()
        tree.add((30, 3))
        tree.add((10, 1))
        tree.add((20, 2))
        assert len(tree) == 3
        assert list(tree) == [(10, 1), (20, 2), (30, 3)]

    def test_avl_discard_existing(self) -> None:
        """Test removing an existing element."""
        tree = AVLTree()
        tree.add((10, 1))
        tree.add((20, 2))
        tree.add((30, 3))
        tree.discard((20, 2))
        assert len(tree) == 2
        assert list(tree) == [(10, 1), (30, 3)]

    def test_avl_discard_nonexistent(self) -> None:
        """Test that discarding a nonexistent element is a no-op."""
        tree = AVLTree()
        tree.add((10, 1))
        tree.discard((20, 2))  # Should not raise
        assert len(tree) == 1
        assert list(tree) == [(10, 1)]

    def test_avl_len_empty(self) -> None:
        """Test length of empty tree."""
        tree = AVLTree()
        assert len(tree) == 0

    def test_avl_len_after_operations(self) -> None:
        """Test length after various operations."""
        tree = AVLTree()
        tree.add((10, 1))
        tree.add((20, 2))
        assert len(tree) == 2
        tree.discard((10, 1))
        assert len(tree) == 1
        tree.discard((20, 2))
        assert len(tree) == 0


class TestAVLBalancing:
    """Tests for AVL tree balancing."""

    def test_avl_balance_left_heavy(self) -> None:
        """Test balancing with increasing insertions (LL case)."""
        tree = AVLTree()
        for i in range(1, 8):
            tree.add((i, i))
        # Tree should be balanced, verify order
        assert list(tree) == [(i, i) for i in range(1, 8)]
        # Height should be O(log n)
        assert tree._root is not None
        assert tree._root.height <= 4  # log2(7) + 1 = 3.8

    def test_avl_balance_right_heavy(self) -> None:
        """Test balancing with decreasing insertions (RR case)."""
        tree = AVLTree()
        for i in range(7, 0, -1):
            tree.add((i, i))
        assert list(tree) == [(i, i) for i in range(1, 8)]
        assert tree._root is not None
        assert tree._root.height <= 4

    def test_avl_balance_after_deletion(self) -> None:
        """Test that tree remains balanced after deletions."""
        tree = AVLTree()
        for i in range(1, 16):
            tree.add((i, i))

        # Delete half the elements
        for i in range(1, 8):
            tree.discard((i, i))

        assert len(tree) == 8
        assert tree._root is not None
        assert tree._root.height <= 5

    def test_avl_height_invariant(self) -> None:
        """Test that the height difference between children is at most 1."""
        tree = AVLTree()
        for i in [5, 3, 7, 2, 4, 6, 8, 1]:
            tree.add((i, i))

        def check_balance(node: AVLNode | None) -> bool:
            if node is None:
                return True
            balance = tree._balance_factor(node)
            if abs(balance) > 1:
                return False
            return check_balance(node.left) and check_balance(node.right)

        assert check_balance(tree._root)


class TestAVLBisect:
    """Tests for bisect operations."""

    def test_avl_bisect_left_existing(self) -> None:
        """Test bisect_left for existing value."""
        tree = AVLTree()
        for i in range(1, 6):
            tree.add((i * 10, i))
        # Values: (10,1), (20,2), (30,3), (40,4), (50,5)
        assert tree.bisect_left((30,)) == 2

    def test_avl_bisect_right_existing(self) -> None:
        """Test bisect_right for existing value."""
        tree = AVLTree()
        for i in range(1, 6):
            tree.add((i * 10, i))
        # Values: (10,1), (20,2), (30,3), (40,4), (50,5)
        assert tree.bisect_right((30,)) == 3

    def test_avl_bisect_partial_key(self) -> None:
        """Test bisect with partial key (value,)."""
        tree = AVLTree()
        tree.add((10, 1))
        tree.add((10, 2))
        tree.add((10, 3))
        tree.add((20, 4))
        # All (10, pk) should be before position 3
        assert tree.bisect_left((10,)) == 0
        assert tree.bisect_right((10,)) == 3

    def test_avl_bisect_nonexistent(self) -> None:
        """Test bisect for non-existent value."""
        tree = AVLTree()
        for i in [10, 30, 50]:
            tree.add((i, i))
        # Position for 20 (between 10 and 30)
        assert tree.bisect_left((20,)) == 1
        assert tree.bisect_right((20,)) == 1


class TestAVLRangeIterators:
    """Tests for range iterator operations."""

    @pytest.fixture
    def populated_tree(self) -> AVLTree:
        """Create a tree with values 10, 20, 30, 40, 50."""
        tree = AVLTree()
        for i in range(1, 6):
            tree.add((i * 10, i))
        return tree

    def test_avl_iter_lt(self, populated_tree: AVLTree) -> None:
        """Test iter_lt (less than)."""
        result = list(populated_tree.iter_lt(30))
        assert result == [(10, 1), (20, 2)]

    def test_avl_iter_lte(self, populated_tree: AVLTree) -> None:
        """Test iter_lte (less than or equal)."""
        result = list(populated_tree.iter_lte(30))
        assert result == [(10, 1), (20, 2), (30, 3)]

    def test_avl_iter_gt(self, populated_tree: AVLTree) -> None:
        """Test iter_gt (greater than)."""
        result = list(populated_tree.iter_gt(30))
        assert result == [(40, 4), (50, 5)]

    def test_avl_iter_gte(self, populated_tree: AVLTree) -> None:
        """Test iter_gte (greater than or equal)."""
        result = list(populated_tree.iter_gte(30))
        assert result == [(30, 3), (40, 4), (50, 5)]

    def test_avl_iter_eq(self, populated_tree: AVLTree) -> None:
        """Test iter_eq (equal)."""
        result = list(populated_tree.iter_eq(30))
        assert result == [(30, 3)]

    def test_avl_iter_eq_multiple(self) -> None:
        """Test iter_eq with multiple matching elements."""
        tree = AVLTree()
        tree.add((10, 1))
        tree.add((10, 2))
        tree.add((10, 3))
        tree.add((20, 4))
        result = list(tree.iter_eq(10))
        # Should return all three elements with value 10
        assert len(result) == 3
        assert all(v == 10 for v, _ in result)


class TestAVLEdgeCases:
    """Tests for edge cases."""

    def test_avl_empty_operations(self) -> None:
        """Test operations on empty tree."""
        tree = AVLTree()
        assert len(tree) == 0
        assert list(tree) == []
        assert tree.bisect_left((10,)) == 0
        assert tree.bisect_right((10,)) == 0
        assert list(tree.iter_lt(10)) == []
        assert list(tree.iter_eq(10)) == []
        tree.discard((10, 1))  # Should not raise

    def test_avl_duplicate_key_ignored(self) -> None:
        """Test that duplicate keys are ignored."""
        tree = AVLTree()
        tree.add((10, 1))
        tree.add((10, 1))  # Duplicate
        assert len(tree) == 1

    def test_avl_same_value_different_pk(self) -> None:
        """Test elements with same value but different pk."""
        tree = AVLTree()
        tree.add((10, 1))
        tree.add((10, 2))
        tree.add((10, 3))
        assert len(tree) == 3
        # Should be sorted by pk within same value
        assert list(tree) == [(10, 1), (10, 2), (10, 3)]

    @pytest.mark.slow
    def test_avl_large_dataset(self) -> None:
        """Test with a large dataset to verify performance."""
        tree = AVLTree()
        n = 10000

        # Insert in random order
        import random

        values = list(range(n))
        random.shuffle(values)
        for v in values:
            tree.add((v, v))

        assert len(tree) == n

        # Verify order
        result = list(tree)
        assert result == [(i, i) for i in range(n)]

        # Verify height is O(log n)
        assert tree._root is not None
        assert tree._root.height <= 20  # log2(10000) ~= 13.3

    def test_avl_delete_root(self) -> None:
        """Test deleting the root node."""
        tree = AVLTree()
        tree.add((20, 2))
        tree.add((10, 1))
        tree.add((30, 3))
        tree.discard((20, 2))
        assert len(tree) == 2
        assert list(tree) == [(10, 1), (30, 3)]

    def test_avl_delete_all(self) -> None:
        """Test deleting all elements."""
        tree = AVLTree()
        for i in range(1, 6):
            tree.add((i, i))
        for i in range(1, 6):
            tree.discard((i, i))
        assert len(tree) == 0
        assert list(tree) == []

    def test_avl_iter_range_empty_result(self) -> None:
        """Test range iterators that return empty results."""
        tree = AVLTree()
        for i in range(10, 20):
            tree.add((i, i))

        assert list(tree.iter_lt(10)) == []
        assert list(tree.iter_gt(19)) == []
        assert list(tree.iter_eq(100)) == []
