# Chain registry

Named skill chains. Each runs via `/skill-chain <name>` (see SKILL.md for the run protocol). Only chains whose skills are installed are `STATUS: live`; others are marked.

---

## session-start
- **STATUS:** live ✅ (all skills installed; this is the `/symphony` master-open chain)
- **trigger:** manual (`/symphony` | "start the session" | "spin me up for the day")
- **bar:** Ian opens the day with full, current, cross-device context and ONE clear next action — never re-briefing by hand, never acting on stale/flagged context. Every claim traces to source.
- **steps:**
  1. `spinup` — Tip-of-Spear + recent dated sessions + five-primitive toolkit → "where we left off."
  2. `session-context` — digest last 3-5 SESSIONS → substantive day-summary card on the web UI (/memory-tab); flags any DO-NOT-TRUST session.
  3. `call-context` — scrub last 3-5 CALLS, flag handoff-gaps (card blind), backfill so the voice context card reflects them.
  4. `telegram-ingest` — ingest pending links/files Ian sent Aria; clear the queue.
  5. `aria-intents` (review only) — proposed action items from calls; **recency-caution** (stale/foreign-intent bug), never auto-fire.
  6. `aria-status` — live stack health in one line.
- **QA gate (before steps 2/3 writes + before the synthesis):** every synthesized line traces to a real session/transcript/file/row; flagged-session claims are NOT trusted; backfilled handoffs are grounded in actual turns. No invention.
- **output / write-back:** a one-screen orientation (where we left off · re-verify · phased path forward · one next action) + two refreshed continuity cards (day card + context card).

## deploy-hygiene
- **STATUS:** live ✅ (all skills installed; run end-to-end 2026-06-09 to ship the recent-calls dedup fix)
- **trigger:** manual | intent:"deploy|ship|patch prod"
- **bar:** the specific change is the code now serving traffic, health green, 0 new journal errors — proven in-product, not code-trace.
- **steps:**
  1. `premortem` — name the change + 3–5 failure modes → cheapest guard each.
  2. `surgical-patch` — apply the exact-match edit to the hot/shared file (timestamped backup, abort-on-drift).
  3. `safe-restart` — GREEN/HOLD gate: 0 active voice calls + no other lane mid-edit on prod.
  4. `aria-deploy` — chmod + restart the right unit, wait for /health green.
  5. `deploy-verify` — data-driven PASS/FAIL that THIS change is live.
- **QA gate (before step 3→4 restart):** boot-test (`import main`) passes AND `safe-restart` is GREEN. No restart otherwise.
- **output / write-back:** the deploy + a deploy splat; outcome noted in the session/continuity memory.

## goal-to-plan
- **STATUS:** live ✅ (installed)
- **trigger:** manual | intent:"build|fix|do <X>" (a fuzzy goal)
- **bar:** a fresh agent could execute the brief with zero follow-up questions, and the result is objectively checkable against one acceptance criterion.
- **steps:**
  1. `goal-to-plan` — compress goal → one acceptance criterion; name the 4 things (goal/skills/tools/context).
  2. `premortem` — failure modes → guards (becomes the Risks section).
  3. `sprint-scaffold` — (only if multi-item/multi-session) drop the spec_charter in a real sprint home.
- **QA gate (before dispatch):** the plan has an objective bar + a premortem; never dispatch a lane without both.
- **output / write-back:** spec_charter + a `/orchestrate` lane-dispatch block.

## client-delivery
- **STATUS:** defined — skills live in the client-delivery pack, NOT installed on this Mac (`doc-consistency-check`, `client-hub-publish` absent here). Run from a host that has the pack.
- **trigger:** manual | intent:"send the client|deliver|publish the hub"
- **bar:** the deliverable is internally consistent, branded, and reaches the client's own access surface (not just Ian's Mac).
- **steps:**
  1. `doc-consistency-check` — reconcile facts/figures across the doc set.
  2. `doc-to-pdf` — render the branded, multi-page PDF deliverable.
  3. `client-hub-publish` — publish to the client's access-controlled hub.
