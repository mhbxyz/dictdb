# Concurrence

DictDB est thread-safe grâce à des verrous lecteur-écrivain sur chaque table.

## Modèle de sécurité des threads

Chaque `Table` possède un `RWLock` indépendant qui :

- Permet plusieurs lecteurs simultanés
- Garantit un accès exclusif aux écrivains
- Empêche les conflits lecture-écriture et écriture-écriture

## Opérations de lecture

Plusieurs threads peuvent lire simultanément :

```python
import threading
from dictdb import DictDB, Condition

db = DictDB()
db.create_table("users")
users = db.get_table("users")

# Remplir les données
for i in range(1000):
    users.insert({"name": f"User {i}"})

def reader(thread_id):
    # Plusieurs lecteurs peuvent s'exécuter simultanément
    results = users.select(where=Condition(users.name.startswith("User 1")))
    print(f"Thread {thread_id} : {len(results)} enregistrements trouvés")

# Démarrer plusieurs threads lecteurs
threads = [threading.Thread(target=reader, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Opérations d'écriture

Les écrivains obtiennent un accès exclusif :

```python
def writer(thread_id):
    # Un seul écrivain à la fois
    users.insert({"name": f"New User {thread_id}"})

def reader(thread_id):
    # Les lecteurs attendent que les écrivains terminent
    count = users.count()
    print(f"Thread {thread_id} : {count} enregistrements au total")

# Charge de travail mixte lecture/écriture
threads = []
for i in range(5):
    threads.append(threading.Thread(target=writer, args=(i,)))
    threads.append(threading.Thread(target=reader, args=(i,)))

for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Opérations atomiques

Toutes les opérations CRUD sont atomiques :

### Insertion

```python
# Thread-safe : l'auto-incrémentation est protégée
pk = users.insert({"name": "Alice"})  # Retourne une clé primaire unique
```

### Mise à jour

```python
# Mise à jour atomique avec validation
# Si la validation échoue, toutes les modifications sont annulées
users.update(
    {"status": "active"},
    where=Condition(users.role == "admin")
)
```

### Suppression

```python
# Suppression atomique des enregistrements correspondants
users.delete(where=Condition(users.status == "inactive"))
```

## Copie des enregistrements

Par défaut, `select` retourne des copies des enregistrements :

```python
# Sûr : retourne des copies
results = users.select()
results[0]["name"] = "Modified"  # N'affecte pas la base de données

# Non sûr : retourne des références (plus rapide mais pas pour la modification)
results = users.select(copy=False)
# Ne modifiez pas ces enregistrements en dehors du verrou !
```

## Isolation par table

Différentes tables peuvent être accédées simultanément :

```python
# users et products ont des verrous séparés
def update_user():
    users.update({"last_login": now()}, where=Condition(users.id == 1))

def update_product():
    products.update({"stock": 99}, where=Condition(products.sku == "ABC"))

# Ces opérations peuvent s'exécuter simultanément sans se bloquer mutuellement
t1 = threading.Thread(target=update_user)
t2 = threading.Thread(target=update_product)
t1.start()
t2.start()
```

## Requêtes longues

Pour les opérations de lecture longues, considérez :

```python
# Obtenir un instantané pour le traitement
with users._lock.read_lock():
    snapshot = users.copy()  # Retourne un dict de {pk: copie_enregistrement}

# Traiter l'instantané en dehors du verrou
for pk, record in snapshot.items():
    process(record)  # D'autres threads peuvent écrire pendant le traitement
```

## Prévention des interblocages

La conception de DictDB empêche les interblocages :

- Un seul verrou par table
- Pas de verrouillage inter-tables
- Les verrous sont toujours libérés après les opérations

Cependant, votre code applicatif doit éviter :

```python
# Schéma d'interblocage potentiel (dans votre code, pas dans DictDB)
def bad_pattern():
    with external_lock:
        users.insert(...)  # DictDB acquiert son verrou à l'intérieur du vôtre

def another_bad_pattern():
    users.select(...)  # Verrou DictDB acquis
    # Si le callback tente d'acquérir external_lock détenu par bad_pattern...
```

## Compatibilité asynchrone

Pour les applications asynchrones, utilisez les méthodes de persistance asynchrones :

```python
import asyncio

async def save_periodically():
    while True:
        await asyncio.sleep(60)
        await db.async_save("backup.json", file_format="json")

# Exécute la sauvegarde dans un pool de threads, ne bloque pas la boucle d'événements
```

## Bonnes pratiques

1. **Gardez les opérations courtes** : Les verrous maintenus longtemps bloquent les autres threads
2. **Utilisez `copy=False` avec précaution** : Uniquement pour un accès en lecture seule
3. **Regroupez les mises à jour** : Plusieurs mises à jour en un seul appel sont plus rapides que plusieurs mises à jour individuelles
4. **Considérez la conception des tables** : Les tables à forte contention peuvent bénéficier d'un partitionnement

## Exemple : Application web concurrente

```python
from dictdb import DictDB, Condition, BackupManager
import threading

# Base de données partagée
db = DictDB()
db.create_table("sessions", primary_key="session_id")
db.create_table("events", primary_key="event_id")

sessions = db.get_table("sessions")
events = db.get_table("events")

# Index pour les requêtes courantes
sessions.create_index("user_id")
events.create_index("session_id")

# Sauvegarde en arrière-plan
backup = BackupManager(db, "./backups", backup_interval=60)
backup.start()

def handle_request(session_id, user_id, action):
    """Appelé depuis plusieurs threads de workers web"""

    # Lire la session (concurrent avec d'autres lectures)
    existing = sessions.select(where=Condition(sessions.session_id == session_id))

    if not existing:
        # Créer la session (accès exclusif)
        sessions.insert({"session_id": session_id, "user_id": user_id})

    # Journaliser l'événement (table différente, pas de contention avec sessions)
    events.insert({"session_id": session_id, "action": action})

# Thread de nettoyage en arrière-plan
def cleanup_old_sessions():
    while True:
        threading.Event().wait(3600)  # Chaque heure
        sessions.delete(where=Condition(sessions.last_active < one_hour_ago()))
```
