# Ma boutique en ligne

## Introduction

Sophie avait toujours rêvé de transformer sa passion pour l'artisanat en activité commerciale. Après des mois de préparation, de nuits blanches à concevoir son site web et d'innombrables visites sur les marchés d'artisans locaux, elle était enfin prête à lancer « Les Trésors de Sophie » - une boutique en ligne spécialisée dans la décoration intérieure et les cadeaux artisanaux.

Mais avant de pouvoir vendre son premier produit, Sophie faisait face à un défi que beaucoup de nouveaux entrepreneurs rencontrent : comment gérer un catalogue de produits qui doit être fiable, facilement consultable et facile à mettre à jour ? Elle avait besoin d'un système capable de :

- S'assurer que chaque produit possède des informations complètes et correctement typées
- Trouver rapidement des produits par catégorie ou gamme de prix
- Gérer des recherches clients complexes
- Rendre les mises à jour de stock transparentes

Suivons Sophie dans la construction de son catalogue de produits avec DictDB.

## Créer le catalogue avec validation de schéma

Sophie commence par définir la structure de ses produits. Elle veut s'assurer que chaque article possède toutes les informations requises et que les types de données sont corrects - plus question d'entrer accidentellement « quinze euros » au lieu de 15.00.

```python
from dictdb import DictDB, Condition, And, Or, Not

# Sophie crée sa base de données
db = DictDB()

# Définir le schéma du produit
product_schema = {
    "sku": str,           # Référence unique du produit
    "name": str,          # Nom du produit
    "description": str,   # Description détaillée
    "category": str,      # Catégorie du produit
    "price": float,       # Prix en euros
    "stock": int,         # Quantité en stock
    "active": bool,       # Disponible à la vente
}

# Créer la table avec validation de schéma
db.create_table("products", primary_key="sku", schema=product_schema)
products = db.get_table("products")
```

Maintenant, si Sophie essaie d'insérer un produit incomplet ou avec des types de données incorrects, DictDB détectera l'erreur immédiatement :

```python
from dictdb import SchemaValidationError

# Tentative d'insertion d'un produit incomplet
try:
    products.insert({
        "sku": "DEC001",
        "name": "Bougie Lavande",
        # Manquant : description, category, price, stock, et active !
    })
except SchemaValidationError as e:
    print(f"Erreur : {e}")
    # Erreur : Missing field 'description' as defined in schema.

# Tentative d'insertion avec un type incorrect
try:
    products.insert({
        "sku": "DEC001",
        "name": "Bougie Lavande",
        "description": "Bougie artisanale",
        "category": "Decor",
        "price": "quinze euros",  # Devrait être un flottant !
        "stock": 50,
        "active": True,
    })
except SchemaValidationError as e:
    print(f"Erreur : {e}")
    # Erreur : Field 'price' expects type 'float', got 'str'.
```

Avec la validation de schéma en place, Sophie peut ajouter ses produits en toute confiance :

```python
# Ajouter les premiers produits
products.insert({
    "sku": "DEC001",
    "name": "Bougie Parfumée Lavande",
    "description": "Bougie artisanale à la lavande de Provence",
    "category": "Decor",
    "price": 15.90,
    "stock": 50,
    "active": True,
})

products.insert({
    "sku": "DEC002",
    "name": "Vase Céramique Bleu",
    "description": "Vase fait main en céramique émaillée bleue",
    "category": "Decor",
    "price": 45.00,
    "stock": 12,
    "active": True,
})

products.insert({
    "sku": "GFT001",
    "name": "Coffret Thé Bio",
    "description": "Assortiment de 5 thés bio dans un coffret en bois",
    "category": "Cadeaux",
    "price": 29.90,
    "stock": 30,
    "active": True,
})

products.insert({
    "sku": "GFT002",
    "name": "Carnet en Cuir",
    "description": "Carnet artisanal avec couverture en cuir véritable",
    "category": "Cadeaux",
    "price": 35.00,
    "stock": 25,
    "active": True,
})

products.insert({
    "sku": "DEC003",
    "name": "Miroir Bohème",
    "description": "Miroir rond avec cadre en macramé fait main",
    "category": "Decor",
    "price": 89.00,
    "stock": 8,
    "active": True,
})

products.insert({
    "sku": "ART001",
    "name": "Kit Peinture Aquarelle",
    "description": "Kit complet pour débutants en peinture aquarelle",
    "category": "Loisirs",
    "price": 55.00,
    "stock": 0,
    "active": False,  # Rupture de stock
})

products.insert({
    "sku": "GFT003",
    "name": "Bouquet de Fleurs Séchées",
    "description": "Bouquet composé de fleurs naturelles séchées",
    "category": "Cadeaux",
    "price": 42.50,
    "stock": 15,
    "active": True,
})

products.insert({
    "sku": "DEC004",
    "name": "Coussin Velours Émeraude",
    "description": "Coussin décoratif en velours vert émeraude",
    "category": "Decor",
    "price": 32.00,
    "stock": 20,
    "active": True,
})

print(f"Catalogue créé avec {products.count()} produits !")
# Catalogue créé avec 8 produits !
```

