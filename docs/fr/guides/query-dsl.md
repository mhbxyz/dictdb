# DSL de Requêtes

DictDB fournit un DSL de requêtes fluide qui vous permet de construire des conditions en utilisant les opérateurs Python.

## Conditions de Base

Accédez aux champs de la table comme attributs pour créer des conditions :

```python
from dictdb import DictDB

db = DictDB()
db.create_table("employees")
employees = db.get_table("employees")

# employees.name retourne un objet Field
# Field == "Alice" retourne un PredicateExpr
# Passez-le directement au paramètre where=
employees.select(where=employees.name == "Alice")
```

!!! remarque "Enveloppe Condition (Optionnelle)"
    L'enveloppe `Condition()` est optionnelle. Les deux syntaxes sont supportées :

    ```python
    # Recommandé : syntaxe directe
    employees.select(where=employees.age >= 18)

    # Fonctionne aussi : enveloppe Condition explicite
    from dictdb import Condition
    employees.select(where=Condition(employees.age >= 18))
    ```

## Opérateurs de Comparaison

Tous les opérateurs de comparaison standard sont supportés :

```python
# Égalité
employees.select(where=employees.department == "IT")

# Inégalité
employees.select(where=employees.department != "HR")

# Inférieur à / Inférieur ou égal à
employees.select(where=employees.age < 30)
employees.select(where=employees.age <= 30)

# Supérieur à / Supérieur ou égal à
employees.select(where=employees.salary > 50000)
employees.select(where=employees.salary >= 50000)
```

## Opérateurs Logiques

Combinez les conditions en utilisant les fonctions `And`, `Or` et `Not` :

```python
from dictdb import And, Or, Not

# AND : toutes les conditions doivent être vraies
employees.select(where=And(employees.department == "IT", employees.salary >= 80000))

# OR : une condition au moins doit être vraie
employees.select(where=Or(employees.department == "IT", employees.department == "HR"))

# NOT : inverse une condition
employees.select(where=Not(employees.department == "Sales"))

# Combinaisons complexes - la structure est claire
employees.select(where=And(
    Or(employees.department == "IT", employees.department == "Engineering"),
    employees.salary >= 70000,
    Not(employees.status == "inactive")
))
```

### Arguments Multiples

`And` et `Or` acceptent un nombre quelconque d'arguments (minimum 2) :

```python
# Plus lisible que le chaînage
employees.select(where=And(
    employees.department == "IT",
    employees.active == True,
    employees.salary >= 50000,
    employees.level >= 3
))
```

### Syntaxe Alternative

Les opérateurs symboliques `&`, `|`, `~` sont également supportés :

```python
# Équivalent à And/Or/Not
employees.select(where=(employees.department == "IT") & (employees.salary >= 80000))
employees.select(where=(employees.department == "IT") | (employees.department == "HR"))
employees.select(where=~(employees.department == "Sales"))
```

!!! avertissement "Utilisez des Parenthèses avec les Symboles"
    Lorsque vous utilisez `&`, `|`, `~`, entourez toujours les conditions individuelles de parenthèses. La priorité des opérateurs Python peut ne pas fonctionner comme prévu sinon.

## Opérateur IN

Vérifiez si la valeur d'un champ est dans une liste :

```python
# Correspond à l'une des valeurs
employees.select(where=employees.department.is_in(["IT", "Engineering", "Data"]))

# Équivalent à plusieurs conditions OR mais plus efficace
```

## Opérateur BETWEEN

Vérifiez si la valeur d'un champ est dans une plage inclusive :

```python
# Correspond aux valeurs dans la plage [30, 50]
employees.select(where=employees.age.between(30, 50))

# Équivalent à (mais plus efficace que) :
employees.select(where=(employees.age >= 30) & (employees.age <= 50))

# Fonctionne avec tous les types comparables
employees.select(where=employees.hire_date.between("2020-01-01", "2023-12-31"))
employees.select(where=employees.salary.between(50000, 100000))
```

!!! astuce "Optimisation d'Index"
    Lorsqu'un index trié existe sur le champ, `between()` utilise un parcours de plage unique optimisé au lieu de deux recherches d'index séparées.

## Vérifications de Null

Vérifiez les valeurs de champ null (None) ou manquantes :

```python
# Correspond aux enregistrements où le champ est None ou manquant
employees.select(where=employees.manager_id.is_null())

# Correspond aux enregistrements où le champ existe et n'est pas None
employees.select(where=employees.manager_id.is_not_null())
```

## Correspondance de Chaînes

Faites correspondre des motifs de chaînes :

```python
# Commence par
employees.select(where=employees.name.startswith("A"))

# Se termine par
employees.select(where=employees.email.endswith("@company.com"))

# Contient
employees.select(where=employees.name.contains("Smith"))
```

## Correspondance de Motifs LIKE

Motifs LIKE de style SQL avec caractères génériques :

```python
# % correspond à n'importe quelle séquence de caractères (y compris vide)
employees.select(where=employees.name.like("A%"))           # Commence par A
employees.select(where=employees.email.like("%@gmail.com")) # Se termine par @gmail.com
employees.select(where=employees.name.like("%smith%"))      # Contient smith

# _ correspond à exactement un caractère
employees.select(where=employees.code.like("A_C"))          # Correspond à A1C, A2C, ABC, etc.
employees.select(where=employees.id.like("___"))            # Exactement 3 caractères

# Combinez les caractères génériques
employees.select(where=employees.file.like("test_.%"))      # test1.txt, test2.doc, etc.
```

