#!/usr/bin/env python3
"""
cc_hook_syntax_check.py — Claude Code PostToolUse(Write|Edit) syntax gate.

Validates the just-written file by extension and, on failure, feeds the error
straight back so it's caught the instant it's introduced (the class of bug that
took the gateway down last night — a conflict-marker / unparseable file):
  .py            → py_compile
  .json          → json.load
  .js/.mjs/.cjs  → node --check (only if node is installed)
Success or unknown type → silent. Never crashes a session (failure = silent).
"""
import json
import pathlib
import shutil
import subprocess
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    ti = data.get("tool_input") or data.get("input") or {}
    tr = data.get("tool_response") or data.get("output") or {}
    fp = ti.get("file_path") or (tr.get("filePath") if isinstance(tr, dict) else None)
    if not fp:
        return
    p = pathlib.Path(fp)
    if not p.exists():
        return
    ext = p.suffix.lower()
    err = None
    try:
        if ext in (".py", ".pyi"):
            r = subprocess.run([sys.executable, "-m", "py_compile", str(p)],
                               capture_output=True, text=True, timeout=15)
            if r.returncode != 0:
                err = (r.stderr or r.stdout).strip()[-500:]
        elif ext == ".json":
            try:
                json.load(open(p, encoding="utf-8"))
            except Exception as e:
                err = f"{e}"
        elif ext in (".js", ".mjs", ".cjs"):
            if shutil.which("node"):
                r = subprocess.run(["node", "--check", str(p)],
                                   capture_output=True, text=True, timeout=15)
                if r.returncode != 0:
                    err = (r.stderr or r.stdout).strip()[-500:]
    except Exception:
        return
    if err:
        print(json.dumps({
            "decision": "block",
            "reason": f"⚠️ syntax check FAILED on {p.name} — fix before continuing:\n{err}",
        }))


if __name__ == "__main__":
    main()
