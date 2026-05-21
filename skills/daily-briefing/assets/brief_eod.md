# 하루 마무리 — {{date_korean}}

## 오늘 완료

- Todo 완료: (모델이 todo_dday 완료 건수로 채움)건
- 정산 입금 확인: (모델이 settlement_settled 오늘 건수/금액으로 채움)건 / (금액)원

## 오늘 추가

- 신규 의뢰: {{new_inquiries_today_count}}건 (모델이 회사명 목록으로 채움)

## 내일 주의

- 미완료 D-day Todo: {{todos_dday_table}}
- 당월 정산 예정: {{settlement_due_total}}원
- 정산 지연: {{settlement_delayed_total}}

## 미결 루프

{{recommended_actions}}

---

**#1 우선순위 (점수 {{priority_score}}점):** {{priority_reason}}

*내일 시작할 때 `daily-briefing` 스킬로 풀 브리핑을 확인하세요.*
