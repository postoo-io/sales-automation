# 의뢰/리드 (Inquiry)

### GET `/v1/inquiry` — 의뢰 목록
- operationId: `inquiry_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `created_end` | string (date) |  | 생성일 종료 (YYYY-MM-DD) |
| `created_start` | string (date) |  | 생성일 시작 (YYYY-MM-DD) |
| `cursor` | string |  | Pagination을 위한 커서 |
| `folder_id` | string |  |  |
| `inquiry_date_end` | string (date) |  | 문의일 종료 (YYYY-MM-DD) |
| `inquiry_date_start` | string (date) |  | 문의일 시작 (YYYY-MM-DD) |
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

### POST `/v1/inquiry` — 의뢰 생성
- operationId: `inquiry_create`

새 의뢰를 생성합니다.


**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `status` |  |  | 의뢰 상태 (미입력 시 기본 폴더의 기본 상태) |
| `client` |  |  | 고객 |
| `contract` |  |  | 계약 |
| `name` | ['string', 'null'] |  | 의뢰 이름 (미입력 시 '의뢰 제목') |
| `content` | ['string', 'null'] |  | 의뢰 내용 |
| `estimate` | ['string', 'null'] (decimal) |  | 예상 견적 |
| `inquiryDate` | ['string', 'null'] (date) |  | 문의 일시 (미입력 시 오늘 날짜) |
| `funnel` |  |  | 유입 경로 |
| `workSet` | ['array', 'null'] |  | 의뢰 업무 |
| `inChargeSet` | ['array', 'null'] |  | 영업 담당자 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |
| `fileLinkSet` | ['array', 'null'] |  | 링크 첨부 |
| `fileSet` | ['array', 'null'] |  | 파일 첨부 (presigned API 응답의 path와 원본 파일명을 전달). 최대 30개. |

**Response 201**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `uniqueId` | ['string', 'null'] | ✓ | 의뢰 고유번호 |
| `status` |  |  | 의뢰 상태 (미입력 시 기본 폴더의 기본 상태) |
| `client` |  |  | 고객 |
| `contract` |  |  | 계약 |
| `name` | ['string', 'null'] |  | 의뢰 이름 (미입력 시 '의뢰 제목') |
| `estimate` | ['string', 'null'] (decimal) |  | 예상 견적 |
| `inquiryDate` | ['string', 'null'] (date) |  | 문의 일시 (미입력 시 오늘 날짜) |
| `created` | string (date-time) | ✓ | 생성일시 |

### GET `/v1/inquiry/work` — 의뢰 업무 목록
- operationId: `inquiry_work_list`

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

### GET `/v1/inquiry/status` — 의뢰 상태 목록
- operationId: `inquiry_status_list`

**Query 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `cursor` | string |  | Pagination을 위한 커서 |
| `folder_id` | string |  |  |
| `page_size` | integer |  | 한번에 조회할 데이터의 개수 (limit) |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `next` | ['string', 'null'] (uri) |  |  |
| `previous` | ['string', 'null'] (uri) |  |  |
| `results` | array<object> | ✓ |  |

### GET `/v1/inquiry/{inquiry_id}` — 의뢰 상세
- operationId: `inquiry_retrieve`

의뢰 상세 정보를 조회합니다. `file_set`에 첨부 파일 목록이 presigned 다운로드 URL과 함께 포함됩니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `uniqueId` | ['string', 'null'] | ✓ | 의뢰 고유번호 |
| `status` |  |  | 의뢰 상태 |
| `client` |  |  | 고객 |
| `contract` |  |  | 계약 |
| `name` | string | ✓ | 의뢰 이름 |
| `content` | ['string', 'null'] |  | 의뢰 내용 |
| `estimate` | ['string', 'null'] (decimal) |  | 예상 견적 |
| `inquiryDate` | string (date) | ✓ | 문의 일시 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `funnel` |  |  | 유입 경로 |
| `workSet` | ['array', 'null'] |  | 의뢰 업무 |
| `inChargeSet` | ['array', 'null'] |  | 영업 담당자 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |
| `fileLinkSet` | ['array', 'null'] |  | 링크 첨부 |
| `fileSet` | array<object> | ✓ | 첨부 파일 (presigned 다운로드 URL 포함) |

### PATCH `/v1/inquiry/{inquiry_id}` — 의뢰 부분 수정
- operationId: `inquiry_partial_update`

의뢰 정보를 부분 수정합니다.

**파일 추가:** `file_set`에 presigned API로 발급받은 name과 path를 전달하면 기존 파일은 유지한 채 새 파일만 추가됩니다 (append). 파일 삭제는 별도의 DELETE API를 사용하세요. 최대 30개까지 첨부 가능합니다 (기존 + 추가분 합산).


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

**Request body** (JSON)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `status` |  |  | 의뢰 상태 |
| `client` |  |  | 고객 |
| `contract` |  |  | 계약 |
| `name` | string |  | 의뢰 이름 |
| `content` | ['string', 'null'] |  | 의뢰 내용 |
| `estimate` | ['string', 'null'] (decimal) |  | 예상 견적 |
| `inquiryDate` | string (date) |  | 문의 일시 |
| `funnel` |  |  | 유입 경로 |
| `workSet` | ['array', 'null'] |  | 의뢰 업무 |
| `inChargeSet` | ['array', 'null'] |  | 영업 담당자 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |
| `fileLinkSet` | ['array', 'null'] |  | 링크 첨부 |
| `fileSet` | ['array', 'null'] |  | 파일 추가 (기존 파일 유지, 새 파일만 추가). 삭제는 DELETE /v1/inquiry/{inquiry_id}/file/{file_id} 사용. 최대 30개 (합산). |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `uniqueId` | ['string', 'null'] | ✓ | 의뢰 고유번호 |
| `status` |  |  | 의뢰 상태 |
| `client` |  |  | 고객 |
| `contract` |  |  | 계약 |
| `name` | string | ✓ | 의뢰 이름 |
| `content` | ['string', 'null'] |  | 의뢰 내용 |
| `estimate` | ['string', 'null'] (decimal) |  | 예상 견적 |
| `inquiryDate` | string (date) | ✓ | 문의 일시 |
| `created` | string (date-time) | ✓ | 생성일시 |
| `funnel` |  |  | 유입 경로 |
| `workSet` | ['array', 'null'] |  | 의뢰 업무 |
| `inChargeSet` | ['array', 'null'] |  | 영업 담당자 |
| `fieldSet` | ['array', 'null'] |  | 커스텀 필드 |
| `fileLinkSet` | ['array', 'null'] |  | 링크 첨부 |
| `fileSet` | array<object> | ✓ | 첨부 파일 (presigned 다운로드 URL 포함) |

### DELETE `/v1/inquiry/{inquiry_id}` — 의뢰 삭제
- operationId: `inquiry_destroy`

**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

### GET `/v1/inquiry/{inquiry_id}/text_history` — 의뢰 텍스트 히스토리 목록
- operationId: `inquiry_text_history_list`

의뢰의 텍스트 히스토리를 조회합니다. 내용, 작성 멤버, 생성 시간 정보를 포함합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

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

### POST `/v1/inquiry/{inquiry_id}/text_history` — 의뢰 텍스트 히스토리 생성
- operationId: `inquiry_text_history_create`

의뢰에 새로운 텍스트 히스토리를 추가합니다. 담당자에게 알림이 발송됩니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

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

### GET `/v1/inquiry/{inquiry_id}/email_history` — 의뢰 이메일 발신 이력 목록
- operationId: `inquiry_email_history_list`

의뢰에서 발송한 이메일 이력을 조회합니다. 수신자(to), 참조(cc), 발송 상태(S:발송, D:임시저장, C:발송예약, F:실패) 정보를 포함합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

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

### DELETE `/v1/inquiry/{inquiry_id}/file/{file_id}` — 의뢰 파일 삭제
- operationId: `inquiry_file_destroy`

의뢰에 첨부된 특정 파일을 삭제합니다. 삭제할 파일의 ID는 의뢰 상세 조회 API의 `file_set[].id`에서 확인할 수 있습니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `file_id` | integer | ✓ |  |
| `inquiry_id` | integer | ✓ |  |

### GET `/v1/inquiry/{inquiry_id}/folder_history` — 의뢰 폴더 이동 이력 목록
- operationId: `inquiry_folder_history_list`

의뢰의 폴더 이동 이력을 조회합니다. 이전 폴더명, 현재 폴더명, 변경한 멤버 정보를 포함합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

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

### GET `/v1/inquiry/{inquiry_id}/status_history` — 의뢰 상태 변경 이력 목록
- operationId: `inquiry_status_history_list`

의뢰의 상태 변경 이력을 조회합니다. 변경된 상태명, 상징 색, 변경한 멤버 정보를 포함합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

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

### GET `/v1/inquiry/{inquiry_id}/submit_history` — 의뢰 폼 제출 이력 목록
- operationId: `inquiry_submit_history_list`

의뢰에 연결된 웹 폼 제출 이력을 조회합니다. 제출된 폼의 ID와 제목 정보를 포함합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

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

### GET `/v1/inquiry/{inquiry_id}/email_reply_history` — 의뢰 이메일 수신 이력 목록
- operationId: `inquiry_email_reply_history_list`

의뢰에 대해 수신된 답장 이메일 이력을 조회합니다. 발신자(from), 수신자(to), 참조(cc), 읽지 않음 여부(is_unread) 정보를 포함합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_id` | integer | ✓ |  |

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

### GET `/v1/inquiry/{inquiry_id}/text_history/{history_id}` — 의뢰 텍스트 히스토리 상세
- operationId: `inquiry_text_history_retrieve`

특정 텍스트 히스토리의 상세 정보를 조회합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `history_id` | integer | ✓ |  |
| `inquiry_id` | integer | ✓ |  |

**Response 200**

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | integer | ✓ |  |
| `content` | string | ✓ | 내용 |
| `created` | string (date-time) | ✓ | 생성시간 |
| `member` |  | ✓ | 작성 멤버 |

### PATCH `/v1/inquiry/{inquiry_id}/text_history/{history_id}` — 의뢰 텍스트 히스토리 부분 수정
- operationId: `inquiry_text_history_partial_update`

텍스트 히스토리의 내용을 수정합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `history_id` | integer | ✓ |  |
| `inquiry_id` | integer | ✓ |  |

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

### DELETE `/v1/inquiry/{inquiry_id}/text_history/{history_id}` — 의뢰 텍스트 히스토리 삭제
- operationId: `inquiry_text_history_destroy`

텍스트 히스토리를 삭제합니다.


**Path 파라미터**

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `history_id` | integer | ✓ |  |
| `inquiry_id` | integer | ✓ |  |
