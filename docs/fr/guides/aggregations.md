# Agrégations

DictDB fournit des fonctions d'agrégation de type SQL pour calculer des statistiques sur vos données.

## Classes d'Agrégation

Importez les classes d'agrégation directement depuis dictdb :

```python
from dictdb import Count, Sum, Avg, Min, Max
```

| Classe  | Description                          | Champ Requis |
|---------|--------------------------------------|--------------|
| `Count` | Compte les enregistrements ou valeurs non-None | Optionnel |
| `Sum`   | Somme des valeurs numériques         | Oui          |
| `Avg`   | Moyenne des valeurs numériques       | Oui          |
| `Min`   | Valeur minimale                      | Oui          |
| `Max`   | Valeur maximale                      | Oui          |

## Utilisation de Base

Utilisez `table.aggregate()` pour calculer des agrégations :

```python
from dictdb import DictDB, Count, Sum, Avg, Min, Max

db = DictDB()
db.create_table("employees")
employees = db.get_table("employees")

# Insertion de données d'exemple
employees.insert({"id": 1, "name": "Alice", "department": "IT", "salary": 75000})
employees.insert({"id": 2, "name": "Bob", "department": "HR", "salary": 65000})
employees.insert({"id": 3, "name": "Charlie", "department": "IT", "salary": 85000})
employees.insert({"id": 4, "name": "Diana", "department": "IT", "salary": 70000})

# Compter tous les employés
result = employees.aggregate(count=Count())
# {"count": 4}
```

## Count

`Count()` peut être utilisé de deux façons :

```python
# Compter tous les enregistrements
employees.aggregate(total=Count())
# {"total": 4}

# Compter les valeurs non-None dans un champ spécifique
employees.aggregate(with_salary=Count("salary"))
# {"with_salary": 4}
```

!!! astuce "Count Sans Champ vs Avec Champ"
    - `Count()` compte tous les enregistrements, y compris ceux avec des valeurs None
    - `Count("field")` compte uniquement les enregistrements où le champ n'est pas None

## Sum

`Sum("field")` calcule la somme des valeurs numériques :

```python
employees.aggregate(total_salary=Sum("salary"))
# {"total_salary": 295000}
```

Retourne `None` si aucun enregistrement ne correspond ou si toutes les valeurs sont None.

## Avg

`Avg("field")` calcule la moyenne des valeurs numériques :

```python
employees.aggregate(avg_salary=Avg("salary"))
# {"avg_salary": 73750.0}
```

Retourne `None` si aucun enregistrement ne correspond ou si toutes les valeurs sont None.

## Min et Max

`Min("field")` et `Max("field")` trouvent les valeurs extrêmes :

```python
employees.aggregate(
    lowest=Min("salary"),
    highest=Max("salary")
)
# {"lowest": 65000, "highest": 85000}
```

Ces fonctions marchent avec tout type comparable (nombres, chaînes, dates, etc.) :

```python
employees.aggregate(
    first_name=Min("name"),
    last_name=Max("name")
)
# {"first_name": "Alice", "last_name": "Diana"}
```

## Agrégations Multiples

Calculez plusieurs agrégations en un seul appel :

```python
result = employees.aggregate(
    count=Count(),
    total=Sum("salary"),
    average=Avg("salary"),
    minimum=Min("salary"),
    maximum=Max("salary")
)
# {
#     "count": 4,
#     "total": 295000,
#     "average": 73750.0,
#     "minimum": 65000,
#     "maximum": 85000
# }
```

## Filtrage avec WHERE

Utilisez le paramètre `where` pour filtrer les enregistrements avant l'agrégation :

```python
from dictdb import Condition

# Compter les employés IT
result = employees.aggregate(
    where=Condition(employees.department == "IT"),
    count=Count()
)
# {"count": 3}

# Salaire moyen dans le département IT
result = employees.aggregate(
    where=Condition(employees.department == "IT"),
    avg_salary=Avg("salary")
)
# {"avg_salary": 76666.67}
```

## GROUP BY

Utilisez `group_by` pour calculer des agrégations pour chaque valeur unique d'un champ :

```python
# Compter les employés par département
results = employees.aggregate(
    group_by="department",
    count=Count()
)
# [
#     {"department": "IT", "count": 3},
#     {"department": "HR", "count": 1}
# ]
```

!!! remarque "Le Type de Retour Change avec GROUP BY"
    - Sans `group_by` : Retourne un seul dictionnaire
    - Avec `group_by` : Retourne une liste de dictionnaires (un par groupe)

### Agrégations Multiples par Groupe

