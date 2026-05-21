# 메일 / 산출물 표준 변수 명세

`skills/sales-setup/scripts/render_template.py`가 인식하는 변수 네임스페이스. 모든 이메일 템플릿(`skills/email-send/templates/00-..70-...md`)과 견적·콜 산출물에서 동일한 표기를 사용해 일관성을 확보합니다.

문법: `{{namespace.field}}` — mustache 스타일. 점(.)으로 중첩 접근.

값이 비어 있는 변수는 **그대로 `{{...}}`로 남깁니다** (사람이 즉시 알아보고 수정). `--strict` 옵션을 주면 빈 변수 발견 시 종료 코드 3으로 abort합니다.

---

## 네임스페이스 요약

| 네임스페이스 | 출처 | 채워지는 시점 |
|---|---|---|
| `company` | `profile.json` company 섹션 | 영구 (한 번 install) |
| `me` | `profile.json` team 배열의 active 멤버 | 영구 (영업 담당자별 1명) |
| `brand` | `profile.json` brand 섹션 | 영구 |
| `client` | Pluuug 의뢰/고객 응답 (`GET /v1/inquiry/{id}`) | 실행 시점 |
| `quote` | quote-writing 산출물 (합계·유효기간·Drive URL 등) | 실행 시점 |
| `meeting` | 미팅 제안 컨텍스트 | 실행 시점 |
| `contract` | 계약 안내 컨텍스트 | 실행 시점 |
| `kickoff` | 수주 후 킥오프 컨텍스트 | 실행 시점 |
| `prevEmail` | 팔로업용 — 직전 메일 메타 | 실행 시점 |
| `request` | 자료 요청 컨텍스트 | 실행 시점 |
| `hold` | 보류·재개 타진 컨텍스트 | 실행 시점 |
| `team` | 특수 매핑 (`team.pm` → PM 역할 멤버 name) | 실행 시점 |
| `date` | 오늘 날짜 (YYYY-MM-DD) | 실행 시점 자동 |

---

## company.*

