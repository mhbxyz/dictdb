import operator
from typing import Any, Literal, Optional, Dict, List, overload, Tuple, Union

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
from .field import Field, _FieldCondition, _IsInCondition
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
        # Monotonic counter for auto-generated primary keys (O(1) instead of O(n))
        self._next_pk: int = 1
        if self.schema is not None:
            if self.primary_key not in self.schema:
                self.schema[self.primary_key] = int
        # Indexes: mapping field name to an IndexBase instance.
        self.indexes: Dict[str, IndexBase] = {}
        # Table-scoped reader-writer lock for concurrency control
        self._lock: RWLock = RWLock()
        # Dirty tracking for incremental backups
        self._dirty_pks: set[Any] = set()  # PKs inserted or updated since last backup
        self._deleted_pks: set[Any] = set()  # PKs deleted since last backup

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
            "_next_pk": self._next_pk,
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
        # Recalculate _next_pk from records for backwards compatibility
        int_keys = [k for k in self.records.keys() if isinstance(k, int)]
        self._next_pk = max(int_keys) + 1 if int_keys else 1
        self.indexes = {}
        # Recreate non-pickled runtime attributes
        self._lock = RWLock()
        self._dirty_pks = set()
        self._deleted_pks = set()

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
                bind.debug("[INDEX] Created {index_type} index on field '{field}'.")
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

    def _get_indexed_candidate_pks(
        self, where: Optional[Condition]
    ) -> Optional[set[Any]]:
        """
        Attempts to use indexes to get candidate primary keys for a condition.

        Supports:
        - Equality conditions (==) on any indexed field
        - Range conditions (<, <=, >, >=) on SortedIndex fields
        - is_in conditions on any indexed field
        - AND conditions: uses first indexable sub-condition

        :param where: The Condition wrapper, or None.
        :return: Set of candidate PKs if index can be used, None otherwise.
        """
        if where is None:
            return None

        func = where.condition.func

        # Handle simple field conditions
        if isinstance(func, _FieldCondition):
            return self._search_index_for_field_condition(func)

        # Handle is_in conditions
        if isinstance(func, _IsInCondition):
            if func.field in self.indexes:
                return self.indexes[func.field].search_multi(func.values)
            return None

        # Handle compound AND conditions (lambda with closure)
        # Try to extract indexable conditions from AND
        return self._extract_indexed_pks_from_compound(where)

    def _search_index_for_field_condition(
        self, func: _FieldCondition
    ) -> Optional[set[Any]]:
        """
        Search index for a single field condition.

        :param func: The _FieldCondition to evaluate.
        :return: Set of candidate PKs if index can be used, None otherwise.
        """
        field = func.field
        value = func.value
        op = func.op

        if field not in self.indexes:
            return None

        index = self.indexes[field]

        # Equality - works with any index
        if op == operator.eq:
            return index.search(value)

        # Range queries - only work with indexes that support range
        if not index.supports_range:
            return None

        if op == operator.lt:
            return index.search_lt(value)
        if op == operator.le:
            return index.search_lte(value)
        if op == operator.gt:
            return index.search_gt(value)
        if op == operator.ge:
            return index.search_gte(value)

        return None

    def _extract_indexed_pks_from_compound(
        self, where: Condition
    ) -> Optional[set[Any]]:
        """
        Attempt to extract indexable conditions from compound AND/OR conditions.

        For AND conditions, finds the first indexable sub-condition and uses it.
        The remaining conditions will still be applied as filters.

        :param where: The compound Condition.
        :return: Set of candidate PKs if any sub-condition is indexable, None otherwise.
        """
        # Try to detect AND pattern by checking if func is a lambda that combines conditions
        # This is a heuristic approach - we check the closure for PredicateExpr objects
        func = where.condition.func
        if (
            not callable(func)
            or not hasattr(func, "__closure__")
            or func.__closure__ is None
        ):
            return None

        # Extract cell contents from closure
        for cell in func.__closure__:
            try:
                cell_contents = cell.cell_contents
                # Check if it's a PredicateExpr with indexable content
                from .condition import PredicateExpr

                if isinstance(cell_contents, PredicateExpr):
                    inner_func = cell_contents.func
                    if isinstance(inner_func, _FieldCondition):
                        result = self._search_index_for_field_condition(inner_func)
                        if result is not None:
                            return result
                    if isinstance(inner_func, _IsInCondition):
                        if inner_func.field in self.indexes:
                            return self.indexes[inner_func.field].search_multi(
                                inner_func.values
                            )
            except (ValueError, AttributeError):
                continue

        return None

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

    @overload
    def insert(
        self,
        record: Record,
        *,
        skip_validation: bool = False,
    ) -> Any: ...

    @overload
    def insert(
        self,
        record: List[Record],
        *,
        batch_size: Optional[int] = None,
        skip_validation: bool = False,
    ) -> List[Any]: ...

    def insert(
        self,
        record: Union[Record, List[Record]],
        *,
        batch_size: Optional[int] = None,
        skip_validation: bool = False,
    ) -> Union[Any, List[Any]]:
        """
        Insert one or more records into the table.

        Auto-assigns primary keys if not provided. Updates indexes automatically.

        :param record: A single record or a list of records to insert.
        :param batch_size: For bulk inserts, process records in batches of this size.
                          Useful for very large datasets. Default: no batching.
        :param skip_validation: Skip schema validation for trusted data. Default: False.
        :return: The primary key (single record) or list of primary keys (multiple).
        :raises DuplicateKeyError: If a record with the same primary key exists.
        :raises SchemaValidationError: If any record fails schema validation.

        For bulk inserts, the operation is atomic: if any record fails validation
        or has a duplicate key, all inserts are rolled back.
        """
        if isinstance(record, list):
            return self._insert_many(
                record, batch_size=batch_size, skip_validation=skip_validation
            )
        return self._insert_one(record, skip_validation=skip_validation)

    def _insert_one(self, record: Record, skip_validation: bool = False) -> Any:
        """Insert a single record."""
        logger.bind(table=self.table_name, op="INSERT").debug(
            f"[INSERT] Inserting record into '{self.table_name}'"
        )
        with self._lock.write_lock():
            if self.primary_key not in record:
                record[self.primary_key] = self._next_pk
                self._next_pk += 1
            else:
                key = record[self.primary_key]
                if key in self.records:
                    raise DuplicateKeyError(
                        f"Record with key '{key}' already exists in table '{self.table_name}'."
                    )
                if isinstance(key, int) and key >= self._next_pk:
                    self._next_pk = key + 1
            if self.schema is not None and not skip_validation:
                self.validate_record(record)
            pk = record[self.primary_key]
            self.records[pk] = record
            self._update_indexes_on_insert(record)
            self._dirty_pks.add(pk)
            self._deleted_pks.discard(pk)
        logger.bind(table=self.table_name, op="INSERT", pk=pk).info(
            "Record inserted into '{table}' (pk={pk})."
        )
        return pk

    def _insert_many(
        self,
        records: List[Record],
        batch_size: Optional[int] = None,
        skip_validation: bool = False,
    ) -> List[Any]:
        """
        Insert multiple records atomically.

        All records are inserted in a single lock acquisition. If any record
        fails validation or has a duplicate key, all inserts are rolled back.

        :param records: List of records to insert.
        :param batch_size: Process records in batches of this size for index updates.
        :param skip_validation: Skip schema validation for trusted data.
        """
        if not records:
            return []

        logger.bind(table=self.table_name, op="INSERT", count=len(records)).debug(
            f"[INSERT] Bulk inserting {len(records)} records into '{self.table_name}'"
        )

        inserted_pks: List[Any] = []
        with self._lock.write_lock():
            original_next_pk = self._next_pk

            try:
                # Phase 1: Validate all records and assign PKs
                for record in records:
                    # Assign PK if missing
                    if self.primary_key not in record:
                        record[self.primary_key] = self._next_pk
                        self._next_pk += 1
                    else:
                        key = record[self.primary_key]
                        if key in self.records or key in inserted_pks:
                            raise DuplicateKeyError(
                                f"Record with key '{key}' already exists in table '{self.table_name}'."
                            )
                        if isinstance(key, int) and key >= self._next_pk:
                            self._next_pk = key + 1

                    # Validate schema
                    if self.schema is not None and not skip_validation:
                        self.validate_record(record)

                    pk = record[self.primary_key]
                    inserted_pks.append(pk)

                # Phase 2: Insert all records (in batches if specified)
                effective_batch_size = batch_size or len(records)
                for batch_start in range(0, len(records), effective_batch_size):
                    batch_end = min(batch_start + effective_batch_size, len(records))
                    for i in range(batch_start, batch_end):
                        record = records[i]
                        pk = inserted_pks[i]
                        self.records[pk] = record
                        self._update_indexes_on_insert(record)
                        self._dirty_pks.add(pk)
                        self._deleted_pks.discard(pk)

            except Exception:
                # Rollback: remove any inserted records
                for pk in inserted_pks:
                    if pk in self.records:
                        self._update_indexes_on_delete(self.records[pk])
                        del self.records[pk]
                        self._dirty_pks.discard(pk)
                self._next_pk = original_next_pk
                raise

        logger.bind(table=self.table_name, op="INSERT", count=len(inserted_pks)).info(
            "Bulk inserted {count} records into '{table}'."
        )
        return inserted_pks

    def upsert(
        self,
        record: Record,
        on_conflict: Literal["update", "ignore", "error"] = "update",
    ) -> Tuple[Any, str]:
        """
        Insert a record or update it if it already exists.

        :param record: The record to insert or update.
        :param on_conflict: Strategy when primary key exists:
                           - "update": update the existing record (default)
                           - "ignore": do nothing, keep existing record
                           - "error": raise DuplicateKeyError
        :return: Tuple of (primary_key, action) where action is one of:
                "inserted", "updated", or "ignored".
        :raises DuplicateKeyError: If on_conflict="error" and record exists.
        :raises SchemaValidationError: If the record fails schema validation.
        """
        logger.bind(table=self.table_name, op="UPSERT").debug(
            f"[UPSERT] Upserting record into '{self.table_name}'"
        )
        with self._lock.write_lock():
            pk = record.get(self.primary_key)

            # No PK provided: always insert with auto-generated key
            if pk is None:
                record[self.primary_key] = self._next_pk
                pk = self._next_pk
                self._next_pk += 1
                if self.schema is not None:
                    self.validate_record(record)
                self.records[pk] = record
                self._update_indexes_on_insert(record)
                self._dirty_pks.add(pk)
                self._deleted_pks.discard(pk)
                action = "inserted"

            elif pk in self.records:
                # Conflict: record with this PK exists
                if on_conflict == "error":
                    raise DuplicateKeyError(
                        f"Record with key '{pk}' already exists in table '{self.table_name}'."
                    )
                if on_conflict == "ignore":
                    action = "ignored"
                else:
                    # on_conflict == "update"
                    old_record = self.records[pk].copy()
                    self.records[pk].update(record)
                    if self.schema is not None:
                        self.validate_record(self.records[pk])
                    self._update_indexes_on_update(pk, old_record, self.records[pk])
                    self._dirty_pks.add(pk)
                    action = "updated"

            else:
                # No conflict: insert new record
                if isinstance(pk, int) and pk >= self._next_pk:
                    self._next_pk = pk + 1
                if self.schema is not None:
                    self.validate_record(record)
                self.records[pk] = record
                self._update_indexes_on_insert(record)
                self._dirty_pks.add(pk)
                self._deleted_pks.discard(pk)
                action = "inserted"

        logger.bind(table=self.table_name, op="UPSERT", pk=pk, action=action).info(
            "Upsert completed on '{table}' (pk={pk}, action={action})."
        )
        return (pk, action)

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
        copy: bool = True,
        distinct: bool = False,
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
        :param copy: If True (default), return copies of records for thread safety.
                     Set to False for read-only use cases to reduce memory usage.
        :param distinct: If True, return only unique records (first occurrence preserved).
        :return: A list of matching records.
        """
        logger.bind(table=self.table_name, op="SELECT").debug(
            f"[SELECT] Querying '{self.table_name}' (columns={columns}, filtered={where is not None})"
        )
        with self._lock.read_lock():
            results: List[Record] = []
            candidate_records: List[Record]
            candidate_pks = self._get_indexed_candidate_pks(where)
            if candidate_pks is not None:
                candidate_records = [
                    self.records[pk] for pk in candidate_pks if pk in self.records
                ]
            else:
                candidate_records = list(self.records.values())
            # Filter (and optionally copy) records; copy ensures thread safety outside lock
            # Early termination: stop when we have enough records if no ORDER BY
            filtered_records: List[Record] = []
            needed = (
                (offset + limit) if (limit is not None and order_by is None) else None
            )
            for record in candidate_records:
                if where is None or where(record):
                    filtered_records.append(record.copy() if copy else record)
                    if needed is not None and len(filtered_records) >= needed:
                        break

        # Perform non-structural ops (ordering/projection) outside lock
        from ..query.order import order_records_with_limit
        from ..query.pager import slice_records
        from ..query.projection import deduplicate_records, project_records

        ordered = order_records_with_limit(filtered_records, order_by, limit, offset)
        sliced_records = slice_records(ordered, limit=limit, offset=offset)
        results = project_records(sliced_records, columns)
        if distinct:
            results = deduplicate_records(results)
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
            # Use index if available to narrow down candidates
            candidate_pks = self._get_indexed_candidate_pks(where)
            if candidate_pks is not None:
                candidate_items = [
                    (pk, self.records[pk]) for pk in candidate_pks if pk in self.records
                ]
            else:
                candidate_items = list(self.records.items())

            try:
                for key, record in candidate_items:
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
            except Exception:
                for key in updated_keys:
                    self.records[key] = backup[key]
                raise

            for pk in updated_keys:
                self._update_indexes_on_update(pk, backup[pk], self.records[pk])
            # Track for incremental backup
            self._dirty_pks.update(updated_keys)
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
            # Use index if available to narrow down candidates
            candidate_pks = self._get_indexed_candidate_pks(where)
            if candidate_pks is not None:
                candidate_items = [
                    (pk, self.records[pk]) for pk in candidate_pks if pk in self.records
                ]
            else:
                candidate_items = list(self.records.items())

            keys_to_delete = [
                key for key, record in candidate_items if where is None or where(record)
            ]
            if not keys_to_delete:
                raise RecordNotFoundError(
                    f"No records match the deletion criteria in table '{self.table_name}'."
                )
            for key in keys_to_delete:
                record = self.records[key]
                self._update_indexes_on_delete(record)
                del self.records[key]
            # Track for incremental backup
            self._deleted_pks.update(keys_to_delete)
            self._dirty_pks.difference_update(keys_to_delete)
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

    # ──────────────────────────────────────────────────────────────────────────
    # Aggregation support
    # ──────────────────────────────────────────────────────────────────────────

    def aggregate(
        self,
        where: Optional[Condition] = None,
        group_by: Optional[Union[str, List[str]]] = None,
        **aggregations: Any,
    ) -> Union[Dict[str, Any], List[Record]]:
        """
        Compute aggregations on table records.

        Supports aggregation classes: Count, Sum, Avg, Min, Max.

        :param where: Optional condition to filter records before aggregating.
        :param group_by: Optional field or list of fields to group by.
        :param aggregations: Keyword arguments mapping result names to Agg instances
                            (e.g., total=Sum("salary"), avg_age=Avg("age")).
        :return: If group_by is None, returns a dict with aggregation results.
                If group_by is provided, returns a list of records with group
                keys and aggregation values.

        Examples:
            from dictdb import Count, Sum, Avg, Max

            # Count all active users
            users.aggregate(where=Condition(users.active == True), count=Count())
            # Returns: {"count": 42}

            # Get salary stats by department
            users.aggregate(
                group_by="department",
                count=Count(),
                avg_salary=Avg("salary"),
                max_salary=Max("salary"),
            )
            # Returns: [{"department": "IT", "count": 10, "avg_salary": 75000, ...}, ...]
        """
        from ..query.aggregate import (
            Agg,
            compute_aggregations,
            group_and_aggregate,
        )

        # Validate aggregations
        agg_dict: Dict[str, Agg] = {}
        for result_key, agg in aggregations.items():
            if not isinstance(agg, Agg):
                raise TypeError(
                    f"Expected Agg instance for '{result_key}', got {type(agg).__name__}"
                )
            agg_dict[result_key] = agg

        # Get filtered records
        with self._lock.read_lock():
            if where is not None:
                candidate_pks = self._get_indexed_candidate_pks(where)
                if candidate_pks is not None:
                    records = [
                        self.records[pk].copy()
                        for pk in candidate_pks
                        if pk in self.records and where(self.records[pk])
                    ]
                else:
                    records = [
                        rec.copy() for rec in self.records.values() if where(rec)
                    ]
            else:
                records = [rec.copy() for rec in self.records.values()]

        # Compute aggregations
        if group_by is not None:
            return group_and_aggregate(records, group_by, agg_dict)
        else:
            return compute_aggregations(records, agg_dict)

    # ──────────────────────────────────────────────────────────────────────────
    # Incremental backup support
    # ──────────────────────────────────────────────────────────────────────────

    def has_changes(self) -> bool:
        """
        Returns True if there are uncommitted changes since the last backup.

        :return: True if dirty or deleted records exist.
        """
        with self._lock.read_lock():
            return bool(self._dirty_pks or self._deleted_pks)

    def get_dirty_records(self) -> List[Record]:
        """
        Returns copies of all records that have been inserted or updated
        since the last backup.

        :return: List of dirty record copies.
        """
        with self._lock.read_lock():
            return [
                self.records[pk].copy() for pk in self._dirty_pks if pk in self.records
            ]

    def get_deleted_pks(self) -> List[Any]:
        """
        Returns the primary keys of records deleted since the last backup.

        :return: List of deleted primary keys.
        """
        with self._lock.read_lock():
            return list(self._deleted_pks)

    def clear_dirty_tracking(self) -> None:
        """
        Clears the dirty and deleted tracking sets.
        Called after a successful backup to reset change tracking.
        """
        with self._lock.write_lock():
            self._dirty_pks.clear()
            self._deleted_pks.clear()
