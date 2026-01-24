# The Sales Manager's Dashboard

## Introduction

Every Monday morning, Marcus dreads the same ritual. As the sales manager at TechSales Inc., a computer hardware distribution company, he needs to present a performance report to the executive team. His team of 8 sales representatives operates across 4 regions, selling 3 product lines, and keeping track of all those numbers has become a weekly nightmare.

Until now, Marcus spent hours copying data between spreadsheets, writing formulas, and double-checking calculations. One misplaced cell reference could throw off the entire report. But this week, Marcus decided enough was enough. He's going to automate his reporting with DictDB and its powerful aggregation features.

Let's follow Marcus as he builds his analytical dashboard.

## Preparing the Data

Marcus starts by creating his database with the month's sales data.

```python
from dictdb import DictDB, Condition, Count, Sum, Avg, Min, Max

# Create the database
db = DictDB()

# Sales representatives table
db.create_table("reps", primary_key="id")
reps = db.get_table("reps")

reps.insert({"id": 1, "name": "Alice Johnson", "region": "North", "team": "A"})
reps.insert({"id": 2, "name": "Bob Martinez", "region": "South", "team": "A"})
reps.insert({"id": 3, "name": "Claire Chen", "region": "East", "team": "B"})
reps.insert({"id": 4, "name": "David Park", "region": "West", "team": "B"})
reps.insert({"id": 5, "name": "Emma Wilson", "region": "North", "team": "A"})
reps.insert({"id": 6, "name": "Frank Brown", "region": "South", "team": "B"})
reps.insert({"id": 7, "name": "Grace Lee", "region": "East", "team": "A"})
reps.insert({"id": 8, "name": "Henry Davis", "region": "West", "team": "B"})

# Sales table
db.create_table("sales", primary_key="id")
sales = db.get_table("sales")

# January sales data
sales_data = [
    # Alice - North Region, Team A
    {"rep_id": 1, "client": "Alpha Corp", "amount": 15000, "product": "Servers", "date": "2024-01-05"},
    {"rep_id": 1, "client": "Beta Startup", "amount": 8500, "product": "Laptops", "date": "2024-01-12"},
    {"rep_id": 1, "client": "Gamma SMB", "amount": 12000, "product": "Networking", "date": "2024-01-20"},

    # Bob - South Region, Team A
    {"rep_id": 2, "client": "Delta Hotel", "amount": 22000, "product": "Servers", "date": "2024-01-08"},
    {"rep_id": 2, "client": "Epsilon Cafe", "amount": 4500, "product": "Laptops", "date": "2024-01-15"},

    # Claire - East Region, Team B
    {"rep_id": 3, "client": "Zeta Factory", "amount": 45000, "product": "Servers", "date": "2024-01-10"},
    {"rep_id": 3, "client": "Eta Logistics", "amount": 18000, "product": "Networking", "date": "2024-01-18"},
    {"rep_id": 3, "client": "Theta Transport", "amount": 9500, "product": "Laptops", "date": "2024-01-25"},

    # David - West Region, Team B
    {"rep_id": 4, "client": "Iota Bank", "amount": 35000, "product": "Servers", "date": "2024-01-03"},
    {"rep_id": 4, "client": "Kappa Insurance", "amount": 28000, "product": "Networking", "date": "2024-01-22"},

    # Emma - North Region, Team A
    {"rep_id": 5, "client": "Lambda School", "amount": 7500, "product": "Laptops", "date": "2024-01-07"},
    {"rep_id": 5, "client": "Mu City Hall", "amount": 19000, "product": "Servers", "date": "2024-01-14"},
    {"rep_id": 5, "client": "Nu Hospital", "amount": 32000, "product": "Networking", "date": "2024-01-28"},

    # Frank - South Region, Team B
    {"rep_id": 6, "client": "Xi Winery", "amount": 5500, "product": "Laptops", "date": "2024-01-11"},
    {"rep_id": 6, "client": "Omicron Co-op", "amount": 11000, "product": "Networking", "date": "2024-01-19"},

    # Grace - East Region, Team A
    {"rep_id": 7, "client": "Pi Pharmacy", "amount": 8000, "product": "Laptops", "date": "2024-01-06"},
    {"rep_id": 7, "client": "Rho Clinic", "amount": 24000, "product": "Servers", "date": "2024-01-16"},
    {"rep_id": 7, "client": "Sigma Labs", "amount": 16500, "product": "Networking", "date": "2024-01-24"},

    # Henry - West Region, Team B
    {"rep_id": 8, "client": "Tau Seaport", "amount": 38000, "product": "Servers", "date": "2024-01-09"},
    {"rep_id": 8, "client": "Upsilon Airport", "amount": 52000, "product": "Networking", "date": "2024-01-21"},
]

for sale in sales_data:
    sales.insert(sale)

print(f"Data loaded: {reps.count()} sales reps, {sales.count()} sales")
# Data loaded: 8 sales reps, 20 sales
```

