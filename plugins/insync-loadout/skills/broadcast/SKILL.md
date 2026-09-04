---
name: broadcast
description: Send a message to the InsyncTech team-broadcast channel — it pops up in a teammate's Claude Code at their next session start, prefixed "📨 From Ian". Use when Ian says "broadcast X", "tell the team to paste this", "send this to their terminals", "push this to the team".
---

# broadcast

The way to push a message or a paste-this command from your terminal into the team's
Claude Code sessions. You post; their session-start hook surfaces it. It's the clean
version of "link my terminal to theirs."

## How it works
- **Send (you):** `/broadcast` writes the message to a JSON channel on the server.
- **Receive (them):** `cc_hook_broadcast.py` (shipped in the flowstate kit) runs at
  every session start, fetches unseen messages addressed to that machine, prints them
  as `📨 Broadcast from ian: …`, and marks them seen locally so they show once.

## Use it
```sh
python3 ~/.claude/skills/broadcast/broadcast.py "your message here"          # PREVIEW only — gate holds
python3 ~/.claude/skills/broadcast/broadcast.py "paste this: /spinup" --yes  # actually send
python3 ~/.claude/skills/broadcast/broadcast.py "Everyone — pull the latest kit" --to all --yes
```
- `--to` = `all` (default) · a teammate's handle · `ian`.
- A recipient sees it the next time they open Claude Code (or run `/spinup`).

## Approval gate (default-safe)
Because a broadcast is outward-facing, **nothing sends without explicit yes**:
- No `--yes` → prints a **preview** (to / from / text) and **holds** — nothing leaves.
- `--yes` (or `--send`) → fires immediately (the "just say yes and go" path).
- Interactive terminal → prompts `[y/N]`. Agent / non-TTY → surfaces the yes/no and holds,
  so the human reviews or simply says "yes" (the agent then adds `--yes` and sends).

## When Ian asks
"Broadcast X" / "tell the team to paste this" / "push this to their terminals" → run the
sender to show the **preview**, then send with `--yes` once Ian confirms (or if he already
said "just send it"). Confirm after: "📡 queued → <target>; they'll see it at next session start."

## Constraints (be honest about these)
- **Sending needs server SSH** — works for Ian now; teammates can send once their
  server login (Sprint 201 #130) is set up, or via a future authenticated endpoint.
- **The channel is team-shared and read over plain HTTPS — treat it as semi-public.**
  Broadcast operational notes and paste-this commands, **never secrets** (keys, PII).
- v2 hardening: move the channel to an authenticated gateway endpoint so anyone can send
  and reads are account-scoped. Tracked, not built yet.
