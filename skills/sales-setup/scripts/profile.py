#!/usr/bin/env python3
"""Manage the unified sales profile at an OS-standard config location.

The profile is the single source of truth that lets every sales skill produce
consistent customer-facing artifacts — email signatures, quote supplier blocks,
call openers, lead-fit scoring, etc.

Storage location (resolved at runtime, JSON):
  - macOS:   ~/Library/Application Support/sales-automation/profile.json
  - Linux:   $XDG_CONFIG_HOME/sales-automation/profile.json
  - Windows: %APPDATA%/sales-automation/profile.json
  - Fallback (all OS): ~/.sales-automation/profile.json

Legacy fallback (auto-migrated when read):
  - <config>/pluuug/business.json  (schemaVersion 1)

Schema (v2): 7 sections — all optional, fill what you have.
  company   법인 메타 (legalName / displayName / registrationNumber / address / ...)
  team      영업 담당자 배열 (멤버별 name/role/email/phone/signature, active 1명)
  brand     강점·차별화·톤·산업·타깃 (이전 business + voice 통합)
  products  메인 상품/서비스 목록 (name / description / target / defaultPrice)
  phrases   카테고리별 자주 쓰는 멘트 (greeting / intro / ctaMeeting / decline 등)
  defaults  기본 계약 조건 (vatType / paymentTerms / quoteValidityDays)
  keywords  리드 적합도 (goodFit / outOfScope)

CLI:
  profile.py --init          → empty template to stdout
  profile.py --show          → installed profile
  profile.py --show-path     → write path
  profile.py --active        → just the active team member as JSON
  profile.py --from-file P   → install from a JSON file
  profile.py --from-stdin    → install from stdin (JSON)
  profile.py --migrate       → upgrade legacy pluuug/business.json to sales-automation/profile.json
  profile.py                 → interactive minimal install (core fields)

Python import:
  from profile import load_profile, get_active_member
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from typing import Any

SCHEMA_VERSION = 2

TEMPLATE: dict = {
    "schemaVersion": SCHEMA_VERSION,
    "company": {
        "legalName": "",
        "displayName": "",
        "registrationNumber": "",
        "ceoName": "",
        "address": "",
        "domain": "",
        "homepage": "",
        "phone": ""
    },
    "team": [
        {
            "id": "default",
            "active": True,
            "name": "",
            "role": "",
            "email": "",
            "phone": "",
            "signature": ""
        }
    ],
    "brand": {
        "tagline": "",
        "tone": "formal_business",
        "language": "ko",
        "industry": "",
        "targetCustomers": [],
        "strengths": [],
        "differentiation": "",
        "values": []
    },
    "products": [
        {
            "id": "default",
            "name": "",
            "description": "",
            "target": "",
            "defaultPrice": None,
            "unitType": ""
        }
    ],
    "phrases": {
        "greeting": [],
        "intro": [],
        "ctaMeeting": [],
        "ctaQuote": [],
        "ctaFollowup": [],
        "thanks": [],
        "decline": [],
        "discount": []
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


def get_profile_paths() -> list[str]:
    """New canonical paths first, then legacy fallback (read-only)."""
    home = os.path.expanduser("~")
    paths: list[str] = []
    system = platform.system()
    # new (v2)
    if system == "Darwin":
        paths.append(os.path.join(home, "Library", "Application Support", "sales-automation", "profile.json"))
    elif system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        paths.append(os.path.join(appdata, "sales-automation", "profile.json"))
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        paths.append(os.path.join(xdg, "sales-automation", "profile.json"))
    paths.append(os.path.join(home, ".sales-automation", "profile.json"))
    # legacy (v1) — auto-migrated on read
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


def get_profile_path() -> str:
    """The canonical write location (first entry)."""
    return get_profile_paths()[0]


def _migrate_v1_to_v2(v1: dict) -> dict:
    """Upgrade legacy business.json (schemaVersion 1) to profile.json (v2)."""
    out = json.loads(json.dumps(TEMPLATE))  # deep copy
    company_v1 = v1.get("company", {}) or {}
    business_v1 = v1.get("business", {}) or {}
    voice_v1 = v1.get("voice", {}) or {}
    defaults_v1 = v1.get("defaults", {}) or {}
    keywords_v1 = v1.get("keywords", {}) or {}

    # company → company
    for k in ("legalName", "displayName", "registrationNumber", "ceoName",
              "address", "domain", "homepage"):
        if company_v1.get(k):
            out["company"][k] = company_v1[k]

    # voice.signatureLines → team[0].signature (joined); voice.tone/language → brand
    sig = voice_v1.get("signatureLines") or []
    if sig:
        out["team"][0]["signature"] = "\n".join(s for s in sig if s)
    if voice_v1.get("tone"):
        out["brand"]["tone"] = voice_v1["tone"]
    if voice_v1.get("language"):
        out["brand"]["language"] = voice_v1["language"]

    # business → brand
    for src, dst in (("industry", "industry"),
                     ("targetCustomers", "targetCustomers"),
                     ("strengths", "strengths"),
                     ("differentiation", "differentiation")):
        if business_v1.get(src):
            out["brand"][dst] = business_v1[src]

    # business.coreProducts → products
    cps = business_v1.get("coreProducts") or []
    if cps:
        out["products"] = []
        for cp in cps:
            if not isinstance(cp, dict):
                continue
            out["products"].append({
                "id": cp.get("id", ""),
                "name": cp.get("name", ""),
                "description": cp.get("description", ""),
                "target": cp.get("target", ""),
                "defaultPrice": cp.get("defaultPrice"),
                "unitType": cp.get("unitType", "")
            })

    # defaults, keywords pass-through
    for k in ("vatType", "paymentTerms", "quoteValidityDays"):
        if defaults_v1.get(k) is not None:
            out["defaults"][k] = defaults_v1[k]
    for k in ("goodFit", "outOfScope"):
        if keywords_v1.get(k):
            out["keywords"][k] = keywords_v1[k]

    return out


def load_profile() -> dict:
    """Return the installed profile, auto-migrating legacy v1 if needed.

    Returns {} when nothing is installed. Never writes.
    """
    for path in get_profile_paths():
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        sv = data.get("schemaVersion")
        if sv == SCHEMA_VERSION:
            return data
        if sv == 1:
            return _migrate_v1_to_v2(data)
        return data
    return {}


def get_active_member(profile: dict | None = None) -> dict:
    """Return the active team member (or first), or {} if no team."""
    p = profile if profile is not None else load_profile()
    team = p.get("team") or []
    if not isinstance(team, list) or not team:
        return {}
    for m in team:
        if isinstance(m, dict) and m.get("active"):
            return m
    return team[0] if isinstance(team[0], dict) else {}


def _validate(data: Any) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "root must be an object"
    sv = data.get("schemaVersion")
    if sv is not None and sv not in (1, 2):
        return False, f"unsupported schemaVersion {sv} (expected 1 or 2)"
    for key in ("company", "brand", "defaults", "keywords", "phrases"):
        if key in data and not isinstance(data[key], dict):
            return False, f"{key} must be an object"
    for key in ("team", "products"):
        if key in data and not isinstance(data[key], list):
            return False, f"{key} must be a list"
    return True, ""


def _write(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _interactive_minimal() -> dict:
    def ask(label: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        try:
            v = input(f"{label}{suffix}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[sales-setup] aborted", file=sys.stderr)
            sys.exit(2)
        return v or default

    print("Sales 프로필 초기 설정 — 핵심 필드만 입력합니다.\n"
          "(엔터로 건너뛰면 빈 값으로 저장됩니다. 나머지는 나중에 편집 가능.)")
    legal = ask("법인명 (예: 주식회사 똑똑한개발자)")
    display = ask("표시명 / 브랜드 약칭", legal)
    domain = ask("도메인 (예: toktokhan.dev)")
    industry = ask("산업 / 카테고리")
    me_name = ask("내 이름 (영업 담당자)")
    me_role = ask("내 직책", "영업담당자")
    me_email = ask("내 이메일")
    me_phone = ask("내 연락처")
    strength_1 = ask("핵심 강점 1")
    strength_2 = ask("핵심 강점 2")

    p = json.loads(json.dumps(TEMPLATE))
    p["company"]["legalName"] = legal
    p["company"]["displayName"] = display
    p["company"]["domain"] = domain
    if domain:
        p["company"]["homepage"] = f"https://{domain}"
    p["brand"]["industry"] = industry
    p["brand"]["strengths"] = [s for s in (strength_1, strength_2) if s]
    p["team"][0].update({
        "name": me_name,
        "role": me_role,
        "email": me_email,
        "phone": me_phone,
        "signature": "\n".join([s for s in (
            f"{me_name} / {me_role}".strip(" /"),
            display if display else "",
            f"{me_email}" if me_email else "",
            f"{me_phone}" if me_phone else "",
            f"https://{domain}" if domain else "",
        ) if s])
    })
    return p


def main() -> int:
    p = argparse.ArgumentParser(description="Install / inspect the sales profile.")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--init", action="store_true", help="Print empty template JSON to stdout.")
    mode.add_argument("--show", action="store_true", help="Print the installed profile.")
    mode.add_argument("--show-path", action="store_true", help="Print the write path and exit.")
    mode.add_argument("--active", action="store_true", help="Print the active team member as JSON.")
    mode.add_argument("--from-file", metavar="PATH", help="Install profile from JSON file.")
    mode.add_argument("--from-stdin", action="store_true", help="Install profile from stdin JSON.")
    mode.add_argument("--migrate", action="store_true",
                      help="Read legacy <config>/pluuug/business.json and save as v2 at the new path.")
    p.add_argument("--force", action="store_true", help="Overwrite existing profile.json.")
    args = p.parse_args()

    target = get_profile_path()

    if args.show_path:
        print(target)
        return 0

    if args.init:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=2))
        return 0

    if args.show:
        prof = load_profile()
        if not prof:
            print(f"[sales-setup] no profile found.\nExpected at: {target}", file=sys.stderr)
            return 5
        print(json.dumps(prof, ensure_ascii=False, indent=2))
        return 0

    if args.active:
        m = get_active_member()
        if not m:
            print("[sales-setup] no team configured", file=sys.stderr)
            return 5
        print(json.dumps(m, ensure_ascii=False, indent=2))
        return 0

    if args.migrate:
        legacy = None
        for path in get_profile_paths():
            if path.endswith("business.json") and os.path.isfile(path):
                legacy = path
                break
        if not legacy:
            print("[sales-setup] no legacy business.json found", file=sys.stderr)
            return 5
        try:
            with open(legacy, "r", encoding="utf-8") as f:
                v1 = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[sales-setup] cannot read legacy file: {e}", file=sys.stderr)
            return 4
        upgraded = _migrate_v1_to_v2(v1)
        if os.path.exists(target) and not args.force:
            print(f"[sales-setup] {target} already exists. Use --force to overwrite.", file=sys.stderr)
            return 3
        try:
            _write(target, upgraded)
        except OSError as e:
            print(f"[sales-setup] failed to write {target}: {e}", file=sys.stderr)
            return 4
        print(f"[sales-setup] migrated {legacy} → {target}")
        return 0

    if args.from_file:
        try:
            with open(args.from_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[sales-setup] cannot read {args.from_file}: {e}", file=sys.stderr)
            return 2
    elif args.from_stdin:
        raw = sys.stdin.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[sales-setup] stdin is not valid JSON: {e}", file=sys.stderr)
            return 2
    else:
        data = _interactive_minimal()

    ok, msg = _validate(data)
    if not ok:
        print(f"[sales-setup] schema check failed: {msg}", file=sys.stderr)
        return 2

    if data.get("schemaVersion") == 1:
        data = _migrate_v1_to_v2(data)

    if os.path.exists(target) and not args.force:
        print(f"[sales-setup] profile already exists at:\n  {target}\nUse --force to overwrite.",
              file=sys.stderr)
        return 3

    try:
        _write(target, data)
    except OSError as e:
        print(f"[sales-setup] failed to write {target}: {e}", file=sys.stderr)
        return 4

    print(f"[sales-setup] saved to {target}")
    print("영업 스킬들이 이 프로필을 참조해 일관된 자기소개·서명·기본값을 사용합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
