# Zerodha Trading Discipline Bot

This program is an **automatic bodyguard for your Zerodha account**. It does
**not** decide what to buy or sell. It watches the trades *you* make and
automatically enforces safety rules so you don't blow up your account through
the common mistakes every trader makes.

> ⚠️ **You do NOT need to know coding to use this.** You only ever edit one
> simple text file called `.env`. You never have to touch the program code.

---

## What it does for you

Every minute it checks your account and:

1. **Rejects oversized trades** – blocks any single trade bigger than your limit.
2. **Adds a stop-loss if you forgot one** – every position gets protection.
3. **Stops revenge trading** – after you hit your daily loss limit, it locks
   trading and closes everything.
4. **Locks in profits** – trails the stop-loss up on winning trades.
5. **Stops overtrading** – blocks new trades after your daily count is reached.
6. **Cuts losers** – sells a position automatically if it falls too far.
7. **Filters weak option buys** – flags options unlikely to move enough.
8. **Avoids overnight risk** – closes all positions at 3:15 PM.

---

## 🟢 Practice mode vs 🔴 Live mode (READ THIS)

There is a single setting called `DRY_RUN` that controls everything:

| Setting | What happens |
|---------|--------------|
| `DRY_RUN=true`  | 🟢 **Practice mode.** It only *watches* and *prints* what it would do. **No real orders. Your money is never touched.** |
| `DRY_RUN=false` | 🔴 **Live mode.** It places **real orders with real money**. |

**It starts in practice mode.** Leave it that way until you have watched it run
for several days and you trust what it does.

---

## Part 1 — One-time setup

Do this **once**. Open a terminal (on Ubuntu: press `Ctrl + Alt + T`) and type
each line below, pressing **Enter** after each one.

**1. Go into the project folder:**
```
cd /home/vcl-alok/Documents/zerodha-automation
```

**2. Install the tools Python needs** (it will ask for your password — type it,
it stays invisible, press Enter):
```
sudo apt install -y python3-pip python3-venv
```

**3. Create a private workspace and install the libraries:**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Create your settings file:**
```
cp .env.example .env
```

Setup is done. ✅

---

## Part 2 — Edit your settings (no coding)

All your settings are in the file named **`.env`**. Open it with a simple editor:
```
nano .env
```

You'll see lines like this. **Just change the number after the `=` sign:**

```
DRY_RUN=true
MAX_CAPITAL_PER_TRADE_PERCENT=10
HARD_STOP_LOSS_PERCENT=10
MAX_DAILY_LOSS=5000
MAX_TRADES_PER_DAY=5
```

### What each setting means

| Setting | Plain English | Example |
|---------|---------------|---------|
| `DRY_RUN` | `true` = practice, `false` = real money | `true` |
| `API_KEY`, `API_SECRET`, `ACCESS_TOKEN` | Your Zerodha login keys | — |
| `MAX_CAPITAL_PER_TRADE_PERCENT` | Biggest single trade, as % of your capital | `10` |
| `HARD_STOP_LOSS_PERCENT` | Sell automatically if a trade drops this % | `10` |
| `MAX_DAILY_LOSS` | Stop & close all after losing this many ₹ in a day | `5000` |
| `MAX_TRADES_PER_DAY` | Block new trades after this many trades | `5` |
| `DEFAULT_SL_PERCENT` | How far below entry the auto stop-loss sits (%) | `10` |
| `TRAIL_START_PERCENT` | Start trailing once a trade is up this % | `2` |
| `TRAIL_SL_MOVE_PERCENT` | Keep the trailing stop this % below price | `0.5` |
| `SQUARE_OFF_HOUR` / `SQUARE_OFF_MINUTE` | Time to close everything (24-hour clock) | `15` / `15` |
| `MONITOR_INTERVAL_MINUTES` | How often it checks (leave at 1) | `1` |

**Important typing rules:**
- No spaces around the `=`. Correct: `MAX_TRADES_PER_DAY=5`
- For `MAX_DAILY_LOSS`, enter a **positive** number (e.g. `5000`, not `-5000`).

**To save in nano:** press `Ctrl + O`, then `Enter`, then `Ctrl + X` to exit.

> You must also paste your Zerodha `API_KEY`, `API_SECRET`, and `ACCESS_TOKEN`
> into `.env`. The access token is generated fresh each day through Kite's
> login. If you don't have one, ask and a login helper can be added.

---

## Part 3 — Run it

Each time you want to start it:
```
cd /home/vcl-alok/Documents/zerodha-automation
source .venv/bin/activate
python main.py
```

You'll see messages scroll by, for example:
```
DRY_RUN = True  (no real orders are sent while True)
Day P&L: -1700.00 (limit -5000)
[DRY_RUN] Would place order -> {... 'order_type': 'SL-M' ...}
```

That `[DRY_RUN]` line means *"in real mode I would have done this"*. In practice
mode nothing actually happens to your account.

**To stop it:** press `Ctrl + C`.

A full record of everything is also saved in the `logs/` folder.

---

## Part 4 — Going live (only when ready)

1. Watch it in practice mode for several days first.
2. Open `.env` (`nano .env`), change `DRY_RUN=true` to `DRY_RUN=false`, save.
3. Start it again with `python main.py`.

It will now place **real orders with real money**. ⚠️

---

## If something goes wrong

- **`ModuleNotFoundError`** → you forgot `source .venv/bin/activate` before
  `python main.py`. Run that line, then try again.
- **`command not found: pip`** → run Part 1 step 2 again.
- **A login / token error** → your `ACCESS_TOKEN` in `.env` is missing or expired
  (it changes daily). Generate a new one and paste it in.
- **Anything else** → copy the red error text and ask for help.

---

## No warranty

This software places real orders on your account when in live mode. You are
responsible for every order. Test thoroughly in practice mode first.
