# 폴더 (Folder)

### GET `/v1/folder` — 폴더 목록
- operationId: `folder_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `search` | string |  |  |

**Response 200**

array of:
| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `name` | string | ✓ | 폴더 이름 |
| `isDefault` | boolean | ✓ | 기본 폴더 여부 |
