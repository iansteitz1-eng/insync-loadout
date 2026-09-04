#!/usr/bin/env python3
"""spinup.py — print Ian's Tip-of-the-Spear state + the five-primitive Flow
State toolkit, so a fresh terminal picks up right where he left off.

Local + fast (no network). Server health is a separate step (/aria-status).
Boris Cherny Flow State: agents · tools · skills · hooks · schedules.
"""
import json
import pathlib
import subprocess

HOME = pathlib.Path.home()
SEP = "─" * 64


def _run(cmd, timeout=2.0):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return ""


def _count(rel, pat):
    d = HOME / rel
    return len(list(d.glob(pat))) if d.exists() else 0


def main():
    # 1) Tip of the Spear — the rolling current-state doc.
    filing = HOME / "Desktop" / "lore"
    if not filing.is_dir() and (HOME / "Desktop" / "claude").is_dir():  # lore-first; fresh boxes default to lore (1.4.4)
        filing = HOME / "Desktop" / "claude"
    sess = filing / "sessions"
    if not sess.is_dir() and (filing / "claude code sessions").is_dir():  # lore-first; fresh boxes default to sessions/ (1.4.4)
        sess = filing / "claude code sessions"
    tip = sess / "_TIP_OF_SPEAR.md"
    if tip.exists():
        print(tip.read_text(encoding="utf-8", errors="ignore").rstrip())
    else:
        print("🗡️  (no _TIP_OF_SPEAR.md yet — run /session-end to seed it)")

    # 2) Recent dated sessions — where the day-to-day state lives.
    print(f"\n📁 RECENT SESSIONS\n{SEP}")
    master = sess
    sess = (
        sorted((p for p in master.glob("*/") if p.is_dir()),
               key=lambda p: p.stat().st_mtime, reverse=True)
        if master.exists() else []
    )
    if not sess:
        print("  (none yet — dated folders appear after a fresh session opens)")
    for p in sess[:3]:
        sm = p / "SESSION.md"
        started = ended = "?"
        if sm.exists():
            for ln in sm.read_text(errors="ignore").splitlines():
                if "**Started:**" in ln:
                    started = ln.split("**Started:**")[-1].strip()
                if "**Ended:**" in ln:
                    ended = ln.split("**Ended:**")[-1].strip()
        print(f"  {p.name}")
        print(f"      started {started}  |  ended {ended}")

    # 3) Five primitives — the Flow State toolkit.
    print(f"\n🧰 FLOW STATE TOOLKIT — 5 primitives\n{SEP}")
    skills = _count(".claude/skills", "*/")
    agents = _count(".claude/agents", "*.md")
    tools = _count("bin", "*")
    # hooks: total command-hooks across all events
    hooks = 0
    try:
        d = json.loads((HOME / ".claude" / "settings.json").read_text())
        hooks = sum(len(b.get("hooks", [])) for ev in d.get("hooks", {}).values() for b in ev)
    except Exception:
        pass
    # schedules: crontab non-comment lines + launchd com.ian*/com.aria*
    cron = [ln for ln in _run(["crontab", "-l"]).splitlines()
            if ln.strip() and not ln.strip().startswith("#")]
    lc = [ln for ln in _run(["launchctl", "list"]).splitlines()
          if any(k in ln for k in ("com.ian", "com.aria", "aria-index", "gmail"))]
    sched = len(cron) + len(lc)

    print(f"  AGENTS     {agents:>2}   ~/.claude/agents/        → Task tool (launch-readiness, security-gate…)")
    print(f"  TOOLS      {tools:>2}   ~/bin/                   → aria · browse · voice · aria-notify · aria-mobile")
    print(f"  SKILLS     {skills:>2}   ~/.claude/skills/        → type / to list (aria-status, email-send…)")
    print(f"  HOOKS      {hooks:>2}   ~/.claude/settings.json  → /hooks (guard · syntax · log · session · voice)")
    print(f"  SCHEDULES  {sched:>2}   crontab + launchd        → newsletter · leads · rsync · gmail · index")
    print(f"\n  Master map → ~/.claude/FLOWSTATE.md")
    print(f"  Next: run /aria-status for live server health.")


if __name__ == "__main__":
    main()
