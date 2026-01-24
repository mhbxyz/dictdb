# Ma boutique en ligne

## Introduction

Sophie avait toujours reve de transformer sa passion pour l'artisanat en activite commerciale. Apres des mois de preparation, de nuits blanches a concevoir son site web et d'innombrables visites sur les marches d'artisans locaux, elle etait enfin prete a lancer « Les Tresors de Sophie » - une boutique en ligne specialisee dans la decoration interieure et les cadeaux artisanaux.

Mais avant de pouvoir vendre son premier produit, Sophie faisait face a un defi que beaucoup de nouveaux entrepreneurs rencontrent : comment gerer un catalogue de produits qui doit etre fiable, consultable et facile a mettre a jour ? Elle avait besoin d'un systeme capable de :

- S'assurer que chaque produit possede des informations completes et correctement typees
- Trouver rapidement des produits par categorie ou gamme de prix
- Gerer des recherches clients complexes
- Rendre les mises a jour de stock transparentes

Suivons Sophie dans la construction de son catalogue de produits avec DictDB.

## Creer le catalogue avec validation de schema

Sophie commence par definir la structure de ses produits. Elle veut s'assurer que chaque article possede toutes les informations requises et que les types de donnees sont corrects - plus question d'entrer accidentellement « quinze euros » au lieu de 15.00.

```python
from dictdb import DictDB, Condition, And, Or, Not

# Sarah creates her database
db = DictDB()

# Define the product schema
product_schema = {
    "sku": str,           # Unique product reference
    "name": str,          # Product name
    "description": str,   # Detailed description
    "category": str,      # Product category
    "price": float,       # Price in dollars
    "stock": int,         # Quantity in stock
    "active": bool,       # Available for sale
}

# Create the table with schema validation
db.create_table("products", primary_key="sku", schema=product_schema)
products = db.get_table("products")
```

Maintenant, si Sophie essaie d'inserer un produit incomplet ou avec des types de donnees incorrects, DictDB detectera l'erreur immediatement :

```python
from dictdb import SchemaValidationError

# Attempting to insert an incomplete product
try:
    products.insert({
        "sku": "DEC001",
        "name": "Lavender Candle",
        # Missing: description, category, price, stock, and active!
    })
except SchemaValidationError as e:
    print(f"Error: {e}")
    # Error: Missing field 'description' as defined in schema.

# Attempting to insert with incorrect type
try:
    products.insert({
        "sku": "DEC001",
        "name": "Lavender Candle",
        "description": "Handcrafted lavender-scented candle",
        "category": "Decor",
        "price": "fifteen dollars",  # Should be a float!
        "stock": 50,
        "active": True,
    })
except SchemaValidationError as e:
    print(f"Error: {e}")
    # Error: Field 'price' expects type 'float', got 'str'.
```

Avec la validation de schema en place, Sophie peut ajouter ses produits en toute confiance :

```python
# Adding the first products
products.insert({
    "sku": "DEC001",
    "name": "Bougie Parfumee Lavande",
    "description": "Bougie artisanale a la lavande de Provence",
    "category": "Decor",
    "price": 15.90,
    "stock": 50,
    "active": True,
})

products.insert({
    "sku": "DEC002",
    "name": "Vase Ceramique Bleu",
    "description": "Vase fait main en ceramique emaillee bleue",
    "category": "Decor",
    "price": 45.00,
    "stock": 12,
    "active": True,
})

products.insert({
    "sku": "GFT001",
    "name": "Coffret The Bio",
    "description": "Assortiment de 5 thes bio dans un coffret en bois",
    "category": "Cadeaux",
    "price": 29.90,
    "stock": 30,
    "active": True,
})

products.insert({
    "sku": "GFT002",
    "name": "Carnet en Cuir",
    "description": "Carnet artisanal avec couverture en cuir veritable",
    "category": "Cadeaux",
    "price": 35.00,
    "stock": 25,
    "active": True,
})

products.insert({
    "sku": "DEC003",
    "name": "Miroir Boheme",
    "description": "Miroir rond avec cadre en macrame fait main",
    "category": "Decor",
    "price": 89.00,
    "stock": 8,
    "active": True,
})

products.insert({
    "sku": "ART001",
    "name": "Kit Peinture Aquarelle",
    "description": "Kit complet pour debutants en peinture aquarelle",
    "category": "Loisirs",
    "price": 55.00,
    "stock": 0,
    "active": False,  # Out of stock
})

products.insert({
    "sku": "GFT003",
    "name": "Bouquet de Fleurs Sechees",
    "description": "Bouquet compose de fleurs naturelles sechees",
    "category": "Cadeaux",
    "price": 42.50,
    "stock": 15,
    "active": True,
})

products.insert({
    "sku": "DEC004",
    "name": "Coussin Velours Emeraude",
    "description": "Coussin decoratif en velours vert emeraude",
    "category": "Decor",
    "price": 32.00,
    "stock": 20,
    "active": True,
})

print(f"Catalog created with {products.count()} products!")
# Catalog created with 8 products!
```

