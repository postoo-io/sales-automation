# 계약 (Contract)

### GET `/v1/contract` — 계약 목록
- operationId: `contract_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `client_id` | string |  |  |
| `created_end` | string (date) |  | 생성일 종료 (YYYY-MM-DD) |
| `created_start` | string (date) |  | 생성일 시작 (YYYY-MM-DD) |
| `cursor` | string |  | Pagination을 위한 커서 |
| `end_date_from` | string (date) |  | 종료일 시작 (YYYY-MM-DD) |
| `end_date_to` | string (date) |  | 종료일 종료 (YYYY-MM-DD) |
| `inquiry_id` | string |  |  |
| `is_hidden` | boolean |  | 숨김 처리 여부 필터 (true: 숨김 항목만, false: 비숨김 항목만, 미전달: 전체) |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |
| `search` | string |  |  |
| `start_date_from` | string (date) |  | 착수일 시작 (YYYY-MM-DD) |
| `start_date_to` | string (date) |  | 착수일 종료 (YYYY-MM-DD) |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### POST `/v1/contract` — 계약 생성
- operationId: `contract_create`

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contractNumber` | ['string', 'null'] |  | 계약 번호 |
| `title` | string | ✓ | 계약 제목 |
| `amount` | integer | ✓ | 계약 금액 |
| `type` | string | ✓ | 계약 타입  * `I` - 회차 정산형 * `S` - 정기 결제형 * `G` - 단건 정산 · enum: ['I', 'S', 'G'] |
| `startDate` | ['string', 'null'] (date) |  | 계약 착수일 |
| `endDate` | ['string', 'null'] (date) |  | 계약 종료일 |
| `vatType` | string |  | 부가세 타입  * `E` - 부가세 별도 * `I` - 부가세 포함 * `N` - 부가세 없음 · enum: ['E', 'I', 'N'] |
| `settlementFrequency` | integer |  | 결제 주기 빈도(정기 결제형 계약에서만 사용) |
| `settlementCycle` | string |  | 결제 주기(정기 결제형 계약에서만 사용)  * `W` - 주 * `M` - 개월 · enum: ['W', 'M'] |
| `settlementDay` | integer |  | **결제일** (정기 결제형 계약에서만 사용)  **주 단위 계약**일 경우, 요일에 해당하는 숫자를 입력하세요: - 일요일: `0` - 월요일: `1` - 화요일: `2` - 수요일: `3` - 목요일: `4` - 금요일: `5` - 토요일: `6`  **월 단위 계약**일 경우, 1일부터 30일 중 원하는 날짜를 숫자로 입력하세요: - 예: 매월 10일 결제 → `10` - 최소값: `1`, 최대값: `30`  ⚠️ * 주의: 월 단위에서 31일은 허용되지 않습니다.*  |
| `inquiry` |  |  | 의뢰 |
| `client` |  |  | 고객 |
| `categorySet` | ['array', 'null'] |  | 카테고리 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `contractNumber` | ['string', 'null'] |  | 계약 번호 |
| `title` | string | ✓ | 계약 제목 |
| `amount` | integer | ✓ | 계약 금액 |
| `type` | string | ✓ | 계약 타입  * `I` - 회차 정산형 * `S` - 정기 결제형 * `G` - 단건 정산 · enum: ['I', 'S', 'G'] |
| `status` | string | ✓ | 계약 상태  * `P` - 계약 준비 중 * `I` - 정산 진행 중 * `C` - 계약 종료 * `T` - 계약 중단 · enum: ['P', 'I', 'C', 'T'] |
| `startDate` | ['string', 'null'] (date) |  | 계약 착수일 |
| `endDate` | ['string', 'null'] (date) |  | 계약 종료일 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `inquiry` |  |  | 의뢰 |
| `client` |  |  | 고객 |
| `categorySet` | ['array', 'null'] |  | 카테고리 |

### GET `/v1/contract/category` — 계약 카테고리 목록
- operationId: `contract_category_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `cursor` | string |  | Pagination을 위한 커서 |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |
| `search` | string |  |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### GET `/v1/contract/{contract_id}` — 계약 상세
- operationId: `contract_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `contractNumber` | ['string', 'null'] |  | 계약 번호 |
| `title` | string | ✓ | 계약 제목 |
| `amount` | integer | ✓ | 계약 금액 |
| `type` | string | ✓ | 계약 타입  * `I` - 회차 정산형 * `S` - 정기 결제형 * `G` - 단건 정산 · enum: ['I', 'S', 'G'] |
| `status` | string | ✓ | 계약 상태  * `P` - 계약 준비 중 * `I` - 정산 진행 중 * `C` - 계약 종료 * `T` - 계약 중단 · enum: ['P', 'I', 'C', 'T'] |
| `startDate` | ['string', 'null'] (date) |  | 계약 착수일 |
| `endDate` | ['string', 'null'] (date) |  | 계약 종료일 |
| `vatType` | string |  | 부가세 타입  * `E` - 부가세 별도 * `I` - 부가세 포함 * `N` - 부가세 없음 · enum: ['E', 'I', 'N'] |
| `settlementFrequency` | integer |  | 결제 주기 빈도(정기 결제형 계약에서만 사용) |
| `settlementCycle` | string |  | 결제 주기(정기 결제형 계약에서만 사용)  * `W` - 주 * `M` - 개월 · enum: ['W', 'M'] |
| `settlementDay` | integer |  | **결제일** (정기 결제형 계약에서만 사용)  **주 단위 계약**일 경우, 요일에 해당하는 숫자를 입력하세요: - 일요일: `0` - 월요일: `1` - 화요일: `2` - 수요일: `3` - 목요일: `4` - 금요일: `5` - 토요일: `6`  **월 단위 계약**일 경우, 1일부터 30일 중 원하는 날짜를 숫자로 입력하세요: - 예: 매월 10일 결제 → `10` - 최소값: `1`, 최대값: `30`  ⚠️ * 주의: 월 단위에서 31일은 허용되지 않습니다.*  |
| `created` | string (date-time) | ✓ | 생성일시 |
| `inquiry` |  |  | 의뢰 |
| `client` |  |  | 고객 |
| `categorySet` | ['array', 'null'] |  | 카테고리 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

