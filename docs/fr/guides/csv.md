# Import/Export CSV

DictDB permet d'importer facilement des données depuis des fichiers CSV vers des tables, et d'exporter vos résultats de requêtes au format CSV.

## Importer des fichiers CSV

Utilisez `DictDB.import_csv()` pour créer automatiquement une nouvelle table à partir d'un fichier :

```python
from dictdb import DictDB

db = DictDB()

# Import simple
db.import_csv("utilisateurs.csv", "users", primary_key="id")

# Accéder aux données
users = db.get_table("users")
print(f"Importé {users.count()} lignes")
```

### Options d'importation

```python
db.import_csv(
    "produits.csv",
    "products",
    primary_key="sku",
    delimiter=";",           # Séparateur personnalisé (défaut : ",")
    has_header=True,         # Indique si la 1ère ligne est l'en-tête (défaut : True)
    encoding="utf-8",        # Encodage du fichier (défaut : "utf-8")
    schema={"id": int, "price": float},  # Forcer le typage de colonnes
    infer_types=True,        # Détection automatique des types (défaut : True)
    skip_validation=False,   # Ignorer la validation du schéma (défaut : False)
)
```

### Inférence automatique des types

Par défaut, DictDB tente de deviner le meilleur type pour chaque colonne :

- Les entiers (`"42"`) deviennent des `int`.
- Les décimaux (`"3.14"`) deviennent des `float`.
- Le reste demeure en `str`.

```python
# Contenu CSV : id,price,name
#               1,19.99,Widget

db.import_csv("data.csv", "data")
rec = db.get_table("data").select()[0]

print(type(rec["id"]))     # <class 'int'>
print(type(rec["price"]))  # <class 'float'>
```

### Utilisation d'un schéma explicite

Pour un contrôle total, vous pouvez fournir un dictionnaire de typage :

```python
schema = {
    "id": int,
    "price": float,
    "active": bool,  # Interprète "true", "false", "1", "0", "yes", "no", "oui", "non"
}

db.import_csv("data.csv", "data", schema=schema)
```

## Exporter au format CSV

Utilisez `Table.export_csv()` pour enregistrer vos données :

```python
from dictdb import DictDB

db = DictDB()
db.create_table("users")
users = db.get_table("users")

users.insert({"id": 1, "name": "Alice", "email": "alice@example.com"})

# Tout exporter
users.export_csv("sauvegarde_users.csv")
```

### Exporter avec filtrage

```python
# Exporter seulement les membres actifs
users.export_csv("actifs.csv", where=users.status == "active")

# Exporter avec une condition complexe
from dictdb import And
users.export_csv("cible.csv", where=And(users.age >= 18, users.pays == "FR"))
```

### Sélection des colonnes

```python
# Exporter uniquement le nom et l'e-mail
users.export_csv("contacts.csv", columns=["name", "email"])
```

### Exporter des résultats pré-calculés

```python
# Calculer d'abord les résultats (ex: triés), puis exporter
resultats = users.select(where=users.age >= 18, order_by="name")

users.export_csv("export_trie.csv", records=resultats)
```

## Gestion des caractères spéciaux

DictDB gère automatiquement les cas complexes (présence de virgules, de guillemets ou de sauts de ligne à l'intérieur des données) en respectant les standards du format CSV.

## Erreurs courantes

```python
from dictdb.exceptions import DuplicateTableError

try:
    # L'import échouera si la table existe déjà dans la base
    db.import_csv("data.csv", "une_table_existante")
except DuplicateTableError as e:
    print(f"Erreur : {e}")
```