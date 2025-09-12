from typing import Any, Dict, Callable, Type

__all__ = ["Record", "Schema", "Predicate"]

Record = Dict[str, Any]
"""
Type alias for a database record.
Each record is represented by a dictionary with string keys and arbitrary values.
"""

Schema = Dict[str, Type[Any]]
"""
Type alias for a table schema definition.
A schema maps field names (strings) to Python types (e.g., ``int``, ``str``, etc.).
"""

Predicate = Callable[[Record], bool]
"""
Type alias for a predicate function that takes a Record and returns a boolean.
Used in conditions for filtering records.
"""
