from dictdb.index.hash import HashIndex


def test_hash_index_delete_removes_empty_bucket() -> None:
    idx = HashIndex()
    idx.insert(1, "x")
    assert "x" in idx.index
    idx.delete(1, "x")
    assert "x" not in idx.index
