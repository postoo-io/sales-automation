#!/usr/bin/env bash
# Pluuug 의뢰 컨텍스트 수집 스크립트
# 사용법: collect_context.sh <inquiry_id> [--out-dir <path>] [--page-size <N>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUUUG="$SCRIPT_DIR/../../pluuug-api/scripts/pluuug.py"

# ── 인수 파싱 ──────────────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
  echo "사용법: $(basename "$0") <inquiry_id> [--out-dir <path>] [--page-size <N>]" >&2
  exit 1
fi

INQUIRY_ID="$1"
shift

OUT_DIR=""
PAGE_SIZE=20

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir)   OUT_DIR="$2";   shift 2 ;;
    --page-size) PAGE_SIZE="$2"; shift 2 ;;
    *) echo "알 수 없는 옵션: $1" >&2; exit 1 ;;
  esac
done

# 출력 디렉터리 결정
if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$(mktemp -d)"
fi

# ── 헬퍼: 실패해도 오류 JSON 기록 ──────────────────────────────────────────────
pluuug_get() {
  local endpoint="$1"
  local out_file="$2"
  if ! python3 "$PLUUUG" GET "$endpoint" > "$OUT_DIR/$out_file" 2>/dev/null; then
    echo "{\"_error\": \"GET $endpoint 호출 실패\"}" > "$OUT_DIR/$out_file"
  fi
}

# ── 1단계: 병렬 호출 ───────────────────────────────────────────────────────────
pluuug_get "/v1/inquiry/${INQUIRY_ID}" "inquiry.json" &
pluuug_get "/v1/inquiry/${INQUIRY_ID}/text_history?page_size=${PAGE_SIZE}" "text_history.json" &
pluuug_get "/v1/inquiry/${INQUIRY_ID}/email_history?page_size=${PAGE_SIZE}" "email_history.json" &
pluuug_get "/v1/inquiry/${INQUIRY_ID}/email_reply_history?page_size=${PAGE_SIZE}" "email_reply_history.json" &
pluuug_get "/v1/inquiry/${INQUIRY_ID}/status_history?page_size=${PAGE_SIZE}" "status_history.json" &
pluuug_get "/v1/todo?inquiry_id=${INQUIRY_ID}&is_complete=false&page_size=50" "todos.json" &
pluuug_get "/v1/contract?inquiry_id=${INQUIRY_ID}&page_size=20" "contracts.json" &

# 모든 병렬 작업 완료 대기
wait

# ── 2단계: inquiry.json 에서 client.id 추출 후 순차 호출 ──────────────────────
CLIENT_ID=""
if [[ -f "$OUT_DIR/inquiry.json" ]]; then
  CLIENT_ID="$(python3 -c "
import json, sys
try:
    data = json.load(open('$OUT_DIR/inquiry.json'))
    cid = data.get('client', {}).get('id') or data.get('client_id')
    print(cid if cid is not None else '')
except Exception:
    print('')
" 2>/dev/null)"
fi

if [[ -n "$CLIENT_ID" ]]; then
  pluuug_get "/v1/client/${CLIENT_ID}" "client.json"
else
  echo "{\"_error\": \"client.id를 inquiry.json에서 추출하지 못했습니다\"}" > "$OUT_DIR/client.json"
fi

# ── 3단계: contracts.json 에서 project_id 추출 후 순차 호출 ───────────────────
PROJECT_ID=""
if [[ -f "$OUT_DIR/contracts.json" ]]; then
  PROJECT_ID="$(python3 -c "
import json, sys
try:
    data = json.load(open('$OUT_DIR/contracts.json'))
    results = data.get('results', data) if isinstance(data, dict) else data
    if isinstance(results, list):
        for item in results:
            pid = (item.get('project') or {}).get('id') if isinstance(item.get('project'), dict) else item.get('project_id')
            if pid:
                print(pid)
                sys.exit(0)
    print('')
except Exception:
    print('')
" 2>/dev/null)"
fi

if [[ -n "$PROJECT_ID" ]]; then
  pluuug_get "/v1/project/${PROJECT_ID}" "project.json"
fi

# ── 4단계: manifest 출력 ───────────────────────────────────────────────────────
FILES_JSON="{"
FILES_JSON+="\"inquiry\":\"inquiry.json\","
FILES_JSON+="\"client\":\"client.json\","
FILES_JSON+="\"text_history\":\"text_history.json\","
FILES_JSON+="\"email_history\":\"email_history.json\","
FILES_JSON+="\"email_reply_history\":\"email_reply_history.json\","
FILES_JSON+="\"status_history\":\"status_history.json\","
FILES_JSON+="\"todos\":\"todos.json\","
FILES_JSON+="\"contracts\":\"contracts.json\""
if [[ -n "$PROJECT_ID" ]]; then
  FILES_JSON+=",\"project\":\"project.json\""
fi
FILES_JSON+="}"

python3 -c "
import json
manifest = {
    'out_dir': '$OUT_DIR',
    'inquiry_id': $INQUIRY_ID,
    'client_id': '$CLIENT_ID' if '$CLIENT_ID' else None,
    'files': $FILES_JSON
}
print(json.dumps(manifest, ensure_ascii=False, indent=2))
"
