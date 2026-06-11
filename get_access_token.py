"""
get_access_token.py  --  generate your daily Zerodha access token.

Zerodha expires the access token every morning, so run this once each trading
day BEFORE you start the bot:

    source .venv/bin/activate
    python get_access_token.py

What happens:
  1. It prints a login link.
  2. You open the link in your browser and log in to Zerodha.
  3. Your browser jumps to a page that may show "site can't be reached" --
     that's fine. Copy the FULL address from the browser's address bar.
  4. Paste it back here. The new access token is saved into your .env for you.

You need API_KEY and API_SECRET already filled in your .env for this to work.
"""
import sys
from urllib.parse import urlparse, parse_qs

from kiteconnect import KiteConnect

import config

ENV_PATH = ".env"


def extract_request_token(text):
    """Accept either a pasted request_token or the full redirect URL."""
    text = text.strip()
    if "request_token" in text:
        qs = parse_qs(urlparse(text).query)
        if qs.get("request_token"):
            return qs["request_token"][0]
    return text  # assume they pasted just the token


def update_env_access_token(token, env_path=ENV_PATH):
    """Write the new ACCESS_TOKEN into .env, replacing the old line if present."""
    try:
        with open(env_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    new_line = f"ACCESS_TOKEN={token}\n"
    replaced = False
    for i, line in enumerate(lines):
        if line.strip().startswith("ACCESS_TOKEN="):
            lines[i] = new_line
            replaced = True
            break
    if not replaced:
        lines.append(new_line)

    with open(env_path, "w") as f:
        f.writelines(lines)


def main():
    if not config.API_KEY or config.API_KEY == "YOUR_API_KEY":
        print("ERROR: API_KEY is missing in .env. Fill it in first.")
        sys.exit(1)
    if not config.API_SECRET or config.API_SECRET == "YOUR_SECRET":
        print("ERROR: API_SECRET is missing in .env. Fill it in first.")
        sys.exit(1)

    kite = KiteConnect(api_key=config.API_KEY)

    print("\n" + "=" * 60)
    print("STEP 1: Open this link in your browser and log in to Zerodha:\n")
    print("   " + kite.login_url())
    print("\nSTEP 2: After logging in your browser will jump to a new address")
    print("        (it may say 'site can't be reached' -- that is OK).")
    print("        Copy the ENTIRE address from the browser's address bar.")
    print("=" * 60 + "\n")

    pasted = input("STEP 3: Paste the full address (or just the request_token) here:\n> ")
    request_token = extract_request_token(pasted)
    if not request_token:
        print("ERROR: couldn't find a request token in what you pasted.")
        sys.exit(1)

    try:
        data = kite.generate_session(request_token, api_secret=config.API_SECRET)
    except Exception as e:
        print(f"\nERROR generating session: {e}")
        print("The request token is only valid for a few minutes and one use only.")
        print("Run this script again and use a fresh login link.")
        sys.exit(1)

    access_token = data["access_token"]
    update_env_access_token(access_token)

    print("\n" + "=" * 60)
    print("SUCCESS! New access token saved to .env")
    print(f"   ACCESS_TOKEN={access_token}")
    print("\nYou can now run:  python main.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
