---
name: question-economy
description: Near session end, when the user is winding down, or on request, analyze the questions Claude asked Ian and Ian's answers — then distill each answer into a standing default written to memory, so Claude asks fewer (only genuinely novel) questions over time. Tracks a per-session question-rate metric so the decline is measurable. Use when Ian says "wrap up", "winding down", "what did you learn about working with me", "question economy", "/question-economy", or proactively at session close.
---

# Question Economy

Every question Claude asks Ian has a cost — it interrupts his flow (especially a focus-stealing modal mid-dictation, see [[feedback-dictation-over-approval]]). And every answer Ian gives is a latent **standing default**: next time the same situation arises, Claude should already know the answer and just proceed, stating the choice instead of asking.

**The goal is not zero questions — it's zero *avoidable* questions.** Genuinely novel decisions that need Ian's judgment still deserve a question. What should decay toward zero is re-asking things Ian has effectively already answered. Run this every session and the avoidable-question count should trend down, session over session.

## Steps

1. **Extract the question→answer ledger.** Run the extractor on this session's transcript:
   ```sh
   python3 ~/.claude/skills/question-economy/question_economy.py --print-trend
   ```
   It prints JSON: `hard_questions` (AskUserQuestion modals — the costliest), `soft_questions` (an assistant turn ending in `?` + Ian's next reply), `counts`, and `trend` (the last 8 sessions' question rates). It also appends one metric row to `question_economy_log.jsonl`.

2. **Classify each pair.** For every question→answer, decide:
   - **Standing default** — Ian's answer generalizes ("whenever X, do Y"). → becomes a `feedback` memory.
   - **One-off** — context-specific, doesn't generalize. → skip.
   - **Avoidable** — Claude *could* have inferred the answer from existing memory or a sensible default and shouldn't have asked. → flag it; this is the number to drive down.
   - **Good question** — genuinely needed Ian's judgment. → leave it; not every question is waste.

3. **Write the new defaults to memory (proposals, not live).** For each standing default, write a `feedback`-type candidate to `_distill_inbox/` with the standard body (the rule, then **Why:** and **How to apply:**). Lead with the generalized rule, not the one instance. Link related memories with `[[slug]]`. Pairs with `/memory-promote` for the live write. Never write straight to live memory — propose, let Ian ratify.
   - Before writing, check MEMORY.md + the memory dir for an existing feedback memory this should *update* instead of duplicating.

4. **Report the economy.** One short readout to Ian:
   - This session: N hard + M soft questions; **K were avoidable** (and why).
   - New standing defaults learned → so I won't ask these again: (list).
   - The trend: this session vs the last few (is the avoidable count actually falling?).
   - If the rate is NOT falling, say so plainly and name what's still being re-asked — that's a signal a memory isn't being honored or is mis-scoped.

## The loop it serves
Question asked → Ian answers → answer distilled to a standing default → memory → next session Claude applies the default instead of asking → avoidable-question count falls. The `question_economy_log.jsonl` metric is the proof; the `feedback` memories are the mechanism. Over many sessions this converges Claude onto Ian's working style so the conversation is about novel decisions, not re-litigating known preferences.

## Notes
- Hard (modal) questions are weighted heaviest — a modal mid-dictation is the worst interruption. If the log shows hard questions not falling, that's a priority fix.
- Distinguish *workflow* defaults (how Ian wants work done) from *compute/architecture* defaults (technical choices he keeps making the same way) — both are worth capturing; tag them so the feedback memories stay findable.
- Complements `session-end` (broad memory capture) and `memory-curator` (deep semantic pass). This skill is narrow on purpose: the Q&A ledger and the question-rate metric.
