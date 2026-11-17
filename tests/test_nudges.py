"""Reminders outside the app (decision D46). Time is frozen and the notifier is fake, so nothing real is shown."""

from __future__ import annotations

import json
import plistlib
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from companion import nudge_agent, nudges, people, store
from companion.ai import MockAI
from companion.app import create_app
from companion.cli import main
from companion.config import Settings
from companion.security import COOKIE_NAME, CSRF_HEADER

from .conftest import BASE, PORT
from .test_checkins import kept

NY = ZoneInfo("America/New_York")
CANARY = "Zed Canary"


def at(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, day, hour, minute, tzinfo=NY)


class Notifier:
    supported, reason = True, ""

    def __init__(self, ok=True):
        self.ok, self.sent = ok, []

    def send(self, title, body):
        self.sent.append((title, body))
        return self.ok


@pytest.fixture
def db(tmp_path):
    from companion.db import Database

    d = Database(tmp_path / "n.sqlite3")
    yield d
    d.close()


def turn_on(db, time="09:00", qs="21:00", qe="08:00"):
    nudges.save_settings(db, True, time, qs, qe)


def reminder_for(db, name=CANARY, due="2026-11-17"):
    person = people.save_person(db, None, {"name": name, "org": "", "profile_link": "", "context": "", "notes": "", "category": ""})
    people.set_next_action(db, person["id"], "Send the article", due)
    return person


# ---- when a reminder is shown ---------------------------------------------------------------

def test_off_until_you_turn_it_on(db):
    reminder_for(db)
    n = Notifier()
    assert nudges.run_once(db, n, at(17, 9, 30)) == {"sent": False, "count": 0, "reason": "reminders are off"} and n.sent == []


def test_one_generic_reminder_with_a_count_and_never_a_name(db):
    turn_on(db); reminder_for(db); n = Notifier()
    assert nudges.run_once(db, n, at(17, 9, 30))["sent"] is True
    assert n.sent == [("Link", "1 follow-up due today. Open Link.")]
    assert CANARY not in json.dumps(n.sent) and CANARY not in json.dumps(nudges.get_state(db))


def test_two_people_read_as_a_plural(db):
    turn_on(db); reminder_for(db, "Ada One"); reminder_for(db, "Bo Two"); n = Notifier()
    nudges.run_once(db, n, at(17, 9, 30))
    assert n.sent == [("Link", "2 follow-ups due today. Open Link.")]


@pytest.mark.parametrize("hour,minute,reason", [(0, 5, "quiet hours"), (7, 59, "quiet hours"), (21, 0, "quiet hours"), (23, 15, "quiet hours")])
def test_never_inside_quiet_hours(db, hour, minute, reason):
    turn_on(db); reminder_for(db); n = Notifier()
    assert nudges.run_once(db, n, at(17, hour, minute))["reason"] == reason and n.sent == []


def test_quiet_hours_end_exactly_when_set(db):
    turn_on(db); reminder_for(db)
    assert nudges.run_once(db, Notifier(), at(17, 8, 0))["reason"] == "not time yet"


def test_waits_for_the_chosen_time_and_sends_at_most_once_a_day(db):
    turn_on(db, time="10:30"); reminder_for(db); n = Notifier()
    assert nudges.run_once(db, n, at(17, 10, 0))["reason"] == "not time yet"
    assert nudges.run_once(db, n, at(17, 10, 30))["sent"] is True
    assert nudges.run_once(db, n, at(17, 15, 0))["reason"] == "already sent today"
    assert len(n.sent) == 1


def test_a_computer_that_was_asleep_still_sends_later_the_same_day(db):
    turn_on(db); reminder_for(db); n = Notifier()
    assert nudges.run_once(db, n, at(17, 16, 45))["sent"] is True


def test_the_reminder_time_cannot_sit_inside_quiet_hours_and_must_look_like_a_time(db):
    with pytest.raises(store.RuleError):
        nudges.save_settings(db, True, "22:00", "21:00", "08:00")
    for bad in ("9:00", "25:00", "09:61", "nine"):
        with pytest.raises(store.RuleError):
            nudges.save_settings(db, True, bad, "21:00", "08:00")


def test_only_open_follow_ups_that_are_due_count(db):
    turn_on(db); n = Notifier()
    future = reminder_for(db, "Later Person", due="2026-11-20")
    closed = reminder_for(db, "Done Person")
    store.update(db, "actions", people.next_action(db, closed["id"])["id"], state="done")
    assert nudges.run_once(db, n, at(17, 9, 30))["reason"] == "nothing due" and n.sent == []
    assert nudges.preview(db, at(17, 9, 30)) == {"due": 0, "would_mention": 0, "paused_people": 0}
    assert nudges.run_once(db, n, at(20, 9, 30))["count"] == 1 and future


