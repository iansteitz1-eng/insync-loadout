#!/usr/bin/env python3
"""
email_send.py — Resend wrapper with auto-CC Ian and sender-identity picker.

Honors the standing 2026-05-16 directive: every outbound email CCs
ian@insynctech.io. Override requires explicit --override-standing-rule
flag (logged into the splat metadata for audit).

Supports attachments via `--attach <path>` (repeatable). Each file is
base64-encoded and sent through Resend's `attachments` array.
"""
import argparse
import base64
import json
import os
import sys

import httpx  # available in your venv; usable from system python too if installed

# Resend per-message attachment ceiling is 40 MB total; we cap individual
# files at 20 MB to leave headroom for the encoded payload.
MAX_ATTACH_BYTES = 20 * 1024 * 1024
MAX_TOTAL_ATTACH_BYTES = 38 * 1024 * 1024

IAN = "ian@insynctech.io"

SHORTCUTS = {
    "ian": IAN,
    # Add your own teammates here, e.g. "sam": "sam@example.com" — edited per machine.
    "team": IAN,
}

SENDERS = {
    "default": "InsyncTech <hello@insynctech.io>",
    "aria": "Aria · InsyncTech <hello@insynctech.io>",
    "stump": "Stump Aria <hello@insynctech.io>",  # using verified domain
}


def _env() -> dict:
    e = dict(os.environ)
    try:
        with open("<install-dir>/.env") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                e.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass
    return e


def resolve(addr: str) -> str:
    """Resolve a shortcut or comma-list of shortcuts to comma-joined emails."""
    parts = [p.strip() for p in addr.split(",") if p.strip()]
    out = []
    for p in parts:
        if "@" in p:
            out.append(p)
        else:
            mapped = SHORTCUTS.get(p.lower())
            if not mapped:
                raise ValueError(f"unknown recipient shortcut: {p}")
            out.extend([a.strip() for a in mapped.split(",")])
    return ", ".join(dict.fromkeys(out))  # dedupe, preserve order


def emit_splat(payload: dict, response: dict, overridden: bool):
    try:
        sys.path.insert(0, "/opt/aria")
        from certus_trace import Nodes as CTNodes
        from certus_trace import emit as ct_emit  # type: ignore

        ct_emit(
            CTNodes.AGENT_ACTION,
            payload.get("to", "?")[:80],
            "skill: email-send",
            pre={
                "to": payload.get("to"),
                "subject": payload.get("subject"),
                "from": payload.get("from"),
                "cc": payload.get("cc"),
                "override_cc_ian": overridden,
                "attachments": [
                    a.get("filename") for a in payload.get("attachments", [])
                ],
            },
            post={
                "ok": response.get("ok"),
                "status": response.get("status"),
                "resend_id": (response.get("body") or {}).get("id"),
            },
        )
    except Exception as e:
        print(f"warn: splat emit failed: {e}", file=sys.stderr)


def send(args) -> int:
    env = _env()
    key = env.get("RESEND_API_KEY")
    if not key:
        print("RESEND_API_KEY missing in <install-dir>/.env", file=sys.stderr)
        return 2

    to = resolve(args.to)

    # Sender selection
    if args.from_custom:
        sender = args.from_custom
    elif args.from_aria:
        sender = SENDERS["aria"]
    elif args.from_stump:
        sender = SENDERS["stump"]
    else:
        sender = SENDERS["default"]

    # CC-Ian enforcement
    cc_list = []
    if args.cc:
        cc_list.append(resolve(args.cc))
    cc_ian = not args.no_cc_ian
    if not cc_ian and not args.override_standing_rule:
        print(
            "ERROR: --no-cc-ian requires --override-standing-rule (audit trail).\n"
            "Per the 2026-05-16 directive, every outbound email CCs ian@insynctech.io.",
            file=sys.stderr,
        )
        return 3
    if cc_ian and IAN not in to:
        cc_list.append(IAN)

    body = args.body
    html = body if "<" in body and ">" in body else f"<p>{body}</p>"

    payload = {
        "from": sender,
        "to": [a.strip() for a in to.split(",") if a.strip()],
        "subject": args.subject,
        "html": html,
    }
    if cc_list:
        payload["cc"] = [a.strip() for a in ",".join(cc_list).split(",") if a.strip()]
    if args.reply_to:
        payload["reply_to"] = [args.reply_to]

    # Attachments: --attach path[:filename] (repeatable)
    if args.attach:
        attachments = []
        total = 0
        for spec in args.attach:
            if ":" in spec and not os.path.exists(spec):
                path, _, override_name = spec.partition(":")
            else:
                path, override_name = spec, ""
            if not os.path.exists(path):
                print(f"ERROR: attachment not found: {path}", file=sys.stderr)
                return 4
            size = os.path.getsize(path)
            if size > MAX_ATTACH_BYTES:
                print(
                    f"ERROR: {path} is {size} bytes; per-file cap is {MAX_ATTACH_BYTES}",
                    file=sys.stderr,
                )
                return 4
            total += size
            if total > MAX_TOTAL_ATTACH_BYTES:
                print(
                    f"ERROR: total attachments exceed {MAX_TOTAL_ATTACH_BYTES} bytes",
                    file=sys.stderr,
                )
                return 4
            with open(path, "rb") as f:
                content = base64.b64encode(f.read()).decode("ascii")
            attachments.append(
                {
                    "filename": override_name or os.path.basename(path),
                    "content": content,
                }
            )
        payload["attachments"] = attachments

    try:
        with httpx.Client(timeout=20.0) as c:
            r = c.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
            )
        ok = r.status_code in (200, 201, 202)
        try:
            body_json = r.json()
        except Exception:
            body_json = {"raw": r.text[:300]}
        response = {"ok": ok, "status": r.status_code, "body": body_json}
    except Exception as e:
        response = {"ok": False, "status": None, "body": {"error": str(e)[:200]}}

    overridden = (not cc_ian) and args.override_standing_rule
    emit_splat(payload, response, overridden)

    print(json.dumps(response, indent=2))
    return 0 if response["ok"] else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True, help="email, shortcut, or comma list")
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--cc", default="", help="extra cc (resolves shortcuts)")
    ap.add_argument("--reply-to", default="")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--from-aria", dest="from_aria", action="store_true")
    g.add_argument("--from-stump", dest="from_stump", action="store_true")
    g.add_argument("--from", dest="from_custom", default="")
    ap.add_argument("--no-cc-ian", action="store_true")
    ap.add_argument("--override-standing-rule", action="store_true")
    ap.add_argument(
        "--attach",
        action="append",
        default=[],
        help="attach a file (repeatable). Use 'path' or 'path:filename' to override the name.",
    )
    args = ap.parse_args()
    sys.exit(send(args))


if __name__ == "__main__":
    main()
