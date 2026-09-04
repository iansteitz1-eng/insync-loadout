#!/usr/bin/env python3
"""cc_hook_pre_restart.py — auto-fire the safe-restart fleet guard.

PreToolUse(Bash) hook. On a command that restarts a SHARED service (app-gateway),
it automatically runs the safe-restart fleet check so no one restarts blind:

  • LIVE VOICE CALL  → HARD BLOCK (exit 2). Unambiguous + matches the standing
    voice-deploy rule (never restart while the voice admin endpoint reports active sessions).
  • other lane edited the prod dir recently → ADVISORY warning on stderr, ALLOW
    (exit 0). We can't attribute which staged edits are "yours", so this surfaces
    the fleet state for a human decision rather than false-blocking your own work.
  • any error / non-restart command → ALLOW silently (fail-open: a broken guard
    must never block a legit deploy).

Override: set ARIA_SKIP_RESTART_GUARD=1 to disable entirely.

Hook protocol: reads JSON on stdin ({tool_name, tool_input:{command}}); exit 0 =
allow, exit 2 = block (stderr returned to the model).
"""
import json
import os
import re
import subprocess
import sys

FLEET_CHECK = os.path.expanduser("~/.claude/skills/safe-restart/fleet_check.py")

# Only shared-service restarts trip the guard. Tight on purpose (cheap no-op for
# the thousands of unrelated Bash calls — we return immediately below).
RESTART_RE = re.compile(
    r"(systemctl\s+restart\s+app-gateway"
    r"|restart\s+app-gateway"
    r"|aria-deploy(\.py)?\s+gateway"
    r"|deploy\.py\s+gateway"
    r"|\bsystemctl\s+restart\b.*\bapp-gateway\b)",
    re.I,
)


def _allow():
    sys.exit(0)


def main():
    if os.environ.get("ARIA_SKIP_RESTART_GUARD") == "1":
        _allow()
    try:
        data = json.load(sys.stdin)
    except Exception:
        _allow()

    if data.get("tool_name") != "Bash":
        _allow()
    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    if not RESTART_RE.search(cmd):
        _allow()  # not a shared-service restart → instant no-op

    # --- it IS a shared-service restart: run the guard ---
    # 1) hard voice gate (its own quick probe; fail-open if unreachable)
    try:
        vs = subprocess.run(
            ["ssh", "<your-server>", "curl -s $VOICE_ADMIN_URL/active_sessions"],
            capture_output=True, text=True, timeout=15,
        ).stdout
        m = re.search(r'"active_sessions"\s*:\s*(\d+)', vs)
        if m and int(m.group(1)) > 0:
            sys.stderr.write(
                f"🛑 safe-restart BLOCK: {m.group(1)} live voice session(s) on the voice admin port. "
                f"Never restart app-gateway during a call. Defer until 0, or set "
                f"ARIA_SKIP_RESTART_GUARD=1 to override.\n"
            )
            sys.exit(2)
    except Exception:
        pass  # voice probe failed → don't hard-block on a broken probe

    # 2) advisory fleet check (other lanes' in-flight edits) — warn, never block
    try:
        r = subprocess.run(
            ["python3", FLEET_CHECK, "--no-voice"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 2:  # HOLD = another lane is mid-flight
            tail = "\n".join(
                l for l in r.stdout.splitlines()
                if "OTHER-LANE" in l or "VERDICT" in l or "•" in l
            )
            sys.stderr.write(
                "⚠️  safe-restart ADVISORY before this restart — another lane may be "
                "mid-flight on the prod box:\n" + tail +
                "\n(Allowing: can't tell which edits are yours. Confirm it's clear, "
                "or run /safe-restart --mine \"<your files>\" to verify.)\n"
            )
    except Exception:
        pass  # advisory only — never block on a broken check

    _allow()


if __name__ == "__main__":
    main()
