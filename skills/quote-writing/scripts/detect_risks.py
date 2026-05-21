#!/usr/bin/env python3
"""
detect_risks.py — 견적 리스크 감지기
stdin: calc_margin.py 출력 JSON + 선택적 context 블록
stdout: JSON (risks 배열 + summary)
stdlib only
"""

import json
import sys
from datetime import date, datetime
from typing import Optional


def check_r1(data: dict) -> Optional[dict]:
    """R1: 전체 마진율 < 20% (warning), < 10% (critical)"""
    margin = data.get("totalMarginPercent")
    if margin is None:
        return None
    if margin < 10:
        return {
            "id": "R1",
            "severity": "critical",
            "title": "마진율 위험",
            "evidence": f"전체 마진율 {margin:.1f}% (임계치 10% 미만)",
            "recommendation": "견적 재검토 전까지 발행 보류 강력 권고. 단가 인상 또는 원가 절감 필요.",
        }
    if margin < 20:
        return {
            "id": "R1",
            "severity": "warning",
            "title": "마진율 낮음",
            "evidence": f"전체 마진율 {margin:.1f}% (임계치 20% 미만)",
            "recommendation": "단가 인상 또는 할인 축소 검토. 발행은 가능하나 재검토 권고.",
        }
    return None


def check_r2(data: dict, context: dict) -> Optional[dict]:
    """R2: 신규 단가(라이브러리 미등록) 비중 > 30%"""
    new_item_count = context.get("new_item_count", 0)
    total_item_count = context.get("total_item_count", 0)
    if total_item_count == 0:
        return None
    ratio = new_item_count / total_item_count * 100
    if ratio > 30:
        return {
            "id": "R2",
            "severity": "warning",
            "title": "신규 단가 비중 과다",
            "evidence": f"라이브러리 미등록 항목 {new_item_count}/{total_item_count}건 ({ratio:.1f}%)",
            "recommendation": "단가 근거 재확인 후 라이브러리 등록 권장.",
        }
    return None


def check_r3(data: dict) -> Optional[dict]:
    """R3: 할인 > 15%"""
    discount = data.get("discount", {})
    if discount.get("type") == "percent":
        value = float(discount.get("value", 0))
        if value > 15:
            return {
                "id": "R3",
                "severity": "warning",
                "title": "과도한 할인",
                "evidence": f"할인율 {value:.1f}% (임계치 15% 초과)",
                "recommendation": "승인 권한자 검토 필요. 가격 기준 훼손 방지.",
            }
    else:
        # 정액 할인: 소계 대비 비율 계산
        subtotal = data.get("subtotal", 0)
        discount_amount = data.get("discount_amount", 0)
        if subtotal > 0:
            ratio = discount_amount / subtotal * 100
            if ratio > 15:
                return {
                    "id": "R3",
                    "severity": "warning",
                    "title": "과도한 할인",
                    "evidence": f"할인액 {discount_amount:,}원 ({ratio:.1f}%) (임계치 15% 초과)",
                    "recommendation": "승인 권한자 검토 필요. 가격 기준 훼손 방지.",
                }
    return None


def check_r4(data: dict, context: dict) -> Optional[dict]:
    """R4: 동일 client 직전 30일 내 다른 견적 흔적"""
    text_history = context.get("recent_text_history", [])
    today = date.today()
    found = []
    for entry in text_history:
        content = entry.get("content", "")
        created_at = entry.get("created_at") or entry.get("date", "")
        if "견적" not in content:
            continue
        # 날짜 파싱 시도
        try:
            if "T" in created_at:
                entry_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
            else:
                entry_date = date.fromisoformat(created_at[:10])
            days_ago = (today - entry_date).days
            if 0 <= days_ago <= 30:
                found.append(f"'{content[:40]}...' ({days_ago}일 전)")
        except (ValueError, TypeError):
            continue
    if found:
        return {
            "id": "R4",
            "severity": "warning",
            "title": "가격 일관성 문제",
            "evidence": f"30일 내 동일 클라이언트 견적 흔적 {len(found)}건: {found[0]}",
            "recommendation": "기존 견적 무효화 여부 확인 후 발행.",
        }
    return None


def check_r5(data: dict) -> Optional[dict]:
    """R5: 부가세 표기 불명확 (vatType이 null이거나 unknown)"""
    vat_type = data.get("vatType")
    if vat_type not in ("E", "I", "N"):
        return {
            "id": "R5",
            "severity": "critical",
            "title": "부가세 표기 불명확",
            "evidence": f"vatType = {repr(vat_type)} (E/I/N 중 하나여야 함)",
            "recommendation": "vatType을 E(별도)/I(포함)/N(없음)으로 명시 후 재발행.",
        }
    return None


