---
name: sales-setup
description: >
  영업 자동화에 필요한 모든 베이스 정보를 OS 표준 위치에 1회 저장해 두는 셋업 스킬입니다.
  Pluuug API 키, 회사 메타(법인명·사업자번호·주소), 영업 담당자 정보(이름·서명·연락처),
  브랜드(강점·차별화·톤), 메인 상품, 자주 쓰는 멘트, 기본 계약 조건을 한 파일에 담아
  account-research / call-prep / call-summary / daily-briefing / email-send / quote-writing이
  자동으로 참조합니다. "셋업", "초기 설정", "회사 정보 등록", "팀 정보 등록", "영업 담당자 추가",
  "브랜드 정보 입력", "강점 등록", "자주 쓰는 멘트", "메일 서명 설정", "Pluuug 키 등록",
  "키 영구 저장", "cowork에서 키 안 풀린다", "프로필 수정", "법인명·사업자번호 등록",
  "이 워크스페이스 처음 세팅" — 처음 환경 구성, 정보 업데이트, 키 교체 시 사용합니다.
---

# 영업 자동화 초기 셋업 (sales-setup)

영업 자동화의 **단일 진실 공급원(Single Source of Truth)**. 한 번 등록해 두면 모든 영업 스킬이 같은 출처를 참조하므로 메일·견적·콜·리드 분석에서 회사명·발신자·서명·기본 결제조건이 자동 일치합니다.

저장 대상:

1. **`credentials.json`** (mode 0600) — Pluuug API Key + Secret Key
2. **`profile.json`** — 회사 · 영업 담당자 배열 · 브랜드 · 상품 · 자주 쓰는 멘트 · 기본 계약 조건 · 리드 적합도 키워드

두 파일 모두 OS 표준 위치(`<config-dir>/sales-automation/`)에 보관됩니다. 각각 독립적으로 설치·교체할 수 있습니다 — 키만 갖고도, 프로필만 갖고도 동작합니다.

---

## 언제 사용하나

- 처음 이 플러그인을 설치한 직후 환경 세팅 (가장 먼저 실행)
- 영업 담당자가 추가되었거나 교체되었을 때 (team 배열 업데이트)
- 회사명·사업자번호·주소·법인명이 변경되었을 때
- 브랜드 강점·차별화 문구를 다듬었을 때
- 새 상품 / 서비스를 추가했을 때
- 자주 쓰는 멘트(인사·CTA·거절 등)를 표준화하고 싶을 때
- Pluuug 키를 재발급해서 교체할 때
- Cowork · 임시 컨테이너 등 매 세션 환경이 새로 시작되는 곳

---

## 저장 위치 (OS별 자동 결정)

| OS | 경로 |
|---|---|
| macOS | `~/Library/Application Support/sales-automation/` |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/sales-automation/` |
| Windows | `%APPDATA%\sales-automation\` |
| Fallback (모든 OS) | `~/.sales-automation/` |

이 디렉토리 안에 `credentials.json`과 `profile.json`이 함께 들어갑니다.

레거시 위치 `<config>/pluuug/` 도 자동으로 인식합니다 — 기존 사용자는 마이그레이션 한 번만 실행하면 됩니다 (`--migrate` 옵션).

---

# Part 1 — Pluuug 키 (credentials.json)

## 인증 우선순위 (pluuug.py가 키를 찾는 순서)

1. **환경 변수** `PLUUUG_API_KEY` / `PLUUUG_SECRET_KEY` — 셸에 export된 값이 가장 우선
2. **프로젝트 `.env`** — 레포 루트 `.env` (로컬 개발용)
3. **OS 표준 위치 — sales-automation/credentials.json** — 이 스킬이 저장 (cowork·운영용)
4. **레거시 — pluuug/credentials.json** — 구 위치 (호환 유지)
5. **`~/.sales-automation/credentials.json` 또는 `~/.pluuug/credentials.json`** — fallback

가장 추천하는 패턴은 **3번**입니다. 한 번 설치하면 새 세션·새 셸·새 머신(같은 사용자 홈)에서 모두 자동 동작합니다.

## 키 설치 방법

### (A) 인터랙티브 (권장, 기본값)

`getpass`로 입력받아 터미널에 키가 노출되지 않습니다.

```bash
skills/sales-setup/scripts/install_credentials.py
# PLUUUG_API_KEY: (입력 시 화면 미노출)
# PLUUUG_SECRET_KEY: (입력 시 화면 미노출)
```

### (B) 현재 환경 변수에서 가져오기

```bash
export PLUUUG_API_KEY="..." PLUUUG_SECRET_KEY="..."
skills/sales-setup/scripts/install_credentials.py --from-env
```

### (C) stdin 파이프 (CI / 자동화)

```bash
printf '%s\n%s\n' "$API_KEY" "$SECRET" | \
  skills/sales-setup/scripts/install_credentials.py --from-stdin
