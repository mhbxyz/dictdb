# La bibliothèque de quartier

## Prologue : Un défi grandissant

Mme Dupont était bibliothécaire depuis vingt ans. Sa petite bibliothèque de quartier avait grandi : des milliers de livres, des centaines d'adhérents, et un système de fiches qui commençait à montrer ses limites.

Son neveu, développeur Python, lui suggéra une solution : « Tante Hélène, laisse-moi te montrer DictDB. C'est simple, léger, et parfait pour ta bibliothèque. »

## Chapitre 1 : Concevoir la structure

Le neveu commença par réfléchir aux données à gérer :

- **Livres** : titre, auteur, genre, année de publication, disponibilité
- **Adhérents** : nom, date d'inscription, email
- **Emprunts** : qui a emprunté quoi, et quand

```python
from dictdb import DictDB

# Créer la base de données de la bibliothèque
db = DictDB()

# Table des livres avec ISBN comme clé primaire
db.create_table("books", primary_key="isbn")

# Table des adhérents avec numéro d'adhérent comme clé
db.create_table("members", primary_key="member_id")

# Table des emprunts
db.create_table("loans")

print("Structure de la bibliothèque créée !")
print(f"Tables : {db.list_tables()}")
```

```
Structure de la bibliothèque créée !
Tables : ['books', 'members', 'loans']
```

## Chapitre 2 : Remplir les étagères

Mme Dupont commença à cataloguer ses livres :

```python
books = db.get_table("books")

# Ajouter des livres au catalogue
books.insert({
    "isbn": "978-2-07-036024-8",
    "title": "Le Petit Prince",
    "author": "Antoine de Saint-Exupéry",
    "genre": "Fiction",
    "year": 1943,
    "available": True
})

books.insert({
    "isbn": "978-2-07-040850-4",
    "title": "L'Étranger",
    "author": "Albert Camus",
    "genre": "Fiction",
    "year": 1942,
    "available": True
})

books.insert({
    "isbn": "978-2-07-036822-0",
    "title": "Les Misérables",
    "author": "Victor Hugo",
    "genre": "Classique",
    "year": 1862,
    "available": True
})

books.insert({
    "isbn": "978-2-07-041239-6",
    "title": "Madame Bovary",
    "author": "Gustave Flaubert",
    "genre": "Classique",
    "year": 1857,
    "available": False  # Déjà emprunté
})

books.insert({
    "isbn": "978-2-07-036842-8",
    "title": "Germinal",
    "author": "Émile Zola",
    "genre": "Naturalisme",
    "year": 1885,
    "available": True
})

books.insert({
    "isbn": "978-2-07-041473-4",
    "title": "Le Rouge et le Noir",
    "author": "Stendhal",
    "genre": "Classique",
    "year": 1830,
    "available": True
})

books.insert({
    "isbn": "978-2-07-040089-8",
    "title": "Vingt mille lieues sous les mers",
    "author": "Jules Verne",
    "genre": "Aventure",
    "year": 1870,
    "available": True
})

print(f"Catalogue : {books.count()} livres")
```

```
Catalogue : 7 livres
```

## Chapitre 3 : Inscrire les adhérents

La bibliothèque accueillit ses premiers adhérents :

```python
members = db.get_table("members")

members.insert({
    "member_id": "ADH001",
    "last_name": "Moreau",
    "first_name": "Julie",
    "email": "julie.moreau@email.com",
    "registration_date": "2024-01-15"
})

members.insert({
    "member_id": "ADH002",
    "last_name": "Petit",
    "first_name": "Thomas",
    "email": "t.petit@email.com",
    "registration_date": "2024-02-20"
})

members.insert({
    "member_id": "ADH003",
    "last_name": "Roux",
    "first_name": "Emma",
    "email": "emma.roux@email.com",
    "registration_date": "2024-03-10"
})

members.insert({
    "member_id": "ADH004",
    "last_name": "Garcia",
    "first_name": "Lucas",
    "email": "lucas.garcia@email.com",
    "registration_date": "2023-11-05"
})

print(f"Adhérents inscrits : {members.count()}")
```

```
Adhérents inscrits : 4
```

## Chapitre 4 : Les opérateurs de comparaison

Mme Dupont voulait retrouver ses livres facilement. Son neveu lui montra la puissance des requêtes :

### Égalité et inégalité

```python
# Trouver les livres de Victor Hugo
hugo_books = books.select(where=books.author == "Victor Hugo")
print("Livres de Victor Hugo :")
for book in hugo_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Livres de Victor Hugo :
  - Les Misérables (1862)
```

