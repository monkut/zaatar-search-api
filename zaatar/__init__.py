import logging
import os
import sys

__version__ = "0.1.0"

_DEFAULT_LOG_LEVEL = "DEBUG"
_LOG_LEVEL = os.getenv("LOG_LEVEL", _DEFAULT_LOG_LEVEL).upper()
_LEVEL = getattr(logging, _LOG_LEVEL, logging.DEBUG)

logging.basicConfig(
    stream=sys.stdout,
    level=_LEVEL,
    force=True,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(funcName)s: %(message)s",
)

# Suppress specific loggers to reduce noise
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
