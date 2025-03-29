import operator
from typing import Any, Optional, Dict, List, Callable

from .exceptions import SchemaValidationError, DuplicateKeyError, RecordNotFoundError
from .condition import Condition, Query
from .logging import logger
from .types import Record, Schema


class _FieldCondition:
    """
    A callable class representing a condition on a field.

    It encapsulates the field name, a value to compare, and an operator function.
    """
    def __init__(self, field: str, value: Any, op: Callable[[Any, Any], bool]) -> None:
        """
        Initializes a _FieldCondition instance.

        :param field: The name of the field.
        :type field: str
        :param value: The value to compare against.
        :type value: Any
        :param op: A binary operator function (e.g., operator.eq, operator.lt).
        :type op: Callable[[Any, Any], bool]
        """
        self.field = field
        self.value = value
        self.op = op

    def __call__(self, record: Dict[str, Any]) -> bool:
        """
        Evaluates the condition on the given record.

        :param record: The record (dictionary) to evaluate.
        :type record: dict
        :return: True if the condition is satisfied; otherwise False.
        :rtype: bool
        """
        return self.op(record.get(self.field), self.value)


class Field:
    """
    Represents a field (column) in a table and overloads comparison operators
    to produce Condition instances.

    Instances of Field are created dynamically by the Table via attribute lookup.
    """

    def __init__(self, table: "Table", name: str) -> None:
        """
        Initializes a Field tied to a specific table and field name.

        :param table: The Table this field belongs to.
        :type table: Table
        :param name: The name of the field.
        :type name: str
        """
        self.table = table
        self.name = name

    def __eq__(self, other: Any) -> Condition:  # type: ignore[override]
        """
        Creates a Condition checking for equality.

        :param other: A value to compare against.
        :type other: Any
        :return: A Condition instance.
        """
        return Condition(_FieldCondition(self.name, other, operator.eq))

    def __ne__(self, other: Any) -> Condition:  # type: ignore[override]
        """
        Creates a Condition checking for inequality.

        :param other: A value to compare against.
        :type other: Any
        :return: A Condition instance.
        """
        return Condition(_FieldCondition(self.name, other, operator.ne))

    def __lt__(self, other: Any) -> Condition:
        """
        Creates a Condition checking for less-than.

        :param other: A value to compare against.
        :type other: Any
        :return: A Condition instance.
        """
        return Condition(_FieldCondition(self.name, other, operator.lt))

    def __le__(self, other: Any) -> Condition:
        """
        Creates a Condition checking for less-than-or-equal.

        :param other: A value to compare against.
        :type other: Any
        :return: A Condition instance.
        """
        return Condition(_FieldCondition(self.name, other, operator.le))

    def __gt__(self, other: Any) -> Condition:
        """
        Creates a Condition checking for greater-than.

        :param other: A value to compare against.
        :type other: Any
        :return: A Condition instance.
        """
        return Condition(_FieldCondition(self.name, other, operator.gt))

    def __ge__(self, other: Any) -> Condition:
        """
        Creates a Condition checking for greater-than-or-equal.

        :param other: A value to compare against.
        :type other: Any
        :return: A Condition instance.
        """
        return Condition(_FieldCondition(self.name, other, operator.ge))


