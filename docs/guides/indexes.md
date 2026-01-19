# Indexes

Indexes accelerate queries by avoiding full table scans. DictDB supports two index types.

## Index Types

### Hash Index

Hash indexes provide O(1) lookups for equality conditions:

```python
employees.create_index("department", index_type="hash")

# This query uses the index - O(1) instead of O(n)
employees.select(where=Condition(employees.department == "IT"))
```

Best for:

- Equality comparisons (`==`)
- `is_in()` conditions
- High-cardinality fields (many unique values)

### Sorted Index

Sorted indexes support both equality and range queries:

```python
employees.create_index("salary", index_type="sorted")

# Equality - uses index
employees.select(where=Condition(employees.salary == 75000))

# Range queries - uses index
employees.select(where=Condition(employees.salary > 70000))
employees.select(where=Condition(employees.salary <= 80000))
employees.select(where=Condition(employees.salary >= 60000))
```

Best for:

- Range queries (`<`, `<=`, `>`, `>=`)
- Ordered data access
- Fields used in `order_by`

## Creating Indexes

```python
# Hash index (default)
employees.create_index("department")
employees.create_index("department", index_type="hash")

# Sorted index
employees.create_index("salary", index_type="sorted")
```

Indexes are automatically updated when records are inserted, updated, or deleted.

## Checking Indexes

```python
# List indexed fields
employees.indexed_fields()  # ["department", "salary"]

# Check if a field is indexed
employees.has_index("department")  # True
employees.has_index("name")  # False
```

## Index Usage

DictDB automatically uses indexes when possible:

```python
# Uses index (equality on indexed field)
employees.select(where=Condition(employees.department == "IT"))

# Uses index (range on sorted index)
employees.select(where=Condition(employees.salary > 70000))

# Uses index (is_in on indexed field)
employees.select(where=Condition(employees.department.is_in(["IT", "HR"])))

# Full table scan (no index on "name")
employees.select(where=Condition(employees.name == "Alice"))
```

### Compound Conditions

For AND conditions, the index is used to narrow down candidates:

```python
employees.create_index("department")

# Uses department index, then filters by salary
employees.select(
    where=Condition((employees.department == "IT") & (employees.salary > 70000))
)
```

## Performance Considerations

### When to Use Indexes

- Fields frequently used in `where` conditions
- Fields with high selectivity (few matches per value)
- Range query fields (use sorted index)

### When to Avoid Indexes

- Tables with few records (< 100)
- Rarely queried fields
- Fields updated very frequently

### Memory Overhead

Indexes consume additional memory:

- Hash index: ~O(n) for n records
- Sorted index: ~O(n) with tree structure overhead

## Persistence

!!! warning "Indexes Are Not Persisted"
    Indexes are not saved when using `db.save()`. After loading a database, recreate indexes if needed:

```python
# Save
db.save("data.json", file_format="json")

# Load
db = DictDB.load("data.json", file_format="json")

# Recreate indexes
employees = db.get_table("employees")
employees.create_index("department")
employees.create_index("salary", index_type="sorted")
```

## Example

```python
from dictdb import DictDB, Condition

db = DictDB()
db.create_table("orders", primary_key="order_id")
orders = db.get_table("orders")

# Create indexes
orders.create_index("customer_id")  # Hash for equality lookups
orders.create_index("total", index_type="sorted")  # Sorted for range queries
orders.create_index("status")  # Hash for status filtering

# Insert data
for i in range(10000):
    orders.insert({
        "customer_id": i % 100,
        "total": 10 + (i * 0.5),
        "status": "completed" if i % 3 == 0 else "pending"
    })

# Fast queries using indexes
customer_orders = orders.select(where=Condition(orders.customer_id == 42))
large_orders = orders.select(where=Condition(orders.total > 1000))
pending = orders.select(where=Condition(orders.status == "pending"))
```
