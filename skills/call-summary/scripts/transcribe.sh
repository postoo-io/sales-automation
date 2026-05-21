#!/usr/bin/env bash
# transcribe.sh — 로컬 Whisper를 이용해 오디오 파일을 텍스트로 변환합니다.
# 사용법: ./transcribe.sh <오디오파일경로>
# 출력: 트랜스크립트 텍스트를 stdout으로 출력
# 보안: 오디오 파일을 외부 클라우드 서비스로 자동 업로드하지 않습니다.

set -euo pipefail

# ── 인자 검사 ──────────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
  echo "사용법: $0 <오디오파일경로>" >&2
  exit 1
fi

AUDIO_FILE="$1"

if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "오류: 파일을 찾을 수 없습니다 — $AUDIO_FILE" >&2
  exit 1
fi

# ── 확장자 검사 (허용: mp3 m4a wav flac aac ogg) ───────────────────────────
EXT="${AUDIO_FILE##*.}"
EXT_LOWER="${EXT,,}"

case "$EXT_LOWER" in
  mp3|m4a|wav|flac|aac|ogg)
    # 지원되는 포맷
    ;;
  *)
    echo "오류: 지원하지 않는 파일 형식입니다 — .$EXT" >&2
    echo "지원 형식: mp3, m4a, wav, flac, aac, ogg" >&2
    exit 1
    ;;
esac

# ── Whisper 설치 여부 확인 ──────────────────────────────────────────────────
if command -v whisper &>/dev/null; then
  # Whisper 발견 — 로컬에서만 변환 (클라우드 업로드 없음)
  TMP_DIR="/tmp/transcribe-$$"
  mkdir -p "$TMP_DIR"

  echo "Whisper로 변환 중: $AUDIO_FILE" >&2
  echo "출력 디렉터리: $TMP_DIR" >&2

  whisper "$AUDIO_FILE" \
    --model small \
    --language ko \
    --output_format txt \
    --output_dir "$TMP_DIR"

  # 생성된 .txt 파일명 추출 (확장자 제거 후 .txt)
  BASENAME="$(basename "$AUDIO_FILE")"
  TXT_FILE="$TMP_DIR/${BASENAME%.*}.txt"

  if [[ ! -f "$TXT_FILE" ]]; then
    echo "오류: Whisper가 텍스트 파일을 생성하지 못했습니다. $TMP_DIR 를 직접 확인하세요." >&2
    exit 1
  fi

  echo "원본 텍스트 파일 경로: $TXT_FILE" >&2

  # 트랜스크립트를 stdout으로 출력
  cat "$TXT_FILE"

else
  # Whisper 미설치 — 설치 방법 및 대안 안내
  echo "" >&2
  echo "────────────────────────────────────────────────────────" >&2
  echo "Whisper가 설치되어 있지 않습니다." >&2
  echo "" >&2
  echo "▶ 설치 방법:" >&2
  echo "    pip install openai-whisper" >&2
  echo "    (패키지명: openai-whisper / openssl-whisper 아님)" >&2
  echo "" >&2
  echo "▶ 설치 없이 사용할 수 있는 대안:" >&2
  echo "    1. Notta (https://www.notta.ai)" >&2
  echo "       — 파일 업로드 후 한국어 변환, 무료 플랜 있음" >&2
  echo "    2. CLOVA Note (https://clovanote.naver.com)" >&2
  echo "       — 네이버 계정 필요, 한국어 특화" >&2
  echo "" >&2
  echo "변환 후 텍스트를 Claude에 붙여넣으면 이어서 처리합니다." >&2
  echo "────────────────────────────────────────────────────────" >&2
  exit 2
fi
