# Référence API

## DictDB

La classe principale de base de données qui gère les tables.

```python
from dictdb import DictDB
```

### Constructeur

```python
DictDB()
```

Crée une instance de base de données vide.

### Méthodes

#### create_table

```python
db.create_table(table_name: str, primary_key: str = "id") -> None
```

Crée une nouvelle table.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `table_name` | `str` | - | Nom de la table |
| `primary_key` | `str` | `"id"` | Champ à utiliser comme clé primaire (primary key) |

**Note :** Pour utiliser la validation de schéma, créez directement une `Table` avec le paramètre `schema` et enregistrez-la via `db.tables[name] = table`.

**Lève :** `DuplicateTableError` si la table existe déjà.

#### drop_table

```python
db.drop_table(table_name: str) -> None
```

Supprime une table de la base de données.

**Lève :** `TableNotFoundError` si la table n'existe pas.

#### get_table

```python
db.get_table(table_name: str) -> Table
```

Retourne une référence vers la table.

**Lève :** `TableNotFoundError` si la table n'existe pas.

#### list_tables

```python
db.list_tables() -> list[str]
```

Retourne la liste de tous les noms de tables.

#### save

```python
db.save(filename: str | Path, file_format: str) -> None
```

Sauvegarde la base de données sur le disque.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `filename` | `str \| Path` | Chemin du fichier de sortie |
| `file_format` | `str` | `"json"` ou `"pickle"` |

#### load (méthode de classe)

```python
DictDB.load(filename: str | Path, file_format: str) -> DictDB
```

Charge la base de données depuis le disque.

#### async_save

```python
await db.async_save(filename: str | Path, file_format: str) -> None
```

Version asynchrone de `save()`.

#### async_load (méthode de classe)

```python
await DictDB.async_load(filename: str | Path, file_format: str) -> DictDB
```

Version asynchrone de `load()`.

#### import_csv

```python
db.import_csv(
    filepath: str | Path,
    table_name: str,
    *,
    primary_key: str = "id",
    delimiter: str = ",",
    has_header: bool = True,
    encoding: str = "utf-8",
    schema: dict[str, type] = None,
    infer_types: bool = True,
    skip_validation: bool = False
) -> int
```

Importe des données depuis un fichier CSV dans une nouvelle table.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `filepath` | `str \| Path` | - | Chemin vers le fichier CSV |
| `table_name` | `str` | - | Nom de la nouvelle table |
| `primary_key` | `str` | `"id"` | Champ à utiliser comme clé primaire |
| `delimiter` | `str` | `","` | Délimiteur de champs CSV |
| `has_header` | `bool` | `True` | Si la première ligne est un en-tête |
| `encoding` | `str` | `"utf-8"` | Encodage du fichier |
| `schema` | `dict[str, type]` | `None` | Schéma de conversion de types |
| `infer_types` | `bool` | `True` | Détection automatique des types de colonnes |
| `skip_validation` | `bool` | `False` | Ignorer la validation du schéma |

**Retourne :** Le nombre d'enregistrements importés.

**Lève :** `DuplicateTableError` si la table existe déjà.

Voir le [Guide CSV](guides/csv.md) pour une utilisation détaillée.

---

## Table

Représente une table unique avec les opérations CRUD.

### Méthodes

#### insert

```python
table.insert(record: dict) -> Any
table.insert(record: list[dict], batch_size: int = None, skip_validation: bool = False) -> list[Any]
```

Insère un ou plusieurs enregistrements, retourne la ou les clé(s) primaire(s).

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `record` | `dict \| list[dict]` | - | Enregistrement ou liste d'enregistrements à insérer |
| `batch_size` | `int` | `None` | Pour les insertions en masse, traiter par lots de cette taille |
| `skip_validation` | `bool` | `False` | Ignorer la validation du schéma pour les données de confiance |

