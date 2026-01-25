# Mon premier carnet de contacts

## Prologue : Une découverte inattendue

C'était un mardi matin comme les autres. Alex, développeur Python depuis trois ans, sirotait son café en fixant son écran. La tâche semblait simple : créer un carnet de contacts pour l'équipe. Rien de bien compliqué, mais sortir l'artillerie lourde paraissait excessif. Pas de PostgreSQL, ni de SQLite. Juste quelque chose de léger et d'élégant.

C'est alors qu'Alex découvrit DictDB.

## Chapitre 1 : Premiers pas

Alex ouvrit son terminal et installa le paquet :

```bash
pip install dctdb
```

Puis, mêlant curiosité et excitation, il écrivit ses premières lignes de code :

```python
from dictdb import DictDB

# Créer une nouvelle base de données
db = DictDB()

# Créer une table pour les contacts
db.create_table("contacts")

# Récupérer une référence vers la table
contacts = db.get_table("contacts")

print("Base de données créée avec succès !")
print(f"Tables disponibles : {db.list_tables()}")
```

```
Base de données créée avec succès !
Tables disponibles : ['contacts']
```

« C'est tout ? » pensa Alex. « C'est vraiment aussi simple que ça ? »

## Chapitre 2 : Ajouter des contacts

Alex commença à remplir le carnet avec les membres de l'équipe :

```python
# Ajouter le premier contact
contacts.insert({
    "last_name": "Dupont",
    "first_name": "Jean",
    "email": "jean.dupont@entreprise.com",
    "phone": "01-23-45-67-89"
})

# Ajouter d'autres contacts
contacts.insert({
    "last_name": "Martin",
    "first_name": "Sophie",
    "email": "sophie.martin@entreprise.com",
    "phone": "01-98-76-54-32"
})

contacts.insert({
    "last_name": "Bernard",
    "first_name": "Pierre",
    "email": "pierre.bernard@entreprise.com",
    "phone": "01-11-22-33-44"
})

contacts.insert({
    "last_name": "Dubois",
    "first_name": "Claire",
    "email": "claire.dubois@entreprise.com",
    "phone": "01-55-66-77-88"
})

print(f"Nombre de contacts : {contacts.count()}")
```

```
Nombre de contacts : 4
```

Alex remarqua que chaque méthode `insert` renvoyait un identifiant unique. DictDB générait automatiquement une clé primaire `id` pour chaque enregistrement.

## Chapitre 3 : Retrouver des contacts

Le carnet se remplissait, mais à quoi bon stocker des données si on ne peut pas les retrouver ?

```python
# Afficher tous les contacts
all_contacts = contacts.select()

print("=== Tous mes contacts ===")
for contact in all_contacts:
    print(f"{contact['first_name']} {contact['last_name']} - {contact['email']}")
```

```
=== Tous mes contacts ===
Jean Dupont - jean.dupont@entreprise.com
Sophie Martin - sophie.martin@entreprise.com
Pierre Bernard - pierre.bernard@entreprise.com
Claire Dubois - claire.dubois@entreprise.com
```

Alex voulait rechercher un contact spécifique. La puissance du DSL de requêtes devint alors évidente :

```python
from dictdb import Condition

# Trouver Sophie
sophie = contacts.select(where=Condition(contacts.first_name == "Sophie"))
print(f"Contact trouvé : {sophie[0]['first_name']} {sophie[0]['last_name']}")

# Trouver tous les contacts dont le nom commence par 'B'
contacts_b = contacts.select(where=contacts.last_name.startswith("B"))
print("\nContacts dont le nom commence par B :")
for c in contacts_b:
    print(f"  - {c['first_name']} {c['last_name']}")
```

```
Contact trouvé : Sophie Martin

Contacts dont le nom commence par B :
  - Pierre Bernard
```

!!! tip "Condition est facultatif"
    Vous pouvez passer l'expression directement au paramètre `where` sans l'envelopper dans `Condition()`. Les deux syntaxes fonctionnent !

## Chapitre 4 : Mettre à jour un contact

Un jour, Pierre Bernard changea de numéro de téléphone. Alex dut mettre à jour le carnet :

```python
# Mettre à jour le numéro de téléphone de Pierre
modified_count = contacts.update(
    {"phone": "01-99-88-77-66"},
    where=Condition(contacts.first_name == "Pierre")
)

print(f"Nombre de contacts modifiés : {modified_count}")

# Vérifier la modification
pierre = contacts.select(where=contacts.first_name == "Pierre")[0]
print(f"Nouveau numéro de Pierre : {pierre['phone']}")
```

