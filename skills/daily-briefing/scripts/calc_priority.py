#!/usr/bin/env python3
"""calc_priority.py — 데일리 브리핑 우선순위 점수 계산기.

JSON manifest(fetch_briefing.sh 출력)를 읽어 점수표 기준으로 #1 우선순위를 선정합니다.

사용법:
  calc_priority.py manifest.json
  calc_priority.py --manifest manifest.json
  fetch_briefing.sh | calc_priority.py -   # stdin 지원

환경 변수 (필수):
  PLUUUG_API_KEY      Pluuug API 키
  PLUUUG_SECRET_KEY   HMAC 서명용 시크릿

출력: JSON (stdout)
  {
    "priority": {"score": 100, "reason": "...", "category": "..."},
    "alternatives": [...],
    "computed_at": "2026-05-21T09:00:00+09:00"
  }
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

# KST = UTC+9
try:
    from zoneinfo import ZoneInfo
    KST = ZoneInfo("Asia/Seoul")
except ImportError:
    # Python < 3.9 폴백
    KST = timezone(timedelta(hours=9))


# ── 유틸 ─────────────────────────────────────────────────────────────────────

def _load_json_file(path: str) -> object:
    """JSON 파일을 로드합니다. 실패 시 {"_error": "..."} 반환."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": str(e)}


