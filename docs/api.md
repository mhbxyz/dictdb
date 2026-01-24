# API Reference

## DictDB

The main database class that manages tables.

```python
from dictdb import DictDB
```

### Constructor

```python
DictDB()
```

Creates an empty database instance.

### Methods

#### create_table

```python
db.create_table(table_name: str, primary_key: str = "id") -> None
```

Creates a new table.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `table_name` | `str` | - | Name of the table |
| `primary_key` | `str` | `"id"` | Field to use as primary key |

**Note:** To use schema validation, create a `Table` directly with the `schema` parameter and register it via `db.tables[name] = table`.

**Raises:** `DuplicateTableError` if table exists.

#### drop_table

```python
db.drop_table(table_name: str) -> None
```

Removes a table from the database.

**Raises:** `TableNotFoundError` if table doesn't exist.

#### get_table

```python
db.get_table(table_name: str) -> Table
```

Returns a table reference.

**Raises:** `TableNotFoundError` if table doesn't exist.

#### list_tables

```python
db.list_tables() -> list[str]
```

Returns list of all table names.

#### save

```python
db.save(filename: str | Path, file_format: str) -> None
```

Saves database to disk.

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | `str \| Path` | Output file path |
| `file_format` | `str` | `"json"` or `"pickle"` |

#### load (classmethod)

```python
DictDB.load(filename: str | Path, file_format: str) -> DictDB
```

Loads database from disk.

#### async_save

```python
await db.async_save(filename: str | Path, file_format: str) -> None
```

Async version of `save()`.

#### async_load (classmethod)

```python
await DictDB.async_load(filename: str | Path, file_format: str) -> DictDB
```

Async version of `load()`.

#### import_csv

```python
db.import_csv(
    filepath: str | Path,
    table_name: str,
    *,
    primary_key: str = "id",
    delimiter: str = ",",
    has_header: bool = True,
    encoding: str = "utf-8",
    schema: dict[str, type] = None,
    infer_types: bool = True,
    skip_validation: bool = False
) -> int
```

Imports data from a CSV file into a new table.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | `str \| Path` | - | Path to the CSV file |
| `table_name` | `str` | - | Name for the new table |
| `primary_key` | `str` | `"id"` | Field to use as primary key |
| `delimiter` | `str` | `","` | CSV field delimiter |
| `has_header` | `bool` | `True` | Whether first row is header |
| `encoding` | `str` | `"utf-8"` | File encoding |
| `schema` | `dict[str, type]` | `None` | Type conversion schema |
| `infer_types` | `bool` | `True` | Auto-detect column types |
| `skip_validation` | `bool` | `False` | Skip schema validation |

**Returns:** Number of records imported.

**Raises:** `DuplicateTableError` if table already exists.

See the [CSV Guide](guides/csv.md) for detailed usage.

---

## Table

Represents a single table with CRUD operations.

### Methods

#### insert

```python
table.insert(record: dict) -> Any
table.insert(record: list[dict], batch_size: int = None, skip_validation: bool = False) -> list[Any]
```

Inserts one or more records, returns the primary key(s).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `record` | `dict \| list[dict]` | - | Record or list of records to insert |
| `batch_size` | `int` | `None` | For bulk inserts, process in batches of this size |
| `skip_validation` | `bool` | `False` | Skip schema validation for trusted data |

For bulk inserts, the operation is atomic: if any record fails validation or has a duplicate key, all inserts are rolled back.

**Raises:**

- `DuplicateKeyError` if primary key exists
- `SchemaValidationError` if record fails validation

#### upsert

```python
table.upsert(record: dict, on_conflict: str = "update") -> tuple[Any, str]
```

Inserts a record or handles conflict if primary key exists.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `record` | `dict` | - | Record to insert or update |
| `on_conflict` | `str` | `"update"` | Conflict strategy: `"update"`, `"ignore"`, or `"error"` |

**Returns:** Tuple of `(primary_key, action)` where action is `"inserted"`, `"updated"`, or `"ignored"`.

**Conflict strategies:**

- `"update"` - Update existing record with new values (default)
- `"ignore"` - Keep existing record, do nothing
- `"error"` - Raise `DuplicateKeyError`

**Raises:**

- `DuplicateKeyError` if `on_conflict="error"` and record exists
- `SchemaValidationError` if record fails validation

#### select

