"""
This module contains unit tests for the persistence (save/load) functionality
of the DictDB in-memory database.

Tests are conducted for both JSON and pickle formats.
"""

from pathlib import Path

import pytest

from dictdb import DictDB


def test_save_load_json(tmp_path: Path) -> None:
    """
    Tests saving and loading the DictDB using JSON format.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    db = DictDB()
    # Create a table and insert a record.
    db.create_table("test")
    table = db.get_table("test")
    table.insert({"id": 1, "name": "Alice", "age": 30})

    # Save the database to a JSON file.
    file_json = tmp_path / "db.json"
    db.save(str(file_json), "json")

    # Load a new database instance from the JSON file.
    loaded_db = DictDB.load(str(file_json), "json")
    loaded_table = loaded_db.get_table("test")
    records = loaded_table.select()

    assert len(records) == 1
    assert records[0]["name"] == "Alice"
    assert records[0]["age"] == 30


def test_save_load_pickle(tmp_path: Path) -> None:
    """
    Tests saving and loading the DictDB using pickle format.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    db = DictDB()
    db.create_table("sample")
    table = db.get_table("sample")
    table.insert({"id": 1, "name": "Bob", "age": 25})

    # Save the database to a pickle file.
    file_pickle = tmp_path / "db.pkl"
    db.save(str(file_pickle), "pickle")

    # Load the database from the pickle file.
    loaded_db = DictDB.load(str(file_pickle), "pickle")
    loaded_table = loaded_db.get_table("sample")
    records = loaded_table.select()

    assert len(records) == 1
    assert records[0]["name"] == "Bob"
    assert records[0]["age"] == 25


@pytest.mark.asyncio
async def test_async_save_load_json(tmp_path: Path) -> None:
    """
    Tests asynchronously saving and loading the DictDB using JSON format.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    db = DictDB()
    db.create_table("test_async")
    table = db.get_table("test_async")
    table.insert({"id": 1, "name": "Alice", "age": 30})

    file_json = tmp_path / "async_db.json"
    await db.async_save(str(file_json), "json")

    loaded_db = await DictDB.async_load(str(file_json), "json")
    loaded_table = loaded_db.get_table("test_async")
    records = loaded_table.select()

    assert len(records) == 1
    assert records[0]["name"] == "Alice"
    assert records[0]["age"] == 30


@pytest.mark.asyncio
async def test_async_save_load_pickle(tmp_path: Path) -> None:
    """
    Tests asynchronously saving and loading the DictDB using pickle format.

    :param tmp_path: A temporary directory provided by pytest.
    :type tmp_path: Path
    :return: None
    :rtype: None
    """
    db = DictDB()
    db.create_table("sample_async")
    table = db.get_table("sample_async")
    table.insert({"id": 1, "name": "Bob", "age": 25})

    file_pickle = tmp_path / "async_db.pkl"
    await db.async_save(str(file_pickle), "pickle")

    loaded_db = await DictDB.async_load(str(file_pickle), "pickle")
    loaded_table = loaded_db.get_table("sample_async")
    records = loaded_table.select()

    assert len(records) == 1
    assert records[0]["name"] == "Bob"
    assert records[0]["age"] == 25
