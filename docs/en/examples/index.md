# Practical Examples

Welcome to the examples section! Here you'll discover DictDB through concrete use cases, presented as progressive stories.

## Learning Path

Each example tells a story and introduces new features. Follow them in order for a gradual learning experience, or jump directly to the one that matches your needs.

### Beginner Level

| Example | Description | Features |
|---------|-------------|----------|
| [My First Contact Book](01-contact-book.md) | Discover DictDB by building a simple app | CRUD, JSON persistence |
| [The Neighborhood Library](02-library.md) | Manage multiple related tables | Multi-tables, Query DSL, sorting, pagination |

### Intermediate Level

| Example | Description | Features |
|---------|-------------|----------|
| [My Online Store](03-online-store.md) | Build a product catalog | Schemas, indexes, advanced search, upsert |
| [The Sales Manager's Dashboard](04-sales-dashboard.md) | Analyze your team's performance | Aggregations, GROUP BY, statistics |

### Advanced Level

| Example | Description | Features |
|---------|-------------|----------|
| [Legacy Data Migration](05-data-migration.md) | Migrate data from CSV files | CSV import/export, transformation |
| [Production Ready](06-production-ready.md) | Deploy to production | Backups, concurrency, async, logging |

## Features Covered

By the end of this learning path, you'll master:

- **Full CRUD**: insert, select, update, delete, upsert
- **Query DSL**: comparisons, LIKE, BETWEEN, is_in, is_null
- **Logical operators**: And, Or, Not
- **Search**: case-sensitive and case-insensitive
- **Indexes**: hash and sorted for performant queries
- **Schemas**: type validation
- **Aggregations**: Count, Sum, Avg, Min, Max with GROUP BY
- **CSV**: data import and export
- **Persistence**: JSON and Pickle
- **Production**: backups, concurrency, async, logging

## How to Use These Examples

Each example is designed to be:

1. **Self-contained**: you can copy-paste the code and run it
2. **Progressive**: concepts build on each other logically
3. **Practical**: based on real-world use cases

```python
# Quick install
pip install dctdb

# Then follow the examples!
from dictdb import DictDB
```

Ready to start? [My First Contact Book](01-contact-book.md) awaits!
