# Mon premier carnet de contacts

## Prologue : Une decouverte inattendue

C'etait un mardi matin comme les autres. Alex, developpeur Python depuis trois ans maintenant, sirotait son cafe en fixant l'ecran. La tache semblait assez simple : creer un carnet de contacts pour l'equipe. Rien de bien complique, mais sortir l'artillerie lourde semblait excessif. Pas de PostgreSQL, pas de SQLite. Juste quelque chose de leger et elegant.

C'est alors qu'Alex decouvrit DictDB.

## Chapitre 1 : Premiers pas

Alex ouvrit le terminal et installa le paquet :

```bash
pip install dctdb
```

Puis, avec un melange de curiosite et d'excitation, les premieres lignes de code apparurent :

```python
from dictdb import DictDB

# Create a new database
db = DictDB()

# Create a table for contacts
db.create_table("contacts")

# Get a reference to the table
contacts = db.get_table("contacts")

print("Database created successfully!")
print(f"Available tables: {db.list_tables()}")
```

```
Database created successfully!
Available tables: ['contacts']
```

« C'est tout ? » pensa Alex. « C'est vraiment aussi simple que ca ? »

## Chapitre 2 : Ajouter des contacts

Alex commenca a remplir le carnet de contacts avec les membres de l'equipe :

```python
# Add the first contact
contacts.insert({
    "last_name": "Dupont",
    "first_name": "Jean",
    "email": "jean.dupont@entreprise.com",
    "phone": "01-23-45-67-89"
})

# Add more contacts
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

print(f"Number of contacts: {contacts.count()}")
```

```
Number of contacts: 4
```

Alex remarqua que chaque `insert` renvoyait un identifiant unique. DictDB generait automatiquement une cle primaire `id` pour chaque enregistrement.

## Chapitre 3 : Retrouver des contacts

Le carnet de contacts se remplissait, mais a quoi bon stocker des donnees si on ne peut pas les retrouver ?

```python
# Display all contacts
all_contacts = contacts.select()

print("=== All My Contacts ===")
for contact in all_contacts:
    print(f"{contact['first_name']} {contact['last_name']} - {contact['email']}")
```

```
=== All My Contacts ===
Jean Dupont - jean.dupont@entreprise.com
Sophie Martin - sophie.martin@entreprise.com
Pierre Bernard - pierre.bernard@entreprise.com
Claire Dubois - claire.dubois@entreprise.com
```

Alex voulait chercher un contact specifique. La puissance du DSL de requetes devint evidente :

```python
from dictdb import Condition

# Find Sophie
sophie = contacts.select(where=Condition(contacts.first_name == "Sophie"))
print(f"Contact found: {sophie[0]['first_name']} {sophie[0]['last_name']}")

# Find all contacts whose last name starts with 'B'
contacts_b = contacts.select(where=contacts.last_name.startswith("B"))
print("\nContacts whose last name starts with B:")
for c in contacts_b:
    print(f"  - {c['first_name']} {c['last_name']}")
```

```
Contact found: Sophie Martin

Contacts whose last name starts with B:
  - Pierre Bernard
```

!!! tip "Condition est optionnel"
    Vous pouvez passer l'expression directement au parametre `where` sans l'envelopper dans `Condition()`. Les deux syntaxes fonctionnent !

## Chapitre 4 : Mettre a jour un contact

Un jour, Pierre Bernard changea de numero de telephone. Alex devait mettre a jour le carnet de contacts :

```python
# Update Pierre's phone number
modified_count = contacts.update(
    {"phone": "01-99-88-77-66"},
    where=Condition(contacts.first_name == "Pierre")
)

print(f"Number of contacts modified: {modified_count}")

# Verify the modification
pierre = contacts.select(where=contacts.first_name == "Pierre")[0]
print(f"Pierre's new phone number: {pierre['phone']}")
```

```
Number of contacts modified: 1
Pierre's new phone number: 01-99-88-77-66
```

## Chapitre 5 : Supprimer un contact

Malheureusement, Jean Dupont quitta l'entreprise. Alex devait le retirer du carnet de contacts :

```python
# Remove Jean from the contact book
deleted_count = contacts.delete(where=Condition(contacts.first_name == "Jean"))

print(f"Number of contacts deleted: {deleted_count}")
print(f"Remaining contacts: {contacts.count()}")
```

```
Number of contacts deleted: 1
Remaining contacts: 3
```

## Chapitre 6 : Sauvegarder son travail

Alex realisa qu'il serait dommage de perdre tout ce travail. DictDB pouvait sauvegarder les donnees dans un fichier JSON :

```python
# Save the database
db.save("contact_book.json", file_format="json")

print("Database saved!")
```

Le fichier JSON cree etait parfaitement lisible :

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

## Chapitre 7 : Reprendre la ou on s'etait arrete

Le lendemain matin, Alex reprit le travail. Charger la base de donnees fut un jeu d'enfant :

```python
from dictdb import DictDB

# Load the saved database
db = DictDB.load("contact_book.json", file_format="json")

# Get the contacts table
contacts = db.get_table("contacts")

print(f"Database loaded! {contacts.count()} contacts found.")

# Verify everything is there
for contact in contacts.select():
    print(f"  - {contact['first_name']} {contact['last_name']}")
```

```
Database loaded! 3 contacts found.
  - Sophie Martin
  - Pierre Bernard
  - Claire Dubois
```

## Epilogue : Un carnet de contacts complet

Alex etait satisfait. En seulement quelques lignes de code, un carnet de contacts entierement fonctionnel avait vu le jour. Voici le script complet partage avec l'equipe :

```python
from dictdb import DictDB, Condition

def main():
    # Create or load the database
    try:
        db = DictDB.load("contact_book.json", file_format="json")
        print("Contact book loaded!")
    except FileNotFoundError:
        db = DictDB()
        db.create_table("contacts")
        print("New contact book created!")

    contacts = db.get_table("contacts")

    # Add a new contact
    new_id = contacts.insert({
        "last_name": "Leroy",
        "first_name": "Emma",
        "email": "emma.leroy@entreprise.com",
        "phone": "01-00-11-22-33"
    })
    print(f"Contact added with id {new_id}")

    # Display all contacts
    print("\n=== Contact Book ===")
    for contact in contacts.select(order_by="last_name"):
        print(f"{contact['first_name']} {contact['last_name']}")
        print(f"  Email: {contact['email']}")
        print(f"  Phone: {contact['phone']}")
        print()

    # Save
    db.save("contact_book.json", file_format="json")
    print("Contact book saved!")

if __name__ == "__main__":
    main()
```

## Ce que nous avons appris

Dans ce tutoriel, nous avons decouvert les bases de DictDB :

| Concept | Code |
|---------|------|
| Creer une base de donnees | `db = DictDB()` |
| Creer une table | `db.create_table("name")` |
| Obtenir une table | `table = db.get_table("name")` |
| Inserer un enregistrement | `table.insert({...})` |
| Selectionner des enregistrements | `table.select()` |
| Filtrer avec une condition | `table.select(where=table.field == value)` |
| Mettre a jour des enregistrements | `table.update({...}, where=...)` |
| Supprimer des enregistrements | `table.delete(where=...)` |
| Sauvegarder en JSON | `db.save("file.json", file_format="json")` |
| Charger depuis JSON | `DictDB.load("file.json", file_format="json")` |

## Prochaines etapes

Alex etait pret pour de nouveaux defis. Dans le prochain chapitre, decouvrez comment gerer plusieurs tables liees entre elles, utiliser des requetes plus avancees et optimiser les recherches.

[Continuer vers « La bibliotheque de quartier » &rarr;](02-library.md)
