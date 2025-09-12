# Indexing

Improve query performance by creating indices on table fields. DictDB supports "hash" and "sorted" index types.

```python
users.create_index("age", index_type="hash")
# or
users.create_index("age", index_type="sorted")
```

Equality lookups on indexed fields are accelerated internally.

