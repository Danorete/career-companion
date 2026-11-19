"""One-click start for Link (decision D47).

`companion launch` opens Link in your browser. If Link is already running it asks it for a fresh one-time sign-in
link, using a private key file that only your user can read. If it is not running it starts it quietly in the
background first. On a Mac, `companion launcher --install` makes a real `Link.app` that does the same thing from
Spotlight or the Dock. Nothing here sends anything beyond this computer.

A running Link keeps the code it started with, so after an update (a `git pull`) opening it used to show the old
version (decision D56). Now each running copy says which code it runs, and opening Link restarts a copy that is older
than the code on disk. `companion launcher --install` can also add a git hook, so `git pull` itself opens the new Link.
"""

from __future__ import annotations

import hashlib
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


# ---- which code is running ---------------------------------------------------------------

CODE_SUFFIXES = frozenset({".py", ".js", ".css", ".html", ".svg"})


def code_version(root: Path | None = None) -> str:
    """A fingerprint of Link's own files on disk. A pull rewrites the files it changes, so the fingerprint moves.
    Sizes and modification times are enough: a false alarm only costs a restart."""
    root = Path(root) if root else Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.suffix in CODE_SUFFIXES and "__pycache__" not in path.parts and path.is_file():
            st = path.stat()
            digest.update(f"{path.relative_to(root).as_posix()}:{st.st_size}:{st.st_mtime_ns}\n".encode())
    return digest.hexdigest()[:16]


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
    """(status, token, version) from a running Link, or None when nothing is listening. A copy started before D56
    gives no version."""
    try:
        r = httpx.get(base + "/launcher/token", headers={"X-Launcher-Key": key or ""}, timeout=2.0, trust_env=False)
    except httpx.HTTPError:
        return None
    body = r.json() if r.status_code == 200 else {}
    return r.status_code, body.get("token"), body.get("version")


def open_in_browser(url: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", url], check=False)  # webbrowser can fail quietly on a Mac
    else:
        webbrowser.open(url)


def spawn_background(settings, python: str = sys.executable) -> None:
    log = Path(settings.data_dir) / "link.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)  # private even before the data folder is locked down
    os.chmod(log, 0o600)
    with os.fdopen(fd, "ab") as out:
        subprocess.Popen([python, "-m", "companion.cli", "run", "--background"], stdin=subprocess.DEVNULL, stdout=out, stderr=out,
                         start_new_session=True, env=os.environ.copy())


def launch(settings, *, ask=ask_for_link, spawn=spawn_background, opener=open_in_browser, sleep=time.sleep,
           clock=time.monotonic, timeout: float = START_TIMEOUT_SECONDS, stop=None, version=code_version) -> tuple[int, str]:
    base = _base(settings)
    answer = ask(base, read_key(settings.data_dir))
    restarted = False
    # Running, but on older code than what is on disk now (an update since it started): stop it and start the new code,
    # so opening Link always shows the newest version. A copy from before D56 says no version, so it counts as older.
    if answer is not None and answer[0] == 200 and (answer[2] if len(answer) > 2 else None) != version():
        (stop or quit_running)(settings)
        deadline = clock() + timeout
        while answer is not None and clock() < deadline:  # wait for the old copy to let go of the port
            sleep(0.3)
            answer = ask(base, read_key(settings.data_dir))
        if answer is not None:
            return 1, "Link is still running the older version and didn't stop. Choose Menu > Quit Link, then open Link again."
        restarted = True
    if answer is None:  # not running: start it, then wait for it to answer
        spawn(settings)
        deadline = clock() + timeout
        while answer is None and clock() < deadline:
            sleep(0.4)
            answer = ask(base, read_key(settings.data_dir))  # the key file appears when Link starts
        if answer is None:
            return 1, f"Link didn't start within {int(timeout)} seconds. The reason is in {Path(settings.data_dir) / 'link.log'}."
    status, token = answer[0], answer[1]
    if status != 200:
        return 1, (f"Something is using port {settings.port} that isn't this copy of Link, or Link was started with a different "
                   "data folder. Quit it and try again.")
    opener(f"{base}/#t={token}")
    return 0, "Restarted Link with the update and opened it in your browser." if restarted else "Opened Link in your browser."


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


# ---- git pull opens Link (decision D56) ------------------------------------------------------

HOOK_MARK = "# Installed by Link (companion launcher --install): after a git pull, open Link with the new code."


def repo_root() -> Path | None:
    """The git checkout this copy of Link runs from (an editable install), or None for an installed package."""
    here = Path(__file__).resolve().parent
    for folder in (here, *here.parents):
        if (folder / ".git").exists():
            return folder
    return None


def hook_path(root: Path, runner=subprocess.run) -> Path:
    """Where git looks for the post-merge hook, which runs after every pull that brings changes."""
    found = runner(["git", "-C", str(root), "rev-parse", "--git-path", "hooks"], capture_output=True, text=True, check=False)
    hooks = Path(found.stdout.strip()) if found.returncode == 0 and found.stdout.strip() else Path(".git") / "hooks"
    return (hooks if hooks.is_absolute() else root / hooks) / "post-merge"


def hook_source(python: str, env: dict[str, str]) -> str:
    """Open Link.app when it is installed, so the pull starts Link with the same settings as the app; otherwise run
    `companion launch` with the settings carried from the install, like the app does. Never a secret."""
    carried = " ".join(f"{k}={shlex.quote(env[k])}" for k in CARRIED_ENV if env.get(k))
    direct = f"{carried + ' ' if carried else ''}{shlex.quote(python)} -m companion.cli launch"
    return ("#!/bin/sh\n"
            f"{HOOK_MARK}\n"
            "# Remove it with: companion launcher --uninstall\n"
            'echo "Opening Link with the new code..."\n'
            'if [ "$(uname)" = "Darwin" ] && [ -d "$HOME/Applications/Link.app" ]; then\n'
            '  open "$HOME/Applications/Link.app"\n'
            "else\n"
            f"  {direct}\n"
            "fi\n")


def install_pull_hook(root: Path | None, *, python: str = sys.executable, env: dict[str, str] | None = None,
                      runner=subprocess.run) -> str:
    if root is None:
        return ""  # not a git checkout: nothing to pull
    path = hook_path(root, runner)
    if not path.resolve().is_relative_to(Path(root).resolve()):
        # core.hooksPath points at a shared folder: a hook there would open Link after a pull in every repository.
        return "Your git hooks live outside this folder (core.hooksPath), so git pull won't open Link. Open Link after pulling."
    if path.exists() and HOOK_MARK not in path.read_text(encoding="utf-8", errors="replace"):
        return f"Your repository already has its own {path.name} hook, so it was left alone and git pull won't open Link."
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(hook_source(python, dict(os.environ if env is None else env)), encoding="utf-8")
    path.chmod(0o755)
    return "From now on, git pull opens Link with the new code when it brings changes."


def uninstall_pull_hook(root: Path | None, runner=subprocess.run) -> str:
    if root is None:
        return ""
    path = hook_path(root, runner)
    if path.exists() and HOOK_MARK in path.read_text(encoding="utf-8", errors="replace"):
        path.unlink()
        return "git pull no longer opens Link."
    return ""


def pull_hook_installed(root: Path | None, runner=subprocess.run) -> bool:
    if root is None:
        return False
    path = hook_path(root, runner)
    return path.exists() and HOOK_MARK in path.read_text(encoding="utf-8", errors="replace")


def uninstall(home: Path) -> str:
    target = app_path(home)
    existed = target.exists()
    if existed:
        shutil.rmtree(target)
    return "Removed Link.app." if existed else "Link.app wasn't installed."
