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

### Basic CRUD

```python
from dictdb import DictDB, Condition

# Create database and table
db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

# Insert records (auto-assigns emp_id if missing)
employees.insert({"emp_id": 101, "name": "Alice", "department": "IT", "salary": 75000})
employees.insert({"name": "Bob", "department": "HR", "salary": 65000})
employees.insert({"name": "Charlie", "department": "IT", "salary": 85000})
employees.insert({"name": "Diana", "department": "Sales", "salary": 70000})

# Select all
all_employees = employees.select()

# Update records
employees.update({"salary": 68000}, where=Condition(employees.name == "Bob"))

# Delete records
employees.delete(where=Condition(employees.name == "Diana"))
```

### Query DSL

```python
# Comparison operators: ==, !=, <, <=, >, >=
seniors = employees.select(where=Condition(employees.salary >= 80000))

# Logical AND
it_seniors = employees.select(
    where=Condition((employees.department == "IT") & (employees.salary >= 80000))
)

# Logical OR
it_or_hr = employees.select(
    where=Condition((employees.department == "IT") | (employees.department == "HR"))
)

# IN operator
tech_teams = employees.select(
    where=Condition(employees.department.is_in(["IT", "Engineering", "Data"]))
)

# String matching
employees.select(where=Condition(employees.name.startswith("A")))
employees.select(where=Condition(employees.name.contains("li")))
```

### Sorting & Pagination

```python
# Order by salary descending
top_earners = employees.select(order_by="-salary")

# Multi-field sort: department asc, then salary desc
sorted_employees = employees.select(order_by=["department", "-salary"])

# Pagination
page_size = 10
page = 2
paginated = employees.select(
    order_by="name",
    limit=page_size,
    offset=(page - 1) * page_size
)
```

### Column Projection

```python
# Select specific columns
names = employees.select(columns=["name", "department"])
# [{"name": "Alice", "department": "IT"}, ...]

# Column aliasing
aliased = employees.select(columns={"employee": "name", "team": "department"})
# [{"employee": "Alice", "team": "IT"}, ...]
```

### Schema Validation

```python
# Define schema for type enforcement
schema = {"emp_id": int, "name": str, "department": str, "salary": int}
db.create_table("staff", primary_key="emp_id", schema=schema)
staff = db.get_table("staff")

staff.insert({"emp_id": 1, "name": "Alice", "department": "IT", "salary": 75000})  # OK
staff.insert({"emp_id": 2, "name": "Bob", "department": "HR", "salary": "high"})   # Raises SchemaValidationError
```

### Indexes

```python
# Hash index for O(1) equality lookups
employees.create_index("department", index_type="hash")
employees.select(where=Condition(employees.department == "IT"))  # Fast

# Sorted index for range queries
employees.create_index("salary", index_type="sorted")
employees.select(where=Condition(employees.salary > 70000))      # Fast
employees.select(where=Condition(employees.salary <= 80000))     # Fast

# Check indexes
employees.indexed_fields()      # ["department", "salary"]
employees.has_index("salary")   # True
```

### Persistence

```python
# Save to JSON (human-readable)
db.save("employees.json", file_format="json")

# Save to Pickle (faster, binary)
db.save("employees.pkl", file_format="pickle")

# Load from disk
db2 = DictDB.load("employees.json", file_format="json")

# Async I/O for non-blocking operations
import asyncio
asyncio.run(db.async_save("employees.json", file_format="json"))
```

### Introspection

```python
# Table metadata
employees.columns()          # ["emp_id", "name", "department", "salary"]
employees.count()            # 3
employees.primary_key_name() # "emp_id"

# Database metadata
db.list_tables()             # ["employees", "staff"]
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
