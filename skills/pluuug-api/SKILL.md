---
name: pluuug-api
description: 플러그(Pluuug) Open API를 호출해 의뢰(리드)·고객·견적·계약·정산·프로젝트·할 일·실무자 데이터를 조회/생성/수정/삭제합니다. 사용자가 "플러그에서 가져와", "의뢰 목록", "이 리드 상세", "고객 추가", "견적 항목 템플릿", "계약/정산 조회" 등 플러그 데이터에 접근하는 모든 요청을 할 때 사용합니다. 다른 영업 스킬(account-research, call-prep, call-summary, daily-briefing, email-send, quote-writing)이 플러그 데이터를 필요로 할 때도 이 스킬을 거쳐 호출합니다.
---

# Pluuug Open API

플러그(https://pluuug.com)의 Open API 호출을 담당합니다. **MCP가 아닌 HTTPS REST**로 직접 접근하며, X-API-Key + HMAC-SHA256 X-Signature 인증을 사용합니다.

영업 워크플로우의 마스터 데이터(의뢰·고객·견적·계약·정산)는 모두 플러그에 있습니다. account-research, call-prep, call-summary, daily-briefing, email-send, quote-writing 등 다른 스킬에서 플러그 데이터를 읽거나 쓸 일이 생기면 **이 스킬의 호출 패턴을 따른다**.

## 언제 사용하나

- "오늘 들어온 의뢰 가져와" / "이 리드 상세"
- "[회사명] 고객 정보 찾아줘 / 새 고객 등록"
- "견적 항목 템플릿 보여줘"
- "이 의뢰에 메모 남겨" (텍스트 히스토리)
- "이 의뢰 첨부 파일 받아줘"
- "지난주 계약·정산 현황"
- 다른 영업 스킬에서 "플러그에서 X 가져오자"가 필요할 때

## 호출 방법

### 사전 준비 (인증 키 확보)

`scripts/pluuug.py`는 아래 우선순위로 키를 자동으로 찾는다 — 일치하는 첫 번째에서 멈춤.

| 순위 | 소스 | 용도 |
|---|---|---|
| 1 | 환경 변수 `PLUUUG_API_KEY` / `PLUUUG_SECRET_KEY` | 임시 오버라이드, CI |
| 2 | 프로젝트 루트 `.env` | 로컬 개발 (gitignored) |
| 3 | OS 표준 설정 위치 — macOS `~/Library/Application Support/pluuug/credentials.json` · Linux `$XDG_CONFIG_HOME/pluuug/credentials.json` · Windows `%APPDATA%\pluuug\credentials.json` | 영구 저장 (cowork·운영) |
| 4 | `~/.pluuug/credentials.json` | 크로스플랫폼 fallback |

가장 추천하는 패턴은 **3번 OS 표준 위치**다. 한 번 설치하면 새 세션·새 셸·새 머신(같은 사용자 홈)에서 모두 자동 동작한다. 설치는 `pluuug-setup` 스킬로 진행:

```bash
# 인터랙티브 (입력 시 화면에 키 노출 안 됨)
skills/pluuug-setup/scripts/install_credentials.py
```

키가 없으면 사용자에게 발급 절차(비즈니스 설정 > 웹훅 & API > Open API 탭, **Agency 플랜 필요**)를 안내한다 — 임의로 키를 만들거나 추측하지 않는다.

### 헬퍼 스크립트 (권장)

본문을 HMAC-SHA256으로 서명하고 헤더에 실어 보내는 일은 매번 손으로 짜지 말고 번들된 스크립트를 사용한다.

```bash
# 조회
scripts/pluuug.py GET /v1/inquiry --query inquiry_date_start=2026-05-14 page_size=20
scripts/pluuug.py GET /v1/inquiry/1234

# 생성/수정 (JSON 본문)
scripts/pluuug.py POST /v1/inquiry/1234/text_history --json '{"content":"콜백 완료"}'
scripts/pluuug.py PATCH /v1/client/567 --json '{"inCharge":"박매니저"}'

# 파일 첨부 (presigned 업로드 후 path를 의뢰에 attach)
scripts/presigned_upload.sh ./quote.pdf
# → {"name":"quote.pdf","path":"uploads/xxxx.pdf"}
# 위 JSON을 fileSet 배열에 넣어 PATCH /v1/inquiry/{id} 호출
```

스크립트는 표준출력에 응답 JSON(pretty)을, 표준에러에 `HTTP <코드>`를 찍는다. HTTP 2xx면 종료코드 0, 그 외는 1.

### 직접 curl이 필요할 때

스크립트로 안 되는 케이스(예: 멀티파트, 응답 헤더가 필요한 디버깅)는 직접 호출한다. 본문은 **JSON 직렬화 시 공백 없이(`,`/`:` separator)** 만들고, 빈 본문은 **빈 문자열**을 서명한다.

```bash
BODY='{"name":"테스트"}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$PLUUUG_SECRET_KEY" -hex | awk '{print $2}')
curl -sS -X POST https://openapi.pluuug.com/v1/client \
  -H "X-API-Key: $PLUUUG_API_KEY" -H "X-Signature: $SIG" \
  -H "Content-Type: application/json" -d "$BODY"
```

`$BODY` 안의 따옴표·이스케이프가 서명한 바이트와 다르면 401이 떨어진다. 본문이 길거나 한글이 섞여 있으면 헬퍼 스크립트를 쓰는 편이 안전하다.

## 공통 규칙

- **Base URL**: `https://openapi.pluuug.com`
- **인증 헤더**: `X-API-Key`, `X-Signature` (HMAC-SHA256 of body, hex)
  - 본문이 없으면 빈 문자열을 서명한다.
  - JSON 본문은 직렬화 직후 그 바이트를 그대로 서명한다. 직렬화/서명 후 본문을 다시 가공하면 안 된다.
- **Rate limit**: 분당 1,000회. 초과 시 HTTP 429 + `{"code":429,"message":"..."}`. 사용자에게 보고하고 잠시 후 재시도하거나 일괄 호출을 줄인다.
- **Pagination**: 거의 모든 list 응답이 `{next, previous, results}` 구조. `cursor` query 파라미터로 다음 페이지를 받는다. `page_size` 기본값은 서버 결정.
- **필드 명명**: 응답은 `camelCase` (`uniqueId`, `companyName`, `inquiryDate`). 요청 본문도 동일하게 `camelCase`로 보낸다.
- **날짜 필터**: `created_start` / `created_end` / `inquiry_date_start` / `inquiry_date_end` 등 `YYYY-MM-DD`.
- **숨김 항목**: 대부분의 list에 `is_hidden` 필터가 있다. 기본은 전체 — 활성 항목만 보고 싶으면 `is_hidden=false`.

## list 엔드포인트 쿼리 파라미터 제한 (자주 헷갈리는 항목)

엔드포인트별로 지원하는 쿼리가 다르다. 아래는 **존재하지 않는 파라미터를 임의로 만들지 않도록** 정리한 표. 의심되면 항상 `references/<category>.md`로 확인한다.

| 엔드포인트 | 지원 쿼리 | 자주 착각하는 미지원 쿼리 |
|---|---|---|
| `GET /v1/inquiry` | `created_start`, `created_end`, `inquiry_date_start`, `inquiry_date_end`, `cursor`, `folder_id`, `is_hidden`, `page_size`, `search`, `status_id` | ❌ `client_id` (응답의 `client.id`로 클라이언트 필터링) |
| `GET /v1/client` | `created_start`, `created_end`, `cursor`, `is_hidden`, `page_size`, `search`, `status_id` | ❌ `domain`, `email` (응답 검색) |
| `GET /v1/settlement` | `contract_id`, `created_start/end`, `cursor`, `due_date_start/end`, `is_hidden`, `page_size`, `search`, `settled_date_start/end` | ❌ `status` (응답의 `status` 필드로 필터) |
| `GET /v1/contract` | `client_id`, `inquiry_id`, `created_start/end`, `cursor`, `end_date_from/to`, `is_hidden`, `page_size`, `search`, `start_date_from/to` | ❌ `status` (응답 필터) |
| `GET /v1/todo` | `due_date_start/end`, `inquiry_id`, `is_complete`, `cursor`, `page_size` | ❌ `inCharge` (응답 필터) |
| `GET /v1/project` | `start_date_start/end`, `end_date_start/end`, `is_hidden`, `page_size`, `status`, `cursor` | ❌ `inquiry_id` (project 자체는 `contract`만 보유 — `inquiry`는 contract를 거쳐 접근) |
| `GET /v1/estimate/item` | `cursor`, `page_size`, `search` | ❌ `classification` 필터(검색어로 우회) |
| `GET /v1/worker` | `cursor`, `is_hidden`, `page_size`, `position_id`, `search` | — |

규칙: **쿼리에 없는 파라미터는 서버에서 무시되거나 400을 받는다.** "필터가 있어 보이는데 실패한다"면 위 표를 먼저 확인하고, 없으면 일단 페이지를 더 받은 뒤 응답 필드로 클라이언트 사이드 필터링한다.

## 어느 엔드포인트를 쓸까 (라우팅 가이드)

| 사용자 의도 | 카테고리 | 참고할 레퍼런스 |
|---|---|---|
| 신규/기존 리드 조회·생성·수정 | 의뢰(Inquiry) | [references/inquiry.md](references/inquiry.md) |
| 의뢰의 메일 발신/수신/상태/폴더/제출 이력 | 의뢰 하위 history | [references/inquiry.md](references/inquiry.md) |
| 의뢰에 메모 추가 | 의뢰 텍스트 히스토리 | [references/inquiry.md](references/inquiry.md) |
| 의뢰 첨부 파일 추가/삭제 | presigned + 의뢰 PATCH/DELETE | [references/presigned.md](references/presigned.md) + inquiry |
| 고객사 검색·등록·수정 | 고객(Client) | [references/client.md](references/client.md) |
| 견적 항목 템플릿 / 단가 | 견적서 항목(Estimate Item) | [references/estimate.md](references/estimate.md) |
| 계약·계약 히스토리·카테고리 | 계약(Contract) | [references/contract.md](references/contract.md) |
| 정산·정산 히스토리·형태 | 정산(Settlement) | [references/settlement.md](references/settlement.md) |
| 프로젝트 | 프로젝트(Project) | [references/project.md](references/project.md) |
| 할 일 | Todo | [references/todo.md](references/todo.md) |
| 실무자 / 멤버 | 실무자·멤버 | [references/worker.md](references/worker.md), [references/member.md](references/member.md) |
| 커스텀 필드 / 폴더 메타 | 필드·폴더 | [references/field.md](references/field.md), [references/folder.md](references/folder.md) |
| 변경 로그 / 감사 | 로그 | [references/log.md](references/log.md) |

레퍼런스 파일에는 각 엔드포인트의 path/method/query/body/response 필드가 표로 정리돼 있다. 호출 전에 해당 카테고리 파일을 확인하라 — 필드명을 추측하지 말 것.

## 가드레일

- **쓰기 작업은 사용자 승인 후에만.** POST/PATCH/DELETE는 사용자가 명시적으로 요청했을 때만 실행한다. 조회(GET)는 자유롭게 호출해도 된다.
- **DELETE는 두 번 확인.** 의뢰·고객·계약·정산 삭제는 영업 마스터 데이터를 지우는 행위다. "삭제할까요?"를 한 번 더 묻는다. 사용자가 "응" 같은 모호한 답이 아닌 명확한 승인(`삭제`, `OK`)을 주기 전엔 호출하지 않는다.
- **본문 추측 금지.** 사용자가 주지 않은 필드(고객 회사명·이메일, 견적 단가 등)를 임의로 채워 보내지 않는다. 모르면 한 번 묻는다.
- **레이트 리밋 존중.** 한 번에 수십 건을 처리해야 하면 페이지네이션을 따라가되, 429를 받으면 즉시 멈추고 사용자에게 보고한다. 자동 백오프 루프로 분 단위 대기에 들어가지 않는다.
- **시크릿 출력 금지.** API Key, Secret Key를 메시지·로그·코드 주석에 노출하지 않는다. 사용자에게 보여줄 일이 있으면 마스킹한다.

## 다른 스킬과의 연동

- **account-research**: `GET /v1/inquiry/{id}` + 의뢰별 `text_history` / `email_history` / `email_reply_history` / `submit_history` + `GET /v1/client/{id}`로 리드 컨텍스트와 갭 분석 데이터를 확보한다.
- **call-prep**: 위 의뢰 히스토리 4종 + `GET /v1/inquiry/{id}/status_history` + `GET /v1/todo?inquiry_id={id}&is_complete=false` + `GET /v1/contract?inquiry_id={id}` + `GET /v1/project/{id}`로 콜 직전 타임라인을 합성한다.
- **call-summary**: `GET /v1/inquiry/{id}`로 컨텍스트 확보, 사용자 승인 후 `POST /v1/inquiry/{id}/text_history`(요약 메모) + `POST /v1/todo`(액션 아이템)로 콜 결과를 기록한다.
- **daily-briefing**: `GET /v1/inquiry?inquiry_date_start=...` + `GET /v1/todo` + `GET /v1/contract?created_start=...` + `GET /v1/settlement?settled_date_start=...&due_date_start=...` + `GET /v1/project?status=I`로 일일 영업 스냅샷을 생성한다. 읽기 전용.
- **email-send**: 단계별 템플릿 선택을 위해 `GET /v1/inquiry/status` + `GET /v1/inquiry/{id}`로 현재 상태를 확인하고, `GET /v1/client/{id}`로 수신자를 보강한다. 발송 후 `POST /v1/inquiry/{id}/text_history`로 발송 이력을 의뢰에 남긴다. 발신/수신 이력은 `GET /v1/inquiry/{id}/email_history` / `email_reply_history`로 조회.
- **quote-writing**: `GET /v1/estimate/item`(템플릿) + `GET /v1/estimate/item/classification`(분류)으로 단가 매칭, `GET /v1/worker`로 인건비 산정, `GET /v1/client/{id}` / `GET /v1/contract?client_id=...`로 수신자/과거 견적 컨텍스트를 보강한다. 발행 시 `PATCH /v1/inquiry/{id}`(예상 견적 갱신) + `POST /v1/inquiry/{id}/text_history`(발행 메모) + 선택적 `POST /v1/estimate/item`(신규 단가 등록).

다른 스킬에서 이 스킬로 인계할 때는 **어떤 엔드포인트를 호출하고 싶은지** 명시하면 좋다 (예: "pluuug-api로 `GET /v1/inquiry?created_start=2026-05-14`").
