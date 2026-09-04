---
name: checkpoint
description: Mid-session "log everything now, keep going" — bank current state to memory + refresh the handoff & tip-of-spear WITHOUT closing or rotating. The lightweight bookend between /symphony (open) and /session-end (close). Use when Ian says "checkpoint", "log where we are", "save our spot", "make sure we got everything", "don't lose our place", "we just checkpointed" — and wants to CONTINUE working, not close.
---

# Checkpoint — log without closing

`/session-end` is the CLOSE: it rotates + archives the handoff/tip, runs question-economy, and treats the day as done. **`/checkpoint` is the lighter SAVE:** capture everything produced so far + refresh the live continuity docs so nothing's lost — **then keep working.** Safe to run repeatedly, after every big milestone, so a crash / context-reset / "did we log that?" never loses the spot.

> Memory dir on this Mac: `~/.claude/projects/-Users-ian/memory/` (NOT `-root`).

## The three movements (then confirm + KEEP GOING)

### 0 · HEALTH GATE — fast critical-systems check (don't keep building on a red system)
One pull through the manifest-driven checker on the box:
```sh
ssh <your-server> '<install-dir>/bin/critical_systems.py --health'
```
It reads `<install-dir>/config/critical_systems.yaml` and returns keystone state (db · runner_online · jobs_roundtrip · customer_path · runner_roundtrip) + any **failed launch/high critical timer**. If keystone is 🔴 DEGRADED or a launch timer is failed, **surface it in the confirm line** before continuing — a checkpoint that banks "all good" onto a silently-red system is the exact 06-26 blind spot. (Full audit is `/session-end`'s job; this is the fast gate.)

### 1 · BANK — the durable record (load-bearing)
For each substantive decision / fix / finding since the last checkpoint or `/symphony`: write or **update** the relevant `project_*` / `feedback_*` memory + its one-line `MEMORY.md` index entry. **Curate — don't dump:** bare directives ("yes do X") and extractor noise are NOT memories; the decision + the verified outcome are. Prefer updating an existing memory over creating a duplicate. Every banked line must trace to a real, verified outcome (no invention). P0/urgent findings → also ping Telegram.

### 2 · REFRESH THE TIP — so the next open lands on NOW
Update `~/Desktop/lore/sessions/_TIP_OF_SPEAR.md` (`~/Desktop/claude/claude code sessions/...` on unrenamed boxes): bump the **Last updated** line + prepend/refresh a concise current-state block (✅ shipped · ◑ in-flight · ▶ next). This is what `/symphony` + a fresh terminal read. **Do NOT archive/rotate** — overwrite in place.

### 3 · REFRESH THE HANDOFF — the running diff
Overwrite `~/orch/HANDOFF_<date>_EOD.md` with the current diff (✅ done+durable · ◑ in-flight · ▶ first moves next). **Do NOT run `loop-rotate`** — the dated archiving is `/session-end`'s job (or the hourly launchds). Checkpoint stays fast + non-destructive.

Then: **one-line confirm + keep going.** Do NOT run question-economy, loop-rotate, or any close ritual.

## /checkpoint vs /session-end
| | `/checkpoint` | `/session-end` |
|---|---|---|
| Banks memory + index | ✅ | ✅ |
| Refreshes tip + handoff (in place) | ✅ | ✅ |
| question-economy (Q&A → defaults) | ❌ | ✅ |
| loop-rotate (dated archive of handoff/tots) | ❌ | ✅ |
| Intent | keep working | close the day |

## Notes
- Idempotent + additive — running it twice just re-banks/refreshes; nothing is destroyed.
- The archiving (dated `handoffs/` + `tots/`) still happens automatically via the hourly launchds + at `/session-end`, so skipping it here loses nothing.
- This is the answer to "I already ran session-end but want to keep working and make sure we keep logging" — run `/checkpoint` after each milestone; run `/session-end` once, whenever you actually stop.
