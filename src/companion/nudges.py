"""Reminders outside the app (decision D46, from D39).

One desktop reminder a day, at most, saying how many follow-ups are due and never who. It runs from a small
local helper, not from a server, and it involves no AI. The wording is generic on purpose: a notification is
shown on a lock screen and stored by the operating system.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import encounters, store
from .config import Settings
from .db import Database

SETTINGS_KEY = "nudge_settings"
STATE_KEY = "nudge_state"
DEFAULTS = {"enabled": False, "time": "09:00", "quiet_start": "21:00", "quiet_end": "08:00"}
MAX_IGNORED = 2        # after two reminders in a row that led to nothing, stop reminding about that person
MAX_PAUSE_DAYS = 14
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def local_now(settings: Settings) -> datetime:
    return datetime.now(ZoneInfo(settings.timezone))


# ---- notifier -------------------------------------------------------------------------

class MacNotifier:
    """Shows a macOS notification through `osascript`. The text is built from fixed words and one number, never from your data."""

    supported = True
    reason = ""

    def send(self, title: str, body: str) -> bool:
        assert '"' not in title + body and "\\" not in title + body  # fixed generic text only
        try:
            done = subprocess.run(["osascript", "-e", f'display notification "{body}" with title "{title}"'],
                                  capture_output=True, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError):
            return False
        return done.returncode == 0


class UnsupportedNotifier:
    supported = False
    reason = "Desktop reminders need a Mac for now."

    def send(self, title: str, body: str) -> bool:
        return False


def build_notifier():
    return MacNotifier() if sys.platform == "darwin" and shutil.which("osascript") else UnsupportedNotifier()


# ---- settings and state ---------------------------------------------------------------

def _minutes(value: str) -> int:
    return int(value[:2]) * 60 + int(value[3:])


def in_quiet_hours(minute: int, start: str, end: str) -> bool:
    a, b = _minutes(start), _minutes(end)
    if a == b:
        return False
    return a <= minute < b if a < b else (minute >= a or minute < b)


def get_settings(db: Database) -> dict:
    row = db.one("SELECT value FROM kv WHERE key=?", (SETTINGS_KEY,))
    return {**DEFAULTS, **(json.loads(row["value"]) if row else {})}


def save_settings(db: Database, enabled: bool, time: str, quiet_start: str, quiet_end: str) -> dict:
    for label, value in (("The reminder time", time), ("The start of quiet hours", quiet_start), ("The end of quiet hours", quiet_end)):
        if not HHMM.match(value):
            raise store.RuleError(f"{label} must look like 09:30.")
    if in_quiet_hours(_minutes(time), quiet_start, quiet_end):
        raise store.RuleError("Pick a reminder time outside your quiet hours.")
    value = {"enabled": bool(enabled), "time": time, "quiet_start": quiet_start, "quiet_end": quiet_end}
    db.run("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (SETTINGS_KEY, json.dumps(value)))
    db.log("nudges_settings", "enabled" if enabled else "disabled")
    return value


def get_state(db: Database) -> dict:
    row = db.one("SELECT value FROM kv WHERE key=?", (STATE_KEY,))
    return {"last_date": None, "last_items": [], "ignored": {}, "snooze_until": None, **(json.loads(row["value"]) if row else {})}


def _save_state(db: Database, state: dict) -> None:
    db.run("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (STATE_KEY, json.dumps(state)))


def pause(db: Database, days: int, today: date) -> dict:
    if not 1 <= days <= MAX_PAUSE_DAYS:
        raise store.RuleError(f"Pause for 1 to {MAX_PAUSE_DAYS} days.")
    state = get_state(db)
    state["snooze_until"] = (today + timedelta(days=days)).isoformat()
    _save_state(db, state)
    return state


def resume(db: Database) -> dict:
    """Ends a pause and lets people who were set aside after two unanswered reminders come back."""
    state = get_state(db)
    state["snooze_until"], state["ignored"] = None, {}
    _save_state(db, state)
    return state


# ---- what is due ----------------------------------------------------------------------

def due_keys(db: Database, current: datetime) -> list[str]:
    """Identifiers only: `p<id>` for a person with a check-in or reminder due, `a<id>` for a reminder not tied to a person."""
    keys: set[str] = {f"p{c['item_id']}" for c in encounters.due_checkins(db, current)}
    for r in store.due_reminders(db, current.date()):
        action = store.get(db, "actions", r["action_id"]) if r["action_id"] else None
        if action and action["state"] in store.OPEN_STATES:
            keys.add(f"p{action['item_id']}" if action["item_id"] else f"a{action['id']}")
    return sorted(keys)


def message(count: int) -> tuple[str, str]:
    return "Link", f"{count} follow-up{'s' if count != 1 else ''} due today. Open Link."


def _eligible(keys: list[str], ignored: dict) -> list[str]:
    return [k for k in keys if ignored.get(k, 0) < MAX_IGNORED]


def preview(db: Database, current: datetime) -> dict:
    """What a reminder would say right now. Changes nothing."""
    state = get_state(db)
    keys = due_keys(db, current)
    return {"due": len(keys), "would_mention": len(_eligible(keys, state["ignored"])),
            "paused_people": sum(1 for k in keys if state["ignored"].get(k, 0) >= MAX_IGNORED)}


def run_once(db: Database, notifier, current: datetime, dry_run: bool = False) -> dict:
    """One pass of the helper. Returns counts and a reason only, so its output is safe to log."""
    settings, state = get_settings(db), get_state(db)
    today = current.date().isoformat()
    if not settings["enabled"]:
        return {"sent": False, "count": 0, "reason": "reminders are off"}
    if state["snooze_until"] and today < state["snooze_until"]:
        return {"sent": False, "count": 0, "reason": "paused"}
    minute = current.hour * 60 + current.minute
    if in_quiet_hours(minute, settings["quiet_start"], settings["quiet_end"]):
        return {"sent": False, "count": 0, "reason": "quiet hours"}
    if minute < _minutes(settings["time"]):
        return {"sent": False, "count": 0, "reason": "not time yet"}
    if state["last_date"] == today:
        return {"sent": False, "count": 0, "reason": "already sent today"}
    keys = due_keys(db, current)
    ignored = dict(state["ignored"])
    for k in state["last_items"]:  # score yesterday's reminder: still due means it led to nothing
        if k in keys:
            ignored[k] = ignored.get(k, 0) + 1
        else:
            ignored.pop(k, None)
    chosen = _eligible(keys, ignored)
    if not chosen:
        if not dry_run:
            _save_state(db, {**state, "ignored": ignored, "last_items": [], "last_date": today if state["last_items"] else state["last_date"]})
        return {"sent": False, "count": 0, "reason": "nothing due"}
    if dry_run:
        return {"sent": False, "count": len(chosen), "reason": "dry run"}
    if not notifier.send(*message(len(chosen))):
        db.log("nudge_failed", f"count={len(chosen)}")
        return {"sent": False, "count": len(chosen), "reason": "the notification could not be shown"}  # tried again next pass
    _save_state(db, {**state, "last_date": today, "last_items": chosen, "ignored": ignored})
    db.log("nudge_sent", f"count={len(chosen)}")
    return {"sent": True, "count": len(chosen), "reason": "sent"}
