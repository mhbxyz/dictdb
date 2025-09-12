<p align="center">
  <img src="https://raw.githubusercontent.com/mhbxyz/dictdb/main/docs/DictDBLogo.png" alt="DictDB Logo" width="800"/>
</p>

![CI](https://github.com/mhbxyz/dictdb/actions/workflows/ci.yml/badge.svg)
[![Release](https://github.com/mhbxyz/dictdb/actions/workflows/release.yml/badge.svg)](https://github.com/mhbxyz/dictdb/actions/workflows/release.yml)
[![PyPI version](https://img.shields.io/pypi/v/dictdb.svg)](https://pypi.org/project/dictdb/)

DictDB is an in‑memory, dictionary-based database for Python with SQL‑like CRUD, optional schemas, fast equality lookups via indexes, and a fluent query DSL. Great for prototyping, tests, and lightweight relational workflows without a full DB engine.

## Install

- Dev setup: `make setup`
- PyPI: `pip install dictdb` (once published)

## Quickstart

```python
from dictdb import DictDB, Condition, configure_logging

# Configure human-friendly console logs (see docs/logging.md for JSON logs)
configure_logging(level="INFO", console=True)

# 1) Create DB and a table
db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

# 2) Insert data (auto-assigns emp_id if missing)
employees.insert({"emp_id": 101, "name": "Alice", "department": "IT", "age": 30})
employees.insert({"name": "Bob", "department": "HR", "age": 26})
employees.insert({"name": "Charlie", "department": "IT", "age": 35})

# 3) Optional: add an index to accelerate equality lookups
employees.create_index("department", index_type="hash")

# 4) Query: IT employees, projecting only their names
it_people = employees.select(columns=["name"], where=Condition(employees.department == "IT"))
print("IT:", it_people)  # [{'name': 'Alice'}, {'name': 'Charlie'}]

# 5) Update: move Bob to IT
employees.update({"department": "IT"}, where=Condition(employees.name == "Bob"))

# 6) Delete: remove junior employees under 28
employees.delete(where=Condition(employees.age < 28))

# 7) Introspection helpers
print("Columns:", employees.columns())
print("Count:", employees.count(), "Indexed:", employees.indexed_fields())

# 8) Persist and load
db.save("employees.json", file_format="json")
db2 = DictDB.load("employees.json", file_format="json")
print("Loaded tables:", db2.list_tables())
```

## Docs

- [Overview](docs/overview.md)
- [Installation](docs/installation.md)
- [Quickstart & Basic Usage](docs/quickstart.md)
- [Conditions & Queries](docs/queries.md)
- [Schema Validation](docs/schema.md)
- [Logging](docs/logging.md)
- [Indexing](docs/indexing.md)
- [API Reference](docs/api.md)
- [Publishing](docs/publishing.md)
- [Development Guide](docs/development.md)
- [Roadmap](docs/roadmap.md)

## Development

- Setup: `make setup` then `make hooks-install`
- Validate: `make check` (format, lint, types, tests)
- Coverage: `make coverage`

Contributions and bug reports are welcome.
