---
name: call-prep
description: >
  전화하기 전에 의뢰·고객·채널 정보를 한 번에 모아 2분 안에 읽히는 콜 브리프를 만들어 드립니다.
  "전화 전 요약", "콜 준비", "[회사명] 콜 준비해줘", "이 의뢰 전화 들어간다", "[프로젝트명] 콜 브리프",
  "[의뢰ID] 전화 전에 정리해줘", "통화 전 요약 부탁해" 등으로 실행합니다.
---

# 콜 브리프 (Call Prep)

전화를 걸기 직전, Pluuug 의뢰 · Slack · Gmail · Google Calendar 데이터를 병렬로 끌어와 **2분 안에 읽을 수 있는** 상황 요약을 만듭니다.

---

## 입력

세 가지 중 하나를 받으면 시작합니다. 아무것도 없으면 바로 묻습니다.

| 우선순위 | 입력 | 예시 |
|------|------|------|
| 1 | Pluuug 의뢰 ID | `의뢰 1234 콜 준비해줘` |
| 2 | Pluuug 프로젝트 ID | `프로젝트 78 콜 브리프` |
| 3 | 회사명 | `(주)에이스테크 전화 들어간다` |

셋 중 하나도 없으면: "콜 브리프를 만들려면 **의뢰 ID, 프로젝트 ID, 회사명** 중 하나가 필요합니다. 알려 주시겠어요?"

---

## 절차

### 1단계 — ID 확보

| 경우 | 처리 |
|------|------|
| 의뢰 ID 있음 | 그대로 사용 |
| 프로젝트 ID만 있음 | `GET /v1/project/{id}` → `contract.id` 추출 → `GET /v1/contract/{contract_id}` → `inquiry.id` 사용. 계약/의뢰가 연결되어 있지 않으면 사용자에게 의뢰 ID 직접 요청 |
| 회사명만 있음 | `GET /v1/client?search={회사명}` → 회사 후보 확인 → `GET /v1/inquiry?search={회사명}&is_hidden=false&page_size=10` → 응답 결과에서 `client.id` 일치하는 의뢰만 클라이언트 사이드 필터 → 가장 최신 의뢰 ID 사용. 복수 의뢰가 있으면 사용자에게 선택 요청. (※ `/v1/inquiry`는 `client_id` 쿼리 파라미터를 지원하지 않으므로 `search` 후 필터링) |

### 2단계 — 병렬 데이터 수집

아래 모든 호출을 **동시에** 실행합니다. Pluuug 9개 호출을 한 번에 실행하려면 `scripts/collect_context.sh <inquiry_id>`를 사용 — manifest JSON을 받아 후속 처리.

#### Pluuug (scripts/pluuug.py)

```bash
# 의뢰 본문 · 상태 · 담당자 · 계약 · 파일
scripts/pluuug.py GET /v1/inquiry/{id}

# 최근 메모 / 콜 기록 (20건)
scripts/pluuug.py GET /v1/inquiry/{id}/text_history --query page_size=20

# Pluuug에서 발송한 이메일 (10건)
scripts/pluuug.py GET /v1/inquiry/{id}/email_history --query page_size=10

# 고객 답장 (10건, is_unread 플래그 확인)
scripts/pluuug.py GET /v1/inquiry/{id}/email_reply_history --query page_size=10

# 단계 변동 이력 (10건)
scripts/pluuug.py GET /v1/inquiry/{id}/status_history --query page_size=10

# 미완료 할일
scripts/pluuug.py GET /v1/todo --query inquiry_id={id} is_complete=false

# 고객사 메타
scripts/pluuug.py GET /v1/client/{client_id}

# 연결된 계약 (있으면)
scripts/pluuug.py GET /v1/contract --query inquiry_id={id}
```

#### Slack (mcp__slack)

1. **채널 후보 찾기**: 회사명을 정규화 — 공백→`-`, 소문자 변환, `(주)` · `주식회사` · `Inc.` 제거 — 후 채널 검색
2. 회사명·프로젝트명 키워드로 추가 검색 (`mcp__slack__search_messages`)
3. 매칭 채널이 **1개**면 최근 메시지 50건 가져오기
4. 매칭 채널이 **복수**면 → 사용자에게 목록 제시 후 선택받기 (임의 선택 금지)
5. 채널이 **없으면** → "Slack에서 채널을 찾지 못했습니다. 워크스페이스에서 채널명을 직접 확인 후 알려 주세요." 표시

