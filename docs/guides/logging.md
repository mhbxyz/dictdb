# Logging

DictDB integrates with Loguru for detailed logging. You can emit human-friendly text logs or structured JSON logs, and include bound context (table, operation, counts) in messages.

## Configure Logging

```python
from dictdb import configure_logging, DictDB

# Text logs to console and file
configure_logging(level="DEBUG", console=True, logfile="dictdb.log")

# JSON logs (structured) to file
configure_logging(level="INFO", console=False, logfile="dictdb.jsonl", json=True)

# Sample DEBUG logs: only 1 in 10 DEBUG messages
configure_logging(level="DEBUG", console=True, sample_debug_every=10)

db = DictDB()
```

## Log Levels and Sinks

- Console: `console=True` logs to stdout.
- File: `logfile="yourfile.log"` writes logs to a file.
- Levels: "DEBUG", "INFO", "WARNING", etc.
- JSON: `json=True` enables `serialize=True` in Loguru for machine-readable logs.

## Structured Context

Table and DB operations bind structured context, visible via `{extra}` in text formats and as fields in JSON logs:

- Table ops: `table`, `op` (INSERT/SELECT/UPDATE/DELETE/INDEX), and relevant fields (e.g., `pk`, `count`, `field`, `index_type`).
- DB ops: `component="DictDB"`, `op` (CREATE_TABLE/DROP_TABLE/SAVE/LOAD), counts (`tables`, `records`), `path`, `format`.

Example JSON line:

```json
{"time": "...", "level": "INFO", "message": "Updated 2 record(s) in 'users'.", "table": "users", "op": "UPDATE", "count": 2}
```

