# Quickstart

```python
from dictdb import DictDB, Condition, configure_logging

# Optional logging
configure_logging(level="DEBUG", console=True)

# Create DB and tables
db = DictDB()
db.create_table("employees", primary_key="emp_id")
employees = db.get_table("employees")

# Insert data
employees.insert({"emp_id": 101, "name": "Alice", "department": "IT"})
employees.insert({"emp_id": 102, "name": "Bob", "department": "HR"})
employees.insert({"name": "Charlie", "department": "IT"})  # auto-assigns emp_id

# Query data
it_staff = employees.select(where=Condition(employees.department == "IT"))
print("IT Department Staff:", it_staff)
```

## Basic Usage

### Creating a Database and Tables

```python
from dictdb import DictDB

db = DictDB()
db.create_table("users")
db.create_table("products", primary_key="product_id")
print(db.list_tables())
```

### Inserting Records

```python
users = db.get_table("users")
users.insert({"id": 1, "name": "Alice", "age": 30})
users.insert({"name": "Bob", "age": 25}) # auto id

products = db.get_table("products")
products.insert({"product_id": 1001, "name": "Laptop", "price": 999.99})
```

### Selecting / Updating / Deleting

```python
from dictdb import Condition

all_users = users.select()
rows_updated = users.update({"age": 26}, where=Condition(users.name == "Bob"))
deleted = users.delete(where=Condition(users.name == "Alice"))
```