def test_a_check_in_that_is_due_counts_as_a_follow_up(tmp_path):
    app, c, cid, person = kept(tmp_path)
    turn_on(app.state.db); n = Notifier()
    assert nudges.run_once(app.state.db, n, at(19, 9, 30))["count"] == 1


# ---- stopping when a reminder leads nowhere --------------------------------------------------

def test_two_ignored_reminders_in_a_row_stop_reminders_about_that_person(db):
    turn_on(db); reminder_for(db); n = Notifier()
    assert nudges.run_once(db, n, at(17, 9, 30))["sent"] is True   # first reminder
    assert nudges.run_once(db, n, at(18, 9, 30))["sent"] is True   # still due, so the first went unanswered
    assert nudges.run_once(db, n, at(19, 9, 30))["reason"] == "nothing due"  # second went unanswered too
    assert len(n.sent) == 2
    assert nudges.preview(db, at(19, 9, 30)) == {"due": 1, "would_mention": 0, "paused_people": 1}


def test_acting_on_it_starts_the_count_again(db):
    turn_on(db); person = reminder_for(db); n = Notifier()
    nudges.run_once(db, n, at(17, 9, 30))
    people.complete_next_action(db, person["id"], date(2026, 11, 17))
    assert nudges.run_once(db, n, at(18, 9, 30))["reason"] == "nothing due"
    assert nudges.get_state(db)["ignored"] == {}
    people.set_next_action(db, person["id"], "Send the dataset", "2026-11-19")
    assert nudges.run_once(db, n, at(19, 9, 30))["sent"] is True


def test_resuming_brings_set_aside_people_back(db):
    turn_on(db); reminder_for(db); n = Notifier()
    for day in (17, 18, 19):
        nudges.run_once(db, n, at(day, 9, 30))
    nudges.resume(db)
    assert nudges.run_once(db, n, at(20, 9, 30))["sent"] is True


def test_pausing_holds_reminders_until_the_day_it_ends(db):
    turn_on(db); reminder_for(db); n = Notifier()
    nudges.pause(db, 3, date(2026, 11, 17))
    assert nudges.run_once(db, n, at(19, 9, 30))["reason"] == "paused" and n.sent == []
    assert nudges.run_once(db, n, at(20, 9, 30))["sent"] is True
    for bad in (0, 15):
        with pytest.raises(store.RuleError):
            nudges.pause(db, bad, date(2026, 11, 17))


def test_a_notification_that_could_not_be_shown_is_tried_again_next_pass(db):
    turn_on(db); reminder_for(db); n = Notifier(ok=False)
    assert nudges.run_once(db, n, at(17, 9, 30)) == {"sent": False, "count": 1, "reason": "the notification could not be shown"}
    assert nudges.get_state(db)["last_date"] is None
    n.ok = True
    assert nudges.run_once(db, n, at(17, 9, 45))["sent"] is True


def test_a_dry_run_shows_nothing_and_changes_nothing(db):
    turn_on(db); reminder_for(db); n = Notifier()
    before = nudges.get_state(db)
    assert nudges.run_once(db, n, at(17, 9, 30), dry_run=True) == {"sent": False, "count": 1, "reason": "dry run"}
    assert n.sent == [] and nudges.get_state(db) == before


# ---- the macOS notification and the helper ----------------------------------------------------

def test_the_mac_notification_runs_without_a_shell_and_carries_only_fixed_words_and_a_number(monkeypatch):
    calls = []
    monkeypatch.setattr(nudges.subprocess, "run", lambda *a, **k: calls.append((a, k)) or type("R", (), {"returncode": 0})())
    assert nudges.MacNotifier().send(*nudges.message(3)) is True
    (args,), kwargs = calls[0]
    assert args[:2] == ["osascript", "-e"] and not kwargs.get("shell")
    assert re.fullmatch(r'display notification "\d+ follow-ups? due today\. Open Link\." with title "Link"', args[2])


def test_other_computers_get_a_notifier_that_says_so(monkeypatch):
    monkeypatch.setattr(nudges.sys, "platform", "linux")
    notifier = nudges.build_notifier()
    assert notifier.supported is False and "Mac" in notifier.reason and notifier.send("Link", "x") is False


