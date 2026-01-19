"""
Custom logging module for DictDB.

Provides a loguru-compatible API using Python's standard logging module.
This eliminates the external dependency while maintaining the same interface.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TextIO, Union

__all__ = ["logger", "configure_logging"]


class SampleDebugFilter(logging.Filter):
    """Filter that passes only 1 out of every N DEBUG messages."""

    def __init__(self, every_n: int) -> None:
        super().__init__()
        self._every_n = every_n
        self._counter = 0

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno != logging.DEBUG:
            return True
        self._counter += 1
        return (self._counter % self._every_n) == 0


class DictDBFormatter(logging.Formatter):
    """Formatter with color support and extra metadata display."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    TIME_COLOR = "\033[32m"  # Green for timestamp

    def __init__(self, use_colors: bool = True) -> None:
        super().__init__()
        self._use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]
        level = record.levelname
        message = record.getMessage()

        # Get extra metadata
        extra: Dict[str, Any] = getattr(record, "extra", {})

        # Interpolate {key} placeholders in message with extra values
        if extra:
            try:
                message = message.format(**extra)
            except (KeyError, IndexError):
                pass  # Keep original message if interpolation fails

        # Format extra as key=value pairs
        extra_str = " ".join(f"{k}={v}" for k, v in extra.items()) if extra else ""

        if self._use_colors:
            level_color = self.COLORS.get(level, "")
            return (
                f"{self.TIME_COLOR}{timestamp}{self.RESET} | "
                f"{level_color}{level:8}{self.RESET} | "
                f"{extra_str + ' | ' if extra_str else ''}"
                f"{level_color}{message}{self.RESET}"
            )
        else:
            return (
                f"{timestamp} | {level:8} | "
                f"{extra_str + ' | ' if extra_str else ''}"
                f"{message}"
            )


