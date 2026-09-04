---
name: orchestrate
description: Spawn and manage parallel Claude Code "lanes" in real terminal windows that boot KNOWING they're orchestrator-managed (role, owned files, acceptance criterion, report protocol injected via system prompt). Dispatch tasks into lanes, read a unified status board, gate dangerous actions, and unify tmux lanes with spawned subagents. Use when Ian says "spawn a lane", "open a managed claude", "orchestrate the lanes", "orchestrator board", "dispatch to <lane>", "run lanes in parallel", or wants one terminal to drive others.
---

# Orchestrate — hybrid multi-lane orchestrator

One terminal drives the others over the disk. A **lane** is an independent Claude
Code session that boots already knowing it's orchestrator-managed and reports its
status back to a shared board.

**Scripts:** `bin/orch.sh` (tmux primitives) + `bin/orchestrate.py` (the brain).
**Runtime home (`ORCH_HOME`, default `~/dev/aria-orchestrator`):** holds `LANES.json`
(the roster), `lanes/<lane>/` (STATUS.md, DISPATCH.log, IDENTITY.md), and the
`STATE_*.md` convergence doc. `bin/LANES.template.json` is a starter roster.

> On a fresh machine: `mkdir -p ~/dev/aria-orchestrator && cp bin/LANES.template.json ~/dev/aria-orchestrator/LANES.json`, then run the scripts from this skill's `bin/` (they default `ORCH_HOME` to that dir). Requires `tmux`; macOS pops iTerm/Terminal windows.

## Why this exists (the hard constraint)
A Claude Code session can't inject prompts into another CC session in a **bare
terminal tab** — no shared control channel. The fix is **topology**: run each
lane's `claude` **inside tmux**, then any process can drive it with `send-keys`
and read it with `capture-pane`. That's what `spawn`/`launch` set up.

## Two lane kinds (hybrid)
- **tmux lane** — a long-lived `claude` in `orch-<lane>` you can sit in AND the
  orchestrator drives. Use `launch` (preferred — injects identity) or `spawn`.
- **spawner lane** — a subagent/workflow this session owns (the `Agent`/`Workflow`
  tools); it reports state with `orch.sh report <lane> "..."` so it shows up on
  the same board.

Control channel = `send` (dispatch). State channel = `lanes/<lane>/STATUS.md`
(clean files) — don't scrape the TUI for state; `read` is a glance only.

## 🔒 MANDATORY — the Lane Contract (canonical, non-negotiable)
Every lane brief MUST embed the seven-clause **Lane Contract** verbatim from `~/orch/briefs/_LANE_CONTRACT.md` before dispatch — no exceptions. It guarantees lanes are **blind to each other** and take **zero initiative** beyond their brief (Ian's standing rule, memory `feedback_lane_blinders_no_initiative`):
1. stay in lane (only listed sprints + owned files) · 2. no initiative beyond the brief (note-and-stop, never act on unlisted work) · 3. **blind to other lanes** (never read/cat/list/grep any `~/orch/` path except your own STATUS) · 4. report UP never sideways · 5. finish = STOP (`state: DONE`, idle is correct) · 6. no commit/deploy/restart/out-of-lane edits · 7. blocked = note in own STATUS + stop.

The orchestrator NEVER feeds a lane any cross-lane context — that's the other half of the guarantee.

**Worktree-per-lane is the canonical default (Ian, 2026-06-15).** Every lane works in its OWN git worktree on branch `lane/<LANE>` — real working-dir + branch isolation so lanes literally cannot see or clobber each other's working files:
- local code lanes: `git worktree add -b lane/<L> ~/orch/worktrees/<L> <base-branch>`
- server lanes: `ssh <host> 'cd <repo> && git worktree add -b lane/<L> <repo>/.worktrees/<L> main'`
- system-file lanes (no repo): author source in a worktree, then install their own unique system paths.

The orchestrator is the SOLE party that merges `lane/*` branches and deploys (server-ahead files via surgical-patch). Clauses 2–4 (no snooping/initiative) still apply on top because lanes share one host filesystem. See also `feedback_lane_siloing_no_shared_file`.

## Commands
```
# brain (bin/orchestrate.py)
orchestrate.py board                         # unified live board: every lane + status
orchestrate.py next                          # actionable items grouped by commit window
orchestrate.py charter <lane>                # a lane's role / owned files / criterion
orchestrate.py launch [--no-window] [--auto|--mode <m>] <lane>
                                             # spawn a MANAGED lane: pops a window, boots
                                             # `claude --append-system-prompt-file IDENTITY.md`
                                             # so it knows it's managed + reports in
orchestrate.py dispatch <lane> "<task>"      # tmux lane -> send-keys (gated); spawner -> emits spec
orchestrate.py gate "<action text>"          # check an action against the safety gates

# primitives (bin/orch.sh)
orch.sh spawn [--headless] [--cwd <dir>] [--identity <file>] [--claude-args "<flags>"] <lane> [cmd]
orch.sh resume [--headless] [--cwd <dir>] [--lane <name>] <session-id> [<session-id>...]
                                             # reopen existing CC sessions AS drivable tmux lanes
                                             # (the controllable version of bare `claude --resume`
                                             # windows). Get IDs from the cc-session-resume skill.
orch.sh send  [--force] <lane> "<text>"      # type INTO a lane (refuses destructive lines)
orch.sh read  <lane> [N]                     # glance at the lane's screen
orch.sh report <lane> "<text>"               # publish lane status (lanes call this)
orch.sh status | list | stop <lane>
```

## Lane identity (what makes a lane "know" it's managed)
`launch` writes `lanes/<lane>/IDENTITY.md` from the roster — role, owned files,
acceptance criterion, the report protocol, and the safety rules — and boots the
lane with `--append-system-prompt-file`. The lane comes up, runs
`orch.sh report <lane> "online"`, reads the convergence plan, and awaits dispatch.

## Autonomy modes (bounded by design)
- default: lane **asks** for permissions (safest).
- `--auto`: `--permission-mode acceptEdits` — auto-accepts edits so a lane can
  report/work without stalling; risky bash still prompts.
- `--mode <m>`: an explicit permission mode (`plan` / `acceptEdits` / `default`).
- **No skip-permissions alias is bundled** — deliberately. A fully-unattended lane
  would need `orch.sh spawn --claude-args "--dangerously-skip-permissions"` typed
  by hand, as an explicit, deliberate choice. Don't add it back into this skill.

## Safety
- `send`/`dispatch` **refuse** lines matching `deploy|restart|rm -rf|git push|shutdown|swap_model`
  unless `--force`. Lane identities forbid deploy/push/restart/rm; cross-lane edits
  go back as diffs. app-gateway restart is the shared, maintainer-gated checkpoint.
- Only touches `orch-`-prefixed tmux sessions; never the live `aria-runner`.
- Closing a lane window never kills the lane (session is detached); reattach with
  `tmux attach -t orch-<lane>`.

## Typical flow
```
orchestrate.py board                                   # see the field
orchestrate.py launch --auto bridge                    # pop a managed lane (knows its charter)
orchestrate.py dispatch bridge "close gate #6; report when verified"
orchestrate.py board                                   # watch status roll in
```
See `~/.claude/projects/-Users-ian/memory/reference_orchestrator_harness.md` for the
full background and the convergence model.
