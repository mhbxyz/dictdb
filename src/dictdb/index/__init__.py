"""
Index package exposing base and concrete index implementations.

Re-exports:
- IndexBase: abstract base/Protocol for indices
- HashIndex: hash map based index (equality)
- SortedIndex: sorted list index (basic range support)
"""

from .base import IndexBase
from .hash import HashIndex
from .sorted import SortedIndex

__all__ = ["IndexBase", "HashIndex", "SortedIndex"]
