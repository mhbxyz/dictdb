from typing import Dict, List

from .table import Table
from .logging import logger


class DictDB:
    """
    The main in-memory database class that supports multiple tables.

    Provides methods to create, drop, and retrieve tables.
    """

    def __init__(self) -> None:
        self.tables: Dict[str, Table] = {}
        logger.info("Initialized an empty DictDB instance.")

    def create_table(self, table_name: str, primary_key: str = 'id') -> None:
        """
        Creates a new table in the database.

        Args:
            table_name: The name of the table to create.
            primary_key: The primary key field for the table.

        Raises:
            ValueError: If the table already exists.
        """
        logger.debug(f"[DictDB] Creating table '{table_name}' with primary key '{primary_key}'.")
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists.")
        self.tables[table_name] = Table(table_name, primary_key)

    def drop_table(self, table_name: str) -> None:
        """
        Removes a table from the database.

        Args:
            table_name: The name of the table to drop.

        Raises:
            ValueError: If the table does not exist.
        """
        logger.debug(f"[DictDB] Dropping table '{table_name}'.")
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        del self.tables[table_name]

    def get_table(self, table_name: str) -> Table:
        """
        Retrieves a table by name.

        Args:
            table_name: The name of the table to retrieve.

        Returns:
            The corresponding Table instance.

        Raises:
            ValueError: If the table does not exist.
        """
        logger.debug(f"[DictDB] Retrieving table '{table_name}'.")
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        return self.tables[table_name]

    def list_tables(self) -> List[str]:
        """
        Lists all table names in the database.

        Returns:
            A list of table names.
        """
        logger.debug("[DictDB] Listing all tables.")
        return list(self.tables.keys())
