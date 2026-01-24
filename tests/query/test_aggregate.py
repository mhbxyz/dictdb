"""
Unit tests for aggregation functions and GROUP BY support.
"""

from typing import List

import pytest

from dictdb import Table, Condition, Count, Sum, Avg, Min, Max
from dictdb.core.types import Record
from dictdb.query.aggregate import (
    compute_aggregations,
    group_and_aggregate,
)


class TestAggregationClasses:
    """Tests for aggregation class compute methods."""

    def test_count_all_records(self) -> None:
        """Test Count() counts all records."""
        agg = Count()
        assert agg.compute([1, 2, 3, None, 5]) == 5

    def test_count_field_excludes_none(self) -> None:
        """Test Count(field) excludes None values."""
        agg = Count("name")
        assert agg.compute([1, 2, None, 3, None]) == 3

    def test_count_empty(self) -> None:
        """Test count of empty list."""
        agg = Count()
        assert agg.compute([]) == 0

    def test_sum_numeric(self) -> None:
        """Test sum of numeric values."""
        agg = Sum("value")
        assert agg.compute([1, 2, 3, 4, 5]) == 15

    def test_sum_with_none(self) -> None:
        """Test sum ignores None values."""
        agg = Sum("value")
        assert agg.compute([1, None, 2, None, 3]) == 6

    def test_sum_empty(self) -> None:
        """Test sum of empty list returns None."""
        agg = Sum("value")
        assert agg.compute([]) is None

    def test_sum_all_none(self) -> None:
        """Test sum of all None values returns None."""
        agg = Sum("value")
        assert agg.compute([None, None]) is None

    def test_avg_numeric(self) -> None:
        """Test average of numeric values."""
        agg = Avg("value")
        assert agg.compute([2, 4, 6]) == 4.0

    def test_avg_with_none(self) -> None:
        """Test avg ignores None values."""
        agg = Avg("value")
        assert agg.compute([2, None, 4, None, 6]) == 4.0

    def test_avg_empty(self) -> None:
        """Test avg of empty list returns None."""
        agg = Avg("value")
        assert agg.compute([]) is None

    def test_min_numeric(self) -> None:
        """Test min of numeric values."""
        agg = Min("value")
        assert agg.compute([5, 2, 8, 1, 9]) == 1

    def test_min_with_none(self) -> None:
        """Test min ignores None values."""
        agg = Min("value")
        assert agg.compute([5, None, 2, None]) == 2

    def test_min_empty(self) -> None:
        """Test min of empty list returns None."""
        agg = Min("value")
        assert agg.compute([]) is None

    def test_min_strings(self) -> None:
        """Test min works with strings."""
        agg = Min("name")
        assert agg.compute(["banana", "apple", "cherry"]) == "apple"

    def test_max_numeric(self) -> None:
        """Test max of numeric values."""
        agg = Max("value")
        assert agg.compute([5, 2, 8, 1, 9]) == 9

    def test_max_with_none(self) -> None:
        """Test max ignores None values."""
        agg = Max("value")
        assert agg.compute([5, None, 2, None]) == 5

    def test_max_empty(self) -> None:
        """Test max of empty list returns None."""
        agg = Max("value")
        assert agg.compute([]) is None


class TestComputeAggregations:
    """Tests for compute_aggregations function."""

    def test_single_aggregation(self) -> None:
        """Test computing a single aggregation."""
        records: List[Record] = [{"salary": 100}, {"salary": 200}, {"salary": 300}]
        result = compute_aggregations(records, {"total": Sum("salary")})
        assert result == {"total": 600}

    def test_multiple_aggregations(self) -> None:
        """Test computing multiple aggregations."""
        records: List[Record] = [{"age": 20}, {"age": 30}, {"age": 40}]
        result = compute_aggregations(
            records,
            {
                "min_age": Min("age"),
                "max_age": Max("age"),
                "avg_age": Avg("age"),
            },
        )
        assert result == {"min_age": 20, "max_age": 40, "avg_age": 30.0}

    def test_count_all(self) -> None:
        """Test Count() counts all records."""
        records: List[Record] = [{"a": 1}, {"a": 2}, {"a": None}]
        result = compute_aggregations(records, {"n": Count()})
        assert result == {"n": 3}

    def test_count_field(self) -> None:
        """Test Count(field) counts non-None values."""
        records: List[Record] = [{"a": 1}, {"a": 2}, {"a": None}]
        result = compute_aggregations(records, {"n": Count("a")})
        assert result == {"n": 2}


