import pytest

from dictdb.index.registry import create


def test_registry_invalid_type() -> None:
    with pytest.raises(ValueError):
        create("unknown")
