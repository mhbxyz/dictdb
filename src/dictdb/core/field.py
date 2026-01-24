"""
Field class for building query conditions via operator overloading.

This module provides the Field class which enables a fluent query DSL by
overloading Python's comparison operators. When you access an attribute on
a Table (e.g., ``users.age``), you get a Field object. Using operators on
that Field (e.g., ``users.age >= 18``) returns a PredicateExpr that can be
wrapped in a Condition for filtering records.

Example::

    from dictdb import Table, Condition

    users = Table("users")
    # Field operators return PredicateExpr, wrap in Condition for queries
    adults = users.select(where=Condition(users.age >= 18))
"""

from __future__ import annotations

import operator
from typing import Any, Callable, Dict, Iterable, cast, TYPE_CHECKING

from .condition import PredicateExpr

if TYPE_CHECKING:  # pragma: no cover - import for typing only
    from .table import Table


class _FieldCondition:
    """
    A callable class representing a condition on a field.

    It encapsulates the field name, a value to compare, and an operator function.
    """

    def __init__(self, field: str, value: Any, op: Callable[[Any, Any], bool]) -> None:
        self.field: str = field
        self.value: Any = value
        self.op: Callable[[Any, Any], bool] = op

    def __call__(self, record: Dict[str, Any]) -> bool:
        return self.op(record.get(self.field), self.value)


class _IsInCondition:
    """
    A callable class representing an 'is_in' condition on a field.

    Encapsulates the field name and a set of values to check membership against.
    """

    def __init__(self, field: str, values: set[Any]) -> None:
        self.field: str = field
        self.values: set[Any] = values

    def __call__(self, record: Dict[str, Any]) -> bool:
        return record.get(self.field) in self.values


class _BetweenCondition:
    """
    A callable class representing a 'between' condition on a field.

    Checks if a field value is within an inclusive range [low, high].
    """

    def __init__(self, field: str, low: Any, high: Any) -> None:
        self.field: str = field
        self.low: Any = low
        self.high: Any = high

    def __call__(self, record: Dict[str, Any]) -> bool:
        val = record.get(self.field)
        if val is None:
            return False
        try:
            return bool(self.low <= val <= self.high)
        except TypeError:
            return False


class Field:
    """
    Represents a field (column) in a table and overloads comparison operators
    to produce Condition instances.

    Instances of Field are created dynamically by the Table via attribute lookup.
    """

    def __init__(self, table: "Table", name: str) -> None:
        """
        Initialize a Field bound to a table and field name.

        :param table: The Table instance this field belongs to.
        :param name: The name of the field (column) in the table.
        """
        self.table = table
        self.name = name

    def __eq__(self, other: Any) -> PredicateExpr:  # type: ignore[override]
        """
        Create an equality condition (field == value).

        :param other: The value to compare against.
        :return: A PredicateExpr that matches records where field equals value.
        """
        return PredicateExpr(_FieldCondition(self.name, other, operator.eq))

    def __ne__(self, other: Any) -> PredicateExpr:  # type: ignore[override]
        """
        Create a not-equal condition (field != value).

        :param other: The value to compare against.
        :return: A PredicateExpr that matches records where field does not equal value.
        """
        return PredicateExpr(_FieldCondition(self.name, other, operator.ne))

    def __lt__(self, other: Any) -> PredicateExpr:
        """
        Create a less-than condition (field < value).

        :param other: The value to compare against.
        :return: A PredicateExpr that matches records where field is less than value.
        """
        return PredicateExpr(_FieldCondition(self.name, other, operator.lt))

    def __le__(self, other: Any) -> PredicateExpr:
        """
        Create a less-than-or-equal condition (field <= value).

        :param other: The value to compare against.
        :return: A PredicateExpr that matches records where field is less than or equal to value.
        """
        return PredicateExpr(_FieldCondition(self.name, other, operator.le))

    def __gt__(self, other: Any) -> PredicateExpr:
        """
        Create a greater-than condition (field > value).

        :param other: The value to compare against.
        :return: A PredicateExpr that matches records where field is greater than value.
        """
        return PredicateExpr(_FieldCondition(self.name, other, operator.gt))

    def __ge__(self, other: Any) -> PredicateExpr:
        """
        Create a greater-than-or-equal condition (field >= value).

        :param other: The value to compare against.
        :return: A PredicateExpr that matches records where field is greater than or equal to value.
        """
        return PredicateExpr(_FieldCondition(self.name, other, operator.ge))

    def is_in(self, values: Iterable[Any]) -> PredicateExpr:
        """
        Create a membership condition (field IN values).

        :param values: An iterable of values to check membership against.
        :return: A PredicateExpr that matches records where field value is in the set.
        """
        vals = set(values)
        return PredicateExpr(_IsInCondition(self.name, vals))

    def contains(self, item: Any) -> PredicateExpr:
        """
        Create a containment condition (item IN field).

        Checks if the field value contains the given item. Works with strings,
        lists, and other container types that support the ``in`` operator.

        :param item: The item to search for within the field value.
        :return: A PredicateExpr that matches records where field contains item.
        """

        def _pred(rec: Dict[str, Any]) -> bool:
            val = rec.get(self.name)
            if val is None:
                return False
            try:
                return item in val
            except TypeError:
                return False

        return PredicateExpr(_pred)

    def startswith(self, prefix: str) -> PredicateExpr:
        """
        Create a prefix condition for string fields.

        :param prefix: The prefix string to match against.
        :return: A PredicateExpr that matches records where field starts with prefix.
        """
        return PredicateExpr(
            lambda rec: isinstance(rec.get(self.name), str)
            and cast(str, rec.get(self.name)).startswith(prefix)
        )

    def endswith(self, suffix: str) -> PredicateExpr:
        """
        Create a suffix condition for string fields.

        :param suffix: The suffix string to match against.
        :return: A PredicateExpr that matches records where field ends with suffix.
        """
        return PredicateExpr(
            lambda rec: isinstance(rec.get(self.name), str)
            and cast(str, rec.get(self.name)).endswith(suffix)
        )

    def is_null(self) -> PredicateExpr:
        """Check if the field value is None or the field is missing."""
        return PredicateExpr(lambda rec: rec.get(self.name) is None)

    def is_not_null(self) -> PredicateExpr:
        """Check if the field value is not None and the field exists."""
        return PredicateExpr(lambda rec: rec.get(self.name) is not None)

    def between(self, low: Any, high: Any) -> PredicateExpr:
        """
        Create a range condition (low <= field <= high).

        Checks if the field value is within the inclusive range [low, high].
        This is equivalent to ``(field >= low) & (field <= high)`` but may
        be optimized to use a single index scan when a sorted index exists.

        :param low: The lower bound (inclusive).
        :param high: The upper bound (inclusive).
        :return: A PredicateExpr that matches records where field is in range.

        Example::

            # Find users aged 18 to 65
            users.select(where=Condition(users.age.between(18, 65)))
        """
        return PredicateExpr(_BetweenCondition(self.name, low, high))
