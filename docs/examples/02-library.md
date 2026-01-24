# The Neighborhood Library

## Prologue: A Growing Challenge

Mrs. Parker had been a librarian for twenty years. Her small neighborhood library had grown: thousands of books, hundreds of members, and a card catalog system that was starting to show its limits.

Her nephew, a Python developer, proposed a solution: "Aunt Helen, let me show you DictDB. It's simple, lightweight, and perfect for your library."

## Chapter 1: Designing the Structure

The nephew began by thinking about the data to manage:

- **Books**: title, author, genre, publication year, availability
- **Members**: name, registration date, email
- **Loans**: who borrowed what, and when

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

## Chapter 2: Stocking the Shelves

Mrs. Parker began cataloging her books:

```python
books = db.get_table("books")

# Add books to the catalog
books.insert({
    "isbn": "978-0-14-028329-7",
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Fiction",
    "year": 1925,
    "available": True
})

books.insert({
    "isbn": "978-0-06-112008-4",
    "title": "To Kill a Mockingbird",
    "author": "Harper Lee",
    "genre": "Fiction",
    "year": 1960,
    "available": True
})

books.insert({
    "isbn": "978-0-452-28423-4",
    "title": "1984",
    "author": "George Orwell",
    "genre": "Dystopian",
    "year": 1949,
    "available": True
})

books.insert({
    "isbn": "978-0-7432-7356-5",
    "title": "Pride and Prejudice",
    "author": "Jane Austen",
    "genre": "Romance",
    "year": 1813,
    "available": False  # Already borrowed
})

books.insert({
    "isbn": "978-0-14-028334-1",
    "title": "Animal Farm",
    "author": "George Orwell",
    "genre": "Dystopian",
    "year": 1945,
    "available": True
})

books.insert({
    "isbn": "978-0-14-118776-1",
    "title": "Crime and Punishment",
    "author": "Fyodor Dostoevsky",
    "genre": "Fiction",
    "year": 1866,
    "available": True
})

books.insert({
    "isbn": "978-0-06-093546-7",
    "title": "To Kill a Kingdom",
    "author": "Alexandra Christo",
    "genre": "Fantasy",
    "year": 2018,
    "available": True
})

print(f"Catalog: {books.count()} books")
```

```
Catalog: 7 books
```

## Chapter 3: Registering Members

The library welcomed its first members:

```python
members = db.get_table("members")

members.insert({
    "member_id": "MEM001",
    "last_name": "Thompson",
    "first_name": "Julia",
    "email": "julia.thompson@email.com",
    "registration_date": "2024-01-15"
})

members.insert({
    "member_id": "MEM002",
    "last_name": "Mitchell",
    "first_name": "Thomas",
    "email": "t.mitchell@email.com",
    "registration_date": "2024-02-20"
})

members.insert({
    "member_id": "MEM003",
    "last_name": "Roberts",
    "first_name": "Emma",
    "email": "emma.roberts@email.com",
    "registration_date": "2024-03-10"
})

members.insert({
    "member_id": "MEM004",
    "last_name": "Morgan",
    "first_name": "Lucas",
    "email": "lucas.morgan@email.com",
    "registration_date": "2023-11-05"
})

print(f"Registered members: {members.count()}")
```

```
Registered members: 4
```

## Chapter 4: Comparison Operators

Mrs. Parker wanted to find her books easily. Her nephew showed her the power of queries:

### Equality and Inequality

```python
# Find books by George Orwell
orwell_books = books.select(where=books.author == "George Orwell")
print("Books by George Orwell:")
for book in orwell_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Books by George Orwell:
  - 1984 (1949)
  - Animal Farm (1945)
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
  - 1984 (Dystopian)
  - Pride and Prejudice (Romance)
  - Animal Farm (Dystopian)
  - To Kill a Kingdom (Fantasy)
```

### Numeric Comparisons

```python
# Books published in the 20th century or later
modern_books = books.select(where=books.year >= 1900)
print("Books from the 20th century onward:")
for book in modern_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Books from the 20th century onward:
  - The Great Gatsby (1925)
  - To Kill a Mockingbird (1960)
  - 1984 (1949)
  - Animal Farm (1945)
  - To Kill a Kingdom (2018)
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
  - Pride and Prejudice (1813)
  - Crime and Punishment (1866)
```

```python
# Books published in exactly 1949
books_1949 = books.select(where=books.year == 1949)
print("\nBooks published in 1949:")
for book in books_1949:
    print(f"  - {book['title']} by {book['author']}")
```

```
Books published in 1949:
  - 1984 by George Orwell
```

## Chapter 5: The Magic of String Methods

Members did not always remember the exact title. The nephew demonstrated text search methods:

### Search by Beginning (startswith)

```python
# Titles starting with "To"
titles_to = books.select(where=books.title.startswith("To"))
print("Titles starting with 'To':")
for book in titles_to:
    print(f"  - {book['title']}")
```

```
Titles starting with 'To':
  - To Kill a Mockingbird
  - To Kill a Kingdom
```

### Search by Ending (endswith)