def check_r6(data: dict) -> Optional[dict]:
    """R6: 유효기간 < 7일"""
    valid_until = data.get("validUntil")
    if not valid_until:
        return None
    try:
        valid_date = date.fromisoformat(valid_until)
        days_left = (valid_date - date.today()).days
        if days_left < 7:
            return {
                "id": "R6",
                "severity": "warning",
                "title": "유효기간 촉박",
                "evidence": f"유효기간 {valid_until} — {days_left}일 남음 (임계치 7일)",
                "recommendation": "유효기간 연장 권고 (최소 14일).",
            }
    except ValueError:
        pass
    return None


def check_r7(data: dict, context: dict) -> Optional[dict]:
    """R7: 의뢰 본문 / text_history에 '예산 미상'/'검토 중'/'미확정' 키워드"""
    keywords = ["예산 미상", "검토 중", "미확정", "미정"]
    sources = []

    inquiry = context.get("inquiry", {})
    inquiry_text = inquiry.get("content", "") + " " + inquiry.get("description", "")
    for kw in keywords:
        if kw in inquiry_text:
            sources.append(f"의뢰 본문: '{kw}'")

    for entry in context.get("recent_text_history", []):
        content = entry.get("content", "")
        for kw in keywords:
            if kw in content:
                sources.append(f"text_history: '{kw}'")
                break

    if sources:
        return {
            "id": "R7",
            "severity": "warning",
            "title": "미확정 신호",
            "evidence": "; ".join(sources[:3]),
            "recommendation": "예산 및 요구사항 확정 후 견적 발행 권고.",
        }
    return None


def check_r8(context: dict) -> Optional[dict]:
    """R8: 결제 조건 미합의 — context에 payment_terms가 없거나 빈 값"""
    payment_terms = context.get("payment_terms")
    if not payment_terms:
        return {
            "id": "R8",
            "severity": "warning",
            "title": "결제 조건 미합의",
            "evidence": "context.payment_terms 없음 또는 빈 값",
            "recommendation": "결제 조건(선금/잔금 비율 및 시점)을 비고란에 명시.",
        }
    return None


def check_r9(data: dict) -> Optional[dict]:
    """R9: 외부 라이선스/SaaS 항목인데 costEstimate 없음"""
    # SaaS/라이선스 키워드 패턴
    saas_keywords = ["saas", "라이선스", "license", "구독", "subscription", "클라우드", "cloud", "aws", "azure", "gcp"]
    missing = []
    for item in data.get("items", []):
        title = item.get("title", "").lower()
        is_saas = any(kw in title for kw in saas_keywords)
        if is_saas and item.get("costEstimate") is None:
            missing.append(item.get("title", ""))
    if missing:
        return {
            "id": "R9",
            "severity": "critical",
            "title": "외부 라이선스 원가 누락",
            "evidence": f"SaaS/라이선스 항목 {len(missing)}건 원가 미입력: {', '.join(missing[:3])}",
            "recommendation": "해당 항목의 실제 라이선스/SaaS 비용을 costEstimate에 입력 후 재계산.",
        }
    return None


def check_r10(data: dict, context: dict) -> Optional[dict]:
    """R10: 항목 총수 대비 신규 단가 = 100% (모든 항목이 라이브러리에 없음)"""
    new_item_count = context.get("new_item_count", 0)
    total_item_count = context.get("total_item_count", 0)
    if total_item_count > 0 and new_item_count >= total_item_count:
        return {
            "id": "R10",
            "severity": "critical",
            "title": "전체 신규 단가",
            "evidence": f"모든 항목({total_item_count}건)이 라이브러리 미등록 신규 단가",
            "recommendation": "단가 근거 전수 확인 후 라이브러리 등록 필요. 단가 신뢰도 심각하게 낮음.",
        }
    return None


def detect_risks(data: dict) -> dict:
    context = data.get("context", {})

    checkers = [
        check_r1(data),
        check_r2(data, context),
        check_r3(data),
        check_r4(data, context),
        check_r5(data),
        check_r6(data),
        check_r7(data, context),
        check_r8(context),
        check_r9(data),
        check_r10(data, context),
    ]

    risks = [r for r in checkers if r is not None]

    summary = {
        "critical": sum(1 for r in risks if r["severity"] == "critical"),
        "warning": sum(1 for r in risks if r["severity"] == "warning"),
        "info": sum(1 for r in risks if r["severity"] == "info"),
    }

    return {"risks": risks, "summary": summary}


if __name__ == "__main__":
    raw = sys.stdin.read()
    data = json.loads(raw)
    result = detect_risks(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
