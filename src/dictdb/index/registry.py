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
    key = index_type.lower()
    if key not in _REGISTRY:
        raise ValueError("Unsupported index type. Use 'hash' or 'sorted'.")
    return _REGISTRY[key]()
