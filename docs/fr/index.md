# DictDB

<p align="center">
  <img src="../assets/dictdb-logo.png" alt="Logo DictDB" width="600"/>
</p>

**DictDB** est une base de données en mémoire basée sur des dictionnaires pour Python, offrant des opérations CRUD de type SQL, des schémas optionnels, des recherches rapides via des index et un DSL de requête fluide.

Parfait pour le prototypage, les tests et les workflows relationnels légers sans nécessiter un moteur de base de données complet.

## Fonctionnalités

- **CRUD de type SQL** - `insert`, `select`, `update`, `delete`, `upsert` avec une sémantique familière
- **DSL de requête fluide** - Construisez des conditions avec les opérateurs Python : `table.age >= 18`, `table.name.like("A%")`
- **Opérateurs logiques** - Fonctions `And`, `Or`, `Not` lisibles pour les requêtes complexes
- **Agrégations** - `Count`, `Sum`, `Avg`, `Min`, `Max` avec support `GROUP BY`
- **Index** - Index de hachage pour des recherches d'égalité en O(1), index triés pour les requêtes de plage
- **Schémas optionnels** - Validation de type quand vous en avez besoin, flexibilité quand vous n'en avez pas besoin
- **Import/Export CSV** - Chargez des données depuis des fichiers CSV et exportez les résultats de requête
- **Persistance** - Sauvegarde/chargement en JSON ou Pickle
- **Sauvegardes automatiques** - Support des sauvegardes périodiques et incrémentales
- **Thread-Safe** - Verrous lecteur-écrivain pour l'accès concurrent
- **Support asynchrone** - Opérations de sauvegarde/chargement non bloquantes
- **Zéro configuration** - Pas de serveur, pas d'installation, juste Python

## Exemple rapide

```python
from dictdb import DictDB, And

# Créer une base de données et une table
db = DictDB()
db.create_table("users", primary_key="id")
users = db.get_table("users")

# Insérer des enregistrements
users.insert({"name": "Alice", "age": 30, "role": "admin"})
users.insert({"name": "Bob", "age": 25, "role": "user"})

# Requête avec le DSL fluide (le wrapper Condition est optionnel)
admins = users.select(where=users.role == "admin")
adults = users.select(where=users.age >= 18)

# Combiner des conditions avec And/Or/Not
senior_admins = users.select(where=And(users.role == "admin", users.age >= 30))

# Mettre à jour et supprimer
users.update({"age": 31}, where=users.name == "Alice")
users.delete(where=users.name == "Bob")

# Persister sur le disque
db.save("data.json", file_format="json")
```

## Installation

```bash
pip install dctdb
```

```python
from dictdb import DictDB, Condition
```

!!! remarque "Nom du paquet"
    Le paquet PyPI est `dctdb`, mais le nom d'import est `dictdb`.

## Prérequis

- Python 3.13+

## Licence

Apache License 2.0 - voir [LICENSE](https://github.com/mhbxyz/dictdb/blob/main/LICENSE) pour les détails.
