# Migration de Données Historiques

*Une histoire de transformation numérique chez TechFlow SARL.*

---

C'était un lundi matin comme les autres quand Sarah, l'ingénieure données principale chez TechFlow SARL, a reçu un email urgent de la direction. Après des années d'exploitation avec des fichiers CSV éparpillés entre plusieurs départements, l'entreprise avait enfin décidé de moderniser son infrastructure de données. Sarah savait que DictDB serait la solution parfaite pour relever ce défi de migration.

« Nous avons des milliers d'enregistrements dispersés entre des fichiers clients, des historiques de commandes et des catalogues produits, » expliqua-t-elle à son équipe lors de la réunion de lancement. « Notre mission est de les importer proprement, de les transformer dans un format cohérent, et de nous assurer que rien ne se perde en chemin. »

## Le Point de Départ : Les Données Historiques

Avant de plonger dans le vif du sujet, Sarah examina les fichiers existants. Voici ce qu'elle trouva :

```csv
# clients_legacy.csv
id;nom;email;date_inscription;actif
1;Jean Dupont;jean@example.com;2023-01-15;oui
2;Maria Garcia;maria@example.com;2022-06-20;oui
3;Pierre Martin;;2021-03-10;non
4;Sophie Leroy;sophie@example.com;2024-02-28;oui
```

```csv
# commandes_legacy.csv
ref,client_id,montant,statut,date_commande
CMD001,1,150.50,livree,2024-01-10
CMD002,2,89.99,en_cours,2024-01-12
CMD003,1,220.00,annulee,2024-01-15
CMD004,4,45.00,livree,2024-01-20
```

## Première Étape : Import CSV avec Inférence de Types

Sarah commença par l'approche la plus simple. DictDB peut détecter automatiquement les types de données à partir du contenu CSV.

```python
from dictdb import DictDB

# Initialize the database
db = DictDB()

# Import CSV with automatic type inference
# The semicolon is the delimiter used in the legacy files
count = db.import_csv(
    "clients_legacy.csv",
    "clients",
    primary_key="id",
    delimiter=";",
    infer_types=True,  # DictDB automatically detects int, float, str
)

print(f"Clients importés : {count}")

# Verify the inferred types
clients = db.get_table("clients")
first_client = clients.select(limit=1)[0]

print(f"Type de 'id' : {type(first_client['id'])}")        # <class 'int'>
print(f"Type de 'nom' : {type(first_client['nom'])}")      # <class 'str'>
print(f"Type de 'actif' : {type(first_client['actif'])}")  # <class 'str'>
```

« Intéressant, » nota Sarah. « L'inférence fonctionne bien pour les nombres, mais le champ 'actif' reste une chaîne de caractères. Pour une meilleure structure, nous devons définir un schéma explicite. »

## Deuxième Étape : Import CSV avec Schéma Explicite

Pour les données critiques comme les commandes, Sarah préférait un contrôle précis sur les types de données.

```python
from dictdb import DictDB, SchemaValidationError

db = DictDB()

# Define the schema for strict control
commandes_schema = {
    "ref": str,
    "client_id": int,
    "montant": float,
    "statut": str,
    "date_commande": str,
}

# Import with explicit schema
count = db.import_csv(
    "commandes_legacy.csv",
    "commandes",
    primary_key="ref",
    delimiter=",",
    schema=commandes_schema,
    infer_types=False,  # Disable inference, use only the schema
)

print(f"Commandes importées : {count}")

# Verify strict typing
commandes = db.get_table("commandes")
first_commande = commandes.select(limit=1)[0]

print(f"Référence : {first_commande['ref']}")
print(f"Montant (float) : {first_commande['montant']}")       # 150.5 (float)
print(f"ID Client (int) : {first_commande['client_id']}")     # 1 (int)
```

## Troisième Étape : Transformation et Nettoyage des Données

« Les données sont importées, mais elles ne sont pas propres, » observa Thomas, le développeur junior. « Certains emails sont manquants, et le champ 'actif' devrait être un booléen. »

Sarah sourit. « C'est là qu'intervient la transformation. »

