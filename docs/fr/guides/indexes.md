# Index

Les index permettent d'accélérer considérablement vos requêtes en évitant de parcourir toute la table ligne par ligne (Full Table Scan). DictDB propose deux types d'index adaptés à différents besoins.

## Types d'index

### Index de hachage (Hash Index)

L'index de hachage offre une recherche en temps constant O(1) pour les conditions d'égalité.

```python
employees.create_index("department", index_type="hash")

# Cette requête utilisera l'index -> O(1) au lieu de O(n)
employees.select(where=Condition(employees.department == "IT"))
```

**Idéal pour :**

- Les comparaisons d'égalité exacte (`==`).
- Les conditions `is_in()`.
- Les colonnes ayant beaucoup de valeurs uniques (haute cardinalité).

### Index trié (Sorted Index)

L'index trié supporte à la fois les recherches d'égalité et les recherches par plage de valeurs.

```python
employees.create_index("salary", index_type="sorted")

# Égalité : utilise l'index
employees.select(where=Condition(employees.salary == 75000))

# Plages : utilise l'index
employees.select(where=Condition(employees.salary > 70000))
employees.select(where=Condition(employees.salary.between(60000, 80000)))
```

**Idéal pour :**

- Les requêtes de plage (`<`, `<=`, `>`, `>=`).
- Les tris de données.
- Les colonnes utilisées dans `order_by`.

## Création des index

```python
# Par défaut, c'est un index Hash qui est créé
employees.create_index("department")
employees.create_index("department", index_type="hash")

# Création d'un index trié
employees.create_index("salary", index_type="sorted")
```

Les index sont maintenus à jour automatiquement lors de chaque insertion, modification ou suppression d'enregistrement.

## Vérifier l'état des index

```python
# Lister tous les champs indexés d'une table
employees.indexed_fields()  # ["department", "salary"]

# Vérifier si un champ précis possède un index
employees.has_index("department")  # True
employees.has_index("name")        # False
```

## Utilisation automatique

DictDB détecte et utilise intelligemment les index disponibles sans action de votre part :

```python
# Utilise l'index (égalité sur champ indexé)
employees.select(where=Condition(employees.department == "IT"))

# Utilise l'index (plage sur index trié)
employees.select(where=Condition(employees.salary > 70000))

# Scan complet car pas d'index sur "name"
employees.select(where=Condition(employees.name == "Alice"))
```

### Conditions combinées

Pour les conditions liées par un `AND`, l'index est utilisé pour restreindre immédiatement le nombre de candidats potentiels, rendant le filtrage final beaucoup plus rapide.

## Considérations de performance

### Quand indexer ?

- Sur les colonnes présentes fréquemment dans vos clauses `where`.
- Sur les colonnes ayant une forte sélectivité (peu de lignes correspondant à une même valeur).
- Sur les colonnes servant de pivots pour des tris (index trié recommandé).

### Quand éviter d'indexer ?

- Sur les petites tables (moins de 100 lignes), car le gain est négligeable.
- Sur les colonnes très rarement consultées.
- Sur les colonnes subissant énormément de modifications par seconde (chaque mise à jour d'index a un coût CPU).

### Consommation mémoire

Gardez à l'esprit que les index résident en mémoire vive :

- L'index Hash consomme environ O(n).
- L'index trié consomme un peu plus de mémoire en raison de sa structure en arbre.

## Persistance

!!! warning "Les index ne sont pas sauvegardés"
    Par souci de légèreté des fichiers, les index ne sont pas inclus lors d'un `db.save()`. Vous devez les recréer après chaque chargement de la base.

```python
# Sauvegarde
db.save("data.json", file_format="json")

# Chargement
db = DictDB.load("data.json", file_format="json")

# Recréation manuelle nécessaire
employees = db.get_table("employees")
employees.create_index("department")
```