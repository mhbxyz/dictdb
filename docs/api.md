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
db.create_table(table_name: str, primary_key: str = "id", schema: dict = None) -> None
```

Creates a new table.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `table_name` | `str` | - | Name of the table |
| `primary_key` | `str` | `"id"` | Field to use as primary key |
| `schema` | `dict` | `None` | Optional schema for validation |

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

---

## Table

Represents a single table with CRUD operations.

### Methods

#### insert

```python
table.insert(record: dict) -> Any
```

Inserts a record, returns the primary key.

| Parameter | Type | Description |
|-----------|------|-------------|
| `record` | `dict` | Record to insert |

**Raises:**

- `DuplicateKeyError` if primary key exists
- `SchemaValidationError` if record fails validation

#### select

```python
table.select(
    columns: list | dict = None,
    where: Condition = None,
    order_by: str | list = None,
    limit: int = None,
    offset: int = 0,
    copy: bool = True
) -> list[dict]
```

Retrieves matching records.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `columns` | `list \| dict` | `None` | Column projection |
| `where` | `Condition` | `None` | Filter condition |
| `order_by` | `str \| list` | `None` | Sort order |
| `limit` | `int` | `None` | Max records |
| `offset` | `int` | `0` | Records to skip |
| `copy` | `bool` | `True` | Return copies |

#### update

```python
table.update(changes: dict, where: Condition = None) -> int
```

Updates matching records, returns count.

**Raises:**

- `RecordNotFoundError` if no records match
- `SchemaValidationError` if changes fail validation

#### delete

```python
table.delete(where: Condition = None) -> int
```

Deletes matching records, returns count.

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

---

## Condition

Wraps a predicate expression for use in queries.

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
# Create from field comparison
Condition(table.field == value)

# Combine conditions
Condition(expr1 & expr2)  # AND
Condition(expr1 | expr2)  # OR
Condition(~expr)          # NOT
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
table.field.startswith("prefix") # String prefix
table.field.endswith("suffix")   # String suffix
table.field.contains("substr")   # String contains
```

### Logical

```python
(expr1) & (expr2)  # AND
(expr1) | (expr2)  # OR
~(expr)            # NOT
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

## Exceptions

```python
from dictdb import (
    DuplicateKeyError,
    DuplicateTableError,
    RecordNotFoundError,
    TableNotFoundError,
    SchemaValidationError,
)
```

| Exception | Description |
|-----------|-------------|
| `DuplicateKeyError` | Primary key already exists |
| `DuplicateTableError` | Table name already exists |
| `RecordNotFoundError` | No records match criteria |
| `TableNotFoundError` | Table doesn't exist |
| `SchemaValidationError` | Record fails schema validation |

All inherit from `DictDBError`.
