# MANIFEST — insync-loadout v0.1.0

Everything bundled in the plugin, one line each. Copied read-only from `~/.claude/skills`
and `~/.claude/agents`; source loadout is untouched.

## Marketplace
- `.claude-plugin/marketplace.json` — catalog named **insync**, owner InsyncTech, 1 plugin.

## Plugin manifest
- `plugins/insync-loadout/.claude-plugin/plugin.json` — `insync-loadout` v0.1.0; declares
  `skills`, `agents`, `hooks` paths.

## Skills (13)

### Session lifecycle
- **spinup** — spin a fresh session into current working state (the OPEN).
- **checkpoint** — mid-session "log everything, keep going" (the SAVE).
- **session-end** — the CLOSE chain: memory pass, question-economy, handoff rotate.

### Orchestration & planning
- **orchestrate** — spawn/manage parallel Claude Code lanes in real terminal windows.
- **skill-chain** — run an ordered sequence of skills as one named macro.
- **goal-to-plan** — turn a vague ask into a spec charter + agent-ready lane brief.
- **premortem** — imagine failure modes → cheapest guard, before a risky change/deploy.
- **wash** — package a fork/uncertainty and wash it through Claude.ai for fresh synthesis.
- **sprint-scaffold** — drop a sprint folder skeleton (charter + pr-review + reference/sql).
  Note: defaults to `<install-dir>/sprints/` — repoint base dir per machine.

### Comms
- **email-send** — send via Resend, auto-CC Ian, resolve teammate shortcuts.
  Note: reads `RESEND_API_KEY` from `<install-dir>/.env` at runtime — repoint per machine (no key committed).
- **broadcast** — push a message to the InsyncTech team-broadcast channel.
  Note: defaults to `--host <your-server>` — repoint per machine.

### Memory / meta
- **memory-promote** — promote a candidate memory from the distill inbox into live memory.
- **question-economy** — distill Q&A into standing defaults; track question-rate decline.

## Agents (11)
- **orchestrator** — user-facing conversation surface; spawns builders, never edits code.
- **builder** — scoped unit of work; edits/calls/runs; emits events; up to 8 parallel.
- **janitor** — post-builder serial cleanup: conflict/credential scan, archive.
- **observer** — subscribes to the workspace event stream; surfaces blocked/high-cost/cross-builder alerts.
- **memory-curator** — reads the session transcript, proposes long-term memory candidates.
- **cost-reviewer** — Anthropic/Twilio/EL/Resend burn analysis + ranked cuts (read-only).
- **doctrine-reviewer** — reviews a plan/change against doctrine; approve / request-changes / rethink.
- **security-gate** — pre-deploy review: secrets, permissions, injection, SSH policy (read-only).
- **launch-readiness** — gates met/unmet vs launch date; go/no-go authority.
- **splat-economist** — splat-economy analytics: volume, layers, routing, billing (read-only).
- **fellows-orchestrator** — drives the Anthropic Fellows application project end-to-end.

> Agents ship whole: they're role/prompt/tool definitions, not wired to any secret.

## Hooks

### Wired in `hooks/hooks.json` (portable, `${CLAUDE_PLUGIN_ROOT}`-relative)
- **PreToolUse / Bash** → `cc_hook_guard.py` — guard dangerous bash before it runs.
- **PreToolUse / Edit|Write** → `cc_hook_canon_gate.py` — gate edits against canon.
- **PostToolUse / Write|Edit|MultiEdit** → `cc_hook_formatter.py` — auto-format edited files.
- **PostToolUse / Write|Edit|MultiEdit** → `cc_hook_syntax_check.py` — syntax-check edited files.

### Bundled but NOT wired (optional adapter)
- `hooks/scripts/cc_hook_pre_restart.py` — safe-restart in-flight gate; wire under PreToolUse/Bash if running a shared service.

### Documented but NOT bundled (machine-specific — post-install, per-machine)
Ian's live `settings.json` has 21 scripts across 7 events. The following are Ian-personal
(voice stack, disk-lane fabric, ordo graph, personal paths) and are intentionally left out:
- Notification: `cc_hook_notify.py`, `cc_hook_voice_notify.py`, Tink.aiff
- SessionStart: `cc_hook_session_start.py`, `aria-saves-funnel`, `screenshot-filer.sh`, `wash-filer.sh`, `ordo-sync`, `certus-pull`, `cc_hook_disk_lane.py`
- PostToolUse: `cc_hook_log.py`, `cc_hook_voice_toolstate.py`
- Stop: `cc_hook_stop.py`, `cc_hook_voice_speak.py`, Purr.aiff, `aria-checkpoint`
- UserPromptSubmit: `cc_hook_voice_interrupt.py`, `recall_hook.sh`
- PreCompact: `cc_hook_precompact.py`

## Docs
- `README.md` — what this is, ship-set rationale, install flow, post-install hook wiring.
- `MANIFEST.md` — this file.
