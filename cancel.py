"""
cancel.py  --  cancel a pending (not-yet-filled) order.

Run it, pick the order, confirm:

    source .venv/bin/activate
    python cancel.py

Why this exists: a LIMIT order that hasn't filled is NOT a position -- you
don't own anything yet, so you *cancel* it rather than sell it. (Selling
instead would open a brand-new opposite position.) This lists every order
still live in your order book and lets you cancel one by number.

While DRY_RUN=true in your .env, this only PRINTS what it would do -- no order
is actually cancelled. Set DRY_RUN=false to cancel for real.
"""
import sys

import config
from kite_client import get_kite
from order_utils import cancel_order, get_open_orders
from trade import ask


def describe(order):
    """One-line summary of a pending order for the chooser list."""
    price = order.get("price") or order.get("trigger_price") or 0
    filled = order.get("filled_quantity", 0)
    qty = order.get("quantity", 0)
    fill_note = f"  ({filled}/{qty} already filled)" if filled else ""
    return (
        f"{order['transaction_type']} {qty} x {order['tradingsymbol']} "
        f"({order['exchange']})  {order['order_type']} @ {price}  "
        f"[{order['status']}]{fill_note}"
    )


def main():
    print("\n" + "=" * 55)
    print("  CANCEL A PENDING ORDER")
    print("=" * 55)
    if config.DRY_RUN:
        print("  MODE: PRACTICE (DRY_RUN=true) -- nothing is really cancelled.")
    else:
        print("  MODE: *** LIVE *** -- this cancels a REAL order!")
    print("=" * 55 + "\n")

    kite = get_kite()

    orders = get_open_orders(kite)
    if not orders:
        print("You have no pending orders to cancel.")
        print("(Only a not-yet-filled order can be cancelled. An order that has")
        print(" filled is a position -- exit it with a SELL/BUY in trade.py.)")
        return

    print("Your pending orders:\n")
    for i, order in enumerate(orders, start=1):
        print(f"  {i}. {describe(order)}")
    print()

    choices = [str(i) for i in range(1, len(orders) + 1)] + ["Q"]
    choice = ask("Cancel which number? (Q to quit)", options=choices)
    if choice == "Q":
        print("Nothing cancelled.")
        return

    order = orders[int(choice) - 1]

    if order.get("filled_quantity", 0):
        print(f"\n  NOTE: {order['filled_quantity']} share(s) already filled. "
              "Cancelling removes only the")
        print("        unfilled remainder; the filled part is a real position you")
        print("        still need to exit with a SELL/BUY.")

    confirm = ask(f"Cancel the order for {order['tradingsymbol']}?",
                  options=["YES", "NO"], default="NO",
                  shortcuts={"Y": "YES", "N": "NO"})
    if confirm != "YES":
        print("Nothing cancelled.")
        return

    result = cancel_order(kite, variety=order["variety"], order_id=order["order_id"])

    print("\n" + "=" * 55)
    if config.DRY_RUN:
        print("  PRACTICE MODE: cancel was simulated only (see the log above).")
    elif result:
        print(f"  ORDER CANCELLED. Order id: {order['order_id']}")
    else:
        print("  COULD NOT CANCEL (it may have just filled, or already gone).")
        print("  Scroll up to see the reason.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