### Caractères d'Échappement

Pour faire correspondre les caractères littéraux `%` ou `_`, utilisez un caractère d'échappement :

```python
# Correspond aux chaînes se terminant par % littéral
employees.select(where=products.discount.like("%\\%", escape="\\"))  # 10%, 20%, etc.

# Correspond aux chaînes contenant _ littéral
employees.select(where=files.name.like("%\\_v1%", escape="\\"))  # file_v1.txt, etc.
```

!!! astuce "Optimisation d'Index"
    Lorsqu'un index trié existe et que le motif commence par un préfixe littéral (par ex., `"ABC%"`), la requête utilise l'index pour des recherches plus rapides.

## Correspondance Insensible à la Casse

Toutes les méthodes de correspondance de chaînes ont des variantes insensibles à la casse avec un préfixe `i` :

```python
# Égalité insensible à la casse
employees.select(where=employees.name.iequals("alice"))  # Correspond à "Alice", "ALICE", etc.

# Contient insensible à la casse
employees.select(where=employees.name.icontains("smith"))  # Correspond à "Smith", "SMITH", etc.

# Préfixe/suffixe insensible à la casse
employees.select(where=employees.name.istartswith("a"))  # Correspond à "Alice", "ADAM", etc.
employees.select(where=employees.email.iendswith("@gmail.com"))  # Correspond à "@Gmail.COM", etc.

# LIKE insensible à la casse
employees.select(where=employees.name.ilike("a%"))  # Correspond à "Alice", "adam", "ANNA", etc.
```

| Méthode | Variante Insensible à la Casse |
|---------|-------------------------------|
| `==` (égalité) | `iequals()` |
| `contains()` | `icontains()` |
| `startswith()` | `istartswith()` |
| `endswith()` | `iendswith()` |
| `like()` | `ilike()` |

## Tri

Triez les résultats avec `order_by` :

```python
# Ordre croissant (par défaut)
employees.select(order_by="name")

# Ordre décroissant (préfixe avec -)
employees.select(order_by="-salary")

# Champs multiples
employees.select(order_by=["department", "-salary"])
# Trie par département croissant, puis par salaire décroissant au sein de chaque département
```

## Pagination

Limitez et décalez les résultats :

```python
# 10 premiers enregistrements
employees.select(limit=10)

# Saute les 20 premiers, obtient les 10 suivants (page 3 avec taille de page 10)
employees.select(limit=10, offset=20)

# Combinez avec le tri pour une pagination cohérente
employees.select(order_by="id", limit=10, offset=20)
```

!!! astuce "Toujours Trier lors de la Pagination"
    Sans `order_by`, l'ordre des résultats n'est pas garanti. Spécifiez toujours un ordre de tri lors de l'utilisation de la pagination.

## Projection de Colonnes

Sélectionnez des colonnes spécifiques :

```python
# Liste de noms de colonnes
employees.select(columns=["name", "department"])
# Retourne : [{"name": "Alice", "department": "IT"}, ...]

# Dictionnaire pour les alias
employees.select(columns={"employee": "name", "team": "department"})
# Retourne : [{"employee": "Alice", "team": "IT"}, ...]

# Liste de tuples
employees.select(columns=[("employee", "name"), ("team", "department")])
# Identique à ci-dessus
```

## Résultats Distincts

Supprimez les enregistrements en double des résultats :

```python
# Obtenir les départements uniques
employees.select(columns=["department"], distinct=True)
# Retourne : [{"department": "IT"}, {"department": "HR"}, {"department": "Sales"}]

# Combinez avec d'autres options
employees.select(
    columns=["department", "status"],
    where=employees.salary >= 50000,
    distinct=True,
    order_by="department"
)
```

!!! remarque "Comportement de Distinct"
    Lorsque des doublons existent, `distinct=True` préserve la première occurrence et supprime les doublons suivants.

## Copie d'Enregistrements

Par défaut, `select` retourne des copies des enregistrements pour la sécurité des threads :

```python
# Par défaut : retourne des copies (modification sans risque)
results = employees.select()
results[0]["name"] = "Modified"  # N'affecte pas l'original

# Pour un accès en lecture seule, sautez la copie pour de meilleures performances
results = employees.select(copy=False)
# Ne modifiez pas ces enregistrements !
```

## Exemple Complet

```python
from dictdb import DictDB

db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

# Insérer des données d'exemple
employees.insert({"emp_id": 1, "name": "Alice", "department": "IT", "salary": 75000})
employees.insert({"emp_id": 2, "name": "Bob", "department": "HR", "salary": 65000})
employees.insert({"emp_id": 3, "name": "Charlie", "department": "IT", "salary": 85000})
employees.insert({"emp_id": 4, "name": "Diana", "department": "Sales", "salary": 70000})

# Trouver les employés IT gagnant >= 80000
high_earners = employees.select(
    columns=["name", "salary"],
    where=(employees.department == "IT") & (employees.salary >= 80000),
    order_by="-salary"
)
# [{"name": "Charlie", "salary": 85000}]

# Liste paginée de tous les employés
page_1 = employees.select(order_by="name", limit=2, offset=0)
page_2 = employees.select(order_by="name", limit=2, offset=2)
```
