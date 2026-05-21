# 견적서 (고객 발송용)

> 이 파일은 고객 발송용 템플릿입니다. 마진율·원가·손익 정보는 절대 포함하지 않습니다.

---

## 견적서 — {{company_name}} / {{contact}}

| 항목 | 내용 |
|---|---|
| 발행일 | {{issued_date}} |
| 유효기간 | {{valid_until}} |
| 공급자 | (자사명) |
| 수신자 | {{company_name}} {{contact}} |
| 부가세 | {{vat_label}} |

---

{{items_table}}

---

| 구분 | 금액 |
|---|---:|
| 소계 | {{subtotal_formatted}} |
| {{discount_label_amount}} | |
| 부가세 | {{vat_formatted}} |
| **합계** | **{{total_formatted}}** |

---

**비고**

{{notes}}

---

*본 견적서의 유효기간은 {{valid_until}}까지이며, 이후에는 단가가 변경될 수 있습니다.*
