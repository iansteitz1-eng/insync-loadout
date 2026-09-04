---
name: memory-promote
description: Promote a candidate memory from _distill_inbox/ to live memory (the directory CC loads from), validate frontmatter, write the MEMORY.md index entry, and update cross-links. Pairs with /session-end. Use when Ian says "promote that memory", "save that", "yes write it", "make it official", or when reviewing inbox candidates.
---

# Memory Promote

Move a candidate from `_distill_inbox/` to live memory the right way: clean frontmatter, unique slug, index entry, cross-links updated, CertusOrdo splat emitted.

## Steps

1. **List or accept a target.** If the user named a specific candidate (slug or partial), promote that one. Otherwise list everything in the inbox:
   ```sh
   python3 ~/.claude/skills/memory-promote/memory_promote.py --list
   ```

2. **Read the candidate.** Open the inbox file at `~/.claude/projects/-root/memory/_distill_inbox/<slug>.md`. Confirm:
   - The frontmatter has a valid `name`, `description`, and `metadata.type`.
   - The body leads with the rule/fact and (for feedback/project) includes **Why:** and **How to apply:** lines.
   - The slug doesn't already exist in live memory (the script enforces this).

3. **Rewrite the body to final form.** The candidate body has a `### Evidence snippet from session` block — strip it before promoting (the evidence stays in the session JSONL; it doesn't belong in the long-term memory). Replace the "(rewrite this — the snippet below is raw evidence, not memory text)" placeholder with the actual memory content. Add `[[other-slug]]` links to related memories.

4. **Promote.** Run:
   ```sh
   python3 ~/.claude/skills/memory-promote/memory_promote.py <slug>
   ```
   This validates frontmatter, moves the file to `~/.claude/projects/-root/memory/<slug>.md`, appends a one-line entry to `MEMORY.md` (in the appropriate section based on `metadata.type`), and emits a CertusOrdo AGENT_ACTION splat with `pre={inbox_path}, post={live_path, mem_kind}`.

5. **Discard variant.** If the user says "no, drop it" / "discard" / "kill that one", run:
   ```sh
   python3 ~/.claude/skills/memory-promote/memory_promote.py <slug> --discard
   ```
   Deletes the inbox file, emits a splat with `outcome=discarded`. No memory written.

6. **Report.** One line: promoted X → Y / discarded X / listed N candidates. Be terse.

## Notes

- The script will refuse to overwrite an existing live-memory slug. If you really want to update an existing memory, edit it in place — don't promote a new one.
- MEMORY.md index entry format is `- [Title](file.md) — one-line hook` per the auto-memory spec.
- The script adds the entry under a section heading inferred from `metadata.type`: feedback → "🧱 ACTIVE DOCTRINE + STANDING RULES", project → "🏗️ CURRENT BUILD STATE", reference → "📇 CANONICAL REFERENCES", user → near "👤 USER PERSONAL FACTS".
- This skill is dual-use: I run it after `/session-end` to triage candidates, Ian fires it manually for explicit "remember this" moments.
