# La bibliotheque de quartier

## Prologue : Un defi grandissant

Mme Dupont etait bibliothecaire depuis vingt ans. Sa petite bibliotheque de quartier avait grandi : des milliers de livres, des centaines d'adherents, et un systeme de fiches qui commencait a montrer ses limites.

Son neveu, developpeur Python, proposa une solution : « Tante Helene, laisse-moi te montrer DictDB. C'est simple, leger, et parfait pour ta bibliotheque. »

## Chapitre 1 : Concevoir la structure

Le neveu commenca par reflechir aux donnees a gerer :

- **Livres** : titre, auteur, genre, annee de publication, disponibilite
- **Adherents** : nom, date d'inscription, email
- **Emprunts** : qui a emprunte quoi, et quand

```python
from dictdb import DictDB

# Create the library database
db = DictDB()

# Books table with ISBN as primary key
db.create_table("books", primary_key="isbn")

# Members table with member number as key
db.create_table("members", primary_key="member_id")

# Loans table
db.create_table("loans")

print("Library structure created!")
print(f"Tables: {db.list_tables()}")
```

```
Library structure created!
Tables: ['books', 'members', 'loans']
```

## Chapitre 2 : Remplir les etageres

Mme Dupont commenca a cataloguer ses livres :

```python
books = db.get_table("books")

# Add books to the catalog
books.insert({
    "isbn": "978-2-07-036024-8",
    "title": "Le Petit Prince",
    "author": "Antoine de Saint-Exupery",
    "genre": "Fiction",
    "year": 1943,
    "available": True
})

books.insert({
    "isbn": "978-2-07-040850-4",
    "title": "L'Etranger",
    "author": "Albert Camus",
    "genre": "Fiction",
    "year": 1942,
    "available": True
})

books.insert({
    "isbn": "978-2-07-036822-0",
    "title": "Les Miserables",
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
    "available": False  # Already borrowed
})

books.insert({
    "isbn": "978-2-07-036842-8",
    "title": "Germinal",
    "author": "Emile Zola",
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

print(f"Catalog: {books.count()} books")
```

```
Catalog: 7 books
```

## Chapitre 3 : Inscrire les adherents

La bibliotheque accueillit ses premiers adherents :

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

print(f"Registered members: {members.count()}")
```

```
Registered members: 4
```

## Chapitre 4 : Les operateurs de comparaison

Mme Dupont voulait retrouver ses livres facilement. Son neveu lui montra la puissance des requetes :

### Egalite et inegalite

```python
# Find books by Victor Hugo
hugo_books = books.select(where=books.author == "Victor Hugo")
print("Books by Victor Hugo:")
for book in hugo_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Books by Victor Hugo:
  - Les Miserables (1862)
```

```python
# All books except Fiction
non_fiction = books.select(where=books.genre != "Fiction")
print("\nBooks that are not Fiction:")
for book in non_fiction:
    print(f"  - {book['title']} ({book['genre']})")
```

```
Books that are not Fiction:
  - Les Miserables (Classique)
  - Madame Bovary (Classique)
  - Germinal (Naturalisme)
  - Le Rouge et le Noir (Classique)
  - Vingt mille lieues sous les mers (Aventure)
```

### Comparaisons numeriques

```python
# Books published in the 20th century or later
modern_books = books.select(where=books.year >= 1900)
print("Books from the 20th century onward:")
for book in modern_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Books from the 20th century onward:
  - Le Petit Prince (1943)
  - L'Etranger (1942)
```

```python
# Books published before 1900
old_books = books.select(where=books.year < 1900)
print("\nBooks from the 19th century and earlier:")
for book in old_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Books from the 19th century and earlier:
  - Les Miserables (1862)
  - Madame Bovary (1857)
  - Germinal (1885)
  - Le Rouge et le Noir (1830)
  - Vingt mille lieues sous les mers (1870)
```

```python
# Books published in exactly 1862
books_1862 = books.select(where=books.year == 1862)
print("\nBooks published in 1862:")
for book in books_1862:
    print(f"  - {book['title']} by {book['author']}")
```

```
Books published in 1862:
  - Les Miserables by Victor Hugo
```

## Chapitre 5 : La magie des methodes de chaines

Les adherents ne se souvenaient pas toujours du titre exact. Le neveu presenta les methodes de recherche textuelle :

### Recherche par debut (startswith)

```python
# Titles starting with "Le"
titles_le = books.select(where=books.title.startswith("Le"))
print("Titles starting with 'Le':")
for book in titles_le:
    print(f"  - {book['title']}")