class TestGroupAndAggregate:
    """Tests for group_and_aggregate function."""

    def test_group_by_single_field(self) -> None:
        """Test grouping by a single field."""
        records: List[Record] = [
            {"dept": "IT", "salary": 100},
            {"dept": "IT", "salary": 200},
            {"dept": "HR", "salary": 150},
        ]
        result = group_and_aggregate(
            records, "dept", {"total": Sum("salary"), "count": Count()}
        )
        result = sorted(result, key=lambda x: x["dept"])
        assert len(result) == 2
        assert result[0] == {"dept": "HR", "total": 150, "count": 1}
        assert result[1] == {"dept": "IT", "total": 300, "count": 2}

    def test_group_by_multiple_fields(self) -> None:
        """Test grouping by multiple fields."""
        records: List[Record] = [
            {"dept": "IT", "role": "dev", "salary": 100},
            {"dept": "IT", "role": "dev", "salary": 200},
            {"dept": "IT", "role": "mgr", "salary": 300},
        ]
        result = group_and_aggregate(records, ["dept", "role"], {"count": Count()})
        result = sorted(result, key=lambda x: (x["dept"], x["role"]))
        assert len(result) == 2
        assert result[0] == {"dept": "IT", "role": "dev", "count": 2}
        assert result[1] == {"dept": "IT", "role": "mgr", "count": 1}


class TestTableAggregate:
    """Tests for Table.aggregate() method."""

    @pytest.fixture
    def employees(self) -> Table:
        """Create a table with employee data."""
        t = Table("employees", primary_key="id")
        t.insert({"id": 1, "name": "Alice", "dept": "IT", "salary": 70000, "age": 30})
        t.insert({"id": 2, "name": "Bob", "dept": "IT", "salary": 80000, "age": 35})
        t.insert({"id": 3, "name": "Carol", "dept": "HR", "salary": 60000, "age": 28})
        t.insert({"id": 4, "name": "Dave", "dept": "HR", "salary": 65000, "age": 32})
        t.insert({"id": 5, "name": "Eve", "dept": "IT", "salary": 90000, "age": 40})
        return t

    def test_aggregate_count_all(self, employees: Table) -> None:
        """Test Count() on entire table."""
        result = employees.aggregate(count=Count())
        assert result == {"count": 5}

    def test_aggregate_sum(self, employees: Table) -> None:
        """Test Sum aggregation."""
        result = employees.aggregate(total=Sum("salary"))
        assert result == {"total": 365000}

    def test_aggregate_avg(self, employees: Table) -> None:
        """Test Avg aggregation."""
        result = employees.aggregate(avg_salary=Avg("salary"))
        assert result == {"avg_salary": 73000.0}

    def test_aggregate_min_max(self, employees: Table) -> None:
        """Test Min and Max aggregations."""
        result = employees.aggregate(min_age=Min("age"), max_age=Max("age"))
        assert result == {"min_age": 28, "max_age": 40}

    def test_aggregate_with_where(self, employees: Table) -> None:
        """Test aggregation with WHERE clause."""
        result = employees.aggregate(
            where=Condition(employees.dept == "IT"),
            count=Count(),
            avg_salary=Avg("salary"),
        )
        assert result == {"count": 3, "avg_salary": 80000.0}

    def test_aggregate_group_by_single(self, employees: Table) -> None:
        """Test GROUP BY single field."""
        result = employees.aggregate(
            group_by="dept",
            count=Count(),
            avg_salary=Avg("salary"),
        )
        assert isinstance(result, list)
        result = sorted(result, key=lambda x: x["dept"])
        assert len(result) == 2
        assert result[0] == {"dept": "HR", "count": 2, "avg_salary": 62500.0}
        assert result[1] == {"dept": "IT", "count": 3, "avg_salary": 80000.0}

    def test_aggregate_group_by_with_where(self, employees: Table) -> None:
        """Test GROUP BY with WHERE clause."""
        result = employees.aggregate(
            where=Condition(employees.age >= 30),
            group_by="dept",
            count=Count(),
        )
        assert isinstance(result, list)
        result = sorted(result, key=lambda x: x["dept"])
        assert len(result) == 2
        assert result[0] == {"dept": "HR", "count": 1}  # Dave (32)
        assert result[1] == {"dept": "IT", "count": 3}  # Alice, Bob, Eve

    def test_aggregate_empty_result(self) -> None:
        """Test aggregation on empty table."""
        t = Table("empty")
        result = t.aggregate(count=Count(), total=Sum("value"))
        assert isinstance(result, dict)
        assert result == {"count": 0, "total": None}

    def test_aggregate_multiple_group_by(self, employees: Table) -> None:
        """Test GROUP BY multiple fields."""
        employees.insert(
            {"id": 6, "name": "Frank", "dept": "IT", "salary": 75000, "age": 30}
        )
        result = employees.aggregate(
            group_by=["dept", "age"],
            count=Count(),
        )
        assert isinstance(result, list)
        it_30 = [r for r in result if r["dept"] == "IT" and r["age"] == 30]
        assert len(it_30) == 1
        assert it_30[0]["count"] == 2

    def test_aggregate_invalid_type_raises(self, employees: Table) -> None:
        """Test that passing non-Agg raises TypeError."""
        with pytest.raises(TypeError, match="Expected Agg instance"):
            employees.aggregate(count="COUNT(*)")
