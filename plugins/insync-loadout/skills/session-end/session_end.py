#!/usr/bin/env python3
"""
session_end.py — Scan the current Claude Code session transcript and emit
candidate memory files to ~/.claude/projects/-root/memory/_distill_inbox/.

Usage:
    python3 session_end.py [--since 24h|1h|all] [--out-inbox]

Output: prints a JSON summary to stdout.
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import time

# Portable project-dir resolution (was hardcoded to the server's /root/...-root).
# Order: explicit env override → the server's -root dir if present → the first
# project dir under ~/.claude/projects that actually has a memory/ → HOME default.
def _resolve_projects_dir() -> pathlib.Path:
    env = os.environ.get("CC_PROJECTS_DIR")
    if env:
        return pathlib.Path(env)
    server = pathlib.Path("/root/.claude/projects/-root")
    if server.exists():
        return server
    base = pathlib.Path.home() / ".claude" / "projects"
    # Prefer the project dir matching THIS machine's HOME slug (e.g. /Users/ian -> -Users-ian).
    # This is the real memory home; the old "first sorted -* dir with memory/" grabbed a
    # stray dir literally named "-" that sorts first and happens to have a memory/.
    home_slug = "-" + str(pathlib.Path.home()).strip("/").replace("/", "-")
    home_dir = base / home_slug
    if (home_dir / "memory").is_dir():
        return home_dir
    if base.is_dir():
        # Fall back to the dir with the MOST memory files (the real one), not first-sorted.
        cands = [d for d in base.glob("-*") if (d / "memory").is_dir()]
        if cands:
            return max(cands, key=lambda d: len(list((d / "memory").glob("*.md"))))
    return home_dir


PROJECTS_DIR = _resolve_projects_dir()
MEMORY_DIR = PROJECTS_DIR / "memory"
INBOX_DIR = MEMORY_DIR / "_distill_inbox"

TRIGGERS = {
    "feedback_correction": [
        r"\bdon't\b", r"\bdo not\b", r"\bstop (doing|saying|using)\b",
        r"\bno not that\b", r"\bnever\b(?! mind)", r"\bplease (don't|stop|avoid)\b",
    ],
    "feedback_rule": [
        r"\bfrom now on\b", r"\balways\b", r"\bevery time\b",
        r"\bwhenever\b", r"\bby default\b",
    ],
    "feedback_validation": [
        r"\byes exactly\b", r"\bperfect\b(?!ly)", r"\bkeep doing that\b",
        r"\bthat'?s the right call\b", r"\bnailed it\b", r"\bnice work\b",
    ],
    "feedback_explicit_save": [
        r"\bremember (this|that)\b", r"\bsave this\b", r"\bnote that\b",
        r"\bwrite (this|that) down\b",
    ],
    "decision": [
        r"\bwe decided\b", r"\bwe (will|'ll) (do|build|go with|use|ship)\b",
        r"\blet'?s go with\b", r"\bfinal answer\b", r"\blocked in?\b",
        r"\bthe answer is\b", r"\bgreenlit\b", r"\bgreen ?light(ed)?\b",
        r"\bapproved\b", r"^\s*(yes|yep|yeah|do it|ship it|go)\b",
        r"\byour recommendation\b", r"\bgo with (your|the) (rec|recommendation|pick)\b",
    ],
    "project_status": [
        r"\b(is|are) (shipped|deferred|paused|parked|live|killed|retired)\b",
        r"\bdeadline\b", r"\bdue (by|on)\b", r"\blaunch date\b",
    ],
    "project_ownership": [
        r"\b\w+ owns? \w+", r"\b\w+ is (doing|leading|driving)\b",
    ],
    "reference_pointer": [
        r"https?://\S+", r"\b/(opt|root|etc|tmp|var)/\S+", r"\b[\w.-]+@[\w.-]+\.\w+\b",
    ],
}


def parse_since(s: str) -> float:
    s = s.strip().lower()
    if s in ("all", "always", "forever"):
        return 0.0
    m = re.match(r"^(\d+)\s*([hd])$", s)
    if not m:
        return time.time() - 24 * 3600
    n, unit = int(m.group(1)), m.group(2)
    secs = n * (3600 if unit == "h" else 86400)
    return time.time() - secs


def _line_count(p: pathlib.Path) -> int:
    try:
        with p.open("rb") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def select_session_jsonl(explicit: str = "", session_id: str = "") -> pathlib.Path | None:
    """Pick the session transcript to scan.

    Priority: --jsonl path → --session <id> match → the most SUBSTANTIVE recent
    session, NOT merely the newest-mtime file. The old newest-mtime rule grabbed
    stray 2-turn scratch/hook sessions; we now require a real turn count so the
    active working session wins.
    """
    if explicit:
        p = pathlib.Path(explicit).expanduser()
        return p if p.exists() else None
    files = list(PROJECTS_DIR.glob("*.jsonl"))
    if not files:
        return None
    if session_id:
        for p in files:
            if p.stem == session_id or p.stem.startswith(session_id):
                return p
    # Among recently-touched, non-trivial sessions, prefer the one with the most turns.
    now = time.time()
    recent = [p for p in files if now - p.stat().st_mtime < 6 * 3600 and _line_count(p) >= 20]
    if recent:
        return max(recent, key=_line_count)
    # Fallback: newest non-trivial, else newest overall.
    ranked = sorted(files, key=lambda p: (_line_count(p) >= 20, p.stat().st_mtime), reverse=True)
    return ranked[0] if ranked else None


def extract_text_turns(jsonl_path: pathlib.Path, cutoff_ts: float):
    """Yield (role, ts, text) for human/assistant turns after cutoff."""
    with jsonl_path.open(encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except Exception:
                continue
            ts_raw = rec.get("timestamp") or rec.get("ts") or 0
            if isinstance(ts_raw, str):
                try:
                    ts = dt.datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).timestamp()
                except Exception:
                    ts = 0
            else:
                ts = float(ts_raw) / (1000.0 if ts_raw > 1e12 else 1.0)
            if cutoff_ts and ts < cutoff_ts:
                continue
            msg = rec.get("message") or {}
            role = (rec.get("type") or msg.get("role") or rec.get("role") or "").lower()
            content = msg.get("content") if isinstance(msg, dict) else None
            text_parts = []
            if isinstance(content, str):
                text_parts.append(content)
            elif isinstance(content, list):
                for blk in content:
                    if isinstance(blk, dict) and blk.get("type") == "text":
                        text_parts.append(blk.get("text", ""))
            if not text_parts and rec.get("display"):
                text_parts.append(rec["display"])
            text = "\n".join(t for t in text_parts if t).strip()
            if not text:
                continue
            yield role, ts, text


def classify_snippet(text: str) -> list[str]:
    """Return list of trigger-category names that match this text."""
    hits = []
    low = text.lower()
    for cat, pats in TRIGGERS.items():
        for p in pats:
            if re.search(p, low):
                hits.append(cat)
                break
    return hits


def slugify(s: str, max_len: int = 50) -> str:
    s = re.sub(r"[^\w\s-]", "", s.lower())
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:max_len] or "candidate"


def kind_for(cats: list[str]) -> tuple[str, str]:
    """Return (memory_type, slug_prefix)."""
    if any(c == "decision" for c in cats):
        return "decision", "project_decision"
    if any(c.startswith("feedback_") for c in cats):
        return "feedback", "feedback"
    if any(c.startswith("project_") for c in cats):
        return "project", "project"
    if "reference_pointer" in cats:
        return "reference", "reference"
    return "feedback", "feedback"


def existing_slugs() -> set:
    slugs = set()
    for p in MEMORY_DIR.glob("*.md"):
        slugs.add(p.stem)
    return slugs


def write_candidate(kind: str, slug_prefix: str, snippet: str,
                    role: str, ts: float, session_id: str) -> pathlib.Path:
    seed = re.sub(r"\s+", " ", snippet)[:80]
    slug = f"{slug_prefix}_{slugify(seed)}"
    # Disambiguate against existing live memory + inbox
    taken = existing_slugs() | {p.stem for p in INBOX_DIR.glob("*.md")}
    base_slug = slug
    i = 2
    while slug in taken:
        slug = f"{base_slug}_v{i}"
        i += 1

    when = dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M UTC")
    body = (
        f"---\n"
        f"name: {slug}\n"
        f"description: CANDIDATE (auto-extracted {when}) — review before promoting.\n"
        f"metadata:\n"
        f"  type: {kind}\n"
        f"  candidate: true\n"
        f"  source_role: {role}\n"
        f"  source_session: {session_id}\n"
        f"---\n\n"
        f"## Draft memory\n\n"
        f"(rewrite this — the snippet below is raw evidence, not memory text)\n\n"
        f"**Why:** \n\n"
        f"**How to apply:** \n\n"
        f"---\n\n"
        f"### Evidence snippet from session\n\n"
        f"> {snippet[:600].replace(chr(10), chr(10) + '> ')}\n"
    )
    out = INBOX_DIR / f"{slug}.md"
    out.write_text(body, encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="24h")
    ap.add_argument("--out-inbox", action="store_true")
    ap.add_argument("--jsonl", default="", help="explicit session transcript path to scan")
    ap.add_argument("--session", default="", help="session id (or prefix) to scan")
    args = ap.parse_args()

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    jsonl = select_session_jsonl(args.jsonl, args.session)
    if not jsonl:
        print(json.dumps({"error": "no session jsonl found", "candidates": []}))
        return

    cutoff = parse_since(args.since)
    session_id = jsonl.stem
    candidates = []
    turns_scanned = 0

    for role, ts, text in extract_text_turns(jsonl, cutoff):
        turns_scanned += 1
        if role not in ("user", "human"):
            continue
        cats = classify_snippet(text)
        if not cats:
            continue
        kind, prefix = kind_for(cats)
        path = write_candidate(kind, prefix, text, role, ts, session_id)
        candidates.append({
            "kind": kind,
            "slug": path.stem,
            "path": str(path),
            "categories": cats,
            "snippet_head": text[:120],
            "ts": dt.datetime.fromtimestamp(ts).isoformat(),
        })

    print(json.dumps({
        "session_id": session_id,
        "session_jsonl": str(jsonl),
        "turns_scanned": turns_scanned,
        "candidates_emitted": len(candidates),
        "inbox": str(INBOX_DIR),
        "candidates": candidates,
    }, indent=2))


if __name__ == "__main__":
    main()
