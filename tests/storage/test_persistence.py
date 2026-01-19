"""
This module contains unit tests for the persistence (save/load) functionality
of the DictDB in-memory database.

Tests are conducted for both JSON and pickle formats.
"""

from pathlib import Path
import asyncio

import pytest

from dictdb import DictDB


@pytest.mark.parametrize(
    "file_format,extension",
    [
        pytest.param("json", "json", id="json_format"),
        pytest.param("pickle", "pkl", id="pickle_format"),
    ],
)
def test_save_load(tmp_path: Path, file_format: str, extension: str) -> None:
    """
    Tests saving and loading the DictDB using specified format.

    :param tmp_path: A temporary directory provided by pytest.
    :param file_format: The serialization format ('json' or 'pickle').
    :param extension: The file extension for the format.
    """
    db = DictDB()
    db.create_table("test")
    table = db.get_table("test")
    table.insert({"id": 1, "name": "Alice", "age": 30})

    file_path = tmp_path / f"db.{extension}"
    db.save(str(file_path), file_format)

    loaded_db = DictDB.load(str(file_path), file_format)
    loaded_table = loaded_db.get_table("test")
    records = loaded_table.select()

    assert len(records) == 1, f"Expected 1 record after loading {file_format}"
    assert records[0]["name"] == "Alice", f"Name mismatch after loading {file_format}"
    assert records[0]["age"] == 30, f"Age mismatch after loading {file_format}"


@pytest.mark.parametrize(
    "file_format,extension",
    [
        pytest.param("json", "json", id="async_json_format"),
        pytest.param("pickle", "pkl", id="async_pickle_format"),
    ],
)
def test_async_save_load(tmp_path: Path, file_format: str, extension: str) -> None:
    """
    Tests asynchronously saving and loading the DictDB using specified format.

    :param tmp_path: A temporary directory provided by pytest.
    :param file_format: The serialization format ('json' or 'pickle').
    :param extension: The file extension for the format.
    """
    db = DictDB()
    db.create_table("test_async")
    table = db.get_table("test_async")
    table.insert({"id": 1, "name": "Bob", "age": 25})

    file_path = tmp_path / f"async_db.{extension}"
    asyncio.run(db.async_save(str(file_path), file_format))

    loaded_db = asyncio.run(DictDB.async_load(str(file_path), file_format))
    loaded_table = loaded_db.get_table("test_async")
    records = loaded_table.select()

    assert len(records) == 1, f"Expected 1 record after async loading {file_format}"
    assert records[0]["name"] == "Bob", (
        f"Name mismatch after async loading {file_format}"
    )
    assert records[0]["age"] == 25, f"Age mismatch after async loading {file_format}"


def test_multiple_save_load_cycles(tmp_path: Path) -> None:
    """
    Tests that the DictDB state remains consistent across multiple save/load cycles.

    The database is saved and loaded repeatedly, and the final state is compared
    with the original state to ensure that no data is lost or corrupted.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    from dictdb import DictDB

    # Create and populate the database with two tables and several records.
    db = DictDB()
    db.create_table("users")
    db.create_table("products")

    users = db.get_table("users")
    products = db.get_table("products")

    users.insert({"id": 1, "name": "Alice", "age": 30})
    users.insert({"id": 2, "name": "Bob", "age": 25})
    products.insert({"id": 101, "name": "Widget", "price": 9.99})
    products.insert({"id": 102, "name": "Gadget", "price": 19.99})

    # Capture the original state for later comparison.
    original_users = sorted(users.select(), key=lambda rec: rec["id"])
    original_products = sorted(products.select(), key=lambda rec: rec["id"])

    file_path = tmp_path / "db_consistency.json"
    cycles = 3
    for _ in range(cycles):
        db.save(str(file_path), "json")
        db = DictDB.load(str(file_path), "json")

    # Validate that the state remains the same after several save/load cycles.
    users = db.get_table("users")
    products = db.get_table("products")

    loaded_users = sorted(users.select(), key=lambda rec: rec["id"])
    loaded_products = sorted(products.select(), key=lambda rec: rec["id"])

    assert loaded_users == original_users, (
        "Users table state is inconsistent across save/load cycles."
    )
    assert loaded_products == original_products, (
        "Products table state is inconsistent across save/load cycles."
    )