```python
from dictdb import DictDB, RecordNotFoundError

db = DictDB()

# Re-import customers for transformation
db.import_csv(
    "clients_legacy.csv",
    "clients_raw",
    primary_key="id",
    delimiter=";",
)

clients_raw = db.get_table("clients_raw")

# Create a new table with clean schema
db.create_table("clients", primary_key="id")
clients = db.get_table("clients")

# Transform the data
for record in clients_raw.select():
    # Convert "oui"/"non" to boolean
    actif_str = record.get("actif", "").lower()
    est_actif = actif_str in ("yes", "true", "1", "oui")

    # Clean email (replace empty with placeholder)
    email = record.get("email", "").strip()
    if not email:
        email = f"inconnu_{record['id']}@placeholder.local"

    # Normalize name (proper capitalization)
    nom = record.get("nom", "").strip().title()

    # Insert the transformed record
    clients.insert({
        "id": record["id"],
        "nom": nom,
        "email": email,
        "date_inscription": record.get("date_inscription", ""),
        "actif": est_actif,
    })

# Verify transformations
print("Clients après transformation :")
for client in clients.select():
    print(f"  {client['id']}: {client['nom']} - actif={client['actif']} ({type(client['actif']).__name__})")
```

Sortie :
```
Clients après transformation :
  1: Jean Dupont - actif=True (bool)
  2: Maria Garcia - actif=True (bool)
  3: Pierre Martin - actif=False (bool)
  4: Sophie Leroy - actif=True (bool)
```

## Quatrième Étape : Export CSV avec Filtrage

« Maintenant que nos données sont propres, nous devons générer des rapports, » expliqua Sarah. « Commençons par exporter uniquement les clients actifs. »

```python
# Export only active customers
clients.export_csv(
    "clients_actifs.csv",
    where=clients.actif == True,
)

print("Fichier clients_actifs.csv généré avec succès")

# Verify the exported content
with open("clients_actifs.csv", "r") as f:
    print(f.read())
```

Sortie :
```csv
id,nom,email,date_inscription,actif
1,Jean Dupont,jean@example.com,2023-01-15,True
2,Maria Garcia,maria@example.com,2022-06-20,True
4,Sophie Leroy,sophie@example.com,2024-02-28,True
```

## Cinquième Étape : Export CSV avec Sélection de Colonnes

« Pour le département marketing, ils n'ont besoin que des noms et des emails, » nota Thomas.

```python
# Export with selected columns
clients.export_csv(
    "contacts_marketing.csv",
    columns=["nom", "email"],  # Only these columns
    where=clients.actif == True,
)

# Export for accounting: delivered orders
commandes.export_csv(
    "commandes_livrees.csv",
    columns=["ref", "client_id", "montant", "date_commande"],
    where=commandes.statut == "livree",
)

print("Exports spécifiques générés")
```

## Sixième Étape : Validation Aller-Retour des Données

« Comment s'assurer que rien n'est perdu dans le processus ? » demanda Thomas.

Sarah expliqua le concept de validation aller-retour : exporter les données puis les réimporter pour vérifier l'intégrité.

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
        errors.append(f"Différence de nombre d'enregistrements : {original_count} vs {reimport_count}")

    # Compare each record
    originals_by_pk = {r[table.primary_key]: r for r in originals}
    reimported_by_pk = {r[table.primary_key]: r for r in reimported}

    for pk, original in originals_by_pk.items():
        if pk not in reimported_by_pk:
            errors.append(f"Enregistrement manquant après réimport : PK={pk}")
            continue

        reimported_record = reimported_by_pk[pk]
        for field, orig_value in original.items():
            reimp_value = reimported_record.get(field)
            # Compare accounting for type conversions
            if str(orig_value) != str(reimp_value):
                errors.append(f"Différence PK={pk}, champ={field}: '{orig_value}' vs '{reimp_value}'")

    return errors


# Validate customers
errors = validate_roundtrip(clients, "validation_clients.csv")
if errors:
    print("ERREURS détectées :")
    for e in errors:
        print(f"  - {e}")
else:
    print("Validation réussie : données clients intactes après aller-retour")

# Validate orders
errors = validate_roundtrip(commandes, "validation_commandes.csv")
if errors:
    print("ERREURS détectées :")
    for e in errors:
        print(f"  - {e}")
else:
    print("Validation réussie : données commandes intactes après aller-retour")
