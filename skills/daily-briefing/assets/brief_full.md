# Daily Briefing — {{date_korean}}

---

## #1 우선순위

**{{priority_reason}}**
점수: {{priority_score}}점 / 분류: {{priority_category}}

---

## 숫자 요약

| 신규 의뢰(오늘) | 어제 의뢰 | D-day Todo | 당월 수주 | 당월 정산 완료 | 당월 정산 예정 | 정산 지연 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| {{new_inquiries_today_count}}건 | {{new_inquiries_yesterday_count}}건 | (D-day 표 참조) | {{contracts_month_total}}원 | {{settlement_settled_total}}원 | {{settlement_due_total}}원 | {{settlement_delayed_total}} |

> 금액은 천 단위 콤마, 정수 표기. 예) 12,500,000원

---

## 신규 의뢰

### 오늘 의뢰 ({{new_inquiries_today_count}}건)

| 회사 | 요약 | 단계 | 견적 금액 |
|------|------|------|----------|
| (모델이 inquiry_today 데이터로 채움) | — | — | — |

> 의뢰가 없으면 "없음"으로 표기.

### 어제 의뢰 ({{new_inquiries_yesterday_count}}건) — 미처리 주의

| 회사 | 요약 | 단계 | 견적 금액 |
|------|------|------|----------|
| (모델이 inquiry_yesterday 데이터로 채움) | — | — | — |

---

## D-day Todo

{{todos_dday_table}}

> 지연: `due_date < 오늘`, D-day: `due_date = 오늘`
> Todo가 없으면 "오늘 마감 Todo 없음".

---

## 당월 매출 스냅샷

| 항목 | 금액 | 건수 |
|------|------|------|
| 수주 합계 | {{contracts_month_total}}원 | {{contracts_month_count}}건 |
| 정산 완료 | {{settlement_settled_total}}원 | — |
| 정산 예정 | {{settlement_due_total}}원 | — |
| **정산 지연** | **{{settlement_delayed_total}}** | — |

---

## 세금계산서 발행 예정 / 미발행 경고

{{tax_invoice_warnings_table}}

> `isTaxInvoiceIssued=false` AND `taxInvoiceIssueDueDate` ≤ 오늘+3일 항목만 표시.
> 해당 없으면 "발행 임박 세금계산서 없음".

---

## 추천 액션 3가지

{{recommended_actions}}

---

*콜 준비는 `call-prep`, 콜 후 정리는 `call-summary`*
