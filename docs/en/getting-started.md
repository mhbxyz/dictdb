# Getting Started

## Installation

```bash
pip install dctdb
```

```python
from dictdb import DictDB, Condition
```

!!! note "Package name"
    The PyPI package is `dctdb`, but the import name is `dictdb`.

### Development Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/mhbxyz/dictdb.git
cd dictdb
make setup
```

Or manually with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

### From Source

```bash
pip install -e .
```

## Basic Usage

### Creating a Database

```python
from dictdb import DictDB

db = DictDB()
```

### Creating Tables

```python
# Create a table with default primary key "id"
db.create_table("users")

# Create a table with custom primary key
db.create_table("products", primary_key="sku")

# Get a table reference
users = db.get_table("users")
products = db.get_table("products")
```

### Inserting Records

```python
# Auto-generated primary key
users.insert({"name": "Alice", "email": "alice@example.com"})
# Returns: 1 (the auto-generated id)

# Explicit primary key
users.insert({"id": 100, "name": "Bob", "email": "bob@example.com"})

# Custom primary key field
products.insert({"sku": "ABC123", "name": "Widget", "price": 9.99})
```

### Selecting Records

```python
from dictdb import Condition

# Select all records
all_users = users.select()

# Select with condition
admins = users.select(where=Condition(users.role == "admin"))

# Select specific columns
names = users.select(columns=["name", "email"])

# Sorting
sorted_users = users.select(order_by="name")
sorted_desc = users.select(order_by="-name")  # Descending

# Pagination
page = users.select(order_by="id", limit=10, offset=20)
```

### Updating Records

```python
# Update matching records
users.update(
    {"role": "moderator"},
    where=Condition(users.name == "Alice")
)

# Returns the number of updated records
```

### Deleting Records

```python
# Delete matching records
users.delete(where=Condition(users.name == "Bob"))

# Returns the number of deleted records
```

### Persistence

```python
# Save to JSON (human-readable)
db.save("database.json", file_format="json")

# Save to Pickle (faster, binary)
db.save("database.pkl", file_format="pickle")

# Load from file
db = DictDB.load("database.json", file_format="json")
```

## Table Operations

```python
# List all tables
db.list_tables()  # ["users", "products"]

# Get table metadata
users.count()           # Number of records
users.columns()         # List of column names
users.primary_key_name()  # "id"

# Drop a table
db.drop_table("products")
```

## Error Handling

```python
from dictdb import (
    DuplicateKeyError,
    DuplicateTableError,
    RecordNotFoundError,
    TableNotFoundError,
    SchemaValidationError,
)

try:
    users.insert({"id": 1, "name": "Duplicate"})
except DuplicateKeyError:
    print("Record with this key already exists")

try:
    db.create_table("users")
except DuplicateTableError:
    print("Table already exists")

try:
    users.delete(where=Condition(users.name == "NonExistent"))
except RecordNotFoundError:
    print("No matching records found")
```

## Next Steps

- [Query DSL](guides/query-dsl.md) - Learn the full query syntax
- [Indexes](guides/indexes.md) - Speed up queries with indexes
- [Schemas](guides/schemas.md) - Add type validation
- [Persistence](guides/persistence.md) - Save and load databases
- [Backups](guides/backups.md) - Automatic backup management
