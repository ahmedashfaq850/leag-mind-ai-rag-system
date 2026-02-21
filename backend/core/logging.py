import logging
import os
from rich.logging import RichHandler


import logging
import os
from rich.logging import RichHandler

def setup_logging(level: str = "INFO") -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)