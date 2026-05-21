# 할 일 (Todo)

### GET `/v1/todo` — Todo 목록
- operationId: `todo_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `cursor` | string |  | Pagination을 위한 커서 |
| `due_date_end` | string (date) |  | 예정일 종료 (YYYY-MM-DD) |
| `due_date_start` | string (date) |  | 예정일 시작 (YYYY-MM-DD) |
| `inquiry_id` | number |  | 의뢰 ID |
| `is_complete` | boolean |  | 완료 여부 |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### POST `/v1/todo` — Todo 생성
- operationId: `todo_create`

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry` |  | ✓ | 의뢰 |
| `inCharge` |  |  | 담당자 |
| `type` | string | ✓ | 타입  * `M` - 미팅 * `CA` - 전화 * `MS` - 메시지 * `E` - 기타 · enum: ['M', 'CA', 'MS', 'E'] |
| `dueDate` | string (date) | ✓ | 예정일 |
| `dueTime` | ['string', 'null'] (time) |  | 예정 시간 |
| `action` | string | ✓ | 액션 |
| `actionHistory` | ['string', 'null'] |  | 액션 히스토리 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `inquiry` |  | ✓ | 의뢰 |
| `inCharge` |  |  | 담당자 |
| `type` | string | ✓ | 타입  * `M` - 미팅 * `CA` - 전화 * `MS` - 메시지 * `E` - 기타 · enum: ['M', 'CA', 'MS', 'E'] |
| `dueDate` | string (date) | ✓ | 예정일 |
| `dueTime` | ['string', 'null'] (time) |  | 예정 시간 |
| `action` | string | ✓ | 액션 |
| `isComplete` | boolean | ✓ | 완료 여부 |
| `completedAt` | ['string', 'null'] (date-time) | ✓ | 완료 일시 |
| `dDay` | integer | ✓ | D-Day |
| `created` | string (date-time) | ✓ | 생성일시 |

### GET `/v1/todo/{todo_id}` — Todo 상세
- operationId: `todo_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `todo_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `inquiry` |  | ✓ | 의뢰 |
| `inCharge` |  |  | 담당자 |
| `completedInCharge` |  |  | 완료한 담당자 |
| `type` | string | ✓ | 타입  * `M` - 미팅 * `CA` - 전화 * `MS` - 메시지 * `E` - 기타 · enum: ['M', 'CA', 'MS', 'E'] |
| `dueDate` | string (date) | ✓ | 예정일 |
| `dueTime` | ['string', 'null'] (time) |  | 예정 시간 |
| `action` | string | ✓ | 액션 |
| `actionHistory` | ['string', 'null'] |  | 액션 히스토리 |
| `isComplete` | boolean |  | 완료 여부 |
| `completedAt` | ['string', 'null'] (date-time) |  | 완료 일시 |
| `dDay` | integer | ✓ | D-Day |
| `created` | string (date-time) | ✓ | 생성일시 |

### PATCH `/v1/todo/{todo_id}` — Todo 부분 수정
- operationId: `todo_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `todo_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inCharge` |  |  | 담당자 |
| `completedInCharge` |  |  | 완료한 담당자 |
| `type` | string |  | 타입  * `M` - 미팅 * `CA` - 전화 * `MS` - 메시지 * `E` - 기타 · enum: ['M', 'CA', 'MS', 'E'] |
| `dueDate` | string (date) |  | 예정일 |
| `dueTime` | ['string', 'null'] (time) |  | 예정 시간 |
| `action` | string |  | 액션 |
| `actionHistory` | ['string', 'null'] |  | 액션 히스토리 |
| `isComplete` | boolean |  | 완료 여부 |
| `completedAt` | ['string', 'null'] (date-time) |  | 완료 일시 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `inquiry` |  | ✓ | 의뢰 |
| `inCharge` |  |  | 담당자 |
| `completedInCharge` |  |  | 완료한 담당자 |
| `type` | string | ✓ | 타입  * `M` - 미팅 * `CA` - 전화 * `MS` - 메시지 * `E` - 기타 · enum: ['M', 'CA', 'MS', 'E'] |
| `dueDate` | string (date) | ✓ | 예정일 |
| `dueTime` | ['string', 'null'] (time) |  | 예정 시간 |
| `action` | string | ✓ | 액션 |
| `actionHistory` | ['string', 'null'] |  | 액션 히스토리 |
| `isComplete` | boolean |  | 완료 여부 |
| `completedAt` | ['string', 'null'] (date-time) |  | 완료 일시 |
| `dDay` | integer | ✓ | D-Day |
| `created` | string (date-time) | ✓ | 생성일시 |

### DELETE `/v1/todo/{todo_id}` — Todo 삭제
- operationId: `todo_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `todo_id` | integer | ✓ |  |
