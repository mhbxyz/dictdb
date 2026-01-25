# Migration de données historiques

*Une histoire de transformation numérique chez TechFlow SARL.*

---

C'était un lundi matin ordinaire quand Sarah, ingénieure de données principale chez TechFlow SARL, reçut un e-mail urgent de la direction. Après des années à travailler avec des fichiers CSV éparpillés entre plusieurs départements, l'entreprise avait enfin décidé de moderniser son infrastructure de données. Sarah savait que DictDB serait l'outil idéal pour relever ce défi.

« Nous avons des milliers d'enregistrements dispersés dans des fichiers clients, des historiques de commandes et des catalogues produits », expliqua-t-elle à son équipe lors de la réunion de lancement. « Notre mission est de les importer proprement, de les transformer dans un format cohérent et de nous assurer qu'aucune donnée ne soit perdue en chemin. »

## Le point de départ : les données historiques

Avant de se lancer, Sarah examina les fichiers existants. Voici un aperçu de ce qu'elle trouva :

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

## Étape 1 : Import CSV avec inférence de types

Sarah commença par l'approche la plus directe. DictDB peut détecter automatiquement les types de données à partir du contenu d'un fichier CSV.

```python
from dictdb import DictDB

# Initialiser la base de données
db = DictDB()

# Import CSV avec détection automatique des types
# Le point-virgule est le délimiteur utilisé dans les fichiers historiques
count = db.import_csv(
    "clients_legacy.csv",
    "clients",
    primary_key="id",
    delimiter=";",
    infer_types=True,  # DictDB détecte automatiquement int, float, str
)

print(f"Clients importés : {count}")

# Vérifier les types détectés
clients = db.get_table("clients")
first_client = clients.select(limit=1)[0]

print(f"Type de 'id'    : {type(first_client['id'])}")        # <class 'int'>
print(f"Type de 'nom'   : {type(first_client['nom'])}")       # <class 'str'>
print(f"Type de 'actif' : {type(first_client['actif'])}")     # <class 'str'>
```

« Intéressant », nota Sarah. « L'inférence fonctionne bien pour les chiffres, mais le champ 'actif' reste une simple chaîne de caractères. Pour plus de rigueur, nous allons définir un schéma explicite. »

## Étape 2 : Import CSV avec schéma explicite

Pour les données critiques comme les commandes, Sarah préférait garder un contrôle total sur les types de données.

```python
from dictdb import DictDB, SchemaValidationError

db = DictDB()

# Définir le schéma pour un contrôle strict
orders_schema = {
    "ref": str,
    "client_id": int,
    "montant": float,
    "statut": str,
    "date_commande": str,
}

# Import avec schéma explicite
count = db.import_csv(
    "commandes_legacy.csv",
    "commandes",
    primary_key="ref",
    delimiter=",",
    schema=orders_schema,
    infer_types=False,  # Désactiver l'inférence pour n'utiliser que le schéma
)

print(f"Commandes importées : {count}")

# Vérifier le typage strict
commandes = db.get_table("commandes")
first_order = commandes.select(limit=1)[0]

print(f"Référence : {first_order['ref']}")
print(f"Montant   : {first_order['montant']} (type : {type(first_order['montant']).__name__})")
print(f"ID Client : {first_order['client_id']} (type : {type(first_order['client_id']).__name__})")
```

## Étape 3 : Transformation et nettoyage des données

« Les données sont importées, mais elles ne sont pas encore propres », observa Thomas, le développeur junior. « Il manque des e-mails, et le champ 'actif' devrait être un vrai booléen. »

Sarah sourit. « C'est là que la transformation entre en scène. »

```python
from dictdb import DictDB, RecordNotFoundError

db = DictDB()

# Ré-importer les clients pour transformation
db.import_csv(
    "clients_legacy.csv",
    "clients_raw",
    primary_key="id",
    delimiter=";",
)

clients_raw = db.get_table("clients_raw")

# Créer une nouvelle table avec un schéma propre
db.create_table("clients", primary_key="id")
clients = db.get_table("clients")

# Transformer les données
for record in clients_raw.select():
    # Convertir "oui"/"non" en booléen
    active_str = record.get("actif", "").lower()
    is_active = active_str in ("yes", "true", "1", "oui")

    # Nettoyer l'e-mail (remplacer les vides par un placeholder)
    email = record.get("email", "").strip()
    if not email:
        email = f"inconnu_{record['id']}@placeholder.local"

    # Normaliser le nom (mise en majuscule de la première lettre)
    name = record.get("nom", "").strip().title()

    # Insérer l'enregistrement transformé
    clients.insert({
        "id": record["id"],
        "nom": name,
        "email": email,
        "date_inscription": record.get("date_inscription", ""),
        "actif": is_active,
    })

# Vérifier les transformations
print("Clients après transformation :")
for client in clients.select():
    print(f"  {client['id']} : {client['nom']} - actif={client['actif']} ({type(client['actif']).__name__})")
```

