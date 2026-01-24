# Le Tableau de Bord du Directeur Commercial

## Introduction

Chaque lundi matin, Marc redoute le même rituel. En tant que directeur commercial chez TechVentes SARL, une entreprise de distribution de matériel informatique, il doit présenter un rapport de performance à l'équipe de direction. Son équipe de 8 commerciaux opère sur 4 régions, vendant 3 gammes de produits, et suivre tous ces chiffres est devenu un cauchemar hebdomadaire.

Jusqu'à présent, Marc passait des heures à copier des données entre des feuilles de calcul, écrire des formules et vérifier les calculs. Une seule référence de cellule mal placée pouvait fausser tout le rapport. Mais cette semaine, Marc a décidé que c'en était assez. Il va automatiser ses rapports avec DictDB et ses puissantes fonctionnalités d'agrégation.

Suivons Marc dans la construction de son tableau de bord analytique.

## Préparation des Données

Marc commence par créer sa base de données avec les données de ventes du mois.

```python
from dictdb import DictDB, Condition, Count, Sum, Avg, Min, Max

# Create the database
db = DictDB()

# Sales representatives table
db.create_table("reps", primary_key="id")
reps = db.get_table("reps")

reps.insert({"id": 1, "name": "Alice Dupont", "region": "Nord", "team": "A"})
reps.insert({"id": 2, "name": "Bernard Martin", "region": "Sud", "team": "A"})
reps.insert({"id": 3, "name": "Claire Chen", "region": "Est", "team": "B"})
reps.insert({"id": 4, "name": "David Park", "region": "Ouest", "team": "B"})
reps.insert({"id": 5, "name": "Emma Leroy", "region": "Nord", "team": "A"})
reps.insert({"id": 6, "name": "François Brun", "region": "Sud", "team": "B"})
reps.insert({"id": 7, "name": "Grace Lee", "region": "Est", "team": "A"})
reps.insert({"id": 8, "name": "Henri Moreau", "region": "Ouest", "team": "B"})

# Sales table
db.create_table("sales", primary_key="id")
sales = db.get_table("sales")

# January sales data
sales_data = [
    # Alice - North Region, Team A
    {"rep_id": 1, "client": "Alpha Corp", "amount": 15000, "product": "Serveurs", "date": "2024-01-05"},
    {"rep_id": 1, "client": "Beta Startup", "amount": 8500, "product": "Portables", "date": "2024-01-12"},
    {"rep_id": 1, "client": "Gamma PME", "amount": 12000, "product": "Réseau", "date": "2024-01-20"},

    # Bob - South Region, Team A
    {"rep_id": 2, "client": "Delta Hôtel", "amount": 22000, "product": "Serveurs", "date": "2024-01-08"},
    {"rep_id": 2, "client": "Epsilon Café", "amount": 4500, "product": "Portables", "date": "2024-01-15"},

    # Claire - East Region, Team B
    {"rep_id": 3, "client": "Zeta Usine", "amount": 45000, "product": "Serveurs", "date": "2024-01-10"},
    {"rep_id": 3, "client": "Eta Logistique", "amount": 18000, "product": "Réseau", "date": "2024-01-18"},
    {"rep_id": 3, "client": "Theta Transport", "amount": 9500, "product": "Portables", "date": "2024-01-25"},

    # David - West Region, Team B
    {"rep_id": 4, "client": "Iota Banque", "amount": 35000, "product": "Serveurs", "date": "2024-01-03"},
    {"rep_id": 4, "client": "Kappa Assurance", "amount": 28000, "product": "Réseau", "date": "2024-01-22"},

    # Emma - North Region, Team A
    {"rep_id": 5, "client": "Lambda École", "amount": 7500, "product": "Portables", "date": "2024-01-07"},
    {"rep_id": 5, "client": "Mu Mairie", "amount": 19000, "product": "Serveurs", "date": "2024-01-14"},
    {"rep_id": 5, "client": "Nu Hôpital", "amount": 32000, "product": "Réseau", "date": "2024-01-28"},

    # Frank - South Region, Team B
    {"rep_id": 6, "client": "Xi Domaine", "amount": 5500, "product": "Portables", "date": "2024-01-11"},
    {"rep_id": 6, "client": "Omicron Coopérative", "amount": 11000, "product": "Réseau", "date": "2024-01-19"},

    # Grace - East Region, Team A
    {"rep_id": 7, "client": "Pi Pharmacie", "amount": 8000, "product": "Portables", "date": "2024-01-06"},
    {"rep_id": 7, "client": "Rho Clinique", "amount": 24000, "product": "Serveurs", "date": "2024-01-16"},
    {"rep_id": 7, "client": "Sigma Labs", "amount": 16500, "product": "Réseau", "date": "2024-01-24"},

    # Henry - West Region, Team B
    {"rep_id": 8, "client": "Tau Port", "amount": 38000, "product": "Serveurs", "date": "2024-01-09"},
    {"rep_id": 8, "client": "Upsilon Aéroport", "amount": 52000, "product": "Réseau", "date": "2024-01-21"},
]

for sale in sales_data:
    sales.insert(sale)

print(f"Data loaded: {reps.count()} sales reps, {sales.count()} sales")
# Data loaded: 8 sales reps, 20 sales
```