class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON-serialized log records."""

    def format(self, record: logging.LogRecord) -> str:
        extra: Dict[str, Any] = getattr(record, "extra", {})
        message = record.getMessage()

        # Interpolate placeholders
        if extra:
            try:
                message = message.format(**extra)
            except (KeyError, IndexError):
                pass

        log_data = {
            "time": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": message,
            "extra": extra,
        }
        return json.dumps(log_data)


class _CallableSinkHandler(logging.Handler):
    """Handler that calls a function with the formatted log message."""

    def __init__(self, sink_fn: Callable[[str], None]) -> None:
        super().__init__()
        self._sink_fn = sink_fn
        self.setFormatter(DictDBFormatter(use_colors=False))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._sink_fn(msg)
        except Exception:
            self.handleError(record)


class BoundLogger:
    """Logger wrapper that carries extra metadata for contextual logging."""

    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]) -> None:
        self._logger = logger
        self._extra = extra

    def bind(self, **kwargs: Any) -> BoundLogger:
        """Create a new BoundLogger with additional metadata."""
        return BoundLogger(self._logger, {**self._extra, **kwargs})

    def _log(self, log_level: int, msg: str, **kwargs: Any) -> None:
        merged_extra = {**self._extra, **kwargs}
        record = self._logger.makeRecord(
            self._logger.name,
            log_level,
            "(unknown)",
            0,
            msg,
            (),
            None,
        )
        record.extra = merged_extra
        self._logger.handle(record)

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.CRITICAL, msg, **kwargs)


class DictDBLogger:
    """
    Main logger with loguru-compatible API.

    Provides bind(), remove(), add() methods and direct logging methods.
    """

    def __init__(self, name: str = "dictdb") -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)  # Allow all levels, handlers filter
        self._handlers: List[logging.Handler] = []
        self._handler_id = 0

        # Add a default stderr handler
        self._add_default_handler()

    def _add_default_handler(self) -> None:
        """Add default handler writing to stderr."""
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(DictDBFormatter(use_colors=sys.stderr.isatty()))
        self._logger.addHandler(handler)
        self._handlers.append(handler)

    def bind(self, **kwargs: Any) -> BoundLogger:
        """Create a BoundLogger with the given metadata."""
        return BoundLogger(self._logger, kwargs)

    def remove(self) -> None:
        """Remove all handlers from the logger."""
        for handler in self._handlers:
            self._logger.removeHandler(handler)
            handler.close()
        self._handlers.clear()

    def add(
        self,
        sink: Union[str, TextIO, Callable[[str], None]],
        *,
        level: str = "DEBUG",
        format: Optional[str] = None,  # noqa: A002 - loguru compat
        serialize: bool = False,
        filter: Optional[Callable[[logging.LogRecord], bool]] = None,  # noqa: A002
    ) -> int:
        """
        Add a new handler to the logger.

        :param sink: File path, file-like object (e.g., sys.stdout), or callable.
        :param level: Minimum log level for this handler.
        :param format: Ignored (kept for API compatibility).
        :param serialize: If True, output JSON format.
        :param filter: Optional filter function.
        :return: Handler ID.
        """
        handler: logging.Handler
        use_colors = False

        # Determine sink type
        if callable(sink) and not hasattr(sink, "write"):
            # Sink is a callable function (loguru-style)
            handler = _CallableSinkHandler(sink)
        elif isinstance(sink, str):
            handler = logging.FileHandler(sink)
        else:
            handler = logging.StreamHandler(sink)
            use_colors = hasattr(sink, "isatty") and sink.isatty()

        # Set level
        numeric_level = getattr(logging, level.upper(), logging.DEBUG)
        handler.setLevel(numeric_level)

        # Set formatter
        if serialize:
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(DictDBFormatter(use_colors=use_colors))

        # Add filter if provided
        if filter is not None:

            class CallableFilter(logging.Filter):
                def __init__(self, fn: Callable[[Any], bool]) -> None:
                    super().__init__()
                    self._fn = fn

                def filter(self, record: logging.LogRecord) -> bool:
                    # Create a loguru-compatible record dict
                    record_dict = {
                        "level": type("Level", (), {"name": record.levelname})(),
                        "message": record.getMessage(),
                        "extra": getattr(record, "extra", {}),
                    }
                    return self._fn(record_dict)

            handler.addFilter(CallableFilter(filter))

        self._logger.addHandler(handler)
        self._handlers.append(handler)
        self._handler_id += 1
        return self._handler_id

    def _log(self, log_level: int, msg: str, **kwargs: Any) -> None:
        record = self._logger.makeRecord(
            self._logger.name,
            log_level,
            "(unknown)",
            0,
            msg,
            (),
            None,
        )
        record.extra = kwargs
        self._logger.handle(record)

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.CRITICAL, msg, **kwargs)


# Global logger instance
logger = DictDBLogger()


def configure_logging(
    level: str = "INFO",
    console: bool = True,
    logfile: Optional[str] = None,
    *,
    json: bool = False,
    sample_debug_every: Optional[int] = None,
) -> None:
    """
    Configure logging for DictDB.

    :param level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    :param console: If True, log to stdout.
    :param logfile: If provided, also log to this file.
    :param json: If True, output logs in JSON format.
    :param sample_debug_every: If set, only log 1 out of every N DEBUG messages.
    """
    logger.remove()

    # Build filter if sampling is requested
    log_filter: Optional[Callable[[Any], bool]] = None
    if sample_debug_every is not None and sample_debug_every > 1:
        counter = {"n": 0}

        def _filter(record: Any) -> bool:
            if record["level"].name != "DEBUG":
                return True
            counter["n"] += 1
            return (counter["n"] % sample_debug_every) == 0

        log_filter = _filter

    if console:
        logger.add(
            sink=sys.stdout,
            level=level,
            serialize=json,
            filter=log_filter,
        )

    if logfile:
        logger.add(
            sink=logfile,
            level=level,
            serialize=json,
            filter=log_filter,
        )

    logger.bind(component="configure_logging").debug(
        "Logger configured (level={level}, console={console}, logfile={logfile}, "
        "json={json}, sample_debug_every={sample})",
        level=level,
        console=console,
        logfile=logfile,
        json=json,
        sample=sample_debug_every,
    )
