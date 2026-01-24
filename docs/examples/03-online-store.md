# My Online Store

## Introduction

Sarah had always dreamed of turning her passion for handcrafted goods into a business. After months of preparation, late nights designing her website, and countless trips to local artisan markets, she was finally ready to launch "Sarah's Treasures" - an online boutique specializing in home decor and artisan gifts.

But before she could sell her first product, Sarah faced a challenge that many new entrepreneurs encounter: how do you manage a product catalog that needs to be reliable, searchable, and easy to update? She needed a system that would:

- Ensure every product has complete and correctly typed information
- Find products quickly by category or price range
- Handle complex customer searches
- Make inventory updates seamless

Let's follow Sarah as she builds her product catalog with DictDB.

## Creating the Catalog with Schema Validation

Sarah begins by defining the structure of her products. She wants to make sure that every item has all the required information and that the data types are correct - no more accidentally entering "fifteen dollars" instead of 15.00.

```python
from dictdb import DictDB, Condition, And, Or, Not

# Sarah creates her database
db = DictDB()

# Define the product schema
product_schema = {
    "sku": str,           # Unique product reference
    "name": str,          # Product name
    "description": str,   # Detailed description
    "category": str,      # Product category
    "price": float,       # Price in dollars
    "stock": int,         # Quantity in stock
    "active": bool,       # Available for sale
}

# Create the table with schema validation
db.create_table("products", primary_key="sku", schema=product_schema)
products = db.get_table("products")
```

Now, if Sarah tries to insert an incomplete product or one with incorrect data types, DictDB will catch the error immediately:

```python
from dictdb import SchemaValidationError

# Attempting to insert an incomplete product
try:
    products.insert({
        "sku": "DEC001",
        "name": "Lavender Candle",
        # Missing: description, category, price, stock, and active!
    })
except SchemaValidationError as e:
    print(f"Error: {e}")
    # Error: Missing field 'description' as defined in schema.

# Attempting to insert with incorrect type
try:
    products.insert({
        "sku": "DEC001",
        "name": "Lavender Candle",
        "description": "Handcrafted lavender-scented candle",
        "category": "Decor",
        "price": "fifteen dollars",  # Should be a float!
        "stock": 50,
        "active": True,
    })
except SchemaValidationError as e:
    print(f"Error: {e}")
    # Error: Field 'price' expects type 'float', got 'str'.
```

With schema validation in place, Sarah can add her products with confidence:

```python
# Adding the first products
products.insert({
    "sku": "DEC001",
    "name": "Lavender Scented Candle",
    "description": "Handcrafted candle with Provence lavender",
    "category": "Decor",
    "price": 15.90,
    "stock": 50,
    "active": True,
})

products.insert({
    "sku": "DEC002",
    "name": "Blue Ceramic Vase",
    "description": "Handmade vase with blue glazed ceramic finish",
    "category": "Decor",
    "price": 45.00,
    "stock": 12,
    "active": True,
})

products.insert({
    "sku": "GFT001",
    "name": "Organic Tea Gift Set",
    "description": "Assortment of 5 organic teas in a wooden gift box",
    "category": "Gifts",
    "price": 29.90,
    "stock": 30,
    "active": True,
})

products.insert({
    "sku": "GFT002",
    "name": "Leather Journal",
    "description": "Artisan journal with genuine leather cover",
    "category": "Gifts",
    "price": 35.00,
    "stock": 25,
    "active": True,
})

products.insert({
    "sku": "DEC003",
    "name": "Bohemian Mirror",
    "description": "Round mirror with handmade macrame frame",
    "category": "Decor",
    "price": 89.00,
    "stock": 8,
    "active": True,
})

products.insert({
    "sku": "ART001",
    "name": "Watercolor Painting Kit",
    "description": "Complete kit for beginners to start watercolor painting",
    "category": "Crafts",
    "price": 55.00,
    "stock": 0,
    "active": False,  # Out of stock
})

products.insert({
    "sku": "GFT003",
    "name": "Dried Flower Bouquet",
    "description": "Bouquet composed of natural dried flowers",
    "category": "Gifts",
    "price": 42.50,
    "stock": 15,
    "active": True,
})

products.insert({
    "sku": "DEC004",
    "name": "Emerald Velvet Cushion",
    "description": "Decorative cushion in emerald green velvet",
    "category": "Decor",
    "price": 32.00,
    "stock": 20,
    "active": True,
})

print(f"Catalog created with {products.count()} products!")
# Catalog created with 8 products!
```

