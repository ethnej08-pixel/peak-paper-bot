# Peak + ChatGPT Project State

> Shared checkpoint for work both assistants are authorized to see. Update this file at the end of each work session. Record evidence and links; do not claim work that cannot be verified.

## Project

- **Project name:** Peak / AI workflow
- **Last updated:** YYYY-MM-DD HH:MM TZ
- **Updated by:** Name or assistant
- **Shared source of truth:** https://github.com/ethnej08-pixel/peak-paper-bot

## Current status

- **Overall:** Not started / In progress / Blocked / Complete
- **Current goal:**
- **Next action:**
- **Blockers / decisions needed:**

## Tasks

| Status | Task | Owner | Evidence / link | Updated |
|---|---|---|---|---|
| Todo |  |  |  |  |

## Work log

Add newest entries first. Keep each entry short and verifiable.

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

### YYYY-MM-DD HH:MM TZ — Name / assistant

- **Completed:**
- **Files changed:** `path` — what changed (link or commit if available)
- **Checks run:** command/tool and actual result; write “not run” when applicable
- **Still working on:**
- **Next step:**

## Skills and automations

| Item | Status | Evidence (file, link, run ID, or result) | Last checked |
|---|---|---|---|
|  |  |  |  |

## Review notes

| Date | Reviewer | Finding | Follow-up task / evidence |
|---|---|---|---|
| 2026-11-06 | Peak (Claude) | **Bot runs about every 50 min, not every 5.** GitHub delays scheduled workflows heavily. The strategy reads 5-min bars, and the 2% stop loss is only checked at each run, so a stop can fill well past -2%. | Commit times on Nov 5–6: tick 15:09, 15:43, 16:32, 17:27… (UTC). Option: switch to 30-min bars, or run the bot locally / on a server for true 5-min checks. ChatGPT: agree? |
| 2026-11-06 | Peak (Claude) | **Lots of small whipsaw losses.** It buys whenever fast avg > slow avg by any amount, e.g. SPY 737.78 > 737.64. All 7 symbols are big US tech/index names, so they cross together and it acts like one bet x7 (7 buys at 14:20, all sold within ~1.5 hrs). | RESULTS.md trades on 11-06 14:20 → 15:11/15:57. Option: require a minimum gap (e.g. fast > slow by 0.1%) and/or mix in less-correlated symbols. |
| 2026-11-06 | Peak (Claude) | **"+0.02% vs SPY -4.25%" overstates the edge.** The SPY baseline is $767.82 from Nov 4 3:23 PM. The bot was in cash during most of that drop, and 2.5 days is far too short to judge. | state.json `spy_start`. Suggest judging after 4+ weeks; worth double-checking the 767.82 baseline against a real Nov 4 quote. |
| 2026-11-06 | Peak (Claude) | Minor: no market-holiday check, so on holidays (e.g. Thanksgiving) it runs on stale prices. Every run commits because `last_run` changes. | `market_open()` in bot.py. Low priority. |

## Access and activity limits

- This file records only work that its contributors choose to document.
- It does not expose or monitor private Claude conversations, hidden session activity, or unshared Mac files.
- Link evidence to commits, file paths, test output, or screenshots only when those are safe to share.
- Do not place passwords, API keys, tokens, or private personal data here.
