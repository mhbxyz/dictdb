from dictdb import Table, Condition


def test_field_equality(table: Table) -> None:
    """
    Tests that a field equality condition (e.g., table.name == "Alice") filters records correctly.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    # Wrap the predicate in Condition so it can be used safely
    condition = Condition(table.name == "Alice")
    record = {"name": "Alice"}
    assert condition(record) is True
    record = {"name": "Bob"}
    assert condition(record) is False


def test_comparison_operators(table: Table) -> None:
    """
    Tests all standard comparison operators (==, !=, <, <=, >, >=) on a table field.

    :param table: A prepopulated Table fixture.
    :type table: Table
    :return: None
    :rtype: None
    """
    eq_cond = Condition(table.age == 30)
    ne_cond = Condition(table.age != 30)
    lt_cond = Condition(table.age < 30)
    le_cond = Condition(table.age <= 30)
    gt_cond = Condition(table.age > 30)
    ge_cond = Condition(table.age >= 30)

    record = {"age": 30}
    assert eq_cond(record)
    assert not ne_cond(record)
    assert not lt_cond(record)
    assert le_cond(record)
    assert not gt_cond(record)
    assert ge_cond(record)

    record = {"age": 25}
    assert not eq_cond(record)
    assert ne_cond(record)
    assert lt_cond(record)
    assert le_cond(record)
    assert not gt_cond(record)
    assert not ge_cond(record)


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
