# session-end

Close out the current Claude Code session by scanning the transcript for memory-worthy moments (user corrections, validated approaches, decisions, project state changes) and writing candidate memory files to the _distill_inbox/ for Ian's review. Use at the end of a working session, or whenever the user says "wrap up", "session end", "save the session", "what did we learn today".

## Usage

```sh
python3 ~/.claude/skills/session-end/session_end.py --since 24h --out-inbox
```

---

_README generated from `SKILL.md`; the canonical contract lives there._  
Stdlib-first. Apache 2.0.
