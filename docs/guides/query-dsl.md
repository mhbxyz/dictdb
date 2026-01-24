# Query DSL

DictDB provides a fluent query DSL that lets you build conditions using Python operators.

## Basic Conditions

Access table fields as attributes to create conditions:

```python
from dictdb import DictDB

db = DictDB()
db.create_table("employees")
employees = db.get_table("employees")

# employees.name returns a Field object
# Field == "Alice" returns a PredicateExpr
# Pass directly to where= parameter
employees.select(where=employees.name == "Alice")
```

!!! note "Condition Wrapper (Optional)"
    The `Condition()` wrapper is optional. Both syntaxes are supported:

    ```python
    # Recommended: direct syntax
    employees.select(where=employees.age >= 18)

    # Also works: explicit Condition wrapper
    from dictdb import Condition
    employees.select(where=Condition(employees.age >= 18))
    ```

## Comparison Operators

All standard comparison operators are supported:

```python
# Equality
employees.select(where=employees.department == "IT")

# Inequality
employees.select(where=employees.department != "HR")

# Less than / Less than or equal
employees.select(where=employees.age < 30)
employees.select(where=employees.age <= 30)

# Greater than / Greater than or equal
employees.select(where=employees.salary > 50000)
employees.select(where=employees.salary >= 50000)
```

## Logical Operators

Combine conditions with `&` (AND), `|` (OR), and `~` (NOT):

```python
# AND: both conditions must be true
employees.select(where=(employees.department == "IT") & (employees.salary >= 80000))

# OR: either condition must be true
employees.select(where=(employees.department == "IT") | (employees.department == "HR"))

# NOT: invert a condition
employees.select(where=~(employees.department == "Sales"))

# Complex combinations
employees.select(
    where=(
        ((employees.department == "IT") | (employees.department == "Engineering"))
        & (employees.salary >= 70000)
        & ~(employees.status == "inactive")
    )
)
```

!!! warning "Use Parentheses"
    Always wrap individual conditions in parentheses when combining them. Python's operator precedence may not work as expected otherwise.

## IN Operator

Check if a field value is in a list:

```python
# Match any of the values
employees.select(where=employees.department.is_in(["IT", "Engineering", "Data"]))

# Equivalent to multiple OR conditions but more efficient
```

## BETWEEN Operator

Check if a field value is within an inclusive range:

```python
# Match values in range [30, 50]
employees.select(where=employees.age.between(30, 50))

# Equivalent to (but more efficient than):
employees.select(where=(employees.age >= 30) & (employees.age <= 50))

# Works with any comparable types
employees.select(where=employees.hire_date.between("2020-01-01", "2023-12-31"))
employees.select(where=employees.salary.between(50000, 100000))
```

!!! tip "Index Optimization"
    When a sorted index exists on the field, `between()` uses an optimized single range scan instead of two separate index lookups.

## Null Checks

Check for null (None) or missing field values:

```python
# Match records where the field is None or missing
employees.select(where=employees.manager_id.is_null())

# Match records where the field exists and is not None
employees.select(where=employees.manager_id.is_not_null())
```

## String Matching

Match string patterns:

```python
# Starts with
employees.select(where=employees.name.startswith("A"))

# Ends with
employees.select(where=employees.email.endswith("@company.com"))

# Contains
employees.select(where=employees.name.contains("Smith"))
```

## LIKE Pattern Matching

SQL-style LIKE patterns with wildcards:

```python
# % matches any sequence of characters (including empty)
employees.select(where=employees.name.like("A%"))           # Starts with A
employees.select(where=employees.email.like("%@gmail.com")) # Ends with @gmail.com
employees.select(where=employees.name.like("%smith%"))      # Contains smith

# _ matches exactly one character
employees.select(where=employees.code.like("A_C"))          # Matches A1C, A2C, ABC, etc.
employees.select(where=employees.id.like("___"))            # Exactly 3 characters

# Combine wildcards
employees.select(where=employees.file.like("test_.%"))      # test1.txt, test2.doc, etc.
```

### Escape Characters

To match literal `%` or `_`, use an escape character:

```python
# Match strings ending with literal %
employees.select(where=products.discount.like("%\\%", escape="\\"))  # 10%, 20%, etc.

# Match strings containing literal _
employees.select(where=files.name.like("%\\_v1%", escape="\\"))  # file_v1.txt, etc.
```

!!! tip "Index Optimization"
    When a sorted index exists and the pattern starts with a literal prefix (e.g., `"ABC%"`), the query uses the index for faster lookups.

## Case-Insensitive Matching

All string matching methods have case-insensitive variants with an `i` prefix:

```python
# Case-insensitive equality
employees.select(where=employees.name.iequals("alice"))  # Matches "Alice", "ALICE", etc.

# Case-insensitive contains
employees.select(where=employees.name.icontains("smith"))  # Matches "Smith", "SMITH", etc.

# Case-insensitive prefix/suffix
employees.select(where=employees.name.istartswith("a"))  # Matches "Alice", "ADAM", etc.
employees.select(where=employees.email.iendswith("@gmail.com"))  # Matches "@Gmail.COM", etc.

# Case-insensitive LIKE
employees.select(where=employees.name.ilike("a%"))  # Matches "Alice", "adam", "ANNA", etc.
```

| Method | Case-Insensitive Variant |
|--------|-------------------------|
| `==` (equality) | `iequals()` |
| `contains()` | `icontains()` |
| `startswith()` | `istartswith()` |
| `endswith()` | `iendswith()` |
| `like()` | `ilike()` |

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

## Distinct Results

Remove duplicate records from results:

```python
# Get unique departments
employees.select(columns=["department"], distinct=True)
# Returns: [{"department": "IT"}, {"department": "HR"}, {"department": "Sales"}]

# Combine with other options
employees.select(
    columns=["department", "status"],
    where=employees.salary >= 50000,
    distinct=True,
    order_by="department"
)
```

!!! note "Distinct Behavior"
    When duplicates exist, `distinct=True` preserves the first occurrence and removes subsequent duplicates.

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
from dictdb import DictDB

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
    where=(employees.department == "IT") & (employees.salary >= 80000),
    order_by="-salary"
)
# [{"name": "Charlie", "salary": 85000}]

# Paginated list of all employees
page_1 = employees.select(order_by="name", limit=2, offset=0)
page_2 = employees.select(order_by="name", limit=2, offset=2)
```