## Optimiser les recherches avec les index

A mesure que la boutique de Sophie grandit, elle veut s'assurer que les recherches restent rapides. Elle cree des index sur les champs les plus frequemment recherches par les clients.

```python
# Hash index for category searches (exact equality)
products.create_index("category", index_type="hash")

# Sorted index for price searches (range queries)
products.create_index("price", index_type="sorted")

# Check which fields are indexed
print(f"Indexed fields: {products.indexed_fields()}")
# Indexed fields: ['category', 'price']
```

**Pourquoi deux types d'index ?**

- **Index hash** : Parfait pour les recherches d'egalite (`category == "Decor"`). Fournit des recherches en temps constant O(1).
- **Index trie** : Ideal pour les recherches par plage (`price >= 20` et `price <= 50`). Fournit des recherches en temps logarithmique O(log n).

## Requetes avancees avec And, Or, Not

Les clients de Sophie ont des besoins varies. Voyons comment elle peut repondre a leurs demandes de recherche.

### Combiner des conditions avec And

Un client cherche des articles de decoration a moins de 50 euros :

```python
# Decor products under 50 euros
results = products.select(
    where=And(
        products.category == "Decor",
        products.price < 50,
        products.active == True
    ),
    order_by="price"
)

print("Decor under 50 euros:")
for p in results:
    print(f"  - {p['name']}: {p['price']} euros")
# Decor under 50 euros:
#   - Bougie Parfumee Lavande: 15.9 euros
#   - Coussin Velours Emeraude: 32.0 euros
#   - Vase Ceramique Bleu: 45.0 euros
```

### Utiliser Or pour elargir la recherche

Un client hesite entre la decoration et les cadeaux :

```python
# Products in Decor OR Cadeaux categories
results = products.select(
    where=And(
        Or(
            products.category == "Decor",
            products.category == "Cadeaux"
        ),
        products.active == True
    ),
    order_by="category"
)

print(f"Decor and Cadeaux: {len(results)} products available")
# Decor and Cadeaux: 7 products available
```

### Exclure avec Not

Un client veut tout sauf la decoration :

```python
# Everything except decor
results = products.select(
    where=And(
        Not(products.category == "Decor"),
        products.active == True
    )
)

print("Products outside Decor:")
for p in results:
    print(f"  - [{p['category']}] {p['name']}")
# Products outside Decor:
#   - [Cadeaux] Coffret The Bio
#   - [Cadeaux] Carnet en Cuir
#   - [Cadeaux] Bouquet de Fleurs Sechees
```

### Conditions imbriquees complexes

Un client a un budget de 30 a 50 euros et cherche un cadeau OU un article de decoration premium :

```python
# Complex query
results = products.select(
    where=And(
        products.active == True,
        Or(
            # Gifts between 30 and 50 euros
            And(
                products.category == "Cadeaux",
                products.price >= 30,
                products.price <= 50
            ),
            # OR premium decor (over 80 euros)
            And(
                products.category == "Decor",
                products.price >= 80
            )
        )
    )
)

print("Cadeaux 30-50 euros ou Decor Premium:")
for p in results:
    print(f"  - {p['name']} ({p['category']}): {p['price']} euros")
# Cadeaux 30-50 euros ou Decor Premium:
#   - Carnet en Cuir (Cadeaux): 35.0 euros
#   - Bouquet de Fleurs Sechees (Cadeaux): 42.5 euros
#   - Miroir Boheme (Decor): 89.0 euros
```

## Recherche par plage de prix avec BETWEEN

Sophie a souvent besoin de filtrer par gamme de prix. La methode `between()` simplifie ces recherches.

```python
# Products between 25 and 45 euros (inclusive)
results = products.select(
    where=And(
        products.price.between(25, 45),
        products.active == True
    ),
    order_by="price"
)

print("Products between 25 and 45 euros:")
for p in results:
    print(f"  - {p['name']}: {p['price']} euros")
# Products between 25 and 45 euros:
#   - Coffret The Bio: 29.9 euros
#   - Coussin Velours Emeraude: 32.0 euros
#   - Carnet en Cuir: 35.0 euros
#   - Bouquet de Fleurs Sechees: 42.5 euros
#   - Vase Ceramique Bleu: 45.0 euros
```

La methode `between()` est equivalente a `(price >= 25) & (price <= 45)`, mais plus lisible et optimisee lors de l'utilisation d'un index trie.

## Recherche textuelle avec LIKE

Les clients utilisent souvent la barre de recherche. Sophie implemente une recherche basee sur des motifs.

```python
# Search for products starting with "Bougie" or "Bouquet"
results = products.select(
    where=products.name.like("Bou%")
)

print("Products starting with 'Bou':")
for p in results:
    print(f"  - {p['name']}")
# Products starting with 'Bou':
#   - Bougie Parfumee Lavande
#   - Bouquet de Fleurs Sechees
```

### Motifs LIKE disponibles