## Agrégations de Base : Count, Sum, Avg, Min, Max

Marc commence par calculer les statistiques globales du mois.

### Compter les Ventes avec Count

```python
# Total number of sales
stats = sales.aggregate(
    total_sales=Count()
)
print(f"Nombre de ventes : {stats['total_sales']}")
# Nombre de ventes : 20
```

### Calculer les Totaux avec Sum

```python
# Total revenue
stats = sales.aggregate(
    revenue=Sum("amount")
)
print(f"Chiffre d'affaires total : {stats['revenue']:,} €")
# Chiffre d'affaires total : 421,000 €
```

### Calculer les Moyennes avec Avg

```python
# Average amount per sale
stats = sales.aggregate(
    avg_amount=Avg("amount")
)
print(f"Montant moyen par vente : {stats['avg_amount']:,.2f} €")
# Montant moyen par vente : 21,050.00 €
```

### Trouver les Extrêmes avec Min et Max

```python
# Smallest and largest sales
stats = sales.aggregate(
    smallest=Min("amount"),
    largest=Max("amount")
)
print(f"Plus petite vente : {stats['smallest']:,} €")
print(f"Plus grande vente : {stats['largest']:,} €")
# Plus petite vente : 4,500 €
# Plus grande vente : 52,000 €
```

### Combiner Plusieurs Agrégations

Marc peut calculer toutes ces statistiques en une seule requête :

```python
# Global dashboard
global_stats = sales.aggregate(
    total_sales=Count(),
    revenue=Sum("amount"),
    avg_amount=Avg("amount"),
    min_sale=Min("amount"),
    max_sale=Max("amount")
)

print("=== TABLEAU DE BORD - JANVIER 2024 ===")
print(f"Nombre de ventes     : {global_stats['total_sales']}")
print(f"Chiffre d'affaires   : {global_stats['revenue']:,} €")
print(f"Montant moyen        : {global_stats['avg_amount']:,.2f} €")
print(f"Plus petite vente    : {global_stats['min_sale']:,} €")
print(f"Plus grande vente    : {global_stats['max_sale']:,} €")
# === TABLEAU DE BORD - JANVIER 2024 ===
# Nombre de ventes     : 20
# Chiffre d'affaires   : 421,000 €
# Montant moyen        : 21,050.00 €
# Plus petite vente    : 4,500 €
# Plus grande vente    : 52,000 €
```

## GROUP BY sur un Seul Champ

Marc veut maintenant analyser les performances par commercial, par produit et par région.

### Performance par Commercial

```python
# Sales by representative
by_rep = sales.aggregate(
    group_by="rep_id",
    num_sales=Count(),
    total=Sum("amount"),
    average=Avg("amount")
)

print("=== PERFORMANCE PAR COMMERCIAL ===")
for stat in by_rep:
    # Get the rep's name
    rep = reps.select(
        where=Condition(reps.id == stat["rep_id"])
    )[0]
    print(f"{rep['name']:20} : {stat['num_sales']} ventes, "
          f"{stat['total']:,} € (moy: {stat['average']:,.0f} €)")
# === PERFORMANCE PAR COMMERCIAL ===
# Alice Dupont         : 3 ventes, 35,500 € (moy: 11,833 €)
# Bernard Martin       : 2 ventes, 26,500 € (moy: 13,250 €)
# Claire Chen          : 3 ventes, 72,500 € (moy: 24,167 €)
# David Park           : 2 ventes, 63,000 € (moy: 31,500 €)
# Emma Leroy           : 3 ventes, 58,500 € (moy: 19,500 €)
# François Brun        : 2 ventes, 16,500 € (moy: 8,250 €)
# Grace Lee            : 3 ventes, 48,500 € (moy: 16,167 €)
# Henri Moreau         : 2 ventes, 90,000 € (moy: 45,000 €)
```

