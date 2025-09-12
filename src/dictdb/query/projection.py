from typing import Dict, List, Optional, Tuple, Union, cast

from ..core.types import Record

ColumnsArg = Optional[
    Union[
        List[str],
        Dict[str, str],
        List[Tuple[str, str]],
    ]
]


def project_records(records: List[Record], columns: ColumnsArg) -> List[Record]:
    def project(rec: Record) -> Record:
        if columns is None:
            return rec
        if isinstance(columns, dict):
            return {alias: rec.get(field) for alias, field in columns.items()}
        if columns and isinstance(columns[0], tuple):
            pairs = cast(List[Tuple[str, str]], columns)
            return {alias: rec.get(field) for (alias, field) in pairs}
        names = cast(List[str], columns)
        return {col: rec.get(col) for col in names}

    return [project(r) for r in records]
