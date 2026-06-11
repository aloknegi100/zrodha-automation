"""
Option-move probability check.

  * Mistake 7 - Buying options that never moved enough -> expected_move_validation()

Compares the move the underlying is statistically expected to make (from its
implied volatility and time to expiry) against the move the option actually
needs to make to hit your target. If the required move is bigger than the
expected move, it's a low-probability trade.
"""
from math import sqrt

from logger import log


def expected_move_validation(
    spot_price,
    implied_volatility,   # decimal, e.g. 0.18 for 18%
    days_to_expiry,
    option_entry_price,
    option_target_price,
    option_delta,
):
    """Mistake 7: validate that the target move is statistically plausible.

    Returns True for a valid trade, False for a low-probability one.
    """
    if option_delta == 0:
        log("Cannot validate: option_delta is 0.", level="error")
        return False

    expected_move = spot_price * implied_volatility * sqrt(days_to_expiry / 365)
    required_move = (option_target_price - option_entry_price) / option_delta

    log(f"EXPECTED MOVE: {expected_move:.2f}")
    log(f"REQUIRED MOVE: {required_move:.2f}")

    if expected_move >= required_move:
        log("TRADE VALID")
        return True

    log("LOW PROBABILITY TRADE -- POSITION SHOULD BE CLOSED")
    return False
