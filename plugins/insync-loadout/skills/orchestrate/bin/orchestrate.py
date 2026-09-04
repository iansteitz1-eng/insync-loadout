#!/usr/bin/env python3
"""
orchestrate.py — the orchestrator BRAIN over the orch.sh harness.

orch.sh = the primitives (spawn/send/read/report on tmux lanes).
orchestrate.py = the brain: a lane roster + charters (LANES.json), a unified live
board across BOTH lane kinds (tmux-human + spawner), window-order gating, and
dispatch routing. Stdlib only; shells to orch.sh + tmux.

Lane kinds:
  tmux-human : long-lived `claude` in tmux orch-<lane>; dispatch via orch.sh send.
  self       : this orchestrator terminal's own work.
  spawner    : a subagent/workflow the CC orchestrator owns; `dispatch` emits the
               task spec for the CC session to run via the Agent tool, and the
               agent reports back with orch.sh report.

Commands:
  board                      unified live board (roster + liveness + STATUS.md)
  charter <lane>             print a lane's charter (role/owns/window/criteria)
  brief <lane>               compose the dispatch brief (charter + STATE pointer)
  dispatch <lane> "<task>"   route a task: tmux->orch.sh send (gated); spawner->emit spec
  gate <action-text>         check an action against the window/destructive gates
  next                       actionable items grouped by window
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HOME = Path(os.environ.get("ORCH_HOME", str(Path.home() / "dev" / "aria-orchestrator")))
ORCH = str(HOME / "orch.sh")
LANES_DIR = HOME / "lanes"
ROSTER = json.loads((HOME / "LANES.json").read_text())
LANES = ROSTER["lanes"]


def _sh(*args):
    return subprocess.run(args, capture_output=True, text=True)


def _tmux_live(lane):
    return _sh("tmux", "has-session", "-t", f"orch-{lane}").returncode == 0


def _status(lane):
    f = LANES_DIR / lane / "STATUS.md"
    if not f.exists():
        return "(no status reported)"
    lines = [l for l in f.read_text().splitlines()[2:] if l.strip()]
    return " ".join(lines)[:160] if lines else "(idle)"


def _last_dispatch(lane):
    f = LANES_DIR / lane / "DISPATCH.log"
    if not f.exists():
        return "none"
    last = f.read_text().splitlines()
    return last[-1].replace("\t", " ")[:80] if last else "none"


def cmd_board(_=None):
    print(f"╔══ ORCHESTRATOR BOARD · {ROSTER['sprint']}")
    print(f"║   state: {ROSTER['state_doc']}   windows: {' → '.join(ROSTER['window_order'])}")
    print("╠" + "─" * 60)
    for lane, d in LANES.items():
        kind = d["kind"]
        if kind == "tmux-human":
            live = "🟢 live(tmux)" if _tmux_live(lane) else "⚫ not-attached"
        elif kind == "self":
            live = "🟢 this-terminal"
        else:
            live = "◇ spawner"
        print(f"║ {lane:13s} [{d['window']:6s}] {live:16s} {kind}")
        print(f"║    role: {d['role']}")
        print(f"║    state: {_status(lane)}")
    print("╚" + "─" * 60)


def cmd_charter(args):
    lane = args[0]
    d = LANES[lane]
    print(f"# CHARTER — {lane}  (window {d['window']}, kind {d['kind']})")
    print(f"role:     {d['role']}")
    print(f"owns:     {', '.join(d['owns'])}")
    print(f"criteria: {d['criteria']}")


def cmd_brief(args):
    lane = args[0]
    d = LANES[lane]
    print(
        f"You are lane '{lane}' ({d['role']}). Read "
        f"{HOME}/{ROSTER['state_doc']} for the convergence plan. Your owned files: "
        f"{', '.join(d['owns'])}. Your acceptance criterion: {d['criteria']}. "
        f"Stay inside your owned files; hand cross-lane needs as diffs. Report progress with: "
        f"{ORCH} report {lane} \"<status>\"."
    )


def _identity_text(lane, spec):
    """The system prompt that makes a spawned Claude session KNOW it is an
    orchestrator-managed lane — its role, owned files, acceptance criterion,
    the report protocol, and the safety gates. Injected via
    `claude --append-system-prompt-file`."""
    owns = ", ".join(spec.get("owns", [])) or "(none specified)"
    return f"""You are an ORCHESTRATOR-MANAGED LANE — not a standalone Claude session.

Lane: {lane}
Managed by: the Aria orchestrator at {HOME} (orch.sh + orchestrate.py). It spawned you, can dispatch tasks into this terminal, and reads the status you publish.
Your role: {spec.get('role', '(unspecified)')}
Files you OWN — edit ONLY these; hand cross-lane needs back as a diff, never edit another lane's files: {owns}
Acceptance criterion (your definition of done): {spec.get('criteria', '(unspecified)')}
Commit window: {spec.get('window', 'n/a')}. Convergence plan to read first: {HOME}/{ROSTER['state_doc']}

