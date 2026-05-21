# 파일 업로드 Presigned URL

### POST `/v1/presigned` — Presigned URL 발급
- operationId: `presigned_create`

S3 업로드용 presigned PUT URL을 발급합니다.

**사용 흐름:**
1. 이 API를 호출하여 presigned URL과 path를 발급받습니다.
2. 응답의 `url`로 파일을 직접 업로드합니다. (PUT 요청, Content-Type: 파일 MIME 타입, Body: 파일 바이너리)
3. 응답의 `path`를 의뢰 생성/수정 API의 `file_set[].file` 필드에 전달합니다.

**제약 사항:**
- 허용 확장자: pdf, doc, docx, xls, xlsx, ppt, pptx, hwp, jpg, jpeg, png, gif, zip
- presigned URL 유효 시간: 60초
- 파일당 1회 호출 필요


**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `name` | string | ✓ | 파일명 (확장자 포함) |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `url` | string (uri) | ✓ | S3 업로드용 presigned PUT URL |
| `path` | string | ✓ | S3 object key (파일 등록 시 file 필드로 사용) |
