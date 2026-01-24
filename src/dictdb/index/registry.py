"""Index factory for creating index instances by type name.

This module provides a registry of available index implementations and a
factory function :func:`create` to instantiate them by name.

Supported index types:

- ``"hash"``: :class:`~dictdb.index.hash.HashIndex` for O(1) equality lookups.
- ``"sorted"``: :class:`~dictdb.index.sorted.SortedIndex` for O(log n) range queries.
"""

from __future__ import annotations

from typing import Dict, Type

from .base import IndexBase
from .hash import HashIndex
from .sorted import SortedIndex


_REGISTRY: Dict[str, Type[IndexBase]] = {
    "hash": HashIndex,
    "sorted": SortedIndex,
}


def create(index_type: str) -> IndexBase:
    """Create an index instance of the specified type.

    Factory function that looks up the index class in the registry and
    returns a new instance.

    :param index_type: The type of index to create. Case-insensitive.
        Supported values: ``"hash"``, ``"sorted"``.
    :return: A new index instance of the requested type.
    :raises ValueError: If the index type is not recognized.

    Example::

        from dictdb.index import registry

        hash_idx = registry.create("hash")
        sorted_idx = registry.create("sorted")
    """
    key = index_type.lower()
    if key not in _REGISTRY:
        raise ValueError("Unsupported index type. Use 'hash' or 'sorted'.")
    return _REGISTRY[key]()