```python
table.select(
    columns: list | dict = None,
    where: Condition | PredicateExpr = None,
    order_by: str | list = None,
    limit: int = None,
    offset: int = 0,
    copy: bool = True,
    distinct: bool = False
) -> list[dict]
```

Retrieves matching records.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `columns` | `list \| dict` | `None` | Column projection |
| `where` | `Condition \| PredicateExpr` | `None` | Filter condition (Condition wrapper optional) |
| `order_by` | `str \| list` | `None` | Sort order |
| `limit` | `int` | `None` | Max records |
| `offset` | `int` | `0` | Records to skip |
| `copy` | `bool` | `True` | Return copies |
| `distinct` | `bool` | `False` | Return only unique records |

#### update

```python
table.update(changes: dict, where: Condition | PredicateExpr = None) -> int
```

Updates matching records, returns count. The `Condition` wrapper is optional.

**Raises:**

- `RecordNotFoundError` if no records match
- `SchemaValidationError` if changes fail validation

#### delete

```python
table.delete(where: Condition | PredicateExpr = None) -> int
```

Deletes matching records, returns count. The `Condition` wrapper is optional.

**Raises:** `RecordNotFoundError` if no records match.

#### create_index

```python
table.create_index(field: str, index_type: str = "hash") -> None
```

Creates an index on a field.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field` | `str` | - | Field to index |
| `index_type` | `str` | `"hash"` | `"hash"` or `"sorted"` |

### Introspection

```python
table.count() -> int              # Number of records
table.size() -> int               # Alias for count()
table.columns() -> list[str]      # Column names
table.primary_key_name() -> str   # Primary key field
table.indexed_fields() -> list[str]  # Indexed fields
table.has_index(field: str) -> bool  # Check index exists
table.schema_fields() -> list[str]   # Schema fields
```

### Other Methods

```python
table.all() -> list[dict]         # All records as copies
table.copy() -> dict[Any, dict]   # Dict of pk -> record copy
```

#### export_csv

```python
table.export_csv(
    filepath: str | Path,
    *,
    records: list[dict] = None,
    columns: list[str] = None,
    where: Condition | PredicateExpr = None,
    delimiter: str = ",",
    encoding: str = "utf-8"
) -> int
```

Exports records to a CSV file.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | `str \| Path` | - | Output CSV file path |
| `records` | `list[dict]` | `None` | Pre-computed records to export |
| `columns` | `list[str]` | `None` | Columns to include (and their order) |
| `where` | `Condition \| PredicateExpr` | `None` | Filter condition |
| `delimiter` | `str` | `","` | CSV field delimiter |
| `encoding` | `str` | `"utf-8"` | File encoding |

**Returns:** Number of records written.

See the [CSV Guide](guides/csv.md) for detailed usage.

---

## Condition

Wraps a predicate expression for use in queries. **The `Condition` wrapper is optional** - you can pass `PredicateExpr` directly to `where=` parameters.

```python
from dictdb import Condition
```

### Constructor

```python
Condition(predicate_expr)
```

Wraps a `PredicateExpr` created from field comparisons.

### Usage

```python
# Recommended: pass PredicateExpr directly (no wrapper needed)
table.select(where=table.field == value)

# Also works: explicit Condition wrapper
table.select(where=Condition(table.field == value))
```

---

## Logical Functions

Combine conditions using readable functions.

```python
from dictdb import And, Or, Not
```

### And

```python
And(*conditions) -> PredicateExpr
```

Returns a condition that is True only if **all** operands are True.

```python
# Two conditions
table.select(where=And(table.age >= 18, table.active == True))

