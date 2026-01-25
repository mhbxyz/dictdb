# Prêt pour la production

*La suite de l'histoire de TechFlow SARL : du prototype au déploiement*

---

Après avoir réussi la migration des données historiques, l'équipe de TechFlow SARL était prête pour l'étape suivante. Sarah convoqua une réunion de planification technique.

« Notre prototype fonctionne à merveille », commença-t-elle. « Mais avant de passer en production, nous devons nous assurer que notre système est robuste, performant et capable de surmonter n'importe quel incident. »

Lucas, l'architecte systèmes, intervint : « Il nous faut des sauvegardes automatiques, une gestion rigoureuse de la concurrence et une observabilité totale. Sans oublier l'optimisation des performances. »

« Exactement », acquiesça Sarah. « Commençons par le commencement. »

## Configuration du BackupManager

« La règle d'or en production : ne jamais faire l'impasse sur les sauvegardes », rappela Lucas.

### Configuration de base

```python
from pathlib import Path
from dictdb import DictDB, BackupManager

# Initialiser la base de données
db = DictDB()
db.create_table("users", primary_key="id")
db.create_table("sessions", primary_key="session_id")
db.create_table("events", primary_key="event_id")

# Configurer le répertoire de sauvegarde
BACKUP_DIR = Path("./data/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Créer le gestionnaire de sauvegardes
backup_manager = BackupManager(
    db=db,
    backup_dir=BACKUP_DIR,
    backup_interval=300,       # Sauvegarde toutes les 5 minutes
    file_format="json",        # Format lisible pour faciliter le débogage
    min_backup_interval=10.0,  # Minimum 10s entre deux sauvegardes déclenchées
)

# Démarrer les sauvegardes automatiques
backup_manager.start()
print("Gestionnaire de sauvegardes démarré")

# ... L'application tourne ...

# À la fermeture de l'application
backup_manager.backup_full()  # Une dernière sauvegarde complète
backup_manager.stop()
print("Gestionnaire de sauvegardes arrêté proprement")
```

### Gestion des échecs de sauvegarde

« Et si une sauvegarde échoue ? », demanda Thomas.

```python
import logging
from dictdb import DictDB, BackupManager

# Configuration standard du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("techflow.backup")

def on_backup_failure(error: Exception, consecutive_failures: int):
    """
    Callback appelé en cas d'échec de sauvegarde.
    """
    logger.error(f"Échec de sauvegarde ({consecutive_failures}x) : {error}")

    # Alertes progressives selon la gravité
    if consecutive_failures == 1:
        logger.warning("Premier échec - surveillance active")
    elif consecutive_failures == 3:
        logger.error("3 échecs consécutifs - vérifiez l'espace disque")
        # envoyer_email_admin("Alerte Sauvegardes", str(error))
    elif consecutive_failures >= 5:
        logger.critical("CRITIQUE : 5+ échecs - intervention immédiate requise !")
        # envoyer_sms_astreinte("Sauvegardes en échec critique")

db = DictDB()
db.create_table("donnees_critiques")

backup_manager = BackupManager(
    db=db,
    backup_dir="./backups",
    backup_interval=60,
    on_backup_failure=on_backup_failure,
)

backup_manager.start()

# Surveiller l'état
print(f"Échecs consécutifs : {backup_manager.consecutive_failures}")
```

## Sauvegardes incrémentales

« Les sauvegardes complètes vont devenir trop lourdes avec des millions d'enregistrements », nota Lucas. « Passons au mode incrémental. »

```python
from dictdb import DictDB, BackupManager

db = DictDB()
db.create_table("transactions", primary_key="tx_id")

# Mode incrémental : on ne sauvegarde que les changements
backup_manager = BackupManager(
    db=db,
    backup_dir="./backups",
    backup_interval=60,           # Chaque minute
    incremental=True,             # Activer le mode incrémental
    max_deltas_before_full=10,    # Une sauvegarde complète tous les 10 deltas
)

backup_manager.start()

# Insérer des données
transactions = db.get_table("transactions")
for i in range(100):
    transactions.insert({"tx_id": f"TX{i:05d}", "amount": i * 10.0})

# Déclencher une sauvegarde incrémentale après un gros lot
backup_manager.notify_change()

# Vérifier le nombre de deltas depuis la dernière sauvegarde complète
print(f"Deltas accumulés : {backup_manager.deltas_since_full}")

# Forcer une sauvegarde complète (compactage)
backup_manager.backup_full()
print(f"Deltas après compactage : {backup_manager.deltas_since_full}")  # 0
```

