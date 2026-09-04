#!/usr/bin/env python3
"""broadcast.py — post a message to the InsyncTech team-broadcast channel.

Anyone running the flowstate kit sees unseen broadcasts at their next session
start (via cc_hook_broadcast.py). This is the sender; the hook is the receiver.

Channel: a JSON file on the server, web-served at
  https://<your-server>/team-broadcast.json
Writing requires server SSH (Ian has it). Reading is open to anyone with the kit.

  python3 broadcast.py "your message" [--to all|<teammate>|ian] [--from ian]

NOTE: the channel is team-shared and read over plain HTTPS — treat it as
semi-public. Broadcast operational notes ("paste this"), never secrets.
"""
from __future__ import annotations

import argparse
import base64
import subprocess
import sys

REMOTE = r'''
import json, base64, sys, time, os
F = "/var/www/downloads/team-broadcast.json"
text = base64.b64decode(sys.argv[1]).decode("utf-8")
to, frm = sys.argv[2], sys.argv[3]
try:
    data = json.load(open(F))
    if not isinstance(data, list): data = []
except Exception:
    data = []
mid = "bc-%d-%d" % (int(time.time()), len(data) + 1)
data.append({"id": mid, "from": frm, "to": to, "ts": int(time.time()), "text": text})
data = data[-200:]  # keep the channel bounded
json.dump(data, open(F, "w"))
try: os.chmod(F, 0o644)
except Exception: pass
print("queued %s -> %s" % (mid, to))
'''


def _confirm(a) -> bool:
    """Approval gate. Show exactly what will go out; send only on explicit yes.

    - `--yes` / `--send` : skip the gate and fire (the "just say yes and go" path).
    - interactive TTY     : prompt [y/N].
    - agent / no TTY       : DO NOT send — surface the yes/no so the human decides;
                             re-running with --yes (or saying "yes") sends it.
    """
    print("📡 BROADCAST — review before send")
    print(f"   to   : {a.to}")
    print(f"   from : {a.frm}")
    print(f"   text : {a.message}")
    print("   channel: team-shared + semi-public — operational notes only, never secrets")
    if a.yes:
        print("   ✓ --yes given → sending now")
        return True
    if sys.stdin.isatty():
        try:
            ans = input("   Ready to broadcast? [y/N] ").strip().lower()
        except EOFError:
            ans = ""
        return ans in ("y", "yes")
    print("   ❔ READY TO SEND? — held, nothing sent yet.")
    print("      Say 'yes' (I'll add --yes and fire it) or re-run with --yes.")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("message")
    ap.add_argument("--to", default="all", help="all | <teammate handle> | ian")
    ap.add_argument("--from", dest="frm", default="ian")
    ap.add_argument("--host", default="<your-server>")
    ap.add_argument("--yes", "--send", action="store_true", dest="yes",
                    help="skip the approval gate and send now")
    a = ap.parse_args()

    if not _confirm(a):
        print("⏸  held — nothing broadcast.")
        return

    b64 = base64.b64encode(a.message.encode("utf-8")).decode("ascii")
    cmd = ["ssh", a.host, "python3 - '%s' '%s' '%s'" % (b64, a.to, a.frm)]
    r = subprocess.run(cmd, input=REMOTE, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        print("broadcast FAILED:", (r.stderr or r.stdout).strip(), file=sys.stderr)
        sys.exit(1)
    print("📡 " + r.stdout.strip() + "  (recipients see it at their next session start)")


if __name__ == "__main__":
    main()