```python
# Tous les livres sauf Fiction
non_fiction = books.select(where=books.genre != "Fiction")
print("\nLivres qui ne sont pas de la Fiction :")
for book in non_fiction:
    print(f"  - {book['title']} ({book['genre']})")
```

```
Livres qui ne sont pas de la Fiction :
  - Les Misérables (Classique)
  - Madame Bovary (Classique)
  - Germinal (Naturalisme)
  - Le Rouge et le Noir (Classique)
  - Vingt mille lieues sous les mers (Aventure)
```

### Comparaisons numériques

```python
# Livres publiés au 20ème siècle ou après
modern_books = books.select(where=books.year >= 1900)
print("Livres du 20ème siècle et après :")
for book in modern_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Livres du 20ème siècle et après :
  - Le Petit Prince (1943)
  - L'Étranger (1942)
```

```python
# Livres publiés avant 1900
old_books = books.select(where=books.year < 1900)
print("\nLivres du 19ème siècle et avant :")
for book in old_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Livres du 19ème siècle et avant :
  - Les Misérables (1862)
  - Madame Bovary (1857)
  - Germinal (1885)
  - Le Rouge et le Noir (1830)
  - Vingt mille lieues sous les mers (1870)
```

```python
# Livres publiés exactement en 1862
books_1862 = books.select(where=books.year == 1862)
print("\nLivres publiés en 1862 :")
for book in books_1862:
    print(f"  - {book['title']} par {book['author']}")
```

```
Livres publiés en 1862 :
  - Les Misérables par Victor Hugo
```

## Chapitre 5 : La magie des méthodes sur les chaînes de caractères

Les adhérents ne se souvenaient pas toujours du titre exact. Le neveu présenta les méthodes de recherche textuelle :

### Recherche par début (startswith)

```python
# Titres commençant par "Le"
titles_le = books.select(where=books.title.startswith("Le"))
print("Titres commençant par 'Le' :")
for book in titles_le:
    print(f"  - {book['title']}")
```

```
Titres commençant par 'Le' :
  - Le Petit Prince
  - Le Rouge et le Noir
```

### Recherche par fin (endswith)

```python
# Emails se terminant par '@email.com'
emails_com = members.select(where=members.email.endswith("@email.com"))
print("\nMembres avec une adresse @email.com :")
for member in emails_com:
    print(f"  - {member['first_name']} {member['last_name']}")
```

```
Membres avec une adresse @email.com :
  - Julie Moreau
  - Thomas Petit
  - Emma Roux
  - Lucas Garcia
```

### Recherche par contenu (contains)

```python
# Auteurs contenant "Zola"
authors_zola = books.select(where=books.author.contains("Zola"))
print("\nAuteurs dont le nom contient 'Zola' :")
for book in authors_zola:
    print(f"  - {book['author']} ({book['title']})")
```

```
Auteurs dont le nom contient 'Zola' :
  - Émile Zola (Germinal)
```

!!! tip "Recherche insensible à la casse"
    Utilisez `istartswith()`, `iendswith()` et `icontains()` pour des recherches qui ignorent les majuscules et minuscules.

## Chapitre 6 : Tri et pagination

La bibliothèque grandissait. L'organisation de l'affichage devint essentielle :

### Tri simple

```python
# Livres triés par titre (ordre alphabétique)
sorted_books = books.select(order_by="title")
print("Livres par ordre alphabétique :")
for book in sorted_books:
    print(f"  - {book['title']}")
```

```
Livres par ordre alphabétique :
  - Germinal
  - L'Étranger
  - Le Petit Prince
  - Le Rouge et le Noir
  - Les Misérables
  - Madame Bovary
  - Vingt mille lieues sous les mers
```

### Tri décroissant

```python
# Livres du plus récent au plus ancien
recent_books = books.select(order_by="-year")
print("\nLivres du plus récent au plus ancien :")
for book in recent_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Livres du plus récent au plus ancien :
  - Le Petit Prince (1943)
  - L'Étranger (1942)
  - Germinal (1885)
  - Vingt mille lieues sous les mers (1870)
  - Les Misérables (1862)
  - Madame Bovary (1857)
  - Le Rouge et le Noir (1830)
```

### Pagination