## Optimiser les recherches avec les index

À mesure que la boutique de Sophie grandit, elle veut s'assurer que les recherches restent rapides. Elle crée des index sur les champs les plus fréquemment recherchés par les clients.

```python
# Index hash pour les recherches de catégorie (égalité exacte)
products.create_index("category", index_type="hash")

# Index trié pour les recherches de prix (requêtes de plage)
products.create_index("price", index_type="sorted")

# Vérifier quels champs sont indexés
print(f"Champs indexés : {products.indexed_fields()}")
# Champs indexés : ['category', 'price']
```

**Pourquoi deux types d'index ?**

- **Index hash** : Parfait pour les recherches d'égalité (`category == "Decor"`). Fournit des recherches en temps constant O(1).
- **Index trié** : Idéal pour les recherches par plage (`price >= 20` et `price <= 50`). Fournit des recherches en temps logarithmique O(log n).

## Requêtes avancées avec And, Or, Not

Les clients de Sophie ont des besoins variés. Voyons comment elle peut répondre à leurs demandes de recherche.

### Combiner des conditions avec And

Un client cherche des articles de décoration à moins de 50 euros :

```python
# Produits de décoration à moins de 50 euros
results = products.select(
    where=And(
        products.category == "Decor",
        products.price < 50,
        products.active == True
    ),
    order_by="price"
)

print("Décoration à moins de 50 euros :")
for p in results:
    print(f"  - {p['name']} : {p['price']} €")
# Décoration à moins de 50 euros :
#   - Bougie Parfumée Lavande : 15.9 €
#   - Coussin Velours Émeraude : 32.0 €
#   - Vase Céramique Bleu : 45.0 €
```

### Utiliser Or pour élargir la recherche

Un client hésite entre la décoration et les cadeaux :

```python
# Produits dans les catégories Décor OU Cadeaux
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

print(f"Décor et Cadeaux : {len(results)} produits disponibles")
# Décor et Cadeaux : 7 produits disponibles
```

### Exclure avec Not

Un client veut tout sauf la décoration :

```python
# Tout sauf la décoration
results = products.select(
    where=And(
        Not(products.category == "Decor"),
        products.active == True
    )
)

print("Produits hors Décoration :")
for p in results:
    print(f"  - [{p['category']}] {p['name']}")
# Produits hors Décoration :
#   - [Cadeaux] Coffret Thé Bio
#   - [Cadeaux] Carnet en Cuir
#   - [Cadeaux] Bouquet de Fleurs Séchées
```

### Conditions imbriquées complexes

Un client a un budget de 30 à 50 euros et cherche un cadeau OU un article de décoration premium :

```python
# Requête complexe
results = products.select(
    where=And(
        products.active == True,
        Or(
            # Cadeaux entre 30 et 50 euros
            And(
                products.category == "Cadeaux",
                products.price >= 30,
                products.price <= 50
            ),
            # OU décor premium (plus de 80 euros)
            And(
                products.category == "Decor",
                products.price >= 80
            )
        )
    )
)

print("Cadeaux 30-50€ ou Décor Premium :")
for p in results:
    print(f"  - {p['name']} ({p['category']}) : {p['price']} €")
# Cadeaux 30-50€ ou Décor Premium :
#   - Carnet en Cuir (Cadeaux) : 35.0 €
#   - Bouquet de Fleurs Séchées (Cadeaux) : 42.5 €
#   - Miroir Bohème (Decor) : 89.0 €
```

## Recherche par plage de prix avec BETWEEN

Sophie a souvent besoin de filtrer par gamme de prix. La méthode `between()` simplifie ces recherches.

```python
# Produits entre 25 et 45 euros (inclus)
results = products.select(
    where=And(
        products.price.between(25, 45),
        products.active == True
    ),
    order_by="price"
)

print("Produits entre 25 et 45 € :")
for p in results:
    print(f"  - {p['name']} : {p['price']} €")
# Produits entre 25 et 45 € :
#   - Coffret Thé Bio : 29.9 €
#   - Coussin Velours Émeraude : 32.0 €
#   - Carnet en Cuir : 35.0 €
#   - Bouquet de Fleurs Séchées : 42.5 €
#   - Vase Céramique Bleu : 45.0 €
```

La méthode `between()` est équivalente à `(price >= 25) & (price <= 45)`, mais plus lisible et optimisée lors de l'utilisation d'un index trié.

## Recherche textuelle avec LIKE

Les clients utilisent souvent la barre de recherche. Sophie implémente une recherche basée sur des motifs.

```python
# Rechercher des produits commençant par "Bougie" ou "Bouquet"
results = products.select(
    where=products.name.like("Bou%")
)

print("Produits commençant par 'Bou' :")
for p in results:
    print(f"  - {p['name']}")
# Produits commençant par 'Bou' :
#   - Bougie Parfumée Lavande
#   - Bouquet de Fleurs Séchées
```

### Motifs LIKE disponibles

