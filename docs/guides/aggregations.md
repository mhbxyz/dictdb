# Aggregations

DictDB provides SQL-like aggregation functions for computing statistics on your data.

## Aggregation Classes

Import the aggregation classes directly from dictdb:

```python
from dictdb import Count, Sum, Avg, Min, Max
```

| Class   | Description                          | Requires Field |
|---------|--------------------------------------|----------------|
| `Count` | Count records or non-None values     | Optional       |
| `Sum`   | Sum of numeric values                | Yes            |
| `Avg`   | Average of numeric values            | Yes            |
| `Min`   | Minimum value                        | Yes            |
| `Max`   | Maximum value                        | Yes            |

## Basic Usage

Use `table.aggregate()` to compute aggregations:

```python
from dictdb import DictDB, Count, Sum, Avg, Min, Max

db = DictDB()
db.create_table("employees")
employees = db.get_table("employees")

# Insert sample data
employees.insert({"id": 1, "name": "Alice", "department": "IT", "salary": 75000})
employees.insert({"id": 2, "name": "Bob", "department": "HR", "salary": 65000})
employees.insert({"id": 3, "name": "Charlie", "department": "IT", "salary": 85000})
employees.insert({"id": 4, "name": "Diana", "department": "IT", "salary": 70000})

# Count all employees
result = employees.aggregate(count=Count())
# {"count": 4}
```

## Count

`Count()` can be used in two ways:

```python
# Count all records
employees.aggregate(total=Count())
# {"total": 4}

# Count non-None values in a specific field
employees.aggregate(with_salary=Count("salary"))
# {"with_salary": 4}
```

!!! tip "Count Without Field vs With Field"
    - `Count()` counts all records, including those with None values
    - `Count("field")` counts only records where the field is not None

## Sum

`Sum("field")` calculates the sum of numeric values:

```python
employees.aggregate(total_salary=Sum("salary"))
# {"total_salary": 295000}
```

Returns `None` if no records match or all values are None.

## Avg

`Avg("field")` calculates the average of numeric values:

```python
employees.aggregate(avg_salary=Avg("salary"))
# {"avg_salary": 73750.0}
```

Returns `None` if no records match or all values are None.

## Min and Max

`Min("field")` and `Max("field")` find extreme values:

```python
employees.aggregate(
    lowest=Min("salary"),
    highest=Max("salary")
)
# {"lowest": 65000, "highest": 85000}
```

These work with any comparable type (numbers, strings, dates, etc.):

```python
employees.aggregate(
    first_name=Min("name"),
    last_name=Max("name")
)
# {"first_name": "Alice", "last_name": "Diana"}
```

## Multiple Aggregations

Compute multiple aggregations in a single call:

```python
result = employees.aggregate(
    count=Count(),
    total=Sum("salary"),
    average=Avg("salary"),
    minimum=Min("salary"),
    maximum=Max("salary")
)
# {
#     "count": 4,
#     "total": 295000,
#     "average": 73750.0,
#     "minimum": 65000,
#     "maximum": 85000
# }
```

## Filtering with WHERE

Use the `where` parameter to filter records before aggregating:

```python
from dictdb import Condition

# Count IT employees
result = employees.aggregate(
    where=Condition(employees.department == "IT"),
    count=Count()
)
# {"count": 3}

# Average salary in IT department
result = employees.aggregate(
    where=Condition(employees.department == "IT"),
    avg_salary=Avg("salary")
)
# {"avg_salary": 76666.67}
```

## GROUP BY

Use `group_by` to compute aggregations for each unique value of a field:

```python
# Count employees by department
results = employees.aggregate(
    group_by="department",
    count=Count()
)
# [
#     {"department": "IT", "count": 3},
#     {"department": "HR", "count": 1}
# ]
```

!!! note "Return Type Changes with GROUP BY"
    - Without `group_by`: Returns a single dictionary
    - With `group_by`: Returns a list of dictionaries (one per group)

### Multiple Aggregations per Group

