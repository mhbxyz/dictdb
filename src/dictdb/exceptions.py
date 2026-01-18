class DictDBError(Exception):
    """
    Base exception class for DictDB-related errors.
    """


class DuplicateKeyError(DictDBError):
    """
    Exception raised when a record with a duplicate primary key is inserted.
    """


class DuplicateTableError(DictDBError):
    """
    Exception raised when a table with the same name already exists.
    """


class RecordNotFoundError(DictDBError):
    """
    Exception raised when no records match the query criteria.
    """


class TableNotFoundError(DictDBError):
    """
    Exception raised when a table does not exist.
    """


class SchemaValidationError(DictDBError):
    """
    Exception raised when a record does not conform to the table schema.
    """
