# sales-automation

**현재 버전**: [v0.2.0](https://github.com/postoo-io/sales-automation/releases/tag/v0.2.0)

Claude Code 플러그인. B2B 영업 워크플로우(리드 검증 → 콜 준비/요약 → 견적 → 메일 → 일일 브리핑)를 Gmail, Google Drive, Google Calendar, Slack, [Pluuug](https://pluuug.com)와 연동해 한 곳에서 처리합니다.

돈이나 고객에게 도달하는 작업(메일 발송, 견적 발행, 의뢰 히스토리 기록, Todo 생성)은 **항상 사용자 승인을 거친 뒤에만** 실행됩니다.

## 구성

### Skills

플러그(Pluuug) 데이터에 접근하는 모든 스킬은 `pluuug-api` 스킬을 거쳐 호출합니다 (HMAC-SHA256 서명 + 엔드포인트 라우팅 위임).

| 스킬 | 언제 트리거되나 | 보조 자원 |
|---|---|---|
| [`sales-setup`](skills/sales-setup/SKILL.md) | "pluuug 키 설정", "Pluuug API 등록", "키 영구 저장", "회사 정보 저장", "비즈니스 프로필 설정", "메일 서명 등록", "cowork에서 키 안 풀린다" | `scripts/install_credentials.py` (키 0600 영구 저장) · `scripts/profile.py` (통합 영업 프로필(회사·팀·브랜드·상품·자주 쓰는 멘트)) · `references/profile_schema.md` |
| [`pluuug-api`](skills/pluuug-api/SKILL.md) | 플러그 Open API 호출 전반 — 의뢰·고객·견적 항목·계약·정산·프로젝트·할 일·실무자 조회/생성/수정 | `scripts/` `references/` (13개 엔드포인트 스펙) |
| [`account-research`](skills/account-research/SKILL.md) | "이 리드 분석해줘", "[회사명] 리서치", "허위문의 확인", "이 의뢰에서 더 받아야 할 정보" | 11신호 점수 룰 (본문 내장) |
| [`call-prep`](skills/call-prep/SKILL.md) | "전화 전 요약", "[회사명] 콜 준비", "이 의뢰 콜 브리프", "[프로젝트명] 콜 들어간다" | `scripts/collect_context.sh` · `assets/brief_{short,deep}.md` · `references/slack_channel_matching.md` |
| [`call-summary`](skills/call-summary/SKILL.md) | "콜 요약", "녹음 정리", "이 콜 의뢰에 기록", "콜 후속 todo 만들어줘" | `scripts/transcribe.sh` · `assets/summary_template.md` · `assets/pluuug_history_body.md` · `references/action_item_examples.md` |
| [`daily-briefing`](skills/daily-briefing/SKILL.md) | "오늘 브리핑", "모닝 브리프", "데일리", "EOD", "당월 수주/정산 요약" | `scripts/fetch_briefing.sh` · `scripts/calc_priority.py` · `assets/brief_{full,quick,eod}.md` |
| [`email-send`](skills/email-send/SKILL.md) | "답장 초안", "미팅 제안 메일", "견적 송부 메일", "팔로업", "[회사명] 메일 다듬어줘" | `templates/` (단계별 메일 8종) |
| [`quote-writing`](skills/quote-writing/SKILL.md) | "견적서 작성", "단가 계산", "할인 적용해서 다시", "이 견적 손익 봐줘", "리스크만 봐줘" | `scripts/calc_margin.py` · `scripts/detect_risks.py` · `references/risk_catalog.md` · `assets/quote_template.md` |

영업 워크플로우는 자연스럽게 이어집니다:

```
의뢰 인입 → account-research(리드 검증·갭 분석)
         → call-prep(콜 직전 요약) → 콜 → call-summary(요약·Todo 기록)
         → quote-writing(견적·손익·리스크) → email-send(견적 송부 메일)
         → daily-briefing(매일 현황 요약)
```

### MCP 서버

[`.mcp.json`](.mcp.json)에 정의되어 있습니다.

| 이름 | 용도 |
|---|---|
| `gmail` | 메일 검색/송수신 이력/발송 |
| `google_drive` | 첨부 파일, 견적서 PDF 저장 |
| `google_calendar` | 미팅 슬롯 조회 및 일정 생성 |
| `slack` | 영업 채널 컨텍스트 / 공지 |

> 플러그는 MCP를 제공하지 않아 [Open API](https://docs.openapi.pluuug.com)로 직접 호출합니다. `pluuug-api` 스킬이 인증/시그니처/엔드포인트 라우팅을 담당합니다.

### 인증 키 설정

플러그 Open API는 **Agency 플랜의 API Key + Secret Key**가 필요합니다 (비즈니스 설정 > 웹훅 & API > 오픈 API 탭에서 발급).

`scripts/pluuug.py`는 아래 우선순위로 키를 자동 탐색합니다 — 일치하는 첫 번째에서 사용:

| 순위 | 소스 | 적합한 환경 |
|---|---|---|
| 1 | 환경 변수 `PLUUUG_API_KEY` / `PLUUUG_SECRET_KEY` | CI, 임시 오버라이드 |
| 2 | 프로젝트 루트 `.env` (gitignored) | 로컬 개발 |
| 3 | OS 표준 위치 (macOS `~/Library/Application Support/pluuug/`, Linux `$XDG_CONFIG_HOME/pluuug/`, Windows `%APPDATA%\pluuug\`) | **Cowork·운영·다중 머신 (권장)** |
| 4 | `~/.pluuug/credentials.json` | 크로스플랫폼 fallback |

**권장: OS 표준 위치에 1회 영구 저장** — 매 세션 환경 변수를 다시 설정할 필요가 없습니다. `sales-setup` 스킬이 자동화합니다:

```bash
# 인터랙티브 (getpass — 입력 시 화면 미노출)
skills/sales-setup/scripts/install_credentials.py

# 또는 현재 셸 env에서 가져와 영구화
export PLUUUG_API_KEY="..." PLUUUG_SECRET_KEY="..."
skills/sales-setup/scripts/install_credentials.py --from-env

# 또는 stdin 파이프 (CI/자동화)
printf '%s\n%s\n' "$API_KEY" "$SECRET" | \
  skills/sales-setup/scripts/install_credentials.py --from-stdin
```

파일은 `0600` 권한으로 저장되어 소유자만 읽을 수 있습니다.

### 비즈니스 프로필 (권장)

자사 정보(법인명·산업·강점·서명·기본 결제조건 등)를 같은 디렉토리의 `profile.json`에 저장하면 영업 스킬들이 메일·견적·콜에서 일관된 자기소개와 기본값을 사용합니다.

```bash
# 1. 템플릿 받기 → 편집 → 설치
skills/sales-setup/scripts/profile.py --init > my-profile.json
vim my-profile.json
skills/sales-setup/scripts/profile.py --from-file my-profile.json

# 또는 인터랙티브 (핵심 필드만 빠르게)
skills/sales-setup/scripts/profile.py
```

스키마 전체: [`skills/sales-setup/references/profile_schema.md`](skills/sales-setup/references/profile_schema.md).

| 활용 | 어느 스킬 | 어떤 필드 |
|---|---|---|
| 메일 서명·자기소개·톤 | `email-send` | `me.signature`, `brand.strengths`, `brand.tone` |
| 견적서 공급자 정보·기본 조건 | `quote-writing` | `company.legalName/registrationNumber/address`, `defaults.vatType/paymentTerms` |
| 리드 적합도 가중치 | `account-research` | `keywords.goodFit/outOfScope`, `business.targetCustomers` |
| 콜 강점·차별화 가이드 | `call-prep` | `brand.strengths`, `brand.differentiation` |

비즈니스 프로필 없이도 모든 스킬은 동작합니다 — 다만 자기소개·서명·기본값이 generic하게 나옵니다.

**로컬 개발에서 빠르게 시작하려면** `.env` 파일도 여전히 동작합니다:

```bash
# .env (gitignored)
PLUUUG_API_KEY=...
PLUUUG_SECRET_KEY=...
```

## 설치

이 레포지토리를 Claude Code 플러그인으로 사용하는 방법:

```bash
# 1. 클론
git clone https://github.com/postoo-io/sales-automation.git ~/.claude/plugins/sales-automation

# 2. Claude Code 재시작
```

플러그인이 로드되면 `skills/` 아래 스킬이 모델에 자동 노출되고, `.mcp.json`의 MCP 서버에 연결을 시도합니다.

### 동작 검증

키 등록 후 가장 단순한 호출로 인증을 확인합니다:

```bash
skills/pluuug-api/scripts/pluuug.py GET /v1/folder
# HTTP 200 + 폴더 목록 JSON → 정상
```

## 산출물 데모

각 스킬을 실행하면 어떤 결과가 나오는지 가상 시나리오와 실 환경 실행 결과 두 갈래로 확인할 수 있습니다:

- [`examples/`](examples/) — (주)노바테크 가상 시나리오로 6개 스킬 산출물 미리보기 (인입 → 콜 전 → 콜 후 → 다음날 → 메일 → 견적)
- [`examples/real-runs/`](examples/real-runs/) — 실제 Pluuug API 호출 결과로 만든 산출물 (워크스페이스 상태에 따라 내용이 달라짐)

각 산출물은 "사용자 발화 → 스킬 실행 결과" 순서로 구성되어 있습니다.

## 가드레일 (전 스킬 공통)

- **자동 발송/발행 금지** — 메일 전송과 견적 발행은 사용자의 명시적 승인("보내", "발행") 뒤에만 실행됩니다.
- **자동 쓰기 금지** — pluuug에 의뢰 히스토리 메모, Todo 생성, 의뢰/고객 수정 등 모든 POST/PATCH/DELETE는 사용자 승인 후에만.
- **추측 금지** — 금액, 담당자, 회사 정보를 모를 때는 "미상"으로 두거나 한 번 물어봅니다.
- **권한 자동 변경 금지** — Drive 공유 권한, Slack 채널 가입 등은 사용자에게 확인을 받습니다.
- **중복 발송 경고** — 같은 수신자에게 24시간 내 유사한 메일이 나가면 경고합니다.
- **민감 정보 보호** — 손익/마진율 같은 내부 수치는 외부 발송물(메일·견적 PDF·플러그 히스토리)에 노출하지 않습니다.
- **시크릿 출력 금지** — API Key, Secret Key를 채팅·로그·코드 주석에 노출하지 않습니다.

## 버전 관리

플러그 매니페스트 두 파일(`plugin.json` · `marketplace.json`)의 version을 락스텝으로 올려 매 push마다 사용자가 어떤 버전인지 추적 가능하게 합니다. `scripts/bump_version.sh` 헬퍼로 한 번에 동기 업데이트:

```bash
# 현재 버전 확인
scripts/bump_version.sh --show

# semver 컴포넌트 자동 증가
scripts/bump_version.sh patch     # 0.2.0 → 0.2.1
scripts/bump_version.sh minor     # 0.2.0 → 0.3.0
scripts/bump_version.sh major     # 0.2.0 → 1.0.0

# 명시 설정
scripts/bump_version.sh --set 1.2.3

# 그 후 커밋 + 푸시
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "Release vX.Y.Z"
git push
```

semver 가이드 (정확한 룰보다 판단력):

- **patch** — 버그 수정 · 본문 미세 수정 · 문서·내부 리팩토링
- **minor** — 새 스킬 / 새 보조 자원 / 새 기능 (호환 유지)
- **major** — 스키마 변경 · 스킬 이름 변경 · 호환 깨짐

`scripts/bump_version.sh`는 두 파일의 version 불일치도 감지합니다 (exit 3).

## 디렉토리 구조

```
.
├── .claude-plugin/
│   └── plugin.json                  # 플러그인 매니페스트
├── .mcp.json                        # MCP 서버 등록 (gmail, drive, calendar, slack)
├── .env                             # Pluuug 키 (gitignored, 자동 로드)
├── skills/
│   ├── sales-setup/                # 영업 자동화 초기 셋업 (키 + 프로필 + 게이트)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── install_credentials.py  # Pluuug 키 0600 영구 저장
│   │   │   ├── profile.py              # 통합 프로필 (회사·팀·브랜드·상품·멘트) v2
│   │   │   ├── render_template.py      # mustache 변수 치환 (profile + Pluuug 자동 합성)
│   │   │   └── check_setup.py          # L0/L1/L2 사전 점검 게이트
│   │   └── references/
│   │       ├── profile_schema.md       # 7섹션 스키마 v2
│   │       └── template_variables.md   # 표준 변수 네임스페이스 명세
│   ├── pluuug-api/                  # 모든 Pluuug API 호출의 단일 진입점
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── pluuug.py            # HMAC 서명 + 4단계 키 자동 탐색
│   │   │   └── presigned_upload.sh  # S3 presigned 업로드
│   │   └── references/              # inquiry/client/contract/settlement/todo 등 13개 엔드포인트 스펙
│   ├── account-research/
│   │   └── SKILL.md                 # 11신호 점수 룰(본문 내장)·갭 분석·유효성 등급
│   ├── call-prep/
│   │   ├── SKILL.md
│   │   ├── scripts/collect_context.sh   # 9개 Pluuug GET 병렬 호출 + manifest
│   │   ├── assets/
│   │   │   ├── brief_short.md       # 1분 브리프 템플릿
│   │   │   └── brief_deep.md        # 심층 브리프 템플릿
│   │   └── references/slack_channel_matching.md
│   ├── call-summary/
│   │   ├── SKILL.md
│   │   ├── scripts/transcribe.sh    # 로컬 whisper 감지·실행
│   │   ├── assets/
│   │   │   ├── summary_template.md  # 화면 표시용 풀 요약
│   │   │   └── pluuug_history_body.md  # 의뢰 히스토리용 컴팩트본
│   │   └── references/action_item_examples.md
│   ├── daily-briefing/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── fetch_briefing.sh    # 10개 GET 병렬 호출 + manifest
│   │   │   └── calc_priority.py     # 10단계 점수표 자동 산정
│   │   └── assets/
│   │       ├── brief_full.md
│   │       ├── brief_quick.md
│   │       └── brief_eod.md
│   ├── email-send/
│   │   ├── SKILL.md
│   │   └── templates/               # 의뢰 단계별 메일 템플릿 8종
│   └── quote-writing/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── calc_margin.py       # Decimal 기반 손익 계산
│       │   └── detect_risks.py      # R1–R10 리스크 자동 감지
│       ├── assets/quote_template.md # 외부 발송용 (마진 변수 없음)
│       └── references/risk_catalog.md
├── examples/                        # 가상 시나리오 산출물 데모
│   ├── README.md
│   ├── scenario.md
│   ├── outputs/                     # 6개 스킬별 가상 산출물
│   └── real-runs/                   # 실제 API 호출 결과
└── README.md
```

새 스킬을 추가할 때는 `skills/<name>/SKILL.md`에 프론트매터(`name`, `description`)와 본문(언제 사용하나 / 절차 / 가드레일)을 작성하세요. `description`은 모델이 라우팅 판단에 사용하므로, 어떤 사용자 발화에 트리거되는지 구체적으로 적어야 합니다.

반복 로직은 `scripts/`, 출력 템플릿은 `assets/`, 긴 참조 문서는 `references/`로 분리하면 SKILL.md 본문을 500줄 이하로 유지할 수 있고 매 실행 시 모델이 같은 추론을 다시 하지 않습니다. 플러그 데이터에 접근해야 한다면 새 스킬도 반드시 `pluuug-api`를 거치도록 작성합니다 (직접 HMAC 서명 재구현 금지).