class Table:
    """
    Represents a single table in the DictDB database.

    Provides SQL-like CRUD operations: INSERT, SELECT, UPDATE, and DELETE.
    Allows dynamic attribute access to fields for building conditions.
    """

    def __init__(self, name: str, primary_key: str = 'id', schema: Optional[Schema] = None) -> None:
        """
        Initializes a new Table.

        :param name: The name of the table.
        :type name: str
        :param primary_key: The field to use as the primary key.
        :type primary_key: str
        :param schema: An optional schema dict mapping field names to types.
        :type schema: dict or None
        :return: None
        :rtype: None
        """
        self.table_name: str = name  # Store the table name in table_name to free up 'name'
        self.primary_key: str = primary_key
        self.records: Dict[Any, Record] = {}  # Maps primary key to record (dict)
        self.schema = schema
        if self.schema is not None:
            # Ensure that the primary key is part of the schema.
            if self.primary_key not in self.schema:
                # Auto-add primary key to schema with type int.
                self.schema[self.primary_key] = int

    def __getattr__(self, attr: str) -> Field:
        """
        Dynamically provides a Field object for the given attribute name.

        :param attr: The field name.
        :type attr: str
        :return: A Field instance for use in conditions.
        :rtype: Field
        """
        return Field(self, attr)

    def __getstate__(self) -> Dict[str, Any]:
        """
        Returns the state of the Table instance for pickling.
        Only include core attributes to avoid pickling dynamically generated objects.
        """
        return {
            "table_name": self.table_name,
            "primary_key": self.primary_key,
            "records": self.records,
            "schema": self.schema,
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Restores the state of the Table instance from the pickled state.
        """
        self.table_name = state["table_name"]
        self.primary_key = state["primary_key"]
        self.records = state["records"]
        self.schema = state["schema"]

    def validate_record(self, record: Record) -> None:
        """
        Validates a record against the table's schema.

        :param record: The record to validate.
        :type record: dict
        :raises SchemaValidationError: If the record fails schema validation.
        :return: None
        :rtype: None
        """
        if self.schema is None:
            # No schema means no validation is performed.
            return

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

    def insert(self, record: Record) -> None:
        """
        Inserts a new record into the table, with optional schema validation.

        Auto-assigns a primary key if one is not provided. Raises an error if
        the primary key already exists.

        :param record: The record to insert.
        :type record: dict
        :raises DuplicateKeyError: If a record with the same primary key exists.
        :raises SchemaValidationError: If the record fails schema validation.
        :return: None
        :rtype: None
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
    ) -> List[Record]:
        """
        Retrieves records matching an optional condition.

        :param columns: List of fields to include in each returned record. If None, returns full records.
        :type columns: list of str or None
        :param where: A Query (or None) used to filter records.
        :type where: Query or None
        :return: A list of matching records.
        :rtype: list of dict
        """
        logger.debug(f"[SELECT] From table '{self.table_name}' with columns={columns}, where={where}")
        results: List[Record] = []
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
            changes: Record,
            where: Optional[Query] = None
    ) -> int:
        """
        Updates records that satisfy the given condition, optionally validated against the schema.

        If any record fails validation, all updates in this call are rolled back.

        :param changes: Dictionary of field-value pairs to update.
        :type changes: dict
        :param where: A Query that determines which records to update. If None, all are updated.
        :type where: Query or None
        :raises RecordNotFoundError: If no records match the update criteria.
        :raises Exception: If validation fails or any other error occurs, changes are rolled back.
        :return: The number of records updated.
        :rtype: int
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
        Deletes records matching the given condition.

        :param where: A Query that determines which records to delete. If None, all are deleted.
        :type where: Query or None
        :raises RecordNotFoundError: If no records match the deletion criteria.
        :return: The number of records deleted.
        :rtype: int
        """
        logger.debug(f"[DELETE] Attempting delete in '{self.table_name}' with where={where}")
        keys_to_delete = [key for key, record in self.records.items() if where is None or where(record)]
        for key in keys_to_delete:
            del self.records[key]
        if not keys_to_delete:
            raise RecordNotFoundError(f"No records match the deletion criteria in table '{self.table_name}'.")
        return len(keys_to_delete)

    def copy(self) -> Dict[Any, Record]:
        """
        Returns a shallow copy of all records in the table.

        :return: A dict mapping primary keys to record copies.
        :rtype: dict
        """
        return {key: record.copy() for key, record in self.records.items()}

    def all(self) -> List[Record]:
        """
        Returns a list of copies of all records in the table.

        :return: A list of record copies.
        :rtype: list
        """
        return [record.copy() for record in self.records.values()]
