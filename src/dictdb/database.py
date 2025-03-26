from typing import Dict, List

from .table import Table
from .logging import logger


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
        logger.info("Initialized an empty DictDB instance.")

    def create_table(self, table_name: str, primary_key: str = 'id') -> None:
        """
        Creates a new table in the database.

        :param table_name: The name of the table to create.
        :type table_name: str
        :param primary_key: The field to use as the primary key for this table.
        :type primary_key: str
        :raises ValueError: If the table already exists.
        :return: None
        :rtype: None
        """
        logger.debug(f"[DictDB] Creating table '{table_name}' with primary key '{primary_key}'.")
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists.")
        self.tables[table_name] = Table(table_name, primary_key)

    def drop_table(self, table_name: str) -> None:
        """
        Removes a table from the database.

        :param table_name: The name of the table to drop.
        :type table_name: str
        :raises ValueError: If the table does not exist.
        :return: None
        :rtype: None
        """
        logger.debug(f"[DictDB] Dropping table '{table_name}'.")
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        del self.tables[table_name]

    def get_table(self, table_name: str) -> Table:
        """
        Retrieves a table by name.

        :param table_name: The name of the table to retrieve.
        :type table_name: str
        :raises ValueError: If the table does not exist.
        :return: The requested Table instance.
        :rtype: Table
        """
        logger.debug(f"[DictDB] Retrieving table '{table_name}'.")
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        return self.tables[table_name]

    def list_tables(self) -> List[str]:
        """
        Lists all table names in the database.

        :return: A list of table names.
        :rtype: list of str
        """
        logger.debug("[DictDB] Listing all tables.")
        return list(self.tables.keys())