Slack 채널 매칭 룰·민감 키워드 카탈로그는 `references/slack_channel_matching.md` 참조.

#### Gmail (mcp__gmail)

```
검색 쿼리: (from:{고객 이메일 또는 도메인} OR to:{고객 이메일 또는 도메인}) newer_than:14d
추출: 최근 14일 스레드, 첨부 파일 여부, 미답장 스레드, 미해결 질문
```

- 이메일을 읽기만 합니다. 어떤 이메일도 발송하지 않습니다.

#### Google Calendar (mcp__google_calendar)

```
조건: 오늘 이후 7일 이내 이벤트 중 회사명 또는 담당자명이 포함된 항목
추출: 참석자, 미팅 링크, 안건 (이벤트가 있을 때만)
```

### 3단계 — 합성 및 출력

수집된 데이터를 아래 템플릿으로 압축합니다. **비어 있는 항목은 "정보 없음"으로 솔직히 표시하고 추측하지 않습니다.**

---

## 출력 템플릿

```markdown
# [회사명] / [의뢰명] 콜 브리프

> 현재 단계: **{status}** · 최근 액션: {최근 액션 한 줄} · 브리프 생성: {날짜}

---

## 회사 · 담당자

| 항목 | 내용 |
|------|------|
| 회사 | {companyName} |
| 담당자 | {담당자명} ({직책}) |
| 연락처 | {이메일} / {전화} |
| 계약 | {계약 존재 여부 / 금액} |

---

## 의뢰 핵심 요구사항

- {요구사항 1}
- {요구사항 2}
- {요구사항 3}

---

## 최근 7일 타임라인

| 일시 | 출처 | 내용 |
|------|------|------|
| {YYYY-MM-DD HH:mm} | [Pluuug 메모] | {내용 요약} |
| {YYYY-MM-DD HH:mm} | [이메일 발송] | {내용 요약} |
| {YYYY-MM-DD HH:mm} | [고객 답장] | {내용 요약} |
| {YYYY-MM-DD HH:mm} | [단계 변동] | {이전 단계} → {현재 단계} |
| {YYYY-MM-DD HH:mm} | [Slack] | {내용 요약} |
| {YYYY-MM-DD HH:mm} | [Gmail] | {내용 요약} |

> 최근 7일 내 변화 없음 → "최근 7일 활동 없음" 표시

---

## 미해결 항목

- [ ] {메일·메모·할일에서 추출한 약속/질문 1}
- [ ] {약속/질문 2}
- [ ] {약속/질문 3}

> 미완료 Pluuug Todo: {건수}건 포함

---

## 콜에서 확인할 포인트 5가지

1. {위 갭에서 도출한 확인 포인트}
2. {확인 포인트}
3. {확인 포인트}
4. {확인 포인트}
5. {확인 포인트}

---

## 지뢰 · 주의사항

> Slack에서 "민감", "주의", "조심", "클레임", "불만" 키워드가 감지된 경우에만 표시.
> 해당 없으면 이 섹션 생략.

- {Slack 내부 논의에서 잡힌 민감 내용 요약}

---

## 추천 다음 액션 (콜 후)

- [ ] {콜 후 생성할 Pluuug 메모 초안}
- [ ] {후속 이메일 초안 — email-send 스킬 연계}
- [ ] {추가 할일 제안}

---

### 데이터 출처 요약

| 소스 | 수집 여부 | 비고 |
|------|----------|------|
| Pluuug 의뢰 | ✅ | 의뢰 ID: {id} |
| Pluuug 메모 | ✅ / ❌ | {건수}건 |
| Pluuug 이메일 발신 | ✅ / ❌ | {건수}건 |
| Pluuug 이메일 수신 | ✅ / ❌ | {건수}건 |
| Pluuug 상태 이력 | ✅ / ❌ | {건수}건 |
| Pluuug 미완료 할일 | ✅ / ❌ | {건수}건 |
| Slack | ✅ / ❌ | 채널: {채널명 또는 "없음"} |
| Gmail | ✅ / ❌ | {건수}개 스레드 |
| Google Calendar | ✅ / ❌ | {이벤트 제목 또는 "없음"} |
```

---

## 자사 강점 가이드 (선택)

