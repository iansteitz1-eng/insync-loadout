---
name: spinup
description: Spin up a fresh terminal session into Ian's current working state — the Tip-of-the-Spear current-state doc, recent dated sessions, and the five-primitive Flow State toolkit (agents · tools · skills · hooks · schedules). Use at the start of a session to "pick up right where I left off," or whenever Ian says "spin up", "where are we", "what's the state", "catch me up", "/spinup".
---

# Spinup

Boris Cherny's Flow State, made into one command. Ian opens a fresh terminal and runs this to pick up *exactly* where he left off — no manual re-briefing. Pairs with `/session-end` (the writer that refreshes the state) on the other end of the day.

## Steps

1. **Run the collector** (local, instant — no network):
   ```sh
   python3 ~/.claude/skills/spinup/spinup.py
   ```
   It prints, in order: the **Tip of the Spear** current-state doc, the **3 most recent dated sessions**, and the **five-primitive toolkit** with counts and pointers.

2. **Read it and orient Ian in 3-5 lines.** Lead with where we left off and the single most important open thread. Don't restate the whole dump — synthesize: "We're in <phase>. Last session shipped <X>. The live wire is <top open thread>. Your toolkit: N skills, M agents, K schedules. Want to pick up <thread>?"

3. **Then pull live server health** — run `/aria-status` (or `python3 ~/.claude/skills/aria-status/status.py --brief`). The spinup collector is deliberately local-only and fast; server health is the second beat. Surface any red flag in one line; if green, say "server green" and move on.

4. **Offer the obvious next action** from the Tip of the Spear's open-threads list. One question, not a menu.

## What this is NOT

- It does not modify state — it's a read. The writer is `/session-end`, which refreshes `_TIP_OF_SPEAR.md`.
- It does not spin up terminals or runners — Ian opens one terminal; this loads the *context*, not infrastructure.

## Notes

- The Tip of the Spear lives at `~/Desktop/Claude Code Sessions/_TIP_OF_SPEAR.md`. The dated per-session record lives in the timestamped folders beside it (created by the SessionStart hook).
- The five primitives are mapped in full at `~/.claude/FLOWSTATE.md` — agents, tools, skills, hooks, schedules, each with how-to-invoke.
- Once the SessionStart hook injects the Tip of the Spear automatically, the *automatic* path covers most of this; `/spinup` remains the on-demand re-ground (mid-day, after a long tangent, or to see the full toolkit).
