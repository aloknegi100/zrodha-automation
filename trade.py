"""
trade.py  --  place a BUY or SELL order through the discipline checks.

Run it and answer the questions:

    source .venv/bin/activate
    python trade.py

Every order you place here first passes the safety rules:
  * revenge-trading lock (Mistake 3)
  * daily trade-count limit (Mistake 5)
  * max-capital-per-trade limit (Mistake 1)

If a rule is broken, the order is REJECTED and nothing is sent.

Remember: while DRY_RUN=true in your .env, this only PRINTS what it would do
-- no real order is placed. Set DRY_RUN=false to place real orders.
"""
import sys

import config
from kite_client import get_kite
from logger import log
from order_utils import get_ltp, place_disciplined_order


def ask(prompt, options=None, default=None, shortcuts=None):
    """Ask a question; optionally restrict to a set of options.

    `shortcuts` maps a single letter to a full option (e.g. {"B": "BUY"}), so
    you can type just the letter instead of the whole word. The full word still
    works too. Everything is case-insensitive and the answer is returned upper.
    """
    shortcuts = {k.upper(): v.upper() for k, v in (shortcuts or {}).items()}
    while True:
        if shortcuts:
            suffix = " [" + " / ".join(f"{k}={v}" for k, v in shortcuts.items()) + "]"
        elif options:
            suffix = f" [{'/'.join(options)}]"
        else:
            suffix = ""
        if default:
            suffix += f" (default {default})"
        answer = input(f"{prompt}{suffix}: ").strip()
        if not answer and default is not None:
            answer = default
        if not answer:
            print("  Please enter a value.")
            continue
        answer = shortcuts.get(answer.upper(), answer.upper())
        if options and answer not in [o.upper() for o in options]:
            print(f"  Please choose one of: {', '.join(options)}")
            continue
        return answer


def ask_int(prompt):
    while True:
        try:
            value = int(input(f"{prompt}: ").strip())
            if value <= 0:
                print("  Enter a number greater than 0.")
                continue
            return value
        except ValueError:
            print("  Please enter a whole number.")


def ask_float(prompt):
    while True:
        try:
            return float(input(f"{prompt}: ").strip())
        except ValueError:
            print("  Please enter a number.")


def get_available_balance(kite):
    """Fetch available cash; if it fails, ask the user."""
    try:
        margins = kite.margins()
        return float(margins["equity"]["available"]["live_balance"])
    except Exception as e:
        log(f"Could not fetch balance automatically: {e}", level="warning")
        return ask_float("Enter your available capital (in rupees)")


def main():
    print("\n" + "=" * 55)
    print("  PLACE AN ORDER  (with discipline checks)")
    print("=" * 55)
    if config.DRY_RUN:
        print("  MODE: PRACTICE (DRY_RUN=true) -- no real order is sent.")
    else:
        print("  MODE: *** LIVE *** -- this places a REAL order!")
    print("=" * 55 + "\n")

    kite = get_kite()

    transaction_type = ask("Buy or Sell?", options=["BUY", "SELL"],
                           shortcuts={"B": "BUY", "S": "SELL"})
    exchange = ask("Exchange?", options=["NSE", "NFO", "BSE", "CDS", "MCX"],
                   default="NSE",
                   shortcuts={"N": "NSE", "F": "NFO", "B": "BSE", "C": "CDS", "M": "MCX"})
    tradingsymbol = ask("Trading symbol (e.g. RELIANCE or BANKNIFTY25MAY56000CE)").upper()
    quantity = ask_int("Quantity")
    order_type = ask("Order type?", options=["MARKET", "LIMIT"], default="MARKET",
                     shortcuts={"M": "MARKET", "L": "LIMIT"})

    price = 0.0
    if order_type == "LIMIT":
        price = ask_float("Limit price")
        check_price = price
    else:
        # For a market order, estimate value using the live price.
        check_price = get_ltp(kite, exchange, tradingsymbol)
        if check_price is None:
            print("  Could not fetch live price; please enter it for the size check.")
            check_price = ask_float("Approx current price")

    product = ask("Product?", options=["MIS", "CNC", "NRML"], default="MIS",
                  shortcuts={"M": "MIS", "C": "CNC", "N": "NRML"})

    balance = get_available_balance(kite)
    est_value = quantity * check_price

    # --- Confirmation summary ---
    print("\n" + "-" * 55)
    print("  REVIEW YOUR ORDER")
    print("-" * 55)
    print(f"  {transaction_type} {quantity} x {tradingsymbol} ({exchange})")
    print(f"  Order type     : {order_type}" + (f" @ {price}" if order_type == "LIMIT" else ""))
    print(f"  Product        : {product}")
    print(f"  Est. value     : {est_value:,.2f}")
    print(f"  Avail. capital : {balance:,.2f}")
    print(f"  Per-trade limit: {config.MAX_CAPITAL_PER_TRADE_PERCENT}% "
          f"= {balance * config.MAX_CAPITAL_PER_TRADE_PERCENT / 100:,.2f}")
    print("-" * 55)

    confirm = ask("Place this order?", options=["YES", "NO"], default="NO",
                  shortcuts={"Y": "YES", "N": "NO"})
    if confirm != "YES":
        print("Cancelled. Nothing was sent.")
        return

    params = dict(
        variety="regular",
        exchange=exchange,
        tradingsymbol=tradingsymbol,
        transaction_type=transaction_type,
        order_type=order_type,
        product=product,
    )
    if order_type == "LIMIT":
        params["price"] = price

    order_id = place_disciplined_order(
        kite, balance=balance, quantity=quantity, price=check_price, **params
    )

    print("\n" + "=" * 55)
    if config.DRY_RUN:
        print("  PRACTICE MODE: order was simulated only (see the log above).")
    elif order_id:
        print(f"  ORDER PLACED. Order id: {order_id}")
    else:
        print("  ORDER NOT PLACED (a discipline rule blocked it, or it failed).")
        print("  Scroll up to see the reason.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
