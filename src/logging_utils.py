"""Logging utilities for setting up consistent logging across the project.

Usage:
    from src.logging_utils import setup_logging

    # In main script
    setup_logging(level="DEBUG")

    # In other modules
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Processing item: %s", item_id)
"""

import logging
from datetime import datetime
from pathlib import Path


def generate_log_filename(log_dir: str | Path = "logs") -> Path:
    """Generate a timestamped log filename.

    Args:
        log_dir: Directory for log files. Created if doesn't exist.

    Returns:
        Path to the log file, e.g., logs/29012026_143052.log
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    return log_dir / f"{timestamp}.log"


def setup_logging(
    level: str = "INFO",
    output_file: str | Path | None = None,
    log_dir: str | Path = "logs",
) -> None:
    """Configure root logger with file and console handlers.

    Call once in the main function. In other modules use:
        logger = logging.getLogger(__name__)

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        output_file: Explicit log file path. If None, generates timestamped filename.
        log_dir: Directory for auto-generated log files.

    Raises:
        ValueError: If level is not a valid logging level.

    Example:
        >>> setup_logging(level="DEBUG")
        >>> setup_logging(output_file="logs/my_run.log")
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid logging level: {level}")

    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    logger.handlers.clear()

    if output_file is None:
        output_file = generate_log_filename(log_dir)
    else:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

    formatter_file = logging.Formatter(
        '%(asctime)s\t[%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    formatter_console = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s'
    )

    file_handler = logging.FileHandler(output_file, encoding='utf-8')
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter_file)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter_console)
    logger.addHandler(console_handler)

    logger.info("Initialized logging. Log file: %s", output_file)
