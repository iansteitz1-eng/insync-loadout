# email-send

Send an email via Resend with the right sender identity, auto-CC ian@insynctech.io (standing rule), and resolve recipient shortcuts (teammate handles → their addresses, edited per machine). Use whenever Ian says "email X about Y", "send X a note", "ship that update to the team", "let X know".

## Usage

```sh
python3 ~/.claude/skills/email-send/email_send.py \
       --to "<recipient or shortcut>" \
       --subject "<subject>" \
       --body "<plain text or HTML body>" \
       [--from-aria] [--from-stump] [--from "<custom>"] \
       [--cc "<extra>"] [--reply-to "<addr>"] \
       [--attach <path>] [--attach <path:filename>] ...
```

---

_README generated from `SKILL.md`; the canonical contract lives there._  
Stdlib-first. Apache 2.0.