## Optimizing Searches with Indexes

As Sarah's store grows, she wants to make sure searches stay fast. She creates indexes on the fields that customers search most often.

```python
# Hash index for category searches (exact equality)
products.create_index("category", index_type="hash")

# Sorted index for price searches (range queries)
products.create_index("price", index_type="sorted")

# Check which fields are indexed
print(f"Indexed fields: {products.indexed_fields()}")
# Indexed fields: ['category', 'price']
```

**Why two types of indexes?**

- **Hash index**: Perfect for equality searches (`category == "Decor"`). Provides constant time O(1) lookups.
- **Sorted index**: Ideal for range searches (`price >= 20` and `price <= 50`). Provides logarithmic time O(log n) lookups.

## Advanced Queries with And, Or, Not

Sarah's customers have varied needs. Let's see how she can respond to their search requests.

### Combining Conditions with And

A customer is looking for decor items under $50:

```python
# Decor products under $50
results = products.select(
    where=And(
        products.category == "Decor",
        products.price < 50,
        products.active == True
    ),
    order_by="price"
)

print("Decor under $50:")
for p in results:
    print(f"  - {p['name']}: ${p['price']}")
# Decor under $50:
#   - Lavender Scented Candle: $15.9
#   - Emerald Velvet Cushion: $32.0
#   - Blue Ceramic Vase: $45.0
```

### Using Or to Broaden the Search

A customer is torn between decor and gifts:

```python
# Products in Decor OR Gifts categories
results = products.select(
    where=And(
        Or(
            products.category == "Decor",
            products.category == "Gifts"
        ),
        products.active == True
    ),
    order_by="category"
)

print(f"Decor and Gifts: {len(results)} products available")
# Decor and Gifts: 7 products available
```

### Excluding with Not

A customer wants everything except decor:

```python
# Everything except decor
results = products.select(
    where=And(
        Not(products.category == "Decor"),
        products.active == True
    )
)

print("Products outside Decor:")
for p in results:
    print(f"  - [{p['category']}] {p['name']}")
# Products outside Decor:
#   - [Gifts] Organic Tea Gift Set
#   - [Gifts] Leather Journal
#   - [Gifts] Dried Flower Bouquet
```

### Complex Nested Conditions

A customer has a budget of $30 to $50 and is looking for a gift OR a premium decor item:

```python
# Complex query
results = products.select(
    where=And(
        products.active == True,
        Or(
            # Gifts between $30 and $50
            And(
                products.category == "Gifts",
                products.price >= 30,
                products.price <= 50
            ),
            # OR premium decor (over $80)
            And(
                products.category == "Decor",
                products.price >= 80
            )
        )
    )
)

print("Gifts $30-50 or Premium Decor:")
for p in results:
    print(f"  - {p['name']} ({p['category']}): ${p['price']}")
# Gifts $30-50 or Premium Decor:
#   - Leather Journal (Gifts): $35.0
#   - Dried Flower Bouquet (Gifts): $42.5
#   - Bohemian Mirror (Decor): $89.0
```

## Price Range Search with BETWEEN

Sarah often needs to filter by price range. The `between()` method simplifies these searches.

```python
# Products between $25 and $45 (inclusive)
results = products.select(
    where=And(
        products.price.between(25, 45),
        products.active == True
    ),
    order_by="price"
)

print("Products between $25 and $45:")
for p in results:
    print(f"  - {p['name']}: ${p['price']}")
# Products between $25 and $45:
#   - Organic Tea Gift Set: $29.9
#   - Emerald Velvet Cushion: $32.0
#   - Leather Journal: $35.0
#   - Dried Flower Bouquet: $42.5
#   - Blue Ceramic Vase: $45.0
```

The `between()` method is equivalent to `(price >= 25) & (price <= 45)`, but more readable and optimized when using a sorted index.

## Text Search with LIKE

Customers often use the search bar. Sarah implements pattern-based searching.

```python
# Search for products starting with "Leather" or "Lavender"
results = products.select(
    where=products.name.like("La%")
)

print("Products starting with 'La':")
for p in results:
    print(f"  - {p['name']}")
# Products starting with 'La':
#   - Lavender Scented Candle
```

### Available LIKE Patterns

