#!/usr/bin/env bash
# Upload a local file to Pluuug via presigned URL, print the path to attach.
#
# Usage: presigned_upload.sh <local-file>
# Output (stdout, single line): {"name":"...","path":"..."}
#
# Requires PLUUUG_API_KEY, PLUUUG_SECRET_KEY env vars and the sibling pluuug.py script.

set -euo pipefail

if [[ $# -ne 1 || ! -f "$1" ]]; then
  echo "usage: $0 <local-file>" >&2
  exit 2
fi

file_path="$1"
file_name="$(basename "$file_path")"
script_dir="$(cd "$(dirname "$0")" && pwd)"

# 1. Request a presigned PUT URL.
resp="$(python3 "$script_dir/pluuug.py" POST /v1/presigned \
  --json "$(printf '{"name":%s}' "$(printf '%s' "$file_name" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')")")"

url="$(printf '%s' "$resp" | python3 -c 'import json,sys;print(json.load(sys.stdin)["url"])')"
path="$(printf '%s' "$resp" | python3 -c 'import json,sys;print(json.load(sys.stdin)["path"])')"

# 2. Upload the file directly to S3 (no signature header — presigned URL carries auth).
mime="$(python3 -c "import mimetypes,sys;print(mimetypes.guess_type(sys.argv[1])[0] or 'application/octet-stream')" "$file_path")"
curl -sSf -X PUT -H "Content-Type: $mime" --data-binary "@$file_path" "$url" > /dev/null

# 3. Print the path payload to feed into inquiry create/patch.
printf '{"name":%s,"path":%s}\n' \
  "$(printf '%s' "$file_name" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
  "$(printf '%s' "$path"      | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')"
