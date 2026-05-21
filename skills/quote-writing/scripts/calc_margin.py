#!/usr/bin/env python3
"""
calc_margin.py — 견적 손익 계산기
stdin: JSON (items + discount + vatType + validUntil)
stdout: JSON (손익 분석 결과)
stdlib only, Decimal 사용으로 float 오차 방지
"""

import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from datetime import date


def parse_decimal(value) -> Decimal:
    """문자열 또는 숫자를 Decimal로 변환"""
    if value is None:
        return None
    return Decimal(str(value))


def round_decimal(value: Decimal, places: int = 0) -> Decimal:
    """지정 소수점 자리로 반올림"""
    quantize_str = Decimal("1") if places == 0 else Decimal("0." + "0" * places)
    return value.quantize(quantize_str, rounding=ROUND_HALF_UP)


def calc_margin(data: dict) -> dict:
    items = data.get("items", [])
    discount_info = data.get("discount", {})
    vat_type = data.get("vatType", "E")  # E: 별도, I: 포함, N: 없음
    valid_until = data.get("validUntil")

    warnings = []
    result_items = []
    total_subtotal = Decimal("0")
    total_cost = Decimal("0")
    missing_cost_count = 0

    for item in items:
        quantity = parse_decimal(item.get("quantity", 1))
        unit_cost = parse_decimal(item.get("unitCost", 0))
        cost_estimate_raw = item.get("costEstimate")
        cost_estimate = parse_decimal(cost_estimate_raw) if cost_estimate_raw is not None else None

        subtotal = quantity * unit_cost
        total_subtotal += subtotal

        if cost_estimate is not None:
            margin_amount = subtotal - cost_estimate
            # 마진율: 소계 기준 (소계가 0이면 N/A)
            if subtotal != Decimal("0"):
                margin_percent = round_decimal(margin_amount / subtotal * 100, 1)
            else:
                margin_percent = Decimal("0")
            total_cost += cost_estimate
        else:
            margin_amount = None
            margin_percent = None
            missing_cost_count += 1

        result_item = dict(item)
        result_item["subtotal"] = int(subtotal)
        result_item["marginAmount"] = int(margin_amount) if margin_amount is not None else None
        result_item["marginPercent"] = float(margin_percent) if margin_percent is not None else None
        result_items.append(result_item)

    # 할인 계산 (단 한 번만 적용)
    discount_type = discount_info.get("type", "percent")
    discount_value = parse_decimal(discount_info.get("value", 0))

    if discount_type == "percent":
        discount_amount = round_decimal(total_subtotal * discount_value / Decimal("100"))
    else:
        # 정액 할인
        discount_amount = discount_value

    taxable = total_subtotal - discount_amount

    # 부가세 계산
    if vat_type == "E":
        vat = round_decimal(taxable * Decimal("0.1"))
        total = taxable + vat
    elif vat_type == "I":
        # 부가세 포함 — 추가 없음
        vat = round_decimal(taxable * Decimal("0.1") / Decimal("1.1"))
        total = taxable
    elif vat_type == "N":
        vat = Decimal("0")
        total = taxable
    else:
        # 알 수 없는 vatType
        vat = Decimal("0")
        total = taxable
        warnings.append(f"vatType '{vat_type}'이 유효하지 않습니다. N으로 처리되었습니다.")

    # 수익(revenue): 부가세 제외 합계
    revenue = taxable

    # 전체 마진 (원가 있는 항목 기준)
    total_margin = revenue - total_cost
    if revenue != Decimal("0") and (len(items) - missing_cost_count) > 0:
        total_margin_percent = round_decimal(total_margin / revenue * 100, 1)
    else:
        total_margin_percent = None

    # 원가 미입력 경고
    if missing_cost_count > 0:
        warnings.append(f"원가 미입력 항목 {missing_cost_count}건")

    # 유효기간 < 7일 경고 (R6 전조 — detect_risks.py에서도 확인)
    if valid_until:
        try:
            valid_date = date.fromisoformat(valid_until)
            days_left = (valid_date - date.today()).days
            if days_left < 7:
                warnings.append(f"유효기간 촉박: {days_left}일 남음")
        except ValueError:
            warnings.append(f"validUntil 형식 오류: {valid_until}")

    return {
        "items": result_items,
        "subtotal": int(total_subtotal),
        "discount_amount": int(discount_amount),
        "vat": int(vat),
        "total": int(total),
        "revenue": int(revenue),
        "totalCost": int(total_cost),
        "totalMargin": int(total_margin),
        "totalMarginPercent": float(total_margin_percent) if total_margin_percent is not None else None,
        "vatType": vat_type,
        "validUntil": valid_until,
        "discount": discount_info,
        "warnings": warnings,
    }


if __name__ == "__main__":
    raw = sys.stdin.read()
    data = json.loads(raw)
    result = calc_margin(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
