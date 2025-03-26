# dictdb/logging.py

import sys
from loguru import logger


def configure_logging(level: str = "INFO", console: bool = True, logfile: str = None) -> None:
    """
    Configures Loguru logging for the DictDB.

    Args:
        level: The minimum log level for messages (e.g. "DEBUG", "INFO", "WARNING", etc.).
        console: If True, logs will be printed to stdout.
        logfile: If provided, logs will also be written to the given file path.
    """
    # Remove any pre-existing log handlers so we don't duplicate logs.
    logger.remove()

    # Add a console sink if desired.
    if console:
        logger.add(
            sink=sys.stdout,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
                   "| <level>{level}</level> | <level>{message}</level>"
        )

    # Optionally add a file sink.
    if logfile:
        logger.add(
            sink=logfile,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )

    logger.debug("Loguru logger configured with level='%s', console=%s, logfile=%s", level, console, logfile)