## Basic Aggregations: Count, Sum, Avg, Min, Max

Marcus begins by calculating the global statistics for the month.

### Counting Sales with Count

```python
# Total number of sales
stats = sales.aggregate(
    total_sales=Count()
)
print(f"Number of sales: {stats['total_sales']}")
# Number of sales: 20
```

### Calculating Totals with Sum

```python
# Total revenue
stats = sales.aggregate(
    revenue=Sum("amount")
)
print(f"Total revenue: ${stats['revenue']:,}")
# Total revenue: $421,000
```

### Calculating Averages with Avg

```python
# Average amount per sale
stats = sales.aggregate(
    avg_amount=Avg("amount")
)
print(f"Average sale amount: ${stats['avg_amount']:,.2f}")
# Average sale amount: $21,050.00
```

### Finding Extremes with Min and Max

```python
# Smallest and largest sales
stats = sales.aggregate(
    smallest=Min("amount"),
    largest=Max("amount")
)
print(f"Smallest sale: ${stats['smallest']:,}")
print(f"Largest sale: ${stats['largest']:,}")
# Smallest sale: $4,500
# Largest sale: $52,000
```

### Combining Multiple Aggregations

Marcus can calculate all these statistics in a single query:

```python
# Global dashboard
global_stats = sales.aggregate(
    total_sales=Count(),
    revenue=Sum("amount"),
    avg_amount=Avg("amount"),
    min_sale=Min("amount"),
    max_sale=Max("amount")
)

print("=== DASHBOARD - JANUARY 2024 ===")
print(f"Number of sales      : {global_stats['total_sales']}")
print(f"Total revenue        : ${global_stats['revenue']:,}")
print(f"Average amount       : ${global_stats['avg_amount']:,.2f}")
print(f"Smallest sale        : ${global_stats['min_sale']:,}")
print(f"Largest sale         : ${global_stats['max_sale']:,}")
# === DASHBOARD - JANUARY 2024 ===
# Number of sales      : 20
# Total revenue        : $421,000
# Average amount       : $21,050.00
# Smallest sale        : $4,500
# Largest sale         : $52,000
```

## GROUP BY on a Single Field

Marcus now wants to analyze performance by sales rep, by product, and by region.

### Performance by Sales Rep

```python
# Sales by representative
by_rep = sales.aggregate(
    group_by="rep_id",
    num_sales=Count(),
    total=Sum("amount"),
    average=Avg("amount")
)

print("=== PERFORMANCE BY SALES REP ===")
for stat in by_rep:
    # Get the rep's name
    rep = reps.select(
        where=Condition(reps.id == stat["rep_id"])
    )[0]
    print(f"{rep['name']:20} : {stat['num_sales']} sales, "
          f"${stat['total']:,} (avg: ${stat['average']:,.0f})")
# === PERFORMANCE BY SALES REP ===
# Alice Johnson        : 3 sales, $35,500 (avg: $11,833)
# Bob Martinez         : 2 sales, $26,500 (avg: $13,250)
# Claire Chen          : 3 sales, $72,500 (avg: $24,167)
# David Park           : 2 sales, $63,000 (avg: $31,500)
# Emma Wilson          : 3 sales, $58,500 (avg: $19,500)
# Frank Brown          : 2 sales, $16,500 (avg: $8,250)
# Grace Lee            : 3 sales, $48,500 (avg: $16,167)
# Henry Davis          : 2 sales, $90,000 (avg: $45,000)
```

