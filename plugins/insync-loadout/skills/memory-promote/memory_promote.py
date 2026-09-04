#!/usr/bin/env python3
"""
memory_promote.py — Promote a _distill_inbox/<slug>.md candidate to live
memory or discard it. Validates frontmatter, writes MEMORY.md index entry,
emits a CertusOrdo splat.

Usage:
    python3 memory_promote.py --list                  # list candidates
    python3 memory_promote.py <slug>                  # promote
    python3 memory_promote.py <slug> --discard        # delete
"""
import argparse
import json
import os
import pathlib
import re
import sys


# Portable memory-dir resolution (was hardcoded to the server's /root/...-root,
# which crashed for every non-root user — read-only /root). Mirrors
# session_end.py's resolver. Order: explicit env override → server -root if
# present (Ian) → this machine's HOME-slug project dir → the dir with the most
# memory files → HOME default (caller mkdirs).
def _resolve_mem_dir() -> pathlib.Path:
    env = os.environ.get("ARIA_MEMORY_DIR") or os.environ.get("CC_PROJECTS_DIR")
    if env:
        p = pathlib.Path(env)
        return p if p.name == "memory" else p / "memory"
    server = pathlib.Path("/root/.claude/projects/-root/memory")
    if server.exists():
        return server
    base = pathlib.Path.home() / ".claude" / "projects"
    home_slug = "-" + str(pathlib.Path.home()).strip("/").replace("/", "-")
    home_mem = base / home_slug / "memory"
    if home_mem.is_dir():
        return home_mem
    if base.is_dir():
        cands = [d / "memory" for d in base.glob("-*") if (d / "memory").is_dir()]
        if cands:
            return max(cands, key=lambda d: len(list(d.glob("*.md"))))
    return home_mem  # default — may not exist yet; caller creates it


MEM_DIR = _resolve_mem_dir()
INBOX = MEM_DIR / "_distill_inbox"
INDEX = MEM_DIR / "MEMORY.md"

SECTION_BY_TYPE = {
    "feedback":  "## 🧱 ACTIVE DOCTRINE + STANDING RULES",
    "project":   "## 🏗️ CURRENT BUILD STATE (2026-05-15 SHIPS)",
    "reference": "## 📇 CANONICAL REFERENCES",
    "user":      "## 📇 CANONICAL REFERENCES",
    "decision":  "## 🏗️ CURRENT BUILD STATE (2026-05-15 SHIPS)",
}

ICON_BY_TYPE = {
    "feedback":  "🔁",
    "project":   "🏗️",
    "reference": "📇",
    "user":      "👤",
    "decision":  "🎯",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) — frontmatter is the YAML-ish block
    between leading '---' lines. We parse it loosely (no yaml dep)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    block = text[4:end].strip()
    body = text[end + 4:].lstrip("\n")
    fm: dict = {}
    cur_key = None
    for line in block.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            cur_key = m.group(1)
            val = m.group(2).strip()
            if val:
                fm[cur_key] = val
            else:
                fm[cur_key] = {}
        elif cur_key and isinstance(fm.get(cur_key), dict):
            m2 = re.match(r"^\s+(\w+):\s*(.*)$", line)
            if m2:
                fm[cur_key][m2.group(1)] = m2.group(2).strip()
    return fm, body


def strip_evidence_block(body: str) -> str:
    """Remove the `### Evidence snippet from session` block + horizontal rule."""
    return re.split(r"\n---\s*\n+### Evidence snippet", body, maxsplit=1)[0].rstrip() + "\n"


def list_candidates() -> list[dict]:
    out = []
    for p in sorted(INBOX.glob("*.md")):
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        meta = fm.get("metadata") or {}
        out.append({
            "slug": p.stem,
            "path": str(p),
            "type": meta.get("type") if isinstance(meta, dict) else None,
            "description": fm.get("description", "")[:120],
        })
    return out


def emit_splat(target: str, pre: dict, post: dict, outcome: str = "ok") -> bool:
    try:
        sys.path.insert(0, "/opt/aria")
        from certus_trace import emit as ct_emit, Nodes as CTNodes  # type: ignore
        ct_emit(
            CTNodes.AGENT_ACTION, target,
            f"skill: memory-promote ({outcome})",
            pre=pre, post=post,
        )
        return True
    except Exception as e:
        print(f"warn: splat emit failed: {e}", file=sys.stderr)
        return False


def index_section_for(kind: str) -> str:
    return SECTION_BY_TYPE.get(kind, "## 🏗️ CURRENT BUILD STATE (2026-05-15 SHIPS)")


def insert_into_index(slug: str, description: str, kind: str) -> bool:
    icon = ICON_BY_TYPE.get(kind, "🧱")
    line = f"- **{icon} [{slug.replace('_', ' ').title()}]({slug}.md) — {description[:140]}**"
    section_marker = index_section_for(kind)
    if not INDEX.exists():
        INDEX.write_text(f"# Memory Index\n\n{section_marker}\n\n{line}\n", encoding="utf-8")
        return True
    text = INDEX.read_text(encoding="utf-8")
    # Idempotent: skip if already linked
    if f"({slug}.md)" in text:
        return False
    if section_marker in text:
        text = text.replace(section_marker, section_marker + "\n\n" + line, 1)
    else:
        text = text.rstrip() + f"\n\n{section_marker}\n\n{line}\n"
    INDEX.write_text(text, encoding="utf-8")
    return True


def promote(slug: str) -> int:
    src = INBOX / f"{slug}.md"
    if not src.exists():
        print(f"error: candidate not found: {src}", file=sys.stderr)
        return 2
    dst = MEM_DIR / f"{slug}.md"
    if dst.exists():
        print(f"error: live memory already exists: {dst} — edit it instead",
              file=sys.stderr)
        return 3
    raw = src.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw)
    if not fm.get("name"):
        print("error: candidate frontmatter missing 'name'", file=sys.stderr)
        return 4
    meta = fm.get("metadata") or {}
    kind = (meta.get("type") if isinstance(meta, dict) else None) or "feedback"

    # Drop the candidate marker + evidence block from the body
    cleaned_body = strip_evidence_block(body)
    # Rebuild frontmatter without the candidate marker
    new_fm_lines = ["---"]
    for k in ("name", "description"):
        if k in fm:
            new_fm_lines.append(f"{k}: {fm[k]}")
    new_fm_lines.append("metadata:")
    new_fm_lines.append(f"  type: {kind}")
    new_fm_lines.append("---")
    new_text = "\n".join(new_fm_lines) + "\n\n" + cleaned_body

    dst.write_text(new_text, encoding="utf-8")
    indexed = insert_into_index(slug, fm.get("description", ""), kind)
    src.unlink()
    emit_splat(slug, {"inbox": str(src), "kind": kind},
               {"live": str(dst), "indexed": indexed}, outcome="promoted")
    print(json.dumps({"promoted": slug, "to": str(dst), "kind": kind,
                      "indexed": indexed}, indent=2))
    return 0


def discard(slug: str) -> int:
    src = INBOX / f"{slug}.md"
    if not src.exists():
        print(f"error: candidate not found: {src}", file=sys.stderr)
        return 2
    src.unlink()
    emit_splat(slug, {"inbox": str(src)}, {"deleted": True}, outcome="discarded")
    print(json.dumps({"discarded": slug}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--discard", action="store_true")
    args = ap.parse_args()

    if args.list or not args.slug:
        cands = list_candidates()
        print(json.dumps({"count": len(cands), "candidates": cands}, indent=2))
        return 0
    if args.discard:
        return discard(args.slug)
    return promote(args.slug)


if __name__ == "__main__":
    sys.exit(main())