OPERATING PROTOCOL (follow without being reminded):
1. After every meaningful step, publish one-line status to the orchestrator board:
   bash {ORCH} report {lane} "<status>"
2. Stay strictly inside your owned files. If you need a change in another lane's file, write it as a diff and report it — do not apply it.
3. NEVER deploy, restart a service, `git push`, or `rm -rf` — those are orchestrator + Ian gated. If your task needs one, report BLOCKED and stop.
4. Lines the orchestrator types into this terminal are DISPATCHES — treat them as task assignments from your manager.
5. When the acceptance criterion is met, report "DONE: <criterion>" and await the next dispatch.

FIRST ACTION NOW: run the report command above to announce you are online and awaiting dispatch, then read the convergence plan.
"""


def cmd_launch(args):  # launch [--no-window] [--auto|--mode <m>] <lane>
    window = True
    claude_args = ""
    rest = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--no-window":
            window = False
        elif a == "--auto":      # auto-accept edits (lane can report/edit without prompts); still gates risky bash
            claude_args = "--permission-mode acceptEdits"
        elif a == "--mode":      # explicit permission mode (plan|acceptEdits|default) — bounded, no skip-permissions alias
            i += 1; claude_args = f"--permission-mode {args[i]}"
        else:
            rest.append(a)
        i += 1
    args = rest
    if not args:
        print("usage: orchestrate.py launch [--no-window] [--auto|--mode <m>] <lane>")
        return 1
    lane = args[0]
    spec = LANES.get(lane)
    if spec is None:
        print(f"⚠ '{lane}' not in roster; using a generic managed identity.")
        spec = {"role": "ad-hoc managed lane", "owns": [], "criteria": "(set by dispatch)", "window": "n/a"}
    if spec.get("kind") == "spawner":
        print(f"'{lane}' is a spawner lane (no tmux terminal); dispatch it via the Agent tool, not launch.")
        return 1
    d = Path(_lane_dir(lane))
    ident = d / "IDENTITY.md"
    ident.write_text(_identity_text(lane, spec))
    cwd = os.path.expanduser(spec.get("cwd", "~"))
    flags = [] if window else ["--headless"]
    if claude_args:
        flags += ["--claude-args", claude_args]
    cmdline = ["bash", ORCH, "spawn", *flags, "--cwd", cwd, "--identity", str(ident), lane]
    r = _sh(*cmdline)
    print(r.stdout.strip() or r.stderr.strip())
    print(f"   identity → {ident}  (lane boots knowing it's managed)")


def _lane_dir(lane):
    p = LANES_DIR / lane
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def _gate_check(text):
    bad = [p for p in ROSTER["gates"]["blocked_phrases"] if p in text.lower()]
    return bad


def cmd_gate(args):
    text = " ".join(args)
    bad = _gate_check(text)
    if bad:
        print(f"⛔ BLOCKED: matches {bad}. {ROSTER['gates']['rule']}")
        return 3
    print(f"✅ allowed: \"{text}\"")
    return 0


def cmd_dispatch(args):
    lane, task = args[0], " ".join(args[1:])
    d = LANES[lane]
    bad = _gate_check(task)
    if bad:
        print(f"⛔ refused dispatch to '{lane}': matches {bad} (gated). Use orch.sh send --force + Ian's go.")
        return 3
    if d["kind"] == "tmux-human":
        r = _sh("bash", ORCH, "send", lane, task)
        print(r.stdout.strip() or r.stderr.strip())
    elif d["kind"] == "spawner":
        (LANES_DIR / lane).mkdir(parents=True, exist_ok=True)
        with open(LANES_DIR / lane / "DISPATCH.log", "a") as f:
            f.write(f"SPAWNER-TASK\t{task}\n")
        print(f"◇ SPAWNER TASK for '{lane}' — orchestrator: run this via the Agent tool, then it reports with `{ORCH} report {lane} ...`:\n   {task}")
    else:
        print(f"lane '{lane}' is kind={d['kind']} — dispatch by working it in this terminal.")


def cmd_next(_=None):
    print("=== actionable by window ===")
    for w in ROSTER["window_order"] + ["post"]:
        items = [(ln, d) for ln, d in LANES.items() if d["window"].startswith(w) or w in d["window"]]
        if not items:
            continue
        print(f"[{w}]")
        for ln, d in items:
            print(f"   {ln}: {d['criteria']}")


CMDS = {"board": cmd_board, "charter": cmd_charter, "brief": cmd_brief,
        "launch": cmd_launch, "gate": cmd_gate, "dispatch": cmd_dispatch, "next": cmd_next}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "board"
    fn = CMDS.get(cmd)
    if not fn:
        print(f"usage: orchestrate.py {{{'|'.join(CMDS)}}}")
        sys.exit(1)
    sys.exit(fn(sys.argv[2:]) or 0)
