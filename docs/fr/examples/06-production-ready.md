# Prêt pour la Production

*La saga de TechFlow SARL continue : du prototype au déploiement*

---

Après avoir terminé avec succès la migration des données historiques, l'équipe de TechFlow SARL était prête pour l'étape suivante. Sarah convoqua une réunion de planification technique.

« Notre prototype fonctionne parfaitement, » dit-elle. « Mais avant de déployer en production, nous devons nous assurer qu'il est robuste, performant et capable de gérer les incidents. »

Lucas, l'architecte systèmes, prit la parole. « Nous avons besoin de sauvegardes automatiques, d'une gestion appropriée de la concurrence et d'une observabilité complète. Sans parler de l'optimisation des performances. »

« Exactement, » acquiesça Sarah. « Commençons par le début. »

## Configuration du BackupManager

« La première règle de la production : toujours avoir des sauvegardes, » rappela Lucas.

### Configuration de Base

```python
from pathlib import Path
from dictdb import DictDB, BackupManager

# Initialize the database
db = DictDB()
db.create_table("users", primary_key="id")
db.create_table("sessions", primary_key="session_id")
db.create_table("events", primary_key="event_id")

# Configure backup directory
BACKUP_DIR = Path("./data/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Create the backup manager
backup_manager = BackupManager(
    db=db,
    backup_dir=BACKUP_DIR,
    backup_interval=300,       # Backup every 5 minutes
    file_format="json",        # Human-readable format for debugging
    min_backup_interval=10.0,  # Minimum 10s between triggered backups
)

# Start automatic backups
backup_manager.start()
print("Gestionnaire de sauvegardes démarré")

# ... Application running ...

# On application shutdown
backup_manager.backup_full()  # Final complete backup
backup_manager.stop()
print("Gestionnaire de sauvegardes arrêté proprement")
```

### Gestion des Échecs de Sauvegarde

« Que se passe-t-il si une sauvegarde échoue ? » demanda Thomas.

```python
import logging
from dictdb import DictDB, BackupManager

# Standard logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("techflow.backup")

def on_backup_failure(error: Exception, consecutive_failures: int):
    """
    Callback invoked when a backup fails.

    :param error: The exception that caused the failure
    :param consecutive_failures: Number of consecutive failures
    """
    logger.error(f"Échec de sauvegarde ({consecutive_failures}x) : {error}")

    # Progressive alerts based on severity
    if consecutive_failures == 1:
        logger.warning("Premier échec de sauvegarde - surveillance active")
    elif consecutive_failures == 3:
        logger.error("3 échecs consécutifs - vérifier l'espace disque")
        # send_admin_email("Alerte Sauvegardes", str(error))
    elif consecutive_failures >= 5:
        logger.critical("CRITIQUE : 5+ échecs - intervention requise !")
        # send_oncall_sms("Sauvegardes en échec critique")

db = DictDB()
db.create_table("critical_data")

backup_manager = BackupManager(
    db=db,
    backup_dir="./backups",
    backup_interval=60,
    on_backup_failure=on_backup_failure,
)

backup_manager.start()

# Monitor status
print(f"Échecs consécutifs : {backup_manager.consecutive_failures}")
```

## Sauvegardes Incrémentales

« Les sauvegardes complètes prennent trop de temps avec des millions d'enregistrements, » nota Lucas. « Passons aux sauvegardes incrémentales. »

```python
from dictdb import DictDB, BackupManager

db = DictDB()
db.create_table("transactions", primary_key="tx_id")

# Incremental mode: saves only changes
backup_manager = BackupManager(
    db=db,
    backup_dir="./backups",
    backup_interval=60,           # Every minute
    incremental=True,             # Enable incremental mode
    max_deltas_before_full=10,    # Full backup every 10 deltas
)

backup_manager.start()

# Insert data
transactions = db.get_table("transactions")
for i in range(100):
    transactions.insert({"tx_id": f"TX{i:05d}", "amount": i * 10.0})

# Trigger an incremental backup after a large batch
backup_manager.notify_change()

# Check the number of deltas since last full backup
print(f"Deltas depuis la dernière sauvegarde complète : {backup_manager.deltas_since_full}")

# Force a full backup (compaction)
backup_manager.backup_full()
print(f"Deltas après compactage : {backup_manager.deltas_since_full}")  # 0
```

