# Import/Export CSV

DictDB supporte l'importation de données depuis des fichiers CSV et l'exportation des résultats de requêtes vers CSV.

## Importation de Fichiers CSV

Utilisez `DictDB.import_csv()` pour créer une nouvelle table à partir d'un fichier CSV :

```python
from dictdb import DictDB

db = DictDB()

# Import basique
db.import_csv("users.csv", "users", primary_key="id")

# Accéder aux données importées
users = db.get_table("users")
print(users.count())  # Nombre d'enregistrements importés
```

### Options d'Import

```python
db.import_csv(
    "data.csv",
    "products",
    primary_key="id",
    delimiter=";",           # Délimiteur personnalisé (par défaut : ",")
    has_header=True,         # La première ligne est l'en-tête (par défaut : True)
    encoding="utf-8",        # Encodage du fichier (par défaut : "utf-8")
    schema={"id": int, "price": float, "name": str},  # Conversion de types
    infer_types=True,        # Détection automatique des types (par défaut : True)
    skip_validation=False,   # Ignorer la validation du schéma (par défaut : False)
)
```

### Inférence de Types

Par défaut, DictDB infère automatiquement les types de colonnes :

- Les valeurs entières (`"42"`) deviennent `int`
- Les valeurs décimales (`"3.14"`) deviennent `float`
- Tout le reste reste `str`

```python
# Contenu CSV : id,price,name
#               1,19.99,Widget

db.import_csv("products.csv", "products")
products = db.get_table("products")
rec = products.select()[0]

print(type(rec["id"]))     # <class 'int'>
print(type(rec["price"]))  # <class 'float'>
print(type(rec["name"]))   # <class 'str'>
```

### Schéma Explicite

Pour un contrôle précis, fournissez un schéma explicite :

```python
schema = {
    "id": int,
    "price": float,
    "name": str,
    "active": bool,  # Analyse "true"/"false", "1"/"0", "yes"/"no"
}

db.import_csv("products.csv", "products", schema=schema)
```

## Exportation vers CSV

Utilisez `Table.export_csv()` pour écrire des enregistrements dans un fichier CSV :

```python
from dictdb import DictDB

db = DictDB()
db.create_table("users")
users = db.get_table("users")

users.insert({"id": 1, "name": "Alice", "email": "alice@example.com"})
users.insert({"id": 2, "name": "Bob", "email": "bob@example.com"})

# Exporter tous les enregistrements
users.export_csv("users_backup.csv")
```

### Exportation avec Filtrage

```python
# Exporter uniquement les utilisateurs actifs
users.export_csv("active_users.csv", where=users.status == "active")

# Exporter en utilisant And/Or/Not
from dictdb import And

users.export_csv(
    "it_seniors.csv",
    where=And(users.department == "IT", users.years >= 5)
)
```

### Exporter des Colonnes Spécifiques

```python
# Exporter uniquement les colonnes name et email
users.export_csv("contacts.csv", columns=["name", "email"])
```

### Exporter des Résultats Pré-calculés

```python
# D'abord calculer les résultats, puis exporter
results = users.select(
    columns=["name", "email"],
    where=users.age >= 18,
    order_by="name"
)

users.export_csv("adults.csv", records=results)
```

### Options d'Exportation

```python
users.export_csv(
    "export.csv",
    columns=["id", "name", "email"],  # Sélection et ordre des colonnes
    where=users.active == True,       # Condition de filtrage
    delimiter=";",                     # Délimiteur personnalisé
    encoding="utf-8",                  # Encodage du fichier
)
```

## Exemple Aller-Retour

```python
from dictdb import DictDB

# Import depuis CSV
db = DictDB()
db.import_csv("original.csv", "data", primary_key="id")

# Modifier les données
data = db.get_table("data")
data.update({"status": "processed"}, where=data.status == "pending")

# Exporter vers CSV
data.export_csv("processed.csv")
```

## Gestion des Caractères Spéciaux

Les fichiers CSV avec des virgules, guillemets ou sauts de ligne dans les valeurs de champs sont gérés automatiquement :

```python
# Cela fonctionne correctement
users.insert({"id": 1, "name": "O'Brien, Jr.", "bio": 'Says "Hello"'})
users.export_csv("users.csv")

# La réimportation préserve les valeurs
db2 = DictDB()
db2.import_csv("users.csv", "users2")
```

## Gestion des Erreurs

```python
from dictdb import DictDB
from dictdb.exceptions import DuplicateTableError

db = DictDB()
db.create_table("users")

try:
    db.import_csv("users.csv", "users")  # La table existe déjà
except DuplicateTableError as e:
    print(f"Erreur : {e}")
```
