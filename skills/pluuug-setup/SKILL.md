---
name: pluuug-setup
description: >
  Pluuug Open API 키와 자사 비즈니스 프로필(법인명·산업·강점·서명·기본 결제조건 등)을 OS
  표준 위치에 영구 저장합니다. 매 세션 환경 변수를 다시 설정하지 않아도 `pluuug.py`가
  자동으로 키를 로드하고, 영업 스킬들이 자기소개·서명·견적서 공급자 정보를 일관되게 채웁니다.
  "pluuug 키 설정", "Pluuug API 등록", "키 영구 저장", "처음 사용",
  "세션마다 키 다시 입력하기 싫어", "cowork에서 키 안 풀린다",
  "회사 정보 저장", "비즈니스 프로필 설정", "메일 서명 등록", "강점·핵심 서비스 등록" —
  처음 환경 세팅, 키 교체, 자사 정보 업데이트 시 사용합니다.
---

# Pluuug 환경 설정 (pluuug-setup)

두 가지를 **사용자 OS의 표준 설정 위치**에 저장합니다:

1. **인증 키** (`credentials.json`, mode 0600) — 매 세션 환경 변수 재설정 불필요
2. **비즈니스 프로필** (`business.json`) — 자사 정보·강점·서명·기본 계약 조건. 영업 스킬들이 자동 참조해 메일·견적·콜에서 일관된 톤과 정보 사용

각각 독립적으로 설치·교체할 수 있습니다 — 키만 갖고도 동작하고, 비즈니스 프로필만 있어도 동작합니다.

---

## 언제 사용하나

- 처음 이 플러그인을 설치한 직후 인증 설정
- 키를 재발급해서 교체할 때
- Cowork·임시 컨테이너 등 매 세션이 새로 시작되는 환경에서 `.env`가 유실될 때
- 여러 머신에서 같은 키를 쓰고 싶을 때 (각 머신에서 한 번씩 설치)

---

## 저장 위치 (OS별 자동 결정)

| OS | 경로 |
|---|---|
| macOS | `~/Library/Application Support/pluuug/credentials.json` |
| Linux | `${XDG_CONFIG_HOME:-~/.config}/pluuug/credentials.json` |
| Windows | `%APPDATA%\pluuug\credentials.json` |
| Fallback (모든 OS) | `~/.pluuug/credentials.json` |

파일 권한은 자동으로 `0600` (소유자만 읽기/쓰기). 포맷:

```json
{"api_key": "...", "secret_key": "..."}
```

---

## 인증 우선순위 (pluuug.py가 키를 찾는 순서)

1. **환경 변수** — 셸에 `export PLUUUG_API_KEY=...` 된 값이 가장 우선
2. **프로젝트 `.env`** — 레포 루트 `.env`에 정의된 값 (개발 환경)
3. **OS 표준 위치** — 이 스킬이 저장한 파일 (cowork·운영 환경)
4. **`~/.pluuug/credentials.json` fallback**

이 스킬은 **3번**에 키를 심어 영구화합니다. 1·2번은 그대로 두면 됩니다 — 명시적 환경변수가 있으면 그게 우선이고, 없을 때 자동으로 영구 키로 떨어집니다.

---

## 절차

### 단계 1 — 키 발급 확인

Pluuug 대시보드에서 **Agency 플랜의 API Key + Secret Key**를 발급받았는지 확인합니다 (비즈니스 설정 > 웹훅 & API > 오픈 API 탭).

키가 아직 없다면 발급 절차를 안내한 뒤 중단합니다 — 추측하지 않습니다.

### 단계 2 — 저장 (3가지 입력 방식 중 선택)

#### (A) 인터랙티브 (권장 — 기본값)

`getpass`로 입력받아 터미널에 키가 노출되지 않습니다.

```bash
skills/pluuug-setup/scripts/install_credentials.py
# PLUUUG_API_KEY: (입력 시 화면에 표시되지 않음)
# PLUUUG_SECRET_KEY: (입력 시 화면에 표시되지 않음)
```

#### (B) 현재 환경 변수에서 가져오기

이미 셸에 `export`해 둔 키를 영구화할 때.

```bash
export PLUUUG_API_KEY="..."
export PLUUUG_SECRET_KEY="..."
skills/pluuug-setup/scripts/install_credentials.py --from-env
```

#### (C) stdin으로 전달 (스크립트화)

CI나 자동화 흐름에서. 첫 줄에 API Key, 둘째 줄에 Secret Key.

```bash
printf '%s\n%s\n' "$API_KEY" "$SECRET" | \
  skills/pluuug-setup/scripts/install_credentials.py --from-stdin
```

> ⚠️ 키를 명령줄 인자로 받지 않습니다. `ps`로 다른 사용자에게 노출되는 것을 막기 위함입니다.

### 단계 3 — 검증

```bash
skills/pluuug-api/scripts/pluuug.py GET /v1/folder
```

`HTTP 200 + 폴더 목록 JSON`이 나오면 성공. 어떤 환경 변수도 export하지 않고도 동작해야 합니다.

### 단계 4 — 키 교체 (필요 시)

```bash
skills/pluuug-setup/scripts/install_credentials.py --force
# 또는 --from-env --force / --from-stdin --force
```

`--force` 없이는 기존 파일을 덮어쓰지 않습니다 (실수 방지).

### 저장 위치 확인만 하고 싶을 때