```

### (D) 레거시 위치에서 마이그레이션

기존 `pluuug-setup`을 쓰던 사용자가 새 위치로 옮길 때:

```bash
skills/sales-setup/scripts/install_credentials.py --migrate
# → <config>/pluuug/credentials.json → <config>/sales-automation/credentials.json
```

기존 파일은 자동 삭제되지 않습니다 (안전). pluuug.py는 두 위치 모두 인식합니다.

## 검증

```bash
skills/pluuug-api/scripts/pluuug.py GET /v1/folder
# HTTP 200 + 폴더 목록 JSON → 정상
```

환경 변수 export 없이도 동작해야 합니다.

## 키 교체

```bash
skills/sales-setup/scripts/install_credentials.py --force
# 또는 --from-env --force / --from-stdin --force
```

`--force` 없이는 기존 파일을 덮어쓰지 않습니다.

---

# Part 2 — 영업 프로필 (profile.json)

회사 · 팀 · 브랜드 · 상품 · 자주 쓰는 멘트 · 기본 계약 조건 · 리드 키워드를 한 파일에 보관. 스키마 전체는 [`references/profile_schema.md`](references/profile_schema.md) 참조. 표준 변수(`{{me.name}}`, `{{client.companyName}}` 등) 명세는 [`references/template_variables.md`](references/template_variables.md).

## 7개 섹션 개요

| 섹션 | 내용 | 영향 스킬 |
|---|---|---|
| `company` | 법인명·사업자번호·주소·도메인·대표·홈페이지·전화 | quote-writing(견적서 공급자), email-send(소개/서명) |
| `team[]` | 영업 담당자 배열. 각 멤버에 name·role·email·phone·signature, `active` 1명 지정 | email-send(서명·발신자), quote-writing(발행자 표기), call-prep / call-summary |
| `brand` | tagline·tone·강점·차별화·산업·타깃·핵심 가치 | email-send(자기소개 톤), call-prep(콜 포인트), account-research(적합도) |
| `products[]` | 메인 상품 — name·description·target·defaultPrice·unitType | quote-writing(항목 매칭 힌트), email-send(소개 단락) |
| `phrases` | 자주 쓰는 멘트 (greeting·intro·ctaMeeting·ctaQuote·thanks·decline·discount 등) | email-send(문구 일관성), call-summary(후속 메일 톤) |
| `defaults` | 기본 부가세 유형·결제 조건·견적 유효기간 | quote-writing(자동 기본값) |
| `keywords` | goodFit / outOfScope — 리드 적합도 키워드 | account-research(점수 가산/감점) |

## 설치 흐름 (권장)

### 빈 템플릿 → 편집 → 설치

```bash
# 1. 빈 템플릿 받기
skills/sales-setup/scripts/profile.py --init > my-profile.json

# 2. 편집기로 채우기 (필요한 필드만 — 모두 선택)
vim my-profile.json

# 3. 설치
skills/sales-setup/scripts/profile.py --from-file my-profile.json

# 4. 검증
skills/sales-setup/scripts/profile.py --show
```

### 빠른 시작 — 인터랙티브 (핵심 10개 필드만)

```bash
skills/sales-setup/scripts/profile.py
# 법인명 / 표시명 / 도메인 / 산업 / 내 이름 / 직책 / 이메일 / 연락처 / 강점 2개
```

자동으로 team[0]을 만들고 active=true, 서명을 회사명·이메일·홈페이지로 구성합니다.

### stdin 파이프 (자동화)

```bash
cat my-profile.json | skills/sales-setup/scripts/profile.py --from-stdin
```

### 레거시 business.json 마이그레이션

```bash
skills/sales-setup/scripts/profile.py --migrate
# <config>/pluuug/business.json (v1) → <config>/sales-automation/profile.json (v2)
```

자동 변환:
- `voice.signatureLines[]` → `team[0].signature` (줄바꿈 join)
- `business.industry/strengths/differentiation` → `brand.*`
- `business.coreProducts[]` → `products[]`

## 조회·편집

```bash
# 전체 조회
skills/sales-setup/scripts/profile.py --show

# 활성 영업 담당자만
skills/sales-setup/scripts/profile.py --active

