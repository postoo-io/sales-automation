# profile.json 스키마 (v2)

`sales-setup/scripts/profile.py`가 관리하는 통합 영업 프로필. 한 파일에 회사·팀·브랜드·상품·자주 쓰는 멘트·기본 계약 조건·리드 적합도 키워드를 함께 담아 모든 영업 스킬이 동일한 출처를 참조합니다.

저장 위치: `<config-dir>/sales-automation/profile.json` (`profile.py --show-path`).
스키마 버전: **2** (v1 `business.json` 자동 마이그레이션 지원 — `profile.py --migrate`).

모든 필드는 선택입니다 — 채운 필드만 다른 스킬이 활용합니다.

---

## 최상위 구조

```json
{
  "schemaVersion": 2,
  "company": {...},
  "team": [...],
  "brand": {...},
  "products": [...],
  "phrases": {...},
  "defaults": {...},
  "keywords": {...}
}
```

7개 섹션. 빈 채로 두어도 동작하며, 영업 스킬이 정보가 없을 때는 generic하게 동작하거나 사용자에게 한 번 묻습니다.

---

## company — 법인 식별 정보

| 필드 | 타입 | 예시 | 사용 스킬 |
|---|---|---|---|
| `legalName` | string | "주식회사 똑똑한개발자" | quote-writing(견적서 공급자) |
| `displayName` | string | "똑똑한개발자" | email-send / call-prep |
| `registrationNumber` | string | "123-45-67890" | quote-writing 비고 |
| `ceoName` | string | "이지훈" | quote-writing 공급자 표기 |
| `address` | string | "서울 강남구 …" | quote-writing |
| `domain` | string | "toktokhan.dev" | email-send 서명·도메인 매칭 |
| `homepage` | string | "https://toktokhan.dev" | email-send / 견적서 헤더 |
| `phone` | string | "02-1234-5678" | quote-writing / call-prep |

---

## team — 영업 담당자 목록

배열. 각 멤버:

| 필드 | 타입 | 의미 |
|---|---|---|
| `id` | string | 내부 식별자 (예: "kim", "park") |
| `active` | boolean | **현재 발송 주체**. 정확히 한 명에게 true 권장 (없으면 첫 멤버 사용) |
| `name` | string | 이름 (예: "김매니저") |
| `role` | string | 직책 (예: "영업총괄", "PM", "AE") |
| `email` | string | 회사 이메일 |
| `phone` | string | 핸드폰 / 직통 |
| `signature` | string | 멀티라인 서명 블록. `\n`으로 줄바꿈. 예: `"김매니저 / 영업총괄\n똑똑한개발자\nkim@toktokhan.dev"` |

특수 매핑:
- `team[*].role`이 "PM"을 포함한 첫 멤버 → 메일 템플릿의 `{{team.pm}}` 변수에 자동 매핑

복수 영업 담당자가 한 워크스페이스를 공유할 때:

```json
"team": [
  {"id": "kim", "active": true,  "name": "김매니저", "role": "영업총괄", ...},
  {"id": "park", "active": false, "name": "박PM",    "role": "PM",     ...}
]
```

`active`를 다른 멤버로 옮기면 그 사람 명의로 메일이 나갑니다.

---

## brand — 사업 정체성

| 필드 | 타입 | 의미 | 사용 스킬 |
|---|---|---|---|
| `tagline` | string | 한 줄 자기소개 | email-send 첫 응답 |
| `tone` | enum | `formal_business` / `friendly` / `professional` | email-send 톤 결정 |
| `language` | string | `"ko"` / `"en"` | 다국어 분기 |
| `industry` | string | 우리 산업 | account-research / call-prep |
| `targetCustomers` | string[] | 핵심 타깃 | account-research 적합도 |
| `strengths` | string[] | 강점·셀링 포인트 3–5개 | call-prep / email-send |
| `differentiation` | string | "다른 곳과 무엇이 다른가" | call-prep / email-send |
| `values` | string[] | 핵심 가치 (선택) | brand voice 일관성 |

---

## products — 메인 상품/서비스

배열. 각 항목:

| 필드 | 타입 | 의미 |
|---|---|---|
| `id` | string | 내부 식별자 |
| `name` | string | 상품명 |
| `description` | string | 1-2줄 설명 |
| `target` | string | 적합 고객 (예: "에이전시 영업팀") |
| `defaultPrice` | number? | 기본 단가 (없으면 null) |
| `unitType` | string | 단위 (예: "M/M", "건", "월") |

