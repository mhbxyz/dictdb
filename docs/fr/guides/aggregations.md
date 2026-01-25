# Agrégations

DictDB propose des fonctions d'agrégation similaires à celles du SQL pour extraire des statistiques de vos données.

## Classes d'agrégation

Vous pouvez importer ces classes directement depuis le paquet `dictdb` :

```python
from dictdb import Count, Sum, Avg, Min, Max
```

| Classe  | Description                                | Champ requis |
|---------|--------------------------------------------|--------------|
| `Count` | Compte les enregistrements ou les valeurs  | Facultatif   |
| `Sum`   | Somme des valeurs numériques               | Oui          |
| `Avg`   | Moyenne des valeurs numériques             | Oui          |
| `Min`   | Valeur minimale                            | Oui          |
| `Max`   | Valeur maximale                            | Oui          |

## Utilisation de base

Appelez `table.aggregate()` pour lancer vos calculs :

```python
from dictdb import DictDB, Count, Sum, Avg, Min, Max

db = DictDB()
db.create_table("employees")
employees = db.get_table("employees")

# Insérer quelques données de test
employees.insert({"id": 1, "name": "Alice", "department": "IT", "salary": 75000})
employees.insert({"id": 2, "name": "Bob", "department": "RH", "salary": 65000})
employees.insert({"id": 3, "name": "Charlie", "department": "IT", "salary": 85000})
employees.insert({"id": 4, "name": "Diane", "department": "IT", "salary": 70000})

# Compter le nombre total d'employés
result = employees.aggregate(total=Count())
# {"total": 4}
```

## Count (Compter)

`Count()` peut s'utiliser de deux manières différentes :

```python
# Compter absolument tous les enregistrements
employees.aggregate(total=Count())
# {"total": 4}

# Compter uniquement les enregistrements où le salaire est renseigné (non-None)
employees.aggregate(avec_salaire=Count("salary"))
# {"avec_salaire": 4}
```

!!! tip "Sans champ vs Avec champ"
    - `Count()` compte tout, y compris les lignes ayant des valeurs `None`.
    - `Count("field")` ignore les lignes où le champ spécifié est `None`.

## Sum (Somme)

`Sum("field")` calcule la somme totale des valeurs d'une colonne :

```python
employees.aggregate(masse_salariale=Sum("salary"))
# {"masse_salariale": 295000}
```

Retourne `None` si aucun enregistrement ne correspond ou si toutes les valeurs sont nulles.

## Avg (Moyenne)

`Avg("field")` calcule la moyenne arithmétique :

```python
employees.aggregate(salaire_moyen=Avg("salary"))
# {"salaire_moyen": 73750.0}
```

## Min et Max (Extrêmes)

`Min("field")` et `Max("field")` permettent de trouver les valeurs bornes :

```python
employees.aggregate(
    plus_bas=Min("salary"),
    plus_haut=Max("salary")
)
# {"plus_bas": 65000, "plus_haut": 85000}
```

Ces fonctions fonctionnent aussi avec les chaînes de caractères (ordre alphabétique) ou les dates :

```python
employees.aggregate(
    premier_nom=Min("name"),
    dernier_nom=Max("name")
)
# {"premier_nom": "Alice", "dernier_nom": "Diane"}
```

## Agrégations multiples

Vous pouvez demander plusieurs calculs en un seul appel :

```python
result = employees.aggregate(
    nb=Count(),
    total=Sum("salary"),
    moyenne=Avg("salary"),
    minimum=Min("salary"),
    maximum=Max("salary")
)
```

## Filtrage avec WHERE

Le paramètre `where` vous permet de restreindre le périmètre de l'agrégation :

```python
from dictdb import Condition

# Compter uniquement les employés du département IT
result = employees.aggregate(
    where=Condition(employees.department == "IT"),
    total_it=Count()
)
# {"total_it": 3}
```

## GROUP BY (Regroupement)

Utilisez `group_by` pour obtenir des statistiques ventilées par catégorie :

```python
# Nombre d'employés par département
results = employees.aggregate(
    group_by="department",
    effectif=Count()
)
# [
#     {"department": "IT", "effectif": 3},
#     {"department": "RH", "effectif": 1}
# ]
```

!!! note "Type de retour"
    - Sans `group_by` : retourne un seul **dictionnaire**.
    - Avec `group_by` : retourne une **liste de dictionnaires** (un par groupe).

### Regroupement sur plusieurs champs

Vous pouvez passer une liste de colonnes pour affiner les groupes :

```python
results = sales.aggregate(
    group_by=["region", "product"],
    volume=Count(),
    ca=Sum("amount")
)
```

### Combiner GROUP BY et WHERE

Les filtres `where` sont appliqués **avant** le regroupement :

```python
results = employees.aggregate(
    where=Condition(employees.salary >= 70000),
    group_by="department",
    nb=Count()
)
# L'employé RH avec 65000 € sera ignoré avant même le calcul par groupe.
```

## Gestion des valeurs nulles (None)

DictDB gère les valeurs `None` de manière prévisible :

- `Count()` (sans champ) les inclut.
- `Count("field")` les ignore.
- `Sum`, `Avg`, `Min` et `Max` ignorent systématiquement les valeurs `None` dans leurs calculs.
- Si toutes les valeurs d'une colonne sont `None`, le résultat sera `None`.