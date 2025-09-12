import pytest

from dictdb.index.base import IndexBase


class DummyIndex(IndexBase):
    def insert(self, pk, value):  # type: ignore[no-untyped-def]
        return IndexBase.insert(self, pk, value)

    def update(self, pk, old_value, new_value):  # type: ignore[no-untyped-def]
        return IndexBase.update(self, pk, old_value, new_value)

    def delete(self, pk, value):  # type: ignore[no-untyped-def]
        return IndexBase.delete(self, pk, value)

    def search(self, value):  # type: ignore[no-untyped-def]
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

