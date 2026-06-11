"""
exit.py  --  exit (square off) a position you already hold.

Run it, pick the position, confirm:

    source .venv/bin/activate
    python exit.py

Use this when an order has FILLED and you now own something you want out of.
It places the opposite order to flatten the position -- SELL to close a long,
BUY to close a short -- and works for one position or all of them at once.

(If your order has NOT filled yet there is no position to exit -- cancel the
pending order instead with `python cancel.py`.)

An exit is never blocked by the discipline guards: closing risk must always be
allowed. While DRY_RUN=true it only PRINTS what it would do -- no real order.
"""
import sys

import config
from kite_client import get_kite
from order_utils import get_open_positions, square_off_position
from trade import ask, ask_float


def describe(position):
    """One-line summary of a held position for the chooser list."""
    qty = position["quantity"]
    side = "LONG" if qty > 0 else "SHORT"
    avg = position.get("average_price", 0)
    ltp = position.get("last_price", 0)
    pnl = position.get("pnl")
    pnl_note = f"  P&L {pnl:+,.2f}" if pnl is not None else ""
    return (
        f"{side} {abs(qty)} x {position['tradingsymbol']} "
        f"({position['exchange']}) {position['product']}  "
        f"avg {avg}  ltp {ltp}{pnl_note}"
    )


def exit_one(kite, position):
    """Exit a single position, asking MARKET vs a LIMIT price."""
    qty = position["quantity"]
    side = "SELL" if qty > 0 else "BUY"

    order_type = ask("Exit order type?", options=["MARKET", "LIMIT"],
                     default="MARKET", shortcuts={"M": "MARKET", "L": "LIMIT"})
    price = ask_float("Limit price") if order_type == "LIMIT" else None

    at = f"@ {price}" if price is not None else "at MARKET"
    print(f"\n  This will {side} {abs(qty)} x {position['tradingsymbol']} {at}.")
    confirm = ask("Place this exit?", options=["YES", "NO"], default="NO",
                  shortcuts={"Y": "YES", "N": "NO"})
    if confirm != "YES":
        print("Nothing exited.")
        return

    result = square_off_position(kite, position, order_type=order_type, price=price)
    _report(position["tradingsymbol"], result)


def exit_all(kite, positions):
    """Exit every position with MARKET orders (a single LIMIT can't span symbols)."""
    print(f"\n  This will MARKET-exit ALL {len(positions)} position(s).")
    confirm = ask("Exit everything?", options=["YES", "NO"], default="NO",
                  shortcuts={"Y": "YES", "N": "NO"})
    if confirm != "YES":
        print("Nothing exited.")
        return

    for position in positions:
        result = square_off_position(kite, position, order_type="MARKET")
        _report(position["tradingsymbol"], result)


def _report(symbol, result):
    if config.DRY_RUN:
        print(f"  PRACTICE: exit for {symbol} simulated only (see the log above).")
    elif result:
        print(f"  EXIT PLACED for {symbol}. Order id: {result}")
    else:
        print(f"  COULD NOT EXIT {symbol} -- scroll up to see the reason.")


def main():
    print("\n" + "=" * 55)
    print("  EXIT A POSITION")
    print("=" * 55)
    if config.DRY_RUN:
        print("  MODE: PRACTICE (DRY_RUN=true) -- nothing is really exited.")
    else:
        print("  MODE: *** LIVE *** -- this closes a REAL position!")
    print("=" * 55 + "\n")

    kite = get_kite()

    positions = get_open_positions(kite)
    if not positions:
        print("You hold no open positions to exit.")
        print("(Nothing has filled yet? Cancel a pending order with cancel.py.)")
        return

    print("Your open positions:\n")
    for i, position in enumerate(positions, start=1):
        print(f"  {i}. {describe(position)}")
    print()

    choices = [str(i) for i in range(1, len(positions) + 1)] + ["A", "Q"]
    choice = ask("Exit which number? (A = all, Q = quit)", options=choices)

    if choice == "Q":
        print("Nothing exited.")
    elif choice == "A":
        exit_all(kite, positions)
    else:
        exit_one(kite, positions[int(choice) - 1])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
