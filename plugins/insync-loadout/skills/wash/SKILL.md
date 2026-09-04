---
name: wash
description: When we hit uncertainty — a real fork, an architecture/product decision that's drifting, "wading through the abyss / chewing glass / lost in the sauce," or before anything big or irreversible — STOP building and wash the idea through Claude.ai (Anthropic, the chatbot) for fresh synthesis. Package the situation into ONE self-contained doc (Claude.ai has none of our canonical context), hand it to Ian to paste in, then fold the AGREED output back into the canonical plan as real sprints — NEVER execute off the advisory wash doc. Run when Ian says "wash this through Claude", "let's do a wash", "run it through the chatbot", "I'm not sure", "we're lost", or when YOU notice we're thrashing.
---

# Wash — stop thrashing, run it through Claude.ai

The single most reliable move in this whole workflow: when we are **uncertain, stuck, or about to make a big/irreversible call**, we do not keep grinding and improvising. We **stop, package the situation, and wash it through Claude.ai** (Anthropic's chatbot) for a fresh, independent synthesis — then fold the agreed answer back into the canonical plan and build from there.

This skill exists because the failure mode it prevents is the expensive one: an agent **wading through the abyss / chewing glass** — thrashing on an under-specified decision, improvising infra, building the wrong thing, losing the thread. The cure is cheap: take a break, wash it, come back with clarity.

## THE TRIGGER — recognize it yourself, don't wait to be told
Call a wash the moment any of these is true (Ian shouldn't have to ask):
- A **real fork** with no obvious right answer (A vs B architecture; sequencing; scope).
- A decision that's **drifted** — we've discussed it 3 different ways and it's not converging.
- Something **big or irreversible** is next (infra, money, auth, data, fleet, a redesign).
- You're **thrashing** — multiple failed attempts, re-litigating, "lost in the sauce," patching untested changes to a live surface.
- You **don't actually know** what Ian wants and you're about to guess.

When you notice it: **say so plainly** ("we're thrashing on X — let's wash it") and propose the wash. That self-recognition IS the skill working.

## THE DISCIPLINE (load-bearing)
1. **STOP building.** No more improvising while uncertain. (Ties to standing law: uncertainty → stop; advisory ≠ authorization; infra never improvised.)
2. **The wash doc is SELF-CONTAINED.** Claude.ai does **not** have our memories, canonical plan, code, or session history. Everything it needs to answer must be IN the doc. Assume zero shared context.
3. **The wash doc is ADVISORY.** Stamp it. Its output is an input, never an instruction. We **fold the agreed decisions into the CANONICAL plan as real sprints** and execute from the plan — we never execute off the wash doc. (This is the exact rule the nginx-break of 2026-06-23 violated.)
4. **Ian rules on anything flagged.** The wash returns decided-vs-flagged; Ian decides the flags; then it's folded in.

## THE MOVEMENTS
### 1 · NAME THE STUCK
One or two sentences: what are we uncertain about, and why is it blocking. The sharper the question, the better the wash.

### 2 · ASSEMBLE THE WASH DOC (self-contained)
Write `~/Desktop/lore/handoffs/wash/<YYYY-MM-DD>/<topic>__wash.md` (`~/Desktop/claude/...` on unrenamed boxes) with frontmatter `authority: advisory` + a stamp, containing: *(CANONICAL location — washes live in `handoffs/wash/<date>/`, NOT deliverables; this is where the Claude.ai RESPONSE docs get filed too. Ian's call 06-24: a wash is a handoff, not canonical — it's tracking.)*
- **What you (Claude.ai) need to know** — the relevant current state, distilled (architecture truth, what's built, what's not). Self-contained.
- **The question / fork** — stated precisely. If multiple, number them.
- **What we've tried / considered** — options on the table + their tradeoffs, honestly (including what failed).
- **The constraints** — money, security, time, the standing law, anything non-negotiable.
- **What we need back** — "synthesize ONE answer: every sub-question resolved or flagged; if flagged, say what Ian must decide." Ask for synthesis, not a menu.

Keep it tight and honest — no spin. The quality of the wash is the quality of this doc.

### 3 · HAND IT OFF
Tell Ian the wash doc is ready and where it is, so he pastes it into Claude.ai (or routes it to the "quad"/Anthropic side). If a `DesignSync`/design wash is the right venue (a UI question), say so — UI questions go to **Claude Design** (Ian's rule: the mock is canonical), product/architecture questions go to the **Claude.ai chatbot**.

### 4 · FOLD BACK (after Claude.ai returns)
When Ian brings back the synthesis:
- Reconcile it against the **canonical plan** (`~/.claude/plans/00_CANONICAL_vox-ordo-execution-spine.md`).
- Turn the **agreed** decisions into named sprints in the plan; surface the **flagged** ones for Ian's ruling.
- THEN build — from the plan, verified on Ian's screen, never from the wash doc.

## NOTES
- This is the partner to `/realign` (reconsolidate the day) and `/premortem` (stress-test before building). `wash` is specifically for **breaking an uncertainty deadlock** with an outside perspective.
- Idempotent: re-washing a refined question is encouraged; each wash is a dated doc, additive.
- The whole point is **cheap clarity beats expensive thrashing.** When in doubt, wash.
