#!/usr/bin/env bash
# fetch_briefing.sh — 데일리 브리핑용 Pluuug API 병렬 수집 스크립트
# 출력: JSON manifest {"out_dir":"...","files":{...}}
#
# 사용법:
#   fetch_briefing.sh [today] [month_start] [month_end] [out_dir]
#
# 환경 변수 (필수):
#   PLUUUG_API_KEY      Pluuug API 키
#   PLUUUG_SECRET_KEY   HMAC 서명용 시크릿

set -euo pipefail

# ── 환경 변수 확인 ───────────────────────────────────────────────────────────
if [ -z "${PLUUUG_API_KEY:-}" ] || [ -z "${PLUUUG_SECRET_KEY:-}" ]; then
  echo "오류: PLUUUG_API_KEY 또는 PLUUUG_SECRET_KEY 환경 변수가 설정되어 있지 않습니다." >&2
  echo "설정 방법은 skills/pluuug-api/SKILL.md 또는 README.md 를 참고하세요." >&2
  exit 2
fi

# ── 날짜 계산 ────────────────────────────────────────────────────────────────
TODAY="${1:-$(date +%Y-%m-%d)}"
MONTH_START="${2:-$(date +%Y-%m-01)}"
# 월말: 다음 달 1일 - 1일
MONTH_END="${3:-$(date -v+1m -v1d -v-1d +%Y-%m-%d 2>/dev/null || date -d "$(date +%Y-%m-01) +1 month -1 day" +%Y-%m-%d)}"
OUT_DIR="${4:-$(mktemp -d)}"

YESTERDAY=$(date -j -v-1d -f "%Y-%m-%d" "$TODAY" +%Y-%m-%d 2>/dev/null \
  || date -d "$TODAY -1 day" +%Y-%m-%d)
TODAY_PLUS1=$(date -j -v+1d -f "%Y-%m-%d" "$TODAY" +%Y-%m-%d 2>/dev/null \
  || date -d "$TODAY +1 day" +%Y-%m-%d)
TODAY_PLUS7=$(date -j -v+7d -f "%Y-%m-%d" "$TODAY" +%Y-%m-%d 2>/dev/null \
  || date -d "$TODAY +7 days" +%Y-%m-%d)

# ── pluuug.py 경로 해결 ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUUUG_PY="$SCRIPT_DIR/../../pluuug-api/scripts/pluuug.py"
if [ ! -f "$PLUUUG_PY" ]; then
  echo "오류: pluuug.py 를 찾을 수 없습니다: $PLUUUG_PY" >&2
  exit 2
fi

# ── 개별 API 호출 함수 ───────────────────────────────────────────────────────
# 실패 시 {"_error":"..."} JSON 을 파일에 기록 (전체 스크립트 중단 없음)
call_api() {
  local out_file="$1"
  shift
  if ! python3 "$PLUUUG_PY" --raw "$@" > "$out_file" 2>/tmp/pluuug_err_$$; then
    local err_msg
    err_msg=$(cat /tmp/pluuug_err_$$ 2>/dev/null || echo "알 수 없는 오류")
    printf '{"_error":"%s"}' "$(echo "$err_msg" | sed 's/"/\\"/g' | tr -d '\n')" > "$out_file"
  fi
  rm -f /tmp/pluuug_err_$$
}

# ── 병렬 API 호출 ───────────────────────────────────────────────────────────
# A1. 오늘 신규 의뢰
call_api "$OUT_DIR/inquiry_today.json" \
  GET /v1/inquiry --query "inquiry_date_start=$TODAY" "inquiry_date_end=$TODAY" "page_size=50" &

# A2. 어제 신규 의뢰
call_api "$OUT_DIR/inquiry_yesterday.json" \
  GET /v1/inquiry --query "inquiry_date_start=$YESTERDAY" "inquiry_date_end=$YESTERDAY" "page_size=50" &

# A3. 의뢰 단계 메타
call_api "$OUT_DIR/inquiry_status.json" \
  GET /v1/inquiry/status &

# B1. D-day Todo (오늘까지 마감)
call_api "$OUT_DIR/todo_dday.json" \
  GET /v1/todo --query "is_complete=false" "due_date_end=$TODAY" "page_size=100" &

# B2. 이번 주 예정 Todo
call_api "$OUT_DIR/todo_week.json" \
  GET /v1/todo --query "is_complete=false" "due_date_start=$TODAY_PLUS1" "due_date_end=$TODAY_PLUS7" "page_size=100" &

# C1. 당월 계약
call_api "$OUT_DIR/contract_month.json" \
  GET /v1/contract --query "created_start=$MONTH_START" "created_end=$MONTH_END" "page_size=100" &

# D1. 당월 정산 완료 (settled_date 기준)
call_api "$OUT_DIR/settlement_settled.json" \
  GET /v1/settlement --query "settled_date_start=$MONTH_START" "settled_date_end=$MONTH_END" "page_size=100" &

# D2. 당월 정산 예정 (due_date 기준)
call_api "$OUT_DIR/settlement_due.json" \
  GET /v1/settlement --query "due_date_start=$MONTH_START" "due_date_end=$MONTH_END" "page_size=100" &

# D3. 정산 형태 메타
call_api "$OUT_DIR/settlement_type.json" \
  GET /v1/settlement/type &

# E1. 진행 중 프로젝트
call_api "$OUT_DIR/project_active.json" \
  GET /v1/project --query "status=I" "page_size=100" &

# 모든 백그라운드 작업 완료 대기
wait

# ── JSON manifest 출력 ───────────────────────────────────────────────────────
python3 - <<PYEOF
import json, os

out_dir = "$OUT_DIR"
files = {
    "inquiry_today":      "inquiry_today.json",
    "inquiry_yesterday":  "inquiry_yesterday.json",
    "inquiry_status":     "inquiry_status.json",
    "todo_dday":          "todo_dday.json",
    "todo_week":          "todo_week.json",
    "contract_month":     "contract_month.json",
    "settlement_settled": "settlement_settled.json",
    "settlement_due":     "settlement_due.json",
    "settlement_type":    "settlement_type.json",
    "project_active":     "project_active.json",
}
manifest = {
    "out_dir": out_dir,
    "dates": {
        "today":        "$TODAY",
        "yesterday":    "$YESTERDAY",
        "today_plus1":  "$TODAY_PLUS1",
        "today_plus7":  "$TODAY_PLUS7",
        "month_start":  "$MONTH_START",
        "month_end":    "$MONTH_END",
    },
    "files": {k: os.path.join(out_dir, v) for k, v in files.items()},
}
print(json.dumps(manifest, ensure_ascii=False))
PYEOF
