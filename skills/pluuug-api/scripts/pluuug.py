#!/usr/bin/env python3
"""Pluuug Open API CLI helper.

Signs the request body with HMAC-SHA256 using PLUUUG_SECRET_KEY,
adds X-API-Key and X-Signature headers, and prints the response.

Auth env vars (required):
  PLUUUG_API_KEY      X-API-Key header value
  PLUUUG_SECRET_KEY   HMAC secret used to sign request body

Examples:
  pluuug.py GET /v1/inquiry --query inquiry_date_start=2026-05-14 page_size=20
  pluuug.py GET /v1/inquiry/1234
  pluuug.py POST /v1/inquiry/1234/text_history --json '{"content":"콜백 완료"}'
  pluuug.py PATCH /v1/client/567 --json '{"inCharge":"박매니저"}'
  cat body.json | pluuug.py POST /v1/client --json -

Exit codes:
  0  success (HTTP 2xx)
  1  HTTP error (response printed to stdout)
  2  configuration / usage error
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json as jsonlib
import os
import platform
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://openapi.pluuug.com"


def sign(secret: str, body: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def canonical_body(raw: str | None) -> str:
    """Re-serialize JSON to match what the server signs (no extra whitespace).

    Empty body is signed as the empty string per Pluuug docs.
    """
    if not raw:
        return ""
    try:
        parsed = jsonlib.loads(raw)
    except jsonlib.JSONDecodeError as e:
        print(f"[pluuug] invalid JSON body: {e}", file=sys.stderr)
        sys.exit(2)
    return jsonlib.dumps(parsed, separators=(",", ":"), ensure_ascii=False)


def build_url(path: str, query_pairs: list[str]) -> str:
    if not path.startswith("/"):
        path = "/" + path
    url = BASE_URL + path
    if query_pairs:
        parsed = []
        for kv in query_pairs:
            if "=" not in kv:
                print(f"[pluuug] --query item must be key=value, got: {kv}", file=sys.stderr)
                sys.exit(2)
            k, v = kv.split("=", 1)
            parsed.append((k, v))
        url += "?" + urllib.parse.urlencode(parsed, doseq=True)
    return url


def _load_dotenv_walk_up() -> None:
    """Load PLUUUG_* vars from a .env file by walking up from script dir."""
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidate = os.path.join(here, ".env")
        if os.path.isfile(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("\"").strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
            return
        parent = os.path.dirname(here)
        if parent == here:
            return
        here = parent


def _os_credentials_paths() -> list[str]:
    """Return OS-standard credential file candidates, most-specific first.

    macOS:   ~/Library/Application Support/pluuug/credentials.json
    Linux:   $XDG_CONFIG_HOME/pluuug/credentials.json (default ~/.config)
    Windows: %APPDATA%/pluuug/credentials.json
    Fallback (all OS): ~/.pluuug/credentials.json
    """
    home = os.path.expanduser("~")
    paths: list[str] = []
    system = platform.system()
    if system == "Darwin":
        paths.append(os.path.join(home, "Library", "Application Support", "pluuug", "credentials.json"))
    elif system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        paths.append(os.path.join(appdata, "pluuug", "credentials.json"))
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        paths.append(os.path.join(xdg, "pluuug", "credentials.json"))
    paths.append(os.path.join(home, ".pluuug", "credentials.json"))
    return paths


def _load_os_credentials() -> None:
    """Load credentials from an OS-standard JSON file if present.

    Accepts both {"api_key":..., "secret_key":...} and
    {"PLUUUG_API_KEY":..., "PLUUUG_SECRET_KEY":...} shapes.
    """
    for path in _os_credentials_paths():
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = jsonlib.load(f)
        except (jsonlib.JSONDecodeError, OSError):
            continue
        api = data.get("api_key") or data.get("PLUUUG_API_KEY")
        secret = data.get("secret_key") or data.get("PLUUUG_SECRET_KEY")
        if api and secret:
            os.environ.setdefault("PLUUUG_API_KEY", api)
            os.environ.setdefault("PLUUUG_SECRET_KEY", secret)
            return


def load_credentials() -> None:
    """Resolve PLUUUG_* credentials in order:
    1. existing environment variables (no-op if already set)
    2. project .env file (walks up from this script)
    3. OS-standard credential file (~/Library/Application Support, $XDG_CONFIG_HOME, %APPDATA%)
    4. cross-platform fallback ~/.pluuug/credentials.json

    Designed so that ephemeral sessions (e.g. Cowork) can keep keys at an
    OS-standard location and avoid re-entering them every session.
    """
    if os.environ.get("PLUUUG_API_KEY") and os.environ.get("PLUUUG_SECRET_KEY"):
        return
    _load_dotenv_walk_up()
    if os.environ.get("PLUUUG_API_KEY") and os.environ.get("PLUUUG_SECRET_KEY"):
        return
    _load_os_credentials()


def main() -> int:
    p = argparse.ArgumentParser(description="Pluuug Open API helper")
    p.add_argument("method", choices=["GET", "POST", "PATCH", "PUT", "DELETE"])
    p.add_argument("path", help="API path, e.g. /v1/inquiry or /v1/inquiry/1234")
    p.add_argument("--query", nargs="*", default=[], help="key=value query params")
    p.add_argument("--json", help='JSON body string, or "-" to read from stdin')
    p.add_argument("--raw", action="store_true", help="Print raw response (default: pretty JSON)")
    args = p.parse_args()

    load_credentials()
    api_key = os.environ.get("PLUUUG_API_KEY")
    secret = os.environ.get("PLUUUG_SECRET_KEY")
    if not api_key or not secret:
        print(
            "[pluuug] credentials not found.\n"
            "  Run the pluuug-setup skill, or set env vars / write .env in the project root.\n"
            "  Lookup order: env vars → project .env → OS config → ~/.pluuug/credentials.json",
            file=sys.stderr,
        )
        return 2

    raw_body = args.json
    if raw_body == "-":
        raw_body = sys.stdin.read()
    body = canonical_body(raw_body) if args.method in ("POST", "PATCH", "PUT") else ""
    signature = sign(secret, body)

    url = build_url(args.path, args.query)
    req = urllib.request.Request(
        url,
        method=args.method,
        data=body.encode("utf-8") if body else None,
        headers={
            "X-API-Key": api_key,
            "X-Signature": signature,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            payload = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")
        status = e.code
    except urllib.error.URLError as e:
        print(f"[pluuug] network error: {e}", file=sys.stderr)
        return 2

    print(f"HTTP {status}", file=sys.stderr)
    if args.raw:
        sys.stdout.write(payload)
    else:
        try:
            sys.stdout.write(jsonlib.dumps(jsonlib.loads(payload), indent=2, ensure_ascii=False))
            sys.stdout.write("\n")
        except jsonlib.JSONDecodeError:
            sys.stdout.write(payload)

    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
