---
name: daily-briefing
description: >
  하루를 시작하거나 마무리할 때 Pluuug CRM · Gmail · Google Calendar 데이터를 자동으로 수집해
  당일 우선순위·Todo·수주·정산 현황을 한눈에 보여 드립니다.
  "오늘 브리핑", "모닝 브리프", "오늘 뭐해야 해", "데일리", "데일리 브리핑" — 풀 브리핑.
  "퀵 브리프", "tldr", "빠른 요약" — 핵심 3줄.
  "EOD", "하루 마무리", "오늘 마감" — 오늘 변동 요약.
---

# 데일리 브리핑 (Daily Briefing)

> ⚠️ **사전 조건**: 이 스킬은 `sales-setup`이 완료돼 있어야 합니다 (최소 레벨 **L0**). 미달 시 0단계 점검에서 차단합니다.

Pluuug CRM · Gmail · Google Calendar 데이터를 **병렬로** 수집해 하루 시작 또는 마감에 필요한
영업 현황을 **한국어 마크다운**으로 정리합니다. 읽기 전용 — 어떤 데이터도 생성·수정하지 않습니다.

---

## 1. 입력

보통 별도 입력 없이 실행합니다. 오늘 날짜를 자동으로 계산하여 기간 필터를 구성합니다.

| 변수 | 계산 방법 | 예시 (2026-05-21 기준) |
|------|-----------|----------------------|
| `오늘` | 실행 당일 | `2026-05-21` |
| `어제` | 오늘 -1일 | `2026-05-20` |
| `월초` | 해당 월 1일 | `2026-05-01` |
| `월말` | 해당 월 마지막 날 | `2026-05-31` |
| `오늘+3` | 오늘 +3일 | `2026-05-24` |
| `오늘+7` | 오늘 +7일 | `2026-05-28` |

---

## 2. 절차

### 2-0. 사전 점검 (setup gate)

스킬 진입 전 setup이 충분한지 확인합니다. 미달이면 진행하지 말고 사용자에게 `sales-setup` 실행을 안내합니다.

```bash
skills/sales-setup/scripts/check_setup.py --level L0 --quiet
# exit 0 = pass, exit 1 = 차단 (사용자에게 sales-setup 실행 안내)
```

이 스킬의 요구 레벨: **L0** (Pluuug 자격증명 존재 여부). 실패 시 사용자에게 보여줄 안내:

> "이 스킬을 실행하려면 sales-setup이 필요합니다. 부족한 항목이 있어 진행할 수 없습니다.
> 자세한 부족 항목은 `skills/sales-setup/scripts/check_setup.py --level L0` 출력을 참고하세요."

### 2-1. 병렬 데이터 수집

> 데이터 수집은 `scripts/fetch_briefing.sh`로 한 번에 실행할 수 있습니다 (병렬 호출 + JSON manifest).

아래 모든 호출을 **동시에** 실행합니다. 각 그룹은 독립적이므로 순서 의존 없음.

#### 그룹 A — 의뢰 (Inquiry)

```bash
# A1. 오늘 신규 의뢰
scripts/pluuug.py GET /v1/inquiry \
  --query inquiry_date_start={오늘} inquiry_date_end={오늘} page_size=100

# A2. 어제 신규 의뢰 (전일 미처리 포함)
scripts/pluuug.py GET /v1/inquiry \
  --query inquiry_date_start={어제} inquiry_date_end={어제} page_size=100

# A3. 의뢰 단계 메타 (단계별 명칭 + 활성 카운트)
scripts/pluuug.py GET /v1/inquiry/status
```

#### 그룹 B — Todo

```bash
# B1. 오늘까지 마감 (D-day ≤ 0) — 지연 포함
scripts/pluuug.py GET /v1/todo \
  --query is_complete=false due_date_end={오늘} page_size=100

# B2. 이번 주 예정 Todo
scripts/pluuug.py GET /v1/todo \
  --query is_complete=false due_date_start={오늘} due_date_end={오늘+7} page_size=100
```

#### 그룹 C — 계약 (Contract)

```bash
# C1. 당월 계약 전체 (수주 금액 집계용)
scripts/pluuug.py GET /v1/contract \
  --query created_start={월초} created_end={월말} page_size=100
```

#### 그룹 D — 정산 (Settlement)