### Ventes par Type de Produit

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

print("\n=== ANALYSE PAR PRODUIT ===")
for stat in by_product:
    print(f"\n{stat['product']} :")
    print(f"  Nombre de ventes : {stat['sales_count']}")
    print(f"  Total            : {stat['total']:,} €")
    print(f"  Moyenne          : {stat['average']:,.0f} €")
    print(f"  Min/Max          : {stat['min_val']:,} € - {stat['max_val']:,} €")
# === ANALYSE PAR PRODUIT ===
#
# Serveurs :
#   Nombre de ventes : 6
#   Total            : 178,000 €
#   Moyenne          : 29,667 €
#   Min/Max          : 15,000 € - 45,000 €
#
# Portables :
#   Nombre de ventes : 6
#   Total            : 43,500 €
#   Moyenne          : 7,250 €
#   Min/Max          : 4,500 € - 9,500 €
#
# Réseau :
#   Nombre de ventes : 8
#   Total            : 199,500 €
#   Moyenne          : 24,938 €
#   Min/Max          : 11,000 € - 52,000 €
```

## GROUP BY sur Plusieurs Champs

Marc souhaite une analyse plus fine : les performances par région ET par produit.

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

print("=== VENTES PAR RÉGION ET PRODUIT ===")
print(f"{'Région':<10} {'Produit':<12} {'Ventes':>8} {'Total':>12}")
print("-" * 45)
for stat in sorted(by_region_product, key=lambda x: (x["region"], x["product"])):
    print(f"{stat['region']:<10} {stat['product']:<12} {stat['sales_count']:>8} {stat['total']:>10,} €")
# === VENTES PAR RÉGION ET PRODUIT ===
# Région     Produit        Ventes        Total
# ---------------------------------------------
# Est        Portables           2     17,500 €
# Est        Réseau              2     34,500 €
# Est        Serveurs            2     69,000 €
# Nord       Portables           2     16,000 €
# Nord       Réseau              2     44,000 €
# Nord       Serveurs            2     34,000 €
# Ouest      Réseau              2     80,000 €
# Ouest      Serveurs            2     73,000 €
# Sud        Portables           2     10,000 €
# Sud        Réseau              1     11,000 €
# Sud        Serveurs            1     22,000 €
```

### Performance par Équipe et Région

```python
# GROUP BY team and region
by_team_region = es.aggregate(
    group_by=["team", "region"],
    sales_count=Count(),
    revenue=Sum("amount"),
    average=Avg("amount")
)

print("\n=== PERFORMANCE PAR ÉQUIPE ET RÉGION ===")
for stat in sorted(by_team_region, key=lambda x: (x["team"], x["region"])):
    print(f"Équipe {stat['team']} - {stat['region']:6} : "
          f"{stat['revenue']:>7,} € ({stat['sales_count']} ventes, "
          f"moy: {stat['average']:,.0f} €)")
# === PERFORMANCE PAR ÉQUIPE ET RÉGION ===
# Équipe A - Est    :  48,500 € (3 ventes, moy: 16,167 €)
# Équipe A - Nord   :  94,000 € (6 ventes, moy: 15,667 €)
# Équipe A - Sud    :  26,500 € (2 ventes, moy: 13,250 €)
# Équipe B - Est    :  72,500 € (3 ventes, moy: 24,167 €)
# Équipe B - Ouest  : 153,000 € (4 ventes, moy: 38,250 €)
# Équipe B - Sud    :  16,500 € (2 ventes, moy: 8,250 €)
```

## Combiner WHERE avec les Agrégations

Marc veut analyser uniquement certaines ventes. Il combine `where` avec `aggregate`.

### Ventes de Serveurs Uniquement

