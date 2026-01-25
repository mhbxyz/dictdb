# Le tableau de bord du directeur commercial

## Introduction

Chaque lundi matin, Marc redoute le même rituel. En tant que directeur commercial chez TechVentes SARL, un distributeur de matériel informatique, il doit présenter un rapport de performance à la direction. Avec une équipe de 8 commerciaux répartis sur 4 régions et vendant 3 gammes de produits, jongler avec tous ces chiffres est devenu un véritable cauchemar hebdomadaire.

Jusqu'à présent, Marc passait des heures à copier des données d'un tableur à l'autre, à rédiger des formules complexes et à vérifier ses calculs. Une seule erreur de cellule et c'est tout le rapport qui était faussé. Mais cette semaine, Marc a décidé de dire stop. Il va automatiser ses rapports grâce à DictDB et ses puissantes fonctions d'agrégation.

Suivons Marc dans la création de son nouveau tableau de bord analytique.

## Préparation des données

Marc commence par initialiser sa base de données avec les ventes du mois.

```python
from dictdb import DictDB, Condition, Count, Sum, Avg, Min, Max

# Créer la base de données
db = DictDB()

# Table des commerciaux
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

# Table des ventes
db.create_table("sales", primary_key="id")
sales = db.get_table("sales")

# Données des ventes de janvier
sales_data = [
    # Alice - Région Nord, Équipe A
    {"rep_id": 1, "client": "Alpha Corp", "amount": 15000, "product": "Serveurs", "date": "2024-01-05"},
    {"rep_id": 1, "client": "Beta Startup", "amount": 8500, "product": "Portables", "date": "2024-01-12"},
    {"rep_id": 1, "client": "Gamma PME", "amount": 12000, "product": "Réseau", "date": "2024-01-20"},

    # Bernard - Région Sud, Équipe A
    {"rep_id": 2, "client": "Delta Hôtel", "amount": 22000, "product": "Serveurs", "date": "2024-01-08"},
    {"rep_id": 2, "client": "Epsilon Café", "amount": 4500, "product": "Portables", "date": "2024-01-15"},

    # Claire - Région Est, Équipe B
    {"rep_id": 3, "client": "Zeta Usine", "amount": 45000, "product": "Serveurs", "date": "2024-01-10"},
    {"rep_id": 3, "client": "Eta Logistique", "amount": 18000, "product": "Réseau", "date": "2024-01-18"},
    {"rep_id": 3, "client": "Theta Transport", "amount": 9500, "product": "Portables", "date": "2024-01-25"},

    # David - Région Ouest, Équipe B
    {"rep_id": 4, "client": "Iota Banque", "amount": 35000, "product": "Serveurs", "date": "2024-01-03"},
    {"rep_id": 4, "client": "Kappa Assurance", "amount": 28000, "product": "Réseau", "date": "2024-01-22"},

    # Emma - Région Nord, Équipe A
    {"rep_id": 5, "client": "Lambda École", "amount": 7500, "product": "Portables", "date": "2024-01-07"},
    {"rep_id": 5, "client": "Mu Mairie", "amount": 19000, "product": "Serveurs", "date": "2024-01-14"},
    {"rep_id": 5, "client": "Nu Hôpital", "amount": 32000, "product": "Réseau", "date": "2024-01-28"},

    # François - Région Sud, Équipe B
    {"rep_id": 6, "client": "Xi Domaine", "amount": 5500, "product": "Portables", "date": "2024-01-11"},
    {"rep_id": 6, "client": "Omicron Coop", "amount": 11000, "product": "Réseau", "date": "2024-01-19"},

    # Grace - Région Est, Équipe A
    {"rep_id": 7, "client": "Pi Pharmacie", "amount": 8000, "product": "Portables", "date": "2024-01-06"},
    {"rep_id": 7, "client": "Rho Clinique", "amount": 24000, "product": "Serveurs", "date": "2024-01-16"},
    {"rep_id": 7, "client": "Sigma Labs", "amount": 16500, "product": "Réseau", "date": "2024-01-24"},

    # Henri - Région Ouest, Équipe B
    {"rep_id": 8, "client": "Tau Port", "amount": 38000, "product": "Serveurs", "date": "2024-01-09"},
    {"rep_id": 8, "client": "Upsilon Aéroport", "amount": 52000, "product": "Réseau", "date": "2024-01-21"},
]

for sale in sales_data:
    sales.insert(sale)

print(f"Données chargées : {reps.count()} commerciaux, {sales.count()} ventes")
# Données chargées : 8 commerciaux, 20 ventes
```

