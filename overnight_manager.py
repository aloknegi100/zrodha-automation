"""
Overnight-risk square-off.

  * Mistake 8 - Losing money in overnight trades -> square_off_all()

Run near 15:15. Every open position is flattened with an intraday MIS market
order so nothing carries to the next session. Squaring off with PRODUCT_MIS
also avoids the overnight margin of a carried NRML/CNC position.
"""
import config
from logger import log
from order_utils import place_order


def square_off_all(kite):
    """Mistake 8: close every open position before the market closes."""
    positions = kite.positions()["net"]
    closed = 0

    for position in positions:
        qty = position["quantity"]
        if qty == 0:
            continue

        transaction_type = "SELL" if qty > 0 else "BUY"
        place_order(
            kite,
            variety=kite.VARIETY_REGULAR,
            exchange=position["exchange"],
            tradingsymbol=position["tradingsymbol"],
            transaction_type=transaction_type,
            quantity=abs(qty),
            product=kite.PRODUCT_MIS,
            order_type=kite.ORDER_TYPE_MARKET,
            validity=kite.VALIDITY_DAY,
        )
        closed += 1

    log(f"Overnight square-off complete. {closed} position(s) closed.")
