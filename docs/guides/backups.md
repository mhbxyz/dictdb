# Backups

The `BackupManager` provides automatic periodic and incremental backups for DictDB.

## Basic Usage

```python
from dictdb import DictDB, BackupManager

db = DictDB()
db.create_table("users")

# Create backup manager
backup = BackupManager(
    db=db,
    backup_dir="./backups",
    backup_interval=300,  # 5 minutes
    file_format="json"
)

# Start automatic backups
backup.start()

# ... your application runs ...

# Stop when done
backup.stop()
```

## Configuration Options

```python
backup = BackupManager(
    db=db,
    backup_dir="./backups",

    # Periodic backup interval in seconds (default: 300)
    backup_interval=300,

    # File format: "json" or "pickle" (default: "json")
    file_format="json",

    # Minimum interval between change-triggered backups (default: 5.0)
    min_backup_interval=5.0,

    # Callback for backup failures
    on_backup_failure=handle_failure,

    # Enable incremental backups (default: False)
    incremental=False,

    # Deltas before forcing full backup (default: 10)
    max_deltas_before_full=10,
)
```

## Manual Backups

```python
# Immediate backup
backup.backup_now()

# Force full backup
backup.backup_full()

# Force delta backup (incremental mode)
backup.backup_delta()
```

## Change Notification

Trigger a backup after significant changes:

```python
# Notify of significant change
# Respects min_backup_interval to avoid excessive I/O
backup.notify_change()
```

## Incremental Backups

Incremental mode saves only changes since the last backup:

```python
backup = BackupManager(
    db=db,
    backup_dir="./backups",
    incremental=True,
    max_deltas_before_full=10,
)
```

**How it works:**

1. Delta files contain only inserted, updated, and deleted records
2. After `max_deltas_before_full` deltas, a full backup is created
3. Full backups reset the delta counter

**Delta file structure:**

```json
{
  "type": "delta",
  "timestamp": 1234567890.123456,
  "tables": {
    "users": {
      "upserts": [
        {"id": 1, "name": "Alice"}
      ],
      "deletes": [2, 3]
    }
  }
}
```

## Failure Handling

Handle backup failures with a callback:

```python
def handle_failure(error: Exception, consecutive_failures: int):
    print(f"Backup failed ({consecutive_failures}x): {error}")
    if consecutive_failures >= 3:
        send_alert("Backup system failing!")

backup = BackupManager(
    db=db,
    backup_dir="./backups",
    on_backup_failure=handle_failure,
)
```

Monitor failure count:

```python
if backup.consecutive_failures > 0:
    print(f"Warning: {backup.consecutive_failures} consecutive failures")
```

## Backup File Naming

Files are named with microsecond-precision timestamps:

- Full backups: `dictdb_backup_1234567890_123456.json`
- Delta backups: `dictdb_delta_1234567890_123456.json`

## Status Monitoring

```python
# Check consecutive failures
backup.consecutive_failures  # 0

# Check deltas since last full backup (incremental mode)
backup.deltas_since_full  # 3
```

## Example: Production Setup

```python
import logging
from pathlib import Path
from dictdb import DictDB, BackupManager

# Configure paths
BACKUP_DIR = Path("./data/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Initialize database
db = DictDB()
db.create_table("events", primary_key="event_id")

# Failure handler with logging
def on_failure(error: Exception, count: int):
    logging.error(f"Backup failed ({count}x): {error}")
    if count >= 5:
        logging.critical("Multiple backup failures - check disk space!")

# Create backup manager
backup = BackupManager(
    db=db,
    backup_dir=BACKUP_DIR,
    backup_interval=60,  # Every minute
    file_format="json",
    min_backup_interval=10.0,
    on_backup_failure=on_failure,
    incremental=True,
    max_deltas_before_full=20,
)

# Start backups
backup.start()

try:
    # Application logic
    events = db.get_table("events")

    # After batch operations, trigger backup
    for i in range(100):
        events.insert({"event_id": i, "type": "click"})
    backup.notify_change()

finally:
    # Ensure final backup on shutdown
    backup.backup_full()
    backup.stop()
```

## Restoring from Backups

Load the most recent full backup:

```python
from pathlib import Path

backup_dir = Path("./backups")

# Find latest full backup
full_backups = sorted(backup_dir.glob("dictdb_backup_*.json"))
if full_backups:
    latest = full_backups[-1]
    db = DictDB.load(str(latest), file_format="json")
```

For incremental backups, apply deltas in order:

```python
from dictdb.storage.persist import apply_delta

# Load base backup
db = DictDB.load("dictdb_backup_base.json", file_format="json")

# Apply deltas in chronological order
for delta_file in sorted(backup_dir.glob("dictdb_delta_*.json")):
    affected = apply_delta(db, delta_file)
    print(f"Applied {delta_file.name}: {affected} records")
```