## Agrégations de base : Count, Sum, Avg, Min, Max

Marc commence par calculer les statistiques globales du mois.

### Compter les ventes avec Count

```python
# Nombre total de ventes
stats = sales.aggregate(
    total_sales=Count()
)
print(f"Nombre de ventes : {stats['total_sales']}")
# Nombre de ventes : 20
```

### Calculer le chiffre d'affaires avec Sum

```python
# Chiffre d'affaires total
stats = sales.aggregate(
    revenue=Sum("amount")
)
print(f"CA total : {stats['revenue']:,} €")
# CA total : 421,000 €
```

### Calculer les moyennes avec Avg

```python
# Montant moyen par vente
stats = sales.aggregate(
    avg_amount=Avg("amount")
)
print(f"Panier moyen : {stats['avg_amount']:,.2f} €")
# Panier moyen : 21,050.00 €
```

### Trouver les extrêmes avec Min et Max

```python
# Plus petite et plus grande vente
stats = sales.aggregate(
    smallest=Min("amount"),
    largest=Max("amount")
)
print(f"Plus petite vente : {stats['smallest']:,} €")
print(f"Plus grande vente : {stats['largest']:,} €")
# Plus petite vente : 4,500 €
# Plus grande vente : 52,000 €
```

### Combiner plusieurs agrégations

Marc peut calculer toutes ces statistiques en une seule passe :

```python
# Tableau de bord global
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
print(f"Panier moyen         : {global_stats['avg_amount']:,.2f} €")
print(f"Vente min            : {global_stats['min_sale']:,} €")
print(f"Vente max            : {global_stats['max_sale']:,} €")
# === TABLEAU DE BORD - JANVIER 2024 ===
# Nombre de ventes     : 20
# Chiffre d'affaires   : 421,000 €
# Panier moyen         : 21,050.00 €
# Vente min            : 4,500 €
# Vente max            : 52,000 €
```

## GROUP BY sur un seul champ

Marc veut maintenant analyser la performance par commercial, par produit et par région.

### Performance par commercial

```python
# Ventes par commercial
by_rep = sales.aggregate(
    group_by="rep_id",
    num_sales=Count(),
    total=Sum("amount"),
    average=Avg("amount")
)

print("=== PERFORMANCE PAR COMMERCIAL ===")
for stat in by_rep:
    # Récupérer le nom du commercial
    rep = reps.select(
        where=Condition(reps.id == stat["rep_id"])
    )[0]
    print(f"{rep['name']:20} : {stat['num_sales']} ventes, "
          f"{stat['total']:,} € (moy : {stat['average']:,.0f} €)")
# === PERFORMANCE PAR COMMERCIAL ===
# Alice Dupont         : 3 ventes, 35,500 € (moy : 11,833 €)
# Bernard Martin       : 2 ventes, 26,500 € (moy : 13,250 €)
# Claire Chen          : 3 ventes, 72,500 € (moy : 24,167 €)
# David Park           : 2 ventes, 63,000 € (moy : 31,500 €)
# Emma Leroy           : 3 ventes, 58,500 € (moy : 19,500 €)
# François Brun        : 2 ventes, 16,500 € (moy : 8,250 €)
# Grace Lee            : 3 ventes, 48,500 € (moy : 16,167 €)
# Henri Moreau         : 2 ventes, 90,000 € (moy : 45,000 €)
```

### Ventes par type de produit

```python
# Analyse par produit
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
    print(f"  Min/Max          : {stat['min_val']:,} - {stat['max_val']:,} €")
# === ANALYSE PAR PRODUIT ===
#
# Serveurs :
#   Nombre de ventes : 6
#   Total            : 178,000 €
#   Moyenne          : 29,667 €
#   Min/Max          : 15,000 - 45,000 €
#
# Portables :
#   Nombre de ventes : 6
#   Total            : 43,500 €
#   Moyenne          : 7,250 €
#   Min/Max          : 4,500 - 9,500 €
#
# Réseau :
#   Nombre de ventes : 8
#   Total            : 199,500 €
#   Moyenne          : 24,938 €
#   Min/Max          : 11,000 - 52,000 €
```

## GROUP BY sur plusieurs champs

Marc souhaite une analyse plus fine : la performance par région ET par produit.

