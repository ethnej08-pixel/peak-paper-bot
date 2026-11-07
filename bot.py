"""Peak paper-trading bot. FAKE MONEY ONLY: no broker, no account, no real orders.

Strategy (simple trend-following on 5-minute bars):
  - Fast average = last 9 bars, slow average = last 21 bars.
  - BUY  when fast is above slow by at least 0.1% (a clear uptrend) and we don't hold it.
  - SELL when fast is below slow by at least 0.1% (trend turned down) or price drops 2% below entry (stop loss).
    The 0.1% gap stops it from buying and selling on tiny wiggles (lots of small losses).
  - Symbols mix stocks with gold, bonds and energy so they don't all move together.
  - Each buy uses $1,400 of the $10,000 fake account. Small slippage is charged.
Runs every 5 min during market hours (9:30-4:00 ET, weekdays, NYSE holidays skipped, 1:00 PM on early-close days):
locally via loop(), on GitHub via --loop.
Results page: http://localhost:8790
"""
import json, time, threading, subprocess, datetime, html, os, base64, secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
# SPY = S&P 500, GLD = gold, TLT = long-term US bonds, XLE = energy stocks. Dropped QQQ/MSFT/AMZN,
# which moved almost exactly with SPY/AAPL/NVDA and turned every signal into one big bet.
SYMBOLS = ["SPY", "AAPL", "NVDA", "TSLA", "GLD", "TLT", "XLE"]
START_CASH, SIZE, FAST, SLOW, STOP, SLIP = 10000.0, 1400.0, 9, 21, 0.02, 0.0002
GAP = 0.001  # fast must clear slow by 0.1% to count as a trend
MIN_DAYS = 20  # trading days before the results mean much

# NYSE full-day closures and 1:00 PM early closes (nyse.com holiday calendar). Add each new year here.
HOLIDAYS = {
    "2026-11-26", "2026-12-25",
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18",
    "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
}
EARLY_CLOSE = {"2026-11-27", "2026-12-24", "2027-11-26"}
lock = threading.Lock()


DASHBOARD_USER = os.environ.get("PEAK_DASHBOARD_USER", "peak")
DASHBOARD_PASSWORD = os.environ.get("PEAK_DASHBOARD_PASSWORD", "")


def is_authorized(header, username=DASHBOARD_USER, password=DASHBOARD_PASSWORD):
    """Validate HTTP Basic credentials without logging or storing the password."""
    if not password or not header or not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header[6:], validate=True).decode("utf-8")
        supplied_user, separator, supplied_password = decoded.partition(":")
    except (ValueError, UnicodeDecodeError):
        return False
    if not separator:
        return False
    return (secrets.compare_digest(supplied_user, username)
            and secrets.compare_digest(supplied_password, password))


def now():
    return datetime.datetime.now(ET)


def trading_day(t):
    return t.weekday() < 5 and t.strftime("%Y-%m-%d") not in HOLIDAYS


def close_time(t):
    return datetime.time(13, 0) if t.strftime("%Y-%m-%d") in EARLY_CLOSE else datetime.time(16, 0)


def market_open(t):
    return trading_day(t) and datetime.time(9, 30) <= t.time() < close_time(t)


def check_spy_start(s):
    """One-time check of the SPY starting price against Yahoo's own 5-min history at the bot's start time.
    The first price was saved from a single live quote; if it's off by more than 0.5%, use the history."""
    if s.get("spy_start_checked") or not s.get("spy_start"):
        return
    start = datetime.datetime.fromisoformat(s["started"]).timestamp()
    url = "https://query1.finance.yahoo.com/v8/finance/chart/SPY?interval=5m&range=1mo"
    try:
        raw = subprocess.run(["curl", "-sf", "--max-time", "15", "-A", "Mozilla/5.0", url],
                             capture_output=True, check=True).stdout
        d = json.loads(raw)["chart"]["result"][0]
        pts = [(ts, c) for ts, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]) if c is not None]
        ts, real = min(pts, key=lambda p: abs(p[0] - start))
    except Exception as e:
        s["log"].append(f"SPY start check failed: {e}")
        return
    if abs(ts - start) > 900:  # no bar within 15 min of the start: can't judge
        s["log"].append("SPY start check: no price near start time")
    elif abs(real / s["spy_start"] - 1) > 0.005:
        s["log"].append(f"SPY start fixed: saved {s['spy_start']:.2f}, history says {real:.2f}")
        s["spy_start"] = real
    else:
        s["log"].append(f"SPY start confirmed: {s['spy_start']:.2f} (history {real:.2f})")
    s["spy_start_checked"] = True


