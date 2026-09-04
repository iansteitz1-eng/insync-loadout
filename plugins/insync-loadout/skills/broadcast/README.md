# broadcast

Send a message to the InsyncTech team-broadcast channel — it pops up in a teammate's Claude Code at their next session start, prefixed "📨 From Ian". Use when Ian says "broadcast X", "tell the team to paste this", "send this to their terminals", "push this to the team".

## Usage

```sh
python3 ~/.claude/skills/broadcast/broadcast.py "your message here"          # to everyone
python3 ~/.claude/skills/broadcast/broadcast.py "paste this: /spinup" --to all
python3 ~/.claude/skills/broadcast/broadcast.py "Everyone — pull the latest kit" --to all
```

---

_README generated from `SKILL.md`; the canonical contract lives there._  
Stdlib-first. Apache 2.0.
