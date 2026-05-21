# 커스텀 필드 (Field)

### GET `/v1/field` — 커스텀 필드 목록
- operationId: `field_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `category` | string |  | * `I` - 의뢰 * `C` - 고객 * `CO` - 계약 · enum: ['C', 'CO', 'I'] |
| `cursor` | string |  | Pagination을 위한 커서 |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |
