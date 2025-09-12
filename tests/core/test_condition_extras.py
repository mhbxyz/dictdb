import pytest

from dictdb import Table, Condition


def test_predicate_expr_bool_raises(table: Table) -> None:
    pred = table.name == "Alice"
    with pytest.raises(TypeError):
        bool(pred)


def test_condition_invalid_init_type() -> None:
    with pytest.raises(TypeError):
        Condition("not a predicate")


def test_condition_boolean_ops_methods(table: Table) -> None:
    c1 = Condition(table.age > 20)
    c2 = Condition(table.name == "Alice")

    c_and = c1 & c2
    assert c_and({"age": 30, "name": "Alice"}) is True
    assert c_and({"age": 30, "name": "Bob"}) is False

    c_or = c1 | c2
    assert c_or({"age": 10, "name": "Alice"}) is True
    assert c_or({"age": 10, "name": "Bob"}) is False

    c_not = ~c2
    assert c_not({"name": "Bob"}) is True
    assert c_not({"name": "Alice"}) is False
