# 실무자 (Worker)

### GET `/v1/worker` — 실무자 목록
- operationId: `worker_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `cursor` | string |  | Pagination을 위한 커서 |
| `is_hidden` | boolean |  | 숨김 여부 |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |
| `position_id` | string |  | 직무 ID |
| `search` | string |  | 이름 검색 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### POST `/v1/worker` — 실무자 생성
- operationId: `worker_create`

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `name` | string | ✓ | 실무자 이름 |
| `position` |  |  | 직무 |
| `order` | integer |  | 순서 |
| `isHidden` | boolean |  | 숨김 여부 |
| `manMonthAmount` | integer |  | M/M 금액 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `name` | string | ✓ | 실무자 이름 |
| `position` |  |  | 직무 |
| `order` | integer |  | 순서 |
| `isHidden` | boolean |  | 숨김 여부 |
| `manMonthAmount` | integer |  | M/M 금액 |
| `created` | string (date-time) | ✓ | 생성일시 |

### GET `/v1/worker/{worker_id}` — 실무자 상세
- operationId: `worker_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `worker_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `name` | string | ✓ | 실무자 이름 |
| `position` |  |  | 직무 |
| `order` | integer |  | 순서 |
| `isHidden` | boolean |  | 숨김 여부 |
| `manMonthAmount` | integer |  | M/M 금액 |
| `created` | string (date-time) | ✓ | 생성일시 |

### PATCH `/v1/worker/{worker_id}` — 실무자 부분 수정
- operationId: `worker_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `worker_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `name` | string |  | 실무자 이름 |
| `position` |  |  | 직무 |
| `order` | integer |  | 순서 |
| `isHidden` | boolean |  | 숨김 여부 |
| `manMonthAmount` | integer |  | M/M 금액 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `name` | string | ✓ | 실무자 이름 |
| `position` |  |  | 직무 |
| `order` | integer |  | 순서 |
| `isHidden` | boolean |  | 숨김 여부 |
| `manMonthAmount` | integer |  | M/M 금액 |
| `created` | string (date-time) | ✓ | 생성일시 |

### DELETE `/v1/worker/{worker_id}` — 실무자 삭제
- operationId: `worker_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `worker_id` | integer | ✓ |  |