`pluuug-setup`으로 저장한 `business.json`이 있으면 콜 브리프의 "콜에서 확인할 포인트" 또는 "추천 다음 액션" 섹션에 **우리 강점·차별화**를 콜 포인트 후보로 노출합니다.

- `business.strengths` → 콜에서 강조할 셀링 포인트 후보 (의뢰 요구사항과 매칭되는 것 우선)
- `business.differentiation` → "왜 우리인가" 한 줄 (이의제기 대응용)
- `company.displayName` → 자기소개 헤더

비즈니스 프로필이 없으면 이 섹션은 생략됩니다. 조회: `skills/pluuug-setup/scripts/business_info.py --show`.

---

## 가드레일

| 규칙 | 상세 |
|------|------|
| Slack 채널 자동 가입 금지 | 채널이 없으면 사용자 안내만. 임의로 가입하거나 DM 검색 대체 금지 |
| Gmail 읽기 전용 | 이메일 발송 불가. 발송이 필요하면 **email-send 스킬**로 인계 |
| Pluuug 쓰기 자동 실행 금지 | 콜 브리프를 의뢰 히스토리에 자동 저장하지 않음. 브리프 생성 후 반드시 묻기: "콜 브리프를 Pluuug 의뢰 히스토리에 저장할까요? (저장 시 `POST /v1/inquiry/{id}/text_history`)" — 사용자 승인 후에만 실행 |
| 빈 데이터 추측 금지 | 소스가 비어 있으면 "정보 없음" 표시. 추측해서 채우지 않음 |
| 채널 복수 매칭 시 임의 선택 금지 | 사용자에게 목록 제시 후 선택받기 |
| 의뢰 복수 매칭 시 임의 선택 금지 | 사용자에게 의뢰 목록 제시 후 선택받기 |
| API 키 노출 금지 | PLUUUG_API_KEY, PLUUUG_SECRET_KEY 절대 출력 금지 |
| 레이트 리밋 | 429 응답 시 즉시 멈추고 사용자에게 보고. 자동 루프 대기 금지 |

---

## 변형 모드

### 1분 브리프 (빠른 모드)

**트리거**: "빠른 콜 준비", "1분 브리프", "간단하게만"

수집 범위를 줄여 핵심만 뽑습니다.

- Pluuug: `GET /v1/inquiry/{id}`, `text_history?page_size=5`, `email_reply_history?page_size=5`, `todo` 만 호출
- Slack · Gmail · Calendar: 생략
- 출력: 헤드라인 + 담당자 + 미해결 항목 + 콜 포인트 3개 (마크다운 20줄 이내)
- 1분 브리프는 `assets/brief_short.md` 템플릿을 사용 — `{{변수}}` 치환 후 사용자에게 표시.

### 심층 브리프 (딥 모드)

**트리거**: "심층 콜 준비", "딥 브리프", "다 긁어줘", "완전 분석"

수집 범위를 최대로 늘립니다.

- Pluuug: 모든 엔드포인트 + `page_size=50` (text_history, email_history, email_reply_history, status_history)
- `GET /v1/contract?inquiry_id={id}` 계약 세부 포함
- Slack: 최근 메시지 100건 + 채널 내 키워드 검색 (회사명, 프로젝트명, 담당자명)
- Gmail: 최근 30일 스레드
- Calendar: 지난 콜 이벤트까지 소급 (30일 이내)
- 출력: 기본 템플릿 전체 + 계약·정산 요약 섹션 추가
- 심층 브리프는 `assets/brief_deep.md` 템플릿을 사용 — `{{변수}}` 치환 후 사용자에게 표시.

---

## 다른 스킬과의 연계

| 스킬 | 연계 방법 |
|------|----------|
| **account-research** | 회사 정보가 부족할 때 먼저 실행 → 결과를 콜 브리프 입력으로 활용 |
| **call-summary** | 콜 종료 후 실행 → 통화 내용을 Pluuug 메모 + 후속 이메일로 정리 |
| **daily-briefing** | 오늘의 콜 목록 확인 → 각 의뢰에 대해 call-prep 실행 |
| **email-send** | 콜 브리프의 "추천 다음 액션" 중 이메일 항목 실행 |
| **pluuug-api** | 모든 Pluuug 데이터 수집의 기반. HMAC 서명은 반드시 scripts/pluuug.py 사용 |
