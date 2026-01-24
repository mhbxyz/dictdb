# DictDB

<p align="center">
  <img src="assets/dictdb-logo.png" alt="DictDB Logo" width="600"/>
</p>

**DictDB** is an in-memory, dictionary-based database for Python with SQL-like CRUD operations, optional schemas, fast lookups via indexes, and a fluent query DSL.

Perfect for prototyping, testing, and lightweight relational workflows without a full database engine.

## Features

- **SQL-like CRUD** - `insert`, `select`, `update`, `delete`, `upsert` with familiar semantics
- **Fluent Query DSL** - Build conditions with Python operators: `table.age >= 18`, `table.name.like("A%")`
- **Logical Operators** - Readable `And`, `Or`, `Not` functions for complex queries
- **Aggregations** - `Count`, `Sum`, `Avg`, `Min`, `Max` with `GROUP BY` support
- **Indexes** - Hash indexes for O(1) equality lookups, sorted indexes for range queries
- **Optional Schemas** - Type validation when you need it, flexibility when you don't
- **CSV Import/Export** - Load data from CSV files and export query results
- **Persistence** - Save/load to JSON or Pickle
- **Automatic Backups** - Periodic and incremental backup support
- **Thread-Safe** - Reader-writer locks for concurrent access
- **Async Support** - Non-blocking save/load operations
- **Zero Config** - No server, no setup, just Python

## Quick Example

```python
from dictdb import DictDB, And

# Create database and table
db = DictDB()
db.create_table("users", primary_key="id")
users = db.get_table("users")

# Insert records
users.insert({"name": "Alice", "age": 30, "role": "admin"})
users.insert({"name": "Bob", "age": 25, "role": "user"})

# Query with fluent DSL (Condition wrapper is optional)
admins = users.select(where=users.role == "admin")
adults = users.select(where=users.age >= 18)

# Combine conditions with And/Or/Not
senior_admins = users.select(where=And(users.role == "admin", users.age >= 30))

# Update and delete
users.update({"age": 31}, where=users.name == "Alice")
users.delete(where=users.name == "Bob")

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