### Structure des Fichiers de Sauvegarde

```
backups/
  dictdb_backup_1706123456_789012.json   # Sauvegarde complète
  dictdb_delta_1706123516_123456.json    # Delta 1
  dictdb_delta_1706123576_234567.json    # Delta 2
  dictdb_delta_1706123636_345678.json    # Delta 3
  dictdb_backup_1706123696_456789.json   # Nouvelle sauvegarde complète (compactage)
```

### Restauration depuis des Sauvegardes Incrémentales

```python
from pathlib import Path
from dictdb import DictDB
from dictdb.storage.persist import apply_delta

BACKUP_DIR = Path("./backups")

def restore_database():
    """Restore the database from backups."""

    # Find the latest full backup
    full_backups = sorted(BACKUP_DIR.glob("dictdb_backup_*.json"))
    if not full_backups:
        raise FileNotFoundError("Aucune sauvegarde complète trouvée")

    latest_full = full_backups[-1]
    print(f"Chargement de la sauvegarde complète : {latest_full.name}")

    # Load the full backup
    db = DictDB.load(str(latest_full), "json")

    # Extract the timestamp from the full backup
    # Format: dictdb_backup_1706123456_789012.json
    backup_timestamp = latest_full.stem.replace("dictdb_backup_", "")

    # Apply subsequent deltas
    deltas = sorted(BACKUP_DIR.glob("dictdb_delta_*.json"))
    for delta_file in deltas:
        delta_timestamp = delta_file.stem.replace("dictdb_delta_", "")
        if delta_timestamp > backup_timestamp:
            affected = apply_delta(db, delta_file)
            print(f"Delta appliqué : {delta_file.name} ({affected} enregistrements)")

    return db

# Restore
restored_db = restore_database()
print(f"Base de données restaurée : {len(restored_db.list_tables())} tables")
```

## Modèles de Thread-Safety

« Notre application recevra des requêtes de plusieurs threads simultanément, » expliqua Sarah. « Comment gérons-nous cela ? »

### Lectures Concurrentes

```python
import threading
from dictdb import DictDB

db = DictDB()
db.create_table("products")
products = db.get_table("products")

# Populate with data
for i in range(1000):
    products.insert({"name": f"Produit {i}", "price": i * 9.99, "stock": i % 100})

def reader_thread(thread_id: int):
    """Function executed by each reader thread."""
    # Multiple threads can read simultaneously
    results = products.select(
        where=products.price > 500,
        order_by="-price",
        limit=10,
    )
    print(f"Thread {thread_id} : trouvé {len(results)} produits chers")

# Launch 10 reader threads in parallel
threads = [threading.Thread(target=reader_thread, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("Toutes les lectures terminées")
```

### Écritures Concurrentes

```python
import threading
import time
from dictdb import DictDB, DuplicateKeyError

db = DictDB()
db.create_table("counters", primary_key="name")
counters = db.get_table("counters")

# Initialize a counter
counters.insert({"name": "visits", "value": 0})

def increment_counter(thread_id: int, iterations: int):
    """Increment counter in a thread-safe manner."""
    for _ in range(iterations):
        # The update is atomic
        counters.update(
            {"value": counters.select(where=counters.name == "visits")[0]["value"] + 1},
            where=counters.name == "visits",
        )

# Note: This approach has a race condition problem!
# Let's see the correct method...

def increment_counter_safe(db_instance: DictDB, thread_id: int, iterations: int):
    """
    Thread-safe version using upsert to avoid race conditions.
    For counters, prefer an atomic structure.
    """
    counters = db_instance.get_table("counters")
    for _ in range(iterations):
        # Read and update atomically
        # Use copy=True to avoid modifications to shared references
        current = counters.select(where=counters.name == "visits", copy=True)
        if current:
            new_value = current[0]["value"] + 1
            counters.update({"value": new_value}, where=counters.name == "visits")
```

