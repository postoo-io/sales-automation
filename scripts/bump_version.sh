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
  PLUGIN_JSON="$PLUGIN_JSON" MARKETPLACE_JSON="$MARKETPLACE_JSON" \
  python3 - <<'PY'
import json, os, sys
plugin = json.load(open(os.environ["PLUGIN_JSON"]))
mp = json.load(open(os.environ["MARKETPLACE_JSON"]))
pv = plugin.get("version")
mv = mp.get("metadata", {}).get("version")
plugin_versions = [p.get("version") for p in mp.get("plugins", []) if isinstance(p, dict)]
all_same = (pv == mv) and all(v == pv for v in plugin_versions)
if not all_same:
    print(f"[bump] inconsistent versions:", file=sys.stderr)
    print(f"  plugin.json                 = {pv}", file=sys.stderr)
    print(f"  marketplace.metadata.version = {mv}", file=sys.stderr)
    for i, v in enumerate(plugin_versions):
        print(f"  marketplace.plugins[{i}].version = {v}", file=sys.stderr)
    sys.exit(3)
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
  PLUGIN_JSON="$PLUGIN_JSON" MARKETPLACE_JSON="$MARKETPLACE_JSON" \
  README_MD="$REPO_ROOT/README.md" NEW_VER="$new" \
  python3 - <<'PY'
import json, os, re
new = os.environ["NEW_VER"]

# plugin.json — single top-level version
with open(os.environ["PLUGIN_JSON"]) as f:
    data = json.load(f)
data["version"] = new
with open(os.environ["PLUGIN_JSON"], "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
    f.write("\n")

# marketplace.json — metadata.version + every plugins[i].version
with open(os.environ["MARKETPLACE_JSON"]) as f:
    mp = json.load(f)
mp.setdefault("metadata", {})["version"] = new
for plugin in mp.get("plugins", []):
    if isinstance(plugin, dict):
        plugin["version"] = new
with open(os.environ["MARKETPLACE_JSON"], "w", encoding="utf-8") as f:
    json.dump(mp, f, indent=4, ensure_ascii=False)
    f.write("\n")

# README.md — replace any "현재 버전: v..." or "Current version: v..." line,
# including the release-tag link if present.
readme_path = os.environ["README_MD"]
if os.path.isfile(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        text = f.read()
    repl_tag_link = (
        r"\g<prefix>v" + new + r"\g<sep>"
        r"https://github.com/postoo-io/sales-automation/releases/tag/v" + new + r")"
    )
    new_text = re.sub(
        r"(?P<prefix>\*\*(?:현재 버전|Current version)\*\*\s*:\s*\[)v\d+\.\d+\.\d+(?P<sep>\]\()"
        r"https://github\.com/postoo-io/sales-automation/releases/tag/v\d+\.\d+\.\d+\)",
        repl_tag_link,
        text,
    )
    # Fallback: plain "**현재 버전**: vX.Y.Z" without link
    new_text = re.sub(
        r"(\*\*(?:현재 버전|Current version)\*\*\s*:\s*)v\d+\.\d+\.\d+",
        r"\1v" + new,
        new_text,
    )
    if new_text != text:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_text)
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
