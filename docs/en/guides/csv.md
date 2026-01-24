# CSV Import/Export

DictDB supports importing data from CSV files and exporting query results to CSV.

## Importing CSV Files

Use `DictDB.import_csv()` to create a new table from a CSV file:

```python
from dictdb import DictDB

db = DictDB()

# Basic import
db.import_csv("users.csv", "users", primary_key="id")

# Access the imported data
users = db.get_table("users")
print(users.count())  # Number of records imported
```

### Import Options

```python
db.import_csv(
    "data.csv",
    "products",
    primary_key="id",
    delimiter=";",           # Custom delimiter (default: ",")
    has_header=True,         # First row is header (default: True)
    encoding="utf-8",        # File encoding (default: "utf-8")
    schema={"id": int, "price": float, "name": str},  # Type conversion
    infer_types=True,        # Auto-detect types (default: True)
    skip_validation=False,   # Skip schema validation (default: False)
)
```

### Type Inference

By default, DictDB automatically infers column types:

- Integer values (`"42"`) become `int`
- Decimal values (`"3.14"`) become `float`
- Everything else remains `str`

```python
# CSV content: id,price,name
#              1,19.99,Widget

db.import_csv("products.csv", "products")
products = db.get_table("products")
rec = products.select()[0]

print(type(rec["id"]))     # <class 'int'>
print(type(rec["price"]))  # <class 'float'>
print(type(rec["name"]))   # <class 'str'>
```

### Explicit Schema

For precise control, provide an explicit schema:

```python
schema = {
    "id": int,
    "price": float,
    "name": str,
    "active": bool,  # Parses "true"/"false", "1"/"0", "yes"/"no"
}

db.import_csv("products.csv", "products", schema=schema)
```

## Exporting to CSV

Use `Table.export_csv()` to write records to a CSV file:

```python
from dictdb import DictDB

db = DictDB()
db.create_table("users")
users = db.get_table("users")

users.insert({"id": 1, "name": "Alice", "email": "alice@example.com"})
users.insert({"id": 2, "name": "Bob", "email": "bob@example.com"})

# Export all records
users.export_csv("users_backup.csv")
```

### Export with Filtering

```python
# Export only active users
users.export_csv("active_users.csv", where=users.status == "active")

# Export using And/Or/Not
from dictdb import And

users.export_csv(
    "it_seniors.csv",
    where=And(users.department == "IT", users.years >= 5)
)
```

### Export Specific Columns

```python
# Only export name and email columns
users.export_csv("contacts.csv", columns=["name", "email"])
```

### Export Pre-computed Results

```python
# First compute results, then export
results = users.select(
    columns=["name", "email"],
    where=users.age >= 18,
    order_by="name"
)

users.export_csv("adults.csv", records=results)
```

### Export Options

```python
users.export_csv(
    "export.csv",
    columns=["id", "name", "email"],  # Column selection and order
    where=users.active == True,       # Filter condition
    delimiter=";",                     # Custom delimiter
    encoding="utf-8",                  # File encoding
)
```

## Roundtrip Example

```python
from dictdb import DictDB

# Import from CSV
db = DictDB()
db.import_csv("original.csv", "data", primary_key="id")

# Modify data
data = db.get_table("data")
data.update({"status": "processed"}, where=data.status == "pending")

# Export back to CSV
data.export_csv("processed.csv")
```

## Handling Special Characters

CSV files with commas, quotes, or newlines in field values are handled automatically:

```python
# This works correctly
users.insert({"id": 1, "name": "O'Brien, Jr.", "bio": 'Says "Hello"'})
users.export_csv("users.csv")

# Re-import preserves the values
db2 = DictDB()
db2.import_csv("users.csv", "users2")
```

## Error Handling

```python
from dictdb import DictDB
from dictdb.exceptions import DuplicateTableError

db = DictDB()
db.create_table("users")

try:
    db.import_csv("users.csv", "users")  # Table already exists
except DuplicateTableError as e:
    print(f"Error: {e}")
```
