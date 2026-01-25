# Sauvegardes

Le `BackupManager` permet de mettre en place une stratégie de sauvegarde automatique, périodique et incrémentale pour vos données.

## Utilisation de base

```python
from dictdb import DictDB, BackupManager

db = DictDB()
db.create_table("users")

# Créer le gestionnaire de sauvegardes
backup = BackupManager(
    db=db,
    backup_dir="./backups",
    backup_interval=300,  # Toutes les 5 minutes
    file_format="json"
)

# Lancer le processus automatique
backup.start()

# ... votre application s'exécute ...

# Arrêter proprement à la fermeture
backup.stop()
```

## Options de configuration

```python
backup = BackupManager(
    db=db,
    backup_dir="./backups",

    # Fréquence de sauvegarde en secondes (défaut : 300)
    backup_interval=300,

    # Format de fichier : "json" ou "pickle" (défaut : "json")
    file_format="json",

    # Temps min entre deux sauvegardes déclenchées par modif (défaut : 5.0)
    min_backup_interval=5.0,

    # Fonction de rappel (callback) en cas d'échec
    on_backup_failure=ma_gestion_erreur,

    # Activer le mode incrémental (défaut : False)
    incremental=False,

    # Nombre de deltas avant une base complète forcée (défaut : 10)
    max_deltas_before_full=10,
)
```

## Sauvegardes manuelles

Vous pouvez forcer une sauvegarde à tout moment :

```python
# Sauvegarde immédiate (selon le mode configuré)
backup.backup_now()

# Forcer une sauvegarde complète (indépendamment du mode)
backup.backup_full()

# Forcer une sauvegarde delta (en mode incrémental uniquement)
backup.backup_delta()
```

## Signalement de modifications

Vous pouvez prévenir le gestionnaire d'un changement important pour qu'il planifie une sauvegarde :

```python
# Déclenche une sauvegarde en respectant min_backup_interval
backup.notify_change()
```

## Sauvegardes incrémentales

En mode incrémental, DictDB n'enregistre que ce qui a changé depuis la dernière fois.

```python
backup = BackupManager(
    db=db,
    backup_dir="./backups",
    incremental=True,
    max_deltas_before_full=10,
)
```

**Fonctionnement :**

1. Les fichiers "delta" ne contiennent que les lignes créées, modifiées ou supprimées.
2. Après `max_deltas_before_full` deltas, une sauvegarde complète est générée automatiquement pour "remettre les compteurs à zéro".
3. Les sauvegardes complètes réinitialisent le nombre de deltas.

**Structure d'un fichier delta :**

```json
{
  "type": "delta",
  "timestamp": 1234567890.123456,
  "tables": {
    "users": {
      "upserts": [{"id": 1, "name": "Alice"}],
      "deletes": [2, 3]
    }
  }
}
```

## Surveillance et erreurs

Le `BackupManager` vous permet de garder un œil sur la santé de vos données :

```python
def ma_gestion_erreur(error: Exception, consecutive_failures: int):
    print(f"Échec de sauvegarde ({consecutive_failures}x) : {error}")
    if consecutive_failures >= 3:
        alerte_admin("Le système de sauvegarde est en panne !")

backup = BackupManager(..., on_backup_failure=ma_gestion_erreur)

# Vérifier l'état actuel
print(f"Échecs consécutifs : {backup.consecutive_failures}")
print(f"Deltas accumulés   : {backup.deltas_since_full}")
```

## Nommage des fichiers

Les fichiers sont nommés avec un timestamp précis à la microseconde :

- Base complète : `dictdb_backup_1234567890_123456.json`
- Delta : `dictdb_delta_1234567890_123456.json`

## Restauration à partir des sauvegardes

Pour restaurer, chargez d'abord la base complète la plus récente :

```python
from pathlib import Path
from dictdb import DictDB

backup_dir = Path("./backups")

# Trouver la dernière base complète
full_backups = sorted(backup_dir.glob("dictdb_backup_*.json"))
if full_backups:
    latest = full_backups[-1]
    db = DictDB.load(str(latest), file_format="json")
```

Pour les sauvegardes incrémentales, appliquez les deltas dans l'ordre chronologique :

```python
from dictdb.storage.persist import apply_delta

# Appliquer tous les deltas parus après la sauvegarde complète choisie
for delta_file in sorted(backup_dir.glob("dictdb_delta_*.json")):
    # (Logique de filtrage par date à prévoir ici)
    nb_touches = apply_delta(db, delta_file)
    print(f"Delta appliqué : {delta_file.name} ({nb_touches} lignes)")
```