# 저장 경로 확인
skills/sales-setup/scripts/profile.py --show-path

# 교체 (기존 덮어쓰기)
skills/sales-setup/scripts/profile.py --from-file new.json --force
```

직접 편집하려면 `--show-path` 출력 경로의 JSON을 텍스트 에디터로 열어 수정해도 동일하게 동작합니다.

---

# Part 3 — 메일 / 산출물 자동 변수 매핑

영업 스킬이 만드는 모든 산출물(메일 · 견적서 · 콜 브리프 · 콜 요약)은 표준 변수 표기를 사용합니다.

```
{{company.displayName}}    → "똑똑한개발자"
{{me.name}}                → team[active].name
{{me.signature}}           → team[active].signature (멀티라인)
{{client.companyName}}     → Pluuug 의뢰의 client.companyName
{{client.contactName}}     → Pluuug 의뢰의 client.inCharge
{{client.inquiryName}}     → Pluuug 의뢰의 name
{{brand.tagline}}          → brand.tagline
{{date}}                   → 오늘 (YYYY-MM-DD)
```

전체 변수 명세는 [`references/template_variables.md`](references/template_variables.md).

## 렌더 헬퍼

```bash
# 변수 치환 (context JSON으로 client.* 등 채움)
echo '{"client":{"companyName":"(주)테스트","contactName":"홍길동"}}' | \
  skills/sales-setup/scripts/render_template.py \
    --template skills/email-send/templates/00-신규접수-첫응답.md \
    --context - \
    --warn

# 템플릿이 사용하는 변수 목록 추출
skills/sales-setup/scripts/render_template.py \
  --vars skills/email-send/templates/30-견적송부.md

# frontmatter ↔ 본문 변수 일치 점검
skills/sales-setup/scripts/render_template.py \
  --check-template skills/email-send/templates/30-견적송부.md
```

Python에서 직접 import도 가능:

```python
import sys
sys.path.insert(0, "skills/sales-setup/scripts")
from render_template import build_context, render
from profile import load_profile, get_active_member