def scorecard(s):
    """Honest context for the headline numbers: how long it has run and how closed trades did."""
    days = len({t["time"][:10] for t in s["trades"]} | ({s["last_run"][:10]} if s["last_run"] else set()))
    sells = [t for t in s["trades"] if "pnl" in t]
    wins = sum(t["pnl"] > 0 for t in sells)
    win = f"{wins}/{len(sells)} closed trades made money" if sells else "no closed trades yet"
    early = (f"Too early to judge: {days} trading day{'s' if days != 1 else ''} so far, need about {MIN_DAYS}. "
             f"Short stretches are mostly luck (e.g. sitting in cash on a day SPY happened to drop).") \
        if days < MIN_DAYS else f"{days} trading days so far."
    return f"{early} {win}."


def bars(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=5m&range=5d"
    raw = subprocess.run(["curl", "-sf", "--max-time", "15", "-A", "Mozilla/5.0", url],
                         capture_output=True, check=True).stdout
    d = json.loads(raw)["chart"]["result"][0]
    closes = [c for c in d["indicators"]["quote"][0]["close"] if c is not None]
    return closes, d["meta"]["regularMarketPrice"]


def load():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"cash": START_CASH, "pos": {}, "trades": [], "prices": {}, "started": now().isoformat(),
            "spy_start": None, "last_run": None, "log": []}


def save(s):
    json.dump(s, open(STATE, "w"), indent=1)


def tick(s):
    t = now()
    for sym in SYMBOLS:
        try:
            closes, price = bars(sym)
        except Exception as e:
            s["log"].append(f"{t:%H:%M} {sym}: data error {e}")
            continue
        s["prices"][sym] = price
        if sym == "SPY" and s["spy_start"] is None:
            s["spy_start"] = price
        if len(closes) < SLOW:
            continue
        fast = sum(closes[-FAST:]) / FAST
        slow = sum(closes[-SLOW:]) / SLOW
        held = s["pos"].get(sym)
        if held is None and fast > slow * (1 + GAP) and s["cash"] >= SIZE:
            fill = price * (1 + SLIP)
            qty = round(SIZE / fill, 4)
            s["cash"] -= qty * fill
            s["pos"][sym] = {"qty": qty, "entry": fill, "time": t.isoformat()}
            s["trades"].append({"time": t.isoformat(), "side": "BUY", "sym": sym, "qty": qty, "price": fill,
                                "why": f"uptrend: 9-bar avg {fast:.2f} > 21-bar avg {slow:.2f}"})
        elif held is not None:
            why = None
            if price <= held["entry"] * (1 - STOP):
                why = f"stop loss: fell 2% below entry {held['entry']:.2f}"
            elif fast < slow * (1 - GAP):
                why = f"trend down: 9-bar avg {fast:.2f} < 21-bar avg {slow:.2f}"
            if why:
                fill = price * (1 - SLIP)
                pnl = (fill - held["entry"]) * held["qty"]
                s["cash"] += held["qty"] * fill
                del s["pos"][sym]
                s["trades"].append({"time": t.isoformat(), "side": "SELL", "sym": sym, "qty": held["qty"],
                                    "price": fill, "pnl": pnl, "why": why})
    check_spy_start(s)
    s["last_run"] = t.isoformat()
    s["log"] = s["log"][-20:]


def equity(s):
    return s["cash"] + sum(p["qty"] * s["prices"].get(k, p["entry"]) for k, p in s["pos"].items())


