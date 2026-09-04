# goal-to-plan

Turns a vague ask into an **agent-ready brief** — the "quality of the brief" discipline an AI-native team runs on (Greg Isenberg / LCA planning pillar, Pillar A of `~/dev/aria/reference/greg-isenberg-ai-native/SYNTHESIS.md`).

An agent earns autonomy once it has four things: a **clear goal**, the **right skills**, the **right tools**, and **scoped context**. This skill produces exactly that as an artifact:

- a **`spec_charter`** — goal · one acceptance criterion · scope (in/out) · skills · tools · context · risks(premortem→guard) · verification
- a **lane dispatch** block ready for `/orchestrate` (role · owned files · acceptance · report · context)

It's itself a **skill chain**: it calls `premortem` (failure-modes → guards) and reuses the `sprint-scaffold` spec_charter template.

**Done =** a fresh agent could execute the plan without asking anything, and you could objectively check the result against the acceptance criterion.

Triggers: "plan this", "scope this out", "make this agent-ready", "turn this into a brief", "goal to plan", `/goal-to-plan`.
