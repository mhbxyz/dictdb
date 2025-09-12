import sys
from typing import Optional, Callable

from loguru import logger

__all__ = ["logger", "configure_logging"]


def configure_logging(
    level: str = "INFO",
    console: bool = True,
    logfile: Optional[str] = None,
    *,
    json: bool = False,
    sample_debug_every: Optional[int] = None,
) -> None:
    """
    Configures Loguru logging for the DictDB.

    :param level: The minimum log level for messages (e.g., "DEBUG", "INFO", "WARNING", etc.).
    :type level: str
    :param console: If True, logs are printed to stdout.
    :type console: bool
    :param logfile: If provided, logs are also written to the given file path.
    :type logfile: str or None
    :param json: If True, logs are serialized as JSON (structured logs).
    :type json: bool
    :param sample_debug_every: If provided and > 1, emit only one DEBUG message out of N to reduce verbosity.
    :type sample_debug_every: Optional[int]
    :return: None
    :rtype: None
    """
    # Remove any pre-existing log handlers so we don't duplicate logs.
    logger.remove()

    # Optional sampling filter for DEBUG-level verbosity.
    log_filter: Optional[Callable[[dict], bool]] = None
    if sample_debug_every is not None and sample_debug_every > 1:
        counter = {"n": 0}

        def _filter(record: dict) -> bool:
            if record["level"].name != "DEBUG":
                return True
            counter["n"] += 1
            return (counter["n"] % sample_debug_every) == 0

        log_filter = _filter

    # Base format includes structured context via {extra}
    base_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
        "| <level>{level}</level> | {extra} | <level>{message}</level>"
    )

    # Add a console sink if desired.
    if console:
        logger.add(
            sink=sys.stdout,
            level=level,
            format=None if json else base_format,
            serialize=json,
            filter=log_filter,
        )

    # Optionally add a file sink.
    if logfile:
        logger.add(
            sink=logfile,
            level=level,
            format=None if json else "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra} | {message}",
            serialize=json,
            filter=log_filter,
        )

    logger.bind(component="configure_logging").debug(
        "Logger configured (level={level}, console={console}, logfile={logfile}, json={json}, sample_debug_every={sample})",
        level=level,
        console=console,
        logfile=logfile,
        json=json,
        sample=sample_debug_every,
    )