def page(s):
    eq = equity(s)
    ret = (eq / START_CASH - 1) * 100
    spy = s["prices"].get("SPY")
    spy_ret = ((spy / s["spy_start"] - 1) * 100) if spy and s["spy_start"] else 0
    col = lambda v: "#16a34a" if v >= 0 else "#dc2626"
    rows_pos = "".join(
        f"<tr><td>{k}</td><td>{p['qty']:.3f}</td><td>${p['entry']:.2f}</td><td>${s['prices'].get(k, 0):.2f}</td>"
        f"<td style='color:{col((s['prices'].get(k, p['entry']) - p['entry']))}'>"
        f"${(s['prices'].get(k, p['entry']) - p['entry']) * p['qty']:+.2f}</td></tr>"
        for k, p in s["pos"].items()) or "<tr><td colspan=5>No open positions</td></tr>"
    rows_tr = "".join(
        f"<tr><td>{t['time'][5:16].replace('T', ' ')}</td><td><b>{t['side']}</b></td><td>{t['sym']}</td>"
        f"<td>${t['price']:.2f}</td><td style='color:{col(t.get('pnl', 0))}'>"
        f"{'$%+.2f' % t['pnl'] if 'pnl' in t else ''}</td><td>{html.escape(t['why'])}</td></tr>"
        for t in reversed(s["trades"][-40:])) or "<tr><td colspan=6>No trades yet</td></tr>"
    status = "OPEN, trading every 5 min" if market_open(now()) else "CLOSED, resumes next trading day 9:30 AM ET"
    return f"""<!doctype html><html><head><meta charset=utf-8><meta http-equiv=refresh content=30>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Peak Paper Bot</title>
<style>body{{font:15px -apple-system,sans-serif;max-width:900px;margin:20px auto;padding:0 14px;color:#111}}
.k{{display:flex;gap:12px;flex-wrap:wrap}}.c{{border:1px solid #ddd;border-radius:10px;padding:10px 14px;min-width:150px}}
.c b{{font-size:22px;display:block}}table{{border-collapse:collapse;width:100%;margin:8px 0 20px}}
td,th{{border-bottom:1px solid #eee;padding:6px;text-align:left;font-size:14px}}.n{{color:#666;font-size:13px}}</style></head><body>
<h2>Peak Paper Bot <span class=n>(FAKE money, real prices)</span></h2>
<p class=n>Market: {status} · last check {(s['last_run'] or 'never')[11:16]} ET · page refreshes every 30s</p>
<div class=k><div class=c>Account value<b>${eq:,.2f}</b></div>
<div class=c>Bot return<b style='color:{col(ret)}'>{ret:+.2f}%</b></div>
<div class=c>If you'd just held SPY<b style='color:{col(spy_ret)}'>{spy_ret:+.2f}%</b></div>
<div class=c>Cash<b>${s['cash']:,.2f}</b></div></div>
<p class=n>{html.escape(scorecard(s))}</p>
<h3>Open positions</h3><table><tr><th>Stock</th><th>Shares</th><th>Bought at</th><th>Now</th><th>P/L</th></tr>{rows_pos}</table>
<h3>Trades (newest first)</h3><table><tr><th>Time</th><th>Side</th><th>Stock</th><th>Price</th><th>P/L</th><th>Why</th></tr>{rows_tr}</table>
<p class=n>Rules: buy when the 9-bar average is at least 0.1% above the 21-bar average (5-min bars); sell when it is 0.1% below, or at -2% stop loss. $1,400 per trade. Started {s['started'][:16].replace('T',' ')}.</p>
</body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if not is_authorized(self.headers.get("Authorization")):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Peak Paper Bot"')
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b"Authentication required.\n")
            return
        with lock:
            body = page(load()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def loop():
    while True:
        if market_open(now()):
            with lock:
                s = load()
                tick(s)
                save(s)
        time.sleep(300)


def results_md(s):
    eq = equity(s)
    ret = (eq / START_CASH - 1) * 100
    spy = s["prices"].get("SPY")
    spy_ret = ((spy / s["spy_start"] - 1) * 100) if spy and s["spy_start"] else 0
    out = [f"# Peak Paper Bot (FAKE money, real prices)", "",
           f"_Last check: {(s['last_run'] or 'never')[:16].replace('T', ' ')} ET. Runs every 5 min, 9:30-4:00 ET on trading days._", "",
           "| Account value | Bot return | If you'd just held SPY | Cash |", "|---|---|---|---|",
           f"| **${eq:,.2f}** | **{ret:+.2f}%** | {spy_ret:+.2f}% | ${s['cash']:,.2f} |", "",
           f"_{scorecard(s)}_", "",
           "## Open positions", "", "| Stock | Shares | Bought at | Now | P/L |", "|---|---|---|---|---|"]
    for k, p in s["pos"].items():
        now_p = s["prices"].get(k, p["entry"])
        out.append(f"| {k} | {p['qty']:.3f} | ${p['entry']:.2f} | ${now_p:.2f} | ${(now_p - p['entry']) * p['qty']:+.2f} |")
    if not s["pos"]:
        out.append("| none | | | | |")
    out += ["", "## Trades (newest first)", "", "| Time | Side | Stock | Price | P/L | Why |", "|---|---|---|---|---|---|"]
    for t in reversed(s["trades"][-60:]):
        pnl = "$%+.2f" % t["pnl"] if "pnl" in t else ""
        out.append(f"| {t['time'][5:16].replace('T', ' ')} | {t['side']} | {t['sym']} | ${t['price']:.2f} | {pnl} | {t['why']} |")
    out += ["", f"Rules: buy when the 9-bar average is at least 0.1% above the 21-bar average (5-min bars); "
            f"sell when it is 0.1% below, or at a -2% stop loss. $1,400 per trade. Started {s['started'][:16].replace('T', ' ')}."]
    return "\n".join(out) + "\n"


def git_save(msg):
    """Commit state.json + RESULTS.md and push. Pulls first so other people's commits are kept."""
    run = lambda *c: subprocess.run(["git", *c], cwd=HERE)
    run("add", "state.json", "RESULTS.md")
    if run("diff", "--cached", "--quiet").returncode == 0:
        return
    run("commit", "-q", "-m", msg)
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        if run("pull", "-q", "--rebase").returncode == 0 and run("push", "-q").returncode == 0:
            return
        run("rebase", "--abort")
    print("push failed, will retry next tick", flush=True)