ctx = build_context({"client": {"companyName": "..."}})
rendered, missing = render(template_text, ctx, warn=True)
```

미해결 변수는 `{{...}}` 형태로 본문에 그대로 남아 사용자가 즉시 식별·수정할 수 있습니다.

---

## 가드레일

- **시크릿 출력 금지** — credentials.json의 API Key·Secret Key를 채팅·로그에 echo하지 않습니다. install_credentials.py는 stdout에 키를 절대 표시하지 않으며, 명령줄 인자로도 받지 않습니다(ps 노출 차단).
- **권한 0600** — credentials.json은 소유자만 읽기/쓰기. Windows에서는 chmod가 무효지만 동작에는 영향 없음.
- **기존 파일은 `--force` 없이 덮어쓰지 않음** — 실수 방지.
- **추측 금지** — 사용자가 채우지 않은 필드를 스킬이 임의로 생성하지 않습니다 ("미상"으로 두거나 한 번 묻습니다).
- **민감 정보 노출 위치 명시** — 사업자번호 / CEO명 등은 quote-writing 같이 명시적으로 그 정보를 쓰는 스킬에서만 외부 발송물에 노출됩니다. 메일 본문에 자동 노출 안 됨.
- **마이그레이션 안전** — 레거시 파일은 자동 삭제되지 않습니다. 사용자가 직접 정리.

---

## 트러블슈팅

| 증상 | 원인·해결 |
|------|----------|
| `[sales-setup] credentials already exist` | 이미 저장된 키. 교체하려면 `--force`. |
| `HTTP 401 InvalidSignature` | 키 페어 불일치. 재발급 후 `--force`로 재설치. |
| `HTTP 403` | API 키 유효하나 권한 부족. Agency 플랜 확인. |
| `credentials not found` | 셸의 잘못된 env var가 우선됨. `unset PLUUUG_API_KEY PLUUUG_SECRET_KEY` 후 재시도. |
| `profile.py --show` 결과가 옛 5섹션 | 레거시 business.json만 있고 v2로 마이그레이션 안 됨. `profile.py --migrate` 실행. |
| 메일 서명이 일반 톤으로 나옴 | profile.team[active].signature가 비어 있음. `--show`로 확인 후 채우기. |
| `{{me.name}}` 잔재가 메일에 보임 | team[active] 미설정 또는 다른 멤버에 active. `profile.py --active`로 확인. |

---

## 다른 스킬과의 관계

| 스킬 | 어떤 필드를 어떻게 활용 |
|---|---|
| **pluuug-api** | credentials.json을 `load_credentials()`로 자동 로드. 다른 모든 영업 스킬이 pluuug-api를 거치므로 키 한 번 설치하면 끝. |
| **email-send** | `voice.tone` / `me.signature` / `company.displayName` / `brand.strengths` 자동 적용 — 모든 발송 메일의 톤·서명·소개 일관 |
| **quote-writing** | 견적서 공급자 섹션을 `company.*` + `team[active].*`로 자동 채움. `defaults.vatType` / `paymentTerms` / `quoteValidityDays`를 기본값으로 |
| **account-research** | `keywords.goodFit/outOfScope` 매칭 시 가중치, `brand.targetCustomers` 부합 시 "✅ 핵심 타깃 부합" 표시 |
| **call-prep** | 콜 포인트 가이드에 `brand.strengths` / `brand.differentiation` 노출, 자기소개 헤더에 `company.displayName` |
| **call-summary** | 후속 메일 / 의뢰 메모 작성 시 `brand.tone` / `brand.language` 유지 |
| **daily-briefing** | 영업 담당자 표기 / 회사 표시명 등 일관성 |

활용 정책: **있으면 쓰고 없으면 무시 — 단, 발송·발행에 필요한 최소치는 강제**. 자세한 차단 규칙은 아래 Part 4 참조.

---

# Part 4 — Setup Gate (다른 스킬 사전 차단)

다른 영업 스킬은 **실행 직전 `scripts/check_setup.py`로 setup 충족 여부를 검증**한 뒤 진행합니다. 미달이면 `sales-setup` 실행을 안내하고 중단합니다 — 이는 placeholder가 남은 메일이 발송되거나 Pluuug 401이 떨어지는 일을 막기 위함입니다.

## 3단계 게이트

| 레벨 | 충족 조건 | 차단 대상 |
|---|---|---|
| **L0** | credentials.json (PLUUUG_API_KEY + PLUUUG_SECRET_KEY) | account-research, call-prep, call-summary, daily-briefing, email-send, quote-writing — **모든 Pluuug 호출** |
| **L1** | L0 + team[active].name·email·signature + company.displayName | call-summary, email-send, quote-writing — **고객 발송·기록 산출물** |
| **L2** | L1 + brand.tagline + brand.strengths + defaults.paymentTerms | (차단 없음, 경고만) generic 표현 회피 |

L0는 **HARD** 게이트 — 통과하지 못하면 어떤 스킬도 진행 불가. L1은 발송/발행 스킬에만 HARD. L2는 SOFT (워닝).

## 사용 방법

```bash
# 사람이 읽는 표
skills/sales-setup/scripts/check_setup.py --level L1

# CI/스크립트용 (exit code만)
skills/sales-setup/scripts/check_setup.py --level L1 --quiet
echo "exit: $?"   # 0=pass, 1=block

# 머신용 JSON
skills/sales-setup/scripts/check_setup.py --level L2 --json
```

## 영업 스킬에서 사전 점검 패턴

각 영업 스킬은 본문 절차 0단계에 다음을 명시합니다:

```bash
if ! skills/sales-setup/scripts/check_setup.py --level L1 --quiet; then
  echo "Setup이 충분하지 않습니다. sales-setup 스킬을 먼저 실행해주세요."
  echo "부족 항목 확인: skills/sales-setup/scripts/check_setup.py --level L1"
  exit 1
fi
```

각 스킬의 요구 레벨:

| 스킬 | 요구 레벨 |
|---|---|
| account-research | L0 (Pluuug GET만) |
| call-prep | L0 (Pluuug GET + 외부 데이터 읽기) |
| daily-briefing | L0 (읽기 전용) |
| call-summary | L1 (의뢰 히스토리·Todo 저장에 me.* 필요) |
| email-send | L1 (메일 발송에 me.signature·company.displayName 필수) |
| quote-writing | L1 (견적서 공급자에 company.*·team[active].* 필수) |

## 차단 시 사용자에게 보여줄 안내

스킬 진입 시 게이트 실패하면:

```
이 스킬은 sales-setup이 완료돼 있어야 합니다 (요구 레벨: <L0|L1>).
부족한 항목이 있어 진행할 수 없습니다.

확인: skills/sales-setup/scripts/check_setup.py --level <레벨>
설치: skills/sales-setup/scripts/install_credentials.py  (키)
설치: skills/sales-setup/scripts/profile.py              (프로필)
```

추측해서 채우거나, 빈 값으로 발송하지 않습니다.
