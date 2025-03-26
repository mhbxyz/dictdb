from typing import Callable, Dict, Any

Predicate = Callable[[Dict[str, Any]], bool]


class Condition:
    """
    Represents a condition (predicate) to be applied to a record.

    Wraps a function that takes a record (dict) and returns a boolean.
    Supports logical operations using:
        - & for logical AND
        - | for logical OR
        - ~ for logical NOT

    Note:
        Implicit boolean conversion is disallowed to prevent accidental usage.
    """

    def __init__(self, func: Predicate) -> None:
        self.func: Predicate = func

    def __call__(self, record: Dict[str, Any]) -> bool:
        return self.func(record)

    def __and__(self, other: "Condition") -> "Condition":
        return Condition(lambda rec: self(rec) and other(rec))

    def __or__(self, other: "Condition") -> "Condition":
        return Condition(lambda rec: self(rec) or other(rec))

    def __invert__(self) -> "Condition":
        return Condition(lambda rec: not self(rec))

    def __bool__(self) -> bool:
        # Prevent implicit boolean conversion
        raise TypeError("Condition objects should not be evaluated as booleans; wrap them in Query instead.")


class Query:
    """
    A wrapper for a Condition to be used as a query predicate.

    By encapsulating a Condition in a Query, implicit boolean conversion
    is avoided, and the Query object can be safely passed as the `where` parameter
    in CRUD methods.

    Example usage:
        Query(table.name == "Alice")
        Query((table.name == "Alice") & (table.age > 25))
    """

    def __init__(self, condition: Condition | bool) -> None:
        self.condition: Condition = condition

    def __call__(self, record: Dict[str, Any]) -> bool:
        return self.condition(record)

    def __and__(self, other: "Query") -> "Query":
        return Query(self.condition & other.condition)

    def __or__(self, other: "Query") -> "Query":
        return Query(self.condition | other.condition)

    def __invert__(self) -> "Query":
        return Query(~self.condition)
