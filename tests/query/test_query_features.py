import pytest

from dictdb import Table, Condition


@pytest.fixture
def people() -> Table:
    t = Table("people", primary_key="id")
    t.insert({"id": 1, "name": "Alice", "age": 30, "city": "Paris"})
    t.insert({"id": 2, "name": "Bob", "age": 25, "city": "Berlin"})
    t.insert({"id": 3, "name": "Charlie", "age": 30, "city": "Boston"})
    t.insert({"id": 4, "name": "Albert", "age": 40, "city": "Prague"})
    return t


def test_in_operator(people: Table) -> None:
    cond = Condition(people.age.is_in([25, 40]))
    results = people.select(where=cond, order_by="id")
    ages = [r["age"] for r in results]
    assert ages == [25, 40]


def test_contains_and_string_prefix_suffix(people: Table) -> None:
    # contains substring
    cond = Condition(people.city.contains("Bo"))
    results = people.select(where=cond)
    assert {r["city"] for r in results} == {"Boston"}

    # startswith
    cond = Condition(people.name.startswith("Al"))
    results = people.select(where=cond, order_by="name")
    assert [r["name"] for r in results] == ["Albert", "Alice"]

    # endswith
    cond = Condition(people.name.endswith("e"))
    results = people.select(where=cond, order_by="id")
    assert [r["name"] for r in results] == ["Alice", "Charlie"]


def test_order_by_multi_field(people: Table) -> None:
    # Order by age asc, then name desc
    rows = people.select(order_by=["age", "-name"])
    # Ages are 25,30,30,40 and within age=30, names should be in reverse alpha: Charlie, Alice
    data = [(r["age"], r["name"]) for r in rows]
    assert data == [(25, "Bob"), (30, "Charlie"), (30, "Alice"), (40, "Albert")]


def test_limit_offset(people: Table) -> None:
    rows = people.select(order_by="id", limit=2, offset=1)
    ids = [r["id"] for r in rows]
    assert ids == [2, 3]


def test_projection_with_aliases(people: Table) -> None:
    # Dict of alias -> field
    projected = people.select(columns={"person": "name", "years": "age"}, order_by="id")
    assert projected[0] == {"person": "Alice", "years": 30}

    # List of (alias, field)
    pairs = [("person", "name"), ("years", "age")]
    projected2 = people.select(columns=pairs, order_by="id")
    assert projected2[1] == {"person": "Bob", "years": 25}