```python
# Emails ending with '@email.com'
emails_com = members.select(where=members.email.endswith("@email.com"))
print("\nMembers with @email.com addresses:")
for member in emails_com:
    print(f"  - {member['first_name']} {member['last_name']}")
```

```
Members with @email.com addresses:
  - Julia Thompson
  - Thomas Mitchell
  - Emma Roberts
  - Lucas Morgan
```

### Search by Content (contains)

```python
# Authors containing "Orwell"
authors_orwell = books.select(where=books.author.contains("Orwell"))
print("\nAuthors whose name contains 'Orwell':")
for book in authors_orwell:
    print(f"  - {book['author']} ({book['title']})")
```

```
Authors whose name contains 'Orwell':
  - George Orwell (1984)
  - George Orwell (Animal Farm)
```

!!! tip "Case-insensitive search"
    Use `istartswith()`, `iendswith()`, and `icontains()` for searches that ignore uppercase and lowercase.

## Chapter 6: Sorting and Pagination

The library was growing. Display organization became essential:

### Simple Sorting

```python
# Books sorted by title (alphabetical order)
sorted_books = books.select(order_by="title")
print("Books in alphabetical order:")
for book in sorted_books:
    print(f"  - {book['title']}")
```

```
Books in alphabetical order:
  - 1984
  - Animal Farm
  - Crime and Punishment
  - Pride and Prejudice
  - The Great Gatsby
  - To Kill a Kingdom
  - To Kill a Mockingbird
```

### Descending Sort

```python
# Books from newest to oldest
recent_books = books.select(order_by="-year")
print("\nBooks from newest to oldest:")
for book in recent_books:
    print(f"  - {book['title']} ({book['year']})")
```

```
Books from newest to oldest:
  - To Kill a Kingdom (2018)
  - To Kill a Mockingbird (1960)
  - 1984 (1949)
  - Animal Farm (1945)
  - The Great Gatsby (1925)
  - Crime and Punishment (1866)
  - Pride and Prejudice (1813)
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
  - 1984
  - Animal Farm
  - Crime and Punishment

=== Page 2 ===
  - Pride and Prejudice
  - The Great Gatsby
  - To Kill a Kingdom

=== Page 3 ===
  - To Kill a Mockingbird
```

!!! warning "Always sort before paginating"
    Without `order_by`, the order of results is not guaranteed. Always specify a sort when paginating for consistent results.

## Chapter 7: Distinct Results

Mrs. Parker wanted to know the available genres:

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
  - Dystopian
  - Romance
  - Fantasy
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
  - 1813
  - 1866
  - 1925
  - 1945
  - 1949
  - 1960
  - 2018
```

## Chapter 8: Managing Loans

The real life of a library revolves around loans. The nephew created a complete system:

```python
loans = db.get_table("loans")

# Record some loans
loans.insert({
    "member_id": "MEM001",
    "book_isbn": "978-0-7432-7356-5",  # Pride and Prejudice
    "loan_date": "2024-06-01",
    "due_date": "2024-06-15",
    "returned": False
})

loans.insert({
    "member_id": "MEM002",
    "book_isbn": "978-0-14-028329-7",  # The Great Gatsby
    "loan_date": "2024-06-05",
    "due_date": "2024-06-19",
    "returned": True
})

loans.insert({
    "member_id": "MEM003",
    "book_isbn": "978-0-06-112008-4",  # To Kill a Mockingbird
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
  - 'Pride and Prejudice' borrowed by Julia Thompson
    Due by 2024-06-15
  - 'To Kill a Mockingbird' borrowed by Emma Roberts
    Due by 2024-06-24
```

## Chapter 9: Saving the Library

At the end of the day, Mrs. Parker saved her database:

```python
# Save the entire library
db.save("library.json", file_format="json")
print("Library saved successfully!")
```

The next day, she could resume her work:

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

## Epilogue: A Digital Library

Mrs. Parker was delighted. Her small neighborhood library had leaped into the 21st century. Here is the complete management script:

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

## What We Learned

In this tutorial, we explored the intermediate features of DictDB:

| Concept | Code |
|---------|------|
| Custom primary key | `db.create_table("t", primary_key="isbn")` |
| Equality | `table.field == value` |
| Inequality | `table.field != value` |
| Less than / Greater than | `table.field < value`, `table.field >= value` |
| Starts with | `table.field.startswith("...")` |
| Ends with | `table.field.endswith("...")` |
| Contains | `table.field.contains("...")` |
| Ascending sort | `order_by="field"` |
| Descending sort | `order_by="-field"` |
| Pagination | `limit=N, offset=M` |
| Unique values | `distinct=True` |
| Column projection | `columns=["col1", "col2"]` |

## Going Further

Mrs. Parker was ready to explore more advanced features:

- [Indexes](../guides/indexes.md) - Speed up searches on large catalogs
- [Schemas](../guides/schemas.md) - Validate data on insertion
- [Automatic Backups](../guides/backups.md) - Never lose data again
- [Concurrency](../guides/concurrency.md) - Handle multiple users simultaneously

[&larr; Back to My First Contact Book](01-contact-book.md)
