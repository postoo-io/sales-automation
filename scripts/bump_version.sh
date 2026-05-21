#!/usr/bin/env bash
# Bump plugin version in lockstep across .claude-plugin/plugin.json and marketplace.json.
#
# semver guidance (use your judgement):
#   patch  — bug fix / 문서·내부 리팩토링 / 스킬 본문 미세 수정
#   minor  — 새 스킬, 새 기능, 새 보조 자원 (호환 유지)
#   major  — 스키마 변경, 스킬 이름 변경, 호환 깨짐
#
# Usage:
#   scripts/bump_version.sh patch          # 0.2.0 → 0.2.1
#   scripts/bump_version.sh minor          # 0.2.0 → 0.3.0
#   scripts/bump_version.sh major          # 0.2.0 → 1.0.0
#   scripts/bump_version.sh --set 1.2.3    # explicit
#   scripts/bump_version.sh --show         # print current version
#
# After bumping, commit the two manifest files and push:
#   git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
#   git commit -m "Release vX.Y.Z"
#   git push
#
# Exit codes: 0 success · 2 usage error · 3 inconsistent versions detected

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"

current_version() {
  python3 - <<PY
import json
plugin = json.load(open("$PLUGIN_JSON"))
mp = json.load(open("$MARKETPLACE_JSON"))
pv = plugin.get("version")
mv = mp.get("metadata", {}).get("version")
if pv != mv:
    print(f"[bump] inconsistent: plugin.json={pv}, marketplace.json={mv}", file=__import__("sys").stderr)
    __import__("sys").exit(3)
print(pv)
PY
}

set_version() {
  local new="$1"
  python3 - "$new" <<'PY'
import json, sys
new = sys.argv[1]
PLUGIN  = "PLUGIN_PLACEHOLDER"
MARKET  = "MARKET_PLACEHOLDER"
for path, keys in ((PLUGIN, ["version"]),
                   (MARKET, ["metadata", "version"])):
    with open(path) as f:
        data = json.load(f)
    cur = data
    for k in keys[:-1]:
        cur = cur[k]
    cur[keys[-1]] = new
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")
PY
}

# Lightweight version of set_version that uses environment vars to avoid
# heredoc placeholder substitution — keeps the script paths editable.
_set_version_py() {
  local new="$1"
  PLUGIN_JSON="$PLUGIN_JSON" MARKETPLACE_JSON="$MARKETPLACE_JSON" NEW_VER="$new" \
  python3 - <<'PY'
import json, os
new = os.environ["NEW_VER"]
for path, keys in ((os.environ["PLUGIN_JSON"], ["version"]),
                   (os.environ["MARKETPLACE_JSON"], ["metadata", "version"])):
    with open(path) as f:
        data = json.load(f)
    cur = data
    for k in keys[:-1]:
        cur = cur[k]
    cur[keys[-1]] = new
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")
PY
}

bump_component() {
  local kind="$1"
  local cur
  cur="$(current_version)"
  local major minor patch
  IFS='.' read -r major minor patch <<< "$cur"
  case "$kind" in
    major) major=$((major+1)); minor=0; patch=0 ;;
    minor) minor=$((minor+1)); patch=0 ;;
    patch) patch=$((patch+1)) ;;
    *) echo "[bump] unknown component: $kind" >&2; exit 2 ;;
  esac
  echo "$major.$minor.$patch"
}

case "${1:-}" in
  --show)
    current_version
    ;;
  --set)
    if [[ -z "${2:-}" ]]; then
      echo "[bump] usage: $0 --set X.Y.Z" >&2
      exit 2
    fi
    _set_version_py "$2"
    echo "version → $2"
    ;;
  patch|minor|major)
    new="$(bump_component "$1")"
    _set_version_py "$new"
    echo "version → $new ($1)"
    ;;
  ""|--help|-h)
    sed -n '1,30p' "$0" | sed 's/^# \{0,1\}//'
    [[ "${1:-}" == "" ]] && exit 2 || exit 0
    ;;
  *)
    echo "[bump] unknown argument: $1" >&2
    echo "       try: patch | minor | major | --set X.Y.Z | --show" >&2
    exit 2
    ;;
esac
