# Index

Les index accélèrent les requêtes en évitant les parcours complets de table. DictDB supporte deux types d'index.

## Types d'Index

### Index Hash

Les index hash fournissent des recherches en O(1) pour les conditions d'égalité :

```python
employees.create_index("department", index_type="hash")

# Cette requête utilise l'index - O(1) au lieu de O(n)
employees.select(where=Condition(employees.department == "IT"))
```

Idéal pour :

- Comparaisons d'égalité (`==`)
- Conditions `is_in()`
- Champs à haute cardinalité (beaucoup de valeurs uniques)

### Index Trié

Les index triés supportent à la fois les requêtes d'égalité et de plage :

```python
employees.create_index("salary", index_type="sorted")

# Égalité - utilise l'index
employees.select(where=Condition(employees.salary == 75000))

# Requêtes de plage - utilise l'index
employees.select(where=Condition(employees.salary > 70000))
employees.select(where=Condition(employees.salary <= 80000))
employees.select(where=Condition(employees.salary >= 60000))
```

Idéal pour :

- Requêtes de plage (`<`, `<=`, `>`, `>=`)
- Accès ordonné aux données
- Champs utilisés dans `order_by`

## Création d'Index

```python
# Index hash (par défaut)
employees.create_index("department")
employees.create_index("department", index_type="hash")

# Index trié
employees.create_index("salary", index_type="sorted")
```

Les index sont automatiquement mis à jour lors de l'insertion, la mise à jour ou la suppression d'enregistrements.

## Vérification des Index

```python
# Lister les champs indexés
employees.indexed_fields()  # ["department", "salary"]

# Vérifier si un champ est indexé
employees.has_index("department")  # True
employees.has_index("name")  # False
```

## Utilisation des Index

DictDB utilise automatiquement les index lorsque c'est possible :

```python
# Utilise l'index (égalité sur un champ indexé)
employees.select(where=Condition(employees.department == "IT"))

# Utilise l'index (plage sur un index trié)
employees.select(where=Condition(employees.salary > 70000))

# Utilise l'index (is_in sur un champ indexé)
employees.select(where=Condition(employees.department.is_in(["IT", "HR"])))

# Parcours complet de table (pas d'index sur "name")
employees.select(where=Condition(employees.name == "Alice"))
```

### Conditions Composées

Pour les conditions AND, l'index est utilisé pour réduire les candidats :

```python
employees.create_index("department")

# Utilise l'index department, puis filtre par salary
employees.select(
    where=Condition((employees.department == "IT") & (employees.salary > 70000))
)
```

## Considérations de Performance

### Quand Utiliser les Index

- Champs fréquemment utilisés dans les conditions `where`
- Champs avec haute sélectivité (peu de correspondances par valeur)
- Champs de requêtes de plage (utilisez un index trié)

### Quand Éviter les Index

- Tables avec peu d'enregistrements (< 100)
- Champs rarement interrogés
- Champs mis à jour très fréquemment

### Surcharge Mémoire

Les index consomment de la mémoire supplémentaire :

- Index hash : ~O(n) pour n enregistrements
- Index trié : ~O(n) avec surcharge de structure d'arbre

## Persistance

!!! avertissement "Les Index ne sont pas Persistés"
    Les index ne sont pas sauvegardés lors de l'utilisation de `db.save()`. Après le chargement d'une base de données, recréez les index si nécessaire :

```python
# Sauvegarde
db.save("data.json", file_format="json")

# Chargement
db = DictDB.load("data.json", file_format="json")

# Recréation des index
employees = db.get_table("employees")
employees.create_index("department")
employees.create_index("salary", index_type="sorted")
```

## Exemple

```python
from dictdb import DictDB, Condition

db = DictDB()
db.create_table("orders", primary_key="order_id")
orders = db.get_table("orders")

# Création des index
orders.create_index("customer_id")  # Hash pour les recherches d'égalité
orders.create_index("total", index_type="sorted")  # Trié pour les requêtes de plage
orders.create_index("status")  # Hash pour le filtrage par statut

# Insertion des données
for i in range(10000):
    orders.insert({
        "customer_id": i % 100,
        "total": 10 + (i * 0.5),
        "status": "completed" if i % 3 == 0 else "pending"
    })

# Requêtes rapides utilisant les index
customer_orders = orders.select(where=Condition(orders.customer_id == 42))
large_orders = orders.select(where=Condition(orders.total > 1000))
pending = orders.select(where=Condition(orders.status == "pending"))
```
