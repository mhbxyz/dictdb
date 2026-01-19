import pytest

from dictdb import Table, Condition


def test_field_equality(table: Table) -> None:
    """
    Tests that a field equality condition (e.g., table.name == "Alice") filters records correctly.

    :param table: A prepopulated Table fixture.
    :type table: Table
    """
    condition = Condition(table.name == "Alice")
    assert condition({"name": "Alice"}) is True, "Equality should match exact value"
    assert condition({"name": "Bob"}) is False, (
        "Equality should not match different value"
    )


@pytest.mark.parametrize(
    "age_value,op,compare_to,expected",
    [
        # age == 30 tests
        pytest.param(30, "==", 30, True, id="eq_match"),
        pytest.param(25, "==", 30, False, id="eq_no_match"),
        pytest.param(35, "==", 30, False, id="eq_greater_no_match"),
        # age != 30 tests
        pytest.param(25, "!=", 30, True, id="ne_less_match"),
        pytest.param(35, "!=", 30, True, id="ne_greater_match"),
        pytest.param(30, "!=", 30, False, id="ne_equal_no_match"),
        # age < 30 tests
        pytest.param(25, "<", 30, True, id="lt_match"),
        pytest.param(30, "<", 30, False, id="lt_equal_no_match"),
        pytest.param(35, "<", 30, False, id="lt_greater_no_match"),
        # age <= 30 tests
        pytest.param(25, "<=", 30, True, id="le_less_match"),
        pytest.param(30, "<=", 30, True, id="le_equal_match"),
        pytest.param(35, "<=", 30, False, id="le_greater_no_match"),
        # age > 30 tests
        pytest.param(35, ">", 30, True, id="gt_match"),
        pytest.param(30, ">", 30, False, id="gt_equal_no_match"),
        pytest.param(25, ">", 30, False, id="gt_less_no_match"),
        # age >= 30 tests
        pytest.param(35, ">=", 30, True, id="ge_greater_match"),
        pytest.param(30, ">=", 30, True, id="ge_equal_match"),
        pytest.param(25, ">=", 30, False, id="ge_less_no_match"),
    ],
)
def test_comparison_operators(
    table: Table, age_value: int, op: str, compare_to: int, expected: bool
) -> None:
    """
    Tests comparison operators (==, !=, <, <=, >, >=) on a table field.

    :param table: A prepopulated Table fixture.
    :param age_value: The value of the 'age' field in the test record.
    :param op: The operator being tested.
    :param compare_to: The value to compare against.
    :param expected: The expected result of the condition.
    """
    conditions = {
        "==": Condition(table.age == compare_to),
        "!=": Condition(table.age != compare_to),
        "<": Condition(table.age < compare_to),
        "<=": Condition(table.age <= compare_to),
        ">": Condition(table.age > compare_to),
        ">=": Condition(table.age >= compare_to),
    }
    condition = conditions[op]
    record = {"age": age_value}
    result = condition(record)
    assert result == expected, f"{age_value} {op} {compare_to} should be {expected}"


def test_logical_operators(table: Table) -> None:
    """
    Tests logical AND, OR, and NOT operators when combining field conditions.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    # Logical AND: (name == "Alice") AND (age > 25)
    condition = Condition((table.name == "Alice") & (table.age > 25))
    record = {"name": "Alice", "age": 30}
    assert condition(record)
    record = {"name": "Alice", "age": 20}
    assert not condition(record)

    # Logical OR: (name == "Alice") OR (age > 25)
    condition = Condition((table.name == "Alice") | (table.age > 25))
    record = {"name": "Bob", "age": 30}
    assert condition(record)
    record = {"name": "Alice", "age": 20}
    assert condition(record)
    record = {"name": "Bob", "age": 20}
    assert not condition(record)

    # Logical NOT: NOT (name == "Alice")
    condition = Condition(~(table.name == "Alice"))
    record = {"name": "Bob"}
    assert condition(record)
    record = {"name": "Alice"}
    assert not condition(record)