### Modèle Producteur-Consommateur

```python
import threading
import queue
import time
from dictdb import DictDB

db = DictDB()
db.create_table("tasks", primary_key="id")
db.create_table("results", primary_key="task_id")

tasks = db.get_table("tasks")
results = db.get_table("results")

# Queue for coordination
task_queue = queue.Queue()
shutdown = threading.Event()

def producer():
    """Create tasks and add them to the queue."""
    for i in range(100):
        task_id = tasks.insert({"id": i, "status": "pending", "data": f"task_{i}"})
        task_queue.put(task_id)
        time.sleep(0.01)  # Simulate delay between tasks

    # Signal completion
    shutdown.set()
    print("Producteur terminé")

def consumer(worker_id: int):
    """Process tasks from the queue."""
    while not shutdown.is_set() or not task_queue.empty():
        try:
            task_id = task_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        # Update status (atomic)
        tasks.update({"status": "in_progress"}, where=tasks.id == task_id)

        # Simulate processing
        time.sleep(0.05)

        # Record the result
        results.insert({
            "task_id": task_id,
            "worker": worker_id,
            "result": "success",
        })

        # Mark as completed
        tasks.update({"status": "completed"}, where=tasks.id == task_id)
        task_queue.task_done()

    print(f"Consommateur {worker_id} terminé")

# Start threads
prod = threading.Thread(target=producer)
consumers = [threading.Thread(target=consumer, args=(i,)) for i in range(3)]

prod.start()
for c in consumers:
    c.start()

prod.join()
for c in consumers:
    c.join()

print(f"Tâches traitées : {results.count()}")
```

## Opérations Asynchrones de Sauvegarde/Chargement

« Pour notre API web asynchrone, nous ne pouvons pas bloquer sur les E/S, » nota Thomas.

```python
import asyncio
from dictdb import DictDB

async def main():
    # Create and populate the database
    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")

    for i in range(1000):
        users.insert({"name": f"Utilisateur{i}", "email": f"user{i}@example.com"})

    # Async save - does not block the event loop
    print("Démarrage de la sauvegarde asynchrone...")
    await db.async_save("backup_async.json", "json")
    print("Sauvegarde terminée")

    # Async load
    print("Chargement asynchrone...")
    db_loaded = await DictDB.async_load("backup_async.json", "json")
    print(f"Chargé {db_loaded.get_table('users').count()} utilisateurs")

# In an async application (FastAPI, aiohttp, etc.)
asyncio.run(main())
```

### Intégration FastAPI

```python
from fastapi import FastAPI, BackgroundTasks
from dictdb import DictDB, BackupManager

app = FastAPI()
db = DictDB()
db.create_table("api_logs", primary_key="id")
logs = db.get_table("api_logs")

# BackupManager in the background
backup_manager = BackupManager(db, "./backups", backup_interval=60, incremental=True)

@app.on_event("startup")
async def startup():
    backup_manager.start()

@app.on_event("shutdown")
async def shutdown():
    backup_manager.backup_full()
    backup_manager.stop()

@app.post("/log")
async def create_log(message: str, background_tasks: BackgroundTasks):
    log_id = logs.insert({"message": message, "timestamp": "2024-01-20T10:00:00"})

    # Save in background after insertion
    background_tasks.add_task(backup_manager.notify_change)

    return {"id": log_id}

@app.get("/backup/status")
async def backup_status():
    return {
        "consecutive_failures": backup_manager.consecutive_failures,
        "deltas_since_full": backup_manager.deltas_since_full,
    }
```

