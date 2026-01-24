# Exemples pratiques

Bienvenue dans la section des exemples ! Ici, vous allez decouvrir DictDB a travers des cas d'utilisation concrets, presentes sous forme d'histoires progressives.

## Parcours d'apprentissage

Chaque exemple raconte une histoire et introduit de nouvelles fonctionnalites. Suivez-les dans l'ordre pour une experience d'apprentissage graduelle, ou sautez directement a celui qui correspond a vos besoins.

### Niveau debutant

| Exemple | Description | Fonctionnalites |
|---------|-------------|-----------------|
| [Mon premier carnet de contacts](01-contact-book.md) | Decouvrez DictDB en construisant une application simple | CRUD, persistance JSON |
| [La bibliotheque de quartier](02-library.md) | Gerez plusieurs tables liees entre elles | Multi-tables, Query DSL, tri, pagination |

### Niveau intermediaire

| Exemple | Description | Fonctionnalites |
|---------|-------------|-----------------|
| [Ma boutique en ligne](03-online-store.md) | Construisez un catalogue de produits | Schemas, index, recherche avancee, upsert |
| [Le tableau de bord du directeur commercial](04-sales-dashboard.md) | Analysez les performances de votre equipe | Agregations, GROUP BY, statistiques |

### Niveau avance

| Exemple | Description | Fonctionnalites |
|---------|-------------|-----------------|
| [Migration de donnees legacy](05-data-migration.md) | Migrez des donnees depuis des fichiers CSV | Import/export CSV, transformation |
| [Pret pour la production](06-production-ready.md) | Deploiement en production | Sauvegardes, concurrence, async, logging |

## Fonctionnalites couvertes

A la fin de ce parcours d'apprentissage, vous maitriserez :

- **CRUD complet** : insert, select, update, delete, upsert
- **Query DSL** : comparaisons, LIKE, BETWEEN, is_in, is_null
- **Operateurs logiques** : And, Or, Not
- **Recherche** : sensible et insensible a la casse
- **Index** : hash et sorted pour des requetes performantes
- **Schemas** : validation des types
- **Agregations** : Count, Sum, Avg, Min, Max avec GROUP BY
- **CSV** : import et export de donnees
- **Persistance** : JSON et Pickle
- **Production** : sauvegardes, concurrence, async, logging

## Comment utiliser ces exemples

Chaque exemple est concu pour etre :

1. **Autonome** : vous pouvez copier-coller le code et l'executer
2. **Progressif** : les concepts s'enchainent de maniere logique
3. **Pratique** : base sur des cas d'utilisation reels

```python
# Installation rapide
pip install dctdb

# Puis suivez les exemples !
from dictdb import DictDB
```

Pret a commencer ? [Mon premier carnet de contacts](01-contact-book.md) vous attend !
