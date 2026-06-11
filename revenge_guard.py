"""
Daily-loss circuit breaker.

  * Mistake 3 - Revenge trading after losses -> revenge_guard()

When the day's P&L breaches MAX_DAILY_LOSS the engine:
  1. engages a cooldown lock (blocks every new order via place_disciplined_order),
  2. cancels all pending orders, and
  3. squares off all live positions.

The lock is in-memory: it clears on restart, or call reset_lock() yourself
(e.g. an OTP-gated unlock after market hours) to release it deliberately.
"""
import config
from logger import log
from order_utils import square_off_position

_locked = False


def is_locked():
    """True while the revenge-trading cooldown lock is engaged."""
    return _locked


def reset_lock():
    """Manually release the cooldown lock (e.g. after market hours / OTP)."""
    global _locked
    _locked = False
    log("Revenge-trading lock RESET.")


def revenge_guard(kite):
    """Mistake 3: stop trading and flatten the book on the daily loss limit.

    Returns True if trading may continue, False if the limit has been hit.
    """
    global _locked

    day_positions = kite.positions()["day"]
    total_pnl = sum(p["pnl"] for p in day_positions)
    log(f"Day P&L: {total_pnl:.2f} (limit {config.MAX_DAILY_LOSS})")

    if total_pnl > config.MAX_DAILY_LOSS and not _locked:
        return True

    # Either the limit is breached now, or the lock is already engaged.
    if not _locked:
        _locked = True
        log("TRADING BLOCKED: daily loss limit hit. Cooldown lock engaged.")

    # Cancel any pending orders so nothing new can fill.
    try:
        for o in kite.orders():
            if o["status"] in ("OPEN", "TRIGGER PENDING"):
                if not config.DRY_RUN:
                    kite.cancel_order(variety=o["variety"], order_id=o["order_id"])
                log(f"Cancelled pending order {o['order_id']} ({o['tradingsymbol']})")
    except Exception as e:
        log(f"Order cancellation error: {e}", level="error")

    # Flatten every live position.
    for position in kite.positions()["net"]:
        if position["quantity"] != 0:
            square_off_position(kite, position, order_type="MARKET")
    log("ALL POSITIONS CLOSED (revenge guard).")

    return False