## Configuration des Logs

« L'observabilité est cruciale en production, » déclara Lucas. « Configurons correctement les logs. »

### Configuration de Base

```python
from dictdb import DictDB, configure_logging

# Simple configuration: logs to stdout at INFO level
configure_logging(level="INFO", console=True)

db = DictDB()  # Will print: "Initialized an empty DictDB instance."
db.create_table("test")  # Will print: "Created table 'test' (pk='id')."
```

### Configuration Avancée pour la Production

```python
from dictdb import configure_logging

# Production configuration:
# - INFO level for console (errors visible)
# - All logs to a file
# - JSON format for aggregation
configure_logging(
    level="INFO",
    console=True,
    logfile="./logs/dictdb.log",
    json=True,  # JSON format for ELK/Splunk/etc.
)
```

### Échantillonnage des Logs DEBUG

```python
from dictdb import configure_logging

# In production with high traffic, sample DEBUG logs
# to avoid drowning important logs
configure_logging(
    level="DEBUG",
    console=True,
    logfile="./logs/dictdb_debug.log",
    sample_debug_every=100,  # Only log 1 DEBUG out of 100
)
```

### Logging Personnalisé avec Filtres

```python
from dictdb import logger

# Remove default handlers
logger.remove()

# Add a handler for stdout with filter
logger.add(
    sink="./logs/operations.log",
    level="INFO",
    filter=lambda record: record["extra"].get("op") in ("INSERT", "UPDATE", "DELETE"),
)

# Add a separate handler for errors
logger.add(
    sink="./logs/errors.log",
    level="ERROR",
)

# Logs will be automatically routed to the appropriate file
```

## Bonnes Pratiques de Gestion des Erreurs

« En production, les erreurs arrivent, » philosopha Sarah. « Ce qui compte, c'est de les gérer correctement. »

```python
from dictdb import (
    DictDB,
    DictDBError,
    DuplicateKeyError,
    DuplicateTableError,
    RecordNotFoundError,
    SchemaValidationError,
    TableNotFoundError,
)

def handle_operation_robustly(db: DictDB, operation: str, **kwargs):
    """
    Execute an operation with complete error handling.
    """
    try:
        if operation == "insert":
            table = db.get_table(kwargs["table"])
            return table.insert(kwargs["record"])

        elif operation == "update":
            table = db.get_table(kwargs["table"])
            return table.update(kwargs["changes"], where=kwargs.get("where"))

        elif operation == "delete":
            table = db.get_table(kwargs["table"])
            return table.delete(where=kwargs.get("where"))

    except TableNotFoundError as e:
        # Table doesn't exist - maybe create it automatically?
        print(f"Table non trouvée : {e}")
        raise

    except DuplicateKeyError as e:
        # Primary key already exists
        print(f"Doublon détecté : {e}")
        # Option: use upsert instead
        raise

    except SchemaValidationError as e:
        # Data doesn't match the schema
        print(f"Erreur de validation : {e}")
        raise

    except RecordNotFoundError as e:
        # No record matches the criteria
        print(f"Enregistrement non trouvé : {e}")
        return 0  # Not a fatal error, just no modifications

    except DictDBError as e:
        # Generic DictDB error
        print(f"Erreur DictDB : {e}")
        raise

    except Exception as e:
        # Unexpected error
        print(f"Erreur inattendue : {type(e).__name__}: {e}")
        raise


# Usage
db = DictDB()
db.create_table("products", primary_key="sku")

try:
    handle_operation_robustly(
        db,
        "insert",
        table="products",
        record={"sku": "ABC123", "name": "Widget", "price": 29.99},
    )
except DuplicateKeyError:
    # Handle the duplicate
    pass
```

### Modèle de Retry avec Backoff Exponentiel

