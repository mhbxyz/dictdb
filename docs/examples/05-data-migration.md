# Legacy Data Migration

*A tale of digital transformation at TechFlow Inc.*

---

It was a typical Monday morning when Sarah, the lead data engineer at TechFlow Inc., received an urgent email from management. After years of operating with scattered CSV files across multiple departments, the company had finally decided to modernize their data infrastructure. Sarah knew that DictDB would be the perfect solution for this migration challenge.

"We have thousands of records spread across customer files, order histories, and product catalogs," she explained to her team during the kickoff meeting. "Our mission is to import them cleanly, transform them into a consistent format, and ensure that nothing gets lost along the way."

## The Starting Point: Legacy Data

Before diving in, Sarah examined the existing files. Here's what she found:

```csv
# customers_legacy.csv
id;name;email;signup_date;active
1;John Smith;john@example.com;2023-01-15;yes
2;Maria Garcia;maria@example.com;2022-06-20;yes
3;Peter Brown;;2021-03-10;no
4;Sophie Wilson;sophie@example.com;2024-02-28;yes
```

```csv
# orders_legacy.csv
ref,customer_id,amount,status,order_date
ORD001,1,150.50,delivered,2024-01-10
ORD002,2,89.99,processing,2024-01-12
ORD003,1,220.00,cancelled,2024-01-15
ORD004,4,45.00,delivered,2024-01-20
```

## Step One: CSV Import with Type Inference

Sarah started with the simplest approach. DictDB can automatically detect data types from CSV content.

```python
from dictdb import DictDB

# Initialize the database
db = DictDB()

# Import CSV with automatic type inference
# The semicolon is the delimiter used in the legacy files
count = db.import_csv(
    "customers_legacy.csv",
    "customers",
    primary_key="id",
    delimiter=";",
    infer_types=True,  # DictDB automatically detects int, float, str
)

print(f"Customers imported: {count}")

# Verify the inferred types
customers = db.get_table("customers")
first_customer = customers.select(limit=1)[0]

print(f"Type of 'id': {type(first_customer['id'])}")        # <class 'int'>
print(f"Type of 'name': {type(first_customer['name'])}")    # <class 'str'>
print(f"Type of 'active': {type(first_customer['active'])}") # <class 'str'>
```

"Interesting," Sarah noted. "The inference works well for numbers, but the 'active' field remains a string. For better structure, we need to define an explicit schema."

## Step Two: CSV Import with Explicit Schema

For critical data like orders, Sarah preferred precise control over data types.

```python
from dictdb import DictDB, SchemaValidationError

db = DictDB()

# Define the schema for strict control
orders_schema = {
    "ref": str,
    "customer_id": int,
    "amount": float,
    "status": str,
    "order_date": str,
}

# Import with explicit schema
count = db.import_csv(
    "orders_legacy.csv",
    "orders",
    primary_key="ref",
    delimiter=",",
    schema=orders_schema,
    infer_types=False,  # Disable inference, use only the schema
)

print(f"Orders imported: {count}")

# Verify strict typing
orders = db.get_table("orders")
first_order = orders.select(limit=1)[0]

print(f"Reference: {first_order['ref']}")
print(f"Amount (float): {first_order['amount']}")       # 150.5 (float)
print(f"Customer ID (int): {first_order['customer_id']}")  # 1 (int)
```

## Step Three: Data Transformation and Cleaning

"The data is imported, but it's not clean," observed Tom, the junior developer. "Some emails are missing, and the 'active' field should be a boolean."

Sarah smiled. "That's where transformation comes in."

```python
from dictdb import DictDB, RecordNotFoundError

db = DictDB()

# Re-import customers for transformation
db.import_csv(
    "customers_legacy.csv",
    "customers_raw",
    primary_key="id",
    delimiter=";",
)

customers_raw = db.get_table("customers_raw")

# Create a new table with clean schema
db.create_table("customers", primary_key="id")
customers = db.get_table("customers")

# Transform the data
for record in customers_raw.select():
    # Convert "yes"/"no" to boolean
    active_str = record.get("active", "").lower()
    is_active = active_str in ("yes", "true", "1", "oui")

    # Clean email (replace empty with placeholder)
    email = record.get("email", "").strip()
    if not email:
        email = f"unknown_{record['id']}@placeholder.local"

    # Normalize name (proper capitalization)
    name = record.get("name", "").strip().title()

    # Insert the transformed record
    customers.insert({
        "id": record["id"],
        "name": name,
        "email": email,
        "signup_date": record.get("signup_date", ""),
        "active": is_active,
    })

# Verify transformations
print("Customers after transformation:")
for customer in customers.select():
    print(f"  {customer['id']}: {customer['name']} - active={customer['active']} ({type(customer['active']).__name__})")
```