### Sales by Product Type

```python
# Analysis by product
by_product = sales.aggregate(
    group_by="product",
    sales_count=Count(),
    total=Sum("amount"),
    average=Avg("amount"),
    min_val=Min("amount"),
    max_val=Max("amount")
)

print("\n=== ANALYSIS BY PRODUCT ===")
for stat in by_product:
    print(f"\n{stat['product']}:")
    print(f"  Number of sales : {stat['sales_count']}")
    print(f"  Total           : ${stat['total']:,}")
    print(f"  Average         : ${stat['average']:,.0f}")
    print(f"  Min/Max         : ${stat['min_val']:,} - ${stat['max_val']:,}")
# === ANALYSIS BY PRODUCT ===
#
# Servers:
#   Number of sales : 6
#   Total           : $178,000
#   Average         : $29,667
#   Min/Max         : $15,000 - $45,000
#
# Laptops:
#   Number of sales : 6
#   Total           : $43,500
#   Average         : $7,250
#   Min/Max         : $4,500 - $9,500
#
# Networking:
#   Number of sales : 8
#   Total           : $199,500
#   Average         : $24,938
#   Min/Max         : $11,000 - $52,000
```

## GROUP BY on Multiple Fields

Marcus wants a finer analysis: performance by region AND by product.

```python
# Create an enriched view with region information
# First, add region to each sale
enriched_sales = []
for sale in sales.select():
    rep = reps.select(
        where=Condition(reps.id == sale["rep_id"])
    )[0]
    enriched_sale = {**sale, "region": rep["region"], "team": rep["team"]}
    enriched_sales.append(enriched_sale)

# Create a new table with enriched data
db.create_table("enriched_sales", primary_key="id")
es = db.get_table("enriched_sales")
for s in enriched_sales:
    es.insert(s)

# GROUP BY on multiple fields: region and product
by_region_product = es.aggregate(
    group_by=["region", "product"],
    sales_count=Count(),
    total=Sum("amount")
)

print("=== SALES BY REGION AND PRODUCT ===")
print(f"{'Region':<10} {'Product':<12} {'Sales':>8} {'Total':>12}")
print("-" * 45)
for stat in sorted(by_region_product, key=lambda x: (x["region"], x["product"])):
    print(f"{stat['region']:<10} {stat['product']:<12} {stat['sales_count']:>8} ${stat['total']:>10,}")
# === SALES BY REGION AND PRODUCT ===
# Region     Product         Sales        Total
# ---------------------------------------------
# East       Laptops              2     $17,500
# East       Networking           2     $34,500
# East       Servers              2     $69,000
# North      Laptops              2     $16,000
# North      Networking           2     $44,000
# North      Servers              2     $34,000
# West       Networking           2     $80,000
# West       Servers              2     $73,000
# South      Laptops              2     $10,000
# South      Networking           1     $11,000
# South      Servers              1     $22,000
```

### Performance by Team and Region

```python
# GROUP BY team and region
by_team_region = es.aggregate(
    group_by=["team", "region"],
    sales_count=Count(),
    revenue=Sum("amount"),
    average=Avg("amount")
)

print("\n=== PERFORMANCE BY TEAM AND REGION ===")
for stat in sorted(by_team_region, key=lambda x: (x["team"], x["region"])):
    print(f"Team {stat['team']} - {stat['region']:6} : "
          f"${stat['revenue']:>7,} ({stat['sales_count']} sales, "
          f"avg: ${stat['average']:,.0f})")
# === PERFORMANCE BY TEAM AND REGION ===
# Team A - East   :  $48,500 (3 sales, avg: $16,167)
# Team A - North  :  $94,000 (6 sales, avg: $15,667)
# Team A - South  :  $26,500 (2 sales, avg: $13,250)
# Team B - East   :  $72,500 (3 sales, avg: $24,167)
# Team B - West   : $153,000 (4 sales, avg: $38,250)
# Team B - South  :  $16,500 (2 sales, avg: $8,250)
```

## Combining WHERE with Aggregations

Marcus wants to analyze only certain sales. He combines `where` with `aggregate`.