```python
import time
import random
from functools import wraps
from dictdb import DictDBError

def with_retry(max_attempts: int = 3, backoff_base: float = 1.0):
    """Decorator to retry an operation on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except DictDBError as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        # Exponential backoff with jitter
                        delay = backoff_base * (2 ** attempt) + random.uniform(0, 1)
                        print(f"Tentative {attempt + 1} échouée, nouvelle tentative dans {delay:.2f}s")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@with_retry(max_attempts=3)
def insert_with_retry(table, record):
    """Insert a record with automatic retry."""
    return table.insert(record)
```

## Conseils de Performance

« Maintenant, optimisons pour la performance, » déclara Lucas.

### 1. Utiliser les Index Judicieusement

```python
from dictdb import DictDB

db = DictDB()
db.create_table("transactions", primary_key="id")
transactions = db.get_table("transactions")

# Create indexes on frequently queried columns
transactions.create_index("customer_id", index_type="hash")   # O(1) for equality
transactions.create_index("amount", index_type="sorted")       # O(log n) for ranges
transactions.create_index("date", index_type="sorted")         # For ORDER BY

# Populate with data
for i in range(100000):
    transactions.insert({
        "customer_id": i % 1000,
        "amount": i * 0.99,
        "date": f"2024-01-{(i % 28) + 1:02d}",
        "status": "active" if i % 2 == 0 else "inactive",
    })

# Fast query using hash index on customer_id
import time

start = time.time()
results = transactions.select(where=transactions.customer_id == 42)
print(f"Recherche par customer_id : {len(results)} résultats en {time.time() - start:.4f}s")

# Range query using sorted index on amount
start = time.time()
results = transactions.select(where=transactions.amount.between(1000, 2000))
print(f"Recherche par plage de montant : {len(results)} résultats en {time.time() - start:.4f}s")
```

### 2. Utiliser copy=False pour les Opérations en Lecture Seule

```python
from dictdb import DictDB

db = DictDB()
db.create_table("logs", primary_key="id")
logs = db.get_table("logs")

# Populate
for i in range(50000):
    logs.insert({"message": f"Entrée de log {i}", "level": "INFO"})

import time

# With copy (default, safer)
start = time.time()
results_copied = logs.select(limit=10000, copy=True)
print(f"Avec copy=True : {time.time() - start:.4f}s")

# Without copy (faster, read-only)
start = time.time()
results_refs = logs.select(limit=10000, copy=False)
print(f"Avec copy=False : {time.time() - start:.4f}s")

# WARNING: never modify results with copy=False!
# results_refs[0]["message"] = "Modifié"  # DANGEREUX !
```

### 3. Insertions par Lots

```python
from dictdb import DictDB
import time

db = DictDB()
db.create_table("events", primary_key="id")
events = db.get_table("events")

# Bad practice: individual inserts
data = [{"type": "click", "page": f"/page/{i}"} for i in range(10000)]

start = time.time()
for record in data:
    events.insert(record)
print(f"Insertions individuelles : {time.time() - start:.4f}s")

# Reset
events.delete()

# Good practice: batch insert
start = time.time()
events.insert(data)  # Single operation
print(f"Insertion par lot : {time.time() - start:.4f}s")

# With explicit batches for very large volumes
start = time.time()
events.delete()
events.insert(data, batch_size=1000)  # Process in batches of 1000
print(f"Insertion par lot avec batch_size : {time.time() - start:.4f}s")
```

### 4. Utiliser skip_validation pour les Données de Confiance

```python
from dictdb import DictDB

db = DictDB()
db.create_table("imported_data", primary_key="id")
data_table = db.get_table("imported_data")

# Data from a trusted source (internal API, validated file, etc.)
trusted_data = [
    {"id": i, "value": i * 10}
    for i in range(100000)
]

import time

# With validation (safer, slower)
start = time.time()
data_table.insert(trusted_data)
print(f"Avec validation : {time.time() - start:.4f}s")

data_table.delete()

# Without validation (faster, only for trusted data!)
start = time.time()
data_table.insert(trusted_data, skip_validation=True)
print(f"Sans validation : {time.time() - start:.4f}s")
```

