"""
Zerodha Kite -- Retail Trading Discipline Automation
====================================================
A risk-control and emotional-discipline enforcement engine. It does NOT
generate trade signals -- it watches your account and enforces the rules
that protect you from the 8 classic retail execution mistakes.

Run:
    python main.py

SAFETY: DRY_RUN defaults to True (set in .env). While True, NO real orders
are sent -- every action is only logged. Set DRY_RUN=false in .env to go live.
"""
import time

import schedule

import config
import overnight_manager
import revenge_guard
import trade_monitor
import trailing_manager
from kite_client import get_kite
from logger import log


def monitor_cycle(kite):
    """One full risk sweep -- runs every MONITOR_INTERVAL_MINUTES."""
    try:
        # Mistake 3: stop everything if the daily loss limit is breached.
        if not revenge_guard.revenge_guard(kite):
            return

        # Mistake 2: ensure every open position has a stop-loss.
        trade_monitor.ensure_sl_exists(kite)

        # Mistake 6: hard stop -- force an exit if breached.
        trade_monitor.emotional_loss_protection(kite)

        # Mistake 4: trail the stop to lock in profit.
        trailing_manager.trail_profit(kite)

    except Exception as e:
        log(f"monitor_cycle error: {e}", level="error")


def overnight_cycle(kite):
    """Square everything off before the close (Mistake 8)."""
    try:
        overnight_manager.square_off_all(kite)
    except Exception as e:
        log(f"overnight_cycle error: {e}", level="error")


def main():
    log("=" * 60)
    log("Zerodha discipline engine starting...")
    log(f"DRY_RUN = {config.DRY_RUN}  (no real orders are sent while True)")
    log("=" * 60)

    kite = get_kite()

    schedule.every(config.MONITOR_INTERVAL_MINUTES).minutes.do(monitor_cycle, kite=kite)

    square_off_at = f"{config.SQUARE_OFF_HOUR:02d}:{config.SQUARE_OFF_MINUTE:02d}"
    schedule.every().day.at(square_off_at).do(overnight_cycle, kite=kite)

    log(
        f"Scheduled: risk sweep every {config.MONITOR_INTERVAL_MINUTES} min, "
        f"square-off at {square_off_at}."
    )

    # Run one sweep immediately, then loop on the schedule.
    monitor_cycle(kite)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
