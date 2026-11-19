"""The small local helper that makes reminders appear while Link is closed (decision D46).

On a Mac, a launchd agent runs `companion nudge` every 15 minutes. The agent only reads Link's own database,
shows at most one generic notification, and writes counts (never names) to a log in Link's data folder.
Installing and removing it is something you do on purpose from Terminal; the web page cannot do it.
"""

from __future__ import annotations

import os
import plistlib
import subprocess
import sys
from pathlib import Path

LABEL = "com.career-companion.nudge"
INTERVAL_SECONDS = 900


def plist_path(home: Path) -> Path:
    return home / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def is_installed(home: Path) -> bool:
    return plist_path(home).exists()


def plist_bytes(python: str, log_path: Path, env: dict[str, str]) -> bytes:
    carried = {k: env[k] for k in ("COMPANION_DATA_DIR", "COMPANION_TIMEZONE") if env.get(k)}
    body = {"Label": LABEL, "ProgramArguments": [python, "-m", "companion.cli", "nudge"], "StartInterval": INTERVAL_SECONDS,
            "RunAtLoad": True, "StandardOutPath": str(log_path), "StandardErrorPath": str(log_path)}
    if carried:
        body["EnvironmentVariables"] = carried
    return plistlib.dumps(body)


def install(home: Path, log_path: Path, *, runner=subprocess.run, platform: str = sys.platform, python: str = sys.executable,
            env: dict[str, str] | None = None) -> str:
    if platform != "darwin":
        return "Desktop reminders need a Mac for now. Nothing was installed."
    target = plist_path(home)
    target.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(plist_bytes(python, log_path, dict(os.environ if env is None else env)))
    domain = f"gui/{os.getuid()}"
    runner(["launchctl", "bootout", domain, str(target)], capture_output=True, check=False)  # replace an older copy
    done = runner(["launchctl", "bootstrap", domain, str(target)], capture_output=True, check=False)
    if done.returncode != 0:
        return f"The helper file was written to {target}, but macOS did not start it. Log out and back in, or run: launchctl bootstrap {domain} {target}"
    return f"Installed. Link checks every {INTERVAL_SECONDS // 60} minutes and shows at most one reminder a day. Remove it with: companion nudge --uninstall"


def uninstall(home: Path, *, runner=subprocess.run, platform: str = sys.platform) -> str:
    target = plist_path(home)
    if platform == "darwin" and target.exists():
        runner(["launchctl", "bootout", f"gui/{os.getuid()}", str(target)], capture_output=True, check=False)
    existed = target.exists()
    target.unlink(missing_ok=True)
    return "Removed the helper." if existed else "The helper wasn't installed."
