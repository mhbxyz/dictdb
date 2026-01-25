# Concurrence

DictDB assure la sécurité des données (Thread-Safety) grâce à un mécanisme de verrous lecteur-écrivain (Reader-Writer Locks) appliqué à chaque table.

## Modèle de verrouillage

Chaque `Table` possède son propre verrou `RWLock` indépendant qui :

- Autorise plusieurs lectures simultanées.
- Garantit un accès exclusif à un seul écrivain à la fois.
- Prévient les conflits lecture-écriture et écriture-écriture.

## Opérations de lecture

Plusieurs threads peuvent consulter les données simultanément sans s'attendre :

```python
import threading
from dictdb import DictDB, Condition

db = DictDB()
db.create_table("users")
users = db.get_table("users")

# Remplissage
for i in range(1000):
    users.insert({"name": f"User {i}"})

def lecteur(thread_id):
    # Les lecteurs s'exécutent en parallèle
    results = users.select(where=Condition(users.name.startswith("User 1")))
    print(f"Thread {thread_id} : {len(results)} enregistrements trouvés")

# Lancer 10 threads de lecture
threads = [threading.Thread(target=lecteur, args=(i,)) for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()
```

## Opérations d'écriture

Les écrivains bloquent les autres threads pour garantir l'intégrité de l'opération :

```python
def ecrivain(thread_id):
    # Un seul écrivain peut modifier la table à l'instant T
    users.insert({"name": f"Nouvel utilisateur {thread_id}"})

def lecteur(thread_id):
    # Les lecteurs attendront que l'écrivain ait terminé avant de lire
    count = users.count()
    print(f"Total : {count}")
```

## Atomicité des opérations

Toutes les opérations CRUD sont atomiques. Par exemple, l'auto-incrémentation des identifiants ou la validation par schéma sont protégées par le verrou de la table.

## Copie des enregistrements

Par défaut, `select` retourne des **copies** des dictionnaires :

```python
# Sûr : retourne des copies indépendantes
results = users.select()
results[0]["name"] = "Modifié"  # N'affecte pas la base de données

# Rapide mais dangereux : retourne des références directes
results = users.select(copy=False)
# ATTENTION : Ne modifiez jamais ces résultats en dehors d'un verrou !
```

## Isolation par table

Les verrous sont indépendants par table. Accéder à la table `users` ne bloquera jamais l'accès à la table `products`.

## Éviter les interblocages (Deadlocks)

DictDB est conçu pour minimiser les risques d'interblocage :

- Un seul verrou par table.
- Pas de verrouillage inter-tables automatique.
- Les verrous sont systématiquement libérés à la fin de chaque méthode.

**Cependant**, soyez prudent dans votre propre code :

```python
# Risque d'interblocage
def mauvais_pattern():
    with mon_verrou_externe:
        # DictDB va demander son verrou interne à l'intérieur du vôtre
        users.insert(...) 
```

## Compatibilité avec Asyncio

Pour les applications asynchrones, DictDB propose des méthodes dédiées qui s'exécutent dans un pool de threads pour ne pas geler la boucle d'événements :

```python
import asyncio

async def sauvegarde_periodique():
    while True:
        await asyncio.sleep(60)
        # Ne bloque pas le reste de votre application async
        await db.async_save("backup.json", "json")
```

## Recommandations

1. **Gardez vos opérations courtes** : Un verrou maintenu trop longtemps fera attendre les autres threads.
2. **Utilisez `copy=False` avec discernement** : Uniquement pour des lectures massives où la performance est critique et où vous êtes sûr de ne pas modifier les données.
3. **Privilégiez les mises à jour par lots** : Effectuer une seule grosse modification est plus efficace que de nombreuses petites modifications unitaires.