def _items(data: object) -> list[dict]:
    """API 응답에서 항목 목록을 추출합니다 (list 또는 {"data": [...]} 형태 모두 처리)."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "_error" in data:
            return []
        # 페이지네이션 래퍼: {"data": [...], "total": N}
        for key in ("data", "items", "results", "content"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


def _parse_date(val: str | None) -> date | None:
    """ISO 날짜 문자열(YYYY-MM-DD 또는 datetime) 을 date 객체로 변환합니다."""
    if not val:
        return None
    try:
        return date.fromisoformat(str(val)[:10])
    except ValueError:
        return None


# ── 점수 계산 ─────────────────────────────────────────────────────────────────

def compute_priority(manifest: dict) -> dict:
    """manifest 를 받아 우선순위 결과 dict 를 반환합니다."""
    now_kst = datetime.now(tz=KST)
    today = now_kst.date()

    # manifest 에 dates 가 있으면 사용
    dates = manifest.get("dates", {})
    if dates.get("today"):
        today_override = _parse_date(dates["today"])
        if today_override:
            today = today_override

    files = manifest.get("files", {})

    # 각 파일 로드
    settlement_settled = _items(_load_json_file(files.get("settlement_settled", "")))
    settlement_due     = _items(_load_json_file(files.get("settlement_due", "")))
    todo_dday          = _items(_load_json_file(files.get("todo_dday", "")))
    inquiry_today      = _items(_load_json_file(files.get("inquiry_today", "")))
    inquiry_yesterday  = _items(_load_json_file(files.get("inquiry_yesterday", "")))
    project_active     = _items(_load_json_file(files.get("project_active", "")))

    candidates: list[dict] = []

    # ── 100점: 정산 지연 (status=D) ──────────────────────────────────────────
    all_settlements = settlement_settled + settlement_due
    delayed = [s for s in all_settlements if s.get("status") == "D"]
    if delayed:
        total_amt = sum(
            (s.get("amount", 0) or 0) + (s.get("additionalAmount", 0) or 0)
            for s in delayed
        )
        candidates.append({
            "score": 100,
            "reason": f"정산 지연 {len(delayed)}건 합계 {total_amt:,.0f}원",
            "category": "settlement_delayed",
            "amount": total_amt,
        })

    # ── 90점: 세금계산서 발행 기한 오늘~+1일 이내 ────────────────────────────
    tax_warn = [
        s for s in all_settlements
        if not s.get("isTaxInvoiceIssued", True)
        and _parse_date(s.get("taxInvoiceIssueDueDate")) is not None
        and _parse_date(s.get("taxInvoiceIssueDueDate")) <= today + timedelta(days=1)
    ]
    if tax_warn:
        candidates.append({
            "score": 90,
            "reason": f"세금계산서 발행 기한 임박 {len(tax_warn)}건 (오늘~+1일 이내)",
            "category": "tax_invoice_urgent",
            "amount": 0,
        })

    # ── 80점: 오늘 외부 미팅 — 캘린더 데이터 없으므로 스킵 ──────────────────
    # (캘린더는 MCP 실시간 조회이므로 manifest 에 포함되지 않음)

    # ── 70점: D-day Todo 3건 이상 ────────────────────────────────────────────
    dday_todos = [
        t for t in todo_dday
        if not t.get("is_complete", False)
        and _parse_date(t.get("due_date")) is not None
        and _parse_date(t.get("due_date")) <= today
    ]
    if len(dday_todos) >= 3:
        candidates.append({
            "score": 70,
            "reason": f"D-day Todo {len(dday_todos)}건 (오늘까지 마감)",
            "category": "todo_dday_many",
            "amount": 0,
        })
    # ── 60점: D-day Todo 1건 이상 ────────────────────────────────────────────
    elif len(dday_todos) >= 1:
        candidates.append({
            "score": 60,
            "reason": f"D-day Todo {len(dday_todos)}건 (오늘까지 마감)",
            "category": "todo_dday_some",
            "amount": 0,
        })

    # ── 55점: 어제 신규 의뢰 중 미처리 ──────────────────────────────────────
    # 초기 단계 의뢰: status 가 첫 번째 단계(일반적으로 "접수" 또는 낮은 순번)
    # API 응답의 status 필드가 초기값(예: 1, "01", "접수" 등)인 경우 미처리로 간주
    # 정확한 초기 단계는 inquiry_status 에 있으나, 보수적으로 status 변동 없는 건으로 판단
    unprocessed_yesterday = [
        i for i in inquiry_yesterday
        # status 가 숫자면 1, 문자열이면 "01"/"접수" 등 초기값
        if str(i.get("status", "")).strip() in ("1", "01", "접수", "신규", "new", "NEW")
    ]
    if unprocessed_yesterday:
        candidates.append({
            "score": 55,
            "reason": f"어제 신규 의뢰 미처리 {len(unprocessed_yesterday)}건",
            "category": "inquiry_yesterday_unprocessed",
            "amount": 0,
        })

    # ── 50점: 오늘 신규 의뢰 존재 ───────────────────────────────────────────
    if inquiry_today:
        candidates.append({
            "score": 50,
            "reason": f"오늘 신규 의뢰 {len(inquiry_today)}건",
            "category": "inquiry_today_new",
            "amount": 0,
        })

    # ── 40점: 당월 정산 예정 D-7 이내 ───────────────────────────────────────
    upcoming_due = [
        s for s in settlement_due
        if s.get("status") == "C"
        and _parse_date(s.get("dueDate") or s.get("due_date")) is not None
        and _parse_date(s.get("dueDate") or s.get("due_date")) <= today + timedelta(days=7)
    ]
    if upcoming_due:
        total_upcoming = sum(
            (s.get("amount", 0) or 0) + (s.get("additionalAmount", 0) or 0)
            for s in upcoming_due
        )
        candidates.append({
            "score": 40,
            "reason": f"당월 정산 예정 D-7 이내 {len(upcoming_due)}건 합계 {total_upcoming:,.0f}원",
            "category": "settlement_due_soon",
            "amount": total_upcoming,
        })

    # ── 30점: 진행 중 프로젝트 endDate 임박 (D-7 이내) ──────────────────────
    ending_soon = [
        p for p in project_active
        if _parse_date(p.get("endDate") or p.get("end_date")) is not None
        and _parse_date(p.get("endDate") or p.get("end_date")) <= today + timedelta(days=7)
    ]
    if ending_soon:
        candidates.append({
            "score": 30,
            "reason": f"프로젝트 종료 임박 {len(ending_soon)}건 (D-7 이내)",
            "category": "project_ending_soon",
            "amount": 0,
        })

    # ── 10점: 기본 (긴급 사항 없음) ─────────────────────────────────────────
    candidates.append({
        "score": 10,
        "reason": "긴급 사항 없음 — 이번 주 Todo 점검을 권장합니다.",
        "category": "no_urgent",
        "amount": 0,
    })

    # ── 정렬: 점수 내림차순, 동점이면 금액 내림차순 ──────────────────────────
    candidates.sort(key=lambda c: (c["score"], c.get("amount", 0)), reverse=True)

    top = candidates[0]
    alternatives = candidates[1:]

    # amount 필드는 내부 계산용이므로 출력에서 제거
    def _clean(c: dict) -> dict:
        return {k: v for k, v in c.items() if k != "amount"}

    return {
        "priority": _clean(top),
        "alternatives": [_clean(a) for a in alternatives],
        "computed_at": now_kst.isoformat(),
    }


# ── 엔트리포인트 ──────────────────────────────────────────────────────────────

def main() -> int:
    # 환경 변수 확인
    if not os.environ.get("PLUUUG_API_KEY") or not os.environ.get("PLUUUG_SECRET_KEY"):
        print(
            "오류: PLUUUG_API_KEY 또는 PLUUUG_SECRET_KEY 환경 변수가 설정되어 있지 않습니다.\n"
            "설정 방법은 skills/pluuug-api/SKILL.md 또는 README.md 를 참고하세요.",
            file=sys.stderr,
        )
        return 2

    parser = argparse.ArgumentParser(description="데일리 브리핑 우선순위 계산기")
    parser.add_argument(
        "manifest_pos",
        nargs="?",
        help="manifest JSON 파일 경로 (또는 '-' 로 stdin 읽기)",
    )
    parser.add_argument(
        "--manifest",
        dest="manifest_flag",
        help="manifest JSON 파일 경로",
    )
    args = parser.parse_args()

    manifest_path = args.manifest_flag or args.manifest_pos

    if not manifest_path or manifest_path == "-":
        raw = sys.stdin.read()
    else:
        try:
            with open(manifest_path, encoding="utf-8") as f:
                raw = f.read()
        except OSError as e:
            print(f"오류: manifest 파일을 열 수 없습니다 — {e}", file=sys.stderr)
            return 2

    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"오류: manifest JSON 파싱 실패 — {e}", file=sys.stderr)
        return 2

    result = compute_priority(manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