```python
# Créer une vue enrichie avec les informations de région
enriched_sales = []
for sale in sales.select():
    rep = reps.select(
        where=Condition(reps.id == sale["rep_id"])
    )[0]
    enriched_sale = {**sale, "region": rep["region"], "team": rep["team"]}
    enriched_sales.append(enriched_sale)

# Créer une nouvelle table avec les données enrichies
db.create_table("enriched_sales", primary_key="id")
es = db.get_table("enriched_sales")
for s in enriched_sales:
    es.insert(s)

# GROUP BY sur plusieurs champs : région et produit
by_region_product = es.aggregate(
    group_by=["region", "product"],
    sales_count=Count(),
    total=Sum("amount")
)

print("=== VENTES PAR RÉGION ET PRODUIT ===")
print(f"{ 'Région':<10} { 'Produit':<12} { 'Ventes':>8} { 'Total':>12}")
print("---------------------------------------------")
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

### Performance par équipe et région

```python
# GROUP BY équipe et région
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
          f"moy : {stat['average']:,.0f} €)")
# === PERFORMANCE PAR ÉQUIPE ET RÉGION ===
# Équipe A - Est    :  48,500 € (3 ventes, moy : 16,167 €)
# Équipe A - Nord   :  94,000 € (6 ventes, moy : 15,667 €)
# Équipe A - Sud    :  26,500 € (2 ventes, moy : 13,250 €)
# Équipe B - Est    :  72,500 € (3 ventes, moy : 24,167 €)
# Équipe B - Ouest  : 153,000 € (4 ventes, moy : 38,250 €)
# Équipe B - Sud    :  16,500 € (2 ventes, moy : 8,250 €)
```

## Combiner WHERE avec les agrégations

Marc veut analyser uniquement certaines ventes. Il combine `where` avec `aggregate`.

### Ventes de serveurs uniquement

```python
# Statistiques pour les ventes de serveurs
server_stats = es.aggregate(
    where=Condition(es.product == "Serveurs"),
    sales_count=Count(),
    total=Sum("amount"),
    average=Avg("amount")
)

print("=== VENTES DE SERVEURS ===")
print(f"Nombre de ventes : {server_stats['sales_count']}")
print(f"CA total         : {server_stats['total']:,} €")
print(f"Contrat moyen    : {server_stats['average']:,.0f} €")
# === VENTES DE SERVEURS ===
# Nombre de ventes : 6
# CA total         : 178,000 €
# Contrat moyen    : 29,667 €
```

### Gros contrats par région

```python
from dictdb import And

# Ventes de plus de 20 000 € par région
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

### Performance premium de l\'équipe A

```python
# Équipe A, ventes > 10 000 €, par produit
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
          f"{stat['total']:,} € (moy : {stat['average']:,.0f} €)")
# === ÉQUIPE A - VENTES PREMIUM (> 10 000 €) ===
# Serveurs     : 4 contrats, 80,000 € (moy : 20,000 €)
# Réseau       : 3 contrats, 60,500 € (moy : 20,167 €)
# Portables    : 1 contrats, 12,000 € (moy : 12,000 €)
```

## Projection de colonnes et alias

Marc souhaite créer des rapports avec des noms de colonnes plus explicites.

### Projection simple

```python
# Sélectionner uniquement certaines colonnes
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

### Utiliser des alias

```python
# Renommer les colonnes avec un dictionnaire
aliased_report = es.select(
    columns={
        "Zone": "region",
        "Catégorie": "product",
        "CA": "amount"
    },
    where=Condition(es.amount >= 30000),
    order_by="-amount"
)

print("\n=== RAPPORT AVEC ALIAS ===")
for sale in aliased_report:
    print(f"{sale['Zone']:8} | {sale['Catégorie']:12} | {sale['CA']:,} €")
# === RAPPORT AVEC ALIAS ===
# Ouest    | Réseau       | 52,000 €
# Est      | Serveurs     | 45,000 €
# Ouest    | Serveurs     | 38,000 €
# Ouest    | Serveurs     | 35,000 €
# Nord     | Réseau       | 32,000 €
```

### Alias avec une liste de tuples

```python
# Syntaxe alternative avec des tuples (alias, champ)
tuple_report = es.select(
    columns=[
        ("ID Rep", "rep_id"),
        ("Produit", "product"),
        ("Valeur", "amount")
    ],
    limit=5,
    order_by="-amount"
)

