# Premiers pas

## Installation

```bash
pip install dctdb
```

```python
from dictdb import DictDB, Condition
```

!!! remarque "Nom du paquet"
    Le paquet PyPI est `dctdb`, mais le nom d'import est `dictdb`.

### Configuration pour le développement

Clonez le dépôt et installez les dépendances :

```bash
git clone https://github.com/mhbxyz/dictdb.git
cd dictdb
make setup
```

Ou manuellement avec [uv](https://docs.astral.sh/uv/) :

```bash
uv sync
```

### Depuis les sources

```bash
pip install -e .
```

## Utilisation de base

### Créer une base de données

```python
from dictdb import DictDB

db = DictDB()
```

### Créer des tables

```python
# Créer une table avec la clé primaire par défaut "id"
db.create_table("users")

# Créer une table avec une clé primaire personnalisée
db.create_table("products", primary_key="sku")

# Obtenir une référence vers une table
users = db.get_table("users")
products = db.get_table("products")
```

### Insérer des enregistrements

```python
# Clé primaire générée automatiquement
users.insert({"name": "Alice", "email": "alice@example.com"})
# Retourne : 1 (l'id généré automatiquement)

# Clé primaire explicite
users.insert({"id": 100, "name": "Bob", "email": "bob@example.com"})

# Champ de clé primaire personnalisé
products.insert({"sku": "ABC123", "name": "Widget", "price": 9.99})
```

### Sélectionner des enregistrements

```python
from dictdb import Condition

# Sélectionner tous les enregistrements
all_users = users.select()

# Sélectionner avec une condition
admins = users.select(where=Condition(users.role == "admin"))

# Sélectionner des colonnes spécifiques
names = users.select(columns=["name", "email"])

# Tri
sorted_users = users.select(order_by="name")
sorted_desc = users.select(order_by="-name")  # Ordre décroissant

# Pagination
page = users.select(order_by="id", limit=10, offset=20)
```

### Mettre à jour des enregistrements

```python
# Mettre à jour les enregistrements correspondants
users.update(
    {"role": "moderator"},
    where=Condition(users.name == "Alice")
)

# Retourne le nombre d'enregistrements mis à jour
```

### Supprimer des enregistrements

```python
# Supprimer les enregistrements correspondants
users.delete(where=Condition(users.name == "Bob"))

# Retourne le nombre d'enregistrements supprimés
```

### Persistance

```python
# Sauvegarder en JSON (lisible par l'humain)
db.save("database.json", file_format="json")

# Sauvegarder en Pickle (plus rapide, binaire)
db.save("database.pkl", file_format="pickle")

# Charger depuis un fichier
db = DictDB.load("database.json", file_format="json")
```

## Opérations sur les tables

```python
# Lister toutes les tables
db.list_tables()  # ["users", "products"]

# Obtenir les métadonnées d'une table
users.count()           # Nombre d'enregistrements
users.columns()         # Liste des noms de colonnes
users.primary_key_name()  # "id"

# Supprimer une table
db.drop_table("products")
```

## Gestion des erreurs

```python
from dictdb import (
    DuplicateKeyError,
    DuplicateTableError,
    RecordNotFoundError,
    TableNotFoundError,
    SchemaValidationError,
)

try:
    users.insert({"id": 1, "name": "Duplicate"})
except DuplicateKeyError:
    print("Un enregistrement avec cette clé existe déjà")

try:
    db.create_table("users")
except DuplicateTableError:
    print("La table existe déjà")

try:
    users.delete(where=Condition(users.name == "NonExistent"))
except RecordNotFoundError:
    print("Aucun enregistrement correspondant trouvé")
```

## Prochaines étapes

- [DSL de requête](guides/query-dsl.md) - Apprenez la syntaxe complète des requêtes
- [Index](guides/indexes.md) - Accélérez les requêtes avec des index
- [Schémas](guides/schemas.md) - Ajoutez la validation de type
- [Persistance](guides/persistence.md) - Sauvegardez et chargez des bases de données
- [Sauvegardes](guides/backups.md) - Gestion automatique des sauvegardes