```

```
Titles starting with 'Le':
  - Le Petit Prince
  - Le Rouge et le Noir
```

### Recherche par fin (endswith)

```python
# Emails ending with '@email.com'
emails_com = members.select(where=members.email.endswith("@email.com"))
print("\nMembers with @email.com addresses:")
for member in emails_com:
    print(f"  - {member['first_name']} {member['last_name']}")
```

```
Members with @email.com addresses:
  - Julie Moreau
  - Thomas Petit
  - Emma Roux
  - Lucas Garcia
```

### Recherche par contenu (contains)

```python
# Authors containing "Zola"
authors_zola = books.select(where=books.author.contains("Zola"))
print("\nAuthors whose name contains 'Zola':")
for book in authors_zola:
    print(f"  - {book['author']} ({book['title']})")
```

```
Authors whose name contains 'Zola':
  - Emile Zola (Germinal)
```

!!! tip "Recherche insensible a la casse"
    Utilisez `istartswith()`, `iendswith()` et `icontains()` pour des recherches qui ignorent les majuscules et minuscules.

## Chapitre 6 : Tri et pagination

La bibliotheque grandissait. L'organisation de l'affichage devint essentielle :

### Tri simple

```python
# Books sorted by title (alphabetical order)
sorted_books = books.select(order_by="title")
print("Books in alphabetical order:")
for book in sorted_books:
    print(f"  - {book['title']}")
```

```
Books in alphabetical order:
  - Germinal
  - L'Etranger
  - Le Petit Prince
  - Le Rouge et le Noir
  - Les Miserables
  - Madame Bovary
  - Vingt mille lieues sous les mers
```

### Tri decroissant

```python
# Books from newest to oldest
recent_books = books.select(order_by="-year")
print("\nBooks from newest to oldest:")
for book in recent_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Books from newest to oldest:
  - Le Petit Prince (1943)
  - L'Etranger (1942)
  - Germinal (1885)
  - Vingt mille lieues sous les mers (1870)
  - Les Miserables (1862)
  - Madame Bovary (1857)
  - Le Rouge et le Noir (1830)
```

### Pagination

```python
# Display books in pages of 3
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
  - L'Etranger
  - Le Petit Prince

=== Page 2 ===
  - Le Rouge et le Noir
  - Les Miserables
  - Madame Bovary

=== Page 3 ===
  - Vingt mille lieues sous les mers
```

!!! warning "Toujours trier avant de paginer"
    Sans `order_by`, l'ordre des resultats n'est pas garanti. Specifiez toujours un tri lors de la pagination pour des resultats coherents.

## Chapitre 7 : Resultats distincts

Mme Dupont voulait connaitre les genres disponibles :

```python
# Get the list of genres (without duplicates)
genres = books.select(columns=["genre"], distinct=True)
print("Genres available in the library:")
for g in genres:
    print(f"  - {g['genre']}")
```

```
Genres available in the library:
  - Fiction
  - Classique
  - Naturalisme
  - Aventure
```

```python
# Unique publication years, sorted
years = books.select(
    columns=["year"],
    distinct=True,
    order_by="year"
)
print("\nPublication years:")
for y in years:
    print(f"  - {y['year']}")
```

```
Publication years:
  - 1830
  - 1857
  - 1862
  - 1870
  - 1885
  - 1942
  - 1943
```

## Chapitre 8 : Gerer les emprunts

La vraie vie d'une bibliotheque tourne autour des emprunts. Le neveu crea un systeme complet :

```python
loans = db.get_table("loans")

# Record some loans
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
    "book_isbn": "978-2-07-040850-4",  # L'Etranger
    "loan_date": "2024-06-10",
    "due_date": "2024-06-24",
    "returned": False
})

print(f"Loans recorded: {loans.count()}")
```

```
Loans recorded: 3
```

```python
# Find unreturned loans
active_loans = loans.select(where=loans.returned == False)
print("\nActive loans:")
for loan in active_loans:
    # Find the corresponding book and member
    book = books.select(where=books.isbn == loan["book_isbn"])[0]
    member = members.select(
        where=members.member_id == loan["member_id"]
    )[0]

    print(f"  - '{book['title']}' borrowed by {member['first_name']} {member['last_name']}")
    print(f"    Due by {loan['due_date']}")
