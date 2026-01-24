# Journalisation

DictDB inclut un système de journalisation intégré avec une API compatible loguru.

## Démarrage rapide

```python
from dictdb import configure_logging

# Activer la journalisation niveau info vers la console
configure_logging(level="INFO", console=True)
```

## Configuration

```python
configure_logging(
    # Niveau de journalisation minimum : DEBUG, INFO, WARNING, ERROR, CRITICAL
    level="INFO",

    # Journaliser vers stdout (par défaut : True)
    console=True,

    # Journaliser vers un fichier (optionnel)
    logfile="dictdb.log",

    # Format de sortie JSON (par défaut : False)
    json=False,

    # Échantillonner les messages DEBUG : journaliser 1 sur N (optionnel)
    sample_debug_every=10,
)
```

## Niveaux de journalisation

| Niveau | Description |
|--------|-------------|
| `DEBUG` | Informations détaillées des opérations (requêtes, utilisation des index) |
| `INFO` | Opérations normales (insertions, mises à jour, sauvegardes) |
| `WARNING` | Problèmes potentiels |
| `ERROR` | Échecs d'opérations |
| `CRITICAL` | Erreurs graves |

## Format de sortie

### Console (colorée)

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

## Accès direct au logger

```python
from dictdb import logger

# Journalisation directe
logger.info("Message personnalisé")
logger.debug("Informations de débogage")
logger.warning("Message d'avertissement")
logger.error("Une erreur s'est produite")

# Journalisation contextuelle avec bind()
log = logger.bind(component="MyApp", user_id=123)
log.info("Action utilisateur effectuée")
```

## Handlers personnalisés

```python
from dictdb import logger
import sys

# Supprimer les handlers par défaut
logger.remove()

# Ajouter un handler stdout personnalisé
logger.add(
    sink=sys.stdout,
    level="INFO",
    serialize=False,  # Lisible par l'humain
)

# Ajouter un handler fichier avec JSON
logger.add(
    sink="app.log",
    level="DEBUG",
    serialize=True,  # Format JSON
)

# Ajouter un handler fonction personnalisé
def my_handler(message: str):
    # Envoyer vers un service externe, etc.
    print(f"PERSONNALISÉ : {message}")

logger.add(sink=my_handler, level="ERROR")
```

## Filtrage

```python
# Fonction de filtre
def only_errors(record):
    return record["level"].name in ("ERROR", "CRITICAL")

logger.add(
    sink="errors.log",
    level="DEBUG",
    filter=only_errors,
)
```

## Échantillonnage du débogage

Réduire le volume des logs DEBUG en production :

```python
# Journaliser seulement 1 message DEBUG sur 100
configure_logging(
    level="DEBUG",
    sample_debug_every=100,
)
```

## Ce qui est journalisé

### Opérations de base de données

```
INFO  | component=DictDB | Initialized an empty DictDB instance.
INFO  | component=DictDB op=CREATE_TABLE table=users pk=id | Created table 'users'
INFO  | component=DictDB op=DROP_TABLE table=users | Dropped table 'users'
```

### Opérations de table

```
DEBUG | table=users op=INSERT | Inserting record into 'users'
INFO  | table=users op=INSERT pk=1 | Record inserted into 'users' (pk=1)
INFO  | table=users op=UPDATE count=3 | Updated 3 record(s) in 'users'
INFO  | table=users op=DELETE count=1 | Deleted 1 record(s) from 'users'
```

### Opérations d'index

```
INFO  | table=users op=INDEX field=email index_type=hash | Index created on field 'email'
```

### Persistance

```
INFO  | component=DictDB op=SAVE tables=2 records=100 format=json path=data.json | Saving database
INFO  | component=DictDB op=LOAD path=data.json format=json tables=2 records=100 | Loaded database
```

### Gestionnaire de sauvegarde

```
INFO  | Starting automatic backup manager.
INFO  | Performing full backup to dictdb_backup_123.json
INFO  | Delta backup saved successfully (3/10 deltas)
ERROR | Backup failed (2 consecutive): Permission denied
```

## Exemple : Configuration de production

```python
from dictdb import DictDB, configure_logging

# Configurer pour la production
configure_logging(
    level="INFO",
    console=True,
    logfile="/var/log/dictdb/app.log",
    json=True,  # Journalisation structurée pour l'agrégation des logs
)

# Application
db = DictDB()
db.create_table("events")
# Toutes les opérations sont maintenant journalisées
```

## Désactiver la journalisation

```python
from dictdb import logger

# Supprimer tous les handlers
logger.remove()

# Ou configurer sans sorties
configure_logging(level="CRITICAL", console=False)
```
