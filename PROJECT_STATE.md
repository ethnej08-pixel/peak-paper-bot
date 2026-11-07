# Peak + ChatGPT Project State

> Shared checkpoint for work both assistants are authorized to see. Update this file at the end of each work session. Record evidence and links; do not claim work that cannot be verified.

## Project

- **Project name:** Peak / AI workflow (paper-trading bot, fake money only)
- **Last updated:** 2026-11-06 20:25 ET (Fri night)
- **Updated by:** Claude Code
- **Shared source of truth:** https://github.com/ethnej08-pixel/peak-paper-bot

## Current status

- **Overall:** Live — repo is public, PR #1 merged, all-day 5-min loop starts Mon 2026-11-09.
- **Current goal:** Run the 9/21-bar trend strategy on 7 symbols and compare against holding SPY.
- **Next action:** Mon 2026-11-09 10:30 ET: Claude Code checks the first live day (tick commits every 5 min from 9:30, `RESULTS.md` updating, SPY start check result in `state.json` log).
- **Blockers / decisions needed:** None. Note: repo is now public, so never commit passwords/keys (dashboard password comes from env vars only; see `SECURITY.md`).

## Tasks

| Status | Task | Owner | Evidence / link | Updated |
|---|---|---|---|---|
| Done | Paper-trading bot (`bot.py`) | Claude | commit `44c63bb` | 2026-11-05 |
| Done | Scheduled GitHub Actions run (`.github/workflows/trade.yml`) | Claude | `tick HH:MM` commits on 2026-11-05 and 2026-11-06 | 2026-11-06 |
| Done | Shared project state template | ethnej08-pixel | commit `25e21b7` | 2026-11-06 |
| Done | True 5-min schedule via all-day loop job | Claude Code | `bot.py --loop`, `.github/workflows/trade.yml` merged in PR #1 (`9758ba3`) | 2026-11-06 |
| Done | Review fixes: 0.1% trend gap, less-correlated symbols, SPY start check + "too early" note, holidays | Claude Code | merged in PR #1 (`9758ba3`) | 2026-11-06 |
| Done | Dashboard password (HTTP Basic auth, env vars) + unit tests | ethnej08-pixel | commit `59d9419`, `SECURITY.md`, `tests/`; 6 tests pass | 2026-11-06 |
| Done | Merge PR #1 to `main` | Claude Code | https://github.com/ethnej08-pixel/peak-paper-bot/pull/1 | 2026-11-06 |
| Done | Make repo public (free unlimited Actions minutes) | ethnej08-pixel | GitHub API: `"visibility": "public"` | 2026-11-06 |
| Done | Price-only test run on GitHub | Claude Code | run 42323273773: all 7 symbols fetched, 391 bars each | 2026-11-06 |
| Done | Daily results panel (right side of dashboard) + "Daily results" table in `RESULTS.md` | Claude Code | `daily_pnl`/`daily_panel` in `bot.py`; `tests/test_daily_results.py` (9 tests pass) | 2026-11-06 |
| Todo | Check first live 5-min day | Claude Code | scheduled Mon 2026-11-09 10:30 ET |  |
| Todo | Add 2028 NYSE holidays to `bot.py` | ethnej08-pixel |  |  |

## Work log

Add newest entries first. Keep each entry short and verifiable.

### 2026-11-06 20:25 ET — Claude Code

- **Completed:** Merged PR #1. Owner made the repo public. Ran a price-only test on GitHub. Added a daily results panel: profitable vs negative days, best/worst day, a bar per day (so far: Fri Nov 6 +$120.62, Thu Nov 5 -$118.47).
- **Files changed:** `PROJECT_STATE.md` — status, tasks, automations; `bot.py` — daily panel + RESULTS.md section; `tests/test_daily_results.py`; `RESULTS.md` regenerated.
- **Checks run:** 9 unit tests pass; screenshot of dashboard at 1280px and 390px (no sideways scroll on phone). GitHub API shows repo `public`; Actions run 42323273773 succeeded, all 7 symbols returned 391 five-min bars; `python3 -m unittest discover -s tests` → 6 OK; scanned repo for committed passwords/tokens → none.
- **Still working on:** Nothing until Monday.
- **Next step:** Mon 2026-11-09 10:30 ET check of the first live 5-min day.

### 2026-11-06 ~20:05 ET — Claude Code

- **Completed:** Filled in this file from the repo's current state. Switched the bot to an all-day loop job so it really runs every 5 min. Fixed the other 3 review findings (see Review notes).
- **Files changed:** `PROJECT_STATE.md` — status, tasks, log; `bot.py` — `--loop` mode + `git_save`; `.github/workflows/trade.yml` — kick-off crons, 6 h job, no DST edits needed.
- **Checks run:** Read `state.json` and `RESULTS.md`: 42 trades since 2026-11-04 15:23 ET; account $10,002.15 (+0.02%) vs SPY -4.25%; no open positions; last check 2026-11-06 15:57 ET. Read `git log` for run times. Simulated `cloud_loop` with a fake clock: 52 ticks 9:30–13:45, then a takeover run 13:47–15:55, stopped at close. Fake-price test: a 0.05% cross is ignored, a 0.5% cross buys; SPY start check replaces a wrong baseline; Thanksgiving closed, Nov 27 closes 1 PM. Not yet run on GitHub (Yahoo is blocked from this sandbox, so the real SPY baseline is still unverified).
- **Still working on:** Nothing.
- **Next step:** Owner makes repo public and merges to `main`; check Actions on Monday.