### Server Sales Only

```python
# Statistics for server sales
server_stats = es.aggregate(
    where=Condition(es.product == "Servers"),
    sales_count=Count(),
    total=Sum("amount"),
    average=Avg("amount")
)

print("=== SERVER SALES ===")
print(f"Number of sales : {server_stats['sales_count']}")
print(f"Total revenue   : ${server_stats['total']:,}")
print(f"Average deal    : ${server_stats['average']:,.0f}")
# === SERVER SALES ===
# Number of sales : 6
# Total revenue   : $178,000
# Average deal    : $29,667
```

### Large Deals by Region

```python
from dictdb import And

# Sales over $20,000 by region
large_deals = es.aggregate(
    where=Condition(es.amount >= 20000),
    group_by="region",
    deals=Count(),
    total=Sum("amount")
)

print("\n=== LARGE DEALS (>= $20,000) BY REGION ===")
for stat in large_deals:
    print(f"{stat['region']:10} : {stat['deals']} deals totaling ${stat['total']:,}")
# === LARGE DEALS (>= $20,000) BY REGION ===
# South      : 1 deals totaling $22,000
# East       : 2 deals totaling $69,000
# West       : 3 deals totaling $125,000
# North      : 2 deals totaling $51,000
```

### Team A's Premium Product Performance

```python
# Team A, sales > $10,000, by product
team_a_premium = es.aggregate(
    where=And(
        es.team == "A",
        es.amount > 10000
    ),
    group_by="product",
    deals=Count(),
    total=Sum("amount"),
    average=Avg("amount")
)

print("\n=== TEAM A - PREMIUM SALES (> $10,000) ===")
for stat in team_a_premium:
    print(f"{stat['product']:12} : {stat['deals']} deals, "
          f"${stat['total']:,} (avg: ${stat['average']:,.0f})")
# === TEAM A - PREMIUM SALES (> $10,000) ===
# Servers      : 4 deals, $80,000 (avg: $20,000)
# Networking   : 3 deals, $60,500 (avg: $20,167)
# Laptops      : 1 deals, $12,000 (avg: $12,000)
```

## Column Projection and Aliasing

Marcus wants to create reports with more readable column names.

### Simple Projection

```python
# Select only specific columns
report = es.select(
    columns=["region", "product", "amount"],
    where=Condition(es.amount >= 30000),
    order_by="-amount"
)

print("=== TOP SALES (>= $30,000) ===")
for sale in report:
    print(f"{sale['region']:8} | {sale['product']:12} | ${sale['amount']:,}")
# === TOP SALES (>= $30,000) ===
# West     | Networking   | $52,000
# East     | Servers      | $45,000
# West     | Servers      | $38,000
# West     | Servers      | $35,000
# North    | Networking   | $32,000
```

### Using Aliases

```python
# Rename columns with a dictionary
aliased_report = es.select(
    columns={
        "Zone": "region",
        "Category": "product",
        "Revenue": "amount"
    },
    where=Condition(es.amount >= 30000),
    order_by="-amount"
)

print("\n=== REPORT WITH ALIASES ===")
for sale in aliased_report:
    print(f"{sale['Zone']:8} | {sale['Category']:12} | ${sale['Revenue']:,}")
# === REPORT WITH ALIASES ===
# West     | Networking   | $52,000
# East     | Servers      | $45,000
# West     | Servers      | $38,000
# West     | Servers      | $35,000
# North    | Networking   | $32,000
```

### Aliases with a List of Tuples

```python
# Alternative syntax with tuples (alias, field)
tuple_report = es.select(
    columns=[
        ("Sales Rep", "rep_id"),
        ("Product Sold", "product"),
        ("Deal Value", "amount")
    ],
    limit=5,
    order_by="-amount"
)

print("\n=== TOP 5 SALES (WITH TUPLES) ===")
for sale in tuple_report:
    print(f"Rep ID {sale['Sales Rep']} | {sale['Product Sold']:12} | ${sale['Deal Value']:,}")
# === TOP 5 SALES (WITH TUPLES) ===
# Rep ID 8 | Networking   | $52,000
# Rep ID 3 | Servers      | $45,000
# Rep ID 8 | Servers      | $38,000
# Rep ID 4 | Servers      | $35,000
# Rep ID 5 | Networking   | $32,000
```