### PATCH `/v1/contract/{contract_id}` — 계약 부분 수정
- operationId: `contract_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contractNumber` | ['string', 'null'] |  | 계약 번호 |
| `title` | string |  | 계약 제목 |
| `amount` | integer |  | 계약 금액 |
| `type` | string |  | 계약 타입  * `I` - 회차 정산형 * `S` - 정기 결제형 * `G` - 단건 정산 · enum: ['I', 'S', 'G'] |
| `startDate` | ['string', 'null'] (date) |  | 계약 착수일 |
| `endDate` | ['string', 'null'] (date) |  | 계약 종료일 |
| `vatType` | string |  | 부가세 타입  * `E` - 부가세 별도 * `I` - 부가세 포함 * `N` - 부가세 없음 · enum: ['E', 'I', 'N'] |
| `settlementFrequency` | integer |  | 결제 주기 빈도(정기 결제형 계약에서만 사용) |
| `settlementCycle` | string |  | 결제 주기(정기 결제형 계약에서만 사용)  * `W` - 주 * `M` - 개월 · enum: ['W', 'M'] |
| `settlementDay` | integer |  | **결제일** (정기 결제형 계약에서만 사용)  **주 단위 계약**일 경우, 요일에 해당하는 숫자를 입력하세요: - 일요일: `0` - 월요일: `1` - 화요일: `2` - 수요일: `3` - 목요일: `4` - 금요일: `5` - 토요일: `6`  **월 단위 계약**일 경우, 1일부터 30일 중 원하는 날짜를 숫자로 입력하세요: - 예: 매월 10일 결제 → `10` - 최소값: `1`, 최대값: `30`  ⚠️ * 주의: 월 단위에서 31일은 허용되지 않습니다.*  |
| `inquiry` |  |  | 의뢰 |
| `client` |  |  | 고객 |
| `categorySet` | ['array', 'null'] |  | 카테고리 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `contractNumber` | ['string', 'null'] |  | 계약 번호 |
| `title` | string | ✓ | 계약 제목 |
| `amount` | integer | ✓ | 계약 금액 |
| `type` | string | ✓ | 계약 타입  * `I` - 회차 정산형 * `S` - 정기 결제형 * `G` - 단건 정산 · enum: ['I', 'S', 'G'] |
| `status` | string | ✓ | 계약 상태  * `P` - 계약 준비 중 * `I` - 정산 진행 중 * `C` - 계약 종료 * `T` - 계약 중단 · enum: ['P', 'I', 'C', 'T'] |
| `startDate` | ['string', 'null'] (date) |  | 계약 착수일 |
| `endDate` | ['string', 'null'] (date) |  | 계약 종료일 |
| `vatType` | string |  | 부가세 타입  * `E` - 부가세 별도 * `I` - 부가세 포함 * `N` - 부가세 없음 · enum: ['E', 'I', 'N'] |
| `settlementFrequency` | integer |  | 결제 주기 빈도(정기 결제형 계약에서만 사용) |
| `settlementCycle` | string |  | 결제 주기(정기 결제형 계약에서만 사용)  * `W` - 주 * `M` - 개월 · enum: ['W', 'M'] |
| `settlementDay` | integer |  | **결제일** (정기 결제형 계약에서만 사용)  **주 단위 계약**일 경우, 요일에 해당하는 숫자를 입력하세요: - 일요일: `0` - 월요일: `1` - 화요일: `2` - 수요일: `3` - 목요일: `4` - 금요일: `5` - 토요일: `6`  **월 단위 계약**일 경우, 1일부터 30일 중 원하는 날짜를 숫자로 입력하세요: - 예: 매월 10일 결제 → `10` - 최소값: `1`, 최대값: `30`  ⚠️ * 주의: 월 단위에서 31일은 허용되지 않습니다.*  |
| `created` | string (date-time) | ✓ | 생성일시 |
| `inquiry` |  |  | 의뢰 |
| `client` |  |  | 고객 |
| `categorySet` | ['array', 'null'] |  | 카테고리 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |

### DELETE `/v1/contract/{contract_id}` — 계약 삭제
- operationId: `contract_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |

### GET `/v1/contract/{contract_id}/history` — 계약 히스토리 목록
- operationId: `contract_history_list`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |

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

### POST `/v1/contract/{contract_id}/history` — 계약 히스토리 생성
- operationId: `contract_history_create`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |

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

### GET `/v1/contract/{contract_id}/history/{history_id}` — 계약 히스토리 상세
- operationId: `contract_history_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |
| `history_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `content` | string | ✓ | 내용 |
| `created` | string (date-time) | ✓ | 생성시간 |
| `member` |  | ✓ | 작성 멤버 |

### PATCH `/v1/contract/{contract_id}/history/{history_id}` — 계약 히스토리 부분 수정
- operationId: `contract_history_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |
| `history_id` | integer | ✓ |  |

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

### DELETE `/v1/contract/{contract_id}/history/{history_id}` — 계약 히스토리 삭제
- operationId: `contract_history_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract_id` | integer | ✓ |  |
| `history_id` | integer | ✓ |  |
