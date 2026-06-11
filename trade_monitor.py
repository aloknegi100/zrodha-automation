"""
Open-position monitoring.

  * Mistake 2 - No stop-loss            -> ensure_sl_exists()
  * Mistake 6 - Holding losers          -> emotional_loss_protection()

Both handle long AND short positions (the original PDF assumed long only).
"""
import config
from logger import log
from order_utils import place_order, get_ltp, square_off_position


def ensure_sl_exists(kite):
    """Mistake 2: every open position must have a stop-loss order."""
    positions = kite.positions()["net"]
    orders = kite.orders()

    for position in positions:
        qty = position["quantity"]
        if qty == 0:
            continue

        symbol = position["tradingsymbol"]
        sl_exists = any(
            o["tradingsymbol"] == symbol
            and o["order_type"] in ("SL", "SL-M")
            and o["status"] in ("OPEN", "TRIGGER PENDING")
            for o in orders
        )
        if sl_exists:
            continue

        # Long -> SL below entry; short -> SL above entry.
        direction = 1 if qty > 0 else -1
        sl_factor = 1 - direction * (config.DEFAULT_SL_PERCENT / 100)
        trigger_price = round(position["average_price"] * sl_factor, 1)
        transaction_type = "SELL" if qty > 0 else "BUY"

        place_order(
            kite,
            variety="regular",
            exchange=position["exchange"],
            tradingsymbol=symbol,
            transaction_type=transaction_type,
            quantity=abs(qty),
            order_type="SL-M",
            trigger_price=trigger_price,
            product=position["product"],
        )
        log(f"SL CREATED FOR {symbol} @ trigger {trigger_price}")


def emotional_loss_protection(kite):
    """Mistake 6: hard stop -- force a market exit if the price breaches it."""
    positions = kite.positions()["net"]

    for position in positions:
        qty = position["quantity"]
        if qty == 0:
            continue

        symbol = position["tradingsymbol"]
        entry_price = position["average_price"]
        direction = 1 if qty > 0 else -1
        hard_sl = entry_price * (1 - direction * (config.HARD_STOP_LOSS_PERCENT / 100))

        ltp = get_ltp(kite, position["exchange"], symbol)
        if ltp is None:
            continue

        breached = (qty > 0 and ltp <= hard_sl) or (qty < 0 and ltp >= hard_sl)
        if breached:
            square_off_position(kite, position, order_type="MARKET")
            log(f"HARD SL EXIT EXECUTED: {symbol} @ {ltp} (hard_sl {hard_sl:.2f})")
