import json
import pickle
from pathlib import Path
from typing import Dict, List, Union, cast, Any

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
        match file_format:
            case "json":
                state: Dict[str, Any] = {"tables": {}}
                for table_name, table in self.tables.items():
                    schema = None
                    if table.schema is not None:
                        schema = {field: table.schema[field].__name__ for field in table.schema}
                    state["tables"][table_name] = {
                        "primary_key": table.primary_key,
                        "schema": schema,
                        "records": table.all(),
                    }
                # Use StringIO to produce a JSON string.
                from io import StringIO
                s = StringIO()
                json.dump(state, s, indent=4)
                json_content: str = s.getvalue()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json_content)
            case "pickle":
                # Use BytesIO to produce pickle bytes.
                from io import BytesIO
                b = BytesIO()
                pickle.dump(self, b)
                pickled_content: bytes = b.getvalue()
                with open(filename, "wb") as f:
                    f.write(pickled_content)
            case _:
                raise ValueError("Unsupported file_format. Please use 'json' or 'pickle'.")

    @classmethod
    def _load_from_json(cls, filename: str) -> "DictDB":
        """
        Loads a DictDB instance from a JSON file.

        :param filename: The path to the JSON file.
        :type filename: str
        :return: A DictDB instance.
        :rtype: DictDB
        :raises ValueError: If an unsupported type is encountered in the schema.
        """
        with open(filename, "r", encoding="utf-8") as f:
            state = json.load(f)
        new_db = cls()
        allowed_types = {"int": int, "str": str, "float": float, "bool": bool, "list": list, "dict": dict}
        for table_name, table_data in state["tables"].items():
            primary_key = table_data["primary_key"]
            schema_data = table_data["schema"]
            schema = None
            if schema_data is not None:
                schema = {}
                for field, type_name in schema_data.items():
                    if type_name in allowed_types:
                        schema[field] = allowed_types[type_name]
                    else:
                        raise ValueError(f"Unsupported type in schema: {type_name}")
            new_table = Table(table_name, primary_key=primary_key, schema=schema)
            for record in table_data["records"]:
                new_table.insert(record)
            new_db.tables[table_name] = new_table
        return new_db

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
        match file_format:
            case "json":
                return cls._load_from_json(filename)
            case "pickle":
                with open(filename, "rb") as f:
                    db = pickle.load(f)
                return cast(DictDB, db)
            case _:
                raise ValueError("Unsupported file_format. Please use 'json' or 'pickle'.")
