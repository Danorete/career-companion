"""Post-event check-in (decision D44). Synthetic data only; time is frozen, so nothing waits."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from companion import encounters, people
from companion.db import Database

from .test_calendar_connect import Provider, event, maya, signed_in

ENDS = datetime(2026, 11, 18, 16, 0, tzinfo=timezone.utc)  # the helper's event runs 15:00 to 16:00


@pytest.fixture
def clock(monkeypatch):
    now = [ENDS + timedelta(hours=2)]
    monkeypatch.setattr(encounters, "_now", lambda: now[0])
    return now


def kept(tmp_path, title="Coffee chat"):
    app, c = signed_in(tmp_path, Provider([event(title, [maya()])]))
    encounters.mark_connected(app.state.db)
    c.post("/api/connectors/calendar/sync", json={})
    cand = c.get("/api/encounters").json()[0]
    person = c.post(f"/api/encounters/{cand['id']}/keep", json={}).json()
    return app, c, cand["id"], person


def due(c):
    return c.get("/api/checkins").json()


def logs(app):
    return app.state.db.q("SELECT * FROM interactions WHERE source='calendar_checkin'")


def test_asked_an_hour_after_the_meeting_and_expired_after_a_week(tmp_path, clock):
    app, c, cid, person = kept(tmp_path)
    clock[0] = ENDS + timedelta(minutes=59)
    assert due(c) == []
    clock[0] = ENDS + timedelta(hours=1)
    [ask] = due(c)
    assert (ask["id"], ask["name"], ask["title"]) == (cid, "Maya Lindqvist", "Coffee chat")
    clock[0] = ENDS + timedelta(days=8)
    assert due(c) == []
    assert app.state.db.one("SELECT checkin_state FROM encounter_candidates WHERE id=?", (cid,))["checkin_state"] == "expired"
    assert logs(app) == []  # an expired question writes nothing


def test_only_people_you_kept_are_asked_about(tmp_path, clock):
    app, c = signed_in(tmp_path, Provider([event("Coffee chat", [maya()])]))
    encounters.mark_connected(app.state.db); c.post("/api/connectors/calendar/sync", json={})
    assert len(c.get("/api/encounters").json()) == 1 and due(c) == []


@pytest.mark.parametrize("answer,words", [("great", "Went well."), ("fine", "Went fine.")])
def test_great_and_fine_save_a_note_dated_to_the_meeting(tmp_path, clock, answer, words):
    app, c, cid, person = kept(tmp_path)
    out = c.post(f"/api/checkins/{cid}/answer", json={"answer": answer, "note": "  we talked about   internships "}).json()
    assert out["logged"] is True
    [log] = logs(app)
    assert log["item_id"] == person["id"] and (log["when_kind"], log["occurred_on"]) == ("exact", "2026-11-18")
    assert log["note"] == f"Coffee chat. {words} we talked about internships"
    assert due(c) == []
    timeline = c.get(f"/api/people/{person['id']}").json()["timeline"]
    assert any(entry["id"] == log["id"] for entry in timeline)


def test_skip_saves_nothing_and_does_not_ask_again(tmp_path, clock):
    app, c, cid, person = kept(tmp_path)
    assert c.post(f"/api/checkins/{cid}/answer", json={"answer": "skip", "note": "ignored"}).json()["logged"] is False
    assert logs(app) == [] and due(c) == []
    assert app.state.db.one("SELECT checkin_state FROM encounter_candidates WHERE id=?", (cid,))["checkin_state"] == "skipped"


def test_a_promise_becomes_the_next_step_with_a_reminder(tmp_path, clock):
    app, c, cid, person = kept(tmp_path)
    out = c.post(f"/api/checkins/{cid}/answer", json={"answer": "great", "promise": "send her the article"}).json()
    assert out["next_step"] is True and out["promise_in_note"] is False
    step = people.next_action(app.state.db, person["id"])
    assert step["title"] == "send her the article"
    reminder = app.state.db.one("SELECT due_on FROM reminders WHERE action_id=?", (step["id"],))
    assert reminder["due_on"] == "2026-11-21"  # three days after the check-in
    assert "I said I would: send her the article" in logs(app)[0]["note"] and logs(app)[0]["commitments"] == "send her the article"


def test_a_promise_never_replaces_a_next_step_you_already_have(tmp_path, clock):
    app, c, cid, person = kept(tmp_path)
    people.set_next_action(app.state.db, person["id"], "Send the dataset", "2026-11-20")
    out = c.post(f"/api/checkins/{cid}/answer", json={"answer": "fine", "promise": "intro her to Sam"}).json()
    assert out["next_step"] is False and out["promise_in_note"] is True
    assert people.next_action(app.state.db, person["id"])["title"] == "Send the dataset"
    assert "intro her to Sam" in logs(app)[0]["note"]


def test_each_check_in_is_answered_once_and_bad_input_is_refused(tmp_path, clock):
    app, c, cid, person = kept(tmp_path)
    assert c.post(f"/api/checkins/{cid}/answer", json={"answer": "amazing"}).status_code == 422
    assert c.post(f"/api/checkins/{cid}/answer", json={"answer": "fine", "note": "x" * 1001}).status_code == 422
    assert c.post(f"/api/checkins/{cid}/answer", json={"answer": "fine", "extra": 1}).status_code == 422
    assert c.post("/api/checkins/99999/answer", json={"answer": "fine"}).status_code == 422
    assert c.post(f"/api/checkins/{cid}/answer", json={"answer": "fine"}).status_code == 200
    assert c.post(f"/api/checkins/{cid}/answer", json={"answer": "great"}).status_code == 422
    assert len(logs(app)) == 1


def test_a_candidate_you_never_kept_cannot_be_answered(tmp_path, clock):
    app, c = signed_in(tmp_path, Provider([event("Coffee chat", [maya()])]))
    encounters.mark_connected(app.state.db); c.post("/api/connectors/calendar/sync", json={})
    cid = c.get("/api/encounters").json()[0]["id"]
    assert c.post(f"/api/checkins/{cid}/answer", json={"answer": "great"}).status_code == 422 and logs(app) == []


def test_disconnecting_and_removing_calendar_data_keeps_the_notes_you_saved(tmp_path, clock):
    app, c, cid, person = kept(tmp_path)
    c.post(f"/api/checkins/{cid}/answer", json={"answer": "great"})
    c.delete("/api/connectors/calendar?remove_data=true")
    assert app.state.db.one("SELECT COUNT(*) AS n FROM encounter_candidates")["n"] == 0
    assert len(logs(app)) == 1 and logs(app)[0]["item_id"] == person["id"]


def test_the_page_is_told_how_many_check_ins_are_waiting(tmp_path, clock):
    app, c, cid, person = kept(tmp_path)
    assert c.get("/api/bootstrap").json()["calendar"]["checkins"] == 1
    c.post(f"/api/checkins/{cid}/answer", json={"answer": "skip"})
    assert c.get("/api/bootstrap").json()["calendar"]["checkins"] == 0


def test_a_version_six_database_gains_the_check_in_columns_and_keeps_its_rows(tmp_path):
    path = tmp_path / "old.sqlite3"
    raw = sqlite3.connect(path)
    raw.execute("CREATE TABLE encounter_candidates (id INTEGER PRIMARY KEY, source TEXT NOT NULL, event_id TEXT NOT NULL, address TEXT NOT NULL,"
                " name TEXT NOT NULL, name_guessed INTEGER NOT NULL DEFAULT 0, title TEXT NOT NULL DEFAULT '', starts_at TEXT NOT NULL,"
                " ends_at TEXT NOT NULL DEFAULT '', reason TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending', item_id INTEGER,"
                " created_at TEXT NOT NULL, decided_at TEXT, UNIQUE(source, event_id, address))")
    raw.execute("INSERT INTO encounter_candidates(source,event_id,address,name,title,starts_at,reason,created_at) VALUES"
                " ('google_calendar','e1','a@example.com','Old Row','Coffee','2026-11-01T10:00:00Z','kept from before','2026-11-01')")
    raw.commit(); raw.close()
    db = Database(path)
    row = db.one("SELECT * FROM encounter_candidates")
    assert (row["name"], row["checkin_state"], row["checkin_at"], row["interaction_id"]) == ("Old Row", "open", None, None)
    assert db.one("PRAGMA user_version")["user_version"] == 7
    db.close()
