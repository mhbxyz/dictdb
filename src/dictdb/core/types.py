from typing import Any, Dict, Callable, Type

__all__ = [
    "Record",
    "Schema",
    "Predicate",
    "ALLOWED_SCHEMA_TYPES",
    "parse_schema_type",
    "serialize_schema_type",
]

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

# Whitelist of types allowed in schemas for serialization/deserialization.
ALLOWED_SCHEMA_TYPES: Dict[str, Type[Any]] = {
    "int": int,
    "str": str,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}

# Reverse mapping for serialization
_TYPE_TO_NAME: Dict[Type[Any], str] = {v: k for k, v in ALLOWED_SCHEMA_TYPES.items()}


def parse_schema_type(type_name: str) -> Type[Any]:
    """
    Convert a type name string to the corresponding Python type.

    :param type_name: The name of the type (e.g., "int", "str").
    :raises ValueError: If the type name is not in the allowed list.
    :return: The corresponding Python type.
    """
    if type_name not in ALLOWED_SCHEMA_TYPES:
        raise ValueError(f"Unsupported type in schema: {type_name}")
    return ALLOWED_SCHEMA_TYPES[type_name]


def serialize_schema_type(typ: Type[Any]) -> str:
    """
    Convert a Python type to its string name for serialization.

    :param typ: The Python type (e.g., int, str).
    :raises ValueError: If the type is not in the allowed list.
    :return: The string name of the type.
    """
    if typ not in _TYPE_TO_NAME:
        raise ValueError(f"Cannot serialize type: {typ.__name__}")
    return _TYPE_TO_NAME[typ]