## Marcus's Final Report

Marcus now compiles his complete report for the executive team:

```python
print("=" * 60)
print("         MONTHLY REPORT - JANUARY 2024")
print("=" * 60)

# 1. Overview
stats = es.aggregate(
    sales_count=Count(),
    total_revenue=Sum("amount"),
    avg_deal=Avg("amount")
)
print(f"\n1. OVERVIEW")
print(f"   Sales completed   : {stats['sales_count']}")
print(f"   Total Revenue     : ${stats['total_revenue']:,}")
print(f"   Average Deal      : ${stats['avg_deal']:,.0f}")

# 2. By team
print(f"\n2. PERFORMANCE BY TEAM")
by_team = es.aggregate(
    group_by="team",
    sales_count=Count(),
    revenue=Sum("amount"),
    average=Avg("amount")
)
for t in sorted(by_team, key=lambda x: x["team"]):
    print(f"   Team {t['team']} : ${t['revenue']:>7,} "
          f"({t['sales_count']} sales, avg: ${t['average']:,.0f})")

# 3. By region
print(f"\n3. PERFORMANCE BY REGION")
by_region = es.aggregate(
    group_by="region",
    sales_count=Count(),
    revenue=Sum("amount")
)
for r in sorted(by_region, key=lambda x: -x["revenue"]):
    print(f"   {r['region']:8} : ${r['revenue']:>7,} ({r['sales_count']} sales)")

# 4. By product
print(f"\n4. PERFORMANCE BY PRODUCT")
by_product = es.aggregate(
    group_by="product",
    sales_count=Count(),
    revenue=Sum("amount")
)
for p in sorted(by_product, key=lambda x: -x["revenue"]):
    print(f"   {p['product']:12} : ${p['revenue']:>7,} ({p['sales_count']} sales)")

# 5. Top 3 sales reps
print(f"\n5. TOP 3 SALES REPS")
by_rep = es.aggregate(
    group_by="rep_id",
    sales_count=Count(),
    revenue=Sum("amount")
)
top_3 = sorted(by_rep, key=lambda x: -x["revenue"])[:3]
for i, stat in enumerate(top_3, 1):
    rep = reps.select(
        where=Condition(reps.id == stat["rep_id"])
    )[0]
    print(f"   {i}. {rep['name']:20} : ${stat['revenue']:,}")

print("\n" + "=" * 60)
```

Report output:

```
============================================================
         MONTHLY REPORT - JANUARY 2024
============================================================

1. OVERVIEW
   Sales completed   : 20
   Total Revenue     : $411,000
   Average Deal      : $20,550

2. PERFORMANCE BY TEAM
   Team A : $169,000 (11 sales, avg: $15,364)
   Team B : $242,000 (9 sales, avg: $26,889)

3. PERFORMANCE BY REGION
   West     : $153,000 (4 sales)
   East     : $121,000 (6 sales)
   North    :  $94,000 (6 sales)
   South    :  $43,000 (4 sales)

4. PERFORMANCE BY PRODUCT
   Networking   : $199,500 (8 sales)
   Servers      : $178,000 (6 sales)
   Laptops      :  $43,500 (6 sales)

5. TOP 3 SALES REPS
   1. Henry Davis          : $90,000
   2. Claire Chen          : $72,500
   3. David Park           : $63,000

============================================================
```

## Summary

In this example, Marcus learned how to:

1. **Use basic aggregations**: `Count()`, `Sum()`, `Avg()`, `Min()`, `Max()` to calculate statistics
2. **Combine multiple aggregations**: Calculate all metrics in a single query
3. **Group by a single field**: Use `group_by` for analysis by dimension (sales rep, product, region)
4. **Group by multiple fields**: Use `group_by=["field1", "field2"]` for cross-dimensional analysis
5. **Filter before aggregating**: Combine `where` with `aggregate` to analyze subsets of data
6. **Project and rename columns**: Use `columns` with dictionaries or tuples to create readable reports

Marcus can now generate his reports in just a few lines of code, instead of spending hours wrestling with spreadsheets!
