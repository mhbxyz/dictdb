"""
Unit tests for case-insensitive string matching.
"""

import pytest

from dictdb import Table, Condition


class TestCaseInsensitive:
    """Tests for case-insensitive Field methods."""

    @pytest.fixture
    def table(self) -> Table:
        """Create a table with test data."""
        t = Table("users", primary_key="id")
        t.insert({"id": 1, "name": "Alice", "email": "Alice@Gmail.com"})
        t.insert({"id": 2, "name": "BOB", "email": "bob@yahoo.com"})
        t.insert({"id": 3, "name": "charlie", "email": "CHARLIE@Gmail.COM"})
        t.insert({"id": 4, "name": "Diana", "email": "diana@company.org"})
        return t

    # --- iequals tests ---

    def test_iequals_lowercase_query(self, table: Table) -> None:
        """Test iequals with lowercase query."""
        results = table.select(where=Condition(table.name.iequals("alice")))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_iequals_uppercase_query(self, table: Table) -> None:
        """Test iequals with uppercase query."""
        results = table.select(where=Condition(table.name.iequals("BOB")))
        assert len(results) == 1
        assert results[0]["name"] == "BOB"

    def test_iequals_mixed_case_query(self, table: Table) -> None:
        """Test iequals with mixed case query."""
        results = table.select(where=Condition(table.name.iequals("ChArLiE")))
        assert len(results) == 1
        assert results[0]["name"] == "charlie"

    def test_iequals_no_match(self, table: Table) -> None:
        """Test iequals with no matching records."""
        results = table.select(where=Condition(table.name.iequals("eve")))
        assert len(results) == 0

    def test_iequals_non_string_values(self) -> None:
        """Test that iequals only matches string values."""
        t = Table("mixed", primary_key="id")
        t.insert({"id": 1, "value": "Alice"})
        t.insert({"id": 2, "value": 123})
        t.insert({"id": 3, "value": None})

        results = t.select(where=Condition(t.value.iequals("alice")))
        assert len(results) == 1
        assert results[0]["value"] == "Alice"

    # --- icontains tests ---

    def test_icontains_lowercase_query(self, table: Table) -> None:
        """Test icontains with lowercase query."""
        results = table.select(where=Condition(table.name.icontains("lic")))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_icontains_uppercase_query(self, table: Table) -> None:
        """Test icontains with uppercase query."""
        results = table.select(where=Condition(table.name.icontains("LIC")))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_icontains_multiple_matches(self, table: Table) -> None:
        """Test icontains matching multiple records."""
        results = table.select(where=Condition(table.email.icontains("gmail")))
        assert len(results) == 2
        emails = {r["email"] for r in results}
        assert emails == {"Alice@Gmail.com", "CHARLIE@Gmail.COM"}

    def test_icontains_no_match(self, table: Table) -> None:
        """Test icontains with no matches."""
        results = table.select(where=Condition(table.name.icontains("xyz")))
        assert len(results) == 0

    def test_icontains_non_string_values(self) -> None:
        """Test that icontains only matches string values."""
        t = Table("mixed", primary_key="id")
        t.insert({"id": 1, "value": "Hello World"})
        t.insert({"id": 2, "value": 123})

        results = t.select(where=Condition(t.value.icontains("WORLD")))
        assert len(results) == 1

    # --- istartswith tests ---

    def test_istartswith_lowercase_query(self, table: Table) -> None:
        """Test istartswith with lowercase query."""
        results = table.select(where=Condition(table.name.istartswith("a")))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_istartswith_uppercase_query(self, table: Table) -> None:
        """Test istartswith with uppercase query."""
        results = table.select(where=Condition(table.name.istartswith("D")))
        assert len(results) == 1
        assert results[0]["name"] == "Diana"

    def test_istartswith_mixed_case_data(self, table: Table) -> None:
        """Test istartswith with mixed case in data."""
        results = table.select(where=Condition(table.name.istartswith("CH")))
        assert len(results) == 1
        assert results[0]["name"] == "charlie"

    def test_istartswith_no_match(self, table: Table) -> None:
        """Test istartswith with no matches."""
        results = table.select(where=Condition(table.name.istartswith("z")))
        assert len(results) == 0

    def test_istartswith_non_string_values(self) -> None:
        """Test that istartswith only matches string values."""
        t = Table("mixed", primary_key="id")
        t.insert({"id": 1, "value": "Hello"})
        t.insert({"id": 2, "value": 123})

        results = t.select(where=Condition(t.value.istartswith("HELLO")))
        assert len(results) == 1

    # --- iendswith tests ---

    def test_iendswith_lowercase_query(self, table: Table) -> None:
        """Test iendswith with lowercase query."""
        results = table.select(where=Condition(table.email.iendswith("@gmail.com")))
        assert len(results) == 2

    def test_iendswith_uppercase_query(self, table: Table) -> None:
        """Test iendswith with uppercase query."""
        results = table.select(where=Condition(table.email.iendswith("@YAHOO.COM")))
        assert len(results) == 1
        assert results[0]["email"] == "bob@yahoo.com"

    def test_iendswith_mixed_case(self, table: Table) -> None:
        """Test iendswith with mixed case query and data."""
        results = table.select(where=Condition(table.email.iendswith("@GmAiL.cOm")))
        assert len(results) == 2

    def test_iendswith_no_match(self, table: Table) -> None:
        """Test iendswith with no matches."""
        results = table.select(where=Condition(table.email.iendswith("@hotmail.com")))
        assert len(results) == 0

    def test_iendswith_non_string_values(self) -> None:
        """Test that iendswith only matches string values."""
        t = Table("mixed", primary_key="id")
        t.insert({"id": 1, "value": "file.TXT"})
        t.insert({"id": 2, "value": 123})

        results = t.select(where=Condition(t.value.iendswith(".txt")))
        assert len(results) == 1

    # --- ilike tests ---

    def test_ilike_starts_with(self, table: Table) -> None:
        """Test ilike pattern starting with prefix."""
        results = table.select(where=Condition(table.name.ilike("a%")))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_ilike_ends_with(self, table: Table) -> None:
        """Test ilike pattern ending with suffix."""
        results = table.select(where=Condition(table.email.ilike("%@GMAIL.COM")))
        assert len(results) == 2

    def test_ilike_contains(self, table: Table) -> None:
        """Test ilike pattern containing substring."""
        results = table.select(where=Condition(table.name.ilike("%LI%")))
        assert len(results) == 2  # Alice and charlie
        names = {r["name"] for r in results}
        assert names == {"Alice", "charlie"}

    def test_ilike_single_char_wildcard(self) -> None:
        """Test ilike with _ single character wildcard."""
        t = Table("codes", primary_key="id")
        t.insert({"id": 1, "code": "A1B"})
        t.insert({"id": 2, "code": "a2b"})
        t.insert({"id": 3, "code": "A12B"})

        results = t.select(where=Condition(t.code.ilike("a_b")))
        assert len(results) == 2
        codes = {r["code"] for r in results}
        assert codes == {"A1B", "a2b"}

    def test_ilike_exact_match(self, table: Table) -> None:
        """Test ilike with no wildcards (case-insensitive exact match)."""
        results = table.select(where=Condition(table.name.ilike("ALICE")))
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_ilike_no_matches(self, table: Table) -> None:
        """Test ilike with no matching records."""
        results = table.select(where=Condition(table.name.ilike("z%")))
        assert len(results) == 0

    def test_ilike_with_escape(self) -> None:
        """Test ilike with escaped characters."""
        t = Table("discounts", primary_key="id")
        t.insert({"id": 1, "label": "10%"})
        t.insert({"id": 2, "label": "10 PERCENT"})

        results = t.select(where=Condition(t.label.ilike("%\\%", escape="\\")))
        assert len(results) == 1
        assert results[0]["label"] == "10%"

    def test_ilike_non_string_values(self) -> None:
        """Test that ilike only matches string values."""
        t = Table("mixed", primary_key="id")
        t.insert({"id": 1, "value": "HELLO"})
        t.insert({"id": 2, "value": 123})

        results = t.select(where=Condition(t.value.ilike("hello")))
        assert len(results) == 1

    # --- Combined tests ---

    def test_combined_case_insensitive_conditions(self, table: Table) -> None:
        """Test combining case-insensitive conditions."""
        results = table.select(
            where=Condition(
                table.name.istartswith("a") & table.email.iendswith("@gmail.com")
            )
        )
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_case_sensitive_vs_insensitive(self, table: Table) -> None:
        """Test difference between case-sensitive and case-insensitive methods."""
        # Case-sensitive startswith
        sensitive = table.select(where=Condition(table.name.startswith("a")))
        assert len(sensitive) == 0  # No match for lowercase 'a'

        # Case-insensitive istartswith
        insensitive = table.select(where=Condition(table.name.istartswith("a")))
        assert len(insensitive) == 1  # Matches 'Alice'

    def test_like_vs_ilike(self, table: Table) -> None:
        """Test difference between like and ilike."""
        # Case-sensitive like
        sensitive = table.select(where=Condition(table.name.like("a%")))
        assert len(sensitive) == 0  # No match for lowercase pattern

        # Case-insensitive ilike
        insensitive = table.select(where=Condition(table.name.ilike("a%")))
        assert len(insensitive) == 1  # Matches 'Alice'
