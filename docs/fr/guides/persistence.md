# Persistance

DictDB permet de sauvegarder l'intégralité de vos bases de données sur le disque et de les recharger ultérieurement aux formats JSON ou Pickle.

## Sauvegarde

### Format JSON

C'est un format lisible par l'humain, idéal pour le débogage, l'édition manuelle ou l'interopérabilité avec d'autres outils.

```python
db.save("database.json", file_format="json")
```

Structure du fichier JSON :

```json
{
  "tables": {
    "users": {
      "primary_key": "id",
      "schema": null,
      "records": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
      ]
    }
  }
}
```

### Format Pickle

C'est un format binaire natif à Python. Il est beaucoup plus rapide et gère nativement tous les types d'objets Python.

```python
db.save("database.pkl", file_format="pickle")
```

!!! warning "Sécurité"
    Le format Pickle peut exécuter du code arbitraire lors du chargement. Ne chargez que des fichiers provenant de sources sûres. DictDB utilise un dé-sérialiseur restreint pour limiter les risques.

## Chargement

```python
# Charger depuis JSON
db = DictDB.load("database.json", file_format="json")

# Charger depuis Pickle
db = DictDB.load("database.pkl", file_format="pickle")
```

## Entrées/Sorties asynchrones (Async I/O)

Pour vos applications web ou asynchrones, utilisez les méthodes dédiées pour ne pas bloquer votre application :

```python
import asyncio

async def ma_logique():
    # Sauvegarde en arrière-plan
    await db.async_save("database.json", file_format="json")

    # Chargement en arrière-plan
    db = await DictDB.async_load("database.json", file_format="json")
```

Ces méthodes utilisent un pool de threads pour gérer l'écriture disque sans geler la boucle d'événements.

## Comparaison des formats

| Caractéristique | JSON | Pickle |
|-----------------|------|--------|
| Lisible par l'humain | Oui | Non |
| Vitesse | Modérée | Très rapide |
| Taille de fichier | Importante | Compacte |
| Types supportés | Limités | Tous (Python) |
| Sécurité | Élevée | Restreinte |
| Interopérabilité | Excellente | Python uniquement |

## Ce qui est conservé

**Éléments sauvegardés :**

- Toutes les tables et leurs noms.
- La configuration de la clé primaire.
- Les définitions des schémas.
- L'intégralité des enregistrements.

**Éléments perdus (à recréer) :**

- Les index (à recréer après chargement).
- L'état d'exécution (verrous en cours, suivi des modifs temporaires).

## Persistance des schémas

Les schémas de données sont intégralement conservés et restaurés. Si vous aviez imposé des types stricts, ils seront de nouveau opérationnels après le chargement.

```python
schema = {"id": int, "score": float}
db.create_table("players", schema=schema)

db.save("game.json", file_format="json")
# Plus tard...
db = DictDB.load("game.json", file_format="json")
# Le schéma est de nouveau là
print(db.get_table("players").schema)
```

## Écritures en flux (Streaming)

Pour les bases de données volumineuses, l'export JSON utilise un mécanisme de streaming afin de réduire l'empreinte mémoire lors de l'écriture sur le disque.

## Gestion des erreurs

```python
from pathlib import Path

# Fichier inexistant
try:
    db = DictDB.load("introuvable.json", file_format="json")
except FileNotFoundError:
    print("Le fichier spécifié est introuvable.")

# Format non supporté
try:
    db.save("data.txt", file_format="xml")
except ValueError as e:
    print(e)  # Unsupported file_format. Please use 'json' or 'pickle'.
```