Sortie :
```
Clients après transformation :
  1 : Jean Dupont - actif=True (bool)
  2 : Maria Garcia - actif=True (bool)
  3 : Pierre Martin - actif=False (bool)
  4 : Sophie Leroy - actif=True (bool)
```

## Étape 4 : Export CSV avec filtrage

« Maintenant que nos données sont propres, nous devons générer des rapports », expliqua Sarah. « Commençons par exporter uniquement les clients actifs. »

```python
# Exporter seulement les clients actifs
clients.export_csv(
    "clients_actifs.csv",
    where=clients.actif == True,
)

print("Fichier clients_actifs.csv généré avec succès")

# Vérifier le contenu exporté
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

## Étape 5 : Export CSV avec sélection de colonnes

« Pour le département marketing, ils n'ont besoin que des noms et des e-mails », nota Thomas.

```python
# Exporter avec des colonnes sélectionnées
clients.export_csv(
    "contacts_marketing.csv",
    columns=["nom", "email"],  # Seulement ces colonnes
    where=clients.actif == True,
)

# Export pour la comptabilité : commandes livrées
commandes.export_csv(
    "commandes_livrees.csv",
    columns=["ref", "client_id", "montant", "date_commande"],
    where=commandes.statut == "livree",
)

print("Exports spécifiques générés")
```

## Étape 6 : Validation aller-retour (Round-Trip)

« Comment être sûrs que rien n'a été perdu pendant le processus ? », demanda Thomas.

Sarah lui expliqua le concept de validation aller-retour : exporter les données puis les ré-importer pour vérifier que l'intégrité est totale.

```python
from dictdb import DictDB

def validate_roundtrip(table, temp_file):
    """
    Vérifie qu'un export puis un ré-import préserve toutes les données.
    """
    # Capturer les données originales
    originals = table.select()
    original_count = len(originals)

    # Exporter vers CSV
    table.export_csv(temp_file)

    # Créer une nouvelle base et ré-importer
    test_db = DictDB()
    test_db.import_csv(
        temp_file,
        "test_reimport",
        primary_key=table.primary_key,
        infer_types=True,
    )

    reimported = test_db.get_table("test_reimport").select()
    reimport_count = len(reimported)

    # Vérifications
    errors = []

    if original_count != reimport_count:
        errors.append(f"Écart sur le nombre d'enregistrements : {original_count} vs {reimport_count}")

    # Comparer chaque enregistrement
    originals_by_pk = {r[table.primary_key]: r for r in originals}
    reimported_by_pk = {r[table.primary_key]: r for r in reimported}

    for pk, original in originals_by_pk.items():
        if pk not in reimported_by_pk:
            errors.append(f"Enregistrement manquant après ré-import : PK={pk}")
            continue

        reimported_record = reimported_by_pk[pk]
        for field, orig_value in original.items():
            reimp_value = reimported_record.get(field)
            # Comparer en tenant compte des conversions de type (str)
            if str(orig_value) != str(reimp_value):
                errors.append(f"Différence PK={pk}, champ={field} : '{orig_value}' vs '{reimp_value}'")

    return errors


# Valider les clients
errors = validate_roundtrip(clients, "validation_clients.csv")
if errors:
    print("ERREURS détectées :")
    for e in errors:
        print(f"  - {e}")
else:
    print("Validation réussie : données clients intactes")

# Valider les commandes
errors = validate_roundtrip(commandes, "validation_commandes.csv")
if errors:
    print("ERREURS détectées :")
    for e in errors:
        print(f"  - {e}")
else:
    print("Validation réussie : données commandes intactes")