### 5. Limiter les Résultats avec LIMIT et ORDER BY Optimisé

```python
from dictdb import DictDB

db = DictDB()
db.create_table("scores", primary_key="id")
scores = db.get_table("scores")

# Index on the sort field
scores.create_index("points", index_type="sorted")

# Populate
for i in range(100000):
    scores.insert({"player": f"Joueur{i}", "points": i * 7 % 10000})

import time

# Get top 10 - DictDB automatically optimizes with heapq
start = time.time()
top10 = scores.select(
    order_by="-points",  # Descending sort
    limit=10,
)
print(f"Top 10 en {time.time() - start:.4f}s")

for i, score in enumerate(top10, 1):
    print(f"  {i}. {score['player']}: {score['points']} points")
```

## Exemple Complet : Application Prête pour la Production

Voici un exemple complet intégrant toutes les bonnes pratiques :

```python
"""
Production-ready DictDB application.
"""

import asyncio
import threading
import time
from pathlib import Path
from contextlib import contextmanager
from dictdb import (
    DictDB,
    BackupManager,
    configure_logging,
    DictDBError,
    RecordNotFoundError,
)


class ProductionApp:
    """DictDB application configured for production."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        configure_logging(
            level="INFO",
            console=True,
            logfile=str(self.data_dir / "app.log"),
            json=False,
        )

        # Initialize or load database
        self.db = self._initialize_or_load()

        # Configure backup manager
        self.backup_manager = BackupManager(
            db=self.db,
            backup_dir=self.data_dir / "backups",
            backup_interval=300,
            file_format="json",
            min_backup_interval=30.0,
            on_backup_failure=self._on_backup_failure,
            incremental=True,
            max_deltas_before_full=20,
        )

        # Statistics
        self._stats = {
            "operations": 0,
            "errors": 0,
            "started_at": time.time(),
        }

    def _initialize_or_load(self) -> DictDB:
        """Load an existing backup or create a new database."""
        backup_dir = self.data_dir / "backups"

        if backup_dir.exists():
            backups = sorted(backup_dir.glob("dictdb_backup_*.json"))
            if backups:
                latest = backups[-1]
                print(f"Chargement de la sauvegarde : {latest.name}")
                return DictDB.load(str(latest), "json")

        # Create a new database with required tables
        print("Création d'une nouvelle base de données")
        db = DictDB()

        db.create_table("users", primary_key="id")
        db.create_table("sessions", primary_key="session_id")
        db.create_table("logs", primary_key="id")

        # Create indexes for frequent queries
        users = db.get_table("users")
        users.create_index("email", index_type="hash")

        sessions = db.get_table("sessions")
        sessions.create_index("user_id", index_type="hash")
        sessions.create_index("expire_at", index_type="sorted")

        return db

    def _on_backup_failure(self, error: Exception, count: int):
        """Callback for backup failures."""
        self._stats["errors"] += 1
        print(f"ALERTE : Échec de sauvegarde ({count}x) : {error}")

        if count >= 5:
            print("CRITIQUE : Échecs multiples de sauvegarde !")
            # Here: send alert to operations

    def start(self):
        """Start the application."""
        print("Démarrage de l'application...")
        self.backup_manager.start()
        print("Application démarrée")

    def stop(self):
        """Stop the application gracefully."""
        print("Arrêt de l'application...")

        # Final backup
        self.backup_manager.backup_full()
        self.backup_manager.stop()

        # Save final state
        self.db.save(str(self.data_dir / "final_state.json"), "json")

        print("Application arrêtée proprement")
        self._display_stats()

    def _display_stats(self):
        """Display application statistics."""
        duration = time.time() - self._stats["started_at"]
        print(f"\n--- Statistiques ---")
        print(f"Durée d'exécution : {duration:.1f}s")
        print(f"Opérations effectuées : {self._stats['operations']}")
        print(f"Erreurs : {self._stats['errors']}")
        print(f"Échecs de sauvegarde : {self.backup_manager.consecutive_failures}")

    @contextmanager
    def operation(self, name: str):
        """Context manager to trace operations."""
        start = time.time()
        try:
            yield
            self._stats["operations"] += 1
        except DictDBError as e:
            self._stats["errors"] += 1
            print(f"Erreur dans {name} : {e}")
            raise
        finally:
            duration = time.time() - start
            if duration > 0.1:  # Log if over 100ms
                print(f"Opération lente : {name} ({duration:.3f}s)")

    def create_user(self, email: str, name: str) -> int:
        """Create a new user."""
        with self.operation("create_user"):
            users = self.db.get_table("users")
            return users.insert({
                "email": email,
                "name": name,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            })

    def get_user(self, user_id: int) -> dict:
        """Retrieve a user by ID."""
        with self.operation("get_user"):
            users = self.db.get_table("users")
            results = users.select(
                where=users.id == user_id,
                copy=True,  # Safe copy
            )
            if not results:
                raise RecordNotFoundError(f"Utilisateur {user_id} non trouvé")
            return results[0]

    def search_by_email(self, email: str) -> list:
        """Search for a user by email (uses index)."""
        with self.operation("search_by_email"):
            users = self.db.get_table("users")
            return users.select(where=users.email == email)


# Entry point
def main():
    app = ProductionApp("./production_data")

    try:
        app.start()

        # Simulate operations
        for i in range(100):
            user_id = app.create_user(
                email=f"user{i}@example.com",
                name=f"Utilisateur {i}",
            )

            # Retrieve the user
            user = app.get_user(user_id)

            # Search by email (uses index)
            results = app.search_by_email(user["email"])

            if i % 10 == 0:
                print(f"Progression : {i}/100 utilisateurs créés")

        print("Opérations terminées avec succès")

    except KeyboardInterrupt:
        print("\nInterruption demandée...")
    finally:
        app.stop()


if __name__ == "__main__":
    main()
```

