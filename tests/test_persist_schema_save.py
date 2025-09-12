from pathlib import Path
import json

from dictdb import DictDB, Table


def test_save_json_includes_schema_types(tmp_path: Path) -> None:
    db = DictDB()
    t = Table("people", schema={"id": int, "name": str, "age": int})
    db.tables["people"] = t
    t.insert({"id": 1, "name": "Alice", "age": 30})

    p = tmp_path / "db.json"
    db.save(p, "json")
    data = json.loads(p.read_text())
    assert data["tables"]["people"]["schema"] == {
        "id": "int",
        "name": "str",
        "age": "int",
    }
