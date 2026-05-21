# Business Profile 스키마

`pluuug-setup/scripts/business_info.py`가 관리하는 비즈니스 프로필의 데이터 구조. 모든 필드는 선택입니다 — 비어 있어도 동작하며, 채워진 필드만 다른 스킬이 활용합니다.

저장 위치: `<config-dir>/pluuug/business.json` (`business_info.py --show-path`로 확인).

스키마 버전: **1**.

---

## 최상위 구조

```json
{
  "schemaVersion": 1,
  "company": {...},
  "business": {...},
  "voice": {...},
  "defaults": {...},
  "keywords": {...}
}
```

5개 섹션은 모두 선택적이며, 각 섹션 내의 모든 필드도 선택적입니다. 예를 들어 `voice.signatureLines`만 채워두면 메일 발송 시 서명에만 반영되고 다른 곳은 영향이 없습니다.

---

## company — 법인 식별 정보

| 필드 | 타입 | 의미 | 사용 스킬 |
|---|---|---|---|
| `legalName` | string | 정식 법인명 — 예: "주식회사 똑똑한개발자" | quote-writing(견적서 공급자명), email-send(공식 메일 서명) |
| `displayName` | string | 약칭 / 브랜드명 — 예: "똑똑한개발자" | email-send(친근한 톤 서명), call-prep(소개 한 줄) |
| `registrationNumber` | string | 사업자등록번호 (`xxx-xx-xxxxx`) | quote-writing(견적서 비고), 세금계산서 발행 안내 |
| `ceoName` | string | 대표자 성명 | quote-writing(공급자 표기) |
| `address` | string | 본사 주소 | quote-writing(견적서 공급자 주소) |
| `domain` | string | 회사 도메인 — 예: "toktokhan.dev" (https:// 없이) | email-send(서명·발신 도메인 일관성), account-research(자사 도메인과 의뢰 도메인 매칭) |
| `homepage` | string | 홈페이지 URL | email-send(첨부 링크), 견적서 헤더 |

---

## business — 사업 성격과 강점

| 필드 | 타입 | 의미 | 사용 스킬 |
|---|---|---|---|
| `industry` | string | 우리 산업 / 카테고리 — 예: "B2B SaaS - CRM/영업 자동화" | account-research(우리 적합 영역 명시), call-prep(콜 도입부 자기소개) |
| `targetCustomers` | string[] | 핵심 타깃 — 예: `["에이전시","컨설팅펌","스타트업 영업팀"]` | account-research(리드 적합도 평가 시 가중치) |
| `coreProducts` | object[] | 핵심 제품/서비스 목록 — 각 원소: `{"name":"...","description":"..."}` | email-send(소개 단락 자동 채움), quote-writing(견적 항목 매칭 힌트) |
| `strengths` | string[] | 강점·셀링 포인트 3–5개 | call-prep(콜 포인트 가이드), email-send(소개 단락) |
| `differentiation` | string | 한 줄 차별화 — "다른 곳과 무엇이 다른가" | email-send(첫 응답 메일), account-research(why we are a fit) |

---

## voice — 톤·언어·서명

| 필드 | 타입 | 의미 | 사용 스킬 |
|---|---|---|---|
| `language` | string | 기본 언어 — `"ko"` 또는 `"en"` | email-send, call-summary |
| `tone` | string | 메일 톤 — `"formal_business"` / `"friendly"` / `"professional"` | email-send(메일 다듬기 기준) |
| `signatureLines` | string[] | 이메일 서명 줄들. 예: `["김매니저 / 영업총괄","Pluuug | https://pluuug.com","02-1234-5678"]` | email-send(모든 발송 메일 말미) |

---

## defaults — 기본 계약 조건

| 필드 | 타입 | 의미 | 사용 스킬 |
|---|---|---|---|
| `vatType` | enum | `"E"` 부가세 별도 / `"I"` 포함 / `"N"` 없음 | quote-writing(기본값 — 사용자가 명시하지 않으면 이 값) |
| `paymentTerms` | string | 결제 조건 — 예: "선금 50% / 잔금 50%" | quote-writing(견적서 비고), email-send(견적 송부 메일) |
| `quoteValidityDays` | integer | 견적 기본 유효기간(일) | quote-writing(`validUntil = 발행일 + 일수`) |

---

## keywords — 적합성 판단 보조

| 필드 | 타입 | 의미 | 사용 스킬 |
|---|---|---|---|
| `goodFit` | string[] | 우리 강점에 부합하는 키워드. 예: `["CRM","영업관리","에이전시","견적관리"]` | account-research(매칭 신호 +5점), call-prep(매칭 키워드 강조) |
| `outOfScope` | string[] | 명백히 우리 영역이 아닌 키워드. 예: `["하드웨어","오프라인 리테일"]` | account-research(매칭 시 -10점), email-send(거절 메일 트리거) |

---

## 예시 — 최소 입력

```json
{
  "schemaVersion": 1,
  "company": {
    "displayName": "Pluuug",
    "domain": "pluuug.com",
    "homepage": "https://pluuug.com"
  },
  "business": {
    "industry": "B2B SaaS - 영업자동화",
    "strengths": [
      "의뢰 인입부터 정산까지 워크플로우 통합 관리",
      "Open API + Claude Code 스킬 연동",
      "한국 시장 표준(세금계산서·부가세) 지원"
    ]
  },
  "voice": {
    "signatureLines": ["Pluuug | https://pluuug.com"]
  }
}
```

이만큼만 채워도 메일 서명·콜 자기소개·리드 평가가 모두 일관됩니다.

---

## 예시 — 풀 입력

```json
{
  "schemaVersion": 1,
  "company": {
    "legalName": "주식회사 ...",
    "displayName": "...",
    "registrationNumber": "xxx-xx-xxxxx",
    "ceoName": "...",
    "address": "서울 ...",
    "domain": "...",
    "homepage": "https://..."
  },
  "business": {
    "industry": "...",
    "targetCustomers": ["...", "..."],
    "coreProducts": [
      {"name": "...", "description": "..."}
    ],
    "strengths": ["...", "..."],
    "differentiation": "..."
  },
  "voice": {
    "language": "ko",
    "tone": "formal_business",
    "signatureLines": ["...", "..."]
  },
  "defaults": {
    "vatType": "E",
    "paymentTerms": "선금 50% / 잔금 50%",
    "quoteValidityDays": 14
  },
  "keywords": {
    "goodFit": ["...", "..."],
    "outOfScope": ["...", "..."]
  }
}
```

---

## 다른 스킬에서 사용하는 방법

Python:
```python
import sys
sys.path.insert(0, "skills/pluuug-setup/scripts")
from business_info import load_business_info

profile = load_business_info()  # 비어 있으면 {} 반환
signature = "\n".join(profile.get("voice", {}).get("signatureLines", []))
```

쉘:
```bash
skills/pluuug-setup/scripts/business_info.py --show | jq -r '.voice.signatureLines | join("\n")'
```

스킬이 비즈니스 정보를 활용할 때는 **있으면 쓰고, 없으면 무시**가 원칙입니다. 사용자가 비즈니스 프로필을 설치하지 않아도 모든 스킬은 동작해야 하며, 다만 자기소개·서명·기본값이 generic하게 나옵니다.
