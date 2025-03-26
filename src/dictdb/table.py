from typing import Any, Optional, Dict, List

from .exceptions import SchemaValidationError, DuplicateKeyError, RecordNotFoundError
from .condition import Condition, Query
from .logging import logger


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

    def __init__(self, name: str, primary_key: str = 'id', schema: Optional[Dict[str, type]] = None) -> None:
        self.table_name: str = name  # Store the table name in table_name to free up 'name'
        self.primary_key: str = primary_key
        self.records: Dict[Any, Dict[str, Any]] = {}  # Maps primary key to record (dict)
        self.schema = schema
        if self.schema is not None:
            # Ensure that the primary key is part of the schema.
            if self.primary_key not in self.schema:
                # Auto-add primary key to schema with type int.
                self.schema[self.primary_key] = int

    def __getattr__(self, attr: str) -> Field:
        """
        Allows dynamic attribute access to fields. For example, table.name will return
        a Field object that can be used in query expressions.
        """
        return Field(self, attr)

    def validate_record(self, record: Dict[str, Any]) -> None:
        """
        Validates a record against the table's schema.

        Raises:
            SchemaValidationError: If the record does not conform to the schema.
        """
        # Check that all schema-defined fields are present and have the correct type.
        for field, expected_type in self.schema.items():
            if field not in record:
                raise SchemaValidationError(f"Missing field '{field}' as defined in schema.")
            if not isinstance(record[field], expected_type):
                raise SchemaValidationError(
                    f"Field '{field}' expects type '{expected_type.__name__}', got '{type(record[field]).__name__}'."
                )
        # Optionally, enforce that no extra fields are present.
        for field in record.keys():
            if field not in self.schema:
                raise SchemaValidationError(f"Field '{field}' is not defined in the schema.")

    def insert(self, record: Dict[str, Any]) -> None:
        """
        Inserts a new record into the table, with schema validation if a schema is defined.

        If the record does not contain the primary key, it automatically assigns the next available key.
        If the record includes the primary key, it validates that no duplicate key exists.
        Additionally, if a schema is defined, the record is validated against the schema.

        Args:
            record: The record to insert.

        Raises:
            DuplicateKeyError: If a record with the same primary key already exists.
            SchemaValidationError: If the record does not match the defined schema.
        """
        logger.debug(f"[INSERT] Attempting to insert record into '{self.table_name}': {record}")
        # Auto-generate primary key if not provided.
        if self.primary_key not in record:
            if self.records:
                new_key = max(self.records.keys()) + 1
            else:
                new_key = 1
            record[self.primary_key] = new_key
        else:
            key = record[self.primary_key]
            if key in self.records:
                raise DuplicateKeyError(
                    f"Record with key '{key}' already exists in table '{self.table_name}'."
                )

        # If a schema is defined, validate the record.
        if self.schema is not None:
            self.validate_record(record)

        self.records[record[self.primary_key]] = record

    def select(
            self,
            columns: Optional[List[str]] = None,
            where: Optional[Query] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves records that match an optional condition.

        Args:
            columns: List of fields to include in the output. If None, returns full records.
            where: A function (or Query) to filter records.

        Returns:
            A list of matching records.
        """
        logger.debug(f"[SELECT] From table '{self.table_name}' with columns={columns}, where={where}")
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
            where: Optional[Query] = None
    ) -> int:
        """
        Atomically updates records that satisfy the given condition.
        If 'where' is omitted (None), all records in the table will be updated.
        If an error occurs while updating any record (e.g., due to schema validation),
        all changes made during this update operation are rolled back.

        Args:
            changes: Field-value pairs to update.
            where: A function (or Query) to determine which records to update.

        Returns:
            The number of records updated.

        Raises:
            RecordNotFoundError: If no records match the update criteria.
            Exception: Propagates any exception encountered during the update, after rolling back.
        """
        logger.debug(f"[UPDATE] Attempting update in '{self.table_name}' with changes={changes}, where={where}")
        updated_keys = []
        backup = {}
        updated_count = 0
        try:
            for key, record in self.records.items():
                if where is None or where(record):
                    backup[key] = record.copy()
                    # Mark the record for rollback immediately.
                    updated_keys.append(key)
                    record.update(changes)
                    if self.schema is not None:
                        self.validate_record(record)
                    updated_count += 1

            if updated_count == 0:
                raise RecordNotFoundError(f"No records match the update criteria in table '{self.table_name}'.")
        except Exception as e:
            # Roll back all changes for records that were attempted to be updated.
            for key in updated_keys:
                self.records[key] = backup[key]
            raise e

        return updated_count

    def delete(self, where: Optional[Query] = None) -> int:
        """
        Deletes records that satisfy the given condition.

        Args:
            where: A function (or Query) to determine which records to delete.

        Returns:
            The number of records deleted.

        Raises:
            RecordNotFoundError: If no records match the deletion criteria.
        """
        logger.debug(f"[DELETE] Attempting delete in '{self.table_name}' with where={where}")
        keys_to_delete = [key for key, record in self.records.items() if where is None or where(record)]
        for key in keys_to_delete:
            del self.records[key]
        if not keys_to_delete:
            raise RecordNotFoundError(f"No records match the deletion criteria in table '{self.table_name}'.")
        return len(keys_to_delete)

    def copy(self) -> dict:
        """
        Returns a shallow copy of all records in the table as a dictionary mapping primary keys to record copies.
        """
        return {key: record.copy() for key, record in self.records.items()}

    def all(self) -> list:
        """
        Returns a list of copies of all records in the table.
        """
        return [record.copy() for record in self.records.values()]