Pour les insertions en masse, l'opération est atomique : si un enregistrement échoue à la validation ou a une clé dupliquée, toutes les insertions sont annulées.

**Lève :**

- `DuplicateKeyError` si la clé primaire existe déjà
- `SchemaValidationError` si l'enregistrement échoue à la validation

#### upsert

```python
table.upsert(record: dict, on_conflict: str = "update") -> tuple[Any, str]
```

Insère un enregistrement ou gère le conflit si la clé primaire existe.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `record` | `dict` | - | Enregistrement à insérer ou mettre à jour |
| `on_conflict` | `str` | `"update"` | Stratégie de conflit : `"update"`, `"ignore"` ou `"error"` |

**Retourne :** Un tuple `(clé_primaire, action)` où action est `"inserted"`, `"updated"` ou `"ignored"`.

**Stratégies de conflit :**

- `"update"` - Met à jour l'enregistrement existant avec les nouvelles valeurs (par défaut)
- `"ignore"` - Conserve l'enregistrement existant, ne fait rien
- `"error"` - Lève `DuplicateKeyError`

**Lève :**

- `DuplicateKeyError` si `on_conflict="error"` et l'enregistrement existe
- `SchemaValidationError` si l'enregistrement échoue à la validation

#### select

```python
table.select(
    columns: list | dict = None,
    where: Condition | PredicateExpr = None,
    order_by: str | list = None,
    limit: int = None,
    offset: int = 0,
    copy: bool = True,
    distinct: bool = False
) -> list[dict]
```