# Multiple conditions
table.select(where=And(table.dept == "IT", table.active == True, table.level >= 3))
```

### Or

```python
Or(*conditions) -> PredicateExpr
```

Returns a condition that is True if **any** operand is True.

```python
# Match multiple values
table.select(where=Or(table.dept == "IT", table.dept == "HR", table.dept == "Sales"))
```

### Not

```python
Not(condition) -> PredicateExpr
```

Returns a condition that is True when the operand is False.

```python
table.select(where=Not(table.status == "inactive"))
```

### Combining Functions

```python
# Complex nested conditions
table.select(where=And(
    Or(table.dept == "IT", table.dept == "Engineering"),
    table.salary >= 70000,
    Not(table.status == "inactive")
))
```

### Alternative: Symbolic Operators

The `&`, `|`, `~` operators are also supported but require careful use of parentheses:

```python
table.select(where=(table.age >= 18) & (table.active == True))  # AND
table.select(where=(table.dept == "IT") | (table.dept == "HR"))  # OR
table.select(where=~(table.status == "inactive"))                # NOT
```

---

## Field Operators

Accessed via table attribute access: `table.field_name`

### Comparison

```python
table.field == value    # Equality
table.field != value    # Inequality
table.field < value     # Less than
table.field <= value    # Less than or equal
table.field > value     # Greater than
table.field >= value    # Greater than or equal
```

### Special Methods

```python
table.field.is_in([v1, v2, v3])  # IN operator
table.field.between(low, high)   # Inclusive range (low <= field <= high)
table.field.like("A%")           # SQL LIKE pattern (% = any, _ = one char)
table.field.startswith("prefix") # String prefix
table.field.endswith("suffix")   # String suffix
table.field.contains("substr")   # String contains
table.field.is_null()            # Check if None or missing
table.field.is_not_null()        # Check if not None
```

### Case-Insensitive Methods

```python
table.field.iequals("value")     # Case-insensitive equality
table.field.icontains("substr")  # Case-insensitive contains
table.field.istartswith("pre")   # Case-insensitive prefix
table.field.iendswith("suf")     # Case-insensitive suffix
table.field.ilike("A%")          # Case-insensitive LIKE
```

### Logical

Use `And`, `Or`, `Not` functions (recommended) or symbolic operators:

```python
And(expr1, expr2)  # AND (preferred)
Or(expr1, expr2)   # OR (preferred)
Not(expr)          # NOT (preferred)

(expr1) & (expr2)  # AND (alternative)
(expr1) | (expr2)  # OR (alternative)
~(expr)            # NOT (alternative)
```

---

## BackupManager

Automatic backup manager.

```python
from dictdb import BackupManager
```

### Constructor

```python
BackupManager(
    db: DictDB,
    backup_dir: str | Path,
    backup_interval: int = 300,
    file_format: str = "json",
    min_backup_interval: float = 5.0,
    on_backup_failure: Callable = None,
    incremental: bool = False,
    max_deltas_before_full: int = 10
)
```

### Methods

```python
backup.start() -> None        # Start background thread
backup.stop() -> None         # Stop background thread
backup.backup_now() -> None   # Immediate backup
backup.backup_full() -> None  # Force full backup
backup.backup_delta() -> None # Force delta backup
backup.notify_change() -> None  # Trigger backup (debounced)
```

### Properties

```python
backup.consecutive_failures -> int  # Failure count
backup.deltas_since_full -> int     # Delta count
```

---

## Logging

```python
from dictdb import logger, configure_logging
```

### configure_logging

```python
configure_logging(
    level: str = "INFO",
    console: bool = True,
    logfile: str = None,
    json: bool = False,
    sample_debug_every: int = None
) -> None
```

### logger

Global logger instance with methods:

```python
logger.debug(msg, **kwargs)
logger.info(msg, **kwargs)
logger.warning(msg, **kwargs)
logger.error(msg, **kwargs)
logger.critical(msg, **kwargs)
logger.bind(**kwargs) -> BoundLogger
logger.add(sink, level, serialize, filter) -> int
logger.remove() -> None
```

---

## Aggregations

SQL-like aggregation functions for query results. See the [Aggregation Guide](guides/aggregations.md) for detailed usage.

```python
from dictdb import Count, Sum, Avg, Min, Max
```

| Class | Description |
|-------|-------------|
| `Count(field=None)` | Count records or non-None values |
| `Sum(field)` | Sum of numeric values |
| `Avg(field)` | Average of numeric values |
| `Min(field)` | Minimum value |
| `Max(field)` | Maximum value |

---

## Version

```python
from dictdb import __version__
```

The installed package version string (e.g., `"1.2.3"`).

---

## Exceptions

```python
from dictdb import (
    DictDBError,
    DuplicateKeyError,
    DuplicateTableError,
    RecordNotFoundError,
    TableNotFoundError,
    SchemaValidationError,
)
```

| Exception | Description |
|-----------|-------------|
| `DictDBError` | Base exception for all dictdb errors |
| `DuplicateKeyError` | Primary key already exists |
| `DuplicateTableError` | Table name already exists |
| `RecordNotFoundError` | No records match criteria |
| `TableNotFoundError` | Table doesn't exist |
| `SchemaValidationError` | Record fails schema validation |

All exceptions inherit from `DictDBError`.
