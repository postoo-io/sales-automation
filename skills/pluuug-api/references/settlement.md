# 정산 (Settlement)

### GET `/v1/settlement` — 정산 목록
- operationId: `settlement_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | string |  |  |
| `created_end` | string (date) |  | 생성일 종료 (YYYY-MM-DD) |
| `created_start` | string (date) |  | 생성일 시작 (YYYY-MM-DD) |
| `cursor` | string |  | Pagination을 위한 커서 |
| `due_date_end` | string (date) |  | 정산 예정일 종료 (YYYY-MM-DD) |
| `due_date_start` | string (date) |  | 정산 예정일 시작 (YYYY-MM-DD) |
| `is_hidden` | boolean |  | 숨김 처리 여부 필터 (true: 숨김 항목만, false: 비숨김 항목만, 미전달: 전체) |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |
| `search` | string |  |  |
| `settled_date_end` | string (date) |  | 정산 완료일 종료 (YYYY-MM-DD) |
| `settled_date_start` | string (date) |  | 정산 완료일 시작 (YYYY-MM-DD) |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### POST `/v1/settlement` — 정산 생성
- operationId: `settlement_create`

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `title` | string | ✓ | 정산 제목 |
| `amount` | integer | ✓ | 정산 금액 |
| `additionalAmount` | integer | ✓ | 추가 금액 |
| `vat` | integer | ✓ | 부가세 |
| `settlementRound` | integer |  | 정산 차수 |
| `dueDate` | ['string', 'null'] (date) |  | 지급 예정일 |
| `settledDate` | ['string', 'null'] (date) |  | 지급 완료일 |
| `isTaxInvoiceIssued` | boolean |  | 세금 계산서 발행 여부 |
| `isTaxInvoiceNeeded` | boolean |  | 세금 계산서 발행 필요 여부 |
| `taxInvoiceIssuedDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 날짜 |
| `taxInvoiceIssueDueDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 예정 날짜 |
| `contract` |  | ✓ | 계약 |
| `type` |  | ✓ | 정산 형태 |
| `inChargeSet` | ['array', 'null'] |  | 담당자 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `title` | string | ✓ | 정산 제목 |
| `status` | string | ✓ | 정산 상태  * `C` - 정산 예정 * `D` - 정산 지연 * `S` - 정산 완료 * `P` - 정산 중단 · enum: ['C', 'D', 'S', 'P'] |
| `amount` | integer | ✓ | 정산 금액 |
| `additionalAmount` | integer | ✓ | 추가 금액 |
| `vat` | integer | ✓ | 부가세 |
| `dueDate` | ['string', 'null'] (date) |  | 지급 예정일 |
| `settledDate` | ['string', 'null'] (date) |  | 지급 완료일 |
| `typeAlias` | string | ✓ | 정산 형태 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `contract` |  | ✓ | 계약 |

### GET `/v1/settlement/type` — 정산 형태 목록
- operationId: `settlement_type_list`

**Response 200**

array of:
| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `baseType` | string | ✓ | 기본 정산 유형  * `INI` - 착수금 * `INS` - 중도금 * `BAL` - 잔금 * `COM` - 수수료 * `SUB` - 회차 * `SIN` - 단건 정산 * `ADD` - 추가 정산 * `OUT` - 미수 정산 · enum: ['INI', 'INS', 'BAL', 'COM', 'SUB', 'SIN', 'ADD', 'OUT'] |
| `category` | string | ✓ | 정산 방식  * `I` - 회차 정산형 * `S` - 정기 결제형 * `E` - 기타 · enum: ['I', 'S', 'E'] |
| `title` | string | ✓ | 제목 |
| `allowsMultipleRounds` | boolean | ✓ | 다중 차수 허용 여부 |

### GET `/v1/settlement/{settlement_id}` — 정산 상세
- operationId: `settlement_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `settlement_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `title` | string | ✓ | 정산 제목 |
| `status` | string | ✓ | 정산 상태  * `C` - 정산 예정 * `D` - 정산 지연 * `S` - 정산 완료 * `P` - 정산 중단 · enum: ['C', 'D', 'S', 'P'] |
| `amount` | integer | ✓ | 정산 금액 |
| `additionalAmount` | integer | ✓ | 추가 금액 |
| `vat` | integer | ✓ | 부가세 |
| `settlementRound` | integer | ✓ | 정산 차수 |
| `dueDate` | ['string', 'null'] (date) |  | 지급 예정일 |
| `settledDate` | ['string', 'null'] (date) |  | 지급 완료일 |
| `isTaxInvoiceIssued` | boolean | ✓ | 세금 계산서 발행 여부 |
| `isTaxInvoiceNeeded` | boolean | ✓ | 세금 계산서 발행 필요 여부 |
| `taxInvoiceIssuedDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 날짜 |
| `taxInvoiceIssueDueDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 예정 날짜 |
| `typeAlias` | string | ✓ | 정산 형태 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `contract` |  | ✓ | 계약 |
| `type` |  | ✓ | 정산 형태 |
| `inChargeSet` | ['array', 'null'] |  | 담당자 |

### PATCH `/v1/settlement/{settlement_id}` — 정산 부분 수정
- operationId: `settlement_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `settlement_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `title` | string |  | 정산 제목 |
| `amount` | integer |  | 정산 금액 |
| `additionalAmount` | integer |  | 추가 금액 |
| `vat` | integer |  | 부가세 |
| `dueDate` | ['string', 'null'] (date) |  | 지급 예정일 |
| `settledDate` | ['string', 'null'] (date) |  | 지급 완료일 |
| `isTaxInvoiceIssued` | boolean |  | 세금 계산서 발행 여부 |
| `isTaxInvoiceNeeded` | boolean |  | 세금 계산서 발행 필요 여부 |
| `taxInvoiceIssuedDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 날짜 |
| `taxInvoiceIssueDueDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 예정 날짜 |
| `inChargeSet` | ['array', 'null'] |  | 담당자 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `title` | string | ✓ | 정산 제목 |
| `status` | string | ✓ | 정산 상태  * `C` - 정산 예정 * `D` - 정산 지연 * `S` - 정산 완료 * `P` - 정산 중단 · enum: ['C', 'D', 'S', 'P'] |
| `amount` | integer | ✓ | 정산 금액 |
| `additionalAmount` | integer | ✓ | 추가 금액 |
| `vat` | integer | ✓ | 부가세 |
| `settlementRound` | integer | ✓ | 정산 차수 |
| `dueDate` | ['string', 'null'] (date) |  | 지급 예정일 |
| `settledDate` | ['string', 'null'] (date) |  | 지급 완료일 |
| `isTaxInvoiceIssued` | boolean | ✓ | 세금 계산서 발행 여부 |
| `isTaxInvoiceNeeded` | boolean | ✓ | 세금 계산서 발행 필요 여부 |
| `taxInvoiceIssuedDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 날짜 |
| `taxInvoiceIssueDueDate` | ['string', 'null'] (date) |  | 세금 계산서 발행 예정 날짜 |
| `typeAlias` | string | ✓ | 정산 형태 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `contract` |  | ✓ | 계약 |
| `type` |  | ✓ | 정산 형태 |
| `inChargeSet` | ['array', 'null'] |  | 담당자 |