```

## Exemple complet : pipeline de migration

Voici le script de migration complet que Sarah a utilisé pour automatiser tout le processus :

```python
"""
Pipeline de migration de données historiques pour DictDB.
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
        """Importe un fichier CSV dans une table."""
        filepath = self.source_dir / filename
        if not filepath.exists():
            print(f"AVERTISSEMENT : {filename} non trouvé, ignoré")
            return 0

        count = self.db.import_csv(str(filepath), table, **options)
        self.stats["imported"] += count
        print(f"Importé {count} enregistrements de {filename} -> {table}")
        return count

    def transform(self, source_table: str, dest_table: str, transform_fn):
        """Transforme les données d'une table vers une autre."""
        source = self.db.get_table(source_table)

        self.db.create_table(dest_table, primary_key=source.primary_key)
        dest = self.db.get_table(dest_table)

        count = 0
        for record in source.select():
            new_record = transform_fn(record)
            if new_record:  # Permet le filtrage en retournant None
                dest.insert(new_record)
                count += 1

        self.stats["transformed"] += count
        print(f"Transformé {count} enregistrements : {source_table} -> {dest_table}")
        return count

    def export_csv(self, table: str, filename: str, **options):
        """Exporte une table en CSV."""
        filepath = self.output_dir / filename
        tbl = self.db.get_table(table)
        count = tbl.export_csv(str(filepath), **options)
        self.stats["exported"] += count
        print(f"Exporté {count} enregistrements : {table} -> {filename}")
        return count

    def report(self):
        """Affiche le rapport de migration."""
        print("\n" + "=" * 50)
        print("RAPPORT DE MIGRATION")
        print("=" * 50)
        print(f"Enregistrements importés    : {self.stats['imported']}")
        print(f"Enregistrements transformés : {self.stats['transformed']}")
        print(f"Enregistrements exportés    : {self.stats['exported']}")
        print(f"Tables créées               : {len(self.db.list_tables())}")
        print("=" * 50)


# Exécuter la migration
def run_migration():
    pipeline = MigrationPipeline("./legacy_data", "./migrated_data")

    # Phase 1 : Importation
    print("\n--- PHASE 1 : IMPORTATION ---")
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

    # Phase 2 : Transformation
    print("\n--- PHASE 2 : TRANSFORMATION ---")

    def transform_client(record):
        """Nettoie et transforme un client historique."""
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
        """Nettoie une commande historique."""
        return {
            "ref": record["ref"],
            "client_id": record["client_id"],
            "montant": record["montant"],
            "statut": record.get("statut", "").lower().replace("_", "-"),
            "date_commande": record.get("date_commande", ""),
        }

    pipeline.transform("commandes_raw", "commandes", transform_commande)

    # Phase 3 : Exportation
    print("\n--- PHASE 3 : EXPORTATION ---")
    pipeline.export_csv("clients", "clients_migres.csv")
    pipeline.export_csv("commandes", "commandes_migrees.csv")

    # Exports filtrés par département
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

    # Rapport final
    pipeline.report()

    # Sauvegarder la base de données migrée
    pipeline.db.save(str(pipeline.output_dir / "base_migree.json"), "json")
    print(f"\nBase de données sauvegardée : base_migree.json")


if __name__ == "__main__":
    run_migration()
```

## Ce que nous avons appris

Tout au long de ce voyage de migration, Sarah et son équipe ont découvert les puissantes capacités CSV de DictDB :

1. **Import avec inférence de types** : DictDB détecte automatiquement les types `int`, `float` et `str`.

2. **Import avec schéma explicite** : Pour un contrôle précis, définissez un dictionnaire `{colonne: type}` à appliquer lors de la conversion.

3. **Transformation des données** : Combinez `select()` et `insert()` pour nettoyer, normaliser et enrichir vos données.

4. **Export avec filtrage** : Utilisez le paramètre `where` pour n'exporter que les enregistrements pertinents.

5. **Export avec sélection de colonnes** : Le paramètre `columns` vous permet de choisir exactement quoi exporter.

6. **Validation aller-retour** : Exportez puis ré-importez vos données pour garantir qu'aucune information n'est altérée.

« La migration est terminée », annonça Sarah avec satisfaction. « Nos données sont désormais propres, correctement typées et nous avons des sauvegardes validées. »

Thomas acquiesça. « Et le meilleur, c'est que tout le processus est reproductible. Si nous recevons de nouveaux fichiers historiques, nous n'avons qu'à relancer le pipeline. »

---

*Fin de l'histoire de migration. Dans le prochain chapitre, nous verrons comment préparer cette base de données pour un déploiement en production.*