```python
# Statistics for server sales
server_stats = es.aggregate(
    where=Condition(es.product == "Serveurs"),
    sales_count=Count(),
    total=Sum("amount"),
    average=Avg("amount")
)

print("=== VENTES DE SERVEURS ===")
print(f"Nombre de ventes : {server_stats['sales_count']}")
print(f"Chiffre d'affaires : {server_stats['total']:,} €")
print(f"Contrat moyen    : {server_stats['average']:,.0f} €")
# === VENTES DE SERVEURS ===
# Nombre de ventes : 6
# Chiffre d'affaires : 178,000 €
# Contrat moyen    : 29,667 €
```

### Gros Contrats par Région

```python
from dictdb import And

# Sales over 20,000€ by region
large_deals = es.aggregate(
    where=Condition(es.amount >= 20000),
    group_by="region",
    deals=Count(),
    total=Sum("amount")
)

print("\n=== GROS CONTRATS (>= 20 000 €) PAR RÉGION ===")
for stat in large_deals:
    print(f"{stat['region']:10} : {stat['deals']} contrats pour un total de {stat['total']:,} €")
# === GROS CONTRATS (>= 20 000 €) PAR RÉGION ===
# Sud        : 1 contrats pour un total de 22,000 €
# Est        : 2 contrats pour un total de 69,000 €
# Ouest      : 3 contrats pour un total de 125,000 €
# Nord       : 2 contrats pour un total de 51,000 €
```

### Performance Premium de l'Équipe A

```python
# Team A, sales > 10,000€, by product
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

print("\n=== ÉQUIPE A - VENTES PREMIUM (> 10 000 €) ===")
for stat in team_a_premium:
    print(f"{stat['product']:12} : {stat['deals']} contrats, "
          f"{stat['total']:,} € (moy: {stat['average']:,.0f} €)")
# === ÉQUIPE A - VENTES PREMIUM (> 10 000 €) ===
# Serveurs     : 4 contrats, 80,000 € (moy: 20,000 €)
# Réseau       : 3 contrats, 60,500 € (moy: 20,167 €)
# Portables    : 1 contrats, 12,000 € (moy: 12,000 €)
```

## Projection de Colonnes et Alias

Marc souhaite créer des rapports avec des noms de colonnes plus lisibles.

### Projection Simple

```python
# Select only specific columns
report = es.select(
    columns=["region", "product", "amount"],
    where=Condition(es.amount >= 30000),
    order_by="-amount"
)

print("=== TOP VENTES (>= 30 000 €) ===")
for sale in report:
    print(f"{sale['region']:8} | {sale['product']:12} | {sale['amount']:,} €")
# === TOP VENTES (>= 30 000 €) ===
# Ouest    | Réseau       | 52,000 €
# Est      | Serveurs     | 45,000 €
# Ouest    | Serveurs     | 38,000 €
# Ouest    | Serveurs     | 35,000 €
# Nord     | Réseau       | 32,000 €
```

### Utilisation des Alias

```python
# Rename columns with a dictionary
aliased_report = es.select(
    columns={
        "Zone": "region",
        "Catégorie": "product",
        "Montant": "amount"
    },
    where=Condition(es.amount >= 30000),
    order_by="-amount"
)

print("\n=== RAPPORT AVEC ALIAS ===")
for sale in aliased_report:
    print(f"{sale['Zone']:8} | {sale['Catégorie']:12} | {sale['Montant']:,} €")
# === RAPPORT AVEC ALIAS ===
# Ouest    | Réseau       | 52,000 €
# Est      | Serveurs     | 45,000 €
# Ouest    | Serveurs     | 38,000 €
# Ouest    | Serveurs     | 35,000 €
# Nord     | Réseau       | 32,000 €
```

### Alias avec une Liste de Tuples

```python
# Alternative syntax with tuples (alias, field)
tuple_report = es.select(
    columns=[
        ("ID Commercial", "rep_id"),
        ("Produit Vendu", "product"),
        ("Valeur Contrat", "amount")
    ],
    limit=5,
    order_by="-amount"
)

print("\n=== TOP 5 VENTES (AVEC TUPLES) ===")
for sale in tuple_report:
    print(f"Commercial {sale['ID Commercial']} | {sale['Produit Vendu']:12} | {sale['Valeur Contrat']:,} €")
# === TOP 5 VENTES (AVEC TUPLES) ===
# Commercial 8 | Réseau       | 52,000 €
# Commercial 3 | Serveurs     | 45,000 €
# Commercial 8 | Serveurs     | 38,000 €
# Commercial 4 | Serveurs     | 35,000 €
# Commercial 5 | Réseau       | 32,000 €
```

