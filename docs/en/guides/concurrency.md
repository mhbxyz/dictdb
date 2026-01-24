# Concurrency

DictDB is thread-safe through reader-writer locks on each table.

## Thread Safety Model

Each `Table` has an independent `RWLock` that:

- Allows multiple concurrent readers
- Ensures exclusive access for writers
- Prevents read-write and write-write conflicts

## Read Operations

Multiple threads can read simultaneously:

```python
import threading
from dictdb import DictDB, Condition

db = DictDB()
db.create_table("users")
users = db.get_table("users")

# Populate data
for i in range(1000):
    users.insert({"name": f"User {i}"})

def reader(thread_id):
    # Multiple readers can run concurrently
    results = users.select(where=Condition(users.name.startswith("User 1")))
    print(f"Thread {thread_id}: found {len(results)} records")

# Start multiple reader threads
threads = [threading.Thread(target=reader, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Write Operations

Writers get exclusive access:

```python
def writer(thread_id):
    # Only one writer at a time
    users.insert({"name": f"New User {thread_id}"})

def reader(thread_id):
    # Readers wait for writers to complete
    count = users.count()
    print(f"Thread {thread_id}: {count} total records")

# Mixed read/write workload
threads = []
for i in range(5):
    threads.append(threading.Thread(target=writer, args=(i,)))
    threads.append(threading.Thread(target=reader, args=(i,)))

for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Atomic Operations

All CRUD operations are atomic:

### Insert

```python
# Thread-safe: auto-increment is protected
pk = users.insert({"name": "Alice"})  # Returns unique PK
```

### Update

```python
# Atomic update with validation
# If validation fails, all changes are rolled back
users.update(
    {"status": "active"},
    where=Condition(users.role == "admin")
)
```

### Delete

```python
# Atomic delete of matching records
users.delete(where=Condition(users.status == "inactive"))
```

## Record Copying

By default, `select` returns copies of records:

```python
# Safe: returns copies
results = users.select()
results[0]["name"] = "Modified"  # Does not affect database

# Unsafe: returns references (faster but not for modification)
results = users.select(copy=False)
# Do not modify these records outside the lock!
```

## Per-Table Isolation

Different tables can be accessed concurrently:

```python
# users and products have separate locks
def update_user():
    users.update({"last_login": now()}, where=Condition(users.id == 1))

def update_product():
    products.update({"stock": 99}, where=Condition(products.sku == "ABC"))

# These can run concurrently without blocking each other
t1 = threading.Thread(target=update_user)
t2 = threading.Thread(target=update_product)
t1.start()
t2.start()
```

## Long-Running Queries

For long-running read operations, consider:

```python
# Get a snapshot for processing
with users._lock.read_lock():
    snapshot = users.copy()  # Returns dict of {pk: record_copy}

# Process snapshot outside the lock
for pk, record in snapshot.items():
    process(record)  # Other threads can write while processing
```

## Deadlock Prevention

DictDB's design prevents deadlocks:

- Single lock per table
- No cross-table locking
- Locks are always released after operations

However, your application code should avoid:

```python
# Potential deadlock pattern (in your code, not DictDB)
def bad_pattern():
    with external_lock:
        users.insert(...)  # DictDB acquires its lock inside yours

def another_bad_pattern():
    users.select(...)  # DictDB lock acquired
    # If callback tries to acquire external_lock held by bad_pattern...
```

## Async Compatibility

For async applications, use async persistence methods:

```python
import asyncio

async def save_periodically():
    while True:
        await asyncio.sleep(60)
        await db.async_save("backup.json", file_format="json")

# Runs save in thread pool, doesn't block event loop
```

## Best Practices

1. **Keep operations short**: Long-held locks block other threads
2. **Use `copy=False` carefully**: Only for read-only access
3. **Batch updates**: Multiple updates in one call are faster than many single updates
4. **Consider table design**: High-contention tables may benefit from partitioning

## Example: Concurrent Web Application

```python
from dictdb import DictDB, Condition, BackupManager
import threading

# Shared database
db = DictDB()
db.create_table("sessions", primary_key="session_id")
db.create_table("events", primary_key="event_id")

sessions = db.get_table("sessions")
events = db.get_table("events")

# Indexes for common queries
sessions.create_index("user_id")
events.create_index("session_id")

# Background backup
backup = BackupManager(db, "./backups", backup_interval=60)
backup.start()

def handle_request(session_id, user_id, action):
    """Called from multiple web worker threads"""

    # Read session (concurrent with other reads)
    existing = sessions.select(where=Condition(sessions.session_id == session_id))

    if not existing:
        # Create session (exclusive access)
        sessions.insert({"session_id": session_id, "user_id": user_id})

    # Log event (different table, no contention with sessions)
    events.insert({"session_id": session_id, "action": action})

# Cleanup background thread
def cleanup_old_sessions():
    while True:
        threading.Event().wait(3600)  # Every hour
        sessions.delete(where=Condition(sessions.last_active < one_hour_ago()))
```