- **QA gate (before publish):** every claim traceable to source; nothing invented/overpromised; sensitive docs stay access-controlled ([[feedback_client_delivery_surface]]).
- **output / write-back:** the published hub + a delivery record.

## proposal
- **STATUS:** template (the Greg/LCA flagship shape — constituent skills NOT built yet; shown as the target pattern)
- **trigger:** event:"RFP detected in transcript/inbox"
- **bar:** ships live in ~3 min, sounds like Ian (not AI), every line pulled from real conversations/data.
- **steps:**
  1. `build-proposal-microsite` *(TODO)* — branded microsite, not raw email.
  2. `copy-voice` *(TODO)* — "sounds like me," grounded in real call transcripts.
  3. `qa-against-source` *(TODO)* — no overpromising, nothing invented; everything pulled from transcripts/data.
- **QA gate (before send):** step 3 IS the gate — the anti-hallucination check is the whole point of the chain.
- **output / write-back:** the live proposal URL + the customer signal feeds back into the brain.

## session-end
- **STATUS:** live ✅ (the CLOSE bookend to `session-start`; installed: `session-end`, `question-economy`; `loop-rotate` script)
- **trigger:** manual (`/session-end` | "wrap up" | "save the session" | "close out") | session close
- **bar:** the next session AND the phone AI inherit EVERYTHING this session produced — memory, standing defaults, the diff, the rotated current-state — with zero manual re-briefing, each finding actually APPLIED by an embedded hook/schedule.
- **steps:**
  1. `session-end` (extract) — transcript → typed memory candidates → curate/promote (auto-promote `kind: decision`) → session summary.
  2. `question-economy` — Q&A → standing defaults written to memory (asks fewer questions over time) + the question-rate metric.
  3. `loop-rotate` — write the handoff (the diff) → rotate the canonical Tip-of-Spear → archive both (`handoffs/` + `tots/`).
  4. **file & apply** — document each finding's home + the embedded hook/schedule that applies it (recall_hook · session-filer · handoff-archive · tots-archive · SessionStart reads the tip next open).
- **QA gate (before promote/rotate):** every promoted memory + standing default + the handoff traces to a real transcript moment / verified outcome — the handoff says what actually *shipped*, not claimed. No invention.
- **output / write-back:** promoted memory + standing defaults + dated handoff + rotated tip-of-spear + a close record — all auto-applied at the next `/symphony` open.

---
<!-- New chains authored 2026-06-16 — built from installed skills (live). -->

## call-to-followups
- **STATUS:** live ✅ (installed: `call-context`, `email-send`; `aria-intents` CLI present)
- **trigger:** manual | intent:"follow up on that call | what do I owe from the call | turn the call into action"
- **bar:** every commitment Ian made on a recent call becomes a concrete, grounded DRAFT he can send in one click — nothing invented, nothing auto-sent.
- **steps:**
  1. `call-context` — scrub the last 1-3 CALLS; surface what was said + any capture gap.
  2. `aria-intents` (review) — extract the action items / commitments from those calls (recency-gated; never auto-fire).
  3. `email-send` — render each follow-up as a **DRAFT** (auto-CC ian@insynctech.io), recipients resolved.
- **QA gate (before any draft):** every item traces to a real turn in the call; **DRAFT only — never send**; last-48h calls only (no stale).
- **output / write-back:** drafted follow-ups + a short "owed-from-call" list; the commitments feed the continuity memory.

