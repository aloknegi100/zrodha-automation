"""
Trailing stop logic.

  * Mistake 4 - Booking profits too early -> trail_profit()

Once a position is in profit by TRAIL_START_PERCENT, the stop-loss is ratcheted
up to TRAIL_SL_MOVE_PERCENT below the live price and only ever moves in the
favourable direction. The computed level is tracked in-memory and logged; wire
it into kite.modify_order() on your live SL once you've validated the levels.
"""
import config
from logger import log
from order_utils import get_ltp

# Best (highest for longs) trailing SL seen per symbol during this run.
_trailing_levels = {}


def get_trailing_level(symbol):
    """Return the current trailing SL tracked for a symbol, or None."""
    return _trailing_levels.get(symbol)


def trail_profit(kite):
    """Mistake 4: ratchet the stop-loss up as an in-profit position runs."""
    positions = kite.positions()["net"]

    for position in positions:
        qty = position["quantity"]
        if qty <= 0:
            continue  # only trail long positions in this basic version

        symbol = position["tradingsymbol"]
        entry_price = position["average_price"]
        current_price = get_ltp(kite, position["exchange"], symbol)
        if current_price is None:
            continue

        profit_percent = (current_price - entry_price) / entry_price * 100
        if profit_percent < config.TRAIL_START_PERCENT:
            continue

        new_sl = round(current_price * (1 - config.TRAIL_SL_MOVE_PERCENT / 100), 1)
        prev_sl = _trailing_levels.get(symbol)

        # Only ratchet upward -- never loosen a trailing stop.
        if prev_sl is None or new_sl > prev_sl:
            _trailing_levels[symbol] = new_sl
            log(
                f"TRAILING SL UPDATED for {symbol}: {new_sl} "
                f"(profit {profit_percent:.2f}%, price {current_price})"
            )
