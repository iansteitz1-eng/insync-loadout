# skill-chain

The **chain primitive** — formalizes what Aria already does informally (deploy-hygiene, client-delivery) into a named, repeatable, trigger-able, **QA-gated** macro-skill. Source: Greg Isenberg / LCA AI-native model (`~/dev/aria/reference/greg-isenberg-ai-native/SYNTHESIS.md`, roadmap item #1).

A **chain** = ordered skills (output threaded forward) + a trigger (manual / intent / event) + a **QA-against-source gate** before any irreversible or outward step. The gate is load-bearing: it's the anti-hallucination move — nothing invented, nothing overpromised, every claim traceable to source. A chain without a gate is just a script.

- `SKILL.md` — what a chain is + the run protocol + how to add one.
- `chains.md` — the registry of defined chains (only chains whose skills are installed are `STATUS: live`).

Live chains today: **deploy-hygiene** (run end-to-end 2026-06-09) and **goal-to-plan**. `client-delivery` is defined (skills in that pack, not on this Mac); `proposal` is the aspirational LCA template.

Triggers: `/skill-chain <name>`, "run the deploy chain", "what chains do we have", "register a chain". Intent-fired chains hook into the live intent-trigger.
