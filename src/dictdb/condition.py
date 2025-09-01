from typing import Any

from .types import Record, Predicate


class Condition:
    """
    Represents a condition (predicate) to be applied to a record.

    Wraps a function that takes a record (dict) and returns a boolean. Supports
    logical operations using & (AND), | (OR), and ~ (NOT). Prevents implicit
    boolean conversion to avoid accidental misuse.
    """

    def __init__(self, func: Predicate) -> None:
        """
        Initializes the Condition with a callable predicate.

        :param func: A function taking a record (dict) and returning bool.
        :type func: Callable[[Record], bool]
        :return: None
        :rtype: None
        """
        self.func: Predicate = func

    def __call__(self, record: Record) -> bool:
        """
        Evaluates the wrapped predicate on a given record.

        :param record: The record (dict) to evaluate.
        :type record: dict
        :return: True if the predicate is satisfied, otherwise False.
        :rtype: bool
        """
        return self.func(record)

    def __and__(self, other: "Condition") -> "Condition":
        """
        Returns a new Condition representing a logical AND of this
        Condition and another.

        :param other: Another Condition instance.
        :type other: Condition
        :return: A new Condition.
        :rtype: Condition
        """
        return Condition(lambda rec: self(rec) and other(rec))

    def __or__(self, other: "Condition") -> "Condition":
        """
        Returns a new Condition representing a logical OR of this
        Condition and another.

        :param other: Another Condition instance.
        :type other: Condition
        :return: A new Condition.
        :rtype: Condition
        """
        return Condition(lambda rec: self(rec) or other(rec))

    def __invert__(self) -> "Condition":
        """
        Returns a new Condition representing the logical NOT of this Condition.

        :return: A new Condition.
        :rtype: Condition
        """
        return Condition(lambda rec: not self(rec))

    def __bool__(self) -> bool:
        """
        Prevents implicit boolean conversion of Condition objects.

        :raises TypeError: Always raised to disallow boolean context usage.
        """
        raise TypeError(
            "Condition objects should not be evaluated as booleans; wrap them in Query instead."
        )


class Query:
    """
    A wrapper for a Condition to be used as a query predicate.

    By encapsulating a Condition in a Query, implicit boolean conversion
    is avoided. The Query object can be passed as the `where` parameter in
    CRUD methods.
    """

    def __init__(self, condition: Any) -> None:
        """
        Initializes the Query with a given Condition.

        :param condition: A Condition instance to wrap.
        :type condition: Condition
        :raises TypeError: If 'condition' is not an instance of Condition.
        :return: None
        :rtype: None
        """
        if not isinstance(condition, Condition):
            raise TypeError(
                "Argument 'condition' must be an instance of Condition "
                "(e.g., Query(Table.field == value)."
            )
        self.condition: Condition = condition

    def __call__(self, record: Record) -> bool:
        """
        Evaluates the underlying Condition on the given record.

        :param record: The record (dict) to evaluate.
        :type record: dict
        :return: True if the Condition is satisfied, otherwise False.
        :rtype: bool
        """
        return self.condition(record)

    def __and__(self, other: "Query") -> "Query":
        """
        Returns a new Query representing a logical AND between
        this Query and another Query.

        :param other: Another Query instance.
        :type other: Query
        :return: A new Query.
        :rtype: Query
        """
        return Query(self.condition & other.condition)

    def __or__(self, other: "Query") -> "Query":
        """
        Returns a new Query representing a logical OR between
        this Query and another Query.

        :param other: Another Query instance.
        :type other: Query
        :return: A new Query.
        :rtype: Query
        """
        return Query(self.condition | other.condition)

    def __invert__(self) -> "Query":
        """
        Returns a new Query representing the logical NOT of this Query.

        :return: A new Query.
        :rtype: Query
        """
        return Query(~self.condition)