```

```
Active loans:
  - 'Madame Bovary' borrowed by Julie Moreau
    Due by 2024-06-15
  - 'L'Etranger' borrowed by Emma Roux
    Due by 2024-06-24
```

## Chapitre 9 : Sauvegarder la bibliotheque

A la fin de la journee, Mme Dupont sauvegardera sa base de donnees :

```python
# Save the entire library
db.save("library.json", file_format="json")
print("Library saved successfully!")
```

Le lendemain, elle pourra reprendre son travail :

```python
# Reload the library
db = DictDB.load("library.json", file_format="json")

books = db.get_table("books")
members = db.get_table("members")
loans = db.get_table("loans")

print(f"Library loaded:")
print(f"  - {books.count()} books")
print(f"  - {members.count()} members")
print(f"  - {loans.count()} loans")
```

```
Library loaded:
  - 7 books
  - 4 members
  - 3 loans
```

## Epilogue : Une bibliotheque numerique

Mme Dupont etait ravie. Sa petite bibliotheque de quartier avait fait un bond dans le XXIe siecle. Voici le script de gestion complet :

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
        # Check if the book is available
        book = self.books.select(where=self.books.isbn == book_isbn)[0]
        if not book["available"]:
            raise ValueError("This book is not available")

        # Record the loan
        self.loans.insert({
            "member_id": member_id,
            "book_isbn": book_isbn,
            "loan_date": loan_date,
            "due_date": due_date,
            "returned": False
        })

        # Mark the book as unavailable
        self.books.update(
            {"available": False},
            where=self.books.isbn == book_isbn
        )
        self.save()

    def return_book(self, member_id, book_isbn):
        # Mark the loan as returned
        self.loans.update(
            {"returned": True},
            where=(self.loans.member_id == member_id)
                  & (self.loans.book_isbn == book_isbn)
                  & (self.loans.returned == False)
        )

        # Mark the book as available again
        self.books.update(
            {"available": True},
            where=self.books.isbn == book_isbn
        )
        self.save()

    def search_books(self, term):
        """Search in titles and authors"""
        by_title = self.books.select(
            where=self.books.title.icontains(term)
        )
        by_author = self.books.select(
            where=self.books.author.icontains(term)
        )

        # Combine results (avoiding duplicates)
        results = {b["isbn"]: b for b in by_title}
        results.update({b["isbn"]: b for b in by_author})
        return list(results.values())

    def available_books(self, page=1, per_page=10):
        """Paginated list of available books"""
        offset = (page - 1) * per_page
        return self.books.select(
            where=self.books.available == True,
            order_by="title",
            limit=per_page,
            offset=offset
        )

    def overdue_loans(self, current_date):
        """Find overdue loans"""
        return self.loans.select(
            where=(self.loans.returned == False)
                  & (self.loans.due_date < current_date)
        )

    def save(self):
        self.db.save(self.filename, file_format="json")


# Example usage
if __name__ == "__main__":
    lib = Library()

    # Display available books
    print("=== Available Books ===")
    for book in lib.available_books():
        print(f"  - {book['title']} ({book['author']})")
```

## Ce que nous avons appris

Dans ce tutoriel, nous avons explore les fonctionnalites intermediaires de DictDB :

| Concept | Code |
|---------|------|
| Cle primaire personnalisee | `db.create_table("t", primary_key="isbn")` |
| Egalite | `table.field == value` |
| Inegalite | `table.field != value` |
| Inferieur / Superieur | `table.field < value`, `table.field >= value` |
| Commence par | `table.field.startswith("...")` |
| Termine par | `table.field.endswith("...")` |
| Contient | `table.field.contains("...")` |
| Tri croissant | `order_by="field"` |
| Tri decroissant | `order_by="-field"` |
| Pagination | `limit=N, offset=M` |
| Valeurs uniques | `distinct=True` |
| Projection de colonnes | `columns=["col1", "col2"]` |

## Aller plus loin

Mme Dupont etait prete a explorer des fonctionnalites plus avancees :

- [Index](../guides/indexes.md) - Accelerer les recherches sur de grands catalogues
- [Schemas](../guides/schemas.md) - Valider les donnees a l'insertion
- [Sauvegardes automatiques](../guides/backups.md) - Ne plus jamais perdre de donnees
- [Concurrence](../guides/concurrency.md) - Gerer plusieurs utilisateurs simultanement

[&larr; Retour a Mon premier carnet de contacts](01-contact-book.md)
