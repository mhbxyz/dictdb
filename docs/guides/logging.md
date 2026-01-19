# Logging

DictDB includes a built-in logging system with a loguru-compatible API.

## Quick Start

```python
from dictdb import configure_logging

# Enable info-level logging to console
configure_logging(level="INFO", console=True)
```

## Configuration

```python
configure_logging(
    # Minimum log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    level="INFO",

    # Log to stdout (default: True)
    console=True,

    # Log to file (optional)
    logfile="dictdb.log",

    # JSON output format (default: False)
    json=False,

    # Sample DEBUG messages: log 1 out of every N (optional)
    sample_debug_every=10,
)
```

## Log Levels

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed operation info (queries, index usage) |
| `INFO` | Normal operations (inserts, updates, saves) |
| `WARNING` | Potential issues |
| `ERROR` | Operation failures |
| `CRITICAL` | Severe errors |

## Output Format

### Console (colored)

```
2024-01-15 10:30:45.123 | INFO     | component=DictDB op=INSERT table=users pk=1 | Record inserted
```

### JSON

```json
{
  "time": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "message": "Record inserted",
  "extra": {"component": "DictDB", "op": "INSERT", "table": "users", "pk": 1}
}
```

## Direct Logger Access

```python
from dictdb import logger

# Direct logging
logger.info("Custom message")
logger.debug("Debug info")
logger.warning("Warning message")
logger.error("Error occurred")

# Contextual logging with bind()
log = logger.bind(component="MyApp", user_id=123)
log.info("User action performed")
```

## Custom Handlers

```python
from dictdb import logger
import sys

# Remove default handlers
logger.remove()

# Add custom stdout handler
logger.add(
    sink=sys.stdout,
    level="INFO",
    serialize=False,  # Human-readable
)

# Add file handler with JSON
logger.add(
    sink="app.log",
    level="DEBUG",
    serialize=True,  # JSON format
)

# Add custom function handler
def my_handler(message: str):
    # Send to external service, etc.
    print(f"CUSTOM: {message}")

logger.add(sink=my_handler, level="ERROR")
```

## Filtering

```python
# Filter function
def only_errors(record):
    return record["level"].name in ("ERROR", "CRITICAL")

logger.add(
    sink="errors.log",
    level="DEBUG",
    filter=only_errors,
)
```

## Debug Sampling

Reduce DEBUG log volume in production:

```python
# Log only 1 out of every 100 DEBUG messages
configure_logging(
    level="DEBUG",
    sample_debug_every=100,
)
```

## What Gets Logged

### Database Operations

```
INFO  | component=DictDB | Initialized an empty DictDB instance.
INFO  | component=DictDB op=CREATE_TABLE table=users pk=id | Created table 'users'
INFO  | component=DictDB op=DROP_TABLE table=users | Dropped table 'users'
```

### Table Operations

```
DEBUG | table=users op=INSERT | Inserting record into 'users'
INFO  | table=users op=INSERT pk=1 | Record inserted into 'users' (pk=1)
INFO  | table=users op=UPDATE count=3 | Updated 3 record(s) in 'users'
INFO  | table=users op=DELETE count=1 | Deleted 1 record(s) from 'users'
```

### Index Operations

```
INFO  | table=users op=INDEX field=email index_type=hash | Index created on field 'email'
```

### Persistence

```
INFO  | component=DictDB op=SAVE tables=2 records=100 format=json path=data.json | Saving database
INFO  | component=DictDB op=LOAD path=data.json format=json tables=2 records=100 | Loaded database
```

### Backup Manager

```
INFO  | Starting automatic backup manager.
INFO  | Performing full backup to dictdb_backup_123.json
INFO  | Delta backup saved successfully (3/10 deltas)
ERROR | Backup failed (2 consecutive): Permission denied
```

## Example: Production Setup

```python
from dictdb import DictDB, configure_logging

# Configure for production
configure_logging(
    level="INFO",
    console=True,
    logfile="/var/log/dictdb/app.log",
    json=True,  # Structured logging for log aggregation
)

# Application
db = DictDB()
db.create_table("events")
# All operations are now logged
```

## Disabling Logging

```python
from dictdb import logger

# Remove all handlers
logger.remove()

# Or configure with no outputs
configure_logging(level="CRITICAL", console=False)
```
