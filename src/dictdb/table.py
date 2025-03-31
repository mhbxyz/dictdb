import operator
from typing import Any, Optional, Dict, List, Callable, cast

from .exceptions import SchemaValidationError, DuplicateKeyError, RecordNotFoundError
from .condition import Condition, Query
from .index import IndexBase, HashIndex, SortedIndex
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
        :param value: The value to compare against.
        :param op: A binary operator function (e.g., operator.eq, operator.lt).
        """
        self.field: str = field
        self.value: Any = value
        self.op: Callable[[Any, Any], bool] = op

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
    Supports dynamic attribute access to fields for building conditions and
    allows creation of indexes on specific fields for query acceleration.
    """
    def __init__(self, name: str, primary_key: str = 'id', schema: Optional[Schema] = None) -> None:
        """
        Initializes a new Table.

        :param name: The name of the table.
        :param primary_key: The field to use as the primary key.
        :param schema: An optional schema dict mapping field names to types.
        """
        self.table_name: str = name  # Stored as table_name to free up 'name'
        self.primary_key: str = primary_key
        self.records: Dict[Any, Record] = {}  # Maps primary key to record (dict)
        self.schema = schema
        if self.schema is not None:
            if self.primary_key not in self.schema:
                self.schema[self.primary_key] = int
        # Indexes: mapping field name to an IndexBase instance.
        self.indexes: Dict[str, IndexBase] = {}

    def __getattr__(self, attr: str) -> Field:
        """
        Dynamically provides a Field object for the given attribute name.

        :param attr: The field name.
        :return: A Field instance for use in conditions.
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
            # Note: indexes are not pickled; they can be recreated if needed.
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Restores the state of the Table instance from the pickled state.
        """
        self.table_name = state["table_name"]
        self.primary_key = state["primary_key"]
        self.records = state["records"]
        self.schema = state["schema"]
        self.indexes = {}

    def create_index(self, field: str, index_type: str = "hash") -> None:
        """
        Creates an index on the specified field using the desired index type.

        If index creation fails, logs the error and the system will continue to operate
        correctly using full table scans instead of the index.

        :param field: The field name on which to create an index.
        :param index_type: The type of index to create ("hash" or "sorted").
        """
        if field in self.indexes:
            return
        try:
            index_instance: IndexBase
            if index_type == "hash":
                index_instance = HashIndex()
            elif index_type == "sorted":
                index_instance = SortedIndex()
            else:
                raise ValueError("Unsupported index type. Use 'hash' or 'sorted'.")
            # Populate the index with existing records.
            for pk, record in self.records.items():
                if field in record:
                    index_instance.insert(pk, record[field])
            self.indexes[field] = index_instance
            logger.debug(
                f"[INDEX] Created {index_type} index on field '{field}' for table '{self.table_name}'."
            )
        except Exception as e:
            logger.error(f"[INDEX] Failed to create index on field '{field}': {e}")

    def _update_indexes_on_insert(self, record: Record) -> None:
        """
        Updates all indexes with the newly inserted record.

        :param record: The record that was inserted.
        """
        pk = record[self.primary_key]
        for field, index in self.indexes.items():
            if field in record:
                index.insert(pk, record[field])

    def _update_indexes_on_update(self, pk: Any, old_record: Record, new_record: Record) -> None:
        """
        Updates indexes for a record that has been updated.

        :param pk: The primary key of the updated record.
        :param old_record: The record's state before the update.
        :param new_record: The record's state after the update.
        """
        for field, index in self.indexes.items():
            old_value = old_record.get(field)
            new_value = new_record.get(field)
            if old_value == new_value:
                continue
            index.update(pk, old_value, new_value)

    def _update_indexes_on_delete(self, record: Record) -> None:
        """
        Removes the record from all indexes when it is deleted.

        :param record: The record to remove from indexes.
        """
        pk = record[self.primary_key]
        for field, index in self.indexes.items():
            if field in record:
                index.delete(pk, record[field])

    def _is_indexed_eq_condition(self, where: Query) -> bool:
        """
        Determines if the provided Query represents a simple equality condition
        on an indexed field.

        :param where: The Query condition.
        :return: True if the condition is a simple equality on an indexed field.
        """
        func = cast(_FieldCondition, where.condition.func)
        if func.op == operator.eq and func.field in self.indexes:
            return True
        return False

    def validate_record(self, record: Record) -> None:
        """
        Validates a record against the table's schema.

        :param record: The record to validate.
        :raises SchemaValidationError: If the record fails schema validation.
        """
        if self.schema is None:
            return
        for field, expected_type in self.schema.items():
            if field not in record:
                raise SchemaValidationError(f"Missing field '{field}' as defined in schema.")
            if not isinstance(record[field], expected_type):
                raise SchemaValidationError(
                    f"Field '{field}' expects type '{expected_type.__name__}', got '{type(record[field]).__name__}'."
                )
        for field in record.keys():
            if field not in self.schema:
                raise SchemaValidationError(f"Field '{field}' is not defined in the schema.")

    def insert(self, record: Record) -> None:
        """
        Inserts a new record into the table, with optional schema validation.

        Auto-assigns a primary key if not provided. Updates indexes automatically.

        :param record: The record to insert.
        :raises DuplicateKeyError: If a record with the same primary key exists.
        :raises SchemaValidationError: If the record fails schema validation.
        """
        logger.debug(f"[INSERT] Attempting to insert record into '{self.table_name}': {record}")
        if self.primary_key not in record:
            new_key = max(self.records.keys()) + 1 if self.records else 1
            record[self.primary_key] = new_key
        else:
            key = record[self.primary_key]
            if key in self.records:
                raise DuplicateKeyError(f"Record with key '{key}' already exists in table '{self.table_name}'.")
        if self.schema is not None:
            self.validate_record(record)
        self.records[record[self.primary_key]] = record
        self._update_indexes_on_insert(record)

    def select(self, columns: Optional[List[str]] = None, where: Optional[Query] = None) -> List[Record]:
        """
        Retrieves records matching an optional condition.

        If the condition is a simple equality on an indexed field, the index is used.

        :param columns: List of fields to include in each returned record. If None, returns full records.
        :param where: A Query used to filter records.
        :return: A list of matching records.
        """
        logger.debug(f"[SELECT] From table '{self.table_name}' with columns={columns}, where={where}")
        results: List[Record] = []
        candidate_records: List[Record]
        if where is not None and self._is_indexed_eq_condition(where):
            func = cast(_FieldCondition, where.condition.func)
            field: str = func.field
            value: Any = func.value
            candidate_pks = self.indexes[field].search(value)
            candidate_records = [self.records[pk] for pk in candidate_pks]
        else:
            candidate_records = list(self.records.values())
        for record in candidate_records:
            if where is None or where(record):
                if columns:
                    filtered = {col: record.get(col) for col in columns}
                    results.append(filtered)
                else:
                    results.append(record)
        return results

    def update(self, changes: Record, where: Optional[Query] = None) -> int:
        """
        Updates records that satisfy the given condition. The operation is atomic:
        if any record fails validation, all changes are rolled back.
        Indexes are updated automatically.

        :param changes: Dictionary of field-value pairs to update.
        :param where: A Query that determines which records to update.
        :raises RecordNotFoundError: If no records match the criteria.
        :raises Exception: If validation fails, all changes are rolled back.
        :return: The number of records updated.
        """
        logger.debug(f"[UPDATE] Attempting update in '{self.table_name}' with changes={changes}, where={where}")
        updated_keys: List[Any] = []
        backup: Dict[Any, Record] = {}
        updated_count = 0
        try:
            for key, record in self.records.items():
                if where is None or where(record):
                    backup[key] = record.copy()
                    updated_keys.append(key)
                    record.update(changes)
                    if self.schema is not None:
                        self.validate_record(record)
                    updated_count += 1
            if updated_count == 0:
                raise RecordNotFoundError(f"No records match the update criteria in table '{self.table_name}'.")
        except Exception as e:
            for key in updated_keys:
                self.records[key] = backup[key]
            raise e

        for pk in updated_keys:
            self._update_indexes_on_update(pk, backup[pk], self.records[pk])
        return updated_count

    def delete(self, where: Optional[Query] = None) -> int:
        """
        Deletes records matching the given condition. Indexes are updated automatically.

        :param where: A Query that determines which records to delete.
        :raises RecordNotFoundError: If no records match the criteria.
        :return: The number of records deleted.
        """
        logger.debug(f"[DELETE] Attempting delete in '{self.table_name}' with where={where}")
        keys_to_delete = [key for key, record in self.records.items() if where is None or where(record)]
        if not keys_to_delete:
            raise RecordNotFoundError(f"No records match the deletion criteria in table '{self.table_name}'.")
        for key in keys_to_delete:
            record = self.records[key]
            self._update_indexes_on_delete(record)
            del self.records[key]
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
