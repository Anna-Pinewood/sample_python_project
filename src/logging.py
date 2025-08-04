import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union


def generate_log_filename(log_dir: Union[str, Path] = "logs") -> Path:
    """Returns a path to a log file with a timestamp.
    e.g. logs/20082025_120000.log
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    return log_dir / f"{timestamp}.log"


def setup_logging(
    level: str = "INFO",
    output_file: str | Path | None = None,
    log_dir: str | Path = "logs"
):
    """Call it once in the main function.
    In others places use logging.getLogger(__name__)
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Неверный уровень логгирования: {level}")

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

    logger.info(f"Initalized logging. Log file: {output_file}")
