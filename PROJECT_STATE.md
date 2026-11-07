# Peak + ChatGPT Project State

> Shared checkpoint for work both assistants are authorized to see. Update this file at the end of each work session. Record evidence and links; do not claim work that cannot be verified.

## Project

- **Project name:** Peak / AI workflow (paper-trading bot, fake money only)
- **Last updated:** 2026-11-07 ET
- **Updated by:** Claude Code
- **Shared source of truth:** https://github.com/ethnej08-pixel/peak-paper-bot

## Current status

- **Overall:** In progress — bot is live on GitHub Actions and trading fake money.
- **Current goal:** Run the 9/21-bar trend strategy on 7 symbols and compare against holding SPY.
- **Next action:** Merge branch `claude/elegant-wright-vtc4sp` into `main` and make the repo public, so the new all-day 5-minute loop starts.
- **Blockers / decisions needed:** GitHub's cron only fired about hourly. Fix (on the branch): one long job per trading day ticks every 5 min itself (`bot.py --loop`). Needs a public repo for free unlimited Actions minutes; owner chose public on 2026-11-07.

## Tasks

| Status | Task | Owner | Evidence / link | Updated |
|---|---|---|---|---|
| Done | Paper-trading bot (`bot.py`) | Claude | commit `44c63bb` | 2026-11-05 |
| Done | Scheduled GitHub Actions run (`.github/workflows/trade.yml`) | Claude | `tick HH:MM` commits on 2026-11-05 and 2026-11-06 | 2026-11-06 |
| Done | Shared project state template | ethnej08-pixel | commit `25e21b7` | 2026-11-06 |
| Done | True 5-min schedule via all-day loop job | Claude Code | `bot.py --loop`, `.github/workflows/trade.yml` on branch `claude/elegant-wright-vtc4sp` | 2026-11-07 |
| Todo | Make repo public + merge branch to `main` | ethnej08-pixel |  |  |

## Work log

Add newest entries first. Keep each entry short and verifiable.

### 2026-11-07 — Claude Code

- **Completed:** Filled in this file from the repo's current state. Switched the bot to an all-day loop job so it really runs every 5 min.
- **Files changed:** `PROJECT_STATE.md` — status, tasks, log; `bot.py` — `--loop` mode + `git_save`; `.github/workflows/trade.yml` — kick-off crons, 6 h job, no DST edits needed.
- **Checks run:** Read `state.json` and `RESULTS.md`: 42 trades since 2026-11-04 15:23 ET; account $10,002.15 (+0.02%) vs SPY -4.25%; no open positions; last check 2026-11-06 15:57 ET. Read `git log` for run times. Simulated `cloud_loop` with a fake clock: 52 ticks 9:30–13:45, then a takeover run 13:47–15:55, stopped at close. Not yet run on GitHub.
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
| `paper-trade` workflow (weekdays 9:30–3:55 ET) | On `main`: about hourly. On branch: every 5 min via loop (simulated full day = 79 ticks; not yet run on GitHub) | `tick` commits in `git log`; output in `RESULTS.md` | 2026-11-07 |
| Manual price check (`workflow_dispatch`, `bot.py --check`) | Available | `.github/workflows/trade.yml` | 2026-11-07 |

## Review notes

| Date | Reviewer | Finding | Follow-up task / evidence |
|---|---|---|---|
| 2026-11-06 | Peak (Claude) | **Bot runs about every 50 min, not every 5.** GitHub delays scheduled workflows heavily. The strategy reads 5-min bars, and the 2% stop loss is only checked at each run, so a stop can fill well past -2%. | Commit times on Nov 5–6: tick 15:09, 15:43, 16:32, 17:27… (UTC). Option: switch to 30-min bars, or run the bot locally / on a server for true 5-min checks. ChatGPT: agree? **Addressed by PR #1** (all-day loop job, ticks every 5 min; needs public repo). |
| 2026-11-06 | Peak (Claude) | **Lots of small whipsaw losses.** It buys whenever fast avg > slow avg by any amount, e.g. SPY 737.78 > 737.64. All 7 symbols are big US tech/index names, so they cross together and it acts like one bet x7 (7 buys at 14:20, all sold within ~1.5 hrs). | RESULTS.md trades on 11-06 14:20 → 15:11/15:57. Option: require a minimum gap (e.g. fast > slow by 0.1%) and/or mix in less-correlated symbols. |
| 2026-11-06 | Peak (Claude) | **"+0.02% vs SPY -4.25%" overstates the edge.** The SPY baseline is $767.82 from Nov 4 3:23 PM. The bot was in cash during most of that drop, and 2.5 days is far too short to judge. | state.json `spy_start`. Suggest judging after 4+ weeks; worth double-checking the 767.82 baseline against a real Nov 4 quote. |
| 2026-11-06 | Peak (Claude) | Minor: no market-holiday check, so on holidays (e.g. Thanksgiving) it runs on stale prices. Every run commits because `last_run` changes. | `market_open()` in bot.py. Low priority. |

## Access and activity limits

- This file records only work that its contributors choose to document.
- It does not expose or monitor private Claude conversations, hidden session activity, or unshared Mac files.
- Link evidence to commits, file paths, test output, or screenshots only when those are safe to share.
- Do not place passwords, API keys, tokens, or private personal data here.
