# Exemples pratiques

Bienvenue dans la section des exemples ! Ici, vous allez découvrir DictDB à travers des cas d'utilisation concrets, présentés sous forme d'histoires progressives.

## Parcours d'apprentissage

Chaque exemple raconte une histoire et introduit de nouvelles fonctionnalités. Suivez-les dans l'ordre pour une expérience d'apprentissage graduelle, ou sautez directement à celui qui correspond à vos besoins.

### Niveau débutant

| Exemple | Description | Fonctionnalités |
|---------|-------------|-----------------|
| [Mon premier carnet de contacts](01-contact-book.md) | Découvrez DictDB en construisant une application simple | CRUD, persistance JSON |
| [La bibliothèque de quartier](02-library.md) | Gérez plusieurs tables liées entre elles | Multi-tables, Query DSL, tri, pagination |

### Niveau intermédiaire

| Exemple | Description | Fonctionnalités |
|---------|-------------|-----------------|
| [Ma boutique en ligne](03-online-store.md) | Construisez un catalogue de produits | Schémas, index, recherche avancée, upsert |
| [Le tableau de bord du directeur commercial](04-sales-dashboard.md) | Analysez les performances de votre équipe | Agrégations, GROUP BY, statistiques |

### Niveau avancé

| Exemple | Description | Fonctionnalités |
|---------|-------------|-----------------|
| [Migration de données historiques](05-data-migration.md) | Migrez des données depuis des fichiers CSV | Import/export CSV, transformation |
| [Prêt pour la production](06-production-ready.md) | Déploiement en production | Sauvegardes, concurrence, async, logging |

## Fonctionnalités couvertes

À la fin de ce parcours d'apprentissage, vous maîtriserez :

- **CRUD complet** : insert, select, update, delete, upsert
- **Query DSL** : comparaisons, LIKE, BETWEEN, is_in, is_null
- **Opérateurs logiques** : And, Or, Not
- **Recherche** : sensible et insensible à la casse
- **Index** : hash et sorted pour des requêtes performantes
- **Schémas** : validation des types
- **Agrégations** : Count, Sum, Avg, Min, Max avec GROUP BY
- **CSV** : import et export de données
- **Persistance** : JSON et Pickle
- **Production** : sauvegardes, concurrence, async, logging

## Comment utiliser ces exemples

Chaque exemple est conçu pour être :

1. **Autonome** : vous pouvez copier-coller le code et l'exécuter
2. **Progressif** : les concepts s'enchaînent de manière logique
3. **Pratique** : basé sur des cas d'utilisation réels

```python
# Installation rapide
pip install dctdb

# Puis suivez les exemples !
from dictdb import DictDB
```

Prêt à commencer ? [Mon premier carnet de contacts](01-contact-book.md) vous attend !