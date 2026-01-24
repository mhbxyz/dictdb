# Sauvegardes

Le `BackupManager` fournit des sauvegardes automatiques périodiques et incrémentielles pour DictDB.

## Utilisation de base

```python
from dictdb import DictDB, BackupManager

db = DictDB()
db.create_table("users")

# Créer le gestionnaire de sauvegarde
backup = BackupManager(
    db=db,
    backup_dir="./backups",
    backup_interval=300,  # 5 minutes
    file_format="json"
)

# Démarrer les sauvegardes automatiques
backup.start()

# ... votre application s'exécute ...

# Arrêter à la fin
backup.stop()
```

## Options de configuration

```python
backup = BackupManager(
    db=db,
    backup_dir="./backups",

    # Intervalle de sauvegarde périodique en secondes (par défaut : 300)
    backup_interval=300,

    # Format de fichier : "json" ou "pickle" (par défaut : "json")
    file_format="json",

    # Intervalle minimum entre les sauvegardes déclenchées par les modifications (par défaut : 5.0)
    min_backup_interval=5.0,

    # Callback pour les échecs de sauvegarde
    on_backup_failure=handle_failure,

    # Activer les sauvegardes incrémentielles (par défaut : False)
    incremental=False,

    # Nombre de deltas avant de forcer une sauvegarde complète (par défaut : 10)
    max_deltas_before_full=10,
)
```

## Sauvegardes manuelles

```python
# Sauvegarde immédiate
backup.backup_now()

# Forcer une sauvegarde complète
backup.backup_full()

# Forcer une sauvegarde delta (mode incrémentiel)
backup.backup_delta()
```

## Notification de modification

Déclencher une sauvegarde après des modifications significatives :

```python
# Notifier d'une modification significative
# Respecte min_backup_interval pour éviter les E/S excessives
backup.notify_change()
```

## Sauvegardes incrémentielles

Le mode incrémentiel ne sauvegarde que les modifications depuis la dernière sauvegarde :

```python
backup = BackupManager(
    db=db,
    backup_dir="./backups",
    incremental=True,
    max_deltas_before_full=10,
)
```

**Fonctionnement :**

1. Les fichiers delta contiennent uniquement les enregistrements insérés, mis à jour et supprimés
2. Après `max_deltas_before_full` deltas, une sauvegarde complète est créée
3. Les sauvegardes complètes réinitialisent le compteur de deltas

**Structure du fichier delta :**

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

## Gestion des échecs

Gérer les échecs de sauvegarde avec un callback :

```python
def handle_failure(error: Exception, consecutive_failures: int):
    print(f"Échec de la sauvegarde ({consecutive_failures}x) : {error}")
    if consecutive_failures >= 3:
        send_alert("Le système de sauvegarde échoue !")

backup = BackupManager(
    db=db,
    backup_dir="./backups",
    on_backup_failure=handle_failure,
)
```

Surveiller le nombre d'échecs :

```python
if backup.consecutive_failures > 0:
    print(f"Attention : {backup.consecutive_failures} échecs consécutifs")
```

## Nommage des fichiers de sauvegarde

Les fichiers sont nommés avec des horodatages à la microseconde près :

- Sauvegardes complètes : `dictdb_backup_1234567890_123456.json`
- Sauvegardes delta : `dictdb_delta_1234567890_123456.json`

## Surveillance de l'état

```python
# Vérifier les échecs consécutifs
backup.consecutive_failures  # 0

# Vérifier les deltas depuis la dernière sauvegarde complète (mode incrémentiel)
backup.deltas_since_full  # 3
```

## Exemple : Configuration de production

```python
import logging
from pathlib import Path
from dictdb import DictDB, BackupManager

# Configurer les chemins
BACKUP_DIR = Path("./data/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Initialiser la base de données
db = DictDB()
db.create_table("events", primary_key="event_id")

# Gestionnaire d'échecs avec journalisation
def on_failure(error: Exception, count: int):
    logging.error(f"Échec de la sauvegarde ({count}x) : {error}")
    if count >= 5:
        logging.critical("Échecs de sauvegarde multiples - vérifiez l'espace disque !")

# Créer le gestionnaire de sauvegarde
backup = BackupManager(
    db=db,
    backup_dir=BACKUP_DIR,
    backup_interval=60,  # Chaque minute
    file_format="json",
    min_backup_interval=10.0,
    on_backup_failure=on_failure,
    incremental=True,
    max_deltas_before_full=20,
)

# Démarrer les sauvegardes
backup.start()

try:
    # Logique applicative
    events = db.get_table("events")

    # Après des opérations par lots, déclencher une sauvegarde
    for i in range(100):
        events.insert({"event_id": i, "type": "click"})
    backup.notify_change()

finally:
    # Assurer une sauvegarde finale à l'arrêt
    backup.backup_full()
    backup.stop()
```

## Restauration à partir des sauvegardes

Charger la sauvegarde complète la plus récente :

```python
from pathlib import Path

backup_dir = Path("./backups")

# Trouver la dernière sauvegarde complète
full_backups = sorted(backup_dir.glob("dictdb_backup_*.json"))
if full_backups:
    latest = full_backups[-1]
    db = DictDB.load(str(latest), file_format="json")
```

Pour les sauvegardes incrémentielles, appliquer les deltas dans l'ordre :

```python
from dictdb.storage.persist import apply_delta

# Charger la sauvegarde de base
db = DictDB.load("dictdb_backup_base.json", file_format="json")

# Appliquer les deltas dans l'ordre chronologique
for delta_file in sorted(backup_dir.glob("dictdb_delta_*.json")):
    affected = apply_delta(db, delta_file)
    print(f"Appliqué {delta_file.name} : {affected} enregistrements")
```
