<p align="center">
  <img src="https://raw.githubusercontent.com/mhbxyz/dictdb/main/docs/DictDBLogo.png" alt="DictDB Logo" width="800"/>
</p>

![CI](https://github.com/mhbxyz/dictdb/actions/workflows/ci.yml/badge.svg)
[![Release](https://github.com/mhbxyz/dictdb/actions/workflows/release.yml/badge.svg)](https://github.com/mhbxyz/dictdb/actions/workflows/release.yml)
[![PyPI version](https://img.shields.io/pypi/v/dictdb.svg)](https://pypi.org/project/dictdb/)

DictDB is an in‑memory, dictionary-based database system for Python. It provides SQL‑like CRUD operations, schema validation, logging, indexing, and a fluent interface for building complex query conditions. DictDB can be used for rapid prototyping, testing, or any scenario where a relational‑style workflow is needed in‑memory without the overhead of a full database engine.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
   - [Creating a Database and Tables](#creating-a-database-and-tables)
   - [Inserting Records](#inserting-records)
   - [Selecting Records](#selecting-records)
   - [Updating Records](#updating-records)
   - [Deleting Records](#deleting-records)
4. [Working With Conditions and Queries](#working-with-conditions-and-queries)
   - [Simple Field Comparisons](#simple-field-comparisons)
   - [Logical Combinations](#logical-combinations)
5. [Schema Validation](#schema-validation)
   - [Defining a Schema](#defining-a-schema)
   - [Schema Errors](#schema-errors)
6. [Logging](#logging)
   - [Configuring Loguru](#configuring-loguru)
   - [Log Levels and Sinks](#log-levels-and-sinks)
7. [Persistence, Backup, and Indexing](#persistence-backup-and-indexing)
   - [Synchronous and Asynchronous Persistence](#synchronous-and-asynchronous-persistence)
   - [Backup Manager](#backup-manager)
   - [Indexing](#indexing)
8. [API Reference](#api-reference)
   - [DictDB](#class-dictdb)
   - [Table](#class-table)
   - [Condition and Query](#condition-and-query)
   - [Exceptions](#exceptions)
   - [BackupManager](#backupmanager)
9. [Roadmap](#roadmap)

---

## Features

- **Multiple Tables**: Manage any number of in‑memory tables within a single DictDB.
- **SQL‑like CRUD**: Insert, select, update, and delete records with a Pythonic API reminiscent of SQL.
- **Schema Validation**: Enforce data consistency by defining a field schema for each table.
- **Condition/Query System**: Build complex filter expressions using logical operators (&, |, ~) and Python comparison operators (==, !=, <, <=, >, >=).
- **Atomic Updates**: All updates are applied atomically; if a single record fails schema validation during an update, all changes are rolled back.
- **Logging and Debugging**: Integrated with Loguru for flexible, configurable logging.
- **Persistence and Backup**: Save and load database state synchronously or asynchronously, with automatic backup support.
- **Indexing**: Optimize query performance by creating indices on table fields.
- **Easy Testing**: Fully unit-tested codebase using pytest.

---

## Installation

DictDB is structured as a standard Python package using pyproject.toml. To install locally (for development or local usage), run:

~~~shell
git clone https://github.com/mhbxyz/dictdb.git
cd dictdb
pip install .
~~~

When published to PyPI **(NOT PUBLISHED YET)**, you could install it with:

~~~shell
pip install dictdb
~~~

### Example Quickstart

Below is a short, end-to-end example showcasing DictDB usage:

~~~python
from dictdb import DictDB, Query, configure_logging

# Optional logging
configure_logging(level="DEBUG", console=True)

# Create DB and tables
db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

# Insert data
employees.insert({"emp_id": 101, "name": "Alice", "department": "IT"})
employees.insert({"emp_id": 102, "name": "Bob", "department": "HR"})
employees.insert({"name": "Charlie", "department": "IT"})  # auto-assigns emp_id=103

# Query data
it_staff = employees.select(where=Query(employees.department == "IT"))
print("IT Department Staff:", it_staff)

# Update data
employees.update({"department": "Engineering"}, where=Query(employees.name == "Alice"))

# Delete data
employees.delete(where=Query(employees.name == "Bob"))

# Print final state
print("All employees:", employees.all())
~~~

---

## Basic Usage

### Creating a Database and Tables

~~~python
from dictdb import DictDB

# Create a new in-memory DictDB instance
db = DictDB()

# Create tables (default primary key is "id")
db.create_table("users")
db.create_table("products", primary_key="product_id")

# List all tables
print(db.list_tables())  # e.g., ["users", "products"]
~~~

### Inserting Records

~~~python
# Get the "users" table
users = db.get_table("users")

# Insert a record with an explicit primary key
users.insert({"id": 1, "name": "Alice", "age": 30})

# Insert a record without specifying the primary key;
# DictDB will auto-generate one.
users.insert({"name": "Bob", "age": 25})

# Insert into the "products" table
products = db.get_table("products")
products.insert({"product_id": 1001, "name": "Laptop", "price": 999.99})
~~~

### Selecting Records

~~~python
# Select all records (equivalent to SQL's SELECT *)
all_users = users.select()
print(all_users)

# Select only specific columns
name_only = users.select(columns=["name"])
print(name_only)
~~~

### Updating Records

~~~python
from dictdb import Query

# Update a single record with a condition
rows_updated = users.update({"age": 26}, where=Query(users.name == "Bob"))
print(rows_updated)

# Update all records
rows_updated = users.update({"age": 99})
print(rows_updated)
~~~

### Deleting Records

~~~python
# Delete a record that meets a condition
deleted_count = users.delete(where=Query(users.name == "Alice"))
print(deleted_count)

# Delete all records in the table
deleted_count = users.delete()
print(deleted_count)
~~~

---

## Working With Conditions and Queries

DictDB allows you to build filter conditions using overloaded Python operators.

### Simple Field Comparisons

~~~python
from dictdb import Query

# Suppose we have a "users" table with fields: id, name, age
users = db.get_table("users")

# Build a condition for "age == 30"
condition = Query(users.age == 30)

# Apply the condition in a select
matching_users = users.select(where=condition)
~~~

### Logical Combinations

~~~python
# (name == "Alice") AND (age > 25)
condition = Query((users.name == "Alice") & (users.age > 25))
result = users.select(where=condition)

# (name == "Alice") OR (age > 25)
condition_or = Query((users.name == "Alice") | (users.age > 25))

# NOT (name == "Alice")
condition_not = Query(~(users.name == "Alice"))
~~~

---

## Schema Validation

### Defining a Schema

~~~python
from dictdb import Table, SchemaValidationError

# Define a schema for users
schema = {
    "id": int,
    "name": str,
    "age": int
}

# Create the table with a schema
table_with_schema = Table("schema_users", primary_key="id", schema=schema)

# Insert a valid record
table_with_schema.insert({"id": 1, "name": "Alice", "age": 30})
~~~

### Schema Errors

If a record violates the schema, DictDB raises a SchemaValidationError:

~~~python
try:
    # Missing 'age' field
    table_with_schema.insert({"id": 2, "name": "Bob"})
except SchemaValidationError as e:
    print(f"Schema error: {e}")

try:
    # Extra field 'nickname' not in schema
    table_with_schema.insert({"id": 3, "name": "Charlie", "age": 28, "nickname": "Chaz"})
except SchemaValidationError as e:
    print(f"Schema error: {e}")

try:
    # Wrong type for 'age'
    table_with_schema.insert({"id": 4, "name": "Diana", "age": "30"})
except SchemaValidationError as e:
    print(f"Schema error: {e}")
~~~

---

## Logging

DictDB integrates with Loguru for detailed logging.

### Configuring Loguru

~~~python
from dictdb import configure_logging, DictDB

# Configure logging to both console and a file
configure_logging(level="DEBUG", console=True, logfile="dictdb.log")

db = DictDB()  # Logs "Initialized an empty DictDB instance."
~~~

### Log Levels and Sinks

- **Console sink**: Set `console=True` to log to stdout.
- **File sink**: Specify `logfile="yourfile.log"` to write logs to a file.
- **Log Levels**: Options include "DEBUG", "INFO", "WARNING", etc.

---

## Persistence, Backup, and Indexing

DictDB supports saving and loading database states, as well as automatic backups and indexing to enhance performance.

### Synchronous and Asynchronous Persistence

You can persist the database state in JSON or pickle formats. DictDB offers both synchronous and asynchronous methods:

~~~python
# Synchronous save and load
db.save("backup.json", "json")
loaded_db = DictDB.load("backup.json", "json")

# Asynchronous save and load (requires an async context)
await db.async_save("backup_async.json", "json")
loaded_db = await DictDB.async_load("backup_async.json", "json")
~~~

### Backup Manager

The BackupManager provides automatic periodic backups or immediate backups after significant changes.

~~~python
from dictdb import BackupManager

# Create a backup manager with a backup interval of 300 seconds
backup_manager = BackupManager(db, backup_dir="backups", backup_interval=300, file_format="json")
backup_manager.start()

# Trigger an immediate backup when needed
backup_manager.notify_change()

# Stop the backup manager gracefully
backup_manager.stop()
~~~

### Indexing

To optimize query performance, you can create indices on table fields. DictDB supports both "hash" and "sorted" index types:

~~~python
# Create an index on the "age" field using a hash index
users.create_index("age", index_type="hash")

# Alternatively, create a sorted index:
users.create_index("age", index_type="sorted")
~~~

---

## API Reference

### Class DictDB

~~~python
class DictDB:
    def __init__(self) -> None:
        """Initializes an empty DictDB instance."""
    
    def create_table(self, table_name: str, primary_key: str = 'id') -> None:
        """Creates a new table with the specified name and optional primary key."""
    
    def drop_table(self, table_name: str) -> None:
        """Removes a table from the database by name."""
    
    def get_table(self, table_name: str) -> Table:
        """Retrieves a Table object by its name."""
    
    def list_tables(self) -> List[str]:
        """Returns a list of all table names in this DictDB."""
    
    def save(self, filename: str, file_format: str) -> None:
        """Saves the current state of the database in the specified format."""
    
    def load(self, filename: str, file_format: str) -> DictDB:
        """Loads a database state from the specified file."""
    
    async def async_save(self, filename: str, file_format: str) -> None:
        """Asynchronously saves the current state of the database."""
    
    @classmethod
    async def async_load(cls, filename: str, file_format: str) -> DictDB:
        """Asynchronously loads the database state from the specified file."""
~~~

### Class Table

Provides CRUD operations and schema validation.

~~~python
class Table:
    def __init__(self, name: str, primary_key: str = 'id', schema: Optional[Dict[str, type]] = None) -> None:
        """Creates a new table with optional schema validation."""
    
    def insert(self, record: Dict[str, Any]) -> None:
        """Inserts a new record, with auto-assignment of the primary key if necessary."""
    
    def select(self, columns: Optional[List[str]] = None, where: Optional[Query] = None) -> List[Dict[str, Any]]:
        """Selects records matching a condition, with optional column projection."""
    
    def update(self, changes: Dict[str, Any], where: Optional[Query] = None) -> int:
        """Updates records matching a condition. Returns the number of records updated."""
    
    def delete(self, where: Optional[Query] = None) -> int:
        """Deletes records matching a condition. Returns the number of records deleted."""
    
    def all(self) -> List[Dict[str, Any]]:
        """Returns all records in the table."""
    
    def create_index(self, field_name: str, index_type: str = "hash") -> None:
        """Creates an index on the specified field. Supported types: 'hash', 'sorted'."""
~~~

### Condition and Query

~~~python
class Condition:
    """Represents a condition to be applied to records. Supports logical operators (&, |, ~)."""

class Query:
    """A wrapper for Condition objects to prevent implicit boolean conversion."""
~~~

### Exceptions

- `DictDBError`: Base exception for DictDB errors.
- `DuplicateKeyError`: Raised when inserting a record with a duplicate primary key.
- `RecordNotFoundError`: Raised when no records match a query.
- `SchemaValidationError`: Raised when a record violates the defined schema.
  
### BackupManager

~~~python
class BackupManager:
    def __init__(self, db: DictDB, backup_dir: Union[str, Path], backup_interval: int = 300, file_format: str = "json") -> None:
        """Initializes the BackupManager."""
    
    def start(self) -> None:
        """Starts automatic periodic backups."""
    
    def stop(self) -> None:
        """Stops the backup manager."""
    
    def backup_now(self) -> None:
        """Performs an immediate backup."""
    
    def notify_change(self) -> None:
        """Triggers an immediate backup after a significant change."""
~~~

---

## Roadmap

See [roadmap.md](roadmap.md) for planned features and enhancements.

---

DictDB is an evolving project. Contributions, suggestions, and bug reports are welcome!