### DELETE `/v1/settlement/{settlement_id}` — 정산 삭제
- operationId: `settlement_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `settlement_id` | integer | ✓ |  |

### GET `/v1/settlement/{settlement_id}/history` — 정산 히스토리 목록
- operationId: `settlement_history_list`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `settlement_id` | integer | ✓ |  |

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

### POST `/v1/settlement/{settlement_id}/history` — 정산 히스토리 생성
- operationId: `settlement_history_create`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `settlement_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `content` | string | ✓ | 내용 |
| `created` | string (date-time) |  | 생성시간 |
| `member` |  |  | 작성 멤버 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `content` | string | ✓ | 내용 |
| `created` | string (date-time) |  | 생성시간 |
| `member` |  |  | 작성 멤버 |

### GET `/v1/settlement/{settlement_id}/history/{history_id}` — 정산 히스토리 상세
- operationId: `settlement_history_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `history_id` | integer | ✓ |  |
| `settlement_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `content` | string | ✓ | 내용 |
| `created` | string (date-time) | ✓ | 생성시간 |
| `member` |  | ✓ | 작성 멤버 |

### PATCH `/v1/settlement/{settlement_id}/history/{history_id}` — 정산 히스토리 부분 수정
- operationId: `settlement_history_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `history_id` | integer | ✓ |  |
| `settlement_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `content` | string |  | 내용 |
| `created` | string (date-time) |  | 생성시간 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `content` | string | ✓ | 내용 |
| `created` | string (date-time) | ✓ | 생성시간 |
| `member` |  | ✓ | 작성 멤버 |

### DELETE `/v1/settlement/{settlement_id}/history/{history_id}` — 정산 히스토리 삭제
- operationId: `settlement_history_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `history_id` | integer | ✓ |  |
| `settlement_id` | integer | ✓ |  |
