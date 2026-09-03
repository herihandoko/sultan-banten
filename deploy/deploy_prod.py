#!/usr/bin/env python3
"""
Deploy SIAGAPIM dari laptop lokal ke VM produksi.

Cara pakai:
  1. cp deploy/.env.deploy.example deploy/.env.deploy
  2. isi kredensial SSH di deploy/.env.deploy
  3. python3 deploy/deploy_prod.py

Opsi:
  python3 deploy/deploy_prod.py --dry-run     # hanya sync, tanpa rebuild
  python3 deploy/deploy_prod.py --skip-sync   # rebuild saja di server
  python3 deploy/deploy_prod.py --health-only # cek health endpoint saja

Kredensial juga bisa lewat environment:
  DEPLOY_HOST, DEPLOY_USER, DEPLOY_PASSWORD, DEPLOY_PORT,
  DEPLOY_REMOTE_DIR, DEPLOY_SUDO_PASSWORD, DEPLOY_HEALTH_URL
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = Path(__file__).resolve().parent / ".env.deploy"

DEFAULTS = {
    "DEPLOY_HOST": "10.249.101.43",
    "DEPLOY_USER": "python",
    "DEPLOY_PORT": "22",
    "DEPLOY_REMOTE_DIR": "/home/python/apps/sultan-banten",
    "DEPLOY_COMPOSE_FILE": "docker-compose.standalone.yml",
    "DEPLOY_ENV_FILE": ".env.standalone",
    "DEPLOY_HEALTH_URL": "https://siagapim.bantenprov.go.id/api/health",
    "DEPLOY_USE_SUDO": "1",
}

RSYNC_EXCLUDES = [
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "frontend/dist",
    "frontend/node_modules",
    "backend/.venv",
    "backend/instance",
    "__pycache__",
    "*.pyc",
    ".DS_Store",
    ".env",
    ".env.docker",
    ".env.local",
    ".env.standalone",  # jangan overwrite secret prod
    "deploy/.env.deploy",
    "*.sqlite",
    "*.sqlite3",
]


def load_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        data[key] = value
    return data


def cfg(key: str) -> str:
    return os.environ.get(key) or ENV.get(key) or DEFAULTS.get(key, "")


ENV = load_env_file(ENV_FILE)


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def run(cmd: list[str], *, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(shlex.quote(c) for c in cmd)}")
    return subprocess.run(cmd, env=env, check=check)


def require_tools() -> None:
    for tool in ("rsync", "ssh", "sshpass"):
        if subprocess.call(["which", tool], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            die(f"Tool '{tool}' belum terpasang. Install dulu (macOS: brew install {tool}).")


def ssh_base(host: str, user: str, port: str) -> list[str]:
    return [
        "sshpass",
        "-e",
        "ssh",
        "-p",
        port,
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "PreferredAuthentications=password",
        "-o",
        "PubkeyAuthentication=no",
        f"{user}@{host}",
    ]


def rsync_ssh(port: str) -> str:
    return (
        f"sshpass -e ssh -p {shlex.quote(port)} "
        "-o StrictHostKeyChecking=accept-new "
        "-o PreferredAuthentications=password "
        "-o PubkeyAuthentication=no"
    )


def resolve_remote_dir(password: str) -> str:
    """Expand ~ to absolute path on the remote host."""
    remote_dir = cfg("DEPLOY_REMOTE_DIR").strip()
    if not remote_dir.startswith("~"):
        return remote_dir
    host = cfg("DEPLOY_HOST")
    user = cfg("DEPLOY_USER")
    port = cfg("DEPLOY_PORT")
    proc = subprocess.run(
        ssh_base(host, user, port) + ["printf %s \"$HOME\""],
        env={**os.environ, "SSHPASS": password},
        check=True,
        capture_output=True,
        text=True,
    )
    home = proc.stdout.strip() or f"/home/{user}"
    if remote_dir == "~":
        return home
    if remote_dir.startswith("~/"):
        return f"{home}/{remote_dir[2:]}"
    return remote_dir


def sync_files(password: str, remote_dir: str) -> None:
    host = cfg("DEPLOY_HOST")
    user = cfg("DEPLOY_USER")
    port = cfg("DEPLOY_PORT")

    run(
        ssh_base(host, user, port) + [f"mkdir -p {shlex.quote(remote_dir)}"],
        env={**os.environ, "SSHPASS": password},
    )

    excludes = []
    for item in RSYNC_EXCLUDES:
        excludes.extend(["--exclude", item])

    dest = f"{user}@{host}:{remote_dir}/"
    cmd = [
        "rsync",
        "-az",
        "--delete",
        "-e",
        rsync_ssh(port),
        *excludes,
        f"{ROOT}/",
        dest,
    ]
    run(cmd, env={**os.environ, "SSHPASS": password})


def remote_rebuild(password: str, remote_dir: str) -> None:
    host = cfg("DEPLOY_HOST")
    user = cfg("DEPLOY_USER")
    port = cfg("DEPLOY_PORT")
    compose = cfg("DEPLOY_COMPOSE_FILE")
    env_file = cfg("DEPLOY_ENV_FILE")
    use_sudo = cfg("DEPLOY_USE_SUDO") in {"1", "true", "yes"}
    sudo_password = cfg("DEPLOY_SUDO_PASSWORD") or password

    rebuild_cmd = (
        f"cd {shlex.quote(remote_dir)} && "
        f"test -f {shlex.quote(env_file)} || "
        f"{{ echo 'Missing {env_file} on server' >&2; exit 2; }} && "
        f"docker compose -f {shlex.quote(compose)} --env-file {shlex.quote(env_file)} "
        "up -d --build --remove-orphans"
    )
    if use_sudo:
        remote = (
            f"printf '%s\\n' {shlex.quote(sudo_password)} | "
            f"sudo -S -p '' bash -lc {shlex.quote(rebuild_cmd)}"
        )
    else:
        remote = rebuild_cmd

    run(
        ssh_base(host, user, port) + [remote],
        env={**os.environ, "SSHPASS": password},
    )


def health_check(url: str, retries: int = 12, delay: float = 5.0) -> None:
    print(f"\nHealth check: {url}")
    last_err = None
    for i in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                print(f"  [{i}/{retries}] HTTP {resp.status}: {body[:200]}")
                if resp.status == 200:
                    print("OK — deploy selesai.")
                    return
        except (urllib.error.URLError, TimeoutError) as err:
            last_err = err
            print(f"  [{i}/{retries}] menunggu... ({err})")
        time.sleep(delay)
    die(f"Health check gagal setelah {retries} percobaan: {last_err}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy SIAGAPIM ke VM produksi")
    parser.add_argument("--dry-run", action="store_true", help="Sync file saja, tanpa rebuild Docker")
    parser.add_argument("--skip-sync", action="store_true", help="Skip rsync, langsung rebuild di server")
    parser.add_argument("--health-only", action="store_true", help="Hanya cek health endpoint")
    args = parser.parse_args()

    if not ENV_FILE.exists() and not os.environ.get("DEPLOY_PASSWORD"):
        print(
            "Belum ada deploy/.env.deploy\n"
            "  cp deploy/.env.deploy.example deploy/.env.deploy\n"
            "lalu isi DEPLOY_PASSWORD (dan opsi lain bila perlu)."
        )
        raise SystemExit(2)

    password = cfg("DEPLOY_PASSWORD")
    host = cfg("DEPLOY_HOST")
    user = cfg("DEPLOY_USER")
    health_url = cfg("DEPLOY_HEALTH_URL")

    if args.health_only:
        if not health_url:
            die("DEPLOY_HEALTH_URL kosong")
        health_check(health_url)
        return

    if not password:
        die("DEPLOY_PASSWORD wajib diisi di deploy/.env.deploy atau environment")
    if not host or not user:
        die("DEPLOY_HOST / DEPLOY_USER wajib diisi")

    require_tools()

    remote_dir = resolve_remote_dir(password)

    print("=== SIAGAPIM deploy ===")
    print(f"Host     : {user}@{host}:{cfg('DEPLOY_PORT')}")
    print(f"Remote   : {remote_dir}")
    print(f"Compose  : {cfg('DEPLOY_COMPOSE_FILE')} + {cfg('DEPLOY_ENV_FILE')}")
    print(f"Health   : {health_url or '(skip)'}")

    if not args.skip_sync:
        print("\n[1/3] Sync file...")
        sync_files(password, remote_dir)
    else:
        print("\n[1/3] Sync dilewati (--skip-sync)")

    if args.dry_run:
        print("\nDry-run: rebuild dilewati.")
        return

    print("\n[2/3] Rebuild & restart Docker di VM...")
    remote_rebuild(password, remote_dir)

    if health_url:
        print("\n[3/3] Verifikasi...")
        health_check(health_url)
    else:
        print("\n[3/3] Health URL kosong — skip verifikasi.")
        print("OK — deploy selesai.")


if __name__ == "__main__":
    main()
