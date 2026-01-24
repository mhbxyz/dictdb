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


def test_is_null_with_none_value(table: Table) -> None:
    """Test is_null returns True when field value is None."""
    cond = Condition(table.email.is_null())
    assert cond({"email": None}) is True
    assert cond({"email": "test@example.com"}) is False


def test_is_null_with_missing_field(table: Table) -> None:
    """Test is_null returns True when field is missing."""
    cond = Condition(table.email.is_null())
    assert cond({}) is True
    assert cond({"name": "Alice"}) is True


def test_is_not_null_with_value(table: Table) -> None:
    """Test is_not_null returns True when field has a value."""
    cond = Condition(table.email.is_not_null())
    assert cond({"email": "test@example.com"}) is True
    assert cond({"email": ""}) is True  # Empty string is not null
    assert cond({"email": 0}) is True  # Zero is not null


def test_is_not_null_with_none_or_missing(table: Table) -> None:
    """Test is_not_null returns False when field is None or missing."""
    cond = Condition(table.email.is_not_null())
    assert cond({"email": None}) is False
    assert cond({}) is False


def test_is_null_combined_with_other_conditions(table: Table) -> None:
    """Test is_null can be combined with other conditions."""
    cond = Condition(table.status == "active") & Condition(table.email.is_not_null())
    assert cond({"status": "active", "email": "a@b.com"}) is True
    assert cond({"status": "active", "email": None}) is False
    assert cond({"status": "inactive", "email": "a@b.com"}) is False
