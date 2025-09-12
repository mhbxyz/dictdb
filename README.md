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
from dictdb import DictDB, Query, configure_logging

configure_logging(level="DEBUG", console=True)

db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

employees.insert({"emp_id": 101, "name": "Alice", "department": "IT"})
employees.insert({"name": "Charlie", "department": "IT"})

it_staff = employees.select(where=Query(employees.department == "IT"))
print(it_staff)
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
