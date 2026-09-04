# sprint-scaffold

Scaffold a new Aria sprint folder with Filing Cabinet spec_charter.md + Flowstate .claude/agents/pr-review.md + reference/sql/ subdirs. Use when starting a new sprint (e.g. "open sprint 021", "start a sprint for X", "new sprint folder"). Drops a working skeleton in <install-dir>/sprints/NNN_slug/ with all the load-bearing files pre-filled so every shipped item gets an audit-trail home. Validated in Sprint 020 (two-terminal push, 20+ items shipped under this pattern).

## Usage

```sh
ls <install-dir>/sprints/ | sort -n | tail -3
```

---

_README generated from `SKILL.md`; the canonical contract lives there._  
Stdlib-first. Apache 2.0.
