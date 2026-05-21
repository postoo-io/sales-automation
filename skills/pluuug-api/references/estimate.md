# 견적서 항목 템플릿 (Estimate Item)

### GET `/v1/estimate/item` — 견적서 항목 목록
- operationId: `estimate_item_list`

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

### POST `/v1/estimate/item` — 견적서 항목 생성
- operationId: `estimate_item_create`

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `title` | string | ✓ | 제목 |
| `unitCost` | string (decimal) | ✓ | 단위당 비용 |
| `unit` | string | ✓ | 단위 |
| `description` | ['string', 'null'] |  | 설명 |
| `classification` |  |  | 분류 |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `title` | string | ✓ | 제목 |
| `unitCost` | string (decimal) | ✓ | 단위당 비용 |
| `unit` | string | ✓ | 단위 |
| `description` | ['string', 'null'] |  | 설명 |
| `image` | string | ✓ |  |
| `classification` |  |  | 분류 |

### GET `/v1/estimate/item/{item_id}` — 견적서 항목 상세
- operationId: `estimate_item_retrieve`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `item_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `title` | string | ✓ | 제목 |
| `unitCost` | string (decimal) | ✓ | 단위당 비용 |
| `unit` | string | ✓ | 단위 |
| `image` | string | ✓ |  |
| `description` | ['string', 'null'] |  | 설명 |
| `classification` |  |  | 분류 |

### PATCH `/v1/estimate/item/{item_id}` — 견적서 항목 부분 수정
- operationId: `estimate_item_partial_update`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `item_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `title` | string |  | 제목 |
| `unitCost` | string (decimal) |  | 단위당 비용 |
| `unit` | string |  | 단위 |
| `description` | ['string', 'null'] |  | 설명 |
| `classification` |  |  | 분류 |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `title` | string | ✓ | 제목 |
| `unitCost` | string (decimal) | ✓ | 단위당 비용 |
| `unit` | string | ✓ | 단위 |
| `image` | string | ✓ |  |
| `description` | ['string', 'null'] |  | 설명 |
| `classification` |  |  | 분류 |

### DELETE `/v1/estimate/item/{item_id}` — 견적서 항목 삭제
- operationId: `estimate_item_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `item_id` | integer | ✓ |  |

### GET `/v1/estimate/item/classification` — 견적서 항목 분류 목록
- operationId: `estimate_item_classification_list`

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