```
Nombre de contacts modifiés : 1
Nouveau numéro de Pierre : 01-99-88-77-66
```

## Chapitre 5 : Supprimer un contact

Malheureusement, Jean Dupont quitta l'entreprise. Alex dut le retirer du carnet :

```python
# Retirer Jean du carnet
deleted_count = contacts.delete(where=Condition(contacts.first_name == "Jean"))

print(f"Nombre de contacts supprimés : {deleted_count}")
print(f"Contacts restants : {contacts.count()}")
```

```
Nombre de contacts supprimés : 1
Contacts restants : 3
```

## Chapitre 6 : Sauvegarder son travail

Alex réalisa qu'il serait dommage de perdre tout ce travail. DictDB permettait de sauvegarder les données dans un fichier JSON :

```python
# Sauvegarder la base de données
db.save("contact_book.json", file_format="json")

print("Base de données sauvegardée !")
```

Le fichier JSON généré était parfaitement lisible :

```json
{
  "tables": {
    "contacts": {
      "primary_key": "id",
      "schema": null,
      "records": [
        {
          "id": 2,
          "last_name": "Martin",
          "first_name": "Sophie",
          "email": "sophie.martin@entreprise.com",
          "phone": "01-98-76-54-32"
        },
        ...
      ]
    }
  }
}
```

## Chapitre 7 : Reprendre là où on s'était arrêté

Le lendemain matin, Alex reprit le travail. Charger la base de données fut un jeu d'enfant :

```python
from dictdb import DictDB

# Charger la base de données sauvegardée
db = DictDB.load("contact_book.json", file_format="json")

# Récupérer la table des contacts
contacts = db.get_table("contacts")

print(f"Base chargée ! {contacts.count()} contacts trouvés.")

# Vérifier que tout est là
for contact in contacts.select():
    print(f"  - {contact['first_name']} {contact['last_name']}")
```

```
Base chargée ! 3 contacts trouvés.
  - Sophie Martin
  - Pierre Bernard
  - Claire Dubois
```

## Épilogue : Un carnet de contacts complet

Alex était satisfait. En seulement quelques lignes de code, un carnet de contacts entièrement fonctionnel avait vu le jour. Voici le script complet partagé avec l'équipe :

```python
from dictdb import DictDB, Condition

def main():
    # Créer ou charger la base de données
    try:
        db = DictDB.load("contact_book.json", file_format="json")
        print("Carnet de contacts chargé !")
    except FileNotFoundError:
        db = DictDB()
        db.create_table("contacts")
        print("Nouveau carnet de contacts créé !")

    contacts = db.get_table("contacts")

    # Ajouter un nouveau contact
    new_id = contacts.insert({
        "last_name": "Leroy",
        "first_name": "Emma",
        "email": "emma.leroy@entreprise.com",
        "phone": "01-00-11-22-33"
    })
    print(f"Contact ajouté avec l'id {new_id}")

    # Afficher tous les contacts
    print("\n=== Carnet de Contacts ===")
    for contact in contacts.select(order_by="last_name"):
        print(f"{contact['first_name']} {contact['last_name']}")
        print(f"  Email : {contact['email']}")
        print(f"  Tél   : {contact['phone']}")
        print()

    # Sauvegarder
    db.save("contact_book.json", file_format="json")
    print("Carnet de contacts sauvegardé !")

if __name__ == "__main__":
    main()
```

## Ce que nous avons appris

Dans ce tutoriel, nous avons découvert les bases de DictDB :

| Concept | Code |
|---------|------|
| Créer une base de données | `db = DictDB()` |
| Créer une table | `db.create_table("name")` |
| Récupérer une table | `table = db.get_table("name")` |
| Insérer un enregistrement | `table.insert({...})` |
| Sélectionner des enregistrements | `table.select()` |
| Filtrer avec une condition | `table.select(where=table.field == value)` |
| Mettre à jour des enregistrements | `table.update({...}, where=...)` |
| Supprimer des enregistrements | `table.delete(where=...)` |
| Sauvegarder en JSON | `db.save("file.json", file_format="json")` |
| Charger depuis JSON | `DictDB.load("file.json", file_format="json")` |

## Prochaines étapes

Alex était prêt pour de nouveaux défis. Dans le prochain chapitre, découvrez comment gérer plusieurs tables liées entre elles, utiliser des requêtes plus avancées et optimiser les recherches.

[Continuer vers « La bibliothèque de quartier » &rarr;](02-library.md)