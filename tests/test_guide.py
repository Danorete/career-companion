"""The step-by-step guide for adding a person (decision D52). Synthetic data; time is frozen by the app's clock."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from companion import encounters, mailbook, people, services

from .test_calendar_connect import Provider, event, maya, signed_in
from .test_mail import MAYA as MAIL_MAYA, Mail, make, msg


def today(app):
    return services.local_today(app.state.settings)


def interactions(app, pid):
    return app.state.db.q("SELECT * FROM interactions WHERE item_id=?", (pid,))


def test_every_answer_is_saved_together(tmp_path):
    app, c = signed_in(tmp_path, Provider([]))
    out = c.post("/api/guide/connection", json={
        "name": "  Priya   Raman ", "org": "Deloitte", "context": "Met at the fall career fair", "when": {"kind": "today"},
        "memory": "Works in analytics consulting. Said to email her about the spring internship.",
        "next_step": "Send a thank-you note", "remind_in_days": 3}).json()
    person = out["person"]
    assert (person["name"], person["org"], person["context"]) == ("Priya Raman", "Deloitte", "Met at the fall career fair")
    [log] = interactions(app, person["id"])
    assert log["note"].startswith("Works in analytics consulting") and log["occurred_on"] == today(app).isoformat()
    step = people.next_action(app.state.db, person["id"])
    assert step["title"] == "Send a thank-you note"
    reminder = app.state.db.one("SELECT due_on FROM reminders WHERE action_id=?", (step["id"],))
    assert reminder["due_on"] == (today(app) + timedelta(days=3)).isoformat() == out["remind_on"]
    assert out["logged"] is True and out["next_step"] == "Send a thank-you note"


def test_a_name_alone_is_enough_and_saves_nothing_else(tmp_path):
    app, c = signed_in(tmp_path, Provider([]))
    out = c.post("/api/guide/connection", json={"name": "Sam"}).json()
    assert out["logged"] is False and out["next_step"] is None and out["remind_on"] is None
    assert interactions(app, out["person"]["id"]) == [] and people.next_action(app.state.db, out["person"]["id"]) is None


def test_how_you_met_becomes_a_dated_line_when_nothing_else_was_remembered(tmp_path):
    app, c = signed_in(tmp_path, Provider([]))
    out = c.post("/api/guide/connection", json={"name": "Sam", "context": "Met in Stats 201", "when": {"kind": "yesterday"}}).json()
    [log] = interactions(app, out["person"]["id"])
    assert log["note"] == "Met in Stats 201" and log["occurred_on"] == (today(app) - timedelta(days=1)).isoformat()


def test_a_next_step_without_a_reminder_day_has_no_reminder(tmp_path):
    app, c = signed_in(tmp_path, Provider([]))
    out = c.post("/api/guide/connection", json={"name": "Sam", "next_step": "Connect on LinkedIn"}).json()
    step = people.next_action(app.state.db, out["person"]["id"])
    assert step["title"] == "Connect on LinkedIn" and out["remind_on"] is None
    assert app.state.db.one("SELECT COUNT(*) AS n FROM reminders")["n"] == 0


@pytest.mark.parametrize("body", [
    {"name": ""}, {"name": "   "}, {"name": "x" * 121}, {"name": "Sam", "next_step": "x" * 201},
    {"name": "Sam", "memory": "x" * 2001}, {"name": "Sam", "remind_in_days": 61}, {"name": "Sam", "extra": 1},
    {"name": "Sam", "when": {"kind": "date", "date": "2026-02-31"}}, {"name": "Sam", "when": {"kind": "approx", "text": ""}},
    {"name": "Sam", "source": {"kind": "calendar", "id": 999}}, {"name": "Sam", "source": {"kind": "linkedin", "id": 1}},
])
def test_bad_answers_are_refused_before_anything_is_written(tmp_path, body):
    app, c = signed_in(tmp_path, Provider([]))
    assert c.post("/api/guide/connection", json=body).status_code == 422
    assert app.state.db.one("SELECT COUNT(*) AS n FROM items WHERE kind='relationship'")["n"] == 0
    assert app.state.db.one("SELECT COUNT(*) AS n FROM interactions")["n"] == 0


def test_starting_from_someone_in_the_calendar_keeps_that_suggestion(tmp_path):
    app, c = signed_in(tmp_path, Provider([event("Coffee chat", [maya()])]))
    encounters.mark_connected(app.state.db)
    c.post("/api/connectors/calendar/sync", json={})
    cand = c.get("/api/encounters").json()[0]
    out = c.post("/api/guide/connection", json={"name": "Maya L.", "context": "Coffee chat after the panel",
                                                "source": {"kind": "calendar", "id": cand["id"]},
                                                "next_step": "Send the article", "remind_in_days": 2}).json()
    row = app.state.db.one("SELECT state, item_id FROM encounter_candidates WHERE id=?", (cand["id"],))
    assert row == {"state": "kept", "item_id": out["person"]["id"]}
    assert out["person"]["name"] == "Maya L." and out["person"]["context"] == "Coffee chat after the panel"
    assert app.state.db.one("SELECT COUNT(*) AS n FROM items WHERE kind='relationship'")["n"] == 1
    assert c.get("/api/encounters").json() == []
    again = c.post("/api/guide/connection", json={"name": "Maya", "source": {"kind": "calendar", "id": cand["id"]}})
    assert again.status_code == 422 and "already decided" in again.json()["error"]


def test_starting_from_someone_you_email_keeps_that_suggestion(tmp_path):
    app, c = make(tmp_path, Mail([msg("sent", 2, MAIL_MAYA), msg("received", 3, MAIL_MAYA)]))
    mailbook.mark_connected(app.state.db)
    c.post("/api/connectors/email/sync", json={})
    contact = c.get("/api/email-contacts").json()[0]
    out = c.post("/api/guide/connection", json={"name": "Maya Lindqvist", "source": {"kind": "email", "id": contact["id"]}}).json()
    assert app.state.db.one("SELECT state FROM email_contacts WHERE id=?", (contact["id"],))["state"] == "kept"
    assert c.get(f"/api/people/{out['person']['id']}").json()["email"]["sent"] == 1
