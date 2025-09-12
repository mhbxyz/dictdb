import json
from pathlib import Path

import pytest

from dictdb.storage import persist
from dictdb import DictDB


def test_persist_save_invalid_format(tmp_path: Path) -> None:
    db = DictDB()
    db.create_table("t")
    with pytest.raises(ValueError):
        persist.save(db, tmp_path / "x.out", "xml")


def test_persist_load_invalid_format(tmp_path: Path) -> None:
    # No need for a real file; should fail before opening
    with pytest.raises(ValueError):
        persist.load(tmp_path / "x.out", "ini")


def test_persist_load_unsupported_schema_type(tmp_path: Path) -> None:
    # Craft a JSON file with an unsupported type in schema
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
        persist.load(p, "json")

