# Persistance

DictDB prend en charge la sauvegarde et le chargement des bases de données sur disque aux formats JSON ou Pickle.

## Sauvegarde

### Format JSON

Format lisible par l'humain, adapté au débogage et à l'interopérabilité :

```python
db.save("database.json", file_format="json")
```

Structure de sortie JSON :

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

Format binaire, plus rapide et prenant en charge tous les types Python :

```python
db.save("database.pkl", file_format="pickle")
```

!!! avertissement "Sécurité"
    Les fichiers Pickle peuvent exécuter du code arbitraire lors du chargement. Ne chargez que des fichiers pickle provenant de sources fiables. DictDB utilise un désérialiseur restreint qui n'autorise que les classes figurant sur une liste blanche.

## Chargement

```python
# Charger depuis JSON
db = DictDB.load("database.json", file_format="json")

# Charger depuis Pickle
db = DictDB.load("database.pkl", file_format="pickle")
```

## E/S asynchrones

Pour les opérations non bloquantes dans les applications asynchrones :

```python
import asyncio

async def save_and_load():
    # Sauvegarde asynchrone
    await db.async_save("database.json", file_format="json")

    # Chargement asynchrone
    db = await DictDB.async_load("database.json", file_format="json")
```

Ces méthodes exécutent les opérations d'E/S dans un pool de threads pour éviter de bloquer la boucle d'événements.

## Comparaison des formats

| Caractéristique | JSON | Pickle |
|-----------------|------|--------|
| Lisible par l'humain | Oui | Non |
| Vitesse | Plus lent | Plus rapide |
| Taille du fichier | Plus grande | Plus petite |
| Types Python | Limités | Tous |
| Sécurité | Sûr | Restreint |
| Interopérabilité | Élevée | Python uniquement |

## Ce qui est persisté

**Sauvegardé :**

- Toutes les tables et leurs noms
- Configuration de la clé primaire
- Définitions de schéma
- Tous les enregistrements

**Non sauvegardé :**

- Index (à recréer après le chargement)
- État d'exécution (verrous, suivi des modifications)

## Recréation des index après le chargement

```python
# Sauvegarde
employees.create_index("department")
db.save("data.json", file_format="json")

# Chargement
db = DictDB.load("data.json", file_format="json")
employees = db.get_table("employees")

# Les index doivent être recréés
employees.create_index("department")
```

## Persistance du schéma

Les schémas sont entièrement préservés :

```python
# Création avec schéma
schema = {"id": int, "name": str, "score": float}
db.create_table("players", schema=schema)

# Sauvegarde et chargement
db.save("game.json", file_format="json")
db = DictDB.load("game.json", file_format="json")

# Le schéma est restauré
players = db.get_table("players")
print(players.schema)  # {"id": int, "name": str, "score": float}
```

## Écritures en flux continu

Pour les grandes bases de données, les sauvegardes JSON utilisent le streaming pour réduire l'utilisation de la mémoire :

```python
# Grande base de données
for i in range(100000):
    users.insert({"name": f"User {i}"})

# Écriture en streaming - ne charge pas toute la BD en mémoire
db.save("large.json", file_format="json")
```

## Gestion des erreurs

```python
from pathlib import Path

# Fichier non trouvé
try:
    db = DictDB.load("missing.json", file_format="json")
except FileNotFoundError:
    print("Fichier de base de données non trouvé")

# Format invalide
try:
    db.save("data.txt", file_format="xml")
except ValueError as e:
    print(e)  # Unsupported file_format. Please use 'json' or 'pickle'.
```

## Types de chemins

Les chaînes de caractères et les objets `Path` sont acceptés :

```python
from pathlib import Path

# Chemin sous forme de chaîne
db.save("data.json", file_format="json")

# Objet Path
db.save(Path("data") / "database.json", file_format="json")
```

## Exemple

```python
from dictdb import DictDB, Condition

# Créer et remplir la base de données
db = DictDB()
db.create_table("config", primary_key="key")
config = db.get_table("config")

config.insert({"key": "version", "value": "1.0.0"})
config.insert({"key": "debug", "value": True})
config.insert({"key": "max_connections", "value": 100})

# Sauvegarder en JSON pour édition manuelle
db.save("config.json", file_format="json")

# Plus tard : charger et utiliser
db = DictDB.load("config.json", file_format="json")
config = db.get_table("config")

version = config.select(where=Condition(config.key == "version"))[0]["value"]
print(f"Version: {version}")
```
