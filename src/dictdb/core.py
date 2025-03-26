"""
dictdb/core.py

This module implements an in-memory database system called DictDB that mimics a
SQL-style database using Python dictionaries. The main components are:

- DictDB: The main database class managing multiple tables.
- Table: Represents a single table with CRUD operations.
- Field: Provides dynamic access to table columns via attribute lookup.
- Condition: Wraps predicate functions for building query conditions.
- Query: A thin wrapper around Condition that allows implicit boolean conversion
         (i.e. prevents warnings) and enables a natural syntax for queries.

Each Table supports methods for inserting, selecting, updating, and deleting records.
Conditions for queries can be built using overloaded operators on Fields, and then wrapped
in a Query object for use in CRUD operations.

Usage Example:
--------------
    from dictdb import DictDB, Query

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")
    users.insert({"id": 1, "name": "Alice", "age": 30})
    results = users.select(where=Query(users.name == "Alice"))
    print(results)
"""

# Type alias for a predicate function that takes a record (dict) and returns a bool.
# A where clause may be a predicate or a Query.


