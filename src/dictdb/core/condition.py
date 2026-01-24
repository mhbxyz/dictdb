from typing import Any, Union

from .types import Record, Predicate

# Type alias for expressions that can be used in logical functions
LogicalOperand = Union["PredicateExpr", "Condition"]


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


def _to_predicate(operand: LogicalOperand) -> PredicateExpr:
    """
    Convert a LogicalOperand to a PredicateExpr.

    :param operand: A PredicateExpr or Condition.
    :return: The underlying PredicateExpr.
    :raises TypeError: If operand is not a valid type.
    """
    if isinstance(operand, PredicateExpr):
        return operand
    if isinstance(operand, Condition):
        return operand.condition
    raise TypeError(
        f"Expected PredicateExpr or Condition, got {type(operand).__name__}"
    )


def And(*operands: LogicalOperand) -> PredicateExpr:
    """
    Combine multiple conditions with logical AND.

    Returns a PredicateExpr that is True only if all operands are True.
    More readable alternative to the ``&`` operator.

    :param operands: Two or more PredicateExpr or Condition objects.
    :return: A PredicateExpr representing the AND of all operands.
    :raises ValueError: If fewer than 2 operands are provided.

    Example::

        from dictdb import And

        # Simple AND
        users.select(where=And(users.age >= 18, users.active == True))

        # Multiple conditions
        users.select(where=And(
            users.department == "IT",
            users.salary >= 50000,
            users.status == "active"
        ))
    """
    if len(operands) < 2:
        raise ValueError("And() requires at least 2 operands")

    predicates = [_to_predicate(op) for op in operands]
    result = predicates[0]
    for pred in predicates[1:]:
        result = result & pred
    return result


def Or(*operands: LogicalOperand) -> PredicateExpr:
    """
    Combine multiple conditions with logical OR.

    Returns a PredicateExpr that is True if any operand is True.
    More readable alternative to the ``|`` operator.

    :param operands: Two or more PredicateExpr or Condition objects.
    :return: A PredicateExpr representing the OR of all operands.
    :raises ValueError: If fewer than 2 operands are provided.

    Example::

        from dictdb import Or

        # Simple OR
        users.select(where=Or(users.department == "IT", users.department == "HR"))

        # Multiple conditions
        users.select(where=Or(
            users.role == "admin",
            users.role == "moderator",
            users.is_superuser == True
        ))
    """
    if len(operands) < 2:
        raise ValueError("Or() requires at least 2 operands")

    predicates = [_to_predicate(op) for op in operands]
    result = predicates[0]
    for pred in predicates[1:]:
        result = result | pred
    return result


def Not(operand: LogicalOperand) -> PredicateExpr:
    """
    Negate a condition with logical NOT.

    Returns a PredicateExpr that is True when the operand is False.
    More readable alternative to the ``~`` operator.

    :param operand: A PredicateExpr or Condition to negate.
    :return: A PredicateExpr representing the negation.

    Example::

        from dictdb import Not

        # Simple NOT
        users.select(where=Not(users.department == "Sales"))

        # Combined with And/Or
        users.select(where=And(
            users.age >= 18,
            Not(users.status == "banned")
        ))
    """
    return ~_to_predicate(operand)
