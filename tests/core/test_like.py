"""
Unit tests for LIKE pattern matching operator.
"""

import pytest

from dictdb import Table, Condition


class TestLike:
    """Tests for Field.like() method."""

    @pytest.fixture
    def table(self) -> Table:
        """Create a table with test data."""
        t = Table("users", primary_key="id")
        t.insert({"id": 1, "name": "Alice", "email": "alice@gmail.com"})
        t.insert({"id": 2, "name": "Bob", "email": "bob@yahoo.com"})
        t.insert({"id": 3, "name": "Charlie", "email": "charlie@gmail.com"})
        t.insert({"id": 4, "name": "Alicia", "email": "alicia@company.org"})
        t.insert({"id": 5, "name": "Bobby", "email": "bobby@test.com"})
        return t

    def test_like_starts_with(self, table: Table) -> None:
        """Test LIKE pattern starting with prefix."""
        results = table.select(where=Condition(table.name.like("A%")))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Alicia"}

    def test_like_ends_with(self, table: Table) -> None:
        """Test LIKE pattern ending with suffix."""
        results = table.select(where=Condition(table.email.like("%@gmail.com")))
        assert len(results) == 2
        emails = {r["email"] for r in results}
        assert emails == {"alice@gmail.com", "charlie@gmail.com"}

    def test_like_contains(self, table: Table) -> None:
        """Test LIKE pattern containing substring."""
        results = table.select(where=Condition(table.name.like("%ob%")))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Bob", "Bobby"}

    def test_like_single_char_wildcard(self, table: Table) -> None:
        """Test LIKE pattern with _ single character wildcard."""
        t = Table("codes", primary_key="id")
        t.insert({"id": 1, "code": "A1B"})
        t.insert({"id": 2, "code": "A2B"})
        t.insert({"id": 3, "code": "A12B"})
        t.insert({"id": 4, "code": "AB"})

        results = t.select(where=Condition(t.code.like("A_B")))
        assert len(results) == 2
        codes = {r["code"] for r in results}
        assert codes == {"A1B", "A2B"}

    def test_like_multiple_single_char_wildcards(self) -> None:
        """Test LIKE pattern with multiple _ wildcards."""
        t = Table("data", primary_key="id")
        t.insert({"id": 1, "value": "ABC"})
        t.insert({"id": 2, "value": "A1C"})
        t.insert({"id": 3, "value": "XYZ"})
        t.insert({"id": 4, "value": "ABCD"})

        results = t.select(where=Condition(t.value.like("A__")))
        assert len(results) == 2
        values = {r["value"] for r in results}
        assert values == {"ABC", "A1C"}

    def test_like_mixed_wildcards(self) -> None:
        """Test LIKE pattern with both % and _ wildcards."""
        t = Table("files", primary_key="id")
        t.insert({"id": 1, "name": "test1.txt"})
        t.insert({"id": 2, "name": "test2.txt"})
        t.insert({"id": 3, "name": "test10.txt"})
        t.insert({"id": 4, "name": "data.txt"})

        results = t.select(where=Condition(t.name.like("test_.%")))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"test1.txt", "test2.txt"}

    def test_like_exact_match(self, table: Table) -> None:
        """Test LIKE pattern with no wildcards (exact match)."""
        results = table.select(where=Condition(table.name.like("Alice")))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_like_no_matches(self, table: Table) -> None:
        """Test LIKE pattern with no matching records."""
        results = table.select(where=Condition(table.name.like("Z%")))
        assert len(results) == 0

    def test_like_match_all(self, table: Table) -> None:
        """Test LIKE pattern matching all records."""
        results = table.select(where=Condition(table.name.like("%")))
        assert len(results) == 5

    def test_like_empty_pattern(self, table: Table) -> None:
        """Test LIKE with empty pattern (matches only empty strings)."""
        t = Table("test", primary_key="id")
        t.insert({"id": 1, "value": ""})
        t.insert({"id": 2, "value": "a"})

        results = t.select(where=Condition(t.value.like("")))
        assert len(results) == 1
        assert results[0]["value"] == ""

    def test_like_escape_percent(self) -> None:
        """Test LIKE with escaped % character."""
        t = Table("discounts", primary_key="id")
        t.insert({"id": 1, "label": "10%"})
        t.insert({"id": 2, "label": "20%"})
        t.insert({"id": 3, "label": "100"})
        t.insert({"id": 4, "label": "10 percent"})

        # Match strings ending with literal %
        results = t.select(where=Condition(t.label.like("%\\%", escape="\\")))
        assert len(results) == 2
        labels = {r["label"] for r in results}
        assert labels == {"10%", "20%"}

    def test_like_escape_underscore(self) -> None:
        """Test LIKE with escaped _ character."""
        t = Table("files", primary_key="id")
        t.insert({"id": 1, "name": "file_1"})
        t.insert({"id": 2, "name": "file_2"})
        t.insert({"id": 3, "name": "fileX1"})

        # Match strings with literal _
        results = t.select(where=Condition(t.name.like("file\\_1", escape="\\")))
        assert len(results) == 1
        assert results[0]["name"] == "file_1"

    def test_like_with_none_values(self) -> None:
        """Test that LIKE excludes None values."""
        t = Table("nullable", primary_key="id")
        t.insert({"id": 1, "name": "Alice"})
        t.insert({"id": 2, "name": None})
        t.insert({"id": 3, "name": "Bob"})

        results = t.select(where=Condition(t.name.like("%")))
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Bob"}

    def test_like_with_non_string_values(self) -> None:
        """Test that LIKE only matches string values."""
        t = Table("mixed", primary_key="id")
        t.insert({"id": 1, "value": "123"})
        t.insert({"id": 2, "value": 123})
        t.insert({"id": 3, "value": "456"})

        results = t.select(where=Condition(t.value.like("%2%")))
        assert len(results) == 1
        assert results[0]["value"] == "123"

    def test_like_case_sensitive(self, table: Table) -> None:
        """Test that LIKE is case-sensitive."""
        results = table.select(where=Condition(table.name.like("a%")))
        assert len(results) == 0  # No match because Alice starts with 'A'

        results = table.select(where=Condition(table.name.like("A%")))
        assert len(results) == 2

    def test_like_with_sorted_index_optimization(self) -> None:
        """Test that LIKE with prefix uses sorted index."""
        t = Table("indexed", primary_key="id")
        t.create_index("name", index_type="sorted")

        for i, name in enumerate(["Alice", "Alicia", "Bob", "Charlie", "Albert"]):
            t.insert({"id": i, "name": name})

        results = t.select(where=Condition(t.name.like("Al%")))
        assert len(results) == 3
        names = {r["name"] for r in results}
        assert names == {"Alice", "Alicia", "Albert"}

    def test_like_special_regex_chars(self) -> None:
        """Test that regex special characters are escaped properly."""
        t = Table("paths", primary_key="id")
        t.insert({"id": 1, "path": "C:\\Users\\test"})
        t.insert({"id": 2, "path": "C:\\Program Files"})
        t.insert({"id": 3, "path": "/home/user"})

        # The backslashes and special chars should be treated literally
        results = t.select(where=Condition(t.path.like("C:\\%")))
        assert len(results) == 2

    def test_like_with_dots(self) -> None:
        """Test that dots are treated literally, not as regex wildcards."""
        t = Table("files", primary_key="id")
        t.insert({"id": 1, "name": "file.txt"})
        t.insert({"id": 2, "name": "fileXtxt"})
        t.insert({"id": 3, "name": "file.doc"})

        results = t.select(where=Condition(t.name.like("%.txt")))
        assert len(results) == 1
        assert results[0]["name"] == "file.txt"

    def test_like_combined_with_other_conditions(self, table: Table) -> None:
        """Test LIKE combined with other conditions."""
        results = table.select(
            where=Condition(table.name.like("A%") & table.email.like("%@gmail.com"))
        )
        assert len(results) == 1
        assert results[0]["name"] == "Alice"
