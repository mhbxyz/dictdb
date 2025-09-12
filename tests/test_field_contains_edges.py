from dictdb import Table, Condition


def test_contains_with_none_value() -> None:
    table = Table("t")
    cond = Condition(table.tags.contains("x"))
    assert cond({"tags": None}) is False


def test_contains_with_non_iterable() -> None:
    table = Table("t")
    cond = Condition(table.tags.contains("x"))
    # 'in' on int raises TypeError internally; predicate should return False
    assert cond({"tags": 123}) is False
