#!/usr/bin/env python3
# cc_hook_canon_gate.py — PreToolUse write-gate for CANON HEADS. Any Edit/Write to a canon head:
#   (1) rotates the prior version → _history/<stamp> (preserved, reversible), (2) logs it,
#   (3) FLAGS changes to authoritative/LOCKED truth (surfaced, allowed — not silent). Protects authoritative truth.
import sys, json, os, shutil, datetime, re
try: d=json.load(sys.stdin)
except: sys.exit(0)
if d.get("tool_name") not in ("Edit","Write"): sys.exit(0)
fp=d.get("tool_input",{}).get("file_path","")
m=re.search(r"/Desktop/(?:lore|claude)/canon/([a-z][a-z-]+)/([^/]+\.md)$", fp)  # path-agnostic (2026-07-08 lore cut)
if not m: sys.exit(0)
section,fn=m.group(1),m.group(2)
if "/_history/" in fp or "/subsections/" in fp or section.startswith("_") or section=="_meta": sys.exit(0)
if not os.path.exists(fp): sys.exit(0)            # brand-new head: nothing to rotate
cur=open(fp).read()
hist=os.path.join(os.path.dirname(fp),"_history"); os.makedirs(hist,exist_ok=True)
stamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
shutil.copy2(fp, os.path.join(hist, fn[:-3]+f"_{stamp}.md"))   # preserve prior authoritative version
auth=("validation: authoritative" in cur) or ("LOCKED" in cur)
open(os.path.expanduser("~/.aria/canon_changes.log"),"a").write(
    f"{datetime.datetime.now():%Y-%m-%d %H:%M} CANON-WRITE {section}/{fn}{' [AUTHORITATIVE]' if auth else ''}\n")
if auth:
    print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow",
      "permissionDecisionReason":f"⚠️ Editing AUTHORITATIVE canon: {section}/{fn}. Prior version rotated to _history (reversible). Ensure the change is corroborated/verified before it becomes the brain's truth."}}))
sys.exit(0)
