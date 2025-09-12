from __future__ import annotations

import json
import pickle
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Dict, Union

from .database import DictDB
from ..core.table import Table


def save(db: DictDB, filename: Union[str, Path], file_format: str) -> None:
    if not isinstance(filename, str):
        filename = str(filename)
    file_format = file_format.lower()

    match file_format:
        case "json":
            state: Dict[str, Any] = {"tables": {}}
            # Snapshot the table mapping to avoid iteration races if tables are added/removed
            for table_name, table in list(db.tables.items()):
                schema = None
                if table.schema is not None:
                    schema = {
                        field: table.schema[field].__name__ for field in table.schema
                    }
                state["tables"][table_name] = {
                    "primary_key": table.primary_key,
                    "schema": schema,
                    "records": table.all(),
                }
            s = StringIO()
            json.dump(state, s, indent=4)
            json_content: str = s.getvalue()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json_content)
        case "pickle":
            b = BytesIO()
            pickle.dump(db, b)
            pickled_content: bytes = b.getvalue()
            with open(filename, "wb") as f:
                f.write(pickled_content)
        case _:
            raise ValueError("Unsupported file_format. Please use 'json' or 'pickle'.")


def load(filename: Union[str, Path], file_format: str) -> DictDB:
    if not isinstance(filename, str):
        filename = str(filename)
    file_format = file_format.lower()

    from .database import DictDB  # Local import to avoid circular import at module load

    match file_format:
        case "json":
            with open(filename, "r", encoding="utf-8") as f:
                state = json.load(f)
            new_db = DictDB()
            allowed_types = {
                "int": int,
                "str": str,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
            }
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
        case "pickle":
            with open(filename, "rb") as f:
                loaded_db: DictDB = pickle.load(f)
            return loaded_db
        case _:
            raise ValueError("Unsupported file_format. Please use 'json' or 'pickle'.")
