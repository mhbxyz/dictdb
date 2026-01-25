# Journalisation (Logging)

DictDB intègre un système de journalisation complet, compatible avec l'API de `loguru`.

## Démarrage rapide

```python
from dictdb import configure_logging

# Activer les logs de niveau INFO vers la console
configure_logging(level="INFO", console=True)
```

## Configuration complète

```python
configure_logging(
    # Niveau minimum : DEBUG, INFO, WARNING, ERROR, CRITICAL
    level="INFO",

    # Afficher dans la console (défaut : True)
    console=True,

    # Écrire dans un fichier (optionnel)
    logfile="dictdb.log",

    # Sortie au format JSON (défaut : False)
    json=False,

    # Échantillonnage : ne logue qu'un message DEBUG sur N (optionnel)
    sample_debug_every=10,
)
```

## Niveaux de logs

| Niveau | Description |
|--------|-------------|
| `DEBUG` | Détails techniques (requêtes, utilisation des index) |
| `INFO` | Opérations courantes (insertions, sauvegardes) |
| `WARNING` | Alertes sur des comportements potentiellement problématiques |
| `ERROR` | Échecs d'opérations |
| `CRITICAL` | Erreurs système graves |

## Formats de sortie

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

Vous pouvez utiliser le logger interne pour vos propres messages :

```python
from dictdb import logger

# Message simple
logger.info("Mon message personnalisé")

# Ajout de contexte avec bind()
log = logger.bind(component="MonApp", user_id=123)
log.info("Action effectuée par l'utilisateur")
```

## Gestionnaires personnalisés (Handlers)

```python
from dictdb import logger
import sys

# Supprimer les sorties par défaut
logger.remove()

# Ajouter une sortie console lisible
logger.add(sys.stdout, level="INFO", serialize=False)

# Ajouter une sortie fichier en JSON pour un outil d'agrégation (ex: ELK)
logger.add("app.log", level="DEBUG", serialize=True)
```

## Échantillonnage en production

Pour éviter de saturer vos fichiers de logs en production tout en gardant une visibilité sur le débogage :

```python
# Ne journalise qu'un message DEBUG sur 100
configure_logging(
    level="DEBUG",
    sample_debug_every=100,
)
```

## Ce qui est journalisé par DictDB

### Opérations de base de données

```
INFO  | component=DictDB | Initialized an empty DictDB instance.
INFO  | component=DictDB op=CREATE_TABLE table=users pk=id | Created table 'users'
```

### Opérations sur les tables

```
DEBUG | table=users op=INSERT | Inserting record into 'users'
INFO  | table=users op=INSERT pk=1 | Record inserted into 'users' (pk=1)
INFO  | table=users op=UPDATE count=3 | Updated 3 record(s) in 'users'
```

### Gestionnaire de sauvegarde

```
INFO  | Performing full backup to dictdb_backup_123.json
ERROR | Backup failed (2 consecutive): Permission denied
```

## Désactiver les logs

```python
from dictdb import logger

# Supprimer tous les gestionnaires
logger.remove()

# Ou configurer au niveau critique uniquement
configure_logging(level="CRITICAL", console=False)
```