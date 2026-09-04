# insync-loadout

**The InsyncTech operator loadout, packaged as a Claude Code plugin + private marketplace.**

This repo turns Ian's Claude Code operator toolkit — the session-lifecycle rituals, the
orchestration/planning primitives, the comms skills, and the 11-agent multi-agent fabric —
into a **distributable artifact** so a new teammate's machine (a new teammate)
boots with the toolkit in **one command** instead of hand-copying 55 skills and 11 agents.

This is the **spine-as-product dogfood**: the loadout that runs our own sessions is itself
the thing we hand to a teammate. The packaging IS the product.

> Built as a NEW packaging repo that **copies from `~/.claude/skills` and `~/.claude/agents`
> read-only**. It does not modify the live loadout, `~/.claude/settings.json`, or the source
> skills/agents. It is a scaffold + manifest, not a migration.

---

## Install (for a teammate)

```bash
# 1. Add this repo as a marketplace (point at the repo root, which holds .claude-plugin/marketplace.json)
claude plugin marketplace add iansteitz1-eng/insync-loadout
#    …or from a local clone:
claude plugin marketplace add /path/to/insync-loadout

# 2. Install the loadout plugin from the "insync" marketplace
claude plugin install insync-loadout@insync
```

After install, the bundled **skills** and **agents** are live immediately. The **hooks**
need a one-time per-machine wiring step (see "Post-install" below), because the full hook
set depends on machine-specific paths and Ian-personal services that don't travel.

---

## What's in the ship set (and why)

Ian runs **55 skills**. Dumping all 55 on a teammate is noise. This loadout ships a curated
**13-skill spine** — the capabilities a teammate actually needs on day one — grouped by role:

### Session lifecycle (open → save → close)
| skill | why it's in |
|---|---|
| `spinup` | pick up where you left off — the session OPEN |
| `checkpoint` | mid-session "log everything, keep going" — the SAVE |
| `session-end` | the CLOSE chain — memory pass, question-economy, handoff rotate |

### Orchestration & planning (the AI-native-team mechanics)
| skill | why it's in |
|---|---|
| `orchestrate` | spawn/manage parallel Claude lanes — the fabric's control surface |
| `skill-chain` | run an ordered sequence of skills as one macro |
| `goal-to-plan` | turn a vague ask into an agent-ready brief |
| `premortem` | "how could this fail" reflex before a risky change |
| `wash` | stop-and-wash-through-Claude.ai when thrashing |
| `sprint-scaffold` | drop a sprint folder skeleton with a filing-cabinet charter |

### Comms
| skill | why it's in |
|---|---|
| `email-send` | send mail with the standing CC-Ian rule enforced |
| `broadcast` | push a message to the team-broadcast channel |

### Memory / meta
| skill | why it's in |
|---|---|
| `memory-promote` | promote a candidate memory into live memory |
| `question-economy` | distill Q&A into standing defaults so Claude asks fewer questions |

### Agents (all 11)
The full multi-agent fabric ships: `orchestrator`, `builder`, `janitor`, `observer`,
`memory-curator`, `cost-reviewer`, `doctrine-reviewer`, `security-gate`, `launch-readiness`,
`splat-economist`, `fellows-orchestrator`. These are role definitions (prompt + tools), not
wired to any secret — safe to ship whole.

---

## What's deliberately OUT (and why)

The **founder-only / prod-wired / secret-touching** skills are excluded. Curate, don't dump:

- **`symphony`** — Ian's session conductor, but hard-wired to `ssh` against our production host and
  `<install-dir>/...` prod paths. A teammate's box has neither. (The pieces it orchestrates —
  `spinup` / `session-context` / `call-context` — a teammate can run à la carte; `spinup` ships.)
- **Deploy / infra gates** — `aria-deploy`, `voice-deploy`, `el-agent-deploy`,
  `cloudflare-dns-deploy`, `github-repo-deploy`, `stripe-sync`, `marketplace-publish`,
  `partnership-email-blast`, `safe-restart` — these touch prod credentials, live voice
  sessions, billing, or DNS. Founder-only.
- **Aria-internal / diagnostic** — `aria-status`, `aria-deploy`, `deploy-verify`,
  `trace-write-target`, `splat-investigate`, `doctrine-check`, `training-watch`,
  `runner-reference`, `call-context`, `session-context`, `telegram-ingest`,
  `aria-drives-your-mac`, `phone-coding`, `voice-*`, `elevenlabs-usage`, `cost-check`,
  `vendor-billing-action` — bound to the maintainer's server/DB/voice stack or personal wiring.
