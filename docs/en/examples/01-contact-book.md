# My First Contact Book

## Prologue: An Unexpected Discovery

It was an ordinary Tuesday morning. Alex, a Python developer for three years now, sipped coffee while staring at the screen. The task seemed simple enough: create a contact book for the team. Nothing fancy required, but pulling out the heavy artillery felt like overkill. No PostgreSQL, no SQLite. Just something light and elegant.

That's when Alex discovered DictDB.

## Chapter 1: First Steps

Alex opened the terminal and installed the package:

```bash
pip install dctdb
```

Then, with a mix of curiosity and excitement, the first lines of code appeared:

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

"That's it?" Alex thought. "Is it really that simple?"

## Chapter 2: Adding Contacts

Alex began filling the contact book with team members:

```python
# Add the first contact
contacts.insert({
    "last_name": "Smith",
    "first_name": "John",
    "email": "john.smith@company.com",
    "phone": "555-123-4567"
})

# Add more contacts
contacts.insert({
    "last_name": "Johnson",
    "first_name": "Sarah",
    "email": "sarah.johnson@company.com",
    "phone": "555-987-6543"
})

contacts.insert({
    "last_name": "Williams",
    "first_name": "Peter",
    "email": "peter.williams@company.com",
    "phone": "555-111-2233"
})

contacts.insert({
    "last_name": "Brown",
    "first_name": "Claire",
    "email": "claire.brown@company.com",
    "phone": "555-556-7788"
})

print(f"Number of contacts: {contacts.count()}")
```

```
Number of contacts: 4
```

Alex noticed that each `insert` returned a unique identifier. DictDB automatically generated an `id` primary key for each record.

## Chapter 3: Finding Contacts

The contact book was filling up, but what good is storing data if you cannot retrieve it?

```python
# Display all contacts
all_contacts = contacts.select()

print("=== All My Contacts ===")
for contact in all_contacts:
    print(f"{contact['first_name']} {contact['last_name']} - {contact['email']}")
```

```
=== All My Contacts ===
John Smith - john.smith@company.com
Sarah Johnson - sarah.johnson@company.com
Peter Williams - peter.williams@company.com
Claire Brown - claire.brown@company.com
```

Alex wanted to search for a specific contact. The power of the query DSL became apparent:

```python
from dictdb import Condition

# Find Sarah
sarah = contacts.select(where=Condition(contacts.first_name == "Sarah"))
print(f"Contact found: {sarah[0]['first_name']} {sarah[0]['last_name']}")

# Find all contacts whose last name starts with 'W'
contacts_w = contacts.select(where=contacts.last_name.startswith("W"))
print("\nContacts whose last name starts with W:")
for c in contacts_w:
    print(f"  - {c['first_name']} {c['last_name']}")
```

```
Contact found: Sarah Johnson

Contacts whose last name starts with W:
  - Peter Williams
```

!!! tip "Condition is optional"
    You can pass the expression directly to the `where` parameter without wrapping it in `Condition()`. Both syntaxes work!

## Chapter 4: Updating a Contact

One day, Peter Williams changed his phone number. Alex needed to update the contact book:

```python
# Update Peter's phone number
modified_count = contacts.update(
    {"phone": "555-999-8877"},
    where=Condition(contacts.first_name == "Peter")
)

print(f"Number of contacts modified: {modified_count}")

# Verify the modification
peter = contacts.select(where=contacts.first_name == "Peter")[0]
print(f"Peter's new phone number: {peter['phone']}")
```

```
Number of contacts modified: 1
Peter's new phone number: 555-999-8877
```

## Chapter 5: Deleting a Contact

Unfortunately, John Smith left the company. Alex needed to remove him from the contact book:

```python
# Remove John from the contact book
deleted_count = contacts.delete(where=Condition(contacts.first_name == "John"))

print(f"Number of contacts deleted: {deleted_count}")
print(f"Remaining contacts: {contacts.count()}")
```

```
Number of contacts deleted: 1
Remaining contacts: 3
```

## Chapter 6: Saving Your Work

Alex realized it would be a shame to lose all this work. DictDB could save the data to a JSON file:

```python
# Save the database
db.save("contact_book.json", file_format="json")

print("Database saved!")
```

The created JSON file was perfectly readable:

```json
{
  "tables": {
    "contacts": {
      "primary_key": "id",
      "schema": null,
      "records": [
        {
          "id": 2,
          "last_name": "Johnson",
          "first_name": "Sarah",
          "email": "sarah.johnson@company.com",
          "phone": "555-987-6543"
        },
        ...
      ]
    }
  }
}
```

## Chapter 7: Picking Up Where You Left Off

The next morning, Alex resumed work. Loading the database was straightforward:

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
  - Sarah Johnson
  - Peter Williams
  - Claire Brown
```

## Epilogue: A Complete Contact Book

Alex was satisfied. In just a few lines of code, a fully functional contact book had emerged. Here is the complete script shared with the team:

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
        "last_name": "Davis",
        "first_name": "Emma",
        "email": "emma.davis@company.com",
        "phone": "555-001-1223"
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

## What We Learned

In this tutorial, we discovered the basics of DictDB:

| Concept | Code |
|---------|------|
| Create a database | `db = DictDB()` |
| Create a table | `db.create_table("name")` |
| Get a table | `table = db.get_table("name")` |
| Insert a record | `table.insert({...})` |
| Select records | `table.select()` |
| Filter with a condition | `table.select(where=table.field == value)` |
| Update records | `table.update({...}, where=...)` |
| Delete records | `table.delete(where=...)` |
| Save to JSON | `db.save("file.json", file_format="json")` |
| Load from JSON | `DictDB.load("file.json", file_format="json")` |

## Next Steps

Alex was ready for new challenges. In the next chapter, discover how to manage multiple related tables, use more advanced queries, and optimize searches.

[Continue to "The Neighborhood Library" &rarr;](02-library.md)
