"""
Builds an authenticated KiteConnect client from the credentials in config.
"""
from kiteconnect import KiteConnect

import config
from logger import log


def get_kite():
    """Initialise and return an authenticated KiteConnect client."""
    if not config.API_KEY or not config.ACCESS_TOKEN:
        raise RuntimeError(
            "API_KEY / ACCESS_TOKEN are missing. Copy .env.example to .env and "
            "fill in your Kite Connect credentials."
        )
    kite = KiteConnect(api_key=config.API_KEY)
    kite.set_access_token(config.ACCESS_TOKEN)
    log("KiteConnect client initialised.")
    return kite
