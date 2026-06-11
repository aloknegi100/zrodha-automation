"""
menu.py  --  ONE command to run everything.

Instead of remembering a different file for each task, just run:

    source .venv/bin/activate
    python menu.py

...and pick what you want from the list. (Or run ./zerodha to skip the
activate step too.) After each task you come straight back to this menu.
"""
import sys

import cancel
import config
import exit as exit_tool
import get_access_token
import main as engine
import trade
from logger import log
from trade import ask

# (number shown) -> (menu label, the function to run)
ACTIONS = [
    ("Log in for today (get a fresh access token)", get_access_token.main),
    ("Start the safety engine (runs until you press Ctrl+C)", engine.main),
    ("Place an order (buy / sell)", trade.main),
    ("Cancel a pending order (not filled yet)", cancel.main),
    ("Exit a position you already hold", exit_tool.main),
]


def run(action):
    """Run one menu action, always returning safely to the menu afterwards."""
    try:
        action()
    except KeyboardInterrupt:
        print("\n(stopped -- back to the menu)")
    except SystemExit:
        # A tool called sys.exit() (e.g. a missing key). Stay in the menu.
        pass
    except Exception as e:
        log(f"menu action error: {e}", level="error")
        print(f"\nSomething went wrong: {e}")


def main():
    print("\n" + "=" * 55)
    print("  ZERODHA DISCIPLINE BOT")
    if config.DRY_RUN:
        print("  MODE: PRACTICE (DRY_RUN=true) -- no real orders are sent.")
    else:
        print("  MODE: *** LIVE *** -- real orders with real money!")
    print("=" * 55)

    choices = [str(i) for i in range(1, len(ACTIONS) + 1)] + ["Q"]
    while True:
        print("\nWhat do you want to do?\n")
        for i, (label, _) in enumerate(ACTIONS, start=1):
            print(f"  {i}. {label}")
        print("  Q. Quit")

        choice = ask("Choose", options=choices)
        if choice == "Q":
            print("Bye.")
            return
        run(ACTIONS[int(choice) - 1][1])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye.")
        sys.exit(0)
