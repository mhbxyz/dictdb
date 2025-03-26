import os

from dictdb import DictDB, configure_logging


def test_configure_logging_no_file(capfd):
    """
    Test configuring logging (console only) and check logs in captured stdout.
    """
    configure_logging(level="DEBUG", console=True, logfile=None)

    # Create the DB to trigger the "Initialized an empty DictDB instance" log
    _ = DictDB()

    # Now retrieve whatever was printed to stdout
    captured = capfd.readouterr().out

    # Verify that the expected log message is in the console output
    assert "Initialized an empty DictDB instance" in captured, \
        "Expected console log about initializing DictDB not found."


def test_configure_logging_with_file(tmp_path):
    """
    Test that specifying a logfile writes logs to that file.
    We do not specify console=True, so no console logs are used in this test.
    """
    log_file = tmp_path / "test_dictdb.log"
    configure_logging(level="DEBUG", console=False, logfile=str(log_file))

    _ = DictDB()  # Should produce 'Initialized an empty DictDB instance' in the file

    # Confirm file was created
    assert log_file.exists(), "Log file was not created by configure_logging."

    # Check file contents
    content = log_file.read_text()
    assert "Initialized an empty DictDB instance" in content, \
        "Expected log line not found in the output file."


def test_crud_logging_in_file(tmp_path):
    """
    Test that CRUD operations produce the expected logs. We direct them to a log file,
    then we read that file to verify the logs.
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
    assert "[DictDB] Creating table 'users'" in content, \
        "Did not find expected 'create_table' log line in file."
    assert "[INSERT] Attempting to insert record into 'users'" in content, \
        "Did not find expected 'insert' log line in file."
    assert "[SELECT] From table 'users'" in content, \
        "Did not find expected 'select' log line in file."