```python
# % = any sequence of characters
# _ = exactly one character

# Products containing "cuir" in the description
results = products.select(
    where=products.description.like("%cuir%")
)
print("Leather products:")
for p in results:
    print(f"  - {p['name']}")
# Leather products:
#   - Carnet en Cuir

# Products with "DEC" followed by 3 characters in the SKU
results = products.select(
    where=products.sku.like("DEC___")
)
print(f"DEC products: {len(results)} items")
# DEC products: 4 items
```

## Recherche insensible a la casse

Les clients ne font pas toujours attention aux majuscules. Sophie utilise les variantes insensibles a la casse pour s'assurer qu'ils trouvent ce qu'ils cherchent.

```python
# Case-insensitive search with icontains
results = products.select(
    where=products.name.icontains("LAVANDE")  # Even typed in uppercase
)
print("Search 'LAVANDE':")
for p in results:
    print(f"  - {p['name']}")
# Search 'LAVANDE':
#   - Bougie Parfumee Lavande

# ilike for case-insensitive patterns
results = products.select(
    where=products.description.ilike("%BIO%")
)
print("Search 'BIO' (case-insensitive):")
for p in results:
    print(f"  - {p['name']}")
# Search 'BIO' (case-insensitive):
#   - Coffret The Bio
```

### Toutes les variantes disponibles

| Methode sensible a la casse | Methode insensible a la casse | Usage |
|----------------------------|------------------------------|-------|
| `==` (egalite) | `iequals()` | Correspondance exacte |
| `contains()` | `icontains()` | Contient du texte |
| `startswith()` | `istartswith()` | Commence par |
| `endswith()` | `iendswith()` | Termine par |
| `like()` | `ilike()` | Motif SQL avec % et _ |

```python
# Example with istartswith
results = products.select(
    where=products.name.istartswith("COFFRET")
)
print("Products starting with 'coffret' (case-insensitive):")
for p in results:
    print(f"  - {p['name']}")
# Products starting with 'coffret' (case-insensitive):
#   - Coffret The Bio
```

## Mises a jour de stock avec Upsert

Sophie recoit regulierement des livraisons. Elle utilise `upsert()` pour mettre a jour son stock : si le produit existe, il est mis a jour ; sinon, il est cree.

```python
# Shipment arrival: updating stock for an existing product
sku, action = products.upsert({
    "sku": "DEC001",
    "name": "Bougie Parfumee Lavande",
    "description": "Bougie artisanale a la lavande de Provence",
    "category": "Decor",
    "price": 15.90,
    "stock": 75,  # New stock: 50 + 25 = 75
    "active": True,
})
print(f"Product {sku}: {action}")
# Product DEC001: updated

# New product in the shipment
sku, action = products.upsert({
    "sku": "DEC005",
    "name": "Photophore en Verre",
    "description": "Photophore artisanal en verre souffle",
    "category": "Decor",
    "price": 24.90,
    "stock": 30,
    "active": True,
})
print(f"Product {sku}: {action}")
# Product DEC005: inserted
```

### Strategies de conflit

La methode `upsert()` accepte un parametre `on_conflict` pour gerer les doublons :

```python
# on_conflict="update" (default): updates if exists
sku, action = products.upsert(
    {"sku": "DEC001", "name": "Bougie Lavande", "description": "...",
     "category": "Decor", "price": 16.90, "stock": 80, "active": True},
    on_conflict="update"
)
print(f"{sku}: {action}")  # DEC001: updated

# on_conflict="ignore": does nothing if exists
sku, action = products.upsert(
    {"sku": "DEC001", "name": "Autre Bougie", "description": "...",
     "category": "Decor", "price": 99.00, "stock": 1, "active": True},
    on_conflict="ignore"
)
print(f"{sku}: {action}")  # DEC001: ignored

# on_conflict="error": raises an exception if exists
from dictdb import DuplicateKeyError

try:
    products.upsert(
        {"sku": "DEC001", "name": "Test", "description": "...",
         "category": "Decor", "price": 10.00, "stock": 1, "active": True},
        on_conflict="error"
    )
except DuplicateKeyError:
    print("Product already exists!")
# Product already exists!
```

## Resume

Dans cet exemple, Sophie a appris a :

1. **Valider les donnees avec un schema** : S'assurer que chaque produit possede tous les champs requis avec les types corrects
2. **Creer des index** : Utiliser des index hash pour les recherches d'egalite et des index tries pour les requetes par plage
3. **Combiner des conditions** : Utiliser `And`, `Or` et `Not` pour des requetes complexes
4. **Filtrer par plage** : Utiliser `between()` pour les recherches par gamme de prix
5. **Rechercher du texte** : Utiliser `like()` avec les motifs `%` et `_`
6. **Ignorer la casse** : Utiliser `icontains()`, `ilike()` et autres variantes insensibles a la casse
7. **Gerer le stock** : Utiliser `upsert()` pour creer ou mettre a jour des produits

Sophie est maintenant prete a lancer sa boutique en ligne avec un systeme de gestion de catalogue robuste et performant !
