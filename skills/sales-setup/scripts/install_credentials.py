#!/usr/bin/env python3
"""Install Pluuug Open API credentials to an OS-standard config location.

This avoids re-exporting PLUUUG_API_KEY / PLUUUG_SECRET_KEY every session
(useful for Cowork, fresh shells, or multi-machine setups).

Write location (resolved at runtime, JSON, mode 0600):
  - macOS:   ~/Library/Application Support/sales-automation/credentials.json
  - Linux:   $XDG_CONFIG_HOME/sales-automation/credentials.json
  - Windows: %APPDATA%/sales-automation/credentials.json
  - Fallback: ~/.sales-automation/credentials.json

The companion pluuug.py reader checks both the new path AND the legacy
<config>/pluuug/credentials.json path (read-only), so existing installs keep
working until they re-run --migrate.

File format:
  {"api_key": "...", "secret_key": "..."}

Input modes (pick one):
  --from-env       read PLUUUG_API_KEY / PLUUUG_SECRET_KEY from the environment
  --from-stdin     read two lines from stdin: api_key, then secret_key
  --migrate        copy from legacy <config>/pluuug/credentials.json
  (default)        interactive prompt via getpass (no echo to terminal)

Exit codes:
  0  saved successfully
  2  missing/invalid input
  3  file already exists (use --force to overwrite)
  4  failed to write file
  5  --migrate: no legacy file found
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import platform
import sys


def get_config_path() -> str:
    """The canonical (write) location."""
    home = os.path.expanduser("~")
    system = platform.system()
    if system == "Darwin":
        return os.path.join(home, "Library", "Application Support", "sales-automation", "credentials.json")
    if system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        return os.path.join(appdata, "sales-automation", "credentials.json")
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
    return os.path.join(xdg, "sales-automation", "credentials.json")


def get_legacy_path() -> str:
    """Legacy pluuug/ location (read-only on this side)."""
    home = os.path.expanduser("~")
    system = platform.system()
    if system == "Darwin":
        return os.path.join(home, "Library", "Application Support", "pluuug", "credentials.json")
    if system == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        return os.path.join(appdata, "pluuug", "credentials.json")
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
    return os.path.join(xdg, "pluuug", "credentials.json")


def write_credentials(path: str, api_key: str, secret_key: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"api_key": api_key, "secret_key": secret_key}, f)
            f.write("\n")
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        raise
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def main() -> int:
    p = argparse.ArgumentParser(description="Install Pluuug API credentials.")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--from-env", action="store_true",
                     help="Read PLUUUG_API_KEY and PLUUUG_SECRET_KEY from the environment.")
    src.add_argument("--from-stdin", action="store_true",
                     help="Read api_key on line 1, secret_key on line 2.")
    src.add_argument("--migrate", action="store_true",
                     help="Copy from <config>/pluuug/credentials.json into the new sales-automation/ path.")
    p.add_argument("--force", action="store_true",
                   help="Overwrite an existing credentials file.")
    p.add_argument("--show-path", action="store_true",
                   help="Print the target path and exit.")
    args = p.parse_args()

    path = get_config_path()
    if args.show_path:
        print(path)
        return 0

    if args.migrate:
        legacy = get_legacy_path()
        if not os.path.isfile(legacy):
            print(f"[sales-setup] no legacy credentials at: {legacy}", file=sys.stderr)
            return 5
        try:
            with open(legacy, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[sales-setup] failed to read legacy {legacy}: {e}", file=sys.stderr)
            return 4
        api_key = (data.get("api_key") or data.get("PLUUUG_API_KEY") or "").strip()
        secret_key = (data.get("secret_key") or data.get("PLUUUG_SECRET_KEY") or "").strip()
        if not api_key or not secret_key:
            print("[sales-setup] legacy file has no usable keys", file=sys.stderr)
            return 2
        if os.path.exists(path) and not args.force:
            print(f"[sales-setup] {path} already exists. Use --force to overwrite.", file=sys.stderr)
            return 3
        try:
            write_credentials(path, api_key, secret_key)
        except OSError as e:
            print(f"[sales-setup] failed to write {path}: {e}", file=sys.stderr)
            return 4
        print(f"[sales-setup] migrated {legacy} → {path} (mode 0600)")
        return 0

    if args.from_env:
        api_key = (os.environ.get("PLUUUG_API_KEY") or "").strip()
        secret_key = (os.environ.get("PLUUUG_SECRET_KEY") or "").strip()
    elif args.from_stdin:
        lines = sys.stdin.read().splitlines()
        api_key = (lines[0].strip() if len(lines) > 0 else "")
        secret_key = (lines[1].strip() if len(lines) > 1 else "")
    else:
        try:
            api_key = getpass.getpass("PLUUUG_API_KEY: ").strip()
            secret_key = getpass.getpass("PLUUUG_SECRET_KEY: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[sales-setup] aborted", file=sys.stderr)
            return 2

    if not api_key or not secret_key:
        print("[sales-setup] api_key and secret_key are both required", file=sys.stderr)
        return 2

    if os.path.exists(path) and not args.force:
        print(f"[sales-setup] credentials already exist at:\n  {path}\nUse --force to overwrite.",
              file=sys.stderr)
        return 3

    try:
        write_credentials(path, api_key, secret_key)
    except OSError as e:
        print(f"[sales-setup] failed to write {path}: {e}", file=sys.stderr)
        return 4

    print(f"[sales-setup] saved to {path} (mode 0600)")
    print("이제 모든 세션에서 pluuug.py가 자동으로 키를 로드합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
