"""One-click start for Link (decision D47).

`companion launch` opens Link in your browser. If Link is already running it asks it for a fresh one-time sign-in
link, using a private key file that only your user can read. If it is not running it starts it quietly in the
background first. On a Mac, `companion launcher --install` makes a real `Link.app` that does the same thing from
Spotlight or the Dock. Nothing here sends anything beyond this computer.
"""

from __future__ import annotations

import os
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

import httpx

KEY_FILE = "launcher.key"
APP_NAME = "Link.app"
START_TIMEOUT_SECONDS = 15.0
# Carried into the app so it finds the same data. Secrets are never copied: use a client file for Google.
CARRIED_ENV = ("COMPANION_DATA_DIR", "COMPANION_GOOGLE_CLIENT_FILE", "COMPANION_TIMEZONE", "COMPANION_AI_MODE", "COMPANION_UI_MODE", "COMPANION_PORT")


# ---- the key ---------------------------------------------------------------------------

def key_path(data_dir: Path) -> Path:
    return Path(data_dir) / KEY_FILE


def ensure_key(data_dir: Path) -> str:
    """Create the key on first start. Readable by your user only, like the database."""
    path = key_path(data_dir)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    value = secrets.token_urlsafe(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(value)
    return value


def read_key(data_dir: Path) -> str | None:
    try:
        return key_path(data_dir).read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


# ---- talking to a running Link -----------------------------------------------------------

def _base(settings) -> str:
    return f"http://{settings.host}:{settings.port}"


def ask_for_link(base: str, key: str | None):
    """(status, token) from a running Link, or None when nothing is listening."""
    try:
        r = httpx.get(base + "/launcher/token", headers={"X-Launcher-Key": key or ""}, timeout=2.0, trust_env=False)
    except httpx.HTTPError:
        return None
    return r.status_code, (r.json().get("token") if r.status_code == 200 else None)


def open_in_browser(url: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", url], check=False)  # webbrowser can fail quietly on a Mac
    else:
        webbrowser.open(url)


def spawn_background(settings, python: str = sys.executable) -> None:
    log = Path(settings.data_dir) / "link.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "ab") as out:
        subprocess.Popen([python, "-m", "companion.cli", "run", "--background"], stdin=subprocess.DEVNULL, stdout=out, stderr=out,
                         start_new_session=True, env=os.environ.copy())


def launch(settings, *, ask=ask_for_link, spawn=spawn_background, opener=open_in_browser, sleep=time.sleep,
           clock=time.monotonic, timeout: float = START_TIMEOUT_SECONDS) -> tuple[int, str]:
    base = _base(settings)
    answer = ask(base, read_key(settings.data_dir))
    if answer is None:  # not running: start it, then wait for it to answer
        spawn(settings)
        deadline = clock() + timeout
        while answer is None and clock() < deadline:
            sleep(0.4)
            answer = ask(base, read_key(settings.data_dir))  # the key file appears when Link starts
        if answer is None:
            return 1, f"Link didn't start within {int(timeout)} seconds. The reason is in {Path(settings.data_dir) / 'link.log'}."
    status, token = answer
    if status != 200:
        return 1, (f"Something is using port {settings.port} that isn't this copy of Link, or Link was started with a different "
                   "data folder. Quit it and try again.")
    opener(f"{base}/#t={token}")
    return 0, "Opened Link in your browser."


def quit_running(settings, *, post=httpx.post) -> tuple[int, str]:
    base = _base(settings)
    try:
        r = post(base + "/launcher/quit", headers={"X-Launcher-Key": read_key(settings.data_dir) or "", "Origin": base,
                                                   "Content-Type": "application/json"}, content=b"{}", timeout=3.0)
    except httpx.HTTPError:
        return 0, "Link wasn't running."
    if r.status_code == 200:
        return 0, "Link has stopped."
    return 1, "Something answered on that port but wasn't this copy of Link, so nothing was stopped."


# ---- the Mac app -------------------------------------------------------------------------

def app_path(home: Path) -> Path:
    return home / "Applications" / APP_NAME


def is_installed(home: Path) -> bool:
    return app_path(home).exists()


def _applescript_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def applescript_source(python: str, log_path: Path, env: dict[str, str]) -> str:
    carried = " ".join(f"{k}={shlex.quote(env[k])}" for k in CARRIED_ENV if env.get(k))
    command = f"{carried + ' ' if carried else ''}{shlex.quote(python)} -m companion.cli launch >> {shlex.quote(str(log_path))} 2>&1"
    return ("try\n"
            f'    do shell script "{_applescript_string(command)}"\n'
            "on error\n"
            f'    display dialog "Link couldn\'t start. The reason is in {_applescript_string(str(log_path))}." buttons {{"OK"}} default button "OK" with icon caution\n'
            "end try\n")


def install(home: Path, data_dir: Path, *, runner=subprocess.run, platform: str = sys.platform, python: str = sys.executable,
            env: dict[str, str] | None = None) -> str:
    if platform != "darwin":
        return "The one-click app is for a Mac for now. Nothing was installed. You can still run: companion launch"
    target = app_path(home)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    source = applescript_source(python, Path(data_dir) / "link.log", dict(os.environ if env is None else env))
    with tempfile.TemporaryDirectory() as folder:
        script = Path(folder) / "link.applescript"
        script.write_text(source, encoding="utf-8")
        done = runner(["osacompile", "-o", str(target), str(script)], capture_output=True, check=False)
    if done.returncode != 0:
        return "macOS could not build the app. Run companion launch from Terminal instead."
    return f"Installed {target}. Open it from Spotlight (press Cmd+Space and type Link), or drag it to your Dock."


def uninstall(home: Path) -> str:
    target = app_path(home)
    existed = target.exists()
    if existed:
        shutil.rmtree(target)
    return "Removed Link.app." if existed else "Link.app wasn't installed."