### Structure des fichiers de sauvegarde

```
backups/
  dictdb_backup_1706123456_789012.json   # Sauvegarde complète
  dictdb_delta_1706123516_123456.json    # Delta 1
  dictdb_delta_1706123576_234567.json    # Delta 2
  dictdb_delta_1706123636_345678.json    # Delta 3
  dictdb_backup_1706123696_456789.json   # Nouvelle sauvegarde complète (compactage)
```

### Restauration à partir de deltas

```python
from pathlib import Path
from dictdb import DictDB
from dictdb.storage.persist import apply_delta

BACKUP_DIR = Path("./backups")

def restaurer_base():
    """Restaure la base de données à partir des sauvegardes."""

    # Trouver la dernière sauvegarde complète
    full_backups = sorted(BACKUP_DIR.glob("dictdb_backup_*.json"))
    if not full_backups:
        raise FileNotFoundError("Aucune sauvegarde complète trouvée")

    latest_full = full_backups[-1]
    print(f"Chargement de la base complète : {latest_full.name}")

    # Charger la base complète
    db = DictDB.load(str(latest_full), "json")

    # Extraire le timestamp de la sauvegarde
    backup_timestamp = latest_full.stem.replace("dictdb_backup_", "")

    # Appliquer les deltas suivants
    deltas = sorted(BACKUP_DIR.glob("dictdb_delta_*.json"))
    for delta_file in deltas:
        delta_timestamp = delta_file.stem.replace("dictdb_delta_", "")
        if delta_timestamp > backup_timestamp:
            affected = apply_delta(db, delta_file)
            print(f"Delta appliqué : {delta_file.name} ({affected} records)")

    return db

# Exécuter la restauration
ma_base = restaurer_base()
print(f"Base restaurée : {len(ma_base.list_tables())} tables")
```

## Gestion de la concurrence (Thread-Safety)

« Notre application va recevoir des requêtes de plusieurs threads en même temps », expliqua Sarah. « Comment s'assurer que tout reste cohérent ? »

### Lectures concurrentes

```python
import threading
from dictdb import DictDB

db = DictDB()
db.create_table("products")
products = db.get_table("products")

# Remplissage initial
for i in range(1000):
    products.insert({"name": f"Produit {i}", "price": i * 9.99, "stock": i % 100})

def lecteur_thread(thread_id: int):
    """Fonction exécutée par chaque thread lecteur."""
    # Plusieurs threads peuvent lire en même temps sans se bloquer
    results = products.select(
        where=products.price > 500,
        order_by="-price",
        limit=10,
    )
    print(f"Thread {thread_id} : trouvé {len(results)} produits chers")

# Lancer 10 threads de lecture en parallèle
threads = [threading.Thread(target=lecteur_thread, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("Toutes les lectures sont terminées")
```

### Écritures concurrentes

```python
import threading
import time
from dictdb import DictDB

db = DictDB()
db.create_table("counters", primary_key="name")
counters = db.get_table("counters")

# Initialiser un compteur
counters.insert({"name": "visites", "value": 0})

def incrementer_compteur_safe(db_instance: DictDB, iterations: int):
    """
    Version sûre utilisant des copies pour éviter les effets de bord.
    """
    table = db_instance.get_table("counters")
    for _ in range(iterations):
        # Lire et mettre à jour de manière atomique
        # Utiliser copy=True pour avoir ses propres données
        current = table.select(where=table.name == "visites", copy=True)
        if current:
            new_value = current[0]["value"] + 1
            table.update({"value": new_value}, where=table.name == "visites")
```

## Opérations asynchrones

« Pour notre API web, nous ne pouvons pas nous permettre de bloquer sur les entrées/sorties », nota Thomas.

```python
import asyncio
from dictdb import DictDB

async def main():
    # Créer et remplir la base
    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")

    for i in range(1000):
        users.insert({"name": f"User{i}", "email": f"user{i}@example.com"})

    # Sauvegarde asynchrone - ne bloque pas la boucle d'événements
    print("Démarrage de la sauvegarde asynchrone...")
    await db.async_save("backup_async.json", "json")
    print("Sauvegarde terminée")

    # Chargement asynchrone
    print("Chargement asynchrone...")
    db_loaded = await DictDB.async_load("backup_async.json", "json")
    print(f"Chargé {db_loaded.get_table('users').count()} utilisateurs")

# Dans une application asynchrone (FastAPI, aiohttp, etc.)
asyncio.run(main())
```