Récupère les enregistrements correspondants.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `columns` | `list \| dict` | `None` | Projection de colonnes |
| `where` | `Condition \| PredicateExpr` | `None` | Condition de filtrage (l'enveloppe Condition est optionnelle) |
| `order_by` | `str \| list` | `None` | Ordre de tri |
| `limit` | `int` | `None` | Nombre maximum d'enregistrements |
| `offset` | `int` | `0` | Enregistrements à ignorer |
| `copy` | `bool` | `True` | Retourner des copies |
| `distinct` | `bool` | `False` | Retourner uniquement les enregistrements uniques |

#### update

```python
table.update(changes: dict, where: Condition | PredicateExpr = None) -> int
```

Met à jour les enregistrements correspondants, retourne le nombre. L'enveloppe `Condition` est optionnelle.

**Lève :**

- `RecordNotFoundError` si aucun enregistrement ne correspond
- `SchemaValidationError` si les modifications échouent à la validation

#### delete

```python
table.delete(where: Condition | PredicateExpr = None) -> int
```

Supprime les enregistrements correspondants, retourne le nombre. L'enveloppe `Condition` est optionnelle.

**Lève :** `RecordNotFoundError` si aucun enregistrement ne correspond.

#### create_index

```python
table.create_index(field: str, index_type: str = "hash") -> None
```

Crée un index sur un champ.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `field` | `str` | - | Champ à indexer |
| `index_type` | `str` | `"hash"` | `"hash"` ou `"sorted"` |

### Introspection

```python
table.count() -> int              # Nombre d'enregistrements
table.size() -> int               # Alias pour count()
table.columns() -> list[str]      # Noms des colonnes
table.primary_key_name() -> str   # Champ de clé primaire
table.indexed_fields() -> list[str]  # Champs indexés
table.has_index(field: str) -> bool  # Vérifie si l'index existe
table.schema_fields() -> list[str]   # Champs du schéma
```

### Autres méthodes

```python
table.all() -> list[dict]         # Tous les enregistrements en copies
table.copy() -> dict[Any, dict]   # Dict de clé_primaire -> copie d'enregistrement
```

#### export_csv

```python
table.export_csv(
    filepath: str | Path,
    *,
    records: list[dict] = None,
    columns: list[str] = None,
    where: Condition | PredicateExpr = None,
    delimiter: str = ",",
    encoding: str = "utf-8"
) -> int
```

Exporte les enregistrements vers un fichier CSV.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `filepath` | `str \| Path` | - | Chemin du fichier CSV de sortie |
| `records` | `list[dict]` | `None` | Enregistrements pré-calculés à exporter |
| `columns` | `list[str]` | `None` | Colonnes à inclure (et leur ordre) |
| `where` | `Condition \| PredicateExpr` | `None` | Condition de filtrage |
| `delimiter` | `str` | `","` | Délimiteur de champs CSV |
| `encoding` | `str` | `"utf-8"` | Encodage du fichier |

**Retourne :** Le nombre d'enregistrements écrits.

Voir le [Guide CSV](guides/csv.md) pour une utilisation détaillée.

---

## Condition

Enveloppe une expression de prédicat pour l'utiliser dans les requêtes. **L'enveloppe `Condition` est optionnelle** - vous pouvez passer `PredicateExpr` directement aux paramètres `where=`.

```python
from dictdb import Condition
```

### Constructeur

```python
Condition(predicate_expr)
```

Enveloppe une `PredicateExpr` créée à partir de comparaisons de champs.

### Utilisation

```python
# Recommandé : passer PredicateExpr directement (pas d'enveloppe nécessaire)
table.select(where=table.field == value)

# Fonctionne aussi : enveloppe Condition explicite
table.select(where=Condition(table.field == value))
```

---

## Fonctions logiques

Combinez les conditions en utilisant des fonctions lisibles.

```python
from dictdb import And, Or, Not
```

### And

```python
And(*conditions) -> PredicateExpr
```

Retourne une condition qui est vraie uniquement si **tous** les opérandes sont vrais.

```python
# Deux conditions
table.select(where=And(table.age >= 18, table.active == True))

# Plusieurs conditions
table.select(where=And(table.dept == "IT", table.active == True, table.level >= 3))
```

### Or

```python
Or(*conditions) -> PredicateExpr
```

Retourne une condition qui est vraie si **au moins un** opérande est vrai.

```python
# Correspondre à plusieurs valeurs
table.select(where=Or(table.dept == "IT", table.dept == "HR", table.dept == "Sales"))
```

### Not

```python
Not(condition) -> PredicateExpr
```

Retourne une condition qui est vraie quand l'opérande est faux.

```python
table.select(where=Not(table.status == "inactive"))
```

### Combinaison de fonctions

```python
# Conditions imbriquées complexes
table.select(where=And(
    Or(table.dept == "IT", table.dept == "Engineering"),
    table.salary >= 70000,
    Not(table.status == "inactive")
))
```

### Alternative : Opérateurs symboliques

Les opérateurs `&`, `|`, `~` sont également supportés mais nécessitent une utilisation prudente des parenthèses :

```python
table.select(where=(table.age >= 18) & (table.active == True))  # AND
table.select(where=(table.dept == "IT") | (table.dept == "HR"))  # OR
table.select(where=~(table.status == "inactive"))                # NOT
```

---

## Opérateurs de champ

Accessibles via l'accès aux attributs de table : `table.nom_du_champ`

### Comparaison

```python
table.field == value    # Égalité
table.field != value    # Inégalité
table.field < value     # Inférieur à
table.field <= value    # Inférieur ou égal à
table.field > value     # Supérieur à
table.field >= value    # Supérieur ou égal à
```

### Méthodes spéciales

```python
table.field.is_in([v1, v2, v3])  # Opérateur IN
table.field.between(low, high)   # Plage inclusive (low <= field <= high)
table.field.like("A%")           # Motif SQL LIKE (% = tout, _ = un caractère)
table.field.startswith("prefix") # Préfixe de chaîne
table.field.endswith("suffix")   # Suffixe de chaîne
table.field.contains("substr")   # Contient une sous-chaîne
table.field.is_null()            # Vérifie si None ou manquant
table.field.is_not_null()        # Vérifie si non None
```

### Méthodes insensibles à la casse

```python
table.field.iequals("value")     # Égalité insensible à la casse
table.field.icontains("substr")  # Contient insensible à la casse
table.field.istartswith("pre")   # Préfixe insensible à la casse
table.field.iendswith("suf")     # Suffixe insensible à la casse
table.field.ilike("A%")          # LIKE insensible à la casse
```

### Logique

Utilisez les fonctions `And`, `Or`, `Not` (recommandé) ou les opérateurs symboliques :

```python
And(expr1, expr2)  # AND (préféré)
Or(expr1, expr2)   # OR (préféré)
Not(expr)          # NOT (préféré)

(expr1) & (expr2)  # AND (alternative)
(expr1) | (expr2)  # OR (alternative)
~(expr)            # NOT (alternative)
```

---

## BackupManager

Gestionnaire de sauvegarde automatique.

```python
from dictdb import BackupManager
```

### Constructeur

```python
BackupManager(
    db: DictDB,
    backup_dir: str | Path,
    backup_interval: int = 300,
    file_format: str = "json",
    min_backup_interval: float = 5.0,
    on_backup_failure: Callable = None,
    incremental: bool = False,
    max_deltas_before_full: int = 10
)
```

### Méthodes

```python
backup.start() -> None        # Démarre le thread d'arrière-plan
backup.stop() -> None         # Arrête le thread d'arrière-plan
backup.backup_now() -> None   # Sauvegarde immédiate
backup.backup_full() -> None  # Force une sauvegarde complète
backup.backup_delta() -> None # Force une sauvegarde delta
backup.notify_change() -> None  # Déclenche une sauvegarde (avec délai)
```

### Propriétés

```python
backup.consecutive_failures -> int  # Nombre d'échecs consécutifs
backup.deltas_since_full -> int     # Nombre de deltas
```

---

## Journalisation (Logging)

```python
from dictdb import logger, configure_logging
```

### configure_logging

```python
configure_logging(
    level: str = "INFO",
    console: bool = True,
    logfile: str = None,
    json: bool = False,
    sample_debug_every: int = None
) -> None
```

### logger

Instance globale du logger avec les méthodes :

```python
logger.debug(msg, **kwargs)
logger.info(msg, **kwargs)
logger.warning(msg, **kwargs)
logger.error(msg, **kwargs)
logger.critical(msg, **kwargs)
logger.bind(**kwargs) -> BoundLogger
logger.add(sink, level, serialize, filter) -> int
logger.remove() -> None
```

---

## Agrégations

Fonctions d'agrégation de type SQL pour les résultats de requêtes. Voir le [Guide d'agrégation](guides/aggregations.md) pour une utilisation détaillée.

```python
from dictdb import Count, Sum, Avg, Min, Max
```

| Classe | Description |
|--------|-------------|
| `Count(field=None)` | Compte les enregistrements ou les valeurs non-None |
| `Sum(field)` | Somme des valeurs numériques |
| `Avg(field)` | Moyenne des valeurs numériques |
| `Min(field)` | Valeur minimale |
| `Max(field)` | Valeur maximale |

---

## Version

```python
from dictdb import __version__
```

La chaîne de version du paquet installé (par exemple, `"1.2.3"`).

---

## Exceptions

```python
from dictdb import (
    DictDBError,
    DuplicateKeyError,
    DuplicateTableError,
    RecordNotFoundError,
    TableNotFoundError,
    SchemaValidationError,
)
```

| Exception | Description |
|-----------|-------------|
| `DictDBError` | Exception de base pour toutes les erreurs dictdb |
| `DuplicateKeyError` | La clé primaire existe déjà |
| `DuplicateTableError` | Le nom de table existe déjà |
| `RecordNotFoundError` | Aucun enregistrement ne correspond aux critères |
| `TableNotFoundError` | La table n'existe pas |
| `SchemaValidationError` | L'enregistrement échoue à la validation du schéma |

Toutes les exceptions héritent de `DictDBError`.
