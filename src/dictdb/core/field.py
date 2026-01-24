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


class Field:
    """
    Represents a field (column) in a table and overloads comparison operators
    to produce Condition instances.

    Instances of Field are created dynamically by the Table via attribute lookup.
    """

    def __init__(self, table: "Table", name: str) -> None:
        self.table = table
        self.name = name

    def __eq__(self, other: Any) -> PredicateExpr:  # type: ignore[override]
        return PredicateExpr(_FieldCondition(self.name, other, operator.eq))

    def __ne__(self, other: Any) -> PredicateExpr:  # type: ignore[override]
        return PredicateExpr(_FieldCondition(self.name, other, operator.ne))

    def __lt__(self, other: Any) -> PredicateExpr:
        return PredicateExpr(_FieldCondition(self.name, other, operator.lt))

    def __le__(self, other: Any) -> PredicateExpr:
        return PredicateExpr(_FieldCondition(self.name, other, operator.le))

    def __gt__(self, other: Any) -> PredicateExpr:
        return PredicateExpr(_FieldCondition(self.name, other, operator.gt))

    def __ge__(self, other: Any) -> PredicateExpr:
        return PredicateExpr(_FieldCondition(self.name, other, operator.ge))

    def is_in(self, values: Iterable[Any]) -> PredicateExpr:
        vals = set(values)
        return PredicateExpr(_IsInCondition(self.name, vals))

    def contains(self, item: Any) -> PredicateExpr:
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
        return PredicateExpr(
            lambda rec: isinstance(rec.get(self.name), str)
            and cast(str, rec.get(self.name)).startswith(prefix)
        )

    def endswith(self, suffix: str) -> PredicateExpr:
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
