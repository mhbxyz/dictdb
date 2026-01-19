# DictDB

<p align="center">
  <img src="assets/dictdb-logo.png" alt="DictDB Logo" width="600"/>
</p>

**DictDB** is an in-memory, dictionary-based database for Python with SQL-like CRUD operations, optional schemas, fast lookups via indexes, and a fluent query DSL.

Perfect for prototyping, testing, and lightweight relational workflows without a full database engine.

## Features

- **SQL-like CRUD** - `insert`, `select`, `update`, `delete` with familiar semantics
- **Fluent Query DSL** - Build conditions with Python operators: `table.age >= 18`
- **Indexes** - Hash indexes for O(1) equality lookups, sorted indexes for range queries
- **Optional Schemas** - Type validation when you need it, flexibility when you don't
- **Persistence** - Save/load to JSON or Pickle
- **Automatic Backups** - Periodic and incremental backup support
- **Thread-Safe** - Reader-writer locks for concurrent access
- **Async Support** - Non-blocking save/load operations
- **Zero Dependencies** - Only `sortedcontainers` for sorted indexes
- **Zero Config** - No server, no setup, just Python

## Quick Example

```python
from dictdb import DictDB, Condition

# Create database and table
db = DictDB()
db.create_table("users", primary_key="id")
users = db.get_table("users")

# Insert records
users.insert({"name": "Alice", "age": 30, "role": "admin"})
users.insert({"name": "Bob", "age": 25, "role": "user"})

# Query with fluent DSL
admins = users.select(where=Condition(users.role == "admin"))
adults = users.select(where=Condition(users.age >= 18))

# Update and delete
users.update({"age": 31}, where=Condition(users.name == "Alice"))
users.delete(where=Condition(users.name == "Bob"))

# Persist to disk
db.save("data.json", file_format="json")
```

## Installation

```bash
pip install dctdb
```

```python
from dictdb import DictDB, Condition
```

!!! note "Package name"
    The PyPI package is `dctdb`, but the import name is `dictdb`.

## Requirements

- Python 3.13+

## License

Apache License 2.0 - see [LICENSE](https://github.com/mhbxyz/dictdb/blob/main/LICENSE) for details.
