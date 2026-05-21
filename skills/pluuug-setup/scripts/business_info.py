#!/usr/bin/env python3
"""Manage the Pluuug business profile at an OS-standard config location.

Other sales skills (email-send, quote-writing, account-research, call-prep)
read this file to keep self-introductions, signatures, default contract terms,
and lead-fit keywords consistent across every customer-facing artifact.

Storage location (resolved at runtime, JSON, mode 0644):
  - macOS:   ~/Library/Application Support/pluuug/business.json
  - Linux:   $XDG_CONFIG_HOME/pluuug/business.json (default ~/.config)
  - Windows: %APPDATA%/pluuug/business.json
  - Fallback (all OS): ~/.pluuug/business.json

CLI usage:
  business_info.py --init           → print an empty template to stdout
  business_info.py --show           → print the currently installed profile
  business_info.py --show-path      → print the target file path
  business_info.py --from-file P    → install profile from a JSON file
  business_info.py --from-stdin     → install profile from stdin (JSON)
  business_info.py                  → interactive minimal install (core fields)

Exit codes:
  0  success
  2  invalid input
  3  file exists (use --force to overwrite)
  4  IO error
  5  profile not installed (only for --show)

This module is also importable: `from business_info import load_business_info`.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys

SCHEMA_VERSION = 1

TEMPLATE: dict = {
    "schemaVersion": SCHEMA_VERSION,
    "company": {
        "legalName": "",
        "displayName": "",
        "registrationNumber": "",
        "ceoName": "",
        "address": "",
        "domain": "",
        "homepage": ""
    },
    "business": {
        "industry": "",
        "targetCustomers": [],
        "coreProducts": [
            {"name": "", "description": ""}
        ],
        "strengths": [],
        "differentiation": ""
    },
    "voice": {
        "language": "ko",
        "tone": "formal_business",
        "signatureLines": []
    },
    "defaults": {
        "vatType": "E",
        "paymentTerms": "",
        "quoteValidityDays": 14
    },
    "keywords": {
        "goodFit": [],
        "outOfScope": []
    }
}


def get_business_paths() -> list[str]:
    home = os.path.expanduser("~")
    system = platform.system()
    paths: list[str] = []
    if system == "Darwin":
        paths.append(os.path.join(home, "Library", "Application Support", "pluuug", "business.json"))
    elif system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        paths.append(os.path.join(appdata, "pluuug", "business.json"))
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        paths.append(os.path.join(xdg, "pluuug", "business.json"))
    paths.append(os.path.join(home, ".pluuug", "business.json"))
    return paths


def get_business_path() -> str:
    """The canonical (write) location — the first candidate from get_business_paths()."""
    return get_business_paths()[0]


def load_business_info() -> dict:
    """Return the installed profile, or {} if none. Importable from other skills."""
    for path in get_business_paths():
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
    return {}


def _validate_minimal(data: dict) -> tuple[bool, str]:
    """Light schema sanity-check — does not reject extra fields."""
    if not isinstance(data, dict):
        return False, "root must be an object"
    sv = data.get("schemaVersion")
    if sv is not None and sv != SCHEMA_VERSION:
        return False, f"schemaVersion {sv} not supported (expected {SCHEMA_VERSION})"
    for key in ("company", "business", "voice", "defaults", "keywords"):
        if key in data and not isinstance(data[key], dict):
            return False, f"{key} must be an object"
    return True, ""


def write_business(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _interactive_minimal() -> dict:
    """Prompt only for the fields most worth filling on day one."""
    def ask(label: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        try:
            v = input(f"{label}{suffix}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[business] aborted", file=sys.stderr)
            sys.exit(2)
        return v or default

    print("Pluuug 비즈니스 프로필 — 핵심 필드만 입력합니다. 나머지는 나중에 직접 편집할 수 있습니다.\n"
          "(엔터로 건너뛰면 빈 값으로 저장됩니다.)")
    company_legal = ask("법인명 (예: 주식회사 똑똑한개발자)")
    company_display = ask("표시명 / 약칭", company_legal)
    domain = ask("도메인 (예: toktokhan.dev)")
    industry = ask("산업 / 카테고리")
    strength_1 = ask("핵심 강점 1")
    strength_2 = ask("핵심 강점 2")
    strength_3 = ask("핵심 강점 3")
    sig = ask("이메일 서명 한 줄", f"{company_display} | https://{domain}" if domain else company_display)

    profile = json.loads(json.dumps(TEMPLATE))  # deep copy
    profile["company"]["legalName"] = company_legal
    profile["company"]["displayName"] = company_display
    profile["company"]["domain"] = domain
    if domain:
        profile["company"]["homepage"] = f"https://{domain}"
    profile["business"]["industry"] = industry
    profile["business"]["strengths"] = [s for s in (strength_1, strength_2, strength_3) if s]
    profile["voice"]["signatureLines"] = [sig] if sig else []
    return profile


def main() -> int:
    p = argparse.ArgumentParser(description="Install / inspect Pluuug business profile.")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--init", action="store_true", help="Print empty template JSON to stdout (pipe to a file, edit, then --from-file).")
    mode.add_argument("--show", action="store_true", help="Print the installed profile to stdout.")
    mode.add_argument("--show-path", action="store_true", help="Print the target file path and exit.")
    mode.add_argument("--from-file", metavar="PATH", help="Install from a JSON file.")
    mode.add_argument("--from-stdin", action="store_true", help="Install from stdin (JSON).")
    p.add_argument("--force", action="store_true", help="Overwrite existing business.json without prompting.")
    args = p.parse_args()

    path = get_business_path()

    if args.show_path:
        print(path)
        return 0

    if args.init:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=2))
        return 0

    if args.show:
        profile = load_business_info()
        if not profile:
            print(f"[business] no profile found.\nLooked in: {get_business_paths()[0]}", file=sys.stderr)
            return 5
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        return 0

    # install paths
    if args.from_file:
        try:
            with open(args.from_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[business] cannot read {args.from_file}: {e}", file=sys.stderr)
            return 2
    elif args.from_stdin:
        raw = sys.stdin.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[business] stdin is not valid JSON: {e}", file=sys.stderr)
            return 2
    else:
        data = _interactive_minimal()

    ok, msg = _validate_minimal(data)
    if not ok:
        print(f"[business] schema check failed: {msg}", file=sys.stderr)
        return 2

    if os.path.exists(path) and not args.force:
        print(f"[business] profile already exists at:\n  {path}\nUse --force to overwrite.", file=sys.stderr)
        return 3

    try:
        write_business(path, data)
    except OSError as e:
        print(f"[business] failed to write {path}: {e}", file=sys.stderr)
        return 4

    print(f"[business] saved to {path}")
    print("영업 스킬들이 이 정보를 자동으로 참조합니다 — 메일 서명·견적서 회사정보·리드 적합성 판단 등.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
