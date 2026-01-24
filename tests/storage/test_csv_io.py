"""
Unit tests for CSV import/export functionality.
"""

from pathlib import Path

import pytest

from dictdb import DictDB, Table
from dictdb.storage.csv_io import read_csv, write_csv, infer_types


class TestReadCSV:
    """Tests for read_csv function."""

    def test_read_csv_basic(self, tmp_path: Path) -> None:
        """Test basic CSV reading."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name,age\n1,Alice,30\n2,Bob,25\n")

        columns, records = read_csv(csv_file)

        assert columns == ["id", "name", "age"]
        assert len(records) == 2
        assert records[0]["name"] == "Alice"
        assert records[0]["age"] == 30  # Type inferred as int
        assert records[1]["name"] == "Bob"

    def test_read_csv_with_schema(self, tmp_path: Path) -> None:
        """Test CSV reading with explicit schema."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,price,name\n1,19.99,Widget\n2,29.99,Gadget\n")

        schema = {"id": int, "price": float, "name": str}
        columns, records = read_csv(csv_file, schema=schema)

        assert records[0]["id"] == 1
        assert records[0]["price"] == 19.99
        assert records[0]["name"] == "Widget"

    def test_read_csv_infer_types(self, tmp_path: Path) -> None:
        """Test automatic type inference."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("int_col,float_col,str_col\n42,3.14,hello\n")

        columns, records = read_csv(csv_file, infer_types_enabled=True)

        assert records[0]["int_col"] == 42
        assert records[0]["float_col"] == 3.14
        assert records[0]["str_col"] == "hello"

    def test_read_csv_no_type_inference(self, tmp_path: Path) -> None:
        """Test reading without type inference."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name\n1,Alice\n")

        columns, records = read_csv(csv_file, infer_types_enabled=False)

        assert records[0]["id"] == "1"  # Remains string
        assert records[0]["name"] == "Alice"

    def test_read_csv_custom_delimiter(self, tmp_path: Path) -> None:
        """Test CSV with semicolon delimiter."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id;name;age\n1;Alice;30\n2;Bob;25\n")

        columns, records = read_csv(csv_file, delimiter=";")

        assert columns == ["id", "name", "age"]
        assert len(records) == 2
        assert records[0]["name"] == "Alice"

    def test_read_csv_no_header(self, tmp_path: Path) -> None:
        """Test CSV without header row."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("1,Alice,30\n2,Bob,25\n")

        columns, records = read_csv(csv_file, has_header=False)

        assert columns == ["col_0", "col_1", "col_2"]
        assert len(records) == 2
        assert records[0]["col_1"] == "Alice"

    def test_read_csv_quoted_fields(self, tmp_path: Path) -> None:
        """Test CSV with quoted fields containing delimiters."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text('id,name,bio\n1,"Alice, Jr.","Hello, World"\n')

        columns, records = read_csv(csv_file, infer_types_enabled=False)

        assert records[0]["name"] == "Alice, Jr."
        assert records[0]["bio"] == "Hello, World"

    def test_read_csv_empty_file(self, tmp_path: Path) -> None:
        """Test reading empty CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("")

        columns, records = read_csv(csv_file)

        assert columns == []
        assert records == []

    def test_read_csv_header_only(self, tmp_path: Path) -> None:
        """Test CSV with only header row."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name,age\n")

        columns, records = read_csv(csv_file)

        assert columns == ["id", "name", "age"]
        assert records == []

    def test_read_csv_encoding(self, tmp_path: Path) -> None:
        """Test CSV with different encoding."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name\n1,Héloïse\n", encoding="utf-8")

        columns, records = read_csv(csv_file, encoding="utf-8")

        assert records[0]["name"] == "Héloïse"

    def test_read_csv_empty_values(self, tmp_path: Path) -> None:
        """Test CSV with empty values."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("id,name,age\n1,,30\n2,Bob,\n")

        schema = {"id": int, "name": str, "age": int}
        columns, records = read_csv(csv_file, schema=schema)

        assert records[0]["name"] == ""
        assert records[1]["age"] is None  # Empty non-string becomes None


class TestWriteCSV:
    """Tests for write_csv function."""

    def test_write_csv_basic(self, tmp_path: Path) -> None:
        """Test basic CSV writing."""
        csv_file = tmp_path / "test.csv"
        records = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ]

        count = write_csv(csv_file, records)

        assert count == 2
        content = csv_file.read_text()
        assert "id,name,age" in content or "id,age,name" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_write_csv_specific_columns(self, tmp_path: Path) -> None:
        """Test writing with specific columns."""
        csv_file = tmp_path / "test.csv"
        records = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ]

        count = write_csv(csv_file, records, columns=["name", "age"])
        assert count == 2

        content = csv_file.read_text()
        lines = content.strip().split("\n")
        assert lines[0] == "name,age"
        assert "Alice,30" in content
        assert "id" not in lines[0]

    def test_write_csv_custom_delimiter(self, tmp_path: Path) -> None:
        """Test writing with custom delimiter."""
        csv_file = tmp_path / "test.csv"
        records = [{"id": 1, "name": "Alice"}]

        write_csv(csv_file, records, columns=["id", "name"], delimiter=";")

        content = csv_file.read_text()
        assert "id;name" in content
        assert "1;Alice" in content

    def test_write_csv_empty_records(self, tmp_path: Path) -> None:
        """Test writing empty record list."""
        csv_file = tmp_path / "test.csv"

        count = write_csv(csv_file, [], columns=["id", "name"])

        assert count == 0
        content = csv_file.read_text()
        assert "id,name" in content

    def test_write_csv_special_characters(self, tmp_path: Path) -> None:
        """Test writing records with special characters."""
        csv_file = tmp_path / "test.csv"
        records = [
            {"id": 1, "name": "Alice, Jr.", "bio": 'Say "Hello"'},
        ]

        write_csv(csv_file, records, columns=["id", "name", "bio"])

        # Read back and verify
        columns, read_records = read_csv(csv_file, infer_types_enabled=False)
        assert read_records[0]["name"] == "Alice, Jr."
        assert read_records[0]["bio"] == 'Say "Hello"'


class TestInferTypes:
    """Tests for infer_types function."""

    def test_infer_types_int(self) -> None:
        """Test inferring int type."""
        records = [{"col": "1"}, {"col": "2"}, {"col": "3"}]
        types = infer_types(records)
        assert types["col"] is int

    def test_infer_types_float(self) -> None:
        """Test inferring float type."""
        records = [{"col": "1.5"}, {"col": "2.5"}]
        types = infer_types(records)
        assert types["col"] is float

    def test_infer_types_mixed_int_float(self) -> None:
        """Test mixed int and float values become float."""
        records = [{"col": "1"}, {"col": "2.5"}]
        types = infer_types(records)
        assert types["col"] is float

    def test_infer_types_string(self) -> None:
        """Test inferring string type."""
        records = [{"col": "hello"}, {"col": "world"}]
        types = infer_types(records)
        assert types["col"] is str

    def test_infer_types_empty(self) -> None:
        """Test empty records."""
        types = infer_types([])
        assert types == {}


class TestDictDBImportCSV:
    """Tests for DictDB.import_csv method."""

    def test_import_csv_basic(self, tmp_path: Path) -> None:
        """Test basic CSV import."""
        csv_file = tmp_path / "users.csv"
        csv_file.write_text("id,name,age\n1,Alice,30\n2,Bob,25\n")

        db = DictDB()
        count = db.import_csv(csv_file, "users", primary_key="id")

        assert count == 2
        users = db.get_table("users")
        assert users.count() == 2
        results = users.select(where=users.name == "Alice")
        assert len(results) == 1
        assert results[0]["age"] == 30

    def test_import_csv_with_schema(self, tmp_path: Path) -> None:
        """Test import with explicit schema."""
        csv_file = tmp_path / "products.csv"
        csv_file.write_text("id,name,price\n1,Widget,19.99\n2,Gadget,29.99\n")

        db = DictDB()
        schema = {"id": int, "name": str, "price": float}
        count = db.import_csv(csv_file, "products", primary_key="id", schema=schema)

        assert count == 2
        products = db.get_table("products")
        results = products.select(where=products.price > 20)
        assert len(results) == 1
        assert results[0]["name"] == "Gadget"

    def test_import_csv_custom_delimiter(self, tmp_path: Path) -> None:
        """Test import with semicolon delimiter."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id;name\n1;Alice\n2;Bob\n")

        db = DictDB()
        count = db.import_csv(csv_file, "data", delimiter=";")

        assert count == 2

    def test_import_csv_duplicate_table_error(self, tmp_path: Path) -> None:
        """Test that importing to existing table raises error."""
        csv_file = tmp_path / "users.csv"
        csv_file.write_text("id,name\n1,Alice\n")

        db = DictDB()
        db.create_table("users")

        from dictdb.exceptions import DuplicateTableError

        with pytest.raises(DuplicateTableError):
            db.import_csv(csv_file, "users")

    def test_import_csv_empty_file(self, tmp_path: Path) -> None:
        """Test importing empty CSV."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("id,name\n")

        db = DictDB()
        count = db.import_csv(csv_file, "empty")

        assert count == 0
        assert db.get_table("empty").count() == 0


class TestTableExportCSV:
    """Tests for Table.export_csv method."""

    def test_export_csv_all_records(self, tmp_path: Path) -> None:
        """Test exporting all records."""
        table = Table("users", primary_key="id")
        table.insert({"id": 1, "name": "Alice", "age": 30})
        table.insert({"id": 2, "name": "Bob", "age": 25})

        csv_file = tmp_path / "export.csv"
        count = table.export_csv(str(csv_file))

        assert count == 2
        content = csv_file.read_text()
        assert "Alice" in content
        assert "Bob" in content

    def test_export_csv_with_where(self, tmp_path: Path) -> None:
        """Test exporting filtered records."""
        table = Table("users", primary_key="id")
        table.insert({"id": 1, "name": "Alice", "age": 30})
        table.insert({"id": 2, "name": "Bob", "age": 25})

        csv_file = tmp_path / "export.csv"
        count = table.export_csv(str(csv_file), where=table.age >= 30)

        assert count == 1
        content = csv_file.read_text()
        assert "Alice" in content
        assert "Bob" not in content

    def test_export_csv_specific_columns(self, tmp_path: Path) -> None:
        """Test exporting specific columns."""
        table = Table("users", primary_key="id")
        table.insert({"id": 1, "name": "Alice", "age": 30, "email": "alice@test.com"})

        csv_file = tmp_path / "export.csv"
        count = table.export_csv(str(csv_file), columns=["name", "email"])
        assert count == 1

        content = csv_file.read_text()
        lines = content.strip().split("\n")
        assert lines[0] == "name,email"
        assert "id" not in content
        assert "age" not in content

    def test_export_csv_custom_records(self, tmp_path: Path) -> None:
        """Test exporting pre-computed records."""
        table = Table("users", primary_key="id")
        table.insert({"id": 1, "name": "Alice"})
        table.insert({"id": 2, "name": "Bob"})

        custom_records = [{"name": "Custom1"}, {"name": "Custom2"}]
        csv_file = tmp_path / "export.csv"
        count = table.export_csv(str(csv_file), records=custom_records)

        assert count == 2
        content = csv_file.read_text()
        assert "Custom1" in content
        assert "Alice" not in content

    def test_export_csv_custom_delimiter(self, tmp_path: Path) -> None:
        """Test exporting with custom delimiter."""
        table = Table("users", primary_key="id")
        table.insert({"id": 1, "name": "Alice"})

        csv_file = tmp_path / "export.csv"
        table.export_csv(str(csv_file), columns=["id", "name"], delimiter=";")

        content = csv_file.read_text()
        assert "id;name" in content
        assert "1;Alice" in content

    def test_export_csv_empty_table(self, tmp_path: Path) -> None:
        """Test exporting empty table."""
        table = Table("users", primary_key="id")

        csv_file = tmp_path / "export.csv"
        count = table.export_csv(str(csv_file), columns=["id", "name"])

        assert count == 0


class TestCSVRoundtrip:
    """Tests for import/export roundtrip."""

    def test_roundtrip_basic(self, tmp_path: Path) -> None:
        """Test that import followed by export preserves data."""
        # Create original CSV
        original_file = tmp_path / "original.csv"
        original_file.write_text("id,name,age\n1,Alice,30\n2,Bob,25\n")

        # Import
        db = DictDB()
        db.import_csv(original_file, "users", primary_key="id")

        # Export
        export_file = tmp_path / "export.csv"
        users = db.get_table("users")
        users.export_csv(str(export_file), columns=["id", "name", "age"])

        # Re-import and compare
        db2 = DictDB()
        db2.import_csv(export_file, "users2", primary_key="id")

        users2 = db2.get_table("users2")
        assert users.count() == users2.count()

        for rec1, rec2 in zip(
            users.select(order_by="id"), users2.select(order_by="id")
        ):
            assert rec1["id"] == rec2["id"]
            assert rec1["name"] == rec2["name"]
            assert rec1["age"] == rec2["age"]

    def test_roundtrip_special_characters(self, tmp_path: Path) -> None:
        """Test roundtrip with special characters."""
        table = Table("data", primary_key="id")
        table.insert({"id": 1, "text": "Hello, World", "quote": 'Say "Hi"'})

        csv_file = tmp_path / "data.csv"
        table.export_csv(str(csv_file), columns=["id", "text", "quote"])

        # Import into new DB
        db = DictDB()
        db.import_csv(csv_file, "data2", primary_key="id", infer_types=False)

        data2 = db.get_table("data2")
        rec = data2.select()[0]
        assert rec["text"] == "Hello, World"
        assert rec["quote"] == 'Say "Hi"'
