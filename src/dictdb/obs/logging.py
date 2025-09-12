import sys
from typing import Optional, Protocol, Any

from loguru import logger

__all__ = ["logger", "configure_logging"]


class LogFilter(Protocol):
    def __call__(self, record: Any) -> bool: ...


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
    """
    logger.remove()

    log_filter: Optional[LogFilter] = None
    if sample_debug_every is not None and sample_debug_every > 1:
        counter: dict[str, int] = {"n": 0}

        def _filter(record: dict[str, Any]) -> bool:
            if record["level"].name != "DEBUG":
                return True
            counter["n"] += 1
            return (counter["n"] % sample_debug_every) == 0

        log_filter = _filter

    base_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
        "| <level>{level}</level> | {extra} | <level>{message}</level>"
    )

    if console:
        if log_filter is not None:
            logger.add(
                sink=sys.stdout,
                level=level,
                format=base_format,
                serialize=json,
                filter=log_filter,
            )
        else:
            logger.add(
                sink=sys.stdout,
                level=level,
                format=base_format,
                serialize=json,
            )

    if logfile:
        file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra} | {message}"
        if log_filter is not None:
            logger.add(
                sink=logfile,
                level=level,
                format=file_format,
                serialize=json,
                filter=log_filter,
            )
        else:
            logger.add(
                sink=logfile,
                level=level,
                format=file_format,
                serialize=json,
            )

    logger.bind(component="configure_logging").debug(
        "Logger configured (level={level}, console={console}, logfile={logfile}, json={json}, sample_debug_every={sample})",
        level=level,
        console=console,
        logfile=logfile,
        json=json,
        sample=sample_debug_every,
    )
