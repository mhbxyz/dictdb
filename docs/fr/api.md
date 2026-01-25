# Référence API

## DictDB

C'est la classe principale qui gère vos tables de données.

```python
from dictdb import DictDB
```

### Constructeur

```python
DictDB()
```

Initialise une instance de base de données vide.

### Méthodes

#### create_table

```python
db.create_table(table_name: str, primary_key: str = "id") -> None
```

Crée une nouvelle table.

| Paramètre | Type | Par défaut | Description |
|-----------|------|------------|-------------|
| `table_name` | `str` | - | Nom de la table |
| `primary_key` | `str` | `"id"` | Champ à utiliser comme clé primaire |

**Note :** Pour utiliser la validation par schéma, vous pouvez soit spécifier le paramètre `schema` lors de la création, soit créer un objet `Table` directement et l'enregistrer via `db.tables[nom] = table`.

**Exceptions :** Lève `DuplicateTableError` si la table existe déjà.

#### drop_table

```python
db.drop_table(table_name: str) -> None
```

Supprime définitivement une table de la base de données.

**Exceptions :** Lève `TableNotFoundError` si la table n'existe pas.

#### get_table

```python
db.get_table(table_name: str) -> Table
```

Récupère une référence vers une table existante.

**Exceptions :** Lève `TableNotFoundError` si la table n'existe pas.

#### list_tables

```python
db.list_tables() -> list[str]
```

Retourne la liste des noms de toutes les tables présentes.

#### save

```python
db.save(filename: str | Path, file_format: str) -> None
```

Sauvegarde l'intégralité de la base sur le disque.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `filename` | `str \| Path` | Chemin du fichier de destination |
| `file_format` | `str` | `"json"` ou `"pickle"` |

#### load (méthode de classe)

```python
DictDB.load(filename: str | Path, file_format: str) -> DictDB
```

Charge une base de données depuis un fichier.

#### async_save

```python
await db.async_save(filename: str | Path, file_format: str) -> None
```

Version asynchrone de `save()`, idéale pour ne pas bloquer la boucle d'événements.

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

Importe les données d'un fichier CSV vers une nouvelle table.

| Paramètre | Type | Par défaut | Description |
|-----------|------|------------|-------------|
| `filepath` | `str \| Path` | - | Chemin vers le fichier CSV |
| `table_name` | `str` | - | Nom de la table à créer |
| `primary_key` | `str` | `"id"` | Champ de clé primaire |
| `delimiter` | `str` | `","` | Séparateur de colonnes |
| `has_header` | `bool` | `True` | Indique si la première ligne est l'en-tête |
| `encoding` | `str` | `"utf-8"` | Encodage du fichier |
| `schema` | `dict[str, type]` | `None` | Schéma de typage manuel |
| `infer_types` | `bool` | `True` | Détection auto des types (int, float) |
| `skip_validation` | `bool` | `False` | Ignore la validation par schéma |

**Retourne :** Le nombre d'enregistrements importés.

**Exceptions :** Lève `DuplicateTableError` si la table cible existe déjà.

Pour plus de détails, consultez le [Guide CSV](guides/csv.md).

---

## Table

Représente une table et permet d'effectuer les opérations CRUD.

### Méthodes

#### insert

```python
table.insert(record: dict) -> Any
table.insert(record: list[dict], batch_size: int = None, skip_validation: bool = False) -> list[Any]
```

Insère un ou plusieurs enregistrements et retourne la ou les clé(s) primaire(s).

| Paramètre | Type | Par défaut | Description |
|-----------|------|------------|-------------|
| `record` | `dict \| list[dict]` | - | Données à insérer |
| `batch_size` | `int` | `None` | Taille des lots pour les insertions massives |
| `skip_validation` | `bool` | `False` | Désactive la validation pour gagner en performance |

L'opération est atomique pour les listes : si une insertion échoue, toute la transaction est annulée.

**Exceptions :**

- `DuplicateKeyError` : Clé primaire déjà utilisée.
- `SchemaValidationError` : Données non conformes au schéma.

#### upsert

```python
table.upsert(record: dict, on_conflict: str = "update") -> tuple[Any, str]
```

Insère un enregistrement ou gère le conflit si la clé existe déjà.

| Paramètre | Type | Par défaut | Description |
|-----------|------|------------|-------------|
| `record` | `dict` | - | Données à insérer ou mettre à jour |
| `on_conflict` | `str` | `"update"` | Stratégie : `"update"`, `"ignore"` ou `"error"` |

**Retourne :** Un tuple `(clé_primaire, action)` où action est `"inserted"`, `"updated"` ou `"ignored"`.

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

Récupère les enregistrements correspondant aux critères.

| Paramètre | Type | Par défaut | Description |
|-----------|------|------------|-------------|
| `columns` | `list \| dict` | `None` | Projection ou alias de colonnes |
| `where` | `Condition \| PredicateExpr` | `None` | Filtre de sélection |
| `order_by` | `str \| list` | `None` | Critères de tri |
| `limit` | `int` | `None` | Nombre max de résultats |
| `offset` | `int` | `0` | Sauter les N premiers résultats |
| `copy` | `bool` | `True` | Retourner des copies indépendantes |
| `distinct` | `bool` | `False` | Éliminer les doublons |