```bash
# D1. 당월 정산 완료 (status=S, settled_date 기준)
scripts/pluuug.py GET /v1/settlement \
  --query settled_date_start={월초} settled_date_end={월말} page_size=100

# D2. 당월 정산 예정 (due_date 기준, 미완료 전체)
scripts/pluuug.py GET /v1/settlement \
  --query due_date_start={월초} due_date_end={월말} page_size=100

# D3. 정산 형태 메타
scripts/pluuug.py GET /v1/settlement/type
```

#### 그룹 E — 프로젝트 (Project)

```bash
# E1. 진행 중 프로젝트
scripts/pluuug.py GET /v1/project --query status=I page_size=100
```

#### 그룹 F — Gmail (mcp__gmail)

```
- 미답장 추적: 72시간 이상 경과한 내 발신 메일 중 답장 없는 스레드
  검색: in:sent older_than:3d -has:reply category:primary
- 오늘 수신 메일 중 의뢰 도메인 관련
  검색: in:inbox newer_than:1d
```

#### 그룹 G — Google Calendar (mcp__google_calendar)

```
- 오늘 일정 조회 (time_min={오늘}T00:00:00, time_max={오늘}T23:59:59)
- 필터: 외부 참석자(사내 도메인 외) 포함 이벤트 우선
```

### 2-2. 파생 계산

수집 완료 후 아래 항목을 계산합니다.

| 계산 항목 | 방법 |
|-----------|------|
| 당월 수주 합계 | C1의 `amount` 합산 (contract.status ≠ T) |
| 타입별 분포 | C1을 `type` (I/S/G) 기준으로 그룹화 → 건수·금액 |
| 평균 단가 | 당월 수주 합계 ÷ 건수 |
| 정산 완료 합계 | D1 응답의 `status=S`만 **클라이언트 사이드 필터** → `amount + additionalAmount` 합산 |
| 정산 예정 합계 | D2 응답의 `status=C`만 **클라이언트 사이드 필터** → `amount + additionalAmount` 합산 |
| 정산 지연 목록 | D1·D2 응답 전체에서 `status=D` **클라이언트 사이드 추출** |

> ⚠️ `/v1/settlement`는 `status` 쿼리 파라미터를 지원하지 않습니다. 위 필터링은 모두 응답을 받은 뒤 응답 본문의 `status` 필드로 클라이언트에서 분류합니다.
| 세금계산서 미발행 경고 | D1·D2에서 `isTaxInvoiceIssued=false` AND `taxInvoiceIssueDueDate` ≤ 오늘+3 |
| D-day Todo | B1 결과 중 `due_date < 오늘` → 지연, `due_date = 오늘` → D-day 당일 |
| 오늘 미팅 | 캘린더 이벤트 + B1·B2 중 `type=M` 또는 `type=CA` |

### 2-3. 우선순위 선정

> 점수 계산은 `scripts/calc_priority.py < manifest.json`로 자동화할 수 있습니다.

아래 **점수표**를 적용해 가장 높은 점수의 항목을 `#1 우선순위`로 선정합니다.
동점이면 금액이 큰 항목을 우선합니다.

| 조건 | 점수 |
|------|------|
| 정산 `status=D` (지연) 건 존재 | **100점** |
| 세금계산서 발행 기한 오늘~+1일 이내 | **90점** |
| 오늘 외부 미팅 존재 | **80점** |
| D-day Todo (오늘 마감) 3건 이상 | **70점** |
| D-day Todo (오늘 마감) 1건 이상 | **60점** |
| 어제 신규 의뢰 중 미처리(단계 변동 없음) | **55점** |
| 오늘 신규 의뢰 존재 | **50점** |
| 이번 주 Todo 5건 이상 | **40점** |
| 미답장 메일 72시간 이상 2건 이상 | **35점** |
| 진행 중 프로젝트 10건 이상 | **20점** |

> 가장 높은 점수의 **하나**만 #1 우선순위로 선정합니다.
> 모든 점수가 0이면 "특별한 긴급 사항 없음 — 이번 주 Todo 점검을 권장합니다." 표시.

---

## 3. 출력 템플릿 (풀 브리핑)

> 출력 템플릿은 `assets/brief_full.md` / `brief_quick.md` / `brief_eod.md`를 사용합니다. 변수 치환은 모델이 직접 수행 — `{{변수}}` 자리를 실제 값으로 채워서 사용자에게 표시.