## Configuration avancée des logs

« L'observabilité est cruciale », déclara Lucas. « Configurons nos logs pour la production. »

```python
from dictdb import configure_logging

# Configuration de production :
# - Niveau INFO pour la console (erreurs visibles)
# - Tous les logs dans un fichier
# - Format JSON pour l'agrégation (ELK, Splunk, etc.)
configure_logging(
    level="INFO",
    console=True,
    logfile="./logs/dictdb.log",
    json=True,
)
```

### Échantillonnage des logs DEBUG

```python
from dictdb import configure_logging

# En production avec beaucoup de trafic, échantillonner les logs DEBUG
# pour ne pas noyer les logs importants
configure_logging(
    level="DEBUG",
    console=True,
    logfile="./logs/dictdb_debug.log",
    sample_debug_every=100,  # On ne logue qu'un DEBUG sur 100
)
```

## Meilleures pratiques de gestion des erreurs

« En production, les erreurs sont inévitables », philosopha Sarah. « Ce qui compte, c'est de savoir les gérer proprement. »

```python
from dictdb import (
    DictDB,
    DictDBError,
    DuplicateKeyError,
    RecordNotFoundError,
    SchemaValidationError,
    TableNotFoundError,
)

def executer_operation_robuste(db: DictDB, operation: str, **kwargs):
    """
    Exécute une opération avec une gestion complète des erreurs.
    """
    try:
        table = db.get_table(kwargs["table"])
        if operation == "insert":
            return table.insert(kwargs["record"])
        elif operation == "update":
            return table.update(kwargs["changes"], where=kwargs.get("where"))
        elif operation == "delete":
            return table.delete(where=kwargs.get("where"))

    except TableNotFoundError:
        print(f"Erreur : Table '{kwargs['table']}' introuvable")
        raise
    except DuplicateKeyError:
        print("Erreur : Cette clé existe déjà")
        # Possibilité d'utiliser upsert ici
        raise
    except SchemaValidationError as e:
        print(f"Erreur de validation : {e}")
        raise
    except RecordNotFoundError:
        print("Avertissement : Aucun enregistrement trouvé")
        return 0
    except DictDBError as e:
        print(f"Erreur DictDB : {e}")
        raise
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        raise
```

## Conseils de performance

« Pour finir, optimisons la vitesse », conclut Lucas.

### 1. Utiliser les index à bon escient

```python
# Index Hash pour les recherches d'égalité exacte -> O(1)
transactions.create_index("customer_id", index_type="hash")

# Index trié pour les plages de valeurs et le tri -> O(log n)
transactions.create_index("amount", index_type="sorted")
```

### 2. Désactiver la copie pour les lectures seules

```python
# Beaucoup plus rapide pour les gros volumes, mais attention :
# INTERDICTION de modifier les résultats !
results = logs.select(limit=10000, copy=False)
```

### 3. Insertions par lots (Batch)

```python
# Pratique recommandée : insertion d'une liste entière
events.insert(liste_de_10000_evenements)

# Avec une taille de lot explicite pour les très gros volumes
events.insert(gros_volume, batch_size=1000)
```

### 4. Ignorer la validation pour les données sûres

```python
# Si les données viennent d'une source interne déjà validée
table.insert(donnees_de_confiance, skip_validation=True)
```

## Ce que nous avons appris

Grâce à cette préparation minutieuse, l'équipe de TechFlow SARL maîtrise désormais :

1. **BackupManager** : Configurer des sauvegardes périodiques avec surveillance et alertes.
2. **Sauvegardes incrémentales** : Économiser des E/S en n'enregistrant que les deltas.
3. **Thread-safety** : Utiliser correctement le modèle de concurrence de DictDB.
4. **Opérations asynchrones** : Intégrer la base de données dans une boucle d'événements non bloquante.
5. **Logging de production** : Configurer des logs structurés (JSON) et échantillonnés.
6. **Gestion des erreurs** : Implémenter des blocs try/except robustes pour chaque type d'exception.
7. **Optimisations** : Utiliser les index, désactiver les copies inutiles et privilégier les traitements par lots.

« Notre application est fin prête pour le monde réel », conclut Sarah. « Nous avons la robustesse, la visibilité et la vitesse nécessaires pour réussir notre lancement. »

---

*Fin de l'épopée TechFlow SARL. Que vos bases de données soient toujours sauvegardées et vos index judicieusement choisis !*