def cloud_loop(max_minutes):
    """One long GitHub Actions job: tick every 5 min until market close or until the job's time is up.
    GitHub's own schedule is too unreliable for 5-min runs, so the timing lives here instead."""
    started = time.time()
    deadline = started + max_minutes * 60
    t = now()
    open_at = t.replace(hour=9, minute=30, second=5, microsecond=0)
    if trading_day(t) and t < open_at:  # started early: wait for the bell
        wait = (open_at - t).total_seconds()
        if time.time() + wait > deadline:
            print("too early to wait for the open, exiting"); return
        print(f"waiting {wait / 60:.0f} min for market open", flush=True)
        time.sleep(wait)
    while time.time() < deadline and market_open(now()):
        s = load()
        tick(s); save(s)
        open(os.path.join(HERE, "RESULTS.md"), "w").write(results_md(s))
        print("ticked", now().isoformat(), flush=True)
        git_save(f"tick {datetime.datetime.utcnow():%H:%M}")
        # sleep to the next 5-minute mark (9:35, 9:40, ...)
        t = now()
        nxt = (t + datetime.timedelta(minutes=5 - t.minute % 5)).replace(second=5, microsecond=0)
        time.sleep(max(1, (nxt - t).total_seconds()))
    print("done:", "market closed" if not market_open(now()) else "job time limit, next run takes over")


if __name__ == "__main__":
    import sys
    if "--loop" in sys.argv:  # GitHub Actions: one job runs all trading day
        cloud_loop(int(os.environ.get("LOOP_MINUTES", "340")))
    elif "--check" in sys.argv:  # cloud smoke test: fetch prices only, no trades
        for sym in SYMBOLS:
            closes, price = bars(sym)
            print(sym, price, len(closes), "bars")
    elif "--cloud" in sys.argv:  # one tick per scheduled run (GitHub Actions)
        s = load()
        if market_open(now()):
            tick(s); save(s)
            print("ticked", now().isoformat())
        else:
            print("market closed, skipping")
        open(os.path.join(HERE, "RESULTS.md"), "w").write(results_md(s))
    elif "--once" in sys.argv:
        s = load(); tick(s); save(s)
        print(json.dumps({"equity": equity(s), "pos": list(s["pos"]), "trades": len(s["trades"])}))
    else:
        if len(DASHBOARD_PASSWORD) < 16:
            raise SystemExit(
                "Refusing to start dashboard: set PEAK_DASHBOARD_PASSWORD "
                "to a password of at least 16 characters. See SECURITY.md."
            )
        threading.Thread(target=loop, daemon=True).start()
        HTTPServer(("127.0.0.1", 8790), H).serve_forever()
