# Conditions and Queries

DictDB lets you build filter conditions using overloaded operators.

## Simple Field Comparisons

```python
from dictdb import Query
users = db.get_table("users")

condition = Query(users.age == 30)
matching_users = users.select(where=condition)
```

## Logical Combinations

```python
# (name == "Alice") AND (age > 25)
condition = Query((users.name == "Alice") & (users.age > 25))
result = users.select(where=condition)

# (name == "Alice") OR (age > 25)
condition_or = Query((users.name == "Alice") | (users.age > 25))

# NOT (name == "Alice")
condition_not = Query(~(users.name == "Alice"))
```