def test_the_helper_file_runs_the_nudge_command_every_fifteen_minutes(tmp_path):
    data = plistlib.loads(nudge_agent.plist_bytes("/venv/bin/python", tmp_path / "n.log", {"COMPANION_DATA_DIR": "/d", "OTHER": "no"}))
    assert data["Label"] == "com.career-companion.nudge" and data["StartInterval"] == 900 and data["RunAtLoad"] is True
    assert data["ProgramArguments"] == ["/venv/bin/python", "-m", "companion.cli", "nudge"]
    assert data["EnvironmentVariables"] == {"COMPANION_DATA_DIR": "/d"}


def test_installing_and_removing_the_helper(tmp_path):
    calls = []
    runner = lambda cmd, **k: calls.append(cmd) or type("R", (), {"returncode": 0})()
    msg = nudge_agent.install(tmp_path, tmp_path / "data" / "nudge.log", runner=runner, platform="darwin", python="/p", env={})
    assert "Installed" in msg and nudge_agent.is_installed(tmp_path)
    assert [c[:2] for c in calls] == [["launchctl", "bootout"], ["launchctl", "bootstrap"]]
    calls.clear()
    assert nudge_agent.uninstall(tmp_path, runner=runner, platform="darwin") == "Removed the helper."
    assert not nudge_agent.is_installed(tmp_path) and calls[0][:2] == ["launchctl", "bootout"]
    assert nudge_agent.uninstall(tmp_path, runner=runner, platform="darwin") == "The helper wasn't installed."


def test_installing_elsewhere_changes_nothing(tmp_path):
    msg = nudge_agent.install(tmp_path, tmp_path / "n.log", runner=lambda *a, **k: pytest.fail("no commands"), platform="linux")
    assert "Mac" in msg and not nudge_agent.is_installed(tmp_path)


def test_the_command_prints_counts_only(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("COMPANION_DATA_DIR", str(tmp_path)); monkeypatch.setenv("HOME", str(tmp_path))
    from companion.db import Database

    d = Database(tmp_path / "companion.sqlite3"); turn_on(d); reminder_for(d, due="2000-01-01"); d.close()
    assert main(["nudge", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "sent=False" in out and CANARY not in out
    assert main(["nudge", "--status"]) == 0 and "Helper installed: no" in capsys.readouterr().out


# ---- the settings routes ----------------------------------------------------------------------

def signed_in(tmp_path, notifier):
    app = create_app(Settings(data_dir=tmp_path / "d", port=PORT, ai_mode="mock"), ai_client=MockAI(), notifier=notifier)
    sid, csrf = app.state.security.new_session_for_tests()
    client = TestClient(app, base_url=BASE, headers={CSRF_HEADER: csrf, "origin": BASE})
    client.cookies.set(COOKIE_NAME, sid)
    return app, client


def test_settings_routes_validate_and_remember(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    app, c = signed_in(tmp_path, Notifier())
    first = c.get("/api/nudges").json()
    assert first["settings"]["enabled"] is False and first["supported"] is True and first["helper_installed"] is False
    ok = {"enabled": True, "time": "08:30", "quiet_start": "22:00", "quiet_end": "07:00"}
    assert c.put("/api/nudges", json=ok).json() == ok and c.get("/api/nudges").json()["settings"] == ok
    assert c.put("/api/nudges", json={**ok, "time": "23:00"}).status_code == 422   # inside quiet hours
    assert c.put("/api/nudges", json={**ok, "time": "8:30"}).status_code == 422
    assert c.put("/api/nudges", json={**ok, "extra": 1}).status_code == 422


def test_pause_resume_and_the_test_reminder(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    notifier = Notifier()
    app, c = signed_in(tmp_path, notifier)
    assert c.post("/api/nudges/pause", json={"days": 0}).status_code == 422
    until = c.post("/api/nudges/pause", json={"days": 3}).json()["snooze_until"]
    assert until == (nudges.local_now(app.state.settings).date() + timedelta(days=3)).isoformat()
    assert c.get("/api/nudges").json()["snooze_until"] == until
    assert c.post("/api/nudges/resume", json={}).json() == {"resumed": True} and c.get("/api/nudges").json()["snooze_until"] is None
    assert c.post("/api/nudges/test", json={}).json() == {"sent": True, "reason": ""}
    assert notifier.sent == [("Link", "This is a test reminder. Nothing is due.")]


def test_the_test_reminder_explains_when_this_computer_cannot_show_one(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    app, c = signed_in(tmp_path, nudges.UnsupportedNotifier())
    out = c.post("/api/nudges/test", json={}).json()
    assert out["sent"] is False and "Mac" in out["reason"] and c.get("/api/nudges").json()["supported"] is False
