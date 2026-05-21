#!/usr/bin/env python3
"""Verify the sales-automation setup gate before running other sales skills.

3 levels, cumulative:

  L0 — Pluuug-callable
       Requires credentials.json (PLUUUG_API_KEY + PLUUUG_SECRET_KEY).
       Without L0, no skill can hit the Pluuug Open API.

  L1 — Customer-facing artifacts safe
       L0 + active team member with name/email/signature + company.displayName.
       Without L1, email-send / quote-writing / call-summary would produce
       artifacts with empty signatures or generic supplier info.

  L2 — Fully automated (no human placeholders left)
       L1 + brand.tagline + at least one brand.strength + defaults.paymentTerms.
       Without L2 the artifacts still go out, but with generic phrasing.

Usage:
  check_setup.py --level L0|L1|L2 [--json] [--quiet]

Exit codes:
  0 → passes the requested level
  1 → blocking gaps at the requested level (caller should halt)
  2 → bad invocation

Other sales skills should call this at the start of their procedure:

  if ! skills/sales-setup/scripts/check_setup.py --level L1 --quiet; then
    echo "Setup incomplete. Run sales-setup first."
    exit 1
  fi
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from profile import load_profile, get_active_member  # noqa: E402


def _credentials_paths() -> list[str]:
    home = os.path.expanduser("~")
    system = platform.system()
    out: list[str] = []
    if system == "Darwin":
        out.append(os.path.join(home, "Library", "Application Support", "sales-automation", "credentials.json"))
        out.append(os.path.join(home, "Library", "Application Support", "pluuug", "credentials.json"))
    elif system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        out.append(os.path.join(appdata, "sales-automation", "credentials.json"))
        out.append(os.path.join(appdata, "pluuug", "credentials.json"))
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        out.append(os.path.join(xdg, "sales-automation", "credentials.json"))
        out.append(os.path.join(xdg, "pluuug", "credentials.json"))
    out.append(os.path.join(home, ".sales-automation", "credentials.json"))
    out.append(os.path.join(home, ".pluuug", "credentials.json"))
    return out


def _has_credentials() -> tuple[bool, str]:
    # env vars win
    if os.environ.get("PLUUUG_API_KEY") and os.environ.get("PLUUUG_SECRET_KEY"):
        return True, "환경 변수"
    # project .env (search up)
    here = HERE
    for _ in range(6):
        cand = os.path.join(here, ".env")
        if os.path.isfile(cand):
            with open(cand, "r", encoding="utf-8") as f:
                content = f.read()
            if "PLUUUG_API_KEY" in content and "PLUUUG_SECRET_KEY" in content:
                return True, cand
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    # OS files
    for path in _credentials_paths():
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        api = data.get("api_key") or data.get("PLUUUG_API_KEY")
        secret = data.get("secret_key") or data.get("PLUUUG_SECRET_KEY")
        if api and secret:
            return True, path
    return False, ""


def _profile_field(profile: dict, path: str) -> bool:
    """True if dotted path has a non-empty value."""
    cur = profile
    for p in path.split("."):
        if not isinstance(cur, dict):
            return False
        cur = cur.get(p)
        if cur is None:
            return False
    if isinstance(cur, str):
        return bool(cur.strip())
    if isinstance(cur, (list, dict)):
        return bool(cur)
    return cur not in (None, "", 0)


def _check_active_member(profile: dict, field: str) -> bool:
    me = get_active_member(profile)
    if not isinstance(me, dict):
        return False
    v = me.get(field)
    if isinstance(v, str):
        return bool(v.strip())
    return v not in (None, "", 0, [], {})


CHECKS = {
    "L0": [
        ("credentials", "Pluuug API credentials", lambda prof: _has_credentials()[0],
         "sales-setup/scripts/install_credentials.py 실행"),
    ],
    "L1": [
        ("me.name", "활성 영업 담당자 이름",
         lambda prof: _check_active_member(prof, "name"),
         "profile.json의 team 배열에서 active=true 멤버의 name 입력"),
        ("me.email", "활성 영업 담당자 이메일",
         lambda prof: _check_active_member(prof, "email"),
         "profile.json의 team[active].email 입력"),
        ("me.signature", "활성 영업 담당자 서명",
         lambda prof: _check_active_member(prof, "signature"),
         "profile.json의 team[active].signature (멀티라인) 입력"),
        ("company.displayName", "회사 표시명",
         lambda prof: _profile_field(prof, "company.displayName"),
         "profile.json의 company.displayName 입력"),
    ],
    "L2": [
        ("brand.tagline", "브랜드 한 줄 자기소개",
         lambda prof: _profile_field(prof, "brand.tagline"),
         "profile.json의 brand.tagline 입력"),
        ("brand.strengths", "강점 1개 이상",
         lambda prof: _profile_field(prof, "brand.strengths"),
         "profile.json의 brand.strengths 배열에 항목 추가"),
        ("defaults.paymentTerms", "기본 결제 조건",
         lambda prof: _profile_field(prof, "defaults.paymentTerms"),
         "profile.json의 defaults.paymentTerms 입력 (예: '선금 50% / 잔금 50%')"),
    ],
}


def _evaluate(level: str) -> tuple[dict, bool]:
    """Run all checks up to (and including) `level`. Returns (report, passes)."""
    profile = load_profile()
    levels_to_run = ["L0"]
    if level in ("L1", "L2"):
        levels_to_run.append("L1")
    if level == "L2":
        levels_to_run.append("L2")
    report: dict = {"profile_installed": bool(profile), "levels": {}}
    overall_pass = True
    for lv in levels_to_run:
        results = []
        passed_count = 0
        for field, label, fn, fix in CHECKS[lv]:
            ok = bool(fn(profile))
            results.append({
                "field": field,
                "label": label,
                "ok": ok,
                "fix": "" if ok else fix,
            })
            if ok:
                passed_count += 1
        lv_pass = passed_count == len(CHECKS[lv])
        report["levels"][lv] = {
            "passed": lv_pass,
            "total": len(CHECKS[lv]),
            "matched": passed_count,
            "checks": results,
        }
        if lv == level and not lv_pass:
            overall_pass = False
        if lv == "L0" and not lv_pass:
            # L0 fail blocks everything above too
            overall_pass = False
    report["requested_level"] = level
    report["pass"] = overall_pass
    return report, overall_pass


def _human_report(report: dict) -> str:
    out = []
    out.append(f"Sales-automation setup check — 요청 레벨: {report['requested_level']}")
    out.append(f"Profile installed: {'✅' if report['profile_installed'] else '❌'}")
    out.append("")
    for lv, info in report["levels"].items():
        mark = "✅" if info["passed"] else "❌"
        out.append(f"{mark} {lv} — {info['matched']}/{info['total']}")
        for c in info["checks"]:
            cm = "  ✓" if c["ok"] else "  ✗"
            out.append(f"{cm} {c['label']} ({c['field']})")
            if not c["ok"]:
                out.append(f"      → 해결: {c['fix']}")
    out.append("")
    if report["pass"]:
        out.append("RESULT: PASS — 진행 가능")
    else:
        out.append("RESULT: FAIL — sales-setup으로 부족 항목 채운 후 다시 시도")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description="Check sales-automation setup gate.")
    p.add_argument("--level", choices=["L0", "L1", "L2"], default="L0",
                   help="Required level (default: L0).")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    p.add_argument("--quiet", action="store_true", help="Suppress output; rely on exit code.")
    args = p.parse_args()

    report, ok = _evaluate(args.level)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif not args.quiet:
        print(_human_report(report), file=sys.stderr if not ok else sys.stdout)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