## Ce Que Nous Avons Appris

À la fin de cette préparation pour la production, l'équipe de TechFlow SARL maîtrise désormais :

1. **BackupManager** : Configurer des sauvegardes périodiques avec des callbacks d'échec et une surveillance de l'état.

2. **Sauvegardes incrémentales** : Réduire les E/S en sauvegardant uniquement les changements, avec un compactage automatique après N deltas.

3. **Thread-safety** : Comprendre le modèle de concurrence de DictDB (verrou lecteur-écrivain par table) et l'utiliser correctement dans des applications multi-threadées.

4. **Opérations asynchrones** : Utiliser `async_save()` et `async_load()` pour éviter de bloquer la boucle d'événements dans les applications asynchrones.

5. **Logging** : Configurer le niveau de log, les sorties (console, fichier), le format JSON pour l'agrégation, et l'échantillonnage des logs DEBUG.

6. **Gestion des erreurs** : Capturer les exceptions spécifiques de DictDB et implémenter des modèles de retry avec backoff exponentiel.

7. **Optimisations de performance** :
   - Index hash pour les recherches d'égalité
   - Index triés pour les plages et le tri
   - `copy=False` pour les opérations en lecture seule
   - Insertions par lots au lieu d'insertions individuelles
   - `skip_validation=True` pour les données de confiance
   - `limit` et `order_by` optimisés avec heapq

« Notre application est maintenant prête à affronter la production, » conclut Sarah avec satisfaction. « Nous avons des sauvegardes robustes, une gestion appropriée de la concurrence, et des logs pour diagnostiquer les problèmes. »

Lucas acquiesça. « Et nous avons les optimisations nécessaires pour gérer la montée en charge. TechFlow SARL peut déployer en toute confiance. »

---

*Fin de la saga TechFlow SARL. Que vos bases de données soient toujours sauvegardées et vos index bien choisis.*
