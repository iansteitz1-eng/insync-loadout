# orchestrate

Spawn and manage parallel Claude Code "lanes" in real terminal windows that boot KNOWING they're orchestrator-managed (role, owned files, acceptance criterion, report protocol injected via system prompt). Dispatch tasks into lanes, read a unified status board, gate dangerous actions, and unify tmux lanes with spawned subagents. Use when Ian says "spawn a lane", "open a managed claude", "orchestrate the lanes", "orchestrator board", "dispatch to <lane>", "run lanes in parallel", or wants one terminal to drive others.

## Usage

```sh
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

---

_README generated from `SKILL.md`; the canonical contract lives there._  
Stdlib-first. Apache 2.0.
