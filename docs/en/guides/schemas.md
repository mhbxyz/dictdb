# Schemas

Schemas provide type validation for table records. When a schema is defined, all insert and update operations validate records against it.

## Defining a Schema

A schema is a dictionary mapping field names to Python types:

```python
schema = {
    "id": int,
    "name": str,
    "email": str,
    "age": int,
    "active": bool,
}

db.create_table("users", primary_key="id", schema=schema)
```

## Supported Types

Schemas support standard Python types:

- `str` - Strings
- `int` - Integers
- `float` - Floating point numbers
- `bool` - Booleans
- `list` - Lists (any content)
- `dict` - Dictionaries (any content)

## Validation Behavior

### Required Fields

All schema fields are required:

```python
schema = {"id": int, "name": str, "email": str}
db.create_table("users", schema=schema)
users = db.get_table("users")

# Missing field raises error
users.insert({"id": 1, "name": "Alice"})
# SchemaValidationError: Missing field 'email' as defined in schema.
```

### Type Checking

Field values must match the expected type:

```python
# Wrong type raises error
users.insert({"id": "one", "name": "Alice", "email": "alice@example.com"})
# SchemaValidationError: Field 'id' expects type 'int', got 'str'.
```

### Extra Fields

Fields not in the schema are rejected:

```python
users.insert({"id": 1, "name": "Alice", "email": "alice@example.com", "phone": "123"})
# SchemaValidationError: Field 'phone' is not defined in the schema.
```

## Primary Key in Schema

If the primary key is not in the schema, it's automatically added as `int`:

```python
schema = {"name": str, "email": str}
db.create_table("users", primary_key="id", schema=schema)

# "id" is automatically added to schema as int
# Auto-generated IDs work as expected
users.insert({"name": "Alice", "email": "alice@example.com"})  # id=1
```

## Update Validation

Updates also validate against the schema:

```python
# Invalid update raises error
users.update({"age": "thirty"}, where=Condition(users.name == "Alice"))
# SchemaValidationError: Field 'age' expects type 'int', got 'str'.
```

Updates are atomic - if validation fails, no records are modified.

## Schema Introspection

```python
# Get schema field names
users.schema_fields()  # ["id", "name", "email"]

# Access full schema
users.schema  # {"id": int, "name": str, "email": str}
```

## Tables Without Schemas

Without a schema, tables accept any record structure:

```python
db.create_table("flexible")
flexible = db.get_table("flexible")

# Any fields are allowed
flexible.insert({"x": 1})
flexible.insert({"a": "hello", "b": [1, 2, 3], "c": {"nested": True}})
```

## Persistence

Schemas are preserved when saving and loading:

```python
schema = {"id": int, "name": str, "score": float}
db.create_table("players", schema=schema)

# Save
db.save("game.json", file_format="json")

# Load - schema is restored
db = DictDB.load("game.json", file_format="json")
players = db.get_table("players")
players.schema  # {"id": int, "name": str, "score": float}
```

## Example

```python
from dictdb import DictDB, Condition, SchemaValidationError

db = DictDB()

# Define schema
product_schema = {
    "sku": str,
    "name": str,
    "price": float,
    "quantity": int,
    "active": bool,
}

db.create_table("products", primary_key="sku", schema=product_schema)
products = db.get_table("products")

# Valid insert
products.insert({
    "sku": "ABC123",
    "name": "Widget",
    "price": 19.99,
    "quantity": 100,
    "active": True,
})

# Validation errors
try:
    products.insert({
        "sku": "DEF456",
        "name": "Gadget",
        "price": "cheap",  # Should be float
        "quantity": 50,
        "active": True,
    })
except SchemaValidationError as e:
    print(e)  # Field 'price' expects type 'float', got 'str'.

# Update with validation
products.update(
    {"quantity": 150},
    where=Condition(products.sku == "ABC123")
)
```
