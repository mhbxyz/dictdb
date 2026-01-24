<p align="center">
  <img src="https://raw.githubusercontent.com/mhbxyz/dictdb/main/docs/assets/dictdb-logo.png" alt="DictDB Logo" width="800"/>
</p>

<p align="center">
  <a href="https://github.com/mhbxyz/dictdb/actions/workflows/ci.yml"><img src="https://github.com/mhbxyz/dictdb/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/mhbxyz/dictdb.svg" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.13+-blue.svg" alt="Python 3.13+"></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-Ruff-46a2f1.svg" alt="Code style: Ruff"></a>
  <a href="https://mypy-lang.org/"><img src="https://img.shields.io/badge/type%20checking-mypy-2A6DB2.svg" alt="Type checking: MyPy"></a>
</p>

---

**DictDB** is a pure Python in-memory database with SQL-like queries.

## Installation

```bash
pip install dctdb
```

> The PyPI package is `dctdb`, but the import is `dictdb`.

## Features

- **SQL-like CRUD** — `insert`, `select`, `update`, `delete`, `upsert`
- **Query DSL** — `table.age >= 18`, `table.name.like("A%")`, `table.salary.between(50000, 100000)`
- **Logical operators** — `And`, `Or`, `Not` for readable complex queries
- **Aggregations** — `Count`, `Sum`, `Avg`, `Min`, `Max` with `GROUP BY`
- **Indexes** — Hash (O(1) lookup) and Sorted (range queries)
- **Schemas** — Optional type validation
- **CSV import/export** — Load from and save to CSV files
- **Persistence** — JSON and Pickle formats with async support
- **Automatic backups** — Periodic and incremental backup manager
- **Thread-safe** — Reader-writer locks per table

## Quick Example

```python
from dictdb import DictDB, And, Count, Avg

db = DictDB()
db.create_table("users", primary_key="id")
users = db.get_table("users")

# Insert
users.insert({"name": "Alice", "age": 30, "dept": "IT"})
users.insert({"name": "Bob", "age": 25, "dept": "HR"})

# Query with DSL (Condition wrapper is optional)
users.select(where=users.age >= 25)
users.select(where=users.dept == "IT", order_by="-age", limit=10)

# Combine conditions with And/Or/Not
users.select(where=And(users.dept == "IT", users.age >= 25))

# Aggregations
users.aggregate(count=Count(), avg_age=Avg("age"))
users.aggregate(group_by="dept", count=Count())

# Persistence
db.save("data.json", file_format="json")
```

## CSV Import/Export

```python
# Import CSV into a new table
db.import_csv("users.csv", "users", primary_key="id")

# Export table to CSV
users.export_csv("backup.csv")
users.export_csv("it_dept.csv", where=users.dept == "IT")
```

## Documentation

**[mhbxyz.github.io/dictdb](https://mhbxyz.github.io/dictdb)**

## License

Apache 2.0
