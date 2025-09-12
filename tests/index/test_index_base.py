import pytest
from typing import Any, Set

from dictdb.index.base import IndexBase


class DummyIndex(IndexBase):
    def insert(self, pk: Any, value: Any) -> None:
        return IndexBase.insert(self, pk, value)

    def update(self, pk: Any, old_value: Any, new_value: Any) -> None:
        return IndexBase.update(self, pk, old_value, new_value)

    def delete(self, pk: Any, value: Any) -> None:
        return IndexBase.delete(self, pk, value)

    def search(self, value: Any) -> Set[Any]:
        return IndexBase.search(self, value)


def test_index_base_not_implemented() -> None:
    idx = DummyIndex()
    with pytest.raises(NotImplementedError):
        idx.insert(1, "v")
    with pytest.raises(NotImplementedError):
        idx.update(1, "a", "b")
    with pytest.raises(NotImplementedError):
        idx.delete(1, "v")
    with pytest.raises(NotImplementedError):
        idx.search("v")