```python
# Afficher les livres par pages de 3
page_size = 3

# Page 1
page1 = books.select(order_by="title", limit=page_size, offset=0)
print("=== Page 1 ===")
for book in page1:
    print(f"  - {book['title']}")

# Page 2
page2 = books.select(order_by="title", limit=page_size, offset=3)
print("\n=== Page 2 ===")
for book in page2:
    print(f"  - {book['title']}")

# Page 3
page3 = books.select(order_by="title", limit=page_size, offset=6)
print("\n=== Page 3 ===")
for book in page3:
    print(f"  - {book['title']}")
```

```
=== Page 1 ===
  - Germinal
  - L'Étranger
  - Le Petit Prince

=== Page 2 ===
  - Le Rouge et le Noir
  - Les Misérables
  - Madame Bovary

=== Page 3 ===
  - Vingt mille lieues sous les mers
```

!!! warning "Toujours trier avant de paginer"
    Sans `order_by`, l'ordre des résultats n'est pas garanti. Spécifiez toujours un tri lors de la pagination pour des résultats cohérents.

## Chapitre 7 : Résultats distincts

Mme Dupont voulait connaître les genres disponibles :

```python
# Obtenir la liste des genres (sans doublons)
genres = books.select(columns=["genre"], distinct=True)
print("Genres disponibles à la bibliothèque :")
for g in genres:
    print(f"  - {g['genre']}")
```

```
Genres disponibles à la bibliothèque :
  - Fiction
  - Classique
  - Naturalisme
  - Aventure
```

```python
# Années de publication uniques, triées
years = books.select(
    columns=["year"],
    distinct=True,
    order_by="year"
)
print("\nAnnées de publication :")
for y in years:
    print(f"  - {y['year']}")
```

```
Années de publication :
  - 1830
  - 1857
  - 1862
  - 1870
  - 1885
  - 1942
  - 1943
```

## Chapitre 8 : Gérer les emprunts

La vie d'une bibliothèque tourne autour des emprunts. Le neveu créa un système complet :

```python
loans = db.get_table("loans")

# Enregistrer des emprunts
loans.insert({
    "member_id": "ADH001",
    "book_isbn": "978-2-07-041239-6",  # Madame Bovary
    "loan_date": "2024-06-01",
    "due_date": "2024-06-15",
    "returned": False
})

loans.insert({
    "member_id": "ADH002",
    "book_isbn": "978-2-07-036024-8",  # Le Petit Prince
    "loan_date": "2024-06-05",
    "due_date": "2024-06-19",
    "returned": True
})

loans.insert({
    "member_id": "ADH003",
    "book_isbn": "978-2-07-040850-4",  # L'Étranger
    "loan_date": "2024-06-10",
    "due_date": "2024-06-24",
    "returned": False
})

print(f"Emprunts enregistrés : {loans.count()}")
```

```
Emprunts enregistrés : 3
```

```python
# Trouver les emprunts non rendus
active_loans = loans.select(where=loans.returned == False)
print("\nEmprunts actifs :")
for loan in active_loans:
    # Trouver le livre et l'adhérent correspondants
    book = books.select(where=books.isbn == loan["book_isbn"])[0]
    member = members.select(
        where=members.member_id == loan["member_id"]
    )[0]

    print(f"  - '{book['title']}' emprunté par {member['first_name']} {member['last_name']}")
    print(f"    À rendre pour le {loan['due_date']}")
```

```
Emprunts actifs :
  - 'Madame Bovary' emprunté par Julie Moreau
    À rendre pour le 2024-06-15
  - 'L'Étranger' emprunté par Emma Roux
    À rendre pour le 2024-06-24
```

## Chapitre 9 : Sauvegarder la bibliothèque

À la fin de la journée, Mme Dupont sauvegardait sa base de données :

```python
# Sauvegarder toute la bibliothèque
db.save("library.json", file_format="json")
print("Bibliothèque sauvegardée avec succès !")
```

Le lendemain, elle pouvait reprendre son travail :

```python
# Recharger la bibliothèque
db = DictDB.load("library.json", file_format="json")

books = db.get_table("books")
members = db.get_table("members")
loans = db.get_table("loans")

print(f"Bibliothèque chargée :")
print(f"  - {books.count()} livres")
print(f"  - {members.count()} adhérents")
print(f"  - {loans.count()} emprunts")
```

```
Bibliothèque chargée :
  - 7 livres
  - 4 adhérents
  - 3 emprunts
```

## Épilogue : Une bibliothèque numérique

Mme Dupont était ravie. Sa petite bibliothèque de quartier avait fait un bond dans le XXIe siècle. Voici le script de gestion complet :

