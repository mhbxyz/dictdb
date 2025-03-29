<p align="center">
  <img src="https://raw.githubusercontent.com/mhbxyz/dictdb/main/docs/DictDBLogo.png" alt="DictDB Logo" width="800"/>
</p>

DictDB is an in‑memory, dictionary-based database system for Python. It provides SQL‑like CRUD operations, schema validation, logging, and a fluent interface for building complex query conditions. DictDB can be used for rapid prototyping, testing, or any scenario where a relational‑style workflow is needed in‑memory without the overhead of a full database engine.

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
7. [API Reference](#api-reference)  
   - [DictDB](#class-dictdb)  
   - [Table](#class-table)  
   - [Condition and Query](#condition-and-query)  
   - [Exceptions](#exceptions)

---

## Features

- **Multiple Tables**: Manage any number of in‑memory tables within a single DictDB.
- **SQL‑like CRUD**: Insert, select, update, delete records with a Pythonic API reminiscent of SQL.
- **Schema Validation**: Enforce data consistency by defining a field schema for each table.
- **Condition/Query System**: Build complex filter expressions using logical operators (&, |, ~) and Python comparison operators (==, !=, <, <=, >, >=).
- **Atomic Updates**: If a single record fails schema validation during an update, all changes in that update call are rolled back.
- **Logging and Debugging**: Integrated with Loguru for flexible, configurable logging.
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
    from dictdb import DictDB, logger

    # Optional: configure logging to see debug statements.
    # from dictdb import configure_logging
    # configure_logging(level="DEBUG", console=True)

    # 1. Create a new in-memory DictDB instance
    db = DictDB()

    # 2. Create tables
    db.create_table("users")     # defaults to primary_key="id"
    db.create_table("products", primary_key="product_id")

    # 3. List all tables
    print(db.list_tables())  # ["users", "products"]
~~~

### Inserting Records

~~~python
    # Get the "users" table
    users = db.get_table("users")

    # Insert a record with an explicit primary key
    users.insert({"id": 1, "name": "Alice", "age": 30})

    # Insert a record without specifying the primary key;
    # DictDB will auto-generate one (starting at 1 if table is empty).
    users.insert({"name": "Bob", "age": 25})

    # Insert into the "products" table
    products_table = db.get_table("products")
    products_table.insert({"product_id": 1001, "name": "Laptop", "price": 999.99})
~~~

### Selecting Records

~~~python
    # Select all records (equivalent to SELECT * in SQL)
    all_users = users.select()
    print(all_users)
    # Output: [
    #   {'id': 1, 'name': 'Alice', 'age': 30},
    #   {'id': 2, 'name': 'Bob', 'age': 25}  # auto-assigned ID
    # ]

    # Select only specific columns
    name_only = users.select(columns=["name"])
    print(name_only)
    # Output: [
    #   {'name': 'Alice'},
    #   {'name': 'Bob'}
    # ]
~~~

### Updating Records

~~~python
 from dictdb import Query

 # Update a single record with a condition
 rows_updated = users.update({"age": 26}, where=Query(users.name == "Bob"))
 print(rows_updated)  # 1 record updated

 # Update all records
 rows_updated = users.update({"age": 99})
 print(rows_updated)  # 2 records updated (Alice and Bob)
~~~

### Deleting Records

~~~python
 # Delete a record that meets a condition
 deleted_count = users.delete(where=Query(users.name == "Alice"))
 print(deleted_count)  # 1

 # Delete all records in the table
 deleted_count = users.delete()
 print(deleted_count)  # number of records that were in the table
~~~

---

## Working With Conditions and Queries

DictDB offers a convenient way to build filter conditions through overloaded Python operators.

### Simple Field Comparisons

Every table generates Field objects when you access an attribute. This lets you write:

~~~python
 from dictdb import Query

 # Suppose we have a "users" table with fields: id, name, age
 users = db.get_table("users")

 # Build a condition for "age == 30"
 condition_age_30 = Query(users.age == 30)

 # Now apply it to a select
 alice_30 = users.select(where=condition_age_30)
~~~

Any standard comparison operator is supported (==, !=, <, <=, >, >=).

### Logical Combinations

Condition objects can be chained or combined:

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

When creating a Table, you can provide a schema. The schema is a dictionary where the keys are field names and the values are the expected Python types.

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

 # Inserting a valid record
 table_with_schema.insert({"id": 1, "name": "Alice", "age": 30})
~~~

If the primary_key is missing from the schema, DictDB will auto‑add it as type int.

### Schema Errors

If you insert or update a record that violates the schema (missing a field, adding an unknown field, or having the wrong type), youll get a SchemaValidationError:

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

DictDB integrates with Loguru to provide detailed logs for database operations.

### Configuring Loguru

~~~python
 from dictdb import configure_logging, DictDB

 # Configure logging
 configure_logging(level="DEBUG", console=True, logfile="dictdb.log")

 # Now all internal logs from DictDB are captured at DEBUG level
 db = DictDB()  # e.g. logs "Initialized an empty DictDB instance."
~~~

### Log Levels and Sinks

- **Console sink**: Use console=True to log messages to stdout.
- **File sink**: Set logfile="yourfile.log" to write logs to a file.
- **Log Levels**: "DEBUG", "INFO", "WARNING", etc.

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
~~~

**Example**:

~~~python
 db = DictDB()
 db.create_table("users")
 table = db.get_table("users")
 print(db.list_tables())  # ["users"]
 db.drop_table("users")
~~~

---

### Class Table

Provides CRUD and schema validation.

~~~python
 class Table:
     def __init__(self, name: str, primary_key: str = 'id', schema: Optional[Dict[str, type]] = None) -> None:
         """Create a new table with optional schema validation."""
     
     def insert(self, record: Dict[str, Any]) -> None:
         """Insert a new record, optionally auto-assigning the primary key."""
     
     def select(
             self,
             columns: Optional[List[str]] = None,
             where: Optional[Query] = None
     ) -> List[Dict[str, Any]]:
         """Return matching records as a list of dicts."""
     
     def update(
             self,
             changes: Dict[str, Any],
             where: Optional[Query] = None
     ) -> int:
         """Update matching records. Returns the number of records updated."""
     
     def delete(self, where: Optional[Query] = None) -> int:
         """Delete matching records. Returns the number of records deleted."""
     
     def all(self) -> List[Dict[str, Any]]:
         """Return all records in the table as a list of copies."""
~~~

**Primary Key Handling**  
If the primary key is missing from record during insert, the system auto-assigns an integer key by taking max(existing_keys) + 1.

**Atomic Updates**  
On update, if any updated record fails schema validation, all updated records are rolled back, and an exception is raised.

---

### Condition and Query

These classes enable SQL-like WHERE clauses:

~~~python
 class Condition:
     """Represents a condition (predicate) to be applied to a record."""
     # Overloaded operators for & (AND), | (OR), and ~ (NOT)
     
 class Query:
     """A wrapper that ensures Condition objects are not used in a boolean context."""
~~~

You typically dont construct Condition directly. Instead, you get them from a Table via table.field_name == value. Then wrap them in Query(...) for usage in CRUD calls:

~~~python
 from dictdb import Query

 users = db.get_table("users")
 condition = Query((users.name == "Alice") & (users.age > 25))
 matching_records = users.select(where=condition)
~~~

---

### Exceptions

- `DictDBError`: Base exception class for all DictDB errors.
- `DuplicateKeyError`: Raised on an insert with a duplicate primary key.
- `RecordNotFoundError`: Raised when no records match an update/delete query.
- `SchemaValidationError`: Raised when a record fails schema validation.

**Example**:

~~~python
 from dictdb import DuplicateKeyError, SchemaValidationError

 try:
     users.insert({"id": 1, "name": "Alice", "age": 30})
     users.insert({"id": 1, "name": "Bob", "age": 25})
 except DuplicateKeyError as e:
     print(f"Cannot insert duplicate key: {e}")
~~~
