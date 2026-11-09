"""
Centralized logging subsystem for OS Resource Management Simulator.
Writes system audit entries, execution events, warnings, and errors to logs/activity.log.
"""

import logging
from pathlib import Path
from typing import Optional

_LOGGER_INSTANCE: Optional[logging.Logger] = None


def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """
    Initializes and configures the singleton application logger.
    Ensures safe creation of log directory and prevents duplicate handlers.
    """
    global _LOGGER_INSTANCE
    if _LOGGER_INSTANCE is not None:
        return _LOGGER_INSTANCE

    if log_file is None:
        project_root = Path(__file__).resolve().parent.parent
        log_path = project_root / "logs" / "activity.log"
    else:
        log_path = Path(log_file)

    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("OSSimulator")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(str(log_path), mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _LOGGER_INSTANCE = logger
    return logger


def get_logger() -> logging.Logger:
    """Returns active logger instance, initializing default if not already initialized."""
    global _LOGGER_INSTANCE
    if _LOGGER_INSTANCE is None:
        return setup_logger()
    return _LOGGER_INSTANCE