```

## Exemple Complet : Pipeline de Migration

Voici le script de migration complet que Sarah a utilisé pour automatiser l'ensemble du processus :

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
            print(f"ATTENTION : {filename} non trouvé, ignoré")
            return 0

        count = self.db.import_csv(str(filepath), table, **options)
        self.stats["imported"] += count
        print(f"Importé {count} enregistrements de {filename} -> {table}")
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
        print(f"Transformé {count} enregistrements : {source_table} -> {dest_table}")
        return count

    def export_csv(self, table: str, filename: str, **options):
        """Export a table to CSV."""
        filepath = self.output_dir / filename
        tbl = self.db.get_table(table)
        count = tbl.export_csv(str(filepath), **options)
        self.stats["exported"] += count
        print(f"Exporté {count} enregistrements : {table} -> {filename}")
        return count

    def report(self):
        """Display migration report."""
        print("\n" + "=" * 50)
        print("RAPPORT DE MIGRATION")
        print("=" * 50)
        print(f"Enregistrements importés    : {self.stats['imported']}")
        print(f"Enregistrements transformés : {self.stats['transformed']}")
        print(f"Enregistrements exportés    : {self.stats['exported']}")
        print(f"Tables créées               : {len(self.db.list_tables())}")
        print("=" * 50)


# Execute the migration
def run_migration():
    pipeline = MigrationPipeline("./legacy_data", "./migrated_data")

    # Phase 1: Import raw data
    print("\n--- PHASE 1 : IMPORT ---")
    pipeline.import_csv(
        "clients_legacy.csv",
        "clients_raw",
        primary_key="id",
        delimiter=";",
    )

    pipeline.import_csv(
        "commandes_legacy.csv",
        "commandes_raw",
        primary_key="ref",
        schema={"ref": str, "client_id": int, "montant": float, "statut": str, "date_commande": str},
    )

    # Phase 2: Transformation
    print("\n--- PHASE 2 : TRANSFORMATION ---")

    def transform_client(record):
        """Transform a legacy customer to clean format."""
        actif_str = record.get("actif", "").lower()
        email = record.get("email", "").strip()

        return {
            "id": record["id"],
            "nom": record.get("nom", "").strip().title(),
            "email": email if email else f"inconnu_{record['id']}@migration.local",
            "date_inscription": record.get("date_inscription", ""),
            "actif": actif_str in ("yes", "true", "1", "oui"),
        }

    pipeline.transform("clients_raw", "clients", transform_client)

    def transform_commande(record):
        """Transform a legacy order."""
        return {
            "ref": record["ref"],
            "client_id": record["client_id"],
            "montant": record["montant"],
            "statut": record.get("statut", "").lower().replace("_", "-"),
            "date_commande": record.get("date_commande", ""),
        }

    pipeline.transform("commandes_raw", "commandes", transform_commande)

    # Phase 3: Export migrated data
    print("\n--- PHASE 3 : EXPORT ---")
    pipeline.export_csv("clients", "clients_migres.csv")
    pipeline.export_csv("commandes", "commandes_migrees.csv")

    # Filtered exports for departments
    clients_table = pipeline.db.get_table("clients")
    clients_table.export_csv(
        str(pipeline.output_dir / "clients_actifs.csv"),
        where=clients_table.actif == True,
    )

    commandes_table = pipeline.db.get_table("commandes")
    commandes_table.export_csv(
        str(pipeline.output_dir / "commandes_livrees.csv"),
        where=commandes_table.statut == "livree",
    )

    # Final report
    pipeline.report()

    # Save the migrated database
    pipeline.db.save(str(pipeline.output_dir / "base_migree.json"), "json")
    print(f"\nBase de données sauvegardée : base_migree.json")


if __name__ == "__main__":
    run_migration()
```

## Ce Que Nous Avons Appris

Tout au long de ce parcours de migration, Sarah et son équipe ont découvert les puissantes capacités CSV de DictDB :

1. **Import avec inférence de types** : DictDB détecte automatiquement les types `int`, `float` et `str` à partir des valeurs CSV.

2. **Import avec schéma explicite** : Pour un contrôle précis, définissez un dictionnaire de types `{colonne: type}` qui sera appliqué lors de la conversion.

3. **Transformation des données** : Combinez `select()` et `insert()` pour nettoyer, normaliser et enrichir vos données.

4. **Export avec filtrage** : Utilisez le paramètre `where` pour exporter uniquement les enregistrements correspondant à vos critères.

5. **Export avec sélection de colonnes** : Le paramètre `columns` vous permet de choisir exactement quelles colonnes inclure dans l'export.

6. **Validation aller-retour** : Exportez puis réimportez vos données pour vérifier que le processus préserve l'intégrité des données.

« La migration est terminée, » annonça Sarah avec satisfaction. « Nos données sont maintenant propres, correctement typées, et nous avons des sauvegardes validées. »

Thomas acquiesça. « Et le meilleur, c'est que tout le processus est reproductible. Si nous recevons de nouveaux fichiers legacy, nous pouvons simplement relancer le pipeline. »

---

*Fin de l'histoire de migration. Dans le prochain chapitre, nous verrons comment préparer cette base de données pour un déploiement en production.*