```bash
skills/pluuug-setup/scripts/install_credentials.py --show-path
# → /Users/.../Library/Application Support/pluuug/credentials.json
```

---

## 가드레일

- **키를 채팅·로그에 출력하지 않는다.** install_credentials.py는 stdout에 키를 절대 echo하지 않으며, `--show-path` 외에는 경로만 알려줍니다.
- **명령줄 인자로 키를 받지 않는다.** stdin / env / getpass만 허용. `ps aux` 노출 위험 차단.
- **기존 파일은 `--force` 없이 덮어쓰지 않는다.** 실수로 운영 키를 덮어쓰는 사고 방지.
- **권한 0600.** 소유자만 읽기/쓰기. Windows에서는 `chmod`가 무시되지만 동작에는 영향 없음.
- **검증은 항상 GET 호출만.** 키가 유효한지 확인하기 위해 안전한 GET (`/v1/folder`)만 사용. 어떤 쓰기 호출도 하지 않습니다.

---

## 트러블슈팅

| 증상 | 원인·해결 |
|------|----------|
| `[pluuug-setup] credentials already exist` | 이미 저장된 키가 있음. 교체하려면 `--force`. |
| `HTTP 401 InvalidSignature` (이후 검증 시) | 키 페어 불일치. Pluuug 대시보드에서 새로 발급 후 `--force`로 재설치. |
| `HTTP 403` | API 키는 유효하나 권한 부족. Agency 플랜인지 확인. |
| 검증 시 여전히 "credentials not found" | 셸에 잘못된 env var가 남아 있을 수 있음. `unset PLUUUG_API_KEY PLUUUG_SECRET_KEY` 후 재시도. |

---

## 다른 스킬과의 관계

- **pluuug-api**: 이 스킬이 저장한 키를 자동 로드합니다 (`load_credentials()`). 다른 모든 영업 스킬은 pluuug-api를 거치므로 한 번 설치하면 전부 동작.
- **다른 영업 스킬 (account-research, call-prep, …)**: 이 스킬을 먼저 1회 실행해 두면 인증 단계가 자동화됩니다.

---

# 비즈니스 프로필 (business.json)

영업 스킬들이 메일·견적·콜에서 일관된 자사 정보를 쓰도록 회사 메타·강점·서명·기본 계약 조건을 저장합니다.

저장 위치: 같은 디렉토리에 `business.json` (`<config-dir>/pluuug/business.json`). 권한은 일반 파일.

스키마 전체는 [references/business_schema.md](references/business_schema.md) 참조 — 5개 섹션(`company` · `business` · `voice` · `defaults` · `keywords`).

## 비즈니스 프로필 설치 흐름 (권장)

```bash
# 1. 빈 템플릿 받기
skills/pluuug-setup/scripts/business_info.py --init > my-business.json

# 2. 편집기로 채우기 (필요한 필드만 — 모두 선택)
vim my-business.json

# 3. 설치
skills/pluuug-setup/scripts/business_info.py --from-file my-business.json
```

빠른 시작용 인터랙티브 모드 (핵심 필드 7개만):

```bash
skills/pluuug-setup/scripts/business_info.py
# 법인명 / 표시명 / 도메인 / 산업 / 강점 3개 / 서명 한 줄
```

CI나 자동화에서는 stdin:

```bash
cat my-business.json | skills/pluuug-setup/scripts/business_info.py --from-stdin
```

조회·경로 확인:

```bash
skills/pluuug-setup/scripts/business_info.py --show       # 전체 JSON
skills/pluuug-setup/scripts/business_info.py --show-path  # 경로만
```

교체할 때는 `--force` 추가.

## 영업 스킬에서 비즈니스 프로필을 어떻게 활용하나

| 스킬 | 활용 필드 | 효과 |
|---|---|---|
| **email-send** | `voice.signatureLines`, `company.displayName`, `business.strengths`, `voice.tone` | 모든 발송 메일 서명·소개 단락·톤이 자동 일관 |
| **quote-writing** | `company.legalName/registrationNumber/ceoName/address`, `defaults.vatType/paymentTerms/quoteValidityDays` | 견적서 공급자 정보·기본 조건 자동 채움 |
| **account-research** | `business.industry`, `business.targetCustomers`, `keywords.goodFit/outOfScope` | 리드 적합도 평가에 가중치 (우리 타깃과 부합/이탈) |
| **call-prep** | `business.strengths`, `business.differentiation` | "콜에서 강조할 차별화 포인트" 가이드 |
| **call-summary** | `voice.tone`, `voice.language` | 후속 메일 / 메모 톤 일관 |

각 스킬은 **있으면 쓰고, 없으면 무시**합니다. 비즈니스 프로필이 없어도 모든 스킬은 동작합니다 — 다만 자기소개·서명·기본값이 generic하게 나옵니다.

## 가드레일 (비즈니스 프로필)

- **사업자번호·CEO명 등 민감 정보 포함 가능** — 외부 발송물에는 `quote-writing` 같이 명시적으로 그 정보를 쓰는 스킬에서만 노출됩니다. 메일 본문에 자동 노출되지 않습니다.
- **파일 추측 금지** — 사용자가 채우지 않은 필드를 스킬이 임의로 만들어내지 않습니다 ("미상"으로 두거나 사용자에게 한 번 묻습니다).
- **버전 호환** — 향후 스키마가 확장되면 `schemaVersion`이 올라갑니다. 현재 v1. 알려진 버전이 아니면 설치 시 거부.
