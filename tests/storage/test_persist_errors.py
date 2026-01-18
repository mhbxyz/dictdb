import json
import pickle
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


def test_pickle_load_rejects_forbidden_class(tmp_path: Path) -> None:
    """Verify that loading a pickle with non-whitelisted classes raises an error."""
    # Create a malicious pickle that tries to instantiate os.system
    # This would allow RCE if not blocked
    import os

    malicious_path = tmp_path / "malicious.pickle"
    with open(malicious_path, "wb") as f:
        # Pickle a reference to os.system (a dangerous callable)
        pickle.dump(os.system, f)

    with pytest.raises(pickle.UnpicklingError, match="not allowed"):
        persist.load(malicious_path, "pickle")


def test_path_traversal_blocked_on_save(tmp_path: Path) -> None:
    """Verify that path traversal attempts are blocked when allowed_dir is set."""
    db = DictDB()
    db.create_table("t")

    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()

    # Try to escape using path traversal
    with pytest.raises(ValueError, match="outside the allowed directory"):
        persist.save(
            db, tmp_path / "allowed" / ".." / "escaped.json", "json", allowed_dir
        )


def test_path_traversal_blocked_on_load(tmp_path: Path) -> None:
    """Verify that path traversal attempts are blocked when allowed_dir is set."""
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()

    # Create a file outside the allowed directory
    outside_file = tmp_path / "outside.json"
    outside_file.write_text('{"tables": {}}')

    # Try to load from outside the allowed directory
    with pytest.raises(ValueError, match="outside the allowed directory"):
        persist.load(outside_file, "json", allowed_dir)
