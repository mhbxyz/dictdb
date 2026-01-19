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


# ──────────────────────────────────────────────────────────────────────────────
# I/O Error Tests: Permissions, Disk Full, Corrupted Files
# ──────────────────────────────────────────────────────────────────────────────


def test_load_nonexistent_file(tmp_path: Path) -> None:
    """Verify that loading a non-existent file raises FileNotFoundError."""
    nonexistent = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        persist.load(nonexistent, "json")


def test_load_nonexistent_pickle(tmp_path: Path) -> None:
    """Verify that loading a non-existent pickle raises FileNotFoundError."""
    nonexistent = tmp_path / "does_not_exist.pickle"
    with pytest.raises(FileNotFoundError):
        persist.load(nonexistent, "pickle")


def test_save_to_readonly_directory(tmp_path: Path) -> None:
    """Verify that saving to a read-only directory raises PermissionError."""
    import stat

    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()

    # Make directory read-only
    readonly_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)

    try:
        db = DictDB()
        db.create_table("t")
        with pytest.raises(PermissionError):
            persist.save(db, readonly_dir / "test.json", "json")
    finally:
        # Restore permissions for cleanup
        readonly_dir.chmod(stat.S_IRWXU)


def test_load_from_unreadable_file(tmp_path: Path) -> None:
    """Verify that loading an unreadable file raises PermissionError."""
    import stat

    # Create a file and make it unreadable
    unreadable = tmp_path / "unreadable.json"
    unreadable.write_text('{"tables": {}}')
    unreadable.chmod(0)  # No permissions

    try:
        with pytest.raises(PermissionError):
            persist.load(unreadable, "json")
    finally:
        # Restore permissions for cleanup
        unreadable.chmod(stat.S_IRWXU)


def test_load_corrupted_json_syntax_error(tmp_path: Path) -> None:
    """Verify that loading malformed JSON raises JSONDecodeError."""
    corrupted = tmp_path / "corrupted.json"
    corrupted.write_text('{"tables": {invalid json syntax')

    with pytest.raises(json.JSONDecodeError):
        persist.load(corrupted, "json")


def test_load_corrupted_json_missing_tables_key(tmp_path: Path) -> None:
    """Verify that loading JSON without 'tables' key raises KeyError."""
    corrupted = tmp_path / "missing_tables.json"
    corrupted.write_text('{"data": {}}')

    with pytest.raises(KeyError):
        persist.load(corrupted, "json")


def test_load_corrupted_json_missing_primary_key(tmp_path: Path) -> None:
    """Verify that loading JSON without primary_key in table raises KeyError."""
    corrupted = tmp_path / "missing_pk.json"
    corrupted.write_text('{"tables": {"t": {"schema": null, "records": []}}}')

    with pytest.raises(KeyError):
        persist.load(corrupted, "json")


def test_load_truncated_pickle(tmp_path: Path) -> None:
    """Verify that loading a truncated pickle raises an unpickling error."""
    # Create a valid pickle first
    db = DictDB()
    db.create_table("t")
    valid_pickle = tmp_path / "valid.pickle"
    persist.save(db, valid_pickle, "pickle")

    # Read and truncate it
    content = valid_pickle.read_bytes()
    truncated = tmp_path / "truncated.pickle"
    truncated.write_bytes(content[: len(content) // 2])

    with pytest.raises((pickle.UnpicklingError, EOFError)):
        persist.load(truncated, "pickle")


def test_load_empty_json_file(tmp_path: Path) -> None:
    """Verify that loading an empty JSON file raises JSONDecodeError."""
    empty = tmp_path / "empty.json"
    empty.write_text("")

    with pytest.raises(json.JSONDecodeError):
        persist.load(empty, "json")


def test_load_empty_pickle_file(tmp_path: Path) -> None:
    """Verify that loading an empty pickle file raises an error."""
    empty = tmp_path / "empty.pickle"
    empty.write_bytes(b"")

    with pytest.raises(EOFError):
        persist.load(empty, "pickle")


def test_load_json_with_invalid_record_type(tmp_path: Path) -> None:
    """Verify that loading JSON with records as dict (not list) raises TypeError."""
    invalid = tmp_path / "invalid_records.json"
    content = {
        "tables": {
            "t": {
                "primary_key": "id",
                "schema": None,
                "records": {"1": {"id": 1}},  # Should be a list, not dict
            }
        }
    }
    invalid.write_text(json.dumps(content))

    with pytest.raises(TypeError):
        persist.load(invalid, "json")


def test_save_delta_to_readonly_directory(tmp_path: Path) -> None:
    """Verify that saving delta to a read-only directory raises PermissionError."""
    import stat

    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()

    # Make directory read-only
    readonly_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)

    try:
        db = DictDB()
        db.create_table("t")
        db.tables["t"].insert({"id": 1, "name": "test"})

        with pytest.raises(PermissionError):
            persist.save_delta(db, readonly_dir / "delta.json")
    finally:
        # Restore permissions for cleanup
        readonly_dir.chmod(stat.S_IRWXU)


def test_apply_delta_corrupted_json(tmp_path: Path) -> None:
    """Verify that applying a corrupted delta file raises JSONDecodeError."""
    corrupted = tmp_path / "corrupted_delta.json"
    corrupted.write_text('{"type": "delta", "tables":')

    db = DictDB()
    with pytest.raises(json.JSONDecodeError):
        persist.apply_delta(db, corrupted)


def test_apply_delta_invalid_type(tmp_path: Path) -> None:
    """Verify that applying a file without type='delta' raises ValueError."""
    invalid = tmp_path / "not_a_delta.json"
    invalid.write_text('{"type": "full", "tables": {}}')

    db = DictDB()
    with pytest.raises(ValueError, match="not a valid delta file"):
        persist.apply_delta(db, invalid)


def test_load_json_with_null_records(tmp_path: Path) -> None:
    """Verify that loading JSON with null records raises TypeError."""
    invalid = tmp_path / "null_records.json"
    content = {
        "tables": {
            "t": {
                "primary_key": "id",
                "schema": None,
                "records": None,
            }
        }
    }
    invalid.write_text(json.dumps(content))

    with pytest.raises(TypeError):
        persist.load(invalid, "json")


@pytest.mark.parametrize(
    "content,error_type",
    [
        pytest.param('{"tables": null}', AttributeError, id="null_tables"),
        pytest.param('{"tables": []}', AttributeError, id="tables_as_list"),
        pytest.param("null", (TypeError, AttributeError), id="null_root"),
        pytest.param("[]", (TypeError, KeyError), id="array_root"),
    ],
)
def test_load_json_structural_errors(
    tmp_path: Path, content: str, error_type: type
) -> None:
    """Verify that various structural JSON errors are handled."""
    invalid = tmp_path / "structural_error.json"
    invalid.write_text(content)

    with pytest.raises(error_type):
        persist.load(invalid, "json")