Output:
```
Customers after transformation:
  1: John Smith - active=True (bool)
  2: Maria Garcia - active=True (bool)
  3: Peter Brown - active=False (bool)
  4: Sophie Wilson - active=True (bool)
```

## Step Four: CSV Export with Filtering

"Now that our data is clean, we need to generate reports," Sarah explained. "Let's start by exporting only active customers."

```python
# Export only active customers
customers.export_csv(
    "active_customers.csv",
    where=customers.active == True,
)

print("File active_customers.csv generated successfully")

# Verify the exported content
with open("active_customers.csv", "r") as f:
    print(f.read())
```

Output:
```csv
id,name,email,signup_date,active
1,John Smith,john@example.com,2023-01-15,True
2,Maria Garcia,maria@example.com,2022-06-20,True
4,Sophie Wilson,sophie@example.com,2024-02-28,True
```

## Step Five: CSV Export with Column Selection

"For the marketing department, they only need names and emails," Tom noted.

```python
# Export with selected columns
customers.export_csv(
    "marketing_contacts.csv",
    columns=["name", "email"],  # Only these columns
    where=customers.active == True,
)

# Export for accounting: delivered orders
orders.export_csv(
    "delivered_orders.csv",
    columns=["ref", "customer_id", "amount", "order_date"],
    where=orders.status == "delivered",
)

print("Specific exports generated")
```

## Step Six: Round-Trip Data Validation

"How do we ensure nothing is lost in the process?" Tom asked.

Sarah explained the concept of round-trip validation: export the data then re-import it to verify integrity.

```python
from dictdb import DictDB

def validate_roundtrip(table, temp_file):
    """
    Validates that an export/re-import preserves all data.
    """
    # Capture original data
    originals = table.select()
    original_count = len(originals)

    # Export to CSV
    table.export_csv(temp_file)

    # Create a new database and re-import
    test_db = DictDB()
    test_db.import_csv(
        temp_file,
        "test_reimport",
        primary_key=table.primary_key,
        infer_types=True,
    )

    reimported = test_db.get_table("test_reimport").select()
    reimport_count = len(reimported)

    # Verifications
    errors = []

    if original_count != reimport_count:
        errors.append(f"Record count mismatch: {original_count} vs {reimport_count}")

    # Compare each record
    originals_by_pk = {r[table.primary_key]: r for r in originals}
    reimported_by_pk = {r[table.primary_key]: r for r in reimported}

    for pk, original in originals_by_pk.items():
        if pk not in reimported_by_pk:
            errors.append(f"Record missing after reimport: PK={pk}")
            continue

        reimported_record = reimported_by_pk[pk]
        for field, orig_value in original.items():
            reimp_value = reimported_record.get(field)
            # Compare accounting for type conversions
            if str(orig_value) != str(reimp_value):
                errors.append(f"Difference PK={pk}, field={field}: '{orig_value}' vs '{reimp_value}'")

    return errors


# Validate customers
errors = validate_roundtrip(customers, "validation_customers.csv")
if errors:
    print("ERRORS detected:")
    for e in errors:
        print(f"  - {e}")
else:
    print("Validation successful: customer data intact after roundtrip")

# Validate orders
errors = validate_roundtrip(orders, "validation_orders.csv")
if errors:
    print("ERRORS detected:")
    for e in errors:
        print(f"  - {e}")
else:
    print("Validation successful: order data intact after roundtrip")
```

## Complete Example: Migration Pipeline

Here's the complete migration script that Sarah used to automate the entire process:

