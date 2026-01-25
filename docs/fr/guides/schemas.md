# Schémas

Les schémas permettent d'imposer une validation de type stricte sur les enregistrements d'une table. Lorsqu'un schéma est défini, chaque insertion ou mise à jour est vérifiée pour garantir l'intégrité des données.

## Définir un schéma

Un schéma se définit sous la forme d'un dictionnaire associant le nom des colonnes aux types Python :

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

## Types supportés

DictDB accepte les types Python standards suivants :

- `str` - Chaînes de caractères.
- `int` - Nombres entiers.
- `float` - Nombres à virgule flottante.
- `bool` - Booléens.
- `list` - Listes (quel que soit leur contenu).
- `dict` - Dictionnaires (quel que soit leur contenu).

## Comportement de la validation

### Champs obligatoires

Dès qu'un schéma est présent, tous les champs qu'il définit deviennent **obligatoires**.

```python
schema = {"id": int, "name": str}
db.create_table("users", schema=schema)
users = db.get_table("users")

# Ceci lèvera une erreur car 'name' manque
users.insert({"id": 1})
# SchemaValidationError: Missing field 'name' as defined in schema.
```

### Vérification du type

Le type de chaque valeur est scrupuleusement vérifié :

```python
# Erreur : 'id' attend un entier, pas une chaîne
users.insert({"id": "un", "name": "Alice"})
# SchemaValidationError: Field 'id' expects type 'int', got 'str'.
```

### Champs interdits

Tout champ non mentionné dans le schéma sera rejeté lors de l'insertion.

```python
# Erreur : 'phone' n'est pas dans le schéma
users.insert({"id": 1, "name": "Alice", "phone": "0123"})
# SchemaValidationError: Field 'phone' is not defined in the schema.
```

## Clé primaire et schéma

Si vous oubliez d'inclure votre clé primaire dans le dictionnaire du schéma, DictDB l'ajoutera automatiquement avec le type `int`. Les identifiants auto-générés continueront donc de fonctionner normalement.

## Validation des mises à jour

La validation s'applique aussi à la méthode `update()` :

```python
# Erreur : 'age' doit être un entier
users.update({"age": "trente"}, where=Condition(users.id == 1))
```

L'opération de mise à jour est atomique : si la validation échoue sur un seul enregistrement du lot, aucun changement n'est appliqué à la base.

## Consulter le schéma

```python
# Liste des champs attendus
users.schema_fields()  # ["id", "name", "age"]

# Accès au dictionnaire complet
print(users.schema)
```

## Tables sans schéma

Si vous ne spécifiez pas de schéma, la table accepte n'importe quelle structure de données. C'est le mode "dictionnaire pur", idéal pour le prototypage rapide ou les données très hétérogènes.

## Persistance

Les schémas sont sauvegardés dans les fichiers JSON ou Pickle. Lorsque vous rechargez votre base, les contraintes de type sont immédiatement rétablies.

## Exemple complet

```python
from dictdb import DictDB, SchemaValidationError

db = DictDB()

product_schema = {
    "sku": str,
    "name": str,
    "price": float,
    "active": bool,
}

db.create_table("products", primary_key="sku", schema=product_schema)
products = db.get_table("products")

# Insertion valide
products.insert({
    "sku": "TV-001",
    "name": "Télévision 4K",
    "price": 499.99,
    "active": True,
})

# Exemple d'erreur capturée
try:
    products.insert({
        "sku": "RD-002",
        "name": "Radio",
        "price": "gratuit",  # Doit être un float !
        "active": True,
    })
except SchemaValidationError as e:
    print(f"Données invalides : {e}")
```