```python
# % = n'importe quelle séquence de caractères
# _ = exactement un caractère

# Produits contenant "cuir" dans la description
results = products.select(
    where=products.description.like("%cuir%")
)
print("Produits en cuir :")
for p in results:
    print(f"  - {p['name']}")
# Produits en cuir :
#   - Carnet en Cuir

# Produits avec "DEC" suivi de 3 caractères dans le SKU
results = products.select(
    where=products.sku.like("DEC___")
)
print(f"Produits DEC : {len(results)} articles")
# Produits DEC : 4 articles
```

## Recherche insensible à la casse

Les clients ne font pas toujours attention aux majuscules. Sophie utilise les variantes insensibles à la casse pour s'assurer qu'ils trouvent ce qu'ils cherchent.

```python
# Recherche insensible à la casse avec icontains
results = products.select(
    where=products.name.icontains("LAVANDE")  # Même tapé en majuscules
)
print("Recherche 'LAVANDE' :")
for p in results:
    print(f"  - {p['name']}")
# Recherche 'LAVANDE' :
#   - Bougie Parfumée Lavande

# ilike pour les motifs insensibles à la casse
results = products.select(
    where=products.description.ilike("%BIO%")
)
print("Recherche 'BIO' (insensible à la casse) :")
for p in results:
    print(f"  - {p['name']}")
# Recherche 'BIO' (insensible à la casse) :
#   - Coffret Thé Bio
```

### Toutes les variantes disponibles

| Méthode sensible à la casse | Méthode insensible à la casse | Usage |
|----------------------------|------------------------------|-------|
| `==` (égalité) | `iequals()` | Correspondance exacte |
| `contains()` | `icontains()` | Contient du texte |
| `startswith()` | `istartswith()` | Commence par |
| `endswith()` | `iendswith()` | Termine par |
| `like()` | `ilike()` | Motif SQL avec % et _ |

```python
# Exemple avec istartswith
results = products.select(
    where=products.name.istartswith("COFFRET")
)
print("Produits commençant par 'coffret' (insensible à la casse) :")
for p in results:
    print(f"  - {p['name']}")
# Produits commençant par 'coffret' (insensible à la casse) :
#   - Coffret Thé Bio
```

## Mises à jour de stock avec Upsert

Sophie reçoit régulièrement des livraisons. Elle utilise `upsert()` pour mettre à jour son stock : si le produit existe, il est mis à jour ; sinon, il est créé.

```python
# Arrivée d'une livraison : mise à jour du stock pour un produit existant
sku, action = products.upsert({
    "sku": "DEC001",
    "name": "Bougie Parfumée Lavande",
    "description": "Bougie artisanale à la lavande de Provence",
    "category": "Decor",
    "price": 15.90,
    "stock": 75,  # Nouveau stock : 50 + 25 = 75
    "active": True,
})
print(f"Produit {sku} : {action}")
# Produit DEC001 : updated

# Nouveau produit dans la livraison
sku, action = products.upsert({
    "sku": "DEC005",
    "name": "Photophore en Verre",
    "description": "Photophore artisanal en verre soufflé",
    "category": "Decor",
    "price": 24.90,
    "stock": 30,
    "active": True,
})
print(f"Produit {sku} : {action}")
# Produit DEC005 : inserted
```

### Stratégies de conflit

La méthode `upsert()` accepte un paramètre `on_conflict` pour gérer les doublons :

```python
# on_conflict="update" (par défaut) : met à jour si existe
sku, action = products.upsert(
    {"sku": "DEC001", "name": "Bougie Lavande", "description": "...",
     "category": "Decor", "price": 16.90, "stock": 80, "active": True},
    on_conflict="update"
)
print(f"{sku} : {action}")  # DEC001 : updated

# on_conflict="ignore" : ne fait rien si existe
sku, action = products.upsert(
    {"sku": "DEC001", "name": "Autre Bougie", "description": "...",
     "category": "Decor", "price": 99.00, "stock": 1, "active": True},
    on_conflict="ignore"
)
print(f"{sku} : {action}")  # DEC001 : ignored

# on_conflict="error" : lève une exception si existe
from dictdb import DuplicateKeyError

try:
    products.upsert(
        {"sku": "DEC001", "name": "Test", "description": "...",
         "category": "Decor", "price": 10.00, "stock": 1, "active": True},
        on_conflict="error"
    )
except DuplicateKeyError:
    print("Le produit existe déjà !")
# Le produit existe déjà !
```

## Résumé

Dans cet exemple, Sophie a appris à :

1. **Valider les données avec un schéma** : S'assurer que chaque produit possède tous les champs requis avec les types corrects
2. **Créer des index** : Utiliser des index hash pour les recherches d'égalité et des index triés pour les requêtes par plage
3. **Combiner des conditions** : Utiliser `And`, `Or` et `Not` pour des requêtes complexes
4. **Filtrer par plage** : Utiliser `between()` pour les recherches par gamme de prix
5. **Rechercher du texte** : Utiliser `like()` avec les motifs `%` et `_`
6. **Ignorer la casse** : Utiliser `icontains()`, `ilike()` et autres variantes insensibles à la casse
7. **Gérer le stock** : Utiliser `upsert()` pour créer ou mettre à jour des produits

Sophie est maintenant prête à lancer sa boutique en ligne avec un système de gestion de catalogue robuste et performant !