```python
results = employees.aggregate(
    group_by="department",
    count=Count(),
    total_salary=Sum("salary"),
    avg_salary=Avg("salary"),
    max_salary=Max("salary")
)
# [
#     {"department": "IT", "count": 3, "total_salary": 230000, "avg_salary": 76666.67, "max_salary": 85000},
#     {"department": "HR", "count": 1, "total_salary": 65000, "avg_salary": 65000.0, "max_salary": 65000}
# ]
```

### Multiple GROUP BY Fields

Group by multiple fields using a list:

```python
db.create_table("sales")
sales = db.get_table("sales")

sales.insert({"region": "East", "product": "A", "amount": 100})
sales.insert({"region": "East", "product": "A", "amount": 150})
sales.insert({"region": "East", "product": "B", "amount": 200})
sales.insert({"region": "West", "product": "A", "amount": 120})

results = sales.aggregate(
    group_by=["region", "product"],
    count=Count(),
    total=Sum("amount")
)
# [
#     {"region": "East", "product": "A", "count": 2, "total": 250},
#     {"region": "East", "product": "B", "count": 1, "total": 200},
#     {"region": "West", "product": "A", "count": 1, "total": 120}
# ]
```

### Combining GROUP BY with WHERE

Filter records before grouping:

```python
results = employees.aggregate(
    where=Condition(employees.salary >= 70000),
    group_by="department",
    count=Count(),
    avg_salary=Avg("salary")
)
# [
#     {"department": "IT", "count": 3, "avg_salary": 76666.67}
# ]
# HR employee (salary 65000) was excluded by the WHERE clause
```

## Complete Example

```python
from dictdb import DictDB, Condition, Count, Sum, Avg, Min, Max

db = DictDB()
db.create_table("orders", primary_key="order_id")
orders = db.get_table("orders")

# Insert sample orders
orders.insert({"order_id": 1, "customer": "Alice", "product": "Widget", "quantity": 5, "price": 10.00})
orders.insert({"order_id": 2, "customer": "Bob", "product": "Gadget", "quantity": 2, "price": 25.00})
orders.insert({"order_id": 3, "customer": "Alice", "product": "Gadget", "quantity": 1, "price": 25.00})
orders.insert({"order_id": 4, "customer": "Charlie", "product": "Widget", "quantity": 10, "price": 10.00})
orders.insert({"order_id": 5, "customer": "Alice", "product": "Widget", "quantity": 3, "price": 10.00})

# Overall statistics
stats = orders.aggregate(
    total_orders=Count(),
    total_quantity=Sum("quantity"),
    avg_price=Avg("price")
)
# {"total_orders": 5, "total_quantity": 21, "avg_price": 16.0}

# Orders per customer
by_customer = orders.aggregate(
    group_by="customer",
    order_count=Count(),
    total_quantity=Sum("quantity")
)
# [
#     {"customer": "Alice", "order_count": 3, "total_quantity": 9},
#     {"customer": "Bob", "order_count": 1, "total_quantity": 2},
#     {"customer": "Charlie", "order_count": 1, "total_quantity": 10}
# ]

# Revenue by product (Widget orders only)
widget_stats = orders.aggregate(
    where=Condition(orders.product == "Widget"),
    group_by="customer",
    order_count=Count(),
    total_qty=Sum("quantity")
)
# [
#     {"customer": "Alice", "order_count": 2, "total_qty": 8},
#     {"customer": "Charlie", "order_count": 1, "total_qty": 10}
# ]
```

## Handling None Values

Aggregations handle None values consistently:

- `Count()` without field: Counts all records (including those with None)
- `Count("field")`: Counts only non-None values
- `Sum`, `Avg`, `Min`, `Max`: Ignore None values in calculations
- If all values are None: `Sum`, `Avg`, `Min`, `Max` return `None`

```python
db.create_table("data")
data = db.get_table("data")
data.insert({"id": 1, "value": 10})
data.insert({"id": 2, "value": None})
data.insert({"id": 3, "value": 20})

result = data.aggregate(
    total_records=Count(),
    non_null_values=Count("value"),
    sum_values=Sum("value"),
    avg_values=Avg("value")
)
# {
#     "total_records": 3,
#     "non_null_values": 2,
#     "sum_values": 30,
#     "avg_values": 15.0
# }
```
