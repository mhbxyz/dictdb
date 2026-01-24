# Persistence

DictDB supports saving and loading databases to disk in JSON or Pickle format.

## Saving

### JSON Format

Human-readable format, good for debugging and interoperability:

```python
db.save("database.json", file_format="json")
```

JSON output structure:

```json
{
  "tables": {
    "users": {
      "primary_key": "id",
      "schema": null,
      "records": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
      ]
    }
  }
}
```

### Pickle Format

Binary format, faster and supports all Python types:

```python
db.save("database.pkl", file_format="pickle")
```

!!! warning "Security"
    Pickle files can execute arbitrary code when loaded. Only load pickle files from trusted sources. DictDB uses a restricted unpickler that only allows whitelisted classes.

## Loading

```python
# Load from JSON
db = DictDB.load("database.json", file_format="json")

# Load from Pickle
db = DictDB.load("database.pkl", file_format="pickle")
```

## Async I/O

For non-blocking operations in async applications:

```python
import asyncio

async def save_and_load():
    # Async save
    await db.async_save("database.json", file_format="json")

    # Async load
    db = await DictDB.async_load("database.json", file_format="json")
```

These methods run I/O operations in a thread pool to avoid blocking the event loop.

## Format Comparison

| Feature | JSON | Pickle |
|---------|------|--------|
| Human readable | Yes | No |
| Speed | Slower | Faster |
| File size | Larger | Smaller |
| Python types | Limited | All |
| Security | Safe | Restricted |
| Interoperability | High | Python only |

## What Gets Persisted

**Saved:**

- All tables and their names
- Primary key configuration
- Schema definitions
- All records

**Not saved:**

- Indexes (recreate after loading)
- Runtime state (locks, dirty tracking)

## Recreating Indexes After Load

```python
# Save
employees.create_index("department")
db.save("data.json", file_format="json")

# Load
db = DictDB.load("data.json", file_format="json")
employees = db.get_table("employees")

# Indexes must be recreated
employees.create_index("department")
```

## Schema Persistence

Schemas are fully preserved:

```python
# Create with schema
schema = {"id": int, "name": str, "score": float}
db.create_table("players", schema=schema)

# Save and load
db.save("game.json", file_format="json")
db = DictDB.load("game.json", file_format="json")

# Schema is restored
players = db.get_table("players")
print(players.schema)  # {"id": int, "name": str, "score": float}
```

## Streaming Writes

For large databases, JSON saves use streaming to reduce memory usage:

```python
# Large database
for i in range(100000):
    users.insert({"name": f"User {i}"})

# Streaming write - doesn't load entire DB into memory
db.save("large.json", file_format="json")
```

## Error Handling

```python
from pathlib import Path

# File not found
try:
    db = DictDB.load("missing.json", file_format="json")
except FileNotFoundError:
    print("Database file not found")

# Invalid format
try:
    db.save("data.txt", file_format="xml")
except ValueError as e:
    print(e)  # Unsupported file_format. Please use 'json' or 'pickle'.
```

## Path Types

Both string and `Path` objects are accepted:

```python
from pathlib import Path

# String path
db.save("data.json", file_format="json")

# Path object
db.save(Path("data") / "database.json", file_format="json")
```

## Example

```python
from dictdb import DictDB, Condition

# Create and populate database
db = DictDB()
db.create_table("config", primary_key="key")
config = db.get_table("config")

config.insert({"key": "version", "value": "1.0.0"})
config.insert({"key": "debug", "value": True})
config.insert({"key": "max_connections", "value": 100})

# Save to JSON for human editing
db.save("config.json", file_format="json")

# Later: load and use
db = DictDB.load("config.json", file_format="json")
config = db.get_table("config")

version = config.select(where=Condition(config.key == "version"))[0]["value"]
print(f"Version: {version}")
```