| 변수 | 의미 | 예시 |
|---|---|---|
| `company.legalName` | 정식 법인명 | "주식회사 똑똑한개발자" |
| `company.displayName` | 브랜드 약칭 | "똑똑한개발자" |
| `company.registrationNumber` | 사업자등록번호 | "123-45-67890" |
| `company.ceoName` | 대표자명 | "이지훈" |
| `company.address` | 본사 주소 | "서울 강남구 …" |
| `company.domain` | 도메인 (https:// 없이) | "toktokhan.dev" |
| `company.homepage` | 홈페이지 URL | "https://toktokhan.dev" |
| `company.phone` | 대표 전화 | "02-1234-5678" |

---

## me.* (활성 영업 담당자)

`profile.json` → `team[]` 배열에서 `active: true`인 멤버. 없으면 첫 멤버.

| 변수 | 의미 |
|---|---|
| `me.name` | 영업 담당자 이름 |
| `me.role` | 직책 |
| `me.email` | 회사 이메일 |
| `me.phone` | 핸드폰 / 직통 |
| `me.signature` | 서명 블록 (멀티라인) |

여러 명을 등록한 경우 `active` 플래그로 누가 발송 주체인지 표시합니다. 메일을 보낼 멤버를 바꾸려면 profile.json을 편집하거나 발송 직전 사용자가 다른 멤버를 지정.

---

## brand.*

| 변수 | 의미 |
|---|---|
| `brand.tagline` | 한 줄 자기소개 |
| `brand.tone` | 메일 톤 (`formal_business` / `friendly` / `professional`) |
| `brand.language` | 기본 언어 (`ko` / `en`) |
| `brand.industry` | 우리 산업 |
| `brand.differentiation` | 차별화 한 줄 |
| `brand.strengths` | 강점 배열 (메일 본문에서 첫 항목만 사용하거나 줄바꿈 join) |
| `brand.values` | 핵심 가치 배열 |
| `brand.targetCustomers` | 타깃 고객 배열 |

---

## client.* (Pluuug 의뢰/고객 데이터)

`render_template.py` 호출 시 `--context` JSON에 포함시킵니다. 주로 `GET /v1/inquiry/{id}` 응답에서 추출:

| 변수 | 의미 | 출처 필드 |
|---|---|---|
| `client.companyName` | 고객 회사명 | `client.companyName` |
| `client.contactName` | 담당자 이름 | `client.inCharge` |
| `client.email` | 담당자 이메일 | `client.email` |
| `client.phone` | 담당자 연락처 | `client.contact` |
| `client.inquiryName` | 의뢰명 | `name` |
| `client.inquiryId` | 의뢰 ID | `id` |
| `client.uniqueId` | 의뢰 고유번호 | `uniqueId` |
| `client.status` | 현재 영업 단계 | `status.title` |

---

## quote.*

quote-writing 출력에서 가져오는 견적 컨텍스트:

| 변수 | 의미 |
|---|---|
| `quote.total` | 합계 (부가세 포함 또는 별도 표기 포함) |
| `quote.validUntil` | 유효기간 (YYYY-MM-DD) |
| `quote.driveUrl` | Drive 링크 |
| `quote.filename` | 파일명 |
| `quote.summary` | 주요 항목 1-3줄 요약 |
| `quote.vatType` | 부가세 유형 (E/I/N) |

---

## meeting.* / contract.* / kickoff.* / prevEmail.* / request.* / hold.*

각 템플릿이 필요한 컨텍스트만 채우면 됩니다.

```
meeting.format / meeting.slot1 / meeting.slot2 / meeting.slot3 / meeting.link
contract.driveUrl / contract.filename / contract.signByDate / contract.startDate
kickoff.slot1 / kickoff.slot2 / kickoff.slot3 / kickoff.link
prevEmail.subject / prevEmail.sentDate
request.itemsList / request.replyDeadline
hold.heldSince / hold.elapsed
```

각 변수의 의미는 이름에서 명확. 발송 시 사용자가 슬롯·링크·기한을 알려주거나, 직전 데이터(`GET /v1/inquiry/{id}/email_history`)에서 자동 추출.

---

## 특수 매핑

| 변수 | 동작 |
|---|---|
| `team.pm` | `profile.json` team 배열에서 `role`이 "PM" 포함 멤버의 `name` 반환. 없으면 빈값. |
| `date` | 오늘 ISO 날짜 (KST). `--context`로 override 가능. |

---

## 사용 예시

### Python (영업 스킬에서 호출)

```python
import sys, json, subprocess
sys.path.insert(0, "skills/sales-setup/scripts")
from render_template import build_context, render

# 1. Pluuug 의뢰 데이터 가져오기
inquiry = json.loads(subprocess.check_output(
    ["skills/pluuug-api/scripts/pluuug.py", "GET", "/v1/inquiry/489749"]
))

# 2. client 네임스페이스 매핑
client_ctx = {
    "client": {
        "companyName": inquiry.get("client", {}).get("companyName", ""),
        "contactName": inquiry.get("client", {}).get("inCharge", ""),
        "email": inquiry.get("client", {}).get("email", ""),
        "inquiryName": inquiry.get("name", ""),
        "inquiryId": inquiry.get("id", ""),
        "status": inquiry.get("status", {}).get("title", "")
    }
}

# 3. 템플릿 렌더
with open("skills/email-send/templates/00-신규접수-첫응답.md") as f:
    tpl = f.read()
ctx = build_context(client_ctx)
rendered, missing = render(tpl, ctx, warn=True)
```

### 쉘 (one-shot)

```bash
# context JSON 직접 조립
echo '{"client":{"companyName":"(주)테스트","contactName":"홍길동","inquiryName":"GEO 대시보드"}}' | \
  skills/sales-setup/scripts/render_template.py \
    --template skills/email-send/templates/00-신규접수-첫응답.md \
    --context - \
    --warn
```

### Pluuug 응답을 직접 파이프

```bash
skills/pluuug-api/scripts/pluuug.py GET /v1/inquiry/489749 \
  | python3 -c '
import json, sys
d = json.load(sys.stdin)
c = d.get("client") or {}
print(json.dumps({"client": {
    "companyName": c.get("companyName",""),
    "contactName": c.get("inCharge",""),
    "email": c.get("email",""),
    "inquiryName": d.get("name",""),
    "inquiryId": d.get("id",""),
    "status": (d.get("status") or {}).get("title","")
}}, ensure_ascii=False))' \
  | skills/sales-setup/scripts/render_template.py \
      --template skills/email-send/templates/00-신규접수-첫응답.md \
      --context -
```

---

## 변수 추가 / 변경 시 체크리스트

1. 이 문서(`template_variables.md`)에 변수 정의 추가
2. 메일 템플릿 파일(`templates/*.md`)의 frontmatter `variables:` 목록에 등록
3. `render_template.py --check-template <path>` 로 frontmatter ↔ 본문 일치 확인
4. profile.json 스키마 변경이 필요하면 `profile_schema.md` 동시 갱신 + `schemaVersion` 증가 고려
