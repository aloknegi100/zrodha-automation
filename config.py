"""
Central configuration.

You normally do NOT need to open or edit this file.

Every setting a user changes lives in the plain-text ".env" file (simple
NAME=value lines -- see .env.example and the README). This file just reads
those values and falls back to sensible defaults if one is missing.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _get_float(name, default):
    """Read a decimal setting from .env, or use the default if it's blank/bad."""
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)


def _get_int(name, default):
    """Read a whole-number setting from .env, or use the default."""
    try:
        return int(float(os.getenv(name, default)))
    except (TypeError, ValueError):
        return int(default)


# --- Kite Connect credentials (from .env) ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# --- Optional email alert credentials (from .env) ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --- Risk parameters (from .env, with defaults) ---
MAX_CAPITAL_PER_TRADE_PERCENT = _get_float("MAX_CAPITAL_PER_TRADE_PERCENT", 10)
HARD_STOP_LOSS_PERCENT = _get_float("HARD_STOP_LOSS_PERCENT", 10)
# User enters a positive number in .env (rupees willing to lose); stored negative.
MAX_DAILY_LOSS = -abs(_get_float("MAX_DAILY_LOSS", 5000))
MAX_TRADES_PER_DAY = _get_int("MAX_TRADES_PER_DAY", 5)

# --- Trailing stop ---
TRAIL_START_PERCENT = _get_float("TRAIL_START_PERCENT", 2)
TRAIL_SL_MOVE_PERCENT = _get_float("TRAIL_SL_MOVE_PERCENT", 0.5)

# --- Auto stop-loss placement ---
DEFAULT_SL_PERCENT = _get_float("DEFAULT_SL_PERCENT", 10)

# --- Overnight square-off ---
SQUARE_OFF_HOUR = _get_int("SQUARE_OFF_HOUR", 15)
SQUARE_OFF_MINUTE = _get_int("SQUARE_OFF_MINUTE", 15)

# --- Monitoring cadence (how often the risk sweep runs, in SECONDS) ---
MONITOR_INTERVAL_SECONDS = _get_int("MONITOR_INTERVAL_SECONDS", 30)

# --- SAFETY SWITCH ---------------------------------------------------------
# When True, NO real orders are sent -- every action is only logged.
# Set DRY_RUN=false in .env to go live. This is the single most important
# guard against an automation handling real money.
DRY_RUN = os.getenv("DRY_RUN", "true").strip().lower() not in ("false", "0", "no")
