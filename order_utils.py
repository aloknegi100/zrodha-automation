"""
Order helpers shared across the engine.

Every real order goes through place_order(), which honours config.DRY_RUN.
While DRY_RUN is True nothing is sent to the exchange -- the intended order
is logged instead, so you can watch the engine make decisions safely.
"""
import config
from logger import log

# Statuses for orders that are still live in the book and can be cancelled.
# "OPEN" also covers partially-filled orders (their unfilled remainder).
OPEN_ORDER_STATUSES = ("OPEN", "TRIGGER PENDING", "AMO REQ RECEIVED")


def place_order(kite, **params):
    """Place an order, respecting the DRY_RUN safety switch."""
    if config.DRY_RUN:
        log(f"[DRY_RUN] Would place order -> {params}")
        return None
    try:
        order_id = kite.place_order(**params)
        log(f"ORDER PLACED ({order_id}) -> {params}")
        return order_id
    except Exception as e:
        log(f"ORDER FAILED: {e} -> {params}", level="error")
        return None


def get_open_orders(kite):
    """Return orders still live in the book (pending / not fully filled)."""
    try:
        return [o for o in kite.orders() if o["status"] in OPEN_ORDER_STATUSES]
    except Exception as e:
        log(f"Could not fetch orders: {e}", level="error")
        return []


def cancel_order(kite, variety, order_id):
    """Cancel a pending order, respecting the DRY_RUN safety switch."""
    if config.DRY_RUN:
        log(f"[DRY_RUN] Would cancel order -> {order_id} ({variety})")
        return None
    try:
        kite.cancel_order(variety=variety, order_id=order_id)
        log(f"ORDER CANCELLED ({order_id})")
        return order_id
    except Exception as e:
        log(f"CANCEL FAILED: {e} -> {order_id}", level="error")
        return None


def get_ltp(kite, exchange, tradingsymbol):
    """Return the last traded price for an instrument, or None on failure.

    Note: the exchange is taken from the position itself (e.g. NFO for
    options), not hardcoded to NSE -- this is the fix for the original PDF bug.
    """
    key = f"{exchange}:{tradingsymbol}"
    try:
        return kite.ltp(key)[key]["last_price"]
    except Exception as e:
        log(f"LTP fetch failed for {key}: {e}", level="error")
        return None


def square_off_position(kite, position, order_type="MARKET", price=None,
                        trigger_price=None):
    """Place an opposite order to flatten a position (works long or short)."""
    qty = position["quantity"]
    if qty == 0:
        return None

    transaction_type = "SELL" if qty > 0 else "BUY"
    params = dict(
        variety="regular",
        exchange=position["exchange"],
        tradingsymbol=position["tradingsymbol"],
        transaction_type=transaction_type,
        quantity=abs(qty),
        order_type=order_type,
        product=position["product"],
    )
    if price is not None:
        params["price"] = price
    if trigger_price is not None:
        params["trigger_price"] = trigger_price
    return place_order(kite, **params)


def get_open_positions(kite):
    """Return positions you actually hold right now (quantity != 0)."""
    try:
        return [p for p in kite.positions()["net"] if p["quantity"] != 0]
    except Exception as e:
        log(f"Could not fetch positions: {e}", level="error")
        return []


def place_disciplined_order(kite, balance, quantity, price, **params):
    """Run every pre-trade guard, then place the order if all pass.

    Combines Mistake 1 (position size), 3 (revenge-trading lock) and
    5 (daily trade-count limit) so a new entry can never bypass them.
    Imports are local to avoid a circular import with revenge_guard.
    """
    import revenge_guard
    import risk_manager

    if revenge_guard.is_locked():
        log("ORDER BLOCKED: revenge-trading cooldown lock is active.")
        return None
    if not risk_manager.check_trade_limit(kite):
        return None
    if not risk_manager.validate_position_size(balance, quantity, price):
        return None

    return place_order(kite, quantity=quantity, **params)
