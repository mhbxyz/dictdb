"""Tests for the custom logging module."""

import json
import logging
from io import StringIO
from pathlib import Path

from _pytest.capture import CaptureFixture

from dictdb import DictDB, configure_logging
from dictdb.obs.logging import (
    BoundLogger,
    DictDBFormatter,
    DictDBLogger,
    JSONFormatter,
    SampleDebugFilter,
    logger,
)


# ──────────────────────────────────────────────────────────────────────────────
# Unit tests for logging components
# ──────────────────────────────────────────────────────────────────────────────


class TestSampleDebugFilter:
    """Tests for the SampleDebugFilter class."""

    def test_passes_non_debug_messages(self) -> None:
        """Non-DEBUG messages should always pass."""
        filter_ = SampleDebugFilter(every_n=10)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )
        # All INFO messages should pass
        for _ in range(20):
            assert filter_.filter(record) is True

    def test_samples_debug_messages(self) -> None:
        """Only 1 out of every N DEBUG messages should pass."""
        filter_ = SampleDebugFilter(every_n=3)
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )
        results = [filter_.filter(record) for _ in range(9)]
        # Should pass on 3rd, 6th, 9th calls
        assert results == [False, False, True, False, False, True, False, False, True]


class TestDictDBFormatter:
    """Tests for the DictDBFormatter class."""

    def test_format_without_colors(self) -> None:
        """Test formatting without ANSI colors."""
        formatter = DictDBFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.extra = {}
        output = formatter.format(record)
        assert "INFO" in output
        assert "Test message" in output
        assert "\033[" not in output  # No ANSI codes

    def test_format_with_colors(self) -> None:
        """Test formatting with ANSI colors."""
        formatter = DictDBFormatter(use_colors=True)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.extra = {}
        output = formatter.format(record)
        assert "\033[32m" in output  # Green for INFO

    def test_format_with_extra_metadata(self) -> None:
        """Test formatting with extra metadata."""
        formatter = DictDBFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.extra = {"table": "users", "op": "INSERT"}
        output = formatter.format(record)
        assert "table=users" in output
        assert "op=INSERT" in output

    def test_format_with_placeholder_interpolation(self) -> None:
        """Test that {key} placeholders are interpolated from extra."""
        formatter = DictDBFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Inserted into {table}",
            args=(),
            exc_info=None,
        )
        record.extra = {"table": "users"}
        output = formatter.format(record)
        assert "Inserted into users" in output


class TestJSONFormatter:
    """Tests for the JSONFormatter class."""

    def test_json_output(self) -> None:
        """Test JSON formatted output."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.extra = {"key": "value"}
        output = formatter.format(record)
        data = json.loads(output)
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert data["extra"] == {"key": "value"}
        assert "time" in data

    def test_json_interpolation(self) -> None:
        """Test that JSON formatter interpolates placeholders."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Table {name} created",
            args=(),
            exc_info=None,
        )
        record.extra = {"name": "users"}
        output = formatter.format(record)
        data = json.loads(output)
        assert data["message"] == "Table users created"


class TestBoundLogger:
    """Tests for the BoundLogger class."""

    def test_bind_creates_new_instance(self) -> None:
        """Test that bind() creates a new BoundLogger with merged extra."""
        base_logger = logging.getLogger("test_bound")
        bound = BoundLogger(base_logger, {"a": 1})
        bound2 = bound.bind(b=2)

        assert bound is not bound2
        assert bound._extra == {"a": 1}
        assert bound2._extra == {"a": 1, "b": 2}

    def test_bind_chain(self) -> None:
        """Test chaining multiple bind() calls."""
        base_logger = logging.getLogger("test_chain")
        bound = BoundLogger(base_logger, {})
        result = bound.bind(a=1).bind(b=2).bind(c=3)
        assert result._extra == {"a": 1, "b": 2, "c": 3}


