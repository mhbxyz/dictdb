# DSL de Requêtes

DictDB propose un DSL (Domain Specific Language) fluide qui vous permet de construire des filtres de recherche en utilisant directement les opérateurs Python habituels.

## Principes de base

Pour créer une condition, accédez aux colonnes de votre table comme s'il s'agissait d'attributs de l'objet :

```python
from dictdb import DictDB

db = DictDB()
db.create_table("employees")
employees = db.get_table("employees")

# employees.name renvoie un objet 'Field'
# Field == "Alice" renvoie une 'PredicateExpr'
# Passez cette expression au paramètre 'where='
employees.select(where=employees.name == "Alice")
```

!!! note "Enveloppe Condition (facultative)"
    L'utilisation de `Condition()` est optionnelle. Les deux syntaxes suivantes sont valides :

    ```python
    # Syntaxe directe (recommandée)
    employees.select(where=employees.age >= 18)

    # Avec l'enveloppe explicite
    from dictdb import Condition
    employees.select(where=Condition(employees.age >= 18))
    ```

## Opérateurs de comparaison

Tous les opérateurs Python standard sont supportés pour le filtrage :

```python
# Égalité et inégalité
employees.select(where=employees.dept == "IT")
employees.select(where=employees.dept != "RH")

# Comparaisons numériques
employees.select(where=employees.age < 30)
employees.select(where=employees.age <= 30)
employees.select(where=employees.salary > 50000)
employees.select(where=employees.salary >= 50000)
```

## Opérateurs logiques

Vous pouvez combiner vos conditions avec les fonctions `And`, `Or` et `Not` :

```python
from dictdb import And, Or, Not

# AND : toutes les conditions doivent être vraies
employees.select(where=And(employees.dept == "IT", employees.salary >= 80000))

# OR : au moins une condition doit être vraie
employees.select(where=Or(employees.dept == "IT", employees.dept == "RH"))

# NOT : inverse le résultat
employees.select(where=Not(employees.dept == "Ventes"))

# Combinaisons complexes
employees.select(where=And(
    Or(employees.dept == "IT", employees.dept == "Dev"),
    employees.salary >= 70000,
    Not(employees.status == "externe")
))
```

### Syntaxe alternative (Symboles)

Les opérateurs `&`, `|` et `~` sont également supportés, mais demandent de bien parenthéser chaque bloc :

```python
employees.select(where=(employees.dept == "IT") & (employees.salary >= 80000))
employees.select(where=~(employees.dept == "Ventes"))
```

## Opérateur IN

Vérifie si une valeur appartient à une liste prédéfinie :

```python
# Équivalent à plusieurs OR, mais plus propre et efficace
employees.select(where=employees.dept.is_in(["IT", "Data", "Support"]))
```

## Opérateur BETWEEN (Plage)

Vérifie si une valeur est comprise dans un intervalle inclusif :

```python
# Cherche les employés âgés de 30 à 50 ans inclus
employees.select(where=employees.age.between(30, 50))

# Fonctionne aussi avec les dates ou les chaînes
employees.select(where=employees.date_embauche.between("2020-01-01", "2023-12-31"))
```

!!! tip "Optimisation"
    Si un index trié (Sorted Index) est présent sur la colonne, `between()` l'utilisera pour accélérer la recherche.

## Valeurs nulles ou absentes

```python
# Trouve les lignes où le champ est None ou inexistant
employees.select(where=employees.manager_id.is_null())

# Trouve les lignes où le champ possède une valeur (non-None)
employees.select(where=employees.manager_id.is_not_null())
```

## Recherche textuelle (Pattern Matching)

```python
# Commence par
employees.select(where=employees.name.startswith("A"))

# Se termine par
employees.select(where=employees.email.endswith("@cie.com"))

# Contient
employees.select(where=employees.name.contains("Dupont"))
```

## Motifs LIKE (Style SQL)

```python
# % correspond à n'importe quelle suite de caractères
employees.select(where=employees.name.like("A%"))      # Commence par A
employees.select(where=employees.name.like("%smith%")) # Contient smith

# _ correspond à un seul caractère exactement
employees.select(where=employees.code.like("A_C"))     # Matches ABC, A1C, etc.
```

### Caractères d'échappement

Pour rechercher les symboles `%` ou `_` littéraux, utilisez un caractère d'échappement :

```python
# Trouve les remises finissant par "%"
employees.select(where=products.promo.like("%\\%", escape="\\"))
```

## Recherche insensible à la casse

Toutes les méthodes de chaînes possèdent une variante commençant par `i` pour ignorer les majuscules/minuscules :

```python
# Matches "Alice", "ALICE", "alice", etc.
employees.select(where=employees.name.iequals("alice"))

# Autres variantes : icontains(), istartswith(), iendswith(), ilike()
```

## Tri des résultats

Utilisez le paramètre `order_by` :

```python
# Ordre croissant (défaut)
employees.select(order_by="name")

# Ordre décroissant (préfixe "-")
employees.select(order_by="-salary")

# Tris multiples
employees.select(order_by=["dept", "-salary"])
```

## Pagination

```python
# 10 premiers résultats
employees.select(limit=10)

# Sauter les 20 premiers et prendre les 10 suivants (page 3)
employees.select(limit=10, offset=20)
```

!!! tip "Conseil"
    Lors d'une pagination, spécifiez toujours un `order_by` pour garantir que l'ordre des pages reste stable entre deux appels.

## Sélection de colonnes (Projection)

```python
# Liste de colonnes
employees.select(columns=["name", "dept"])

# Dictionnaire pour créer des alias (renommage)
employees.select(columns={"collaborateur": "name", "equipe": "dept"})
```

## Élimination des doublons

```python
# Récupérer la liste des départements uniques
employees.select(columns=["dept"], distinct=True)
```

## Copie des données

```python
# Par défaut : retourne des copies (sûr pour la modification)
results = employees.select()

# Pour la performance en lecture seule : pas de copie
results = employees.select(copy=False)
```