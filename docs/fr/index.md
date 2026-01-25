# DictDB

<p align="center">
  <img src="../assets/dictdb-logo.png" alt="Logo DictDB" width="600"/>
</p>

**DictDB** est une base de données en mémoire pour Python, basée sur des dictionnaires. Elle propose des opérations CRUD de type SQL, des schémas de données facultatifs, des index ultra-rapides et un DSL de requête particulièrement fluide.

C'est l'outil idéal pour le prototypage, les tests unitaires et les workflows relationnels légers qui ne nécessitent pas le déploiement d'un moteur de base de données complet.

## Fonctionnalités principales

- **CRUD complet** - Profitez des opérations `insert`, `select`, `update`, `delete` et `upsert` avec une sémantique familière.
- **DSL de requête fluide** - Construisez vos conditions directement avec les opérateurs Python : `table.age >= 18`, `table.name.like("A%")`.
- **Opérateurs logiques** - Utilisez les fonctions `And`, `Or` et `Not` pour composer des requêtes complexes et lisibles.
- **Agrégations** - Calculez des statistiques (`Count`, `Sum`, `Avg`, `Min`, `Max`) avec support du `GROUP BY`.
- **Index performants** - Index de hachage pour des recherches d'égalité en O(1) et index triés pour les requêtes par plage.
- **Schémas optionnels** - Gardez la flexibilité du dictionnaire ou imposez une validation de type stricte quand c'est nécessaire.
- **Import/Export CSV** - Chargez vos données depuis des fichiers CSV et exportez vos résultats de requêtes en un clin d'œil.
- **Persistance** - Sauvegardez et chargez vos bases de données aux formats JSON ou Pickle.
- **Sauvegardes automatiques** - Gestion intégrée des sauvegardes périodiques et incrémentales.
- **Thread-Safe** - Verrous lecteur-écrivain intégrés pour un accès concurrent sans risque.
- **Support asynchrone** - Opérations de sauvegarde et de chargement non bloquantes pour vos applications async.
- **Zéro configuration** - Pas de serveur à installer, pas de setup complexe : juste du Python pur.

## Exemple rapide

```python
from dictdb import DictDB, And

# Créer la base de données et une table
db = DictDB()
db.create_table("users", primary_key="id")
users = db.get_table("users")

# Insérer des enregistrements
users.insert({"name": "Alice", "age": 30, "role": "admin"})
users.insert({"name": "Bob", "age": 25, "role": "user"})

# Requête avec le DSL fluide (l'enveloppe Condition est facultative)
admins = users.select(where=users.role == "admin")
adults = users.select(where=users.age >= 18)

# Combiner des conditions avec And/Or/Not
senior_admins = users.select(where=And(users.role == "admin", users.age >= 30))

# Mises à jour et suppressions
users.update({"age": 31}, where=users.name == "Alice")
users.delete(where=users.name == "Bob")

# Persistance sur disque
db.save("data.json", file_format="json")
```

## Installation

```bash
pip install dctdb
```

```python
from dictdb import DictDB, Condition
```

!!! note "Nom du paquet"
    Le paquet sur PyPI est nommé `dctdb`, mais le nom à utiliser pour l'import est `dictdb`.

## Prérequis

- Python 3.13+

## Licence

Licence Apache 2.0 - voir le fichier [LICENSE](https://github.com/mhbxyz/dictdb/blob/main/LICENSE) pour plus de détails.