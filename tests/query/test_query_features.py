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


# --- Tests for select() optimizations ---


@pytest.fixture
def large_table() -> Table:
    """Table with 100 records for testing optimizations."""
    t = Table("items", primary_key="id")
    for i in range(1, 101):
        t.insert({"id": i, "value": 100 - i, "name": f"item_{i:03d}"})
    return t


def test_early_termination_limit_without_order_by(large_table: Table) -> None:
    """Test that LIMIT without ORDER BY returns correct results."""
    # Without order_by, should return first N records (in insertion order)
    results = large_table.select(limit=5)
    assert len(results) == 5
    # First 5 records by insertion order
    ids = [r["id"] for r in results]
    assert ids == [1, 2, 3, 4, 5]


def test_early_termination_limit_offset_without_order_by(large_table: Table) -> None:
    """Test that LIMIT + OFFSET without ORDER BY returns correct results."""
    results = large_table.select(limit=5, offset=10)
    assert len(results) == 5
    ids = [r["id"] for r in results]
    assert ids == [11, 12, 13, 14, 15]


def test_heapq_order_by_asc_with_limit(large_table: Table) -> None:
    """Test ORDER BY ASC + LIMIT uses heapq optimization correctly."""
    # Get 5 smallest values
    results = large_table.select(order_by="value", limit=5)
    assert len(results) == 5
    values = [r["value"] for r in results]
    # Smallest values are 0,1,2,3,4 (corresponding to id 100,99,98,97,96)
    assert values == [0, 1, 2, 3, 4]


def test_heapq_order_by_desc_with_limit(large_table: Table) -> None:
    """Test ORDER BY DESC + LIMIT uses heapq optimization correctly."""
    # Get 5 largest values
    results = large_table.select(order_by="-value", limit=5)
    assert len(results) == 5
    values = [r["value"] for r in results]
    # Largest values are 99,98,97,96,95 (corresponding to id 1,2,3,4,5)
    assert values == [99, 98, 97, 96, 95]


def test_heapq_order_by_with_limit_and_offset(large_table: Table) -> None:
    """Test ORDER BY + LIMIT + OFFSET returns correct results."""
    # Get records 6-10 by ascending value
    results = large_table.select(order_by="value", limit=5, offset=5)
    assert len(results) == 5
    values = [r["value"] for r in results]
    assert values == [5, 6, 7, 8, 9]


def test_multi_field_order_by_with_limit() -> None:
    """Test that multi-field ORDER BY + LIMIT still works correctly."""
    t = Table("data", primary_key="id")
    t.insert({"id": 1, "group": "A", "score": 10})
    t.insert({"id": 2, "group": "B", "score": 20})
    t.insert({"id": 3, "group": "A", "score": 30})
    t.insert({"id": 4, "group": "B", "score": 10})
    t.insert({"id": 5, "group": "A", "score": 20})

    # Order by group asc, score desc, limit 3
    results = t.select(order_by=["group", "-score"], limit=3)
    assert len(results) == 3
    data = [(r["group"], r["score"]) for r in results]
    # Group A: scores 30,20,10 (desc) -> (A,30), (A,20), (A,10)
    # Group B: scores 20,10 (desc) -> (B,20), (B,10)
    # First 3 should be (A,30), (A,20), (A,10)
    assert data == [("A", 30), ("A", 20), ("A", 10)]
