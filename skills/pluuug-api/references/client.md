# 고객 (Client)

### GET `/v1/client` — 고객 목록
- operationId: `client_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `created_end` | string (date) |  | 생성일 종료 (YYYY-MM-DD) |
| `created_start` | string (date) |  | 생성일 시작 (YYYY-MM-DD) |
| `cursor` | string |  | Pagination을 위한 커서 |
| `is_hidden` | boolean |  | 숨김 처리 여부 필터 (true: 숨김 항목만, false: 비숨김 항목만, 미전달: 전체) |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |
| `search` | string |  |  |
| `status_id` | string |  |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### POST `/v1/client` — 고객 생성
- operationId: `client_create`

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `status` |  |  | 고객 상태 (미입력 시 기본 상태) |
| `companyName` | string | ✓ | 회사명 |
| `inCharge` | ['string', 'null'] |  | 담당자 |
| `position` | ['string', 'null'] |  | 직책 |
| `contact` | ['string', 'null'] |  | 연락처 |
| `email` | ['string', 'null'] (email) |  | 이메일 |
| `content` | ['string', 'null'] |  | 메모 |
| `businessRegistrationNumber` | ['string', 'null'] |  | 사업자 등록번호 |
| `ceoName` | ['string', 'null'] |  | 대표자 |
| `companyAddress` | ['string', 'null'] |  | 소재지 |
| `companyDetailAddress` | ['string', 'null'] |  | 소재지 상세 |
| `businessType` | ['string', 'null'] |  | 업태 |
| `businessClass` | ['string', 'null'] |  | 종목 |
| `branchNumber` | ['string', 'null'] |  | 종사업장 번호 |
| `taxInvoiceEmail` | ['string', 'null'] |  | 세금계산서 전용 이메일 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `status` |  |  | 고객 상태 (미입력 시 기본 상태) |
| `companyName` | string | ✓ | 회사명 |
| `inCharge` | ['string', 'null'] |  | 담당자 |
| `position` | ['string', 'null'] |  | 직책 |
| `contact` | ['string', 'null'] |  | 연락처 |
| `email` | ['string', 'null'] (email) |  | 이메일 |
| `created` | string (date-time) | ✓ | 생성일시 |

### GET `/v1/client/status` — 고객 상태 목록
- operationId: `client_status_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `cursor` | string |  | Pagination을 위한 커서 |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### GET `/v1/client/{client_id}` — 고객 상세
- operationId: `client_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `client_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `status` |  |  | 고객 상태 |
| `companyName` | string | ✓ | 회사명 |
| `inCharge` | ['string', 'null'] |  | 담당자 |
| `position` | ['string', 'null'] |  | 직책 |
| `contact` | ['string', 'null'] |  | 연락처 |
| `email` | ['string', 'null'] (email) |  | 이메일 |
| `content` | ['string', 'null'] |  | 메모 |
| `businessRegistrationNumber` | ['string', 'null'] |  | 사업자 등록번호 |
| `ceoName` | ['string', 'null'] |  | 대표자 |
| `companyAddress` | ['string', 'null'] |  | 소재지 |
| `companyDetailAddress` | ['string', 'null'] |  | 소재지 상세 |
| `businessType` | ['string', 'null'] |  | 업태 |
| `businessClass` | ['string', 'null'] |  | 종목 |
| `branchNumber` | ['string', 'null'] |  | 종사업장 번호 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `taxInvoiceEmail` | ['string', 'null'] |  | 세금계산서 전용 이메일 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

### PATCH `/v1/client/{client_id}` — 고객 부분 수정
- operationId: `client_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `client_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `status` |  |  | 고객 상태 |
| `companyName` | string |  | 회사명 |
| `inCharge` | ['string', 'null'] |  | 담당자 |
| `position` | ['string', 'null'] |  | 직책 |
| `contact` | ['string', 'null'] |  | 연락처 |
| `email` | ['string', 'null'] (email) |  | 이메일 |
| `content` | ['string', 'null'] |  | 메모 |
| `businessRegistrationNumber` | ['string', 'null'] |  | 사업자 등록번호 |
| `ceoName` | ['string', 'null'] |  | 대표자 |
| `companyAddress` | ['string', 'null'] |  | 소재지 |
| `companyDetailAddress` | ['string', 'null'] |  | 소재지 상세 |
| `businessType` | ['string', 'null'] |  | 업태 |
| `businessClass` | ['string', 'null'] |  | 종목 |
| `branchNumber` | ['string', 'null'] |  | 종사업장 번호 |
| `taxInvoiceEmail` | ['string', 'null'] |  | 세금계산서 전용 이메일 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `status` |  |  | 고객 상태 |
| `companyName` | string | ✓ | 회사명 |
| `inCharge` | ['string', 'null'] |  | 담당자 |
| `position` | ['string', 'null'] |  | 직책 |
| `contact` | ['string', 'null'] |  | 연락처 |
| `email` | ['string', 'null'] (email) |  | 이메일 |
| `content` | ['string', 'null'] |  | 메모 |
| `businessRegistrationNumber` | ['string', 'null'] |  | 사업자 등록번호 |
| `ceoName` | ['string', 'null'] |  | 대표자 |
| `companyAddress` | ['string', 'null'] |  | 소재지 |
| `companyDetailAddress` | ['string', 'null'] |  | 소재지 상세 |
| `businessType` | ['string', 'null'] |  | 업태 |
| `businessClass` | ['string', 'null'] |  | 종목 |
| `branchNumber` | ['string', 'null'] |  | 종사업장 번호 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `taxInvoiceEmail` | ['string', 'null'] |  | 세금계산서 전용 이메일 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

### DELETE `/v1/client/{client_id}` — 고객 삭제
- operationId: `client_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `client_id` | integer | ✓ |  |
