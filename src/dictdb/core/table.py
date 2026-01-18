import operator
from typing import Any, Optional, Dict, List, cast, Tuple, Union

from ..exceptions import (
    SchemaValidationError,
    DuplicateKeyError,
    RecordNotFoundError,
)
from .condition import Condition
from ..index import IndexBase
from ..index.registry import create as create_index
from ..obs.logging import logger
from .types import Record, Schema
from .field import Field, _FieldCondition
from .rwlock import RWLock


class _RemovedField:
    pass


class Table:
    """
    Represents a single table in the DictDB database.

    Provides SQL-like CRUD operations: INSERT, SELECT, UPDATE, and DELETE.
    Supports dynamic attribute access to fields for building conditions and
    allows creation of indexes on specific fields for query acceleration.
    """

    def __init__(
        self, name: str, primary_key: str = "id", schema: Optional[Schema] = None
    ) -> None:
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
        # Table-scoped reader-writer lock for concurrency control
        self._lock: RWLock = RWLock()

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
        # Recreate non-pickled runtime attributes
        self._lock = RWLock()

    def create_index(self, field: str, index_type: str = "hash") -> None:
        """
        Creates an index on the specified field using the desired index type.

        If index creation fails, logs the error and the system will continue to operate
        correctly using full table scans instead of the index.

        :param field: The field name on which to create an index.
        :param index_type: The type of index to create ("hash" or "sorted").
        """
        with self._lock.write_lock():
            if field in self.indexes:
                return
            try:
                index_instance: IndexBase = create_index(index_type)
                # Populate the index with existing records.
                for pk, record in self.records.items():
                    if field in record:
                        index_instance.insert(pk, record[field])
                self.indexes[field] = index_instance
                bind = logger.bind(
                    table=self.table_name,
                    op="INDEX",
                    field=field,
                    index_type=index_type,
                )
                bind.debug("[INDEX] Created {index_type} index on field '{table}'.")
                bind.info(
                    "Index created on field '{field}' (type={index_type}) for table '{table}'."
                )
            except Exception as e:
                logger.bind(
                    table=self.table_name,
                    op="INDEX",
                    field=field,
                    index_type=index_type,
                ).error(f"[INDEX] Failed to create index on field '{field}': {e}")

    def _update_indexes_on_insert(self, record: Record) -> None:
        """
        Updates all indexes with the newly inserted record.

        :param record: The record that was inserted.
        """
        pk = record[self.primary_key]
        for field, index in self.indexes.items():
            if field in record:
                index.insert(pk, record[field])

    def _update_indexes_on_update(
        self, pk: Any, old_record: Record, new_record: Record
    ) -> None:
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

    def _is_indexed_eq_condition(self, where: Condition) -> bool:
        """
        Determines if the provided Condition represents a simple equality condition
        on an indexed field.

        :param where: The Condition wrapper.
        :return: True if the condition is a simple equality on an indexed field.
        """
        func = where.condition.func
        if isinstance(func, _FieldCondition):
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
                raise SchemaValidationError(
                    f"Missing field '{field}' as defined in schema."
                )
            if not isinstance(record[field], expected_type):
                raise SchemaValidationError(
                    f"Field '{field}' expects type '{expected_type.__name__}', got '{type(record[field]).__name__}'."
                )
        for field in record.keys():
            if field not in self.schema:
                raise SchemaValidationError(
                    f"Field '{field}' is not defined in the schema."
                )

    def insert(self, record: Record) -> None:
        """
        Inserts a new record into the table, with optional schema validation.

        Auto-assigns a primary key if not provided. Updates indexes automatically.

        :param record: The record to insert.
        :raises DuplicateKeyError: If a record with the same primary key exists.
        :raises SchemaValidationError: If the record fails schema validation.
        """
        logger.bind(table=self.table_name, op="INSERT").debug(
            f"[INSERT] Inserting record into '{self.table_name}'"
        )
        with self._lock.write_lock():
            if self.primary_key not in record:
                new_key = max(self.records.keys()) + 1 if self.records else 1
                record[self.primary_key] = new_key
            else:
                key = record[self.primary_key]
                if key in self.records:
                    raise DuplicateKeyError(
                        f"Record with key '{key}' already exists in table '{self.table_name}'."
                    )
            if self.schema is not None:
                self.validate_record(record)
            self.records[record[self.primary_key]] = record
            self._update_indexes_on_insert(record)
        logger.bind(
            table=self.table_name, op="INSERT", pk=record[self.primary_key]
        ).info("Record inserted into '{table}' (pk={pk}).")

    def select(
        self,
        columns: Optional[
            Union[List[str], Dict[str, str], List[Tuple[str, str]]]
        ] = None,
        where: Optional[Condition] = None,
        *,
        order_by: Optional[Union[str, List[str], Tuple[str, ...]]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Record]:
        """
        Retrieves records matching an optional condition.

        If the condition is a simple equality on an indexed field, the index is used.

        :param columns: Projection of fields to include. Can be:
                        - list of field names (str)
                        - dict of alias -> field name
                        - list of (alias, field) tuples
        :param where: A Condition used to filter records.
        :param order_by: Field name or list of field names to sort by. Prefix with '-' for descending.
        :param limit: Maximum number of records to return after offset.
        :param offset: Number of records to skip from the start.
        :return: A list of matching records.
        """
        logger.bind(table=self.table_name, op="SELECT").debug(
            f"[SELECT] Querying '{self.table_name}' (columns={columns}, filtered={where is not None})"
        )
        with self._lock.read_lock():
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
            # Filter and copy records to ensure thread safety outside the lock
            filtered_records: List[Record] = []
            for record in candidate_records:
                if where is None or where(record):
                    filtered_records.append(record.copy())

        # Perform non-structural ops (ordering/projection) outside lock
        from ..query.order import order_records
        from ..query.pager import slice_records
        from ..query.projection import project_records

        ordered = order_records(filtered_records, order_by)
        sliced_records = slice_records(ordered, limit=limit, offset=offset)
        results = project_records(sliced_records, columns)
        return results

    def update(self, changes: Record, where: Optional[Condition] = None) -> int:
        """
        Updates records that satisfy the given condition. The operation is atomic:
        if any record fails validation, all changes are rolled back.
        Indexes are updated automatically.

        :param changes: Dictionary of field-value pairs to update.
        :param where: A Condition that determines which records to update.
        :raises RecordNotFoundError: If no records match the criteria.
        :raises Exception: If validation fails, all changes are rolled back.
        :return: The number of records updated.
        """
        logger.bind(table=self.table_name, op="UPDATE").debug(
            f"[UPDATE] Updating records in '{self.table_name}' (fields={list(changes.keys())})"
        )
        updated_keys: List[Any] = []
        backup: Dict[Any, Record] = {}
        updated_count = 0
        with self._lock.write_lock():
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
                    raise RecordNotFoundError(
                        f"No records match the update criteria in table '{self.table_name}'."
                    )
            except Exception as e:
                for key in updated_keys:
                    self.records[key] = backup[key]
                raise e

            for pk in updated_keys:
                self._update_indexes_on_update(pk, backup[pk], self.records[pk])
        logger.bind(table=self.table_name, op="UPDATE", count=updated_count).info(
            "Updated {count} record(s) in '{table}'."
        )
        return updated_count

    def delete(self, where: Optional[Condition] = None) -> int:
        """
        Deletes records matching the given condition. Indexes are updated automatically.

        :param where: A Condition that determines which records to delete.
        :raises RecordNotFoundError: If no records match the criteria.
        :return: The number of records deleted.
        """
        logger.bind(table=self.table_name, op="DELETE").debug(
            f"[DELETE] Deleting from '{self.table_name}' (filtered={where is not None})"
        )
        with self._lock.write_lock():
            keys_to_delete = [
                key
                for key, record in self.records.items()
                if where is None or where(record)
            ]
            if not keys_to_delete:
                raise RecordNotFoundError(
                    f"No records match the deletion criteria in table '{self.table_name}'."
                )
            for key in keys_to_delete:
                record = self.records[key]
                self._update_indexes_on_delete(record)
                del self.records[key]
            deleted_count = len(keys_to_delete)
        logger.bind(table=self.table_name, op="DELETE", count=deleted_count).info(
            "Deleted {count} record(s) from '{table}'."
        )
        return deleted_count

    def copy(self) -> Dict[Any, Record]:
        """
        Returns a shallow copy of all records in the table.

        :return: A dict mapping primary keys to record copies.
        :rtype: dict
        """
        with self._lock.read_lock():
            return {key: record.copy() for key, record in self.records.items()}

    def all(self) -> List[Record]:
        """
        Returns a list of copies of all records in the table.

        :return: A list of record copies.
        :rtype: list
        """
        with self._lock.read_lock():
            return [record.copy() for record in self.records.values()]

    def columns(self) -> List[str]:
        """
        Returns the list of column names for this table.

        If a schema is defined, columns are derived from it. Otherwise, the
        union of keys across all existing records is returned. The order is
        deterministic (sorted) when derived from records.

        :return: List of column names.
        """
        if self.schema is not None:
            return list(self.schema.keys())
        # Derive from data when schema is absent
        with self._lock.read_lock():
            cols: set[str] = set()
            for rec in self.records.values():
                cols.update(rec.keys())
            return sorted(cols)

    def size(self) -> int:
        """
        Returns the number of records stored in the table.

        :return: Count of records.
        """
        return self.count()

    def count(self) -> int:
        """
        Returns the number of records stored in the table.

        Preferred over size(); size() remains as an alias.

        :return: Count of records.
        """
        with self._lock.read_lock():
            return len(self.records)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return self.count()

    def indexed_fields(self) -> List[str]:
        """
        Returns the list of fields that currently have an index.

        :return: List of indexed field names.
        """
        with self._lock.read_lock():
            return list(self.indexes.keys())

    def has_index(self, field: str) -> bool:
        """
        Indicates whether an index exists for the given field.

        :param field: Field name to check.
        :return: True if an index exists for the field.
        """
        with self._lock.read_lock():
            return field in self.indexes

    def schema_fields(self) -> List[str]:
        """
        Returns the list of fields defined in the schema, or an empty list if no schema.

        :return: Schema field names.
        """
        return list(self.schema.keys()) if self.schema is not None else []

    def primary_key_name(self) -> str:
        """
        Returns the name of the primary key field for this table.

        :return: Primary key field name.
        """
        return self.primary_key
