class DictDBError(Exception):
    """Base exception class for DictDB-related errors."""
    pass

class DuplicateKeyError(DictDBError):
    """Exception raised when a record with a duplicate primary key is inserted."""
    pass

class RecordNotFoundError(DictDBError):
    """Exception raised when no records match the query criteria."""
    pass

class SchemaValidationError(DictDBError):
    """Exception raised when a record does not conform to the table schema."""
    pass