```python
# % = any sequence of characters
# _ = exactly one character

# Products containing "leather" in the description
results = products.select(
    where=products.description.like("%leather%")
)
print("Leather products:")
for p in results:
    print(f"  - {p['name']}")
# Leather products:
#   - Leather Journal

# Products with "DEC" followed by 3 characters in the SKU
results = products.select(
    where=products.sku.like("DEC___")
)
print(f"DEC products: {len(results)} items")
# DEC products: 4 items
```

## Case-Insensitive Search

Customers don't always pay attention to capitalization. Sarah uses case-insensitive variants to ensure they find what they're looking for.

```python
# Case-insensitive search with icontains
results = products.select(
    where=products.name.icontains("LAVENDER")  # Even typed in uppercase
)
print("Search 'LAVENDER':")
for p in results:
    print(f"  - {p['name']}")
# Search 'LAVENDER':
#   - Lavender Scented Candle

# ilike for case-insensitive patterns
results = products.select(
    where=products.description.ilike("%ORGANIC%")
)
print("Search 'ORGANIC' (case-insensitive):")
for p in results:
    print(f"  - {p['name']}")
# Search 'ORGANIC' (case-insensitive):
#   - Organic Tea Gift Set
```

### All Available Variants

| Case-Sensitive Method | Case-Insensitive Method | Usage |
|----------------------|------------------------|-------|
| `==` (equality) | `iequals()` | Exact match |
| `contains()` | `icontains()` | Contains text |
| `startswith()` | `istartswith()` | Starts with |
| `endswith()` | `iendswith()` | Ends with |
| `like()` | `ilike()` | SQL pattern with % and _ |

```python
# Example with istartswith
results = products.select(
    where=products.name.istartswith("ORGANIC")
)
print("Products starting with 'organic' (case-insensitive):")
for p in results:
    print(f"  - {p['name']}")
# Products starting with 'organic' (case-insensitive):
#   - Organic Tea Gift Set
```

## Inventory Updates with Upsert

Sarah regularly receives shipments. She uses `upsert()` to update her stock: if the product exists, it gets updated; otherwise, it gets created.

```python
# Shipment arrival: updating stock for an existing product
sku, action = products.upsert({
    "sku": "DEC001",
    "name": "Lavender Scented Candle",
    "description": "Handcrafted candle with Provence lavender",
    "category": "Decor",
    "price": 15.90,
    "stock": 75,  # New stock: 50 + 25 = 75
    "active": True,
})
print(f"Product {sku}: {action}")
# Product DEC001: updated

# New product in the shipment
sku, action = products.upsert({
    "sku": "DEC005",
    "name": "Glass Candle Holder",
    "description": "Artisan candle holder in blown glass",
    "category": "Decor",
    "price": 24.90,
    "stock": 30,
    "active": True,
})
print(f"Product {sku}: {action}")
# Product DEC005: inserted
```

### Conflict Strategies

The `upsert()` method accepts an `on_conflict` parameter to handle duplicates:

```python
# on_conflict="update" (default): updates if exists
sku, action = products.upsert(
    {"sku": "DEC001", "name": "Lavender Candle", "description": "...",
     "category": "Decor", "price": 16.90, "stock": 80, "active": True},
    on_conflict="update"
)
print(f"{sku}: {action}")  # DEC001: updated

# on_conflict="ignore": does nothing if exists
sku, action = products.upsert(
    {"sku": "DEC001", "name": "Another Candle", "description": "...",
     "category": "Decor", "price": 99.00, "stock": 1, "active": True},
    on_conflict="ignore"
)
print(f"{sku}: {action}")  # DEC001: ignored

# on_conflict="error": raises an exception if exists
from dictdb import DuplicateKeyError

try:
    products.upsert(
        {"sku": "DEC001", "name": "Test", "description": "...",
         "category": "Decor", "price": 10.00, "stock": 1, "active": True},
        on_conflict="error"
    )
except DuplicateKeyError:
    print("Product already exists!")
# Product already exists!
```

## Summary

In this example, Sarah learned how to:

1. **Validate data with a schema**: Ensure every product has all required fields with correct types
2. **Create indexes**: Use hash indexes for equality searches and sorted indexes for range queries
3. **Combine conditions**: Use `And`, `Or`, and `Not` for complex queries
4. **Filter by range**: Use `between()` for price range searches
5. **Search text**: Use `like()` with `%` and `_` patterns
6. **Ignore case**: Use `icontains()`, `ilike()`, and other case-insensitive variants
7. **Manage inventory**: Use `upsert()` to create or update products

Sarah is now ready to launch her online store with a robust and performant catalog management system!