```markdown
# Daily Briefing — {YYYY-MM-DD} ({요일})

---

## #1 우선순위

**{우선순위 제목}**
{이유 한 줄 — 위 점수표에서 선정된 근거}

---

## 숫자 요약

| 신규 의뢰(오늘) | 어제 의뢰 | 활성 Todo | 지연 Todo | 당월 수주 | 당월 정산 완료 | 당월 정산 예정 | 정산 지연 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| {N}건 | {N}건 | {N}건 | {N}건 | {금액}원 | {금액}원 | {금액}원 | {N}건 |

> 금액은 천 단위 콤마, 정수 표기. 예) 12,500,000원

---

## 신규 의뢰

### 오늘 ({YYYY-MM-DD})

| 회사 | 요약 | 단계 | 견적 금액 |
|------|------|------|----------|
| {companyName} | {title 30자 이내} | {status} | {estimate 없으면 "미정"} |

### 어제 ({YYYY-MM-DD}) — 미처리 주의

| 회사 | 요약 | 단계 | 견적 금액 |
|------|------|------|----------|
| {companyName} | {title 30자 이내} | {status} | {estimate 없으면 "미정"} |

> 의뢰가 없으면 "없음"으로 표기.

---

## 오늘 콜 · 미팅

| 시간 | 구분 | 회사 / 제목 | 비고 |
|------|------|------------|------|
| {HH:mm} | {캘린더 / Todo-M / Todo-CA} | {회사명 또는 이벤트 제목} | {Todo ID 또는 캘린더 링크} |

> 미팅이 없으면 "오늘 예정된 외부 미팅 없음".
> 미팅이 있으면 각 항목 아래: 콜 준비는 `call-prep {회사명}` 실행 권장.

---

## D-day Todo

| 마감일 | 상태 | 제목 | 관련 의뢰 |
|--------|------|------|----------|
| {YYYY-MM-DD} | 지연 / D-day | {title} | {inquiry.id 있으면 표시, 없으면 "-"} |

> 지연: `due_date < 오늘`, D-day: `due_date = 오늘`
> Todo가 없으면 "오늘 마감 Todo 없음".

---

## 이번 주 Todo

이번 주 예정 Todo: **{N}건**

| 마감일 | 제목 | 관련 의뢰 |
|--------|------|----------|
| {YYYY-MM-DD} | {title} | {inquiry.id 또는 "-"} |

> 5건 초과 시 상위 5건만 표시 후 "외 {N}건 더 있음" 안내.

---

## 당월 매출 스냅샷 ({YYYY-MM})

| 항목 | 금액 | 건수 |
|------|------|------|
| 수주 합계 | {금액}원 | {N}건 |
| ├ 회차 정산형(I) | {금액}원 | {N}건 |
| ├ 정기 결제형(S) | {금액}원 | {N}건 |
| └ 단건 정산(G) | {금액}원 | {N}건 |
| 평균 단가 | {금액}원 | — |
| 정산 완료 | {금액}원 | {N}건 |
| 정산 예정 | {금액}원 | {N}건 |
| **정산 지연** | **{금액}원** | **{N}건** |

> contract.vatType / settlement.vat 기준으로 "부가세 포함" 또는 "부가세 별도" 병기.
> 정산 status 한국어 대응: C→예정, D→지연, S→완료, P→중단.

---

## 세금계산서 발행 예정 / 미발행 경고

| 발행 기한 | 거래처 | 정산 금액 | 긴급도 |
|----------|--------|----------|--------|
| {YYYY-MM-DD} | {companyName 또는 "-"} | {금액}원 | D-{N} / 오늘 / 지연 |

> `isTaxInvoiceIssued=false` AND `taxInvoiceIssueDueDate` ≤ 오늘+3일 항목만 표시.
> 해당 없으면 "발행 임박 세금계산서 없음".

---

## 이메일 우선순위

### 미답장 (72시간+)

| 수신자 | 제목 | 발송일 | 경과 |
|--------|------|--------|------|
| {to} | {subject} | {YYYY-MM-DD} | {N}일 |

### 오늘 수신 (의뢰 관련)

| 발신자 | 제목 | 수신 시각 |
|--------|------|----------|
| {from} | {subject} | {HH:mm} |

> 이메일이 없으면 각 소항목에 "없음" 표기.

---

## 진행 중 프로젝트

진행 중 프로젝트: **{N}건**

> 10건 이하: 회사명 목록 표시.
> 10건 초과: 건수만 표시.

---

## 추천 액션 3가지

1. **{액션 제목}** — {위 데이터에서 도출한 구체적 이유}
2. **{액션 제목}** — {이유}
3. **{액션 제목}** — {이유}

---

*콜 준비는 `call-prep`, 콜 후 정리는 `call-summary`*
```

