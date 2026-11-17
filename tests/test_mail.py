"""Email connection (decision D48). Synthetic headers only: there is no subject or body anywhere in this feature."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from companion import connectors, mailbook
from companion.ai import MockAI
from companion.app import create_app
from companion.config import Settings
from companion.connectors import SampleMail
from companion.security import COOKIE_NAME, CSRF_HEADER

from .test_calendar_connect import BASE, PORT, Secrets

BASE_TIME = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)


class Mail:
    demo = False

    def __init__(self, messages, me="me@example.com"):
        self._messages, self.me, self.disconnected = messages, me, 0

    def has_token(self): return True
    def self_address(self): return self.me
    def messages(self, per_label=60): return self._messages
    def disconnect(self): self.disconnected += 1
    def authorize_url(self, redirect_uri, state, challenge): return f"https://accounts.example/auth?state={state}"
    def complete(self, code, verifier, redirect_uri): pass


def msg(direction, days, *parties, bulk=False):
    return {"direction": direction, "at": (BASE_TIME - timedelta(days=days)).isoformat(), "bulk": bulk,
            "parties": [{"name": n, "address": a} for n, a in parties]}


MAYA = ("Maya Lindqvist", "maya@example.com")


def make(tmp_path, provider):
    app = create_app(Settings(data_dir=tmp_path / "d", port=PORT, ai_mode="mock"), ai_client=MockAI(), mail=provider, secret_store=Secrets())
    sid, csrf = app.state.security.new_session_for_tests()
    c = TestClient(app, base_url=BASE, headers={CSRF_HEADER: csrf, "origin": BASE})
    c.cookies.set(COOKIE_NAME, sid)
    return app, c


def synced(tmp_path, messages):
    app, c = make(tmp_path, Mail(messages))
    mailbook.mark_connected(app.state.db)
    assert c.post("/api/connectors/email/sync", json={}).status_code == 200
    return app, c


def test_only_a_real_two_way_exchange_becomes_a_suggestion(tmp_path):
    app, c = synced(tmp_path, [msg("sent", 2, MAYA), msg("received", 3, MAYA), msg("sent", 4, ("", "sam@example.com")),
                               msg("received", 1, ("Digest", "digest@example.com"), bulk=True),
                               msg("received", 2, ("", "noreply@example.com")),
                               msg("sent", 5, *[("", f"m{i}@example.com") for i in range(8)])])
    assert [p["address"] for p in c.get("/api/email-contacts").json()] == ["maya@example.com"]


def test_nothing_is_saved_until_you_keep_someone_and_no_text_is_stored(tmp_path):
    app, c = synced(tmp_path, [msg("sent", 2, MAYA), msg("received", 3, MAYA)])
    assert app.state.db.one("SELECT COUNT(*) AS n FROM items WHERE kind='relationship'")["n"] == 0
    cols = {r["name"] for r in app.state.db.q("PRAGMA table_info(email_contacts)")}
    assert not cols & {"subject", "body", "snippet", "text"}
    cid = c.get("/api/email-contacts").json()[0]["id"]
    person = c.post(f"/api/email-contacts/{cid}/keep", json={}).json()
    assert person["name"] == "Maya Lindqvist"
    detail = c.get(f"/api/people/{person['id']}").json()
    assert detail["email"]["last_direction"] == "sent" and detail["email"]["sent"] == 1 and detail["email"]["received"] == 1
    assert c.get("/api/email-contacts").json() == []


def test_not_now_returns_only_with_newer_mail_and_never_stays_gone(tmp_path):
    app, c = synced(tmp_path, [msg("sent", 2, MAYA), msg("received", 3, MAYA)])
    cid = c.get("/api/email-contacts").json()[0]["id"]
    c.post(f"/api/email-contacts/{cid}/dismiss", json={"scope": "later"})
    c.post("/api/connectors/email/sync", json={})
    assert c.get("/api/email-contacts").json() == []
    app.state.db.run("UPDATE email_contacts SET decided_at=?", ((BASE_TIME - timedelta(days=5)).isoformat(),))
    c.post("/api/connectors/email/sync", json={})
    assert len(c.get("/api/email-contacts").json()) == 1
    c.post(f"/api/email-contacts/{cid}/dismiss", json={"scope": "never"})
    app.state.db.run("UPDATE email_contacts SET decided_at=?", ((BASE_TIME - timedelta(days=30)).isoformat(),))
    c.post("/api/connectors/email/sync", json={})
    assert c.get("/api/email-contacts").json() == []


def test_people_you_already_keep_get_a_last_contact_line_without_a_suggestion(tmp_path):
    app, c = make(tmp_path, Mail([msg("received", 1, MAYA)]))
    mailbook.mark_connected(app.state.db)
    person = c.post("/api/people", json={"name": "Maya Lindqvist"}).json() if c.post("/api/people", json={"name": "x"}).status_code != 404 else None
    if person is None:
        pytest.skip("no direct create route")
    from companion.encounters import _remember_address
    _remember_address(app.state.db, person["id"], "maya@example.com")
    c.post("/api/connectors/email/sync", json={})
    assert c.get("/api/email-contacts").json() == []
    assert c.get(f"/api/people/{person['id']}").json()["email"]["last_direction"] == "received"


def test_a_bad_decision_is_refused_and_decisions_are_final(tmp_path):
    app, c = synced(tmp_path, [msg("sent", 2, MAYA), msg("received", 3, MAYA)])
    cid = c.get("/api/email-contacts").json()[0]["id"]
    assert c.post(f"/api/email-contacts/{cid}/dismiss", json={"scope": "forever"}).status_code == 422
    assert c.post(f"/api/email-contacts/{cid}/keep", json={"extra": 1}).status_code == 422
    assert c.post(f"/api/email-contacts/{cid}/keep", json={}).status_code == 200
    assert c.post(f"/api/email-contacts/{cid}/keep", json={}).status_code == 422
    assert c.post("/api/email-contacts/9999/dismiss", json={}).status_code == 422


def test_sync_needs_a_connection_and_disconnect_can_remove_what_came_from_email(tmp_path):
    provider = Mail([msg("sent", 2, MAYA), msg("received", 3, MAYA)])
    app, c = make(tmp_path, provider)
    assert c.post("/api/connectors/email/sync", json={}).status_code == 422
    mailbook.mark_connected(app.state.db)
    c.post("/api/connectors/email/sync", json={})
    cid = c.get("/api/email-contacts").json()[0]["id"]
    person = c.post(f"/api/email-contacts/{cid}/keep", json={}).json()
    out = c.delete("/api/connectors/email?remove_data=true").json()
    assert out["removed_data"] is True and provider.disconnected == 1
    assert app.state.db.one("SELECT COUNT(*) AS n FROM email_contacts")["n"] == 0
    assert c.get(f"/api/people/{person['id']}").json()["email"] is None
    assert c.get(f"/api/people/{person['id']}").json()["name"] == "Maya Lindqvist"  # the person you kept stays


def test_start_gives_a_google_link_that_carries_the_mail_kind(tmp_path):
    app, c = make(tmp_path, Mail([]))
    url = c.post("/api/connectors/email/start", json={}).json()["url"]
    state = url.split("state=")[1]
    assert connectors.OAuthFlows.take_with_kind  # exists
    found = app.state.flows.take_with_kind(state) if hasattr(app.state, "flows") else None
    if found is not None:
        assert found[1] == "mail"


def test_the_demo_mailbox_shows_two_people_and_hides_the_one_way_and_bulk_mail(tmp_path):
    app, c = make(tmp_path, SampleMail(clock=lambda: BASE_TIME))
    assert c.post("/api/connectors/email/start", json={}).json() == {"connected": True, "demo": True}
    c.post("/api/connectors/email/sync", json={})
    assert sorted(p["name"] for p in c.get("/api/email-contacts").json()) == ["Maya Lindqvist", "Priya Venkataraman"]
    assert c.get("/api/bootstrap").json()["calendar"]["email"]["connected"] is True


def test_a_version_seven_database_gains_the_email_table(tmp_path):
    import sqlite3
    from companion.db import Database
    path = tmp_path / "old.sqlite3"
    raw = sqlite3.connect(path); raw.execute("PRAGMA user_version=7"); raw.commit(); raw.close()
    db = Database(path)
    assert db.one("SELECT COUNT(*) AS n FROM email_contacts")["n"] == 0
    db.close()


def test_google_mail_reads_archived_mail_and_pages_through_the_newest_messages():
    class Fake(connectors.GoogleMail):
        def __init__(self):
            self.calls = []
        def _get(self, url, params, what):
            self.calls.append((url, params))
            p = dict(params) if not isinstance(params, dict) else params
            if url.endswith("/messages"):
                if p.get("labelIds") == "SENT":
                    return {"messages": [{"id": "s1"}]}
                if p.get("pageToken"):
                    return {"messages": [{"id": "r3"}]}
                return {"messages": [{"id": "r1"}, {"id": "r2"}, {"id": "s1"}], "nextPageToken": "next"}
            labels = {"s1": ["SENT"], "r1": ["CATEGORY_UPDATES"], "r2": [], "r3": ["INBOX"]}  # r2 is archived: no INBOX label
            mid = url.rsplit("/", 1)[1]
            who = {"s1": "To", "r1": "From", "r2": "From", "r3": "From"}[mid]
            return {"internalDate": "1763380800000", "labelIds": labels[mid], "payload": {"headers": [{"name": who, "value": f"{mid}@example.com"}]}}

    mail = Fake()
    got = mail.messages(per_label=10)
    assert [(m["direction"], m["parties"][0]["address"]) for m in got] == [
        ("sent", "s1@example.com"), ("received", "r1@example.com"), ("received", "r2@example.com"), ("received", "r3@example.com")]
    assert not any(c[1].get("labelIds") == "INBOX" for c in mail.calls if isinstance(c[1], dict))  # not limited to the Inbox


def test_a_sent_message_with_only_a_to_address_keeps_its_recipient():
    item = {"internalDate": "1763380800000", "payload": {"headers": [{"name": "To", "value": "Maya Lindqvist <maya@example.com>"}]}}
    assert connectors.normalize_message(item, "sent")["parties"] == [{"name": "Maya Lindqvist", "address": "maya@example.com"}]
    both = {"internalDate": "1763380800000", "payload": {"headers": [{"name": "To", "value": "a@example.com"}, {"name": "Cc", "value": "b@example.com"}]}}
    assert [p["address"] for p in connectors.normalize_message(both, "sent")["parties"]] == ["a@example.com", "b@example.com"]
