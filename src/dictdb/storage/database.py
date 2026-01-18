import asyncio
from pathlib import Path
from typing import Dict, List, Union

from ..core.table import Table
from ..exceptions import DuplicateTableError, TableNotFoundError
from ..obs.logging import logger


class DictDB:
    """
    The main in-memory database class that supports multiple tables.

    Provides methods to create, drop, and retrieve tables.
    """

    def __init__(self) -> None:
        """
        Initializes an empty DictDB instance.

        :return: None
        :rtype: None
        """
        self.tables: Dict[str, Table] = {}
        logger.bind(component="DictDB").info("Initialized an empty DictDB instance.")

    def create_table(self, table_name: str, primary_key: str = "id") -> None:
        """
        Creates a new table in the database.

        :param table_name: The name of the table to create.
        :type table_name: str
        :param primary_key: The field to use as the primary key for this table.
        :type primary_key: str
        :raises DuplicateTableError: If the table already exists.
        :return: None
        :rtype: None
        """
        logger.debug(
            f"[DictDB] Creating table '{table_name}' with primary key '{primary_key}'."
        )
        if table_name in self.tables:
            raise DuplicateTableError(f"Table '{table_name}' already exists.")
        self.tables[table_name] = Table(table_name, primary_key)
        logger.bind(
            component="DictDB", op="CREATE_TABLE", table=table_name, pk=primary_key
        ).info("Created table '{table}' (pk='{pk}').")

    def drop_table(self, table_name: str) -> None:
        """
        Removes a table from the database.

        :param table_name: The name of the table to drop.
        :type table_name: str
        :raises TableNotFoundError: If the table does not exist.
        :return: None
        :rtype: None
        """
        logger.debug(f"[DictDB] Dropping table '{table_name}'.")
        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist.")
        del self.tables[table_name]
        logger.bind(component="DictDB", op="DROP_TABLE", table=table_name).info(
            "Dropped table '{table}'."
        )

    def get_table(self, table_name: str) -> Table:
        """
        Retrieves a table by name.

        :param table_name: The name of the table to retrieve.
        :type table_name: str
        :raises TableNotFoundError: If the table does not exist.
        :return: The requested Table instance.
        :rtype: Table
        """
        logger.debug(f"[DictDB] Retrieving table '{table_name}'.")
        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist.")
        return self.tables[table_name]

    def list_tables(self) -> List[str]:
        """
        Lists all table names in the database.

        :return: A list of table names.
        :rtype: list of str
        """
        logger.debug("[DictDB] Listing all tables.")
        return list(self.tables.keys())

    def save(self, filename: Union[str, Path], file_format: str) -> None:
        """
        Saves the current state of the DictDB to a file in the specified file format.

        For JSON file_format, the state is converted to a serializable dictionary.
        For pickle file_format, the instance is directly serialized.

        :param filename: The path to the file where the state will be saved. Accepts both str and pathlib.Path.
        :type filename: Union[str, pathlib.Path]
        :param file_format: The file format to use for saving ("json" or "pickle").
        :type file_format: str
        :return: None
        :rtype: None
        :raises ValueError: If the file_format is unsupported.
        """
        if not isinstance(filename, str):
            filename = str(filename)

        file_format = file_format.lower()
        # Compute simple stats for observability
        table_count = len(self.tables)
        record_count = sum(t.size() for t in self.tables.values())
        logger.bind(
            component="DictDB",
            op="SAVE",
            tables=table_count,
            records=record_count,
            format=file_format,
            path=filename,
        ).info(
            "Saving database to {path} (format={format}, tables={tables}, records={records})."
        )
        from .persist import save as persist_save

        persist_save(self, filename, file_format)
        logger.bind(component="DictDB", op="SAVE", path=filename).info(
            "Save completed: {path}"
        )

    @classmethod
    def load(cls, filename: Union[str, Path], file_format: str) -> "DictDB":
        """
        Loads and returns a DictDB instance from a file containing a saved state.

        For JSON file_format, the state is parsed and each table is reconstructed.
        For pickle file_format, the DictDB instance is directly loaded.

        :param filename: The path to the file from which to load the state. Accepts both str and pathlib.Path.
        :type filename: Union[str, pathlib.Path]
        :param file_format: The file format used in the saved file ("json" or "pickle").
        :type file_format: str
        :return: A DictDB instance reconstructed from the file.
        :rtype: DictDB
        :raises ValueError: If the file_format is unsupported.
        """
        if not isinstance(filename, str):
            filename = str(filename)

        file_format = file_format.lower()
        from .persist import load as persist_load

        db = persist_load(filename, file_format)
        tables = len(db.tables)
        records = sum(t.size() for t in db.tables.values())
        logger.bind(
            component="DictDB",
            op="LOAD",
            path=filename,
            format=file_format,
            tables=tables,
            records=records,
        ).info(
            "Loaded database from {path} (format={format}, tables={tables}, records={records})."
        )
        return db

    async def async_save(self, filename: Union[str, Path], file_format: str) -> None:
        """
        Asynchronously saves the current state of the DictDB to a file in the specified file format.

        This method offloads the save operation to a background thread so that ongoing
        database operations are not blocked by file I/O.

        :param filename: The path to the file where the state will be saved.
        :type filename: Union[str, pathlib.Path]
        :param file_format: The file format to use for saving ("json" or "pickle").
        :type file_format: str
        :return: None
        :rtype: None
        """
        await asyncio.to_thread(self.save, filename, file_format)

    @classmethod
    async def async_load(cls, filename: Union[str, Path], file_format: str) -> "DictDB":
        """
        Asynchronously loads and returns a DictDB instance from a file containing a saved state.

        This method offloads the load operation to a background thread so that ongoing
        database operations are not blocked by file I/O.

        :param filename: The path to the file from which to load the state.
        :type filename: Union[str, pathlib.Path]
        :param file_format: The file format used in the saved file ("json" or "pickle").
        :type file_format: str
        :return: A DictDB instance reconstructed from the file.
        :rtype: DictDB
        :raises ValueError: If the file_format is unsupported.
        """
        return await asyncio.to_thread(cls.load, filename, file_format)
