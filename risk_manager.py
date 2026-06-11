"""
Pre-trade risk checks.

  * Mistake 1 - Risking too much on one trade  -> validate_position_size()
  * Mistake 5 - Overtrading                    -> check_trade_limit()
"""
import config
from logger import log


def validate_position_size(balance, quantity, price):
    """Mistake 1: reject any trade whose value exceeds the capital cap."""
    max_allowed = balance * (config.MAX_CAPITAL_PER_TRADE_PERCENT / 100)
    trade_value = quantity * price

    if trade_value > max_allowed:
        log(
            f"ORDER REJECTED: trade value {trade_value:.2f} exceeds max "
            f"allowed {max_allowed:.2f} ({config.MAX_CAPITAL_PER_TRADE_PERCENT}% of "
            f"{balance:.2f})"
        )
        return False

    log(f"POSITION SIZE APPROVED: {trade_value:.2f} <= {max_allowed:.2f}")
    return True


def check_trade_limit(kite):
    """Mistake 5: block new trades once the daily count is reached."""
    orders = kite.orders()
    completed = [o for o in orders if o["status"] == "COMPLETE"]
    total_trades = len(completed)

    if total_trades >= config.MAX_TRADES_PER_DAY:
        log(f"TRADE LIMIT REACHED: {total_trades}/{config.MAX_TRADES_PER_DAY}")
        return False

    log(f"Trade count OK: {total_trades}/{config.MAX_TRADES_PER_DAY}")
    return True
