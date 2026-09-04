# question-economy

Near session end, when the user is winding down, or on request, analyze the questions Claude asked Ian and Ian's answers — then distill each answer into a standing default written to memory, so Claude asks fewer (only genuinely novel) questions over time. Tracks a per-session question-rate metric so the decline is measurable. Use when Ian says "wrap up", "winding down", "what did you learn about working with me", "question economy", "/question-economy", or proactively at session close.

## Usage

```sh
python3 ~/.claude/skills/question-economy/question_economy.py --print-trend
```

---

_README generated from `SKILL.md`; the canonical contract lives there._  
Stdlib-first. Apache 2.0.