### 2026-11-06 20:10 EST — Peak (Claude)

- **Completed:** Reviewed `bot.py`, `.github/workflows/trade.yml`, `RESULTS.md`, `state.json`. 4 findings added under Review notes.
- **Files changed:** `PROJECT_STATE.md` only. No code changed.
- **Checks run:** read code; compared commit times to the 5-min schedule; read `spy_start` from state.json. Did not run the bot.
- **Still working on:** nothing; waiting on ChatGPT's second opinion
- **Next step:** ChatGPT reviews the 4 findings (agree/disagree under Review notes), then Ethan picks which fixes to make

### 2026-11-06 20:02 EST — Peak (Claude)

- **Completed:** Peak (Claude) now has read/write access to this repo. Ethan approved attaching it in Claude chat.
- **Files changed:** `PROJECT_STATE.md` — added this log entry as a connection test
- **Checks run:** cloned repo and read `PROJECT_STATE.md` — file present, matched ChatGPT's template
- **Still working on:** confirming ChatGPT can see this entry
- **Next step:** ChatGPT reads this file and replies under "Review notes" to confirm the two-way loop works

### 2026-11-06 19:49 ET — ethnej08-pixel

- **Completed:** Added this shared project state template.
- **Files changed:** `PROJECT_STATE.md` (commit `25e21b7`)
- **Checks run:** not run
- **Still working on:** —
- **Next step:** —

## Skills and automations

| Item | Status | Evidence (file, link, run ID, or result) | Last checked |
|---|---|---|---|
| `paper-trade` workflow (trading days 9:30–3:55 ET) | Merged; all-day loop every 5 min. First live day Mon 2026-11-09 (simulated full day = 79 ticks) | `tick` commits in `git log`; output in `RESULTS.md` | 2026-11-07 |
| Manual price check (`workflow_dispatch`, `bot.py --check`) | Passed | https://github.com/ethnej08-pixel/peak-paper-bot/actions/runs/42323273773 — SPY 735.29, AAPL 342.37, NVDA 186.64, TSLA 358.22, GLD 372.52, TLT 81.92, XLE 61.62 | 2026-11-06 |
| `tests` workflow (unit tests on PRs) | Added | `.github/workflows/tests.yml`; 6 tests pass locally | 2026-11-06 |

## Review notes

| Date | Reviewer | Finding | Follow-up task / evidence |
|---|---|---|---|
| 2026-11-06 | Peak (Claude) | **Bot runs about every 50 min, not every 5.** GitHub delays scheduled workflows heavily. The strategy reads 5-min bars, and the 2% stop loss is only checked at each run, so a stop can fill well past -2%. | Commit times on Nov 5–6: tick 15:09, 15:43, 16:32, 17:27… (UTC). Option: switch to 30-min bars, or run the bot locally / on a server for true 5-min checks. ChatGPT: agree? **Addressed by PR #1** (all-day loop job, ticks every 5 min; needs public repo). |
| 2026-11-06 | Peak (Claude) | **Lots of small whipsaw losses.** It buys whenever fast avg > slow avg by any amount, e.g. SPY 737.78 > 737.64. All 7 symbols are big US tech/index names, so they cross together and it acts like one bet x7 (7 buys at 14:20, all sold within ~1.5 hrs). | RESULTS.md trades on 11-06 14:20 → 15:11/15:57. Option: require a minimum gap (e.g. fast > slow by 0.1%) and/or mix in less-correlated symbols. **Fixed in PR #1:** 0.1% gap to buy and to sell; symbols now SPY, AAPL, NVDA, TSLA, GLD, TLT, XLE (dropped QQQ, MSFT, AMZN). |
| 2026-11-06 | Peak (Claude) | **"+0.02% vs SPY -4.25%" overstates the edge.** The SPY baseline is $767.82 from Nov 4 3:23 PM. The bot was in cash during most of that drop, and 2.5 days is far too short to judge. | state.json `spy_start`. Suggest judging after 4+ weeks; worth double-checking the 767.82 baseline against a real Nov 4 quote. **Fixed in PR #1:** bot checks the SPY start once against Yahoo 5-min history and corrects it if >0.5% off (logged in state.json); results now say "Too early to judge" until ~20 trading days and show how many closed trades made money. |
| 2026-11-06 | Peak (Claude) | Minor: no market-holiday check, so on holidays (e.g. Thanksgiving) it runs on stale prices. Every run commits because `last_run` changes. | `market_open()` in bot.py. Low priority. **Fixed in PR #1:** NYSE holidays and 1 PM early closes for Nov 2026–2027 in `HOLIDAYS`/`EARLY_CLOSE`; closed days don't tick or commit. Add 2028 dates next year. |

## Access and activity limits

- This file records only work that its contributors choose to document.
- It does not expose or monitor private Claude conversations, hidden session activity, or unshared Mac files.
- Link evidence to commits, file paths, test output, or screenshots only when those are safe to share.
- Do not place passwords, API keys, tokens, or private personal data here.
