# premortem

The DVE/GVE prosthetic premortem reflex — before writing, changing, debugging, or deploying code, briefly imagine how the decision could fail and turn that into an ARTIFACT (predicted failure modes → cheapest guard → predicted-vs-actual ledger), not just talk. Use before any risky change or deploy, or when the user says "premortem", "how could this fail", "what's the risk", "/premortem", "/dve". The operational core of the DVE Guidebook tool.

## Usage

```sh
## <date> — <decision>  [phase: <phase>]
   | # | failure | blast radius | likelihood | guard | predicted | actual |
   |---|---------|--------------|------------|-------|-----------|--------|
   ...one row per failure mode; leave "actual" blank until after.
```

---

_README generated from `SKILL.md`; the canonical contract lives there._  
Stdlib-first. Apache 2.0.
