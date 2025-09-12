from typing import Any, Callable, List, Optional, Sequence, Union

from ..core.types import Record


def order_records(
    records: List[Record], order_by: Optional[Union[str, Sequence[str]]]
) -> List[Record]:
    if not order_by:
        return list(records)
    fields = [order_by] if isinstance(order_by, str) else list(order_by)

    def _make_key(field_name: str) -> Callable[[Record], Any]:
        def _key_fn(r: Record) -> Any:
            return r.get(field_name)

        return _key_fn

    result = list(records)
    for field in reversed(fields):
        desc = False
        fname = field
        if field.startswith("-"):
            desc = True
            fname = field[1:]
        result.sort(key=_make_key(fname), reverse=desc)
    return result
