#!/usr/bin/env python3
"""
cc_hook_guard.py — Claude Code PreToolUse(Bash) destructive-command guard.

The one hook that can BLOCK. Two tiers:
  • DENY  — catastrophic / irreversible (rm -rf on / or ~, fork bomb, dd to a
            raw disk, mkfs, chmod -R 777 /, redirect to /dev/sdX). Hard stop.
  • ASK   — dangerous-but-sometimes-legit (rm -rf anything, git reset --hard,
            git clean -f, git push --force, SQL DROP/TRUNCATE). Prompts Ian.
Everything else: allow silently (exit 0, no output).

Inspects the whole command string, so it also catches the dangerous bit inside
`ssh <your-server> '...'`. Never crashes a session (failure = allow).
Reinforces Ian's standing "we don't like to delete things" preference.
"""
import json
import re
import sys

DENY = [
    (r"\brm\s+-[a-z]*\s*(-[a-z]+\s+)*(/|~|\$HOME)(\s|/?\*|$)", "rm -rf targeting / ~ or a root path"),
    (r":\(\)\s*\{\s*:\s*\|\s*:?\s*&?\s*\}\s*;\s*:", "fork bomb"),
    (r"\bdd\b[^|]*\bof=/dev/(sd|nvme|disk|hd|mmcblk)", "dd to a raw disk device"),
    (r"\bmkfs(\.\w+)?\b", "filesystem format (mkfs)"),
    (r">\s*/dev/(sd|nvme|disk|hd|mmcblk)", "redirect onto a raw disk device"),
    (r"\bchmod\s+-R\s+0?777\s+/(\s|$)", "chmod -R 777 on /"),
]
ASK = [
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r", "rm -rf (recursive force delete)"),
    (r"\bgit\s+reset\s+--hard", "git reset --hard (discards uncommitted work)"),
    (r"\bgit\s+clean\s+-[a-z]*f", "git clean -f (deletes untracked files)"),
    (r"\bgit\s+push\b[^|;&]*(--force\b|\s-f\b)", "git force-push (rewrites remote history)"),
    (r"\b(drop|truncate)\s+(table|database|schema)\b", "destructive SQL (DROP/TRUNCATE)"),
]


def decide(cmd: str):
    for pat, why in DENY:
        if re.search(pat, cmd, re.I):
            return "deny", why
    for pat, why in ASK:
        if re.search(pat, cmd, re.I):
            return "ask", why
    return "allow", ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if (data.get("tool_name") or data.get("tool") or "") != "Bash":
        sys.exit(0)
    cmd = ((data.get("tool_input") or data.get("input") or {}).get("command") or "")
    if not cmd:
        sys.exit(0)
    decision, why = decide(cmd)
    if decision == "allow":
        sys.exit(0)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"🛡️ guard: {why}.",
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
