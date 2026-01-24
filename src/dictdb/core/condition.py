from typing import Any

from .types import Record, Predicate


class PredicateExpr:
    """
    Represents a low-level predicate to be applied to a record.

    Wraps a function that takes a record (dict) and returns a boolean. Supports
    logical operations using & (AND), | (OR), and ~ (NOT). Prevents implicit
    boolean conversion to avoid accidental misuse.
    """

    def __init__(self, func: Predicate) -> None:
        """
        Initialize with a callable predicate.

        :param func: A function taking a record (dict) and returning bool.
        :type func: Callable[[Record], bool]
        """
        self.func: Predicate = func

    def __call__(self, record: Record) -> bool:
        """
        Evaluate the wrapped predicate on a given record.
        """
        return self.func(record)

    def __and__(self, other: "PredicateExpr") -> "PredicateExpr":
        """
        Combine two predicates with logical AND.

        :param other: Another PredicateExpr to combine with.
        :return: A new PredicateExpr that is True only if both predicates are True.
        """
        return PredicateExpr(lambda rec: self(rec) and other(rec))

    def __or__(self, other: "PredicateExpr") -> "PredicateExpr":
        """
        Combine two predicates with logical OR.

        :param other: Another PredicateExpr to combine with.
        :return: A new PredicateExpr that is True if either predicate is True.
        """
        return PredicateExpr(lambda rec: self(rec) or other(rec))

    def __invert__(self) -> "PredicateExpr":
        """
        Negate this predicate with logical NOT.

        :return: A new PredicateExpr that is True when this predicate is False.
        """
        return PredicateExpr(lambda rec: not self(rec))

    def __bool__(self) -> bool:
        """
        Prevent implicit boolean conversion of predicate expressions.
        """
        raise TypeError(
            "PredicateExpr objects should not be evaluated as booleans; wrap them in Condition instead."
        )


class Condition:
    """
    A user-facing wrapper around a PredicateExpr to be used as a filter.

    Encapsulating a PredicateExpr in a Condition avoids accidental boolean
    conversion. Pass Condition instances as the `where` parameter in CRUD methods.
    """

    def __init__(self, condition: Any) -> None:
        """
        Initialize the wrapper with a PredicateExpr.
        """
        if not isinstance(condition, PredicateExpr):
            raise TypeError(
                "Argument 'condition' must be a PredicateExpr (e.g., Condition(Table.field == value))."
            )
        self.condition: PredicateExpr = condition

    def __call__(self, record: Record) -> bool:
        """
        Evaluate the condition on a given record.

        :param record: The record (dict) to evaluate.
        :return: True if the record satisfies the condition, False otherwise.
        """
        return self.condition(record)

    def __and__(self, other: "Condition") -> "Condition":
        """
        Combine two conditions with logical AND.

        :param other: Another Condition to combine with.
        :return: A new Condition that is True only if both conditions are True.
        """
        return Condition(self.condition & other.condition)

    def __or__(self, other: "Condition") -> "Condition":
        """
        Combine two conditions with logical OR.

        :param other: Another Condition to combine with.
        :return: A new Condition that is True if either condition is True.
        """
        return Condition(self.condition | other.condition)

    def __invert__(self) -> "Condition":
        """
        Negate this condition with logical NOT.

        :return: A new Condition that is True when this condition is False.
        """
        return Condition(~self.condition)
