---
name: email-send
description: Send an email via Resend with the right sender identity, auto-CC ian@insynctech.io (standing rule), and resolve recipient shortcuts (teammate handles → their addresses, edited per machine). Use whenever Ian says "email X about Y", "send X a note", "ship that update to the team", "let X know".
---

# Email Send

One way to send mail from this server with the standing CC-Ian rule enforced. No more hand-rolled curl + Resend payloads.

## Steps

1. **Resolve recipients.** Shortcuts the script understands:
   - `ian` → `ian@insynctech.io`
   - any other teammate → add them to `SHORTCUTS` in `email_send.py`; don't guess an address
   - `team` → the addresses you list under `team` in `SHORTCUTS`
   - Anything containing `@` is used as-is.

2. **Pick the sender identity.** Default `InsyncTech <hello@insynctech.io>`. Override flags:
   - `--from-aria` → `Aria · InsyncTech <hello@insynctech.io>`
   - `--from-stump` → `Stump Aria <stump@insynctech.io>` (if verified — script checks)
   - `--from <"Name <email@verified-domain>">` — full override; must be a Resend-verified domain (insynctech.io is verified, ariatravel.com is NOT).

3. **Send.** Auto-CCs Ian unless `--no-cc-ian` is passed (which the script refuses without `--override-standing-rule`, an audit-trail switch):
   ```sh
   python3 ~/.claude/skills/email-send/email_send.py \
       --to "<recipient or shortcut>" \
       --subject "<subject>" \
       --body "<plain text or HTML body>" \
       [--from-aria] [--from-stump] [--from "<custom>"] \
       [--cc "<extra>"] [--reply-to "<addr>"] \
       [--attach <path>] [--attach <path:filename>] ...
   ```
   The script prints `{ok: bool, id: str, status: int}`.

   **Attachments.** Repeatable `--attach` flag. Per-file cap 20 MB, total cap 38 MB (Resend's ceiling minus base64 overhead). Override the displayed filename with `path:filename` syntax (e.g. `--attach /tmp/build.tar.gz:project.tar.gz`). Attachments are base64-encoded and sent via Resend's native attachments API; the file list lands in the splat audit trail.

4. **Body formatting.** The script wraps plain text in `<p>` tags; HTML passes through. Don't include a salutation that says "Hi Ian" if the email is *to* a teammate — they are the primary recipient; Ian is on CC.

5. **Emit a CertusOrdo splat** with `pre={to, subject, sender_identity, override_cc_ian}, post={ok, resend_id}`. Override of the CC-Ian rule shows up in `pre` so it's auditable forever.

6. **Confirm one sentence.** "Sent to X (CC ian) via Resend, id=…".

## Notes

- Resend API key is in `<install-dir>/.env` as `RESEND_API_KEY`.
- The CC-Ian rule comes from the standing memory ([[cc_ian_on_outbound_emails]]). The script enforces it by default and warns loudly on override.
- For anything sensitive (legal, PII, financials), either ask Ian first or set `--reply-to ian@insynctech.io` so replies go to him.
- This skill is dual-use: I send routine updates (status emails, summaries) via this; Ian uses it to fire a quick note without leaving the terminal.
