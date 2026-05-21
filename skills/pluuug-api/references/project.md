# 프로젝트 (Project)

### GET `/v1/project` — 프로젝트 목록
- operationId: `project_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `cursor` | string |  | Pagination을 위한 커서 |
| `end_date_end` | string (date) |  | 종료일 종료 (YYYY-MM-DD) |
| `end_date_start` | string (date) |  | 종료일 시작 (YYYY-MM-DD) |
| `is_hidden` | boolean |  | 숨김 여부 |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |
| `start_date_end` | string (date) |  | 시작일 종료 (YYYY-MM-DD) |
| `start_date_start` | string (date) |  | 시작일 시작 (YYYY-MM-DD) |
| `status` | string |  | 상태 (U: 예정됨, I: 진행 중, A: 추가 기간, E: 종료됨) |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### POST `/v1/project` — 프로젝트 생성
- operationId: `project_create`

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract` |  |  | 계약 |
| `title` | string | ✓ | 프로젝트 제목 |
| `status` | string |  | 상태 (U: 예정됨, I: 진행 중, A: 추가 기간, E: 종료됨)  * `U` - 예정됨 * `I` - 진행 중 * `A` - 추가 기간 * `E` - 종료됨 · enum: ['U', 'I', 'A', 'E'] |
| `symbolColor` | string |  | 상징색 |
| `startDate` | ['string', 'null'] (date) |  | 시작 날짜 |
| `endDate` | ['string', 'null'] (date) |  | 종료 날짜 |
| `isHidden` | boolean |  | 숨김 여부 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `contract` |  |  | 계약 |
| `title` | string | ✓ | 프로젝트 제목 |
| `status` | string |  | 상태 (U: 예정됨, I: 진행 중, A: 추가 기간, E: 종료됨)  * `U` - 예정됨 * `I` - 진행 중 * `A` - 추가 기간 * `E` - 종료됨 · enum: ['U', 'I', 'A', 'E'] |
| `symbolColor` | string |  | 상징색 |
| `startDate` | ['string', 'null'] (date) |  | 시작 날짜 |
| `endDate` | ['string', 'null'] (date) |  | 종료 날짜 |
| `actualEndDate` | ['string', 'null'] (date) | ✓ | 실제 종료 날짜 |
| `isHidden` | boolean |  | 숨김 여부 |
| `created` | string (date-time) | ✓ | 생성일시 |

### GET `/v1/project/{project_id}` — 프로젝트 상세
- operationId: `project_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `project_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `contract` |  |  | 계약 |
| `title` | string | ✓ | 프로젝트 제목 |
| `status` | string |  | 상태 (U: 예정됨, I: 진행 중, A: 추가 기간, E: 종료됨)  * `U` - 예정됨 * `I` - 진행 중 * `A` - 추가 기간 * `E` - 종료됨 · enum: ['U', 'I', 'A', 'E'] |
| `symbolColor` | string |  | 상징색 |
| `startDate` | ['string', 'null'] (date) |  | 시작 날짜 |
| `endDate` | ['string', 'null'] (date) |  | 종료 날짜 |
| `actualEndDate` | ['string', 'null'] (date) |  | 실제 종료 날짜 |
| `isHidden` | boolean |  | 숨김 여부 |
| `created` | string (date-time) | ✓ | 생성일시 |

### PATCH `/v1/project/{project_id}` — 프로젝트 부분 수정
- operationId: `project_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `project_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `contract` |  |  | 계약 |
| `title` | string |  | 프로젝트 제목 |
| `status` | string |  | 상태 (U: 예정됨, I: 진행 중, A: 추가 기간, E: 종료됨)  * `U` - 예정됨 * `I` - 진행 중 * `A` - 추가 기간 * `E` - 종료됨 · enum: ['U', 'I', 'A', 'E'] |
| `symbolColor` | string |  | 상징색 |
| `startDate` | ['string', 'null'] (date) |  | 시작 날짜 |
| `endDate` | ['string', 'null'] (date) |  | 종료 날짜 |
| `actualEndDate` | ['string', 'null'] (date) |  | 실제 종료 날짜 |
| `isHidden` | boolean |  | 숨김 여부 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `contract` |  |  | 계약 |
| `title` | string | ✓ | 프로젝트 제목 |
| `status` | string |  | 상태 (U: 예정됨, I: 진행 중, A: 추가 기간, E: 종료됨)  * `U` - 예정됨 * `I` - 진행 중 * `A` - 추가 기간 * `E` - 종료됨 · enum: ['U', 'I', 'A', 'E'] |
| `symbolColor` | string |  | 상징색 |
| `startDate` | ['string', 'null'] (date) |  | 시작 날짜 |
| `endDate` | ['string', 'null'] (date) |  | 종료 날짜 |
| `actualEndDate` | ['string', 'null'] (date) |  | 실제 종료 날짜 |
| `isHidden` | boolean |  | 숨김 여부 |
| `created` | string (date-time) | ✓ | 생성일시 |

### DELETE `/v1/project/{project_id}` — 프로젝트 삭제
- operationId: `project_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `project_id` | integer | ✓ |  |
