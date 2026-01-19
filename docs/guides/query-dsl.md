# Query DSL

DictDB provides a fluent query DSL that lets you build conditions using Python operators.

## Basic Conditions

Access table fields as attributes to create conditions:

```python
from dictdb import DictDB, Condition

db = DictDB()
db.create_table("employees")
employees = db.get_table("employees")

# employees.name returns a Field object
# Field == "Alice" returns a PredicateExpr
# Condition wraps the PredicateExpr for use in queries
employees.select(where=Condition(employees.name == "Alice"))
```

## Comparison Operators

All standard comparison operators are supported:

```python
# Equality
Condition(employees.department == "IT")

# Inequality
Condition(employees.department != "HR")

# Less than / Less than or equal
Condition(employees.age < 30)
Condition(employees.age <= 30)

# Greater than / Greater than or equal
Condition(employees.salary > 50000)
Condition(employees.salary >= 50000)
```

## Logical Operators

Combine conditions with `&` (AND), `|` (OR), and `~` (NOT):

```python
# AND: both conditions must be true
Condition((employees.department == "IT") & (employees.salary >= 80000))

# OR: either condition must be true
Condition((employees.department == "IT") | (employees.department == "HR"))

# NOT: invert a condition
Condition(~(employees.department == "Sales"))

# Complex combinations
Condition(
    ((employees.department == "IT") | (employees.department == "Engineering"))
    & (employees.salary >= 70000)
    & ~(employees.status == "inactive")
)
```

!!! warning "Use Parentheses"
    Always wrap individual conditions in parentheses when combining them. Python's operator precedence may not work as expected otherwise.

## IN Operator

Check if a field value is in a list:

```python
# Match any of the values
Condition(employees.department.is_in(["IT", "Engineering", "Data"]))

# Equivalent to multiple OR conditions but more efficient
```

## String Matching

Match string patterns:

```python
# Starts with
Condition(employees.name.startswith("A"))

# Ends with
Condition(employees.email.endswith("@company.com"))

# Contains
Condition(employees.name.contains("Smith"))
```

## Sorting

Sort results with `order_by`:

```python
# Ascending order (default)
employees.select(order_by="name")

# Descending order (prefix with -)
employees.select(order_by="-salary")

# Multiple fields
employees.select(order_by=["department", "-salary"])
# Sort by department ascending, then by salary descending within each department
```

## Pagination

Limit and offset results:

```python
# First 10 records
employees.select(limit=10)

# Skip first 20, get next 10 (page 3 with page size 10)
employees.select(limit=10, offset=20)

# Combine with sorting for consistent pagination
employees.select(order_by="id", limit=10, offset=20)
```

!!! tip "Always Sort When Paginating"
    Without `order_by`, the order of results is not guaranteed. Always specify a sort order when using pagination.

## Column Projection

Select specific columns:

```python
# List of column names
employees.select(columns=["name", "department"])
# Returns: [{"name": "Alice", "department": "IT"}, ...]

# Dictionary for aliasing
employees.select(columns={"employee": "name", "team": "department"})
# Returns: [{"employee": "Alice", "team": "IT"}, ...]

# List of tuples
employees.select(columns=[("employee", "name"), ("team", "department")])
# Same as above
```

## Record Copying

By default, `select` returns copies of records for thread safety:

```python
# Default: returns copies (safe to modify)
results = employees.select()
results[0]["name"] = "Modified"  # Does not affect original

# For read-only access, skip copying for better performance
results = employees.select(copy=False)
# Do not modify these records!
```

## Complete Example

```python
from dictdb import DictDB, Condition

db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

# Insert sample data
employees.insert({"emp_id": 1, "name": "Alice", "department": "IT", "salary": 75000})
employees.insert({"emp_id": 2, "name": "Bob", "department": "HR", "salary": 65000})
employees.insert({"emp_id": 3, "name": "Charlie", "department": "IT", "salary": 85000})
employees.insert({"emp_id": 4, "name": "Diana", "department": "Sales", "salary": 70000})

# Find IT employees earning >= 80000
high_earners = employees.select(
    columns=["name", "salary"],
    where=Condition((employees.department == "IT") & (employees.salary >= 80000)),
    order_by="-salary"
)
# [{"name": "Charlie", "salary": 85000}]

# Paginated list of all employees
page_1 = employees.select(order_by="name", limit=2, offset=0)
page_2 = employees.select(order_by="name", limit=2, offset=2)
```