## research-brief
- **STATUS:** live ✅ (installed: `deep-research`, `memory-promote`, `email-send`)
- **trigger:** manual | intent:"research X | deep dive on Y | what's the state of Z"
- **bar:** a cited, adversarially-verified brief — every claim traceable to a source, the canonical findings saved so we never re-research the same thing.
- **steps:**
  1. `deep-research` — fan-out web search → fetch → adversarially verify → synthesize a cited report.
  2. `memory-promote` — promote the durable findings to a canonical memory card (so it's recallable later).
  3. `email-send` *(optional)* — share the brief as a DRAFT if it's for someone.
- **QA gate (before save/share):** every claim has a source; uncertain claims are labeled, not asserted (the verify step IS the gate).
- **output / write-back:** the cited brief + a memory card; future "what did we find on X" resolves instantly.

## lead-to-outreach
- **STATUS:** live ✅ (installed: `deep-research`, `runner-reference`, `email-send`)
- **trigger:** manual | intent:"research this lead/partner | draft outreach to X | warm up this prospect"
- **bar:** a personalized, accurate outreach DRAFT whose offer terms are pulled from our CANONICAL pricing/affiliate deal — not improvised.
- **steps:**
  1. `deep-research` — the lead/company/person → a tight context brief (who, what they need, the angle).
  2. `runner-reference` — pull our canonical terms (pricing, the `affiliate-program` ladder) so the offer is exact.
  3. `email-send` — a voice-matched outreach **DRAFT**, grounded in 1 + 2.
- **QA gate (before draft):** every offer figure comes from canonical source (ask-the-runner-first), not memory; DRAFT only; no overpromising.
- **output / write-back:** the outreach draft + the lead brief; supports the affiliate channel ([[marketing/affiliate-program]]).

## ship-a-skill
- **STATUS:** live ✅ (installed: `aria-automation-candidates`, `premortem`, `aria-skill-test`, `marketplace-publish`)
- **trigger:** manual | intent:"ship this as a skill | publish the skill | turn this pattern into a skill"
- **bar:** the new skill is regression-clean (no traceback, no credential leak, valid frontmatter) BEFORE it's published anywhere.
- **steps:**
  1. `aria-automation-candidates` — confirm the pattern is worth crystallizing AND pick the right primitive (skill · chain · hook · schedule · combo); not already covered.
  2. `premortem` — failure modes of the skill → guards baked into it.
  3. `aria-skill-test` — dry-run the skill; assert clean output + no secrets + README/frontmatter present.
  4. `marketplace-publish` — ship to the right surface (repo tier / marketplace) only after the test passes.
- **QA gate (before publish):** `aria-skill-test` is GREEN — no publish on a failing test. Tier (internal/user) is correct per the reinventory.
- **output / write-back:** the published skill + its test report; the catalog (`build-claude-org.py`) is regenerated.

## config-reconcile
- **STATUS:** live ✅ (installed: `premortem`, `stripe-sync`/`cloudflare-dns-deploy`/`github-repo-deploy`/`el-agent-deploy`, `deploy-verify`)
- **trigger:** manual | intent:"sync stripe | deploy DNS | update the agent | push repo metadata | reconcile <catalog>"
- **bar:** the live vendor state matches our declared YAML catalog — and nothing money/DNS/agent-facing changed without a reviewed diff + explicit go.
- **steps:**
  1. `premortem` — what could this reconcile break? cheapest guard each.
  2. the matching reconcile skill **`--dry-run`** — show the field-level DIFF against live (Stripe prices / Cloudflare records / GitHub metadata / EL agent prompt).
  3. **(approval gate)** then `--apply` (and `--prod` where required) — never before the diff is reviewed.
  4. `deploy-verify` — prove the change is the live state now.
- **QA gate (before --apply):** the dry-run diff is reviewed and approved; money/DNS/voice-agent changes are NEVER auto-applied.
- **output / write-back:** the reconciled live state + a record of what changed.

## cost-guard
- **STATUS:** live ✅ (installed: `cost-check`, `splat-investigate`, `elevenlabs-usage`)
- **trigger:** manual | intent:"what's the burn | are we overspending | cost review" | weekly
- **bar:** a true spend picture + root-caused anomalies + ranked cuts — no blind cuts, only real anomalies acted on.
- **steps:**
  1. `cost-check` — MTD spend across Anthropic/Twilio/ElevenLabs/Resend + burn-rate + projection.
  2. `elevenlabs-usage` — voice minutes vs benchmark (the usual cost driver).
  3. `splat-investigate` *(if an anomaly)* — trace the disproportionate splat/skill/project to root.
- **QA gate (before recommending cuts):** the anomaly is verified real (works-not-runs), not a heuristic blip; cuts ranked by ROI.
- **output / write-back:** a spend readout + ranked, root-caused cut proposals.