quote-writing이 견적 항목 매칭 시 힌트로 사용. email-send 소개 단락에 노출.

---

## phrases — 자주 쓰는 멘트

카테고리별 문구 배열. 빈 배열도 허용. 사용 시 첫 항목을 우선 쓰거나 사용자가 선택.

| 카테고리 | 용도 | 예시 문구 |
|---|---|---|
| `greeting` | 메일 인사말 | "안녕하세요, {{client.companyName}} {{client.contactName}}님." |
| `intro` | 자기소개 | "{{company.displayName}}의 {{me.name}}입니다." |
| `ctaMeeting` | 미팅 제안 클로징 | "편하신 시간을 알려주시면 일정 조율 도와드리겠습니다." |
| `ctaQuote` | 견적 제안 클로징 | "검토 후 회신 부탁드립니다." |
| `ctaFollowup` | 팔로업 클로징 | "한 번 더 확인 부탁드립니다." |
| `thanks` | 감사 인사 | "감사합니다." |
| `decline` | 거절 / out-of-scope | "이번 건은 도움드리기 어려운 영역인 것 같습니다." |
| `discount` | 할인 안내 | "이번 분기 도입 고객에게 N% 할인 적용 가능합니다." |

이 멘트들은 메일 본문에 mustache 변수처럼 박을 수도 있고, 사용자가 작성한 초안을 다듬을 때 톤 기준으로 활용할 수도 있습니다.

---

## defaults — 기본 계약 조건

| 필드 | 타입 | 의미 |
|---|---|---|
| `vatType` | enum | `"E"` 부가세 별도 / `"I"` 포함 / `"N"` 없음 |
| `paymentTerms` | string | 결제 조건 (예: "선금 50% / 잔금 50%") |
| `quoteValidityDays` | integer | 견적 기본 유효기간(일) |

quote-writing이 값 미지정 시 자동 적용. 사용자가 명시하면 우선.

---

## keywords — 리드 적합도 보조

| 필드 | 타입 | 의미 |
|---|---|---|
| `goodFit` | string[] | 매칭 시 가산점 (account-research) |
| `outOfScope` | string[] | 매칭 시 감점 |

---

## 사용 예시 (최소)

본인 팀이 한 명이고 회사 정보만 채우려면 이 정도로 충분:

```json
{
  "schemaVersion": 2,
  "company": {
    "legalName": "주식회사 똑똑한개발자",
    "displayName": "똑똑한개발자",
    "domain": "toktokhan.dev",
    "homepage": "https://toktokhan.dev"
  },
  "team": [
    {
      "id": "kim",
      "active": true,
      "name": "김매니저",
      "role": "영업총괄",
      "email": "kim@toktokhan.dev",
      "phone": "010-1234-5678",
      "signature": "김매니저 / 영업총괄\n똑똑한개발자\nkim@toktokhan.dev\nhttps://toktokhan.dev"
    }
  ],
  "brand": {
    "tagline": "B2B 영업을 자동화합니다",
    "strengths": ["워크플로우 통합 관리", "API + AI 연동", "한국 시장 표준 지원"]
  }
}
```

위만 채워도 모든 메일 템플릿이 회사명·발신자명·서명을 일관되게 출력합니다.

---

## Python에서 사용

```python
import sys
sys.path.insert(0, "skills/sales-setup/scripts")
from profile import load_profile, get_active_member

p = load_profile()              # v1 자동 마이그레이션 포함
me = get_active_member(p)       # 활성 영업 담당자

print(me["name"], me["email"])  # 김매니저 kim@toktokhan.dev
print(p["company"]["displayName"])
print("\n".join(p["brand"]["strengths"]))
```

---

## v1 → v2 마이그레이션

기존 `business.json` (`schemaVersion: 1`) 사용자는 `profile.py --migrate` 한 번으로 자동 변환:

- `voice.signatureLines[]` → `team[0].signature` (줄바꿈으로 join)
- `voice.tone`, `voice.language` → `brand.tone`, `brand.language`
- `business.industry/targetCustomers/strengths/differentiation` → `brand.*`
- `business.coreProducts[]` → `products[]`
- `defaults`, `keywords`, `company` → 동명 섹션 그대로

마이그레이션 후 `--show`로 검증 권장. 구 `business.json` 파일은 자동 삭제되지 않습니다 (안전을 위해 그대로 보존 — 사용자가 직접 삭제).
