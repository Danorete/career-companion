"""Calendar connection (decisions D39, D43). Synthetic data only; no network and no real sign-in."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient

from companion import connectors, encounters
from companion.ai import MockAI
from companion.app import create_app
from companion.config import Settings
from companion.security import COOKIE_NAME, CSRF_HEADER

from .conftest import BASE, PORT

NOW = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
CALLBACK = "/connect/google/callback"


class Secrets:
    """Dictionary-backed stand-in for the keychain."""

    def __init__(self):
        self.values: dict[str, str] = {}

    def get(self, account):
        return self.values.get(account)

    def set(self, account, value):
        self.values[account] = value

    def delete(self, account):
        self.values.pop(account, None)


def attendee(address, name="", *, me=False, response="accepted", resource=False):
    return {"email": address, "name": name, "self": me, "response": response, "resource": resource}


def event(title, others, *, recurring=False, all_day=False, status="confirmed", me_response="accepted", key=None):
    return {"id": key or title, "title": title, "start": "2026-11-18T15:00:00+00:00", "end": "2026-11-18T16:00:00+00:00",
            "all_day": all_day, "status": status, "recurring": recurring,
            "attendees": [attendee("you@example.com", me=True, response=me_response)] + others}


def maya(): return attendee("maya.lindqvist@example.com", "Maya Lindqvist")


class Provider:
    demo = False
    configured = True

    def __init__(self, events):
        self._events, self.disconnects = events, 0

    def has_token(self): return True
    def events(self, a, b): return self._events
    def disconnect(self): self.disconnects += 1
    def authorize_url(self, *a): raise AssertionError("not used")
    def complete(self, *a): raise AssertionError("not used")


def signed_in(tmp_path, provider, secrets=None):
    app = create_app(Settings(data_dir=tmp_path / "d", port=PORT, ai_mode="mock"), ai_client=MockAI(), calendar=provider, secret_store=secrets or Secrets())
    sid, csrf = app.state.security.new_session_for_tests()
    client = TestClient(app, base_url=BASE, headers={CSRF_HEADER: csrf, "origin": BASE})
    client.cookies.set(COOKIE_NAME, sid)
    return app, client


# ---- which events become suggestions ----------------------------------------------------

@pytest.mark.parametrize("ev,expect", [
    (event("Coffee chat", [maya()]), 1),
    (event("Project sync", [maya()]), 1),
    (event("Weekly lecture", [maya()], recurring=True), 0),
    (event("Coffee chat", [maya()], recurring=True), 1),
    (event("Club social", [attendee(f"p{i}@example.com") for i in range(8)]), 0),
    (event("Networking mixer", [attendee(f"p{i}@example.com") for i in range(8)]), 8),
    (event("Coffee chat", [maya()], all_day=True), 0),
    (event("Coffee chat", [maya()], status="cancelled"), 0),
    (event("Coffee chat", [maya()], me_response="declined"), 0),
    (event("Study block", []), 0),
    (event("Standup", [attendee("noreply@example.com"), attendee("calendar-notification@example.com")]), 0),
    (event("Room booking", [attendee("room1@resource.calendar.google.com", resource=True)]), 0),
])
def test_detection_rules(ev, expect):
    assert len(encounters.detect(ev, set())) == expect


def test_a_name_is_guessed_from_the_address_and_marked_as_a_guess():
    [c] = encounters.detect(event("Coffee chat", [attendee("sam.ortega@example.com")]), set())
    assert (c["name"], c["name_guessed"]) == ("Sam Ortega", 1)
    [c] = encounters.detect(event("Coffee chat", [maya()]), set())
    assert (c["name"], c["name_guessed"]) == ("Maya Lindqvist", 0)


def test_ignored_addresses_are_not_suggested():
    assert encounters.detect(event("Coffee chat", [maya()]), {"maya.lindqvist@example.com"}) == []


# ---- sync, keep, dismiss ----------------------------------------------------------------

def test_sync_finds_people_once_and_keeps_nothing_until_clicked(tmp_path):
    app, c = signed_in(tmp_path, connectors.SampleCalendar(clock=lambda: NOW))
    assert c.post("/api/connectors/calendar/start", json={}).json() == {"connected": True, "demo": True}
    first = c.post("/api/connectors/calendar/sync", json={}).json()
    assert first["found"] == 3 and c.post("/api/connectors/calendar/sync", json={}).json()["found"] == 0
    found = c.get("/api/encounters").json()
    assert {x["name"] for x in found} == {"Maya Lindqvist", "Priya Venkataraman", "Sam Ortega"}
    assert c.get("/api/people").json() == []  # a suggestion is not a person


def test_keeping_saves_a_person_and_no_conversation(tmp_path):
    app, c = signed_in(tmp_path, connectors.SampleCalendar(clock=lambda: NOW))
    c.post("/api/connectors/calendar/start", json={}); c.post("/api/connectors/calendar/sync", json={})
    cand = next(x for x in c.get("/api/encounters").json() if x["name"] == "Maya Lindqvist")
    person = c.post(f"/api/encounters/{cand['id']}/keep", json={}).json()
    assert person["name"] == "Maya Lindqvist"
    assert app.state.db.q("SELECT COUNT(*) AS n FROM interactions")[0]["n"] == 0  # an invitation isn't a conversation
    assert c.post(f"/api/encounters/{cand['id']}/keep", json={}).status_code == 422  # decided once
    assert all(x["id"] != cand["id"] for x in c.get("/api/encounters").json())


def test_a_guessed_name_can_be_corrected_and_blank_is_refused(tmp_path):
    app, c = signed_in(tmp_path, connectors.SampleCalendar(clock=lambda: NOW))
    c.post("/api/connectors/calendar/start", json={}); c.post("/api/connectors/calendar/sync", json={})
    cand = next(x for x in c.get("/api/encounters").json() if x["name_guessed"])
    assert c.post(f"/api/encounters/{cand['id']}/keep", json={"name": "  "}).status_code == 422
    assert c.post(f"/api/encounters/{cand['id']}/keep", json={"name": "Samuel Ortega"}).json()["name"] == "Samuel Ortega"


def test_a_known_address_is_offered_as_the_same_person(tmp_path):
    ev = [event("Coffee chat", [maya()], key="a"), event("Follow-up coffee", [maya()], key="b")]
    app, c = signed_in(tmp_path, Provider(ev))
    encounters.mark_connected(app.state.db)
    c.post("/api/connectors/calendar/sync", json={})
    first, second = c.get("/api/encounters").json()
    person = c.post(f"/api/encounters/{first['id']}/keep", json={}).json()
    [left] = c.get("/api/encounters").json()
    assert left["matches"] == [{"id": person["id"], "name": "Maya Lindqvist", "why": "Same email address"}]
    linked = c.post(f"/api/encounters/{left['id']}/keep", json={"person_id": person["id"]}).json()
    assert linked["id"] == person["id"] and len(c.get("/api/people").json()) == 1


def test_dismissing_a_person_stops_future_suggestions(tmp_path):
    ev = [event("Coffee chat", [maya()], key="a"), event("Catch-up coffee", [maya()], key="b")]
    app, c = signed_in(tmp_path, Provider(ev))
    encounters.mark_connected(app.state.db)
    c.post("/api/connectors/calendar/sync", json={})
    first = c.get("/api/encounters").json()[0]
    assert c.post(f"/api/encounters/{first['id']}/dismiss", json={"scope": "person"}).status_code == 200
    assert c.get("/api/encounters").json() == []
    assert c.post("/api/connectors/calendar/sync", json={}).json()["found"] == 0
    assert c.post(f"/api/encounters/{first['id']}/dismiss", json={"scope": "nobody"}).status_code == 422


def test_disconnect_removes_calendar_data_but_keeps_people_you_kept(tmp_path):
    provider = Provider([event("Coffee chat", [maya()])])
    app, c = signed_in(tmp_path, provider)
    encounters.mark_connected(app.state.db)
    c.post("/api/connectors/calendar/sync", json={})
    cand = c.get("/api/encounters").json()[0]
    person = c.post(f"/api/encounters/{cand['id']}/keep", json={}).json()
    assert c.delete("/api/connectors/calendar?remove_data=true").json() == {"disconnected": True, "removed_data": True}
    assert provider.disconnects == 1
    assert app.state.db.q("SELECT COUNT(*) AS n FROM encounter_candidates")[0]["n"] == 0
    assert app.state.db.one("SELECT 1 FROM kv WHERE key LIKE 'person_address:%'") is None
    assert c.get("/api/connectors/calendar").json()["connected"] is False
    assert c.get(f"/api/people/{person['id']}").status_code == 200


def test_delete_everything_cancels_the_sign_in(tmp_path):
    provider = Provider([])
    app, c = signed_in(tmp_path, provider)
    assert c.post("/api/wipe", json={"confirm": "DELETE EVERYTHING"}).status_code == 200
    assert provider.disconnects == 1


def test_export_includes_candidates_but_never_a_token(tmp_path):
    secrets = Secrets(); secrets.set(connectors.TOKEN_ACCOUNT, "REFRESH-TOKEN-CANARY")
    app, c = signed_in(tmp_path, Provider([event("Coffee chat", [maya()])]), secrets)
    encounters.mark_connected(app.state.db); c.post("/api/connectors/calendar/sync", json={})
    body = c.get("/api/export").text
    assert "encounter_candidates" in body and "maya.lindqvist@example.com" in body
    assert "REFRESH-TOKEN-CANARY" not in body
    assert b"REFRESH-TOKEN-CANARY" not in app.state.db.path.read_bytes()
    assert "REFRESH-TOKEN-CANARY" not in json.dumps(app.state.db.q("SELECT * FROM activity"))


def test_without_a_provider_the_page_is_told_it_is_unavailable(tmp_path):
    app = create_app(Settings(data_dir=tmp_path / "d", port=PORT, ai_mode="mock"), ai_client=MockAI(), secret_store=Secrets())
    sid, csrf = app.state.security.new_session_for_tests()
    c = TestClient(app, base_url=BASE, headers={CSRF_HEADER: csrf, "origin": BASE}); c.cookies.set(COOKIE_NAME, sid)
    assert c.get("/api/bootstrap").json()["calendar"]["available"] is False
    assert c.post("/api/connectors/calendar/start", json={}).status_code == 422


# ---- sign-in handshake and what leaves the computer -----------------------------------------

def google(handler, secrets=None, clock=None):
    return connectors.GoogleCalendar("client-id", "client-secret", secrets or Secrets(), transport=httpx.MockTransport(handler), clock=clock or (lambda: 1000.0))


def ok_handler(request):
    if request.url.path == "/token":
        form = parse_qs(request.content.decode())
        if form["grant_type"] == ["authorization_code"]:
            return httpx.Response(200, json={"access_token": "ACCESS", "refresh_token": "REFRESH", "expires_in": 3600})
        return httpx.Response(200, json={"access_token": "ACCESS2", "expires_in": 3600})
    if request.url.path == "/calendar/v3/calendars/primary/events":
        return httpx.Response(200, json={"items": [{"id": "e1", "summary": "Coffee chat", "status": "confirmed",
                    "start": {"dateTime": "2026-11-18T15:00:00Z"}, "end": {"dateTime": "2026-11-18T16:00:00Z"},
                    "attendees": [{"email": "you@example.com", "self": True, "responseStatus": "accepted"},
                                  {"email": "Maya.Lindqvist@Example.com", "displayName": "Maya Lindqvist"}]}]})
    return httpx.Response(200, json={})


def test_authorize_url_uses_pkce_state_and_read_only_scope():
    url = urlsplit(google(ok_handler).authorize_url(f"{BASE}{CALLBACK}", "STATE", "CHALLENGE"))
    q = parse_qs(url.query)
    assert url.netloc == "accounts.google.com"
    assert q["scope"] == ["https://www.googleapis.com/auth/calendar.readonly"]
    assert q["code_challenge"] == ["CHALLENGE"] and q["code_challenge_method"] == ["S256"] and q["state"] == ["STATE"]
    assert q["redirect_uri"] == [f"{BASE}{CALLBACK}"] and "client_secret" not in q


def test_only_google_hosts_over_https_can_be_reached():
    seen = []
    transport = connectors.ConnectorTransport(httpx.MockTransport(lambda r: seen.append(r) or httpx.Response(200)))
    for url in ("https://example.com/", "http://oauth2.googleapis.com/token", "https://oauth2.googleapis.com.evil.test/token",
                "https://www.linkedin.com/feed/", "https://api.anthropic.com/v1/messages"):
        with pytest.raises(connectors.NeverSent):
            transport.handle_request(httpx.Request("GET", url))
    assert seen == []
    transport.handle_request(httpx.Request("GET", "https://www.googleapis.com/calendar/v3/calendars/primary/events"))
    assert len(seen) == 1


def test_events_ask_google_only_for_the_fields_link_keeps():
    requests = []
    cal = google(lambda r: requests.append(r) or ok_handler(r))
    cal.store.set(connectors.TOKEN_ACCOUNT, "REFRESH")
    [ev] = cal.events(NOW, NOW + timedelta(days=1))
    asked = parse_qs(urlsplit(str(requests[-1].url)).query)["fields"][0]
    assert "description" not in asked and "location" not in asked
    assert ev["attendees"][1]["email"] == "maya.lindqvist@example.com"


def test_a_refused_refresh_removes_the_saved_sign_in_and_shows_a_safe_message():
    secrets = Secrets(); secrets.set(connectors.TOKEN_ACCOUNT, "REFRESH")
    cal = google(lambda r: httpx.Response(400, json={"error": "invalid_grant", "detail": "SECRET-BODY"}), secrets)
    with pytest.raises(connectors.ConnectorError) as exc:
        cal.events(NOW, NOW + timedelta(days=1))
    assert secrets.get(connectors.TOKEN_ACCOUNT) is None and "SECRET-BODY" not in str(exc.value)


def test_state_works_once_and_expires():
    clock = [0.0]
    flows = connectors.OAuthFlows(clock=lambda: clock[0])
    state, _ = flows.begin()
    assert flows.take(state) and flows.take(state) is None
    state, _ = flows.begin(); clock[0] += connectors.FLOW_SECONDS + 1
    assert flows.take(state) is None
    assert flows.take("guess") is None and flows.take("") is None


def test_full_sign_in_through_the_callback_without_a_session_cookie(tmp_path):
    secrets = Secrets()
    app, c = signed_in(tmp_path, google(ok_handler, secrets), secrets)
    url = c.post("/api/connectors/calendar/start", json={}).json()["url"]
    state = parse_qs(urlsplit(url).query)["state"][0]
    visitor = TestClient(app, base_url=BASE)  # no cookie: the browser withholds it on a cross-site return
    page = visitor.get(CALLBACK, params={"code": "CODE", "state": state}, headers={"sec-fetch-site": "cross-site"})
    assert page.status_code == 200 and "connected" in page.text and 'url=/#sources' in page.text
    assert secrets.get(connectors.TOKEN_ACCOUNT) == "REFRESH"
    assert c.get("/api/connectors/calendar").json()["connected"] is True
    assert c.post("/api/connectors/calendar/sync", json={}).json()["found"] == 1
    again = visitor.get(CALLBACK, params={"code": "CODE", "state": state}, headers={"sec-fetch-site": "cross-site"})
    assert "already used or has expired" in again.text


def test_the_callback_with_a_wrong_state_connects_nothing(tmp_path):
    secrets = Secrets()
    app, c = signed_in(tmp_path, google(ok_handler, secrets), secrets)
    c.post("/api/connectors/calendar/start", json={})
    page = TestClient(app, base_url=BASE).get(CALLBACK, params={"code": "CODE", "state": "wrong"}, headers={"sec-fetch-site": "cross-site"})
    assert "already used or has expired" in page.text and secrets.get(connectors.TOKEN_ACCOUNT) is None
    assert c.get("/api/connectors/calendar").json()["connected"] is False


def test_cross_site_is_refused_everywhere_except_the_callback(tmp_path):
    app, c = signed_in(tmp_path, Provider([]))
    visitor = TestClient(app, base_url=BASE)
    cross = {"sec-fetch-site": "cross-site"}
    assert visitor.get("/api/bootstrap", headers=cross).status_code == 403
    assert visitor.get("/api/encounters", headers=cross).status_code == 403
    assert visitor.get(CALLBACK + "x", headers=cross).status_code == 403
    assert visitor.post(CALLBACK, headers={**cross, "origin": "https://evil.example"}).status_code == 403
    assert visitor.get(CALLBACK, headers={**cross, "host": "evil.example"}).status_code == 400  # host check still applies
    assert visitor.get(CALLBACK, headers=cross).status_code == 200


def test_google_client_settings_come_from_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPANION_DATA_DIR", str(tmp_path)); monkeypatch.setenv("COMPANION_GOOGLE_CLIENT_ID", " abc ")
    assert Settings.from_env().google_client_id == "abc" and Settings(data_dir=tmp_path).google_client_id == ""
