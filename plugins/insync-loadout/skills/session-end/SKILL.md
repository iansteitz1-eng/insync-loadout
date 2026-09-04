---
name: session-end
description: The session-CLOSE master chain (the bookend to /symphony's open). Does everything session-end always did — scan the transcript for memory-worthy moments → typed candidates → curate/promote — PLUS runs question-economy (Q&A → standing defaults) and loop-rotate (write the handoff → rotate the Tip-of-Spear → archive both), files every finding to its documented home, and ensures each is APPLIED by an embedded hook/schedule. Use at the end of a working session, or when the user says "wrap up", "session end", "save the session", "close out", "what did we learn today".
---

# Session End — the session-CLOSE master chain

Leave the next session smarter than this one. This is the **close bookend to `/symphony`**: it
captures everything this session produced, files it to a documented home, and ensures each finding
is **applied** by the embedded hooks + schedules — so the next session AND the phone AI inherit it
automatically, with zero manual re-briefing.

> Memory dir on this Mac is `~/.claude/projects/-Users-ian/memory/` (NOT `-root`, which is the server).

## The close runs FIVE movements, then FILES + APPLIES

### 1 · EXTRACT — mine the transcript for memory
1. **Run the extractor** → typed candidate files in `…/-Users-ian/memory/_distill_inbox/`:
   ```sh
   python3 ~/.claude/skills/session-end/session_end.py --since 24h --out-inbox
   ```
   Prints `{candidates:[...], session_id, turns_scanned}`; each has `kind` (feedback/project/decision/reference/user), `slug`, `snippet`, `path`.
2. **Read each candidate**, then **curate — don't dump**: belongs in long-term memory (not ephemeral)? updates an existing memory? slug unique? leads with the rule + has **Why:**/**How to apply:**?
3. **Promote / discard / defer.** Promote = finalize body → move to `…/memory/<slug>.md` + add the one-line `MEMORY.md` entry + `[[link]]` related. **Auto-promote `kind: decision`** (Ian's 5/16 directive) — straight to live memory, no gate.
4. **Write the session summary** `project_session_<date>.md` (shipped · open · next) + MEMORY.md entry.

### 2 · QUESTION-ECONOMY — turn Q&A into standing defaults
Run the `question-economy` skill: mine the questions Claude asked + Ian's answers this session →
distill each into a **standing default written to memory** (so Claude asks fewer, only-novel
questions over time) and log the per-session question-rate metric. These defaults are `feedback_*`
memories — applied every future session.

### 3 · ROTATE — the continuity loop (handoff ↔ tip-of-spear)
Write tonight's **HANDOFF** (the diff: ✅ done+durable · ◑ in-flight · ▶ first moves next), then:
```sh
bash ~/bin/loop-rotate.sh
```
It archives the handoff → `handoffs/handoff_<date>.md` AND rotates + archives the rolling current
state → `tots/_TIP_OF_SPEAR_<date>.md`. The handoff content updates the canonical
`sessions/_TIP_OF_SPEAR.md` (`claude code sessions/` on unrenamed boxes) so `/symphony` opens on it. (See `handoffs/_loop.md`.)

### 3.5 · DISCOVER — register new critical systems (the auto-registration backstop)
The three commands stay current ONLY if every new timer/endpoint/gate is in the manifest. This step is the enforcement so registration is never left to memory (the 06-26 drift):
```sh
ssh <your-server> '<install-dir>/bin/critical_systems.py --discover'
```
- **UNREGISTERED live `aria-*.timer`** → classify each: launch/high → add to `timers:` (with `role`+`criticality`+`expect`) in `<install-dir>/config/critical_systems.yaml`; routine → add to `ignore:`. Anything this session shipped MUST land here.
- **STALE manifest entries** (unit gone) → prune or note it moved.
- Any new launch-critical `/healthz/*` endpoint or gate → add under `keystone:`/a new section.
The manifest is in `your backend repo`, so the edit commits in the **next** movement — same pass, zero drift. (Source of truth + checker: `critical_systems.yaml` + `<install-dir>/bin/critical_systems.py`; both read by `/symphony` HAZARDS+CURRENT-STATE and `/checkpoint`.)

### 3.6 · BRAIN METABOLISM — keep the curated brain sharp at close (built 2026-06-27)
The brain self-maintains nightly (04:30 via `refresh_corpus.sh`), but run its sleep-pass at close so it never rots between sessions:
```sh
python3 ~/.aria/bin/brain_importance.py --apply   # 1. recompute importance (stable base − age-decay + citation-bonus; pins behavior/authoritative)
~/.aria/bin/brain_supersede.py                    # 2. flag supersession candidates (report-only, review-gated)
python3 ~/.aria/bin/brain_metabolism.py --apply   # 3. retire superseded(tombstone-guarded)/past-TTL/stale → _archive/retired (reversible)
~/.aria/bin/brain_dedup.py --apply                # 4. collapse near-duplicates → _archive/merged (3_log excluded)
R=~/Desktop/lore; if [ ! -d "$R" ] && [ -d ~/Desktop/claude ]; then R=~/Desktop/claude; fi; ~/bin/aria-semantic index --name brain --roots "$R/canon" ~/.claude/projects/-Users-ian/memory | tail -1
~/.aria/bin/brain_eval.py                          # 5. golden regression guard (recall ≥80% + router) — RED if a change broke recall
~/.aria/bin/brain_sync.sh                          # mirror canon+memory → Obsidian vault (→ iphone)
```
The four verbs are the metabolism (the "sleep pass"): **importance · supersede · retire · dedup** — the brain re-weighs, flags, prunes, and de-dupes itself every close + nightly (04:30 via `refresh_corpus.sh`).
- New memories this session go into their section (`2_memory/<section>/`) in the **file template** (`canon/_meta/FILE_TEMPLATE.md`: frontmatter + CLAIM/DRIVE/DETAIL); agent-written = `validation: candidate` until earned.
- If a **canon head** changed, rotate the old one → `canon/<section>/_history/<stamp>.md` with a one-line diff. The curated `brain` index is the authoritative recall channel — keep it fresh. (Ref `reference_brain_retrieval_architecture` · `project_brain_os_built_2026_06_27`.)

### 4 · COMMIT — save all uncommitted code to git (no work lost on redeploy)
Ian's standing rule (06-19): **whatever hasn't been committed gets committed at session end.** Off-git prod code is silently lost on the next redeploy; uncommitted Mac work (e.g. Superwhisper) is lost to any mishap. Survey his ACTIVE repos and commit per-repo — **safely, never blindly.**

For each active repo (the server `your backend repo` at `<your-server>:/opt/aria`; the Mac repos under `~/dev/*` incl. Superwhisper; any repo touched this session):
1. `git status --short`. Clean → skip. **(safe.directory):** on the box, git throws `dubious ownership` (root vs repo owner) — run `git config --global --add safe.directory /opt/aria` once if it does (06-26 wall).
2. **Commit the MODIFIED tracked files + clearly-source NEW files** by EXPLICIT path (`git add <path1> <path2>`), with a descriptive message tied to the session's work. **NEVER `git add -A` blindly** — that is the trap (it sweeps in secrets, `.bak` litter, and per-user `instances/`/data dirs).
3. **Verify `.gitignore` first.** Confirm `.env`, `.env.*`, `*token*`, `*.pem`, and per-user `instances/`/data dirs are ignored. ⚠️ **The `*.bak` pattern does NOT match our real backups** named `*.bak-<tag>-<timestamp>` (e.g. `main.py.bak-keystone-20260626`) — add `*.bak-*` to `.gitignore` or they slip through (06-26 near-miss). If an untracked path looks like a secret or data, **skip + flag it**, don't commit it.
4. **Push** only where the repo convention is commit-to-remote (your backend repo = direct-to-`main`, one-committer → `pull --rebase` first). Mac-local repos: commit locally unless a remote is source-of-truth.
5. **Report per repo:** committed (files + hash), skipped (+why), and any dirty tree left untouched.

⚠️ **Tracked-secrets rule (detect → flag → handle, don't perpetuate):** never track a secret file; if one was ever committed, untrack it AND rotate the value (it lives in git history until the history is rewritten). Keep secrets in an ignored `.env` and read them at runtime.

### 5 · FILE & APPLY — document what was found + ensure it's applied
Everything this close produced is filed to its documented home, and each is **applied by an embedded
hook/schedule** so it actually takes effect next session:

| Finding | Filed to (documented home) | Applied by (embedded hook/schedule) |
|---|---|---|
| memory candidates | `_distill_inbox/` → live `memory/` + `MEMORY.md` | `recall_hook.sh` (UserPromptSubmit) injects relevant memory; SessionStart loads `MEMORY.md` |
| standing defaults (question-economy) | live `memory/feedback_*.md` | same recall + session-start injection — every session |
| the handoff (the diff) | `claude/handoffs/handoff_<date>.md` | `com.iansteitz.handoff-archive` launchd (hourly + login) |
| rotated tip-of-spear | `sessions/_TIP_OF_SPEAR.md` + `tots/<date>` | `com.iansteitz.tots-archive` launchd + the **SessionStart hook reads it at next `/symphony`** |
| the session transcript/card | `sessions/<session>/SESSION.md` | `com.iansteitz.session-filer` launchd (hourly + login) |
| per-caller voice cards | their instance scope | `aria-session-card-synth.timer` (server, hourly) |

Write a one-screen **CLOSE RECORD** into the current session's folder documenting *what was found,
where each was filed, and which hook/schedule applies it* — that folder IS the documented home.

## QA gate (before any promote / rotate)
Every promoted memory, standing default, and the handoff must trace to a **real transcript moment /
verified outcome** — the handoff says what actually *shipped* (verified, not claimed). No invention.
P0-tagged candidates → Telegram ping to Ian.

## Report
One short paragraph: N promoted, K standing-defaults added, handoff + tip rotated, close record at
`<path>`. Terse.

## Notes
- The extractor is deterministic + idempotent; already-promoted slugs are skipped. Default window 24h (`--since 1h|all`).
- ⚠️ If `session_end.py` scans the wrong project dir (`-root` vs `-Users-ian`), pass `--jsonl <path>` to the real session transcript.
- Registered as the **`session-end` close chain** in `~/.claude/skills/skill-chain/chains.md` (bookend to the `session-start` chain).
