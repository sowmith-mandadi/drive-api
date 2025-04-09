"""
Logging configuration for the application.
"""
import logging
import sys

import structlog
from structlog.processors import CallsiteParameter
from structlog.types import Processor


def configure_logging(log_level: str = "INFO") -> structlog.BoundLogger:
    """
    Configure structured logging for the application.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    # Set log level based on environment
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )

    # Configure structlog processors
    processors: list[Processor] = [
        # Add timestamps
        structlog.processors.TimeStamper(fmt="iso"),
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add log level
        structlog.stdlib.add_log_level,
        # Filter log levels
        structlog.stdlib.filter_by_level,
        # Add callsite information (file, line, function)
        structlog.processors.CallsiteParameterAdder(
            parameters={
                CallsiteParameter.FILENAME,
                CallsiteParameter.LINENO,
                CallsiteParameter.FUNC_NAME,
            }
        ),
        # Format exception
        structlog.processors.format_exc_info,
        # Format as JSON
        structlog.processors.JSONRenderer(),
    ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create and return logger
    return structlog.get_logger("app")