print("\n=== TOP 5 VENTES (AVEC TUPLES) ===")
for sale in tuple_report:
    print(f"Rep ID {sale['ID Rep']} | {sale['Produit']:12} | {sale['Valeur']:,} €")
# === TOP 5 VENTES (AVEC TUPLES) ===
# Rep ID 8 | Réseau       | 52,000 €
# Rep ID 3 | Serveurs     | 45,000 €
# Rep ID 8 | Serveurs     | 38,000 €
# Rep ID 4 | Serveurs     | 35,000 €
# Rep ID 5 | Réseau       | 32,000 €
```

## Le rapport final de Marc

Marc compile enfin son rapport complet pour la direction :

```python
print("=" * 60)
print("         RAPPORT MENSUEL - JANVIER 2024")
print("=" * 60)

# 1. Vue d'ensemble
stats = es.aggregate(
    sales_count=Count(),
    total_revenue=Sum("amount"),
    avg_deal=Avg("amount")
)
print(f"\n1. VUE D\'ENSEMBLE")
print(f"   Ventes réalisées   : {stats['sales_count']}")
print(f"   CA Total           : {stats['total_revenue']:,} €")
print(f"   Contrat moyen      : {stats['avg_deal']:,.0f} €")

# 2. Par équipe
print(f"\n2. PERFORMANCE PAR ÉQUIPE")
by_team = es.aggregate(
    group_by="team",
    sales_count=Count(),
    revenue=Sum("amount"),
    average=Avg("amount")
)
for t in sorted(by_team, key=lambda x: x["team"]):
    print(f"   Équipe {t['team']} : {t['revenue']:>7,} € "
          f"({t['sales_count']} ventes, moy : {t['average']:,.0f} €)")

# 3. Par région
print(f"\n3. PERFORMANCE PAR RÉGION")
by_region = es.aggregate(
    group_by="region",
    sales_count=Count(),
    revenue=Sum("amount")
)
for r in sorted(by_region, key=lambda x: -x["revenue"]):
    print(f"   {r['region']:8} : {r['revenue']:>7,} € ({r['sales_count']} ventes)")

# 4. Par produit
print(f"\n4. PERFORMANCE PAR PRODUIT")
by_product = es.aggregate(
    group_by="product",
    sales_count=Count(),
    revenue=Sum("amount")
)
for p in sorted(by_product, key=lambda x: -x["revenue"]):
    print(f"   {p['product']:12} : {p['revenue']:>7,} € ({p['sales_count']} ventes)")

# 5. Top 3 commerciaux
print(f"\n5. TOP 3 COMMERCIAUX")
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

1. VUE D\'ENSEMBLE
   Ventes réalisées   : 20
   CA Total           : 411,000 €
   Contrat moyen      : 20,550 €

2. PERFORMANCE PAR ÉQUIPE
   Équipe A : 169,000 € (11 ventes, moy : 15,364 €)
   Équipe B : 242,000 € (9 ventes, moy : 26,889 €)

3. PERFORMANCE PAR RÉGION
   Ouest    : 153,000 € (4 ventes)
   Est      : 121,000 € (6 ventes)
   Nord     :  94,000 € (6 ventes)
   Sud      :  43,000 € (4 ventes)

4. PERFORMANCE PAR PRODUIT
   Réseau       : 199,500 € (8 ventes)
   Serveurs     : 178,000 € (6 ventes)
   Portables    :  43,500 € (6 ventes)

5. TOP 3 COMMERCIAUX
   1. Henri Moreau         : 90,000 €
   2. Claire Chen          : 72,500 €
   3. David Park           : 63,000 €

============================================================
```

## Résumé

Dans cet exemple, Marc a appris à :

1. **Utiliser les agrégations de base** : `Count()`, `Sum()`, `Avg()`, `Min()`, `Max()` pour calculer des statistiques
2. **Combiner plusieurs agrégations** : Calculer tous les indicateurs en une seule requête
3. **Grouper par un seul champ** : Utiliser `group_by` pour analyser par dimension (commercial, produit, région)
4. **Grouper par plusieurs champs** : Utiliser `group_by=["champ1", "champ2"]` pour une analyse croisée
5. **Filtrer avant d'agréger** : Combiner `where` avec `aggregate` pour cibler des données précises
6. **Projeter et renommer les colonnes** : Utiliser `columns` pour générer des rapports lisibles

Marc peut désormais générer ses rapports en quelques lignes de code, au lieu de passer des heures à se battre avec ses tableurs !
```