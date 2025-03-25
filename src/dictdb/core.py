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
    users.insert_record({"id": 1, "name": "Alice", "age": 30})
    results = users.select_records(where=Query(users.name == "Alice"))
    print(results)
"""

from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import DuplicateKeyError, RecordNotFoundError

# Type alias for a predicate function that takes a record (dict) and returns a bool.
Predicate = Callable[[Dict[str, Any]], bool]
# A where clause may be a predicate or a Query.
WherePredicate = Union[Predicate, "Query"]


class Condition:
    """
    Represents a condition (predicate) to be applied to a record.

    Wraps a function that takes a record (dict) and returns a boolean.
    Supports logical operations using:
        - & for logical AND
        - | for logical OR
        - ~ for logical NOT

    Note:
        Implicit boolean conversion is disallowed to prevent accidental usage.
    """

    def __init__(self, func: Predicate) -> None:
        self.func: Predicate = func

    def __call__(self, record: Dict[str, Any]) -> bool:
        return self.func(record)

    def __and__(self, other: "Condition") -> "Condition":
        return Condition(lambda rec: self(rec) and other(rec))

    def __or__(self, other: "Condition") -> "Condition":
        return Condition(lambda rec: self(rec) or other(rec))

    def __invert__(self) -> "Condition":
        return Condition(lambda rec: not self(rec))

    def __bool__(self) -> bool:
        # Prevent implicit boolean conversion
        raise TypeError("Condition objects should not be evaluated as booleans; wrap them in Query instead.")


class Query:
    """
    A wrapper for a Condition to be used as a query predicate.

    By encapsulating a Condition in a Query, implicit boolean conversion
    is avoided, and the Query object can be safely passed as the `where` parameter
    in CRUD methods.

    Example usage:
        Query(table.name == "Alice")
        Query((table.name == "Alice") & (table.age > 25))
    """

    def __init__(self, condition: Condition | bool) -> None:
        self.condition: Condition = condition

    def __call__(self, record: Dict[str, Any]) -> bool:
        return self.condition(record)

    def __and__(self, other: "Query") -> "Query":
        return Query(self.condition & other.condition)

    def __or__(self, other: "Query") -> "Query":
        return Query(self.condition | other.condition)

    def __invert__(self) -> "Query":
        return Query(~self.condition)


class Field:
    """
    A helper class representing a field (column) in a table.

    Overloads comparison operators to produce Condition instances.
    This Field is created dynamically by the Table via attribute lookup.
    """

    def __init__(self, table: "Table", name: str) -> None:
        self.table = table
        self.name = name

    def __eq__(self, other: Any) -> Condition:
        return Condition(lambda rec: rec.get(self.name) == other)

    def __ne__(self, other: Any) -> Condition:
        return Condition(lambda rec: rec.get(self.name) != other)

    def __lt__(self, other: Any) -> Condition:
        return Condition(lambda rec: rec.get(self.name) < other)

    def __le__(self, other: Any) -> Condition:
        return Condition(lambda rec: rec.get(self.name) <= other)

    def __gt__(self, other: Any) -> Condition:
        return Condition(lambda rec: rec.get(self.name) > other)

    def __ge__(self, other: Any) -> Condition:
        return Condition(lambda rec: rec.get(self.name) >= other)


class Table:
    """
    Represents a single table in the DictDB database.

    Provides SQL-like CRUD operations: INSERT, SELECT, UPDATE, and DELETE.
    Also allows dynamic attribute access to fields so you can write conditions
    like: where = Query(User.name == 'Alice')
    """

    def __init__(self, name: str, primary_key: str = 'id') -> None:
        self.table_name: str = name  # Store the table name in table_name to free up 'name'
        self.primary_key: str = primary_key
        self.records: Dict[Any, Dict[str, Any]] = {}  # Maps primary key to record (dict)

    def __getattr__(self, attr: str) -> Field:
        # Dynamically return a Field instance for undefined attributes.
        return Field(self, attr)

    def insert(self, record: Dict[str, Any]) -> None:
        """
        Inserts a new record into the table.

        If the record does not contain the primary key, it automatically assigns the next available key.
        If the record includes the primary key, it validates that no duplicate key exists.

        Args:
            record: The record to insert.

        Raises:
            DuplicateKeyError: If a record with the same primary key already exists.
        """
        # Auto-generate primary key if not provided
        if self.primary_key not in record:
            if self.records:
                # Assumes keys are integers; auto-assign the next available integer key.
                new_key = max(self.records.keys()) + 1
            else:
                new_key = 1
            record[self.primary_key] = new_key
        else:
            key = record[self.primary_key]
            if key in self.records:
                raise DuplicateKeyError(f"Record with key '{key}' already exists in table '{self.table_name}'.")

        self.records[record[self.primary_key]] = record

    def select(
            self,
            columns: Optional[List[str]] = None,
            where: Optional[WherePredicate] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves records that match an optional condition.

        Args:
            columns: List of fields to include in the output. If None, returns full records.
            where: A function (or Query) to filter records.

        Returns:
            A list of matching records.
        """
        results: List[Dict[str, Any]] = []
        for record in self.records.values():
            if where is None or where(record):
                if columns:
                    filtered = {col: record.get(col) for col in columns}
                    results.append(filtered)
                else:
                    results.append(record)
        return results

    def update(
            self,
            changes: Dict[str, Any],
            where: Optional[WherePredicate] = None
    ) -> int:
        """
        Updates records that satisfy the given condition.

        Args:
            changes: Field-value pairs to update.
            where: A function (or Query) to determine which records to update.

        Returns:
            The number of records updated.

        Raises:
            RecordNotFoundError: If no records match the update criteria.
        """
        updated_count = 0
        for record in self.records.values():
            if where is None or where(record):
                record.update(changes)
                updated_count += 1
        if updated_count == 0:
            raise RecordNotFoundError(f"No records match the update criteria in table '{self.table_name}'.")
        return updated_count

    def delete(self, where: Optional[WherePredicate] = None) -> int:
        """
        Deletes records that satisfy the given condition.

        Args:
            where: A function (or Query) to determine which records to delete.

        Returns:
            The number of records deleted.

        Raises:
            RecordNotFoundError: If no records match the deletion criteria.
        """
        keys_to_delete = [key for key, record in self.records.items() if where is None or where(record)]
        for key in keys_to_delete:
            del self.records[key]
        if not keys_to_delete:
            raise RecordNotFoundError(f"No records match the deletion criteria in table '{self.table_name}'.")
        return len(keys_to_delete)


class DictDB:
    """
    The main in-memory database class that supports multiple tables.

    Provides methods to create, drop, and retrieve tables.
    """

    def __init__(self) -> None:
        self.tables: Dict[str, Table] = {}

    def create_table(self, table_name: str, primary_key: str = 'id') -> None:
        """
        Creates a new table in the database.

        Args:
            table_name: The name of the table to create.
            primary_key: The primary key field for the table.

        Raises:
            ValueError: If the table already exists.
        """
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists.")
        self.tables[table_name] = Table(table_name, primary_key)

    def drop_table(self, table_name: str) -> None:
        """
        Removes a table from the database.

        Args:
            table_name: The name of the table to drop.

        Raises:
            ValueError: If the table does not exist.
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        del self.tables[table_name]

    def get_table(self, table_name: str) -> Table:
        """
        Retrieves a table by name.

        Args:
            table_name: The name of the table to retrieve.

        Returns:
            The corresponding Table instance.

        Raises:
            ValueError: If the table does not exist.
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        return self.tables[table_name]

    def list_tables(self) -> List[str]:
        """
        Lists all table names in the database.

        Returns:
            A list of table names.
        """
        return list(self.tables.keys())