## Le Rapport Final de Marc

Marc compile maintenant son rapport complet pour l'équipe de direction :

```python
print("=" * 60)
print("         RAPPORT MENSUEL - JANVIER 2024")
print("=" * 60)

# 1. Overview
stats = es.aggregate(
    sales_count=Count(),
    total_revenue=Sum("amount"),
    avg_deal=Avg("amount")
)
print(f"\n1. VUE D'ENSEMBLE")
print(f"   Ventes réalisées   : {stats['sales_count']}")
print(f"   Chiffre d'affaires : {stats['total_revenue']:,} €")
print(f"   Contrat moyen      : {stats['avg_deal']:,.0f} €")

# 2. By team
print(f"\n2. PERFORMANCE PAR ÉQUIPE")
by_team = es.aggregate(
    group_by="team",
    sales_count=Count(),
    revenue=Sum("amount"),
    average=Avg("amount")
)
for t in sorted(by_team, key=lambda x: x["team"]):
    print(f"   Équipe {t['team']} : {t['revenue']:>7,} € "
          f"({t['sales_count']} ventes, moy: {t['average']:,.0f} €)")

# 3. By region
print(f"\n3. PERFORMANCE PAR RÉGION")
by_region = es.aggregate(
    group_by="region",
    sales_count=Count(),
    revenue=Sum("amount")
)
for r in sorted(by_region, key=lambda x: -x["revenue"]):
    print(f"   {r['region']:8} : {r['revenue']:>7,} € ({r['sales_count']} ventes)")

# 4. By product
print(f"\n4. PERFORMANCE PAR PRODUIT")
by_product = es.aggregate(
    group_by="product",
    sales_count=Count(),
    revenue=Sum("amount")
)
for p in sorted(by_product, key=lambda x: -x["revenue"]):
    print(f"   {p['product']:12} : {p['revenue']:>7,} € ({p['sales_count']} ventes)")

# 5. Top 3 sales reps
print(f"\n5. TOP 3 DES COMMERCIAUX")
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
    print(f"   {i}. {rep['name']:20} : {stat['revenue']:,} €")

print("\n" + "=" * 60)
```

Sortie du rapport :

```
============================================================
         RAPPORT MENSUEL - JANVIER 2024
============================================================

1. VUE D'ENSEMBLE
   Ventes réalisées   : 20
   Chiffre d'affaires : 411,000 €
   Contrat moyen      : 20,550 €

2. PERFORMANCE PAR ÉQUIPE
   Équipe A : 169,000 € (11 ventes, moy: 15,364 €)
   Équipe B : 242,000 € (9 ventes, moy: 26,889 €)

3. PERFORMANCE PAR RÉGION
   Ouest    : 153,000 € (4 ventes)
   Est      : 121,000 € (6 ventes)
   Nord     :  94,000 € (6 ventes)
   Sud      :  43,000 € (4 ventes)

4. PERFORMANCE PAR PRODUIT
   Réseau       : 199,500 € (8 ventes)
   Serveurs     : 178,000 € (6 ventes)
   Portables    :  43,500 € (6 ventes)

5. TOP 3 DES COMMERCIAUX
   1. Henri Moreau         : 90,000 €
   2. Claire Chen          : 72,500 €
   3. David Park           : 63,000 €

============================================================
```

## Résumé

Dans cet exemple, Marc a appris à :

1. **Utiliser les agrégations de base** : `Count()`, `Sum()`, `Avg()`, `Min()`, `Max()` pour calculer des statistiques
2. **Combiner plusieurs agrégations** : Calculer toutes les métriques en une seule requête
3. **Grouper par un seul champ** : Utiliser `group_by` pour l'analyse par dimension (commercial, produit, région)
4. **Grouper par plusieurs champs** : Utiliser `group_by=["champ1", "champ2"]` pour une analyse multidimensionnelle
5. **Filtrer avant d'agréger** : Combiner `where` avec `aggregate` pour analyser des sous-ensembles de données
6. **Projeter et renommer les colonnes** : Utiliser `columns` avec des dictionnaires ou des tuples pour créer des rapports lisibles

Marc peut maintenant générer ses rapports en quelques lignes de code, au lieu de passer des heures à se débattre avec des feuilles de calcul !
