# Schémas

Les schémas fournissent une validation de type pour les enregistrements de table. Lorsqu'un schéma est défini, toutes les opérations d'insertion et de mise à jour valident les enregistrements par rapport à celui-ci.

## Définition d'un Schéma

Un schéma est un dictionnaire associant les noms de champs aux types Python :

```python
schema = {
    "id": int,
    "name": str,
    "email": str,
    "age": int,
    "active": bool,
}

db.create_table("users", primary_key="id", schema=schema)
```

## Types Supportés

Les schémas supportent les types Python standard :

- `str` - Chaînes de caractères
- `int` - Entiers
- `float` - Nombres à virgule flottante
- `bool` - Booléens
- `list` - Listes (tout contenu)
- `dict` - Dictionnaires (tout contenu)

## Comportement de Validation

### Champs Obligatoires

Tous les champs du schéma sont obligatoires :

```python
schema = {"id": int, "name": str, "email": str}
db.create_table("users", schema=schema)
users = db.get_table("users")

# Un champ manquant lève une erreur
users.insert({"id": 1, "name": "Alice"})
# SchemaValidationError: Missing field 'email' as defined in schema.
```

### Vérification de Type

Les valeurs des champs doivent correspondre au type attendu :

```python
# Un type incorrect lève une erreur
users.insert({"id": "one", "name": "Alice", "email": "alice@example.com"})
# SchemaValidationError: Field 'id' expects type 'int', got 'str'.
```

### Champs Supplémentaires

Les champs absents du schéma sont rejetés :

```python
users.insert({"id": 1, "name": "Alice", "email": "alice@example.com", "phone": "123"})
# SchemaValidationError: Field 'phone' is not defined in the schema.
```

## Clé Primaire dans le Schéma

Si la clé primaire n'est pas dans le schéma, elle est automatiquement ajoutée comme `int` :

```python
schema = {"name": str, "email": str}
db.create_table("users", primary_key="id", schema=schema)

# "id" est automatiquement ajouté au schéma comme int
# Les IDs auto-générés fonctionnent comme prévu
users.insert({"name": "Alice", "email": "alice@example.com"})  # id=1
```

## Validation des Mises à Jour

Les mises à jour sont également validées par rapport au schéma :

```python
# Une mise à jour invalide lève une erreur
users.update({"age": "thirty"}, where=Condition(users.name == "Alice"))
# SchemaValidationError: Field 'age' expects type 'int', got 'str'.
```

Les mises à jour sont atomiques - si la validation échoue, aucun enregistrement n'est modifié.

## Introspection du Schéma

```python
# Obtenir les noms des champs du schéma
users.schema_fields()  # ["id", "name", "email"]

# Accéder au schéma complet
users.schema  # {"id": int, "name": str, "email": str}
```

## Tables Sans Schéma

Sans schéma, les tables acceptent n'importe quelle structure d'enregistrement :

```python
db.create_table("flexible")
flexible = db.get_table("flexible")

# N'importe quels champs sont autorisés
flexible.insert({"x": 1})
flexible.insert({"a": "hello", "b": [1, 2, 3], "c": {"nested": True}})
```

## Persistance

Les schémas sont préservés lors de la sauvegarde et du chargement :

```python
schema = {"id": int, "name": str, "score": float}
db.create_table("players", schema=schema)

# Sauvegarde
db.save("game.json", file_format="json")

# Chargement - le schéma est restauré
db = DictDB.load("game.json", file_format="json")
players = db.get_table("players")
players.schema  # {"id": int, "name": str, "score": float}
```

## Exemple

```python
from dictdb import DictDB, Condition, SchemaValidationError

db = DictDB()

# Définition du schéma
product_schema = {
    "sku": str,
    "name": str,
    "price": float,
    "quantity": int,
    "active": bool,
}

db.create_table("products", primary_key="sku", schema=product_schema)
products = db.get_table("products")

# Insertion valide
products.insert({
    "sku": "ABC123",
    "name": "Widget",
    "price": 19.99,
    "quantity": 100,
    "active": True,
})

# Erreurs de validation
try:
    products.insert({
        "sku": "DEF456",
        "name": "Gadget",
        "price": "cheap",  # Devrait être un float
        "quantity": 50,
        "active": True,
    })
except SchemaValidationError as e:
    print(e)  # Field 'price' expects type 'float', got 'str'.

# Mise à jour avec validation
products.update(
    {"quantity": 150},
    where=Condition(products.sku == "ABC123")
)
```
