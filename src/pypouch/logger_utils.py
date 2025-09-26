from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InfoLevelFormatter(logging.Formatter):
    COLORS = {
        "STEP": "\033[1;35m",  # Purple
        "DATAIO": "\033[1;33m",  # Orange
        "RESULT": "\033[32m",  # Green
        "WARNING": "\033[31m",  # Red
        "PROCESS": "\033[1;36m",  # Cyan
        "DEFAULT": "\033[0m",  # Default
    }
    RESET = "\033[0m"

    def format(self, record):
        # Set color based on log level
        if record.levelname == "WARNING":
            color = self.COLORS["WARNING"]
        else:
            # Default category
            category = getattr(record, "category", "DEFAULT")
            color = self.COLORS.get(category, self.COLORS["DEFAULT"])

        # Normal format
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def setup_logger(log_folder: str, run_mode: str = "TEST") -> None:
    """
    Set up logger to output logs to both file and console

    Args:
        - log_folder (str): Log folder path
        - run_mode (str): Run mode, supports "PROD" (production environment), "REGR" (regression test environment), etc. Different modes have different log output behaviors
    """
    if run_mode == "REGR":
        return

    os.makedirs(Path(log_folder), exist_ok=True)  # Ensure log directory exists
    log_filename = Path(log_folder).joinpath(f"logger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log").absolute()
    file_handler = logging.FileHandler(log_filename, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    if run_mode == "PROD":
        stream_formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s", "%Y-%m-%d %H:%M:%S")
    else:
        stream_formatter = InfoLevelFormatter("%(asctime)s - %(levelname)-8s - %(message)s", "%Y-%m-%d %H:%M:%S")

    file_formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    stream_handler.setFormatter(stream_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            return
        logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