class TestDictDBLogger:
    """Tests for the DictDBLogger class."""

    def test_remove_clears_handlers(self) -> None:
        """Test that remove() clears all handlers."""
        test_logger = DictDBLogger("test_remove")
        assert len(test_logger._handlers) > 0
        test_logger.remove()
        assert len(test_logger._handlers) == 0

    def test_add_stream_handler(self) -> None:
        """Test adding a stream handler."""
        test_logger = DictDBLogger("test_add_stream")
        test_logger.remove()

        stream = StringIO()
        test_logger.add(sink=stream, level="INFO")

        test_logger.info("Test message")
        output = stream.getvalue()
        assert "Test message" in output

    def test_add_file_handler(self, tmp_path: Path) -> None:
        """Test adding a file handler."""
        test_logger = DictDBLogger("test_add_file")
        test_logger.remove()

        logfile = tmp_path / "test.log"
        test_logger.add(sink=str(logfile), level="INFO")

        test_logger.info("File test message")
        content = logfile.read_text()
        assert "File test message" in content

    def test_add_json_handler(self) -> None:
        """Test adding a JSON serializing handler."""
        test_logger = DictDBLogger("test_json")
        test_logger.remove()

        stream = StringIO()
        test_logger.add(sink=stream, level="INFO", serialize=True)

        test_logger.info("JSON test")
        output = stream.getvalue()
        data = json.loads(output.strip())
        assert data["message"] == "JSON test"
        assert data["level"] == "INFO"

    def test_bind_returns_bound_logger(self) -> None:
        """Test that bind() returns a BoundLogger."""
        test_logger = DictDBLogger("test_bind")
        bound = test_logger.bind(table="users")
        assert isinstance(bound, BoundLogger)
        assert bound._extra == {"table": "users"}

    def test_log_levels(self) -> None:
        """Test all log levels."""
        test_logger = DictDBLogger("test_levels")
        test_logger.remove()

        stream = StringIO()
        test_logger.add(sink=stream, level="DEBUG")

        test_logger.debug("debug msg")
        test_logger.info("info msg")
        test_logger.warning("warning msg")
        test_logger.error("error msg")
        test_logger.critical("critical msg")

        output = stream.getvalue()
        assert "DEBUG" in output
        assert "INFO" in output
        assert "WARNING" in output
        assert "ERROR" in output
        assert "CRITICAL" in output

    def test_level_filtering(self) -> None:
        """Test that level filtering works."""
        test_logger = DictDBLogger("test_level_filter")
        test_logger.remove()

        stream = StringIO()
        test_logger.add(sink=stream, level="WARNING")

        test_logger.debug("should not appear")
        test_logger.info("should not appear")
        test_logger.warning("should appear")
        test_logger.error("should appear")

        output = stream.getvalue()
        assert "should not appear" not in output
        assert "should appear" in output


class TestGlobalLogger:
    """Tests for the global logger instance."""

    def test_global_logger_exists(self) -> None:
        """Test that the global logger is available."""
        assert logger is not None
        assert isinstance(logger, DictDBLogger)

    def test_global_logger_bind(self) -> None:
        """Test using bind() on the global logger."""
        bound = logger.bind(component="test")
        assert isinstance(bound, BoundLogger)
        assert bound._extra == {"component": "test"}


# ──────────────────────────────────────────────────────────────────────────────
# Integration tests with DictDB
# ──────────────────────────────────────────────────────────────────────────────


def test_configure_logging_no_file(capfd: CaptureFixture[str]) -> None:
    """
    Tests configuring logging with only console output.

    :param capfd: Pytest fixture that captures stdout/stderr.
    :type capfd: _pytest.capture.CaptureFixture
    :return: None
    :rtype: None
    """
    configure_logging(level="DEBUG", console=True, logfile=None)

    # Create the DB to trigger the "Initialized an empty DictDB instance" log
    _ = DictDB()

    # Now retrieve whatever was printed to stdout
    captured = capfd.readouterr().out

    # Verify that the expected log message is in the console output
    assert "Initialized an empty DictDB instance" in captured, (
        "Expected console log about initializing DictDB not found."
    )


def test_configure_logging_with_file(tmp_path: Path) -> None:
    """
    Tests that specifying a logfile writes logs to that file.

    :param tmp_path: A Pytest fixture providing a temporary directory.
    :type tmp_path: pathlib.Path
    :return: None
    :rtype: None
    """
    log_file = tmp_path / "test_dictdb.log"
    configure_logging(level="DEBUG", console=False, logfile=str(log_file))

    _ = DictDB()  # Should produce 'Initialized an empty DictDB instance' in the file

    # Confirm file was created
    assert log_file.exists(), "Log file was not created by configure_logging."

    # Check file contents
    content = log_file.read_text()
    assert "Initialized an empty DictDB instance" in content, (
        "Expected log line not found in the output file."
    )


def test_crud_logging_in_file(tmp_path: Path) -> None:
    """
    Tests that CRUD operations produce the expected logs when directed to a log file.

    :param tmp_path: A Pytest fixture providing a temporary directory.
    :type tmp_path: pathlib.Path
    :return: None
    :rtype: None
    """
    log_file = tmp_path / "crud_test.log"
    configure_logging(level="DEBUG", console=False, logfile=str(log_file))

    db = DictDB()
    db.create_table("users")
    users = db.get_table("users")

    # Insert a record
    users.insert({"id": 1, "name": "Alice"})
    # Select records
    records = users.select()

    # Just confirm the record is present
    assert len(records) == 1, "Expected 1 record in 'users' table."

    # Now read the file and check that it contains the relevant logs
    content = log_file.read_text()

    # Check for expected log lines
    assert "[DictDB] Creating table 'users'" in content, (
        "Did not find expected 'create_table' log line in file."
    )
    assert "[INSERT] Inserting record into 'users'" in content, (
        "Did not find expected 'insert' log line in file."
    )
    assert "[SELECT] Querying 'users'" in content, (
        "Did not find expected 'select' log line in file."
    )


def test_configure_logging_json_output(tmp_path: Path) -> None:
    """Test configuring with JSON output."""
    logfile = tmp_path / "app.json"
    configure_logging(level="INFO", console=False, logfile=str(logfile), json=True)

    _ = DictDB()
    content = logfile.read_text()
    # Get the last non-empty line
    lines = [line for line in content.strip().split("\n") if line]
    data = json.loads(lines[-1])
    assert "level" in data
    assert "message" in data
