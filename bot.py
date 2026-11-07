"""Peak paper-trading bot. FAKE MONEY ONLY: no broker, no account, no real orders.

Strategy (simple trend-following on 5-minute bars):
  - Fast average = last 9 bars, slow average = last 21 bars.
  - BUY  when fast > slow (price trending up) and we don't hold it.
  - SELL when fast < slow (trend turned down) or price drops 2% below entry (stop loss).
  - Each buy uses $1,400 of the $10,000 fake account. Small slippage is charged.
Runs every 5 min during market hours (9:30-4:00 ET, weekdays).
Results page: http://localhost:8790
"""
import json, time, threading, subprocess, datetime, html, os, base64, secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
SYMBOLS = ["SPY", "QQQ", "AAPL", "NVDA", "MSFT", "TSLA", "AMZN"]
START_CASH, SIZE, FAST, SLOW, STOP, SLIP = 10000.0, 1400.0, 9, 21, 0.02, 0.0002
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


def market_open(t):
    return t.weekday() < 5 and datetime.time(9, 30) <= t.time() < datetime.time(16, 0)


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
        if held is None and fast > slow and s["cash"] >= SIZE:
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
            elif fast < slow:
                why = f"trend down: 9-bar avg {fast:.2f} < 21-bar avg {slow:.2f}"
            if why:
                fill = price * (1 - SLIP)
                pnl = (fill - held["entry"]) * held["qty"]
                s["cash"] += held["qty"] * fill
                del s["pos"][sym]
                s["trades"].append({"time": t.isoformat(), "side": "SELL", "sym": sym, "qty": held["qty"],
                                    "price": fill, "pnl": pnl, "why": why})
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
    status = "OPEN, trading every 5 min" if market_open(now()) else "CLOSED, resumes 9:30 AM ET"
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
<h3>Open positions</h3><table><tr><th>Stock</th><th>Shares</th><th>Bought at</th><th>Now</th><th>P/L</th></tr>{rows_pos}</table>
<h3>Trades (newest first)</h3><table><tr><th>Time</th><th>Side</th><th>Stock</th><th>Price</th><th>P/L</th><th>Why</th></tr>{rows_tr}</table>
<p class=n>Rules: buy when the 9-bar average is above the 21-bar average (5-min bars); sell when it drops below, or at -2% stop loss. $1,400 per trade. Started {s['started'][:16].replace('T',' ')}.</p>
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
           f"_Last check: {(s['last_run'] or 'never')[:16].replace('T', ' ')} ET. Runs every 5 min, 9:30-4:00 ET weekdays._", "",
           "| Account value | Bot return | If you'd just held SPY | Cash |", "|---|---|---|---|",
           f"| **${eq:,.2f}** | **{ret:+.2f}%** | {spy_ret:+.2f}% | ${s['cash']:,.2f} |", "",
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
    out += ["", f"Rules: buy when the 9-bar average is above the 21-bar average (5-min bars); sell when it drops below, "
            f"or at a -2% stop loss. $1,400 per trade. Started {s['started'][:16].replace('T', ' ')}."]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:  # cloud smoke test: fetch prices only, no trades
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
