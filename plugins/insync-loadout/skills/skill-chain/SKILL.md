---
name: skill-chain
description: The chain primitive — run an ordered sequence of ASI skills as ONE macro-skill, threading each step's output into the next, halting on failure, and enforcing a mandatory QA-against-source gate before any irreversible/outward action. A chain can be fired manually (/skill-chain <name>), by a detected intent (intent-trigger), or by an event; its outcome writes back into the context brain. Use when Ian says "run the <X> chain", "chain these skills", "skill chain", "/skill-chain", "what chains do we have", "register a chain", "fire the deploy chain", or when a multi-skill sequence should run as one named, repeatable unit.
---

# Skill Chain (the chain primitive)

A **skill** is a markdown playbook. A **skill chain** is "a macro skill with skills inside it — skill one fires, calls skill two, skill two calls skill three." This skill formalizes what Aria already does informally (the deploy-hygiene sequence, client-delivery) into a **named, repeatable, trigger-able, QA-gated** primitive. Source: the Greg Isenberg / LCA AI-native model — `~/dev/aria/reference/greg-isenberg-ai-native/SYNTHESIS.md` (roadmap item #1).

The registry of defined chains lives in **`chains.md`** (next to this file). This SKILL.md defines what a chain IS and how to run/add one.

## What makes it a chain (3 properties)
1. **Ordered skills, output threaded forward.** Step N's output is step N+1's input. Each step is a real installed ASI skill (type `/` to see them), not prose.
2. **A trigger.** `manual` (`/skill-chain <name>`), `intent:<pattern>` (auto-fired by the live intent-trigger — see [[project_intent_trigger_ainative_2026_06_08]]), or `event:<x>`.
3. **A QA-against-source gate.** Before any **irreversible or outward** step (deploy, send, publish, pay), a gate verifies the output is grounded in real source — *"AI loves to fake it till it makes it; your job is to make sure it doesn't."* Nothing invented, nothing overpromised, every claim traceable to data/transcripts/files. The gate is the load-bearing part — a chain without it is just a script.

## Run protocol
When asked to run a chain (e.g. `/skill-chain deploy-hygiene`):

1. **Load** the chain entry from `chains.md`. If it names skills not installed here, say so and stop (don't fake a step).
2. **Confirm the trigger fired legitimately** (manual ask, or a matched intent/event). Echo the chain's acceptance bar.
3. **Run each step in order** via the named skill. Pass the prior step's concrete output into the next. **Halt the whole chain on any step failure** — report which step, why, and what's safe to retry. Never silently skip a step.
4. **At the QA gate** (marked in the chain), STOP and verify against source before the irreversible step. If the gate can't confirm grounding, do NOT proceed to the outward action — surface the gap.
5. **Write back.** On completion, record the outcome into the context brain (memory / card / `ops_log`) so the chain compounds — same loop the intent write-back closes.

## Triggers in practice
- **Manual:** `/skill-chain <name>` or "run the deploy chain."
- **Intent-fired:** the live intent-trigger detects a goal in a call/inbox → matches a chain's `intent:` pattern → proposes firing it (proposal-only by default per [[feedback_build_not_flag]]/Ian's isolation rule; never auto-fire an outward chain without the bar + gate).
- **Event:** e.g. an RFP/inbox event → the proposal chain.

## Adding a chain
Append an entry to `chains.md` in this shape (skills must be installed + named exactly):

```markdown
## <chain-name>
- **trigger:** manual | intent:<pattern> | event:<x>
- **bar:** <objective acceptance criterion for the whole chain>
- **steps:**
  1. <skill> — <what it consumes → produces>
  2. <skill> — …
- **QA gate (before step N):** <what must be verified against source>
- **output / write-back:** <the deliverable + where the outcome compounds>
```

Keep chains honest: only catalog chains whose skills exist; mark aspirational ones `STATUS: template`. A chain that references a missing skill must say so, not pretend.

## Worked example
The **deploy-hygiene** chain (all skills installed, run live 2026-06-09 to ship the recent-calls dedup fix): premortem → surgical-patch → safe-restart → aria-deploy → deploy-verify, with the QA gate = "0 active calls + boot-test passes" before restart. See `chains.md`.