```python
from dictdb import DictDB, Condition

class Library:
    def __init__(self, filename="library.json"):
        self.filename = filename
        try:
            self.db = DictDB.load(filename, file_format="json")
        except FileNotFoundError:
            self.db = DictDB()
            self.db.create_table("books", primary_key="isbn")
            self.db.create_table("members", primary_key="member_id")
            self.db.create_table("loans")

        self.books = self.db.get_table("books")
        self.members = self.db.get_table("members")
        self.loans = self.db.get_table("loans")

    def add_book(self, isbn, title, author, genre, year):
        self.books.insert({
            "isbn": isbn,
            "title": title,
            "author": author,
            "genre": genre,
            "year": year,
            "available": True
        })
        self.save()

    def register_member(self, member_id, last_name, first_name, email, date):
        self.members.insert({
            "member_id": member_id,
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "registration_date": date
        })
        self.save()

    def borrow_book(self, member_id, book_isbn, loan_date, due_date):
        # Vérifier si le livre est disponible
        book = self.books.select(where=self.books.isbn == book_isbn)[0]
        if not book["available"]:
            raise ValueError("Ce livre n'est pas disponible")

        # Enregistrer l'emprunt
        self.loans.insert({
            "member_id": member_id,
            "book_isbn": book_isbn,
            "loan_date": loan_date,
            "due_date": due_date,
            "returned": False
        })

        # Marquer le livre comme indisponible
        self.books.update(
            {"available": False},
            where=self.books.isbn == book_isbn
        )
        self.save()

    def return_book(self, member_id, book_isbn):
        # Marquer l'emprunt comme rendu
        self.loans.update(
            {"returned": True},
            where=(self.loans.member_id == member_id)
                  & (self.loans.book_isbn == book_isbn)
                  & (self.loans.returned == False)
        )

        # Marquer le livre comme de nouveau disponible
        self.books.update(
            {"available": True},
            where=self.books.isbn == book_isbn
        )
        self.save()

    def search_books(self, term):
        """Recherche dans les titres et auteurs"""
        by_title = self.books.select(
            where=self.books.title.icontains(term)
        )
        by_author = self.books.select(
            where=self.books.author.icontains(term)
        )

        # Combiner les résultats (en évitant les doublons)
        results = {b["isbn"]: b for b in by_title}
        results.update({b["isbn"]: b for b in by_author})
        return list(results.values())

    def available_books(self, page=1, per_page=10):
        """Liste paginée des livres disponibles"""
        offset = (page - 1) * per_page
        return self.books.select(
            where=self.books.available == True,
            order_by="title",
            limit=per_page,
            offset=offset
        )

    def overdue_loans(self, current_date):
        """Trouver les emprunts en retard"""
        return self.loans.select(
            where=(self.loans.returned == False)
                  & (self.loans.due_date < current_date)
        )

    def save(self):
        self.db.save(self.filename, file_format="json")


# Exemple d'utilisation
if __name__ == "__main__":
    lib = Library()

    # Afficher les livres disponibles
    print("=== Livres disponibles ===")
    for book in lib.available_books():
        print(f"  - {book['author']})")
```

## Ce que nous avons appris

Dans ce tutoriel, nous avons exploré les fonctionnalités intermédiaires de DictDB :

| Concept | Code |
|---------|------|
| Clé primaire personnalisée | `db.create_table("t", primary_key="isbn")` |
| Égalité | `table.field == value` |
| Inégalité | `table.field != value` |
| Inférieur / Supérieur | `table.field < value`, `table.field >= value` |
| Commence par | `table.field.startswith("...")` |
| Termine par | `table.field.endswith("...")` |
| Contient | `table.field.contains("...")` |
| Tri croissant | `order_by="field"` |
| Tri décroissant | `order_by="-field"` |
| Pagination | `limit=N, offset=M` |
| Valeurs uniques | `distinct=True` |
| Projection de colonnes | `columns=["col1", "col2"]` |

## Aller plus loin

Mme Dupont était prête à explorer des fonctionnalités plus avancées :

- [Index](../guides/indexes.md) - Accélérer les recherches sur de grands catalogues
- [Schémas](../guides/schemas.md) - Valider les données à l'insertion
- [Sauvegardes automatiques](../guides/backups.md) - Ne plus jamais perdre de données
- [Concurrence](../guides/concurrency.md) - Gérer plusieurs utilisateurs simultanément

[&larr; Retour à Mon premier carnet de contacts](01-contact-book.md)