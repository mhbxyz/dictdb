<p align="center">
  <img src="https://raw.githubusercontent.com/mhbxyz/dictdb/main/docs/DictDBLogo.png" alt="DictDB Logo" width="800"/>
</p>

<p align="center">
  <a href="https://github.com/mhbxyz/dictdb/actions/workflows/ci.yml"><img src="https://github.com/mhbxyz/dictdb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/mhbxyz/dictdb.svg" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.13+-blue.svg" alt="Python 3.13+"></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-Ruff-46a2f1.svg" alt="Code style: Ruff"></a>
  <a href="https://mypy-lang.org/"><img src="https://img.shields.io/badge/type%20checking-mypy-2A6DB2.svg" alt="Type checking: MyPy"></a>
</p>

---

**DictDB** is an in-memory, dictionary-based database for Python with SQL-like CRUD operations, optional schemas, fast lookups via indexes, and a fluent query DSL.

Perfect for prototyping, testing, and lightweight relational workflows without a full database engine.

## Features

- **SQL-like CRUD** — `INSERT`, `SELECT`, `UPDATE`, `DELETE` with familiar semantics
- **Fluent Query DSL** — Build conditions with Python operators: `table.age >= 18`
- **Indexes** — Hash indexes for O(1) equality lookups, sorted indexes for range queries
- **Optional Schemas** — Type validation when you need it, flexibility when you don't
- **Persistence** — Save/load to JSON or Pickle
- **Thread-Safe** — Reader-writer locks for concurrent access
- **Zero Config** — No server, no setup, just Python

## Installation

```bash
# Development setup
make setup

# Or install dependencies manually
uv sync
```

## Quickstart

```python
from dictdb import DictDB, Condition

# Create database and table
db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

# Insert records (auto-assigns emp_id if missing)
employees.insert({"emp_id": 101, "name": "Alice", "department": "IT", "age": 30})
employees.insert({"name": "Bob", "department": "HR", "age": 26})
employees.insert({"name": "Charlie", "department": "IT", "age": 35})

# Add index for faster lookups
employees.create_index("department", index_type="hash")

# Query with conditions
it_team = employees.select(
    columns=["name"],
    where=Condition(employees.department == "IT")
)
# [{'name': 'Alice'}, {'name': 'Charlie'}]

# Update records
employees.update(
    {"department": "IT"},
    where=Condition(employees.name == "Bob")
)

# Delete with range condition
employees.delete(where=Condition(employees.age < 28))

# Persist to disk
db.save("employees.json", file_format="json")

# Load from disk
db2 = DictDB.load("employees.json", file_format="json")
```

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](docs/getting-started/README.md) | Installation and first steps |
| [Guides](docs/guides/README.md) | In-depth tutorials |
| [Reference](docs/reference/README.md) | API documentation |
| [Contributing](docs/contributing/README.md) | How to contribute |
| [Roadmap](docs/roadmap.md) | Future plans |

## Development

```bash
# Setup environment
make setup
make hooks-install

# Run all checks (format, lint, types, tests)
make check

# Run tests with coverage
make coverage

# Run benchmarks
make benchmark
```

## License

MIT License — see [LICENSE](LICENSE) for details.
