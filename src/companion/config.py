"""Settings. Everything has a safe default; environment variables override a few."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

LOOPBACK_HOST = "127.0.0.1"
AI_MODES = ("mock", "live", "off")
# "user" is the plain-language build for testers. "dev" keeps the builder's controls and original wording.
UI_MODES = ("user", "dev")


def default_data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "CareerCompanion"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "career-companion"


def load_google_client_file(path: str | Path, kind: str = "installed") -> dict[str, str]:
    """Read the file Google lets you download for an OAuth client. `installed` is a Desktop app client (the Mac app);
    `web` is a Web application client (the web version, D50). Error messages never include its contents."""
    file = Path(path).expanduser()
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Google client file not found: {file}") from None
    except (OSError, ValueError):
        raise ValueError("The Google client file isn't readable JSON.") from None
    section = data.get(kind) if isinstance(data, dict) else None
    if not isinstance(section, dict):
        if kind == "installed" and isinstance(data, dict) and "web" in data:
            raise ValueError("That client is a Web application. Create a client of type Desktop app instead.")
        if kind == "web" and isinstance(data, dict) and "installed" in data:
            raise ValueError("That client is a Desktop app. The web version needs a client of type Web application.")
        raise ValueError("That file isn't a Google Web application client file." if kind == "web" else "That file isn't a Google Desktop app client file.")
    client_id, secret = str(section.get("client_id", "")).strip(), str(section.get("client_secret", "")).strip()
    if not client_id:
        raise ValueError("That Google client file has no client ID.")
    return {"google_client_id": client_id, "google_client_secret": secret}


@dataclass
class Settings:
    data_dir: Path = field(default_factory=default_data_dir)
    host: str = LOOPBACK_HOST
    port: int = 8765
    ai_mode: str = "mock"
    monthly_budget_usd: float = 20.0
    hard_stop_usd: float = 16.0
    warn_usd: tuple[float, ...] = (10.0, 13.0)
    session_cap_usd: float = 1.0
    day_cap_usd: float = 2.0
    timezone: str = "America/New_York"
    transcript_days: int = 30
    ui_mode: str = "user"
    # Google Calendar sign-in (decision D39). Create a Desktop app OAuth client; see the README. Unset means unconfigured.
    google_client_id: str = ""
    google_client_secret: str = ""
    # The web version (D50): this copy serves one signed-in person behind the web front door, never a port of its own.
    hosted: bool = False
    public_url: str = ""

    def __post_init__(self) -> None:
        if self.host != LOOPBACK_HOST:
            raise ValueError("The app only binds to 127.0.0.1.")
        if self.ai_mode not in AI_MODES:
            raise ValueError(f"ai_mode must be one of {AI_MODES}")
        if self.ui_mode not in UI_MODES:
            raise ValueError(f"ui_mode must be one of {UI_MODES}")
        if not 0 < self.hard_stop_usd <= self.monthly_budget_usd:
            raise ValueError("hard_stop_usd must be positive and within the monthly budget.")
        self.data_dir = Path(self.data_dir)
        if self.hosted and not self.public_url:
            raise ValueError("A hosted copy needs the site's public address.")

    @property
    def db_path(self) -> Path:
        return self.data_dir / "companion.sqlite3"

    @classmethod
    def from_env(cls) -> "Settings":
        kwargs: dict = {}
        if os.environ.get("COMPANION_DATA_DIR"):
            kwargs["data_dir"] = Path(os.environ["COMPANION_DATA_DIR"])
        if os.environ.get("COMPANION_PORT"):
            kwargs["port"] = int(os.environ["COMPANION_PORT"])
        if os.environ.get("COMPANION_AI_MODE"):
            kwargs["ai_mode"] = os.environ["COMPANION_AI_MODE"]
        if os.environ.get("COMPANION_GOOGLE_CLIENT_FILE"):
            kwargs.update(load_google_client_file(os.environ["COMPANION_GOOGLE_CLIENT_FILE"]))  # the two variables below override it
        if os.environ.get("COMPANION_GOOGLE_CLIENT_ID"):
            kwargs["google_client_id"] = os.environ["COMPANION_GOOGLE_CLIENT_ID"].strip()
        if os.environ.get("COMPANION_GOOGLE_CLIENT_SECRET"):
            kwargs["google_client_secret"] = os.environ["COMPANION_GOOGLE_CLIENT_SECRET"].strip()
        if os.environ.get("COMPANION_UI_MODE"):
            kwargs["ui_mode"] = os.environ["COMPANION_UI_MODE"]
        if os.environ.get("COMPANION_TIMEZONE"):
            kwargs["timezone"] = os.environ["COMPANION_TIMEZONE"]
        return cls(**kwargs)
