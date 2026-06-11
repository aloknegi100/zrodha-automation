"""
Tiny logging helper. Writes to both the console and a daily log file so you
have an audit trail of every decision the engine made.
"""
import logging
import os
from datetime import datetime

_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

_log_file = os.path.join(_LOG_DIR, f"trading_{datetime.now():%Y%m%d}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(_log_file),
        logging.StreamHandler(),
    ],
)

_logger = logging.getLogger("zerodha-automation")


def log(message, level="info"):
    """Log a message at the given level ('info', 'warning', 'error')."""
    getattr(_logger, level, _logger.info)(message)
