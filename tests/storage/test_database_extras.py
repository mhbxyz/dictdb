from pathlib import Path
import json

import pytest

from dictdb import DictDB, Table


def test_create_table_duplicate_raises() -> None:
    db = DictDB()
    db.create_table("t")
    with pytest.raises(ValueError):
        db.create_table("t")


def test_save_load_with_path_objects(tmp_path: Path) -> None:
    db = DictDB()
    db.create_table("t")
    t: Table = db.get_table("t")
    t.insert({"id": 1, "name": "a"})
    p = tmp_path / "db.json"
    db.save(p, "json")  # pass Path to cover str-cast
    loaded = DictDB.load(p, "json")  # pass Path to cover str-cast
    lt = loaded.get_table("t")
    assert lt.select()[0]["name"] == "a"


def test_private_load_from_json(tmp_path: Path) -> None:
    db = DictDB()
    db.create_table("t")
    db.get_table("t").insert({"id": 1, "x": 1})
    p = tmp_path / "db.json"
    db.save(p, "json")
    loaded = DictDB._load_from_json(str(p))
    assert isinstance(loaded.get_table("t"), Table)


def test_private_load_from_json_unsupported_type(tmp_path: Path) -> None:
    # Craft a JSON with unsupported schema type to hit error branch
    content = {
        "tables": {
            "t": {
                "primary_key": "id",
                "schema": {"id": "int", "bad": "unknown_type"},
                "records": [{"id": 1, "bad": 1}],
            }
        }
    }
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(content))
    with pytest.raises(ValueError):
        DictDB._load_from_json(str(p))
