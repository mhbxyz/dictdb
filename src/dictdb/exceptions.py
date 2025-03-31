class DictDBError(Exception):
    """
    Base exception class for DictDB-related errors.
    """


class DuplicateKeyError(DictDBError):
    """
    Exception raised when a record with a duplicate primary key is inserted.
    """


class RecordNotFoundError(DictDBError):
    """
    Exception raised when no records match the query criteria.
    """


class SchemaValidationError(DictDBError):
    """
    Exception raised when a record does not conform to the table schema.
    """

class TransactionError(DictDBError):
    """
    Exception raised when there is an error in transaction management.
    """