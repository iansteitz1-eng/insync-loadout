---
name: goal-to-plan
description: Turn a vague/ambiguous ask into an agent-ready plan — the "quality of the brief" discipline an AI-native team runs on. Emits a spec_charter (mission · scope · ONE acceptance criterion · risks) + a ready-to-dispatch lane brief (role · owned files · acceptance · report protocol), chaining the premortem + sprint-scaffold skills. Use when Ian says "plan this", "turn this into a brief", "scope this out", "make this agent-ready", "what's the plan for X", "goal to plan", "/goal-to-plan", or before dispatching a lane / starting multi-step work from a fuzzy goal.
---

# Goal → Plan

The bottleneck of an AI-native team is **not the model — it's the quality of the brief.** An agent earns autonomy (runs for hours, holds a real bar) once it has the four things a good new hire gets: a **clear goal**, the **right skills**, the **right tools**, and **rich, scoped context**. This skill turns a vague ask into exactly that — an artifact an agent (a lane, the runner, or a teammate's session) can pick up and run without re-briefing.

It is a **skill chain**: it calls [[premortem]] (failure-modes → cheapest guard) and reuses the [[sprint-scaffold]] `spec_charter` template, then emits a lane dispatch for `/orchestrate`. Source idea: the Greg Isenberg / LCA "AI-native in <60 min" planning pillar — `~/dev/aria/reference/greg-isenberg-ai-native/SYNTHESIS.md`.

## When to use
- A goal arrives fuzzy ("build the CRM", "fix onboarding", "do the affiliate program") and you're about to start work or dispatch a lane.
- Before any multi-step / multi-session effort that should have one canonical, agent-readable home.
- When triaging an intent (`aria-intents`) into something actionable.

## Steps

1. **Compress the goal to ONE sentence + ONE acceptance criterion.** The acceptance criterion is the bar that makes "done" objective and testable ("a real call's card shows recent-calls exactly once", not "improve the card"). If the ask is genuinely ambiguous, ask **at most 2–3** targeted questions — otherwise pick sensible defaults, state them, and proceed (respect [[feedback_dictation_over_approval]] + [[reference_question_economy_skill]]: prefer defaults over modals).

2. **Name the four things** (this IS the plan's spine):
   - **Goal** — the one-sentence outcome + acceptance criterion from step 1.
   - **Skills** — which existing ASI skills apply (type `/` to scan; e.g. `surgical-patch`, `safe-restart`, `deploy-verify`, `doc-to-pdf`, `email-send`). Name them; don't reinvent.
   - **Tools** — the concrete surface: runner mtypes (`code_task`/`disk_rpc`/`computer_use`), DB, gateway endpoints, CLIs in `~/bin`.
   - **Context** — the *scoped* set of files/dirs/memory the agent should read (and the denylist of what it must NOT touch). Narrow beats broad.

3. **Run a premortem** (chain [[premortem]]). 3–5 concrete failure modes for THIS goal → blast radius → likelihood → the **cheapest guard** for each. These become the plan's "Risks" section — not prose, an artifact.

4. **Emit the `spec_charter`** (reuse the [[sprint-scaffold]] template):

   ```markdown
   # <Title> · spec_charter v1
   **Goal (one sentence):** …
   **Acceptance criterion (the bar):** …            # objective, testable
   **Scope — IN:** …
   **Scope — OUT (explicitly not now):** …
   **Skills:** …            **Tools:** …
   **Context (read):** …    **Do NOT touch:** …
   **Risks (premortem → guard):**
     - <failure> · <blast radius> · <likelihood> → <cheapest guard>
   **Verification (how we prove the bar is met, in-product not code-trace):** …
   ```

5. **Emit the lane dispatch** — ready to paste into `/orchestrate` (or hand to a runner/teammate):

   ```
   ROLE: <one line>
   OWNED FILES: <exact paths — the file-lock contract>
   ACCEPTANCE: <the criterion from step 1>
   REPORT: <what to report back + when (e.g. on green / on blocker)>
   CONTEXT: <pointer to the spec_charter + the scoped reads>
   ```

6. **Decide the home.** Single self-contained task → keep the spec_charter inline / in the relevant project folder. Multi-item, multi-session, or multi-lane → run [[sprint-scaffold]] to drop it in a real sprint folder so nothing ships "homeless."

## Output
One artifact (the spec_charter) + one dispatch block. That's a vague goal turned into "goal + skills + tools + context + a bar + guards" — the agent-ready brief. If the work is dispatch-ready, offer to fire it via `/orchestrate`; never auto-dispatch without the bar and the premortem present.

## Done = 
The plan is agent-ready when a fresh agent could execute it **without asking you anything** and you could **objectively check the result** against the acceptance criterion. If either isn't true, the brief isn't done — tighten it.
