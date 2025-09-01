# Logging

DictDB integrates with Loguru for detailed logging.

## Configure Loguru

```python
from dictdb import configure_logging, DictDB

configure_logging(level="DEBUG", console=True, logfile="dictdb.log")
db = DictDB()
```

## Log Levels and Sinks

- Console: `console=True` logs to stdout.
- File: `logfile="yourfile.log"` writes logs to a file.
- Levels: "DEBUG", "INFO", "WARNING", etc.