```python
results = employees.aggregate(
    group_by="department",
    count=Count(),
    total_salary=Sum("salary"),
    avg_salary=Avg("salary"),
    max_salary=Max("salary")
)
# [
#     {"department": "IT", "count": 3, "total_salary": 230000, "avg_salary": 76666.67, "max_salary": 85000},
#     {"department": "HR", "count": 1, "total_salary": 65000, "avg_salary": 65000.0, "max_salary": 65000}
# ]
```

### Champs GROUP BY Multiples

Groupez par plusieurs champs en utilisant une liste :

```python
db.create_table("sales")
sales = db.get_table("sales")

sales.insert({"region": "East", "product": "A", "amount": 100})
sales.insert({"region": "East", "product": "A", "amount": 150})
sales.insert({"region": "East", "product": "B", "amount": 200})
sales.insert({"region": "West", "product": "A", "amount": 120})

results = sales.aggregate(
    group_by=["region", "product"],
    count=Count(),
    total=Sum("amount")
)
# [
#     {"region": "East", "product": "A", "count": 2, "total": 250},
#     {"region": "East", "product": "B", "count": 1, "total": 200},
#     {"region": "West", "product": "A", "count": 1, "total": 120}
# ]
```

### Combinaison de GROUP BY avec WHERE

Filtrez les enregistrements avant le regroupement :

```python
results = employees.aggregate(
    where=Condition(employees.salary >= 70000),
    group_by="department",
    count=Count(),
    avg_salary=Avg("salary")
)
# [
#     {"department": "IT", "count": 3, "avg_salary": 76666.67}
# ]
# L'employé HR (salaire 65000) a été exclu par la clause WHERE
```

## Exemple Complet

```python
from dictdb import DictDB, Condition, Count, Sum, Avg, Min, Max

db = DictDB()
db.create_table("orders", primary_key="order_id")
orders = db.get_table("orders")

# Insertion de commandes d'exemple
orders.insert({"order_id": 1, "customer": "Alice", "product": "Widget", "quantity": 5, "price": 10.00})
orders.insert({"order_id": 2, "customer": "Bob", "product": "Gadget", "quantity": 2, "price": 25.00})
orders.insert({"order_id": 3, "customer": "Alice", "product": "Gadget", "quantity": 1, "price": 25.00})
orders.insert({"order_id": 4, "customer": "Charlie", "product": "Widget", "quantity": 10, "price": 10.00})
orders.insert({"order_id": 5, "customer": "Alice", "product": "Widget", "quantity": 3, "price": 10.00})

# Statistiques globales
stats = orders.aggregate(
    total_orders=Count(),
    total_quantity=Sum("quantity"),
    avg_price=Avg("price")
)
# {"total_orders": 5, "total_quantity": 21, "avg_price": 16.0}

# Commandes par client
by_customer = orders.aggregate(
    group_by="customer",
    order_count=Count(),
    total_quantity=Sum("quantity")
)
# [
#     {"customer": "Alice", "order_count": 3, "total_quantity": 9},
#     {"customer": "Bob", "order_count": 1, "total_quantity": 2},
#     {"customer": "Charlie", "order_count": 1, "total_quantity": 10}
# ]

# Chiffre d'affaires par produit (commandes Widget uniquement)
widget_stats = orders.aggregate(
    where=Condition(orders.product == "Widget"),
    group_by="customer",
    order_count=Count(),
    total_qty=Sum("quantity")
)
# [
#     {"customer": "Alice", "order_count": 2, "total_qty": 8},
#     {"customer": "Charlie", "order_count": 1, "total_qty": 10}
# ]
```

## Gestion des Valeurs None

Les agrégations gèrent les valeurs None de manière cohérente :

- `Count()` sans champ : Compte tous les enregistrements (y compris ceux avec None)
- `Count("field")` : Compte uniquement les valeurs non-None
- `Sum`, `Avg`, `Min`, `Max` : Ignorent les valeurs None dans les calculs
- Si toutes les valeurs sont None : `Sum`, `Avg`, `Min`, `Max` retournent `None`

```python
db.create_table("data")
data = db.get_table("data")
data.insert({"id": 1, "value": 10})
data.insert({"id": 2, "value": None})
data.insert({"id": 3, "value": 20})

result = data.aggregate(
    total_records=Count(),
    non_null_values=Count("value"),
    sum_values=Sum("value"),
    avg_values=Avg("value")
)
# {
#     "total_records": 3,
#     "non_null_values": 2,
#     "sum_values": 30,
#     "avg_values": 15.0
# }
```
