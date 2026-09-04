#!/usr/bin/env python3
"""
cc_hook_formatter.py — Claude Code PostToolUse hook.

Boris's "last 10%" pattern: after Claude writes or edits a file, run an
autoformatter so the diff stays clean. Hook never blocks — if the formatter
isn't installed or the file fails to format, we silently move on.

Formatters by extension:
  .py             → black + isort
  .ts .tsx .js    → prettier (if available)
  .jsx .json .md  → prettier (if available)

Scope (Mac edition): only files under ~/dev/, ~/measure/, ~/.claude/skills/,
~/.claude/agents/, ~/.claude/hooks/.
Skips: anything in venv/, node_modules/, .git/, /tmp/.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys

_HOME = str(pathlib.Path.home())
ALLOWED_ROOTS = (
    f"{_HOME}/dev",
    f"{_HOME}/measure",
    f"{_HOME}/.claude/skills",
    f"{_HOME}/.claude/agents",
    f"{_HOME}/.claude/hooks",
)
SKIP_FRAGMENTS = ("venv/", "node_modules/", ".git/", "/tmp/", "__pycache__")

FORMATTERS = {
    ".py": [["black", "-q"], ["isort", "-q"]],
    ".ts": [["npx", "--yes", "prettier", "--write", "--log-level", "silent"]],
    ".tsx": [["npx", "--yes", "prettier", "--write", "--log-level", "silent"]],
    ".js": [["npx", "--yes", "prettier", "--write", "--log-level", "silent"]],
    ".jsx": [["npx", "--yes", "prettier", "--write", "--log-level", "silent"]],
    ".json": [["npx", "--yes", "prettier", "--write", "--log-level", "silent"]],
}


def should_format(path: str) -> bool:
    if not path:
        return False
    if not any(path.startswith(r) for r in ALLOWED_ROOTS):
        return False
    if any(f in path for f in SKIP_FRAGMENTS):
        return False
    if not os.path.isfile(path):
        return False
    return True


def run_formatters(path: str, ext: str) -> None:
    cmds = FORMATTERS.get(ext)
    if not cmds:
        return
    for cmd in cmds:
        binary = cmd[0]
        if not shutil.which(binary):
            continue
        try:
            subprocess.run(cmd + [path], capture_output=True, timeout=8)
        except Exception:
            pass  # never block on formatter failures


def main() -> int:
    try:
        payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except Exception:
        return 0

    tool = (payload.get("tool_name") or "").strip()
    if tool not in ("Write", "Edit", "MultiEdit"):
        return 0

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    if not should_format(path):
        return 0

    ext = pathlib.Path(path).suffix.lower()
    run_formatters(path, ext)
    return 0


if __name__ == "__main__":
    sys.exit(main())