#### update

```python
table.update(changes: dict, where: Condition | PredicateExpr = None) -> int
```

Modifie les enregistrements correspondants et retourne leur nombre.

**Exceptions :**

- `RecordNotFoundError` : Si aucun enregistrement n'est trouvé.
- `SchemaValidationError` : Si les changements sont invalides.

#### delete

```python
table.delete(where: Condition | PredicateExpr = None) -> int
```

Supprime les enregistrements correspondants et retourne leur nombre.

**Exceptions :** Lève `RecordNotFoundError` si aucun enregistrement n'est trouvé.

#### create_index

```python
table.create_index(field: str, index_type: str = "hash") -> None
```

Crée un index pour accélérer les recherches sur un champ.

| Paramètre | Type | Par défaut | Description |
|-----------|------|------------|-------------|
| `field` | `str` | - | Champ à indexer |
| `index_type` | `str` | `"hash"` | `"hash"` ou `"sorted"` |

### Introspection

```python
table.count() -> int              # Nombre d'enregistrements
table.size() -> int               # Alias de count()
table.columns() -> list[str]      # Liste des noms de colonnes
table.primary_key_name() -> str   # Nom du champ de clé primaire
table.indexed_fields() -> list[str]  # Champs indexés
table.has_index(field: str) -> bool  # Vérifie l'existence d'un index
table.schema_fields() -> list[str]   # Champs définis dans le schéma
```

### Autres méthodes

```python
table.all() -> list[dict]         # Tous les enregistrements (copies)
table.copy() -> dict[Any, dict]   # Dictionnaire complet {pk: copie}
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

Exporte les données vers un fichier CSV.

**Retourne :** Le nombre d'enregistrements écrits.

---

## Condition

Enveloppe une expression de prédicat. **Son utilisation est facultative** : vous pouvez passer une `PredicateExpr` directement à `where=`.

```python
from dictdb import Condition
```

### Constructeur

```python
Condition(predicate_expr)
```

### Exemple

```python
# Syntaxe recommandée
table.select(where=table.field == valeur)

# Syntaxe avec enveloppe explicite
table.select(where=Condition(table.field == valeur))
```

---

## Fonctions logiques

Permettent de combiner plusieurs conditions.

```python
from dictdb import And, Or, Not
```

### And

```python
And(*conditions) -> PredicateExpr
```

Vrai si **toutes** les conditions sont remplies.

### Or

```python
Or(*conditions) -> PredicateExpr
```

Vrai si **au moins une** condition est remplie.

### Not

```python
Not(condition) -> PredicateExpr
```

Inverse le résultat d'une condition.

---

## Opérateurs de champ

Accessibles via l'attribut de table : `table.nom_du_champ`.

### Comparaison standard

```python
table.field == valeur    # Égalité
table.field != valeur    # Inégalité
table.field < valeur     # Strictement inférieur
table.field <= valeur    # Inférieur ou égal
table.field > valeur     # Strictement supérieur
table.field >= valeur    # Supérieur ou égal
```

### Méthodes spécialisées

```python
table.field.is_in([v1, v2])      # Opérateur IN
table.field.between(low, high)   # Intervalle inclusif
table.field.like("A%")           # Motif LIKE SQL (% = tout, _ = un seul car.)
table.field.startswith("prefix") # Démarre par
table.field.endswith("suffix")   # Se termine par
table.field.contains("substr")   # Contient la chaîne
table.field.is_null()            # Est None ou absent
table.field.is_not_null()        # N'est pas None
```

### Variantes insensibles à la casse

```python
table.field.iequals("valeur")    # Égalité (case-insensitive)
table.field.icontains("substr")  # Contient (case-insensitive)
table.field.istartswith("pre")   # Démarre par (case-insensitive)
table.field.iendswith("suf")     # Se termine par (case-insensitive)
table.field.ilike("A%")          # LIKE (case-insensitive)
```

---

## BackupManager

Gère la sauvegarde automatique en arrière-plan.

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
backup.start() -> None        # Lance le thread d'arrière-plan
backup.stop() -> None         # Arrête proprement le thread
backup.backup_now() -> None   # Déclenche une sauvegarde immédiate
backup.notify_change() -> None  # Signale une modif (avec délai anti-rebond)
```

---

## Logging (Journalisation)

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

---

## Agrégations

Fonctions de type SQL pour vos analyses.

```python
from dictdb import Count, Sum, Avg, Min, Max
```

| Classe | Description |
|--------|-------------|
| `Count(field=None)` | Compte les enregistrements (ou les valeurs non-None) |
| `Sum(field)` | Calcule la somme numérique |
| `Avg(field)` | Calcule la moyenne numérique |
| `Min(field)` | Trouve la valeur minimale |
| `Max(field)` | Trouve la valeur maximale |

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

Toutes ces exceptions héritent de `DictDBError`.