```python
"""
Legacy data migration pipeline for DictDB.
"""

from pathlib import Path
from dictdb import DictDB, DictDBError


class MigrationPipeline:
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db = DictDB()
        self.stats = {"imported": 0, "transformed": 0, "exported": 0}

    def import_csv(self, filename: str, table: str, **options):
        """Import a CSV file into a table."""
        filepath = self.source_dir / filename
        if not filepath.exists():
            print(f"WARNING: {filename} not found, skipping")
            return 0

        count = self.db.import_csv(str(filepath), table, **options)
        self.stats["imported"] += count
        print(f"Imported {count} records from {filename} -> {table}")
        return count

    def transform(self, source_table: str, dest_table: str, transform_fn):
        """Transform data from one table to another."""
        source = self.db.get_table(source_table)

        self.db.create_table(dest_table, primary_key=source.primary_key)
        dest = self.db.get_table(dest_table)

        count = 0
        for record in source.select():
            new_record = transform_fn(record)
            if new_record:  # Allows filtering by returning None
                dest.insert(new_record)
                count += 1

        self.stats["transformed"] += count
        print(f"Transformed {count} records: {source_table} -> {dest_table}")
        return count

    def export_csv(self, table: str, filename: str, **options):
        """Export a table to CSV."""
        filepath = self.output_dir / filename
        tbl = self.db.get_table(table)
        count = tbl.export_csv(str(filepath), **options)
        self.stats["exported"] += count
        print(f"Exported {count} records: {table} -> {filename}")
        return count

    def report(self):
        """Display migration report."""
        print("\n" + "=" * 50)
        print("MIGRATION REPORT")
        print("=" * 50)
        print(f"Records imported    : {self.stats['imported']}")
        print(f"Records transformed : {self.stats['transformed']}")
        print(f"Records exported    : {self.stats['exported']}")
        print(f"Tables created      : {len(self.db.list_tables())}")
        print("=" * 50)


# Execute the migration
def run_migration():
    pipeline = MigrationPipeline("./legacy_data", "./migrated_data")

    # Phase 1: Import raw data
    print("\n--- PHASE 1: IMPORT ---")
    pipeline.import_csv(
        "customers_legacy.csv",
        "customers_raw",
        primary_key="id",
        delimiter=";",
    )

    pipeline.import_csv(
        "orders_legacy.csv",
        "orders_raw",
        primary_key="ref",
        schema={"ref": str, "customer_id": int, "amount": float, "status": str, "order_date": str},
    )

    # Phase 2: Transformation
    print("\n--- PHASE 2: TRANSFORMATION ---")

    def transform_customer(record):
        """Transform a legacy customer to clean format."""
        active_str = record.get("active", "").lower()
        email = record.get("email", "").strip()

        return {
            "id": record["id"],
            "name": record.get("name", "").strip().title(),
            "email": email if email else f"unknown_{record['id']}@migration.local",
            "signup_date": record.get("signup_date", ""),
            "active": active_str in ("yes", "true", "1"),
        }

    pipeline.transform("customers_raw", "customers", transform_customer)

    def transform_order(record):
        """Transform a legacy order."""
        return {
            "ref": record["ref"],
            "customer_id": record["customer_id"],
            "amount": record["amount"],
            "status": record.get("status", "").lower().replace("_", "-"),
            "order_date": record.get("order_date", ""),
        }

    pipeline.transform("orders_raw", "orders", transform_order)

    # Phase 3: Export migrated data
    print("\n--- PHASE 3: EXPORT ---")
    pipeline.export_csv("customers", "customers_migrated.csv")
    pipeline.export_csv("orders", "orders_migrated.csv")

    # Filtered exports for departments
    customers_table = pipeline.db.get_table("customers")
    customers_table.export_csv(
        str(pipeline.output_dir / "active_customers.csv"),
        where=customers_table.active == True,
    )

    orders_table = pipeline.db.get_table("orders")
    orders_table.export_csv(
        str(pipeline.output_dir / "delivered_orders.csv"),
        where=orders_table.status == "delivered",
    )

    # Final report
    pipeline.report()

    # Save the migrated database
    pipeline.db.save(str(pipeline.output_dir / "migrated_database.json"), "json")
    print(f"\nDatabase saved: migrated_database.json")


if __name__ == "__main__":
    run_migration()
```

## What We Learned

Throughout this migration journey, Sarah and her team discovered the powerful CSV capabilities of DictDB:

1. **Import with type inference**: DictDB automatically detects `int`, `float`, and `str` types from CSV values.

2. **Import with explicit schema**: For precise control, define a type dictionary `{column: type}` that will be applied during conversion.

3. **Data transformation**: Combine `select()` and `insert()` to clean, normalize, and enrich your data.

4. **Export with filtering**: Use the `where` parameter to export only records matching your criteria.

5. **Export with column selection**: The `columns` parameter lets you choose exactly which columns to include in the export.

6. **Round-trip validation**: Export then re-import your data to verify that the process preserves data integrity.

"The migration is complete," Sarah announced with satisfaction. "Our data is now clean, properly typed, and we have validated backups."

Tom nodded. "And the best part is that the entire process is reproducible. If we receive new legacy files, we can simply rerun the pipeline."

---

*End of the migration story. In the next chapter, we'll see how to prepare this database for production deployment.*
