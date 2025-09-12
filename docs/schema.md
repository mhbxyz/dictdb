# Schema Validation

## Defining a Schema

```python
from dictdb import Table, SchemaValidationError

schema = {"id": int, "name": str, "age": int}
table = Table("users", primary_key="id", schema=schema)
table.insert({"id": 1, "name": "Alice", "age": 30})
```

## Schema Errors

```python
try:
    table.insert({"id": 2, "name": "Bob"}) # missing field
except SchemaValidationError as e:
    print(e)

try:
    table.insert({"id": 3, "name": "Charlie", "age": 28, "nickname": "Chaz"})
except SchemaValidationError as e:
    print(e)

try:
    table.insert({"id": 4, "name": "Diana", "age": "30"}) # wrong type
except SchemaValidationError as e:
    print(e)
```

