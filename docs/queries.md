# Conditions

DictDB lets you build filter conditions using overloaded operators.

## Simple Field Comparisons

```python
from dictdb import Condition
users = db.get_table("users")

condition = Condition(users.age == 30)
matching_users = users.select(where=condition)
```

## Logical Combinations

```python
# (name == "Alice") AND (age > 25)
condition = Condition((users.name == "Alice") & (users.age > 25))
result = users.select(where=condition)

# (name == "Alice") OR (age > 25)
condition_or = Condition((users.name == "Alice") | (users.age > 25))

# NOT (name == "Alice")
condition_not = Condition(~(users.name == "Alice"))
```