---

## 4. 빠른 모드 / EOD 모드

### 퀵 브리프 (빠른 모드)

**트리거**: "퀵 브리프", "tldr", "빠른 요약", "한 줄 요약"

수집 범위를 최소화합니다.

- 호출: B1(D-day Todo), D2(당월 정산 예정), D1(정산 지연 확인), A1(오늘 의뢰)
- 출력:

```markdown
# 퀵 브리프 — {YYYY-MM-DD}

**#1:** {우선순위 한 줄}

**숫자:** 신규 의뢰 {N}건 · D-day Todo {N}건 · 당월 수주 {금액}원 · 정산 지연 {N}건

**Do Now:** {가장 급한 한 가지 액션}
```

### EOD 모드 (하루 마무리)

**트리거**: "EOD", "하루 마무리", "오늘 마감", "데일리 마감"

오늘 하루 동안의 **변동 사항**만 요약합니다.

수집: A1(오늘 의뢰 현황), B1(오늘 마감 Todo — 완료 여부), D1(오늘 정산 완료 건)

```markdown
# 하루 마무리 — {YYYY-MM-DD}

## 오늘 완료

- Todo 완료: {N}건
- 정산 입금 확인: {N}건 / {금액}원

## 오늘 추가

- 신규 의뢰: {N}건 ({회사명 목록})

## 내일 주의

- 미완료 D-day Todo: {N}건
- 내일 마감 Todo: {N}건
- 내일 외부 미팅: {N}건

## 미결 루프

- {오늘 처리 못한 항목}
```

---

## 5. 가드레일

| 규칙 | 상세 |
|------|------|
| **읽기 전용** | GET 호출만 사용. POST·PATCH·DELETE 절대 금지 |
| **금액 표기** | 정수 + `원`, 천 단위 콤마. 예) 5,200,000원. 소수점 반올림 |
| **부가세 표기** | `contract.vatType` / `settlement.vat` 원본값 그대로 "부가세 포함" / "부가세 별도"로 병기 |
| **정산 상태 한국어** | C→예정, D→지연, S→완료, P→중단. 원본 코드 사용자에게 노출 금지 |
| **빈 데이터** | 조회 결과가 0건이면 "없음" 또는 0으로 표기. 임의 숫자 생성 금지 |
| **페이지네이션** | `page_size=100`까지. 결과가 100건 이상이면 "100건 이상 — 전체 조회가 필요하면 알려 주세요" 안내 |
| **레이트 리밋** | 분당 1,000회. HTTP 429 수신 시 즉시 멈추고 사용자 보고. 자동 루프 대기 금지 |
| **시크릿 출력 금지** | PLUUUG_API_KEY, PLUUUG_SECRET_KEY 절대 노출 금지 |
| **Gmail 읽기 전용** | 이메일 발송 금지. 발송 필요 시 email-send 스킬로 인계 |
| **캘린더 읽기 전용** | 이벤트 수정·생성 금지 |

---

## 6. 다른 스킬과의 연계

| 상황 | 연계 스킬 |
|------|----------|
| 오늘 미팅 콜 준비가 필요할 때 | `call-prep {회사명}` |
| 통화 후 내용 정리 | `call-summary` |
| 신규 의뢰 심층 분석 | `account-research` |
| 미답장 이메일 발송 | `email-send` |
| 의뢰/계약/정산 상세 조회 | `pluuug-api` |

---

## 7. 엔드포인트 참조 요약

| 엔드포인트 | 목적 | 주요 파라미터 |
|-----------|------|--------------|
| `GET /v1/inquiry` | 신규·전체 의뢰 목록 | `inquiry_date_start`, `inquiry_date_end`, `page_size` |
| `GET /v1/inquiry/status` | 의뢰 단계 메타 | — |
| `GET /v1/todo` | 할 일 목록 | `is_complete`, `due_date_end`, `due_date_start` |
| `GET /v1/contract` | 계약 목록 | `created_start`, `created_end` |
| `GET /v1/settlement` | 정산 목록 | `settled_date_start`, `settled_date_end`, `due_date_start`, `due_date_end` |
| `GET /v1/settlement/type` | 정산 형태 메타 | — |
| `GET /v1/project` | 프로젝트 목록 | `status` (I=진행 중) |
