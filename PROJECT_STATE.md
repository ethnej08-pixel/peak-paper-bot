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
- **Next action:** Decide whether hourly checks are OK or the bot needs a more reliable 5-minute scheduler (see blockers).
- **Blockers / decisions needed:** The workflow asks for a run every 5 min, but GitHub only ran it about once an hour (git log: 15:09, 15:43, 16:32, 17:27 … UTC on 2026-11-06). GitHub delays scheduled workflows under load, so the bot sees ~7 checks a day, not ~78.

## Tasks

| Status | Task | Owner | Evidence / link | Updated |
|---|---|---|---|---|
| Done | Paper-trading bot (`bot.py`) | Claude | commit `44c63bb` | 2026-11-05 |
| Done | Scheduled GitHub Actions run (`.github/workflows/trade.yml`) | Claude | `tick HH:MM` commits on 2026-11-05 and 2026-11-06 | 2026-11-06 |
| Done | Shared project state template | ethnej08-pixel | commit `25e21b7` | 2026-11-06 |
| Todo | Decide on schedule reliability (hourly vs true 5-min) | ethnej08-pixel |  |  |
| Todo | Update cron times when DST starts in March (shift back 1 hour) | ethnej08-pixel | comment in `trade.yml` |  |

## Work log

Add newest entries first. Keep each entry short and verifiable.

### 2026-11-07 — Claude Code

- **Completed:** Filled in this file from the repo's current state.
- **Files changed:** `PROJECT_STATE.md` — status, tasks, work log, automations.
- **Checks run:** Read `state.json` and `RESULTS.md`: 42 trades since 2026-11-04 15:23 ET; account $10,002.15 (+0.02%) vs SPY -4.25%; no open positions; last check 2026-11-06 15:57 ET. Read `git log` for run times. Bot code not run.
- **Still working on:** Nothing.
- **Next step:** Owner decides on the schedule question above.

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
| `paper-trade` workflow (scheduled, weekdays 9:30–3:55 ET) | Running, but about hourly instead of every 5 min | `tick` commits in `git log`; output in `RESULTS.md` | 2026-11-07 |
| Manual price check (`workflow_dispatch`, `bot.py --check`) | Available | `.github/workflows/trade.yml` | 2026-11-07 |

## Review notes

| Date | Reviewer | Finding | Follow-up task / evidence |
|---|---|---|---|
|  |  |  |  |

## Access and activity limits

- This file records only work that its contributors choose to document.
- It does not expose or monitor private Claude conversations, hidden session activity, or unshared Mac files.
- Link evidence to commits, file paths, test output, or screenshots only when those are safe to share.
- Do not place passwords, API keys, tokens, or private personal data here.