- **Machine-fix helpers** — `copy-paste-fix`, `tui-scroll-fix`, `cc-session-resume`,
  `gmail-organizer-setup`, `ffmpeg-audio`, `doc-to-pdf`, `client-*` — useful but not core
  spine; kept out of v0.1 to keep the ship set tight. Easy to add later.

### Honest note on the shipped comms skills
`email-send` and `broadcast` are **included but not turnkey**. They read Ian's runtime
config at execution time — `email-send` pulls `RESEND_API_KEY` from `<install-dir>/.env` and
`broadcast` defaults to `--host <your-server>`. **No secret value is baked into the bundle**
(the key is read at runtime, never committed), but a teammate must repoint these at their
own Resend key / broadcast host before they work. They ship as the *pattern*, adaptation required.
`sprint-scaffold` similarly writes into `<install-dir>/sprints/` by default — repoint the base dir.

---

## Post-install: hook wiring (manual, per-machine)

Ian's live setup wires **21 hook scripts across 7 events** in `~/.claude/settings.json`.
Most of those are **machine-specific** (voice notify/speak/interrupt, disk-lane exchange,
ordo-sync, certus-pull, aria-checkpoint, session-start funnels) and reference absolute paths
that only exist on Ian's Mac. **We do not hardcode those.**

This plugin ships `hooks/hooks.json` with the **portable subset**, referenced via
`${CLAUDE_PLUGIN_ROOT}` so they resolve on any machine:

| event | hook | what it does |
|---|---|---|
| `PreToolUse` (Bash) | `cc_hook_guard.py` | guards dangerous bash before it runs |
| `PreToolUse` (Edit\|Write) | `cc_hook_canon_gate.py` | gates edits against canon |
| `PostToolUse` (Write\|Edit\|MultiEdit) | `cc_hook_formatter.py` | auto-formats edited files |
| `PostToolUse` (Write\|Edit\|MultiEdit) | `cc_hook_syntax_check.py` | syntax-checks edited files |

Also bundled as an **optional adapter** (not wired by default): `cc_hook_pre_restart.py`
(the safe-restart in-flight gate) — wire it under `PreToolUse`/`Bash` if the teammate runs
a shared service.

**These plugin hooks activate automatically when the plugin is enabled** — no settings.json
edit needed for the bundled set. If a teammate wants the full Ian loadout (voice, disk-lane,
etc.), those remain a separate, manual, per-machine wiring job against their own paths — by
design. See [the reference in Ian's memory](../) on why Obsidian/canon renames ≠ live wiring:
the same rule applies here — packaging ≠ per-machine activation of personal hooks.

---

## Repo layout

```
insync-loadout/
├── .claude-plugin/
│   └── marketplace.json          # the "insync" catalog (1 plugin)
├── plugins/
│   └── insync-loadout/
│       ├── .claude-plugin/
│       │   └── plugin.json        # name/version/desc + skills/agents/hooks paths
│       ├── skills/                # 13 curated skill dirs (copied read-only from ~/.claude/skills)
│       │   ├── spinup/  checkpoint/  session-end/
│       │   ├── orchestrate/  skill-chain/  goal-to-plan/  premortem/  wash/  sprint-scaffold/
│       │   ├── email-send/  broadcast/
│       │   └── memory-promote/  question-economy/
│       ├── agents/                # all 11 agents (copied read-only from ~/.claude/agents)
│       └── hooks/
│           ├── hooks.json         # portable subset, ${CLAUDE_PLUGIN_ROOT}-relative
│           └── scripts/           # 5 portable hook scripts
├── README.md
└── MANIFEST.md                    # everything bundled, one line each
```

## Validation

```bash
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool plugins/insync-loadout/.claude-plugin/plugin.json
python3 -m json.tool plugins/insync-loadout/hooks/hooks.json
```

All three parse clean; every skill dir has a `SKILL.md`; all agents carry frontmatter; every
hook `command` in `hooks.json` resolves to a bundled script. Schema shapes were copied from
real installed examples (the superwhisper plugin + the official `claude-plugins-official`
marketplace + the `plugin-dev` manifest reference), not guessed.

## Maintenance

Bump `version` in **both** `plugin.json` and the plugin entry in `marketplace.json` together.
To add a skill: `cp -R ~/.claude/skills/<name> plugins/insync-loadout/skills/<name>`, confirm
it's portable (no `/opt/aria`, no private hostnames, no secret), and note it in `MANIFEST.md`.

## Support

support@insynctech.io, or open an issue on this repo.

## License

Apache-2.0. See [LICENSE](LICENSE). Product names and artwork are covered by [TRADEMARKS.md](TRADEMARKS.md).
