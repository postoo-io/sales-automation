#!/usr/bin/env python3
"""Render a mustache-like Korean B2B email template using profile + context.

Variable scheme (see references/template_variables.md):

  company.*    from profile.json
  me.*         from active team member (profile.team[active])
  brand.*      from profile.json
  client.*     from Pluuug inquiry/client (passed via --context)
  quote.*      quote-writing output (passed via --context)
  meeting.*    meeting metadata (passed via --context)
  contract.*   contract metadata
  kickoff.*    kickoff metadata
  prevEmail.*  previous-email metadata (for follow-ups)
  request.*    info-request metadata
  hold.*       hold/resume metadata
  team.pm      project manager from team (role match)
  date         today's ISO date

Resolution: dotted lookup on a merged context dict. Unresolved variables are
left in place by default (so the human can fix them) — use --strict to abort
if anything is missing, or --warn to print missing keys to stderr.

CLI:
  render_template.py --template PATH [--context FILE_OR_-] [--strict|--warn]
  render_template.py --vars PATH                       # list variables used
  render_template.py --check-template PATH             # report variables vs frontmatter

Examples:
  # Render with profile + a small Pluuug-derived context blob
  render_template.py \
    --template skills/email-send/templates/30-견적송부.md \
    --context  context.json

  # Pipe context from stdin
  pluuug.py GET /v1/inquiry/489749 | render_template.py \
    --template skills/email-send/templates/00-신규접수-첫응답.md \
    --context -
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from profile import load_profile, get_active_member  # noqa: E402

VAR_RE = re.compile(r"\{\{\s*([a-zA-Z][a-zA-Z0-9_.]*)\s*\}\}")


def _dotted_get(obj: Any, path: str) -> Any:
    """Return obj.<dotted.path> or None if missing.

    Special handling: `team.pm` → first team member with role containing "PM"
    (case-insensitive), else None.
    """
    if not isinstance(obj, dict):
        return None
    parts = path.split(".")
    # special team.pm
    if parts[0] == "team" and len(parts) >= 2 and parts[1] == "pm":
        team = obj.get("team") or []
        if isinstance(team, list):
            for m in team:
                if isinstance(m, dict) and ("PM" in (m.get("role") or "").upper()):
                    cur: Any = m
                    for p in parts[2:]:
                        if isinstance(cur, dict):
                            cur = cur.get(p)
                        else:
                            cur = None
                            break
                    # if no further parts, fall back to name
                    if not parts[2:]:
                        return m.get("name") or ""
                    return cur if cur is not None else ""
        return None
    cur: Any = obj
    for p in parts:
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            return None
        if cur is None:
            return None
    return cur


def build_context(extra: dict | None = None) -> dict:
    """Merge profile + active member as `me` + extras into a single namespace."""
    profile = load_profile() or {}
    ctx = dict(profile)  # company / team / brand / products / phrases / defaults / keywords
    ctx["me"] = get_active_member(profile)
    if extra:
        # extras may include client, quote, meeting, contract, ...
        for k, v in extra.items():
            ctx[k] = v
    ctx.setdefault("date", datetime.date.today().isoformat())
    return ctx


def extract_variables(template_text: str) -> list[str]:
    """Return the deduplicated list of variable paths the template references."""
    found = []
    seen = set()
    for m in VAR_RE.finditer(template_text):
        v = m.group(1)
        if v not in seen:
            seen.add(v)
            found.append(v)
    return found


def render(template_text: str, context: dict, strict: bool = False, warn: bool = False) -> tuple[str, list[str]]:
    """Replace `{{path}}` with `context.path`. Return (rendered, missing)."""
    missing: list[str] = []

    def sub(match: re.Match) -> str:
        path = match.group(1)
        val = _dotted_get(context, path)
        if val is None or (isinstance(val, str) and val == ""):
            missing.append(path)
            if strict:
                return match.group(0)
            # leave placeholder visible for the human reviewer
            return match.group(0)
        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)
        return str(val)

    out = VAR_RE.sub(sub, template_text)
    if warn and missing:
        uniq = list(dict.fromkeys(missing))
        print(f"[render] unresolved variables: {', '.join(uniq)}", file=sys.stderr)
    return out, missing


def main() -> int:
    p = argparse.ArgumentParser(description="Render a sales email template.")
    p.add_argument("--template", metavar="PATH", help="Template markdown file.")
    p.add_argument("--context", metavar="FILE_OR_-",
                   help="JSON file (or '-' for stdin) merged into the context.")
    p.add_argument("--vars", metavar="PATH",
                   help="Print variables referenced by the template and exit.")
    p.add_argument("--check-template", metavar="PATH",
                   help="Compare template variables with its YAML frontmatter `variables:` list.")
    p.add_argument("--strict", action="store_true",
                   help="Exit with non-zero if any variable is missing.")
    p.add_argument("--warn", action="store_true",
                   help="Print missing variables to stderr but still render.")
    args = p.parse_args()

    if args.vars:
        with open(args.vars, "r", encoding="utf-8") as f:
            text = f.read()
        for v in extract_variables(text):
            print(v)
        return 0

    if args.check_template:
        with open(args.check_template, "r", encoding="utf-8") as f:
            text = f.read()
        used = set(extract_variables(text))
        # parse very simple YAML frontmatter
        declared: set[str] = set()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if m:
            for line in m.group(1).splitlines():
                line = line.strip()
                if line.startswith("- "):
                    declared.add(line[2:].strip().strip("'\""))
        extra_in_body = used - declared
        missing_in_body = declared - used
        if extra_in_body:
            print(f"used in body but not declared: {sorted(extra_in_body)}", file=sys.stderr)
        if missing_in_body:
            print(f"declared but not used: {sorted(missing_in_body)}", file=sys.stderr)
        return 0 if not extra_in_body else 1

    if not args.template:
        p.error("--template is required (or use --vars / --check-template)")

    with open(args.template, "r", encoding="utf-8") as f:
        text = f.read()

    extra: dict = {}
    if args.context:
        if args.context == "-":
            raw = sys.stdin.read()
        else:
            with open(args.context, "r", encoding="utf-8") as f:
                raw = f.read()
        try:
            blob = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[render] invalid context JSON: {e}", file=sys.stderr)
            return 2
        if isinstance(blob, dict):
            extra = blob

    ctx = build_context(extra)
    rendered, missing = render(text, ctx, strict=args.strict, warn=args.warn)
    sys.stdout.write(rendered)
    if args.strict and missing:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
