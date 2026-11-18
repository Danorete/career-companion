"""The web version's front door (decision D50). Google is a stand-in; time is a list we move by hand.

Every test here is an attack or a promise from the sign-in page: strangers stay out, each person's data is separate,
sessions end, and Delete everything really deletes.
"""

from __future__ import annotations

import base64
import json
import logging
import stat
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient

from companion import connectors
from companion.keys import EncryptedFileSecrets
from companion.web import INACTIVE_SECONDS, SESSION_IDLE_SECONDS, WebConfig, create_web_app

PUBLIC = "https://link.test"
CLIENT_ID = "web-client.apps.example"
T0 = 1_800_000_000.0
MAYA, SAM, STRANGER = "maya@example.com", "sam@example.com", "stranger@example.com"


def b64(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()


class FakeGoogle:
    """Answers the token endpoint like Google would, with claims a test can bend."""

    def __init__(self, clock):
        self.clock, self.email, self.nonce, self.overrides, self.revoked, self.calls = clock, MAYA, "", {}, [], []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(str(request.url))
        form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
        if request.url.path == "/revoke":
            self.revoked.append(form.get("token"))
            return httpx.Response(200)
        if form.get("grant_type") == "authorization_code":
            claims = {"iss": "https://accounts.google.com", "aud": CLIENT_ID, "exp": self.clock[0] + 3600, "iat": self.clock[0],
                      "nonce": self.nonce, "email": self.email, "email_verified": True, **self.overrides}
            return httpx.Response(200, json={"id_token": "e30." + b64(claims) + ".signature", "access_token": "AT"})
        return httpx.Response(400, json={"error": "invalid_grant"})


def config(tmp_path, **changes) -> WebConfig:
    values = dict(public_url=PUBLIC, data_root=tmp_path / "root", secret_key="k" * 48, google_client_id=CLIENT_ID,
                  google_client_secret="web-secret", invites=frozenset({MAYA, SAM}))
    values.update(changes)
    return WebConfig(**values)


@pytest.fixture
def site(tmp_path):
    clock = [T0]
    google = FakeGoogle(clock)
    app = create_web_app(config(tmp_path), transport=httpx.MockTransport(google.handler), clock=lambda: clock[0])
    return app, google, clock


def browser(app) -> TestClient:
    return TestClient(app, base_url=PUBLIC, headers={"origin": PUBLIC})


def sign_in(c: TestClient, google: FakeGoogle, email: str = MAYA, tz: str = "America/Chicago") -> httpx.Response:
    start = c.get(f"/signin?tz={tz}", follow_redirects=False)
    assert start.status_code == 303
    query = parse_qs(urlsplit(start.headers["location"]).query)
    google.nonce, google.email = query["nonce"][0], email
    return c.get(f"/connect/google/callback?state={query['state'][0]}&code=one-time-code")


def csrf(c: TestClient) -> str:
    return c.get("/api/bootstrap").json()["csrf"]


def signed_in(app, google, email=MAYA) -> TestClient:
    c = browser(app)
    assert sign_in(c, google, email).status_code == 200
    c.headers["x-csrf-token"] = csrf(c)
    return c


def folders(app) -> list[Path]:
    root = app.state.cfg.data_root / "people"
    return sorted(root.iterdir()) if root.exists() else []


# ---- who can get in --------------------------------------------------------------------------------------------

def test_signed_out_visitors_see_the_sign_in_page_and_no_data(site):
    app, google, clock = site
    c = browser(app)
    page = c.get("/").text
    assert "Sign in with Google" in page and "deleted when you click" in page and "30 days" in page
    assert c.get("/api/bootstrap").status_code == 401 and c.get("/api/people").status_code == 401
    assert c.get("/static/app.js").status_code == 200  # the page's own code is public; no data is


def test_the_sign_in_asks_google_only_for_an_email_address_with_pkce_and_a_nonce(site):
    app, google, clock = site
    location = browser(app).get("/signin", follow_redirects=False).headers["location"]
    parts, query = urlsplit(location), parse_qs(urlsplit(location).query)
    assert f"{parts.scheme}://{parts.netloc}{parts.path}" == connectors.GOOGLE_AUTH
    assert query["scope"] == ["openid email"] and query["redirect_uri"] == [PUBLIC + "/connect/google/callback"]
    assert query["code_challenge_method"] == ["S256"] and len(query["nonce"][0]) >= 24 and query["state"][0].startswith("signin.")


def test_an_invited_person_signs_in_with_a_cookie_scripts_cannot_read(site):
    app, google, clock = site
    c = browser(app)
    r = sign_in(c, google)
    cookie = r.headers["set-cookie"]
    assert cookie.startswith("__Host-link=") and "Secure" in cookie and "HttpOnly" in cookie
    assert "SameSite=lax" in cookie and "Path=/" in cookie and "Domain" not in cookie
    boot = c.get("/api/bootstrap").json()
    assert boot["hosted"] is True and boot["csrf"]
    assert "Sign in with Google" not in c.get("/").text  # the app itself now


def test_a_stranger_is_refused_and_nothing_is_created(site):
    app, google, clock = site
    c = browser(app)
    r = sign_in(c, google, STRANGER)
    assert r.status_code == 403 and "invite list" in r.text and "set-cookie" not in r.headers
    assert app.state.accounts.count() == 0 and folders(app) == []


@pytest.mark.parametrize("bad", [
    {"email_verified": False}, {"aud": "someone-elses-app"}, {"iss": "https://evil.example"},
    {"exp": T0 - 1}, {"nonce": "replayed-nonce"}, {"email": ""},
])
def test_a_sign_in_google_did_not_vouch_for_is_refused(site, bad):
    app, google, clock = site
    google.overrides = bad
    r = sign_in(browser(app), google)
    assert r.status_code == 400 and "set-cookie" not in r.headers and app.state.accounts.count() == 0


def test_a_sign_in_link_works_once_expires_and_cannot_be_invented(site):
    app, google, clock = site
    c = browser(app)
    start = c.get("/signin", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    google.nonce = parse_qs(urlsplit(start.headers["location"]).query)["nonce"][0]
    assert c.get(f"/connect/google/callback?state=signin.made-up&code=x").status_code == 400
    assert c.get(f"/connect/google/callback?state={state}&code=x").status_code == 200
    assert c.get(f"/connect/google/callback?state={state}&code=x").status_code == 400  # replay
    late = c.get("/signin", follow_redirects=False)
    late_state = parse_qs(urlsplit(late.headers["location"]).query)["state"][0]
    clock[0] += 601
    assert c.get(f"/connect/google/callback?state={late_state}&code=x").status_code == 400


def test_the_email_address_is_never_stored_or_logged(site, caplog):
    app, google, clock = site
    caplog.set_level(logging.DEBUG)
    signed_in(app, google)
    root = app.state.cfg.data_root
    for path in root.rglob("*"):
        if path.is_file():
            assert b"maya@example.com" not in path.read_bytes(), path
    server = "\n".join(r.getMessage() for r in caplog.records if not r.name.startswith("httpx2"))  # httpx2: the test's browser
    assert "maya@example.com" not in server and "one-time-code" not in server and "signin." not in server


# ---- each person's data is separate --------------------------------------------------------------------------

def test_two_people_never_see_or_change_each_others_records(site):
    app, google, clock = site
    maya, sam = signed_in(app, google, MAYA), signed_in(app, google, SAM)
    alice = maya.post("/api/people", json={"name": "Alice from the career fair"}).json()
    bob = sam.post("/api/people", json={"name": "Bob from class"}).json()
    assert alice["id"] == bob["id"]  # same number, different databases
    assert [p["name"] for p in maya.get("/api/people").json()] == ["Alice from the career fair"]
    assert [p["name"] for p in sam.get("/api/people").json()] == ["Bob from class"]
    sam.put(f"/api/people/{alice['id']}", json={"name": "renamed by Sam"})
    sam.delete(f"/api/people/{alice['id']}")
    assert [p["name"] for p in maya.get("/api/people").json()] == ["Alice from the career fair"]
    assert "Alice" not in sam.get("/api/export").text and "Bob" not in maya.get("/api/export").text
    assert len(folders(app)) == 2


def test_each_folder_and_database_is_readable_by_the_server_user_only(site):
    app, google, clock = site
    signed_in(app, google)
    [folder] = folders(app)
    assert stat.S_IMODE(app.state.cfg.data_root.stat().st_mode) == 0o700
    assert stat.S_IMODE(folder.stat().st_mode) == 0o700
    assert stat.S_IMODE((folder / "companion.sqlite3").stat().st_mode) == 0o600
    assert stat.S_IMODE((app.state.cfg.data_root / "accounts.sqlite3").stat().st_mode) == 0o600


# ---- the rules every request follows --------------------------------------------------------------------------

def test_changes_need_the_csrf_token_and_this_sites_origin(site):
    app, google, clock = site
    c = signed_in(app, google)
    token = c.headers.pop("x-csrf-token")
    assert c.post("/api/people", json={"name": "x"}).status_code == 403
    assert c.post("/api/people", json={"name": "x"}, headers={"x-csrf-token": "wrong"}).status_code == 403
    assert c.post("/api/people", json={"name": "x"}, headers={"x-csrf-token": token, "origin": "https://evil.example"}).status_code == 403
    assert c.post("/api/people", content="name=x", headers={"x-csrf-token": token, "content-type": "application/x-www-form-urlencoded"}).status_code == 415
    assert c.post("/api/people", json={"name": "x"}, headers={"x-csrf-token": token}).status_code == 200


def test_other_sites_can_link_here_but_cannot_read_or_change_anything(site):
    app, google, clock = site
    c = signed_in(app, google)
    from_linkedin = {"sec-fetch-site": "cross-site", "sec-fetch-mode": "navigate"}
    assert c.get("/", headers=from_linkedin).status_code == 200
    assert c.get("/api/people", headers={"sec-fetch-site": "cross-site", "sec-fetch-mode": "cors"}).status_code == 403
    assert c.get("/api/people", headers=from_linkedin).status_code == 403  # not even as a navigation


def test_only_this_sites_address_is_answered(site):
    app, google, clock = site
    c = signed_in(app, google)
    assert c.get("/api/people", headers={"host": "attacker.example"}).status_code == 400
    assert TestClient(app, base_url="https://link.test.attacker.example").get("/").status_code == 400


def test_the_mac_apps_launcher_quit_and_one_time_links_do_not_exist_here(site):
    app, google, clock = site
    c = signed_in(app, google)
    for method, path in (("post", "/auth/exchange"), ("get", "/launcher/token"), ("post", "/launcher/quit"), ("post", "/api/quit")):
        assert getattr(c, method)(path, **({"json": {}} if method == "post" else {})).status_code == 404, path


def test_every_answer_carries_the_security_headers_and_hsts(site):
    app, google, clock = site
    for r in (browser(app).get("/"), browser(app).get("/api/people"), signed_in(app, google).get("/api/bootstrap")):
        assert "default-src 'none'" in r.headers["content-security-policy"] and r.headers["x-frame-options"] == "DENY"
        assert r.headers["strict-transport-security"].startswith("max-age=31536000")


def test_too_many_requests_are_slowed_down(site):
    app, google, clock = site
    c = signed_in(app, google)
    codes = [c.get("/api/people").status_code for _ in range(260)]
    assert codes.count(429) > 0 and codes[0] == 200
    clock[0] += 61
    assert c.get("/api/people").status_code == 200
    stranger = browser(app)
    starts = [stranger.get("/signin", follow_redirects=False).status_code for _ in range(25)]
    assert starts[0] == 303 and starts[-1] == 429 and starts.count(429) >= 5
    clock[0] += 601
    assert stranger.get("/signin", follow_redirects=False).status_code == 303


# ---- sessions end ---------------------------------------------------------------------------------------------

def test_a_session_ends_after_a_week_unused_and_on_sign_out(site):
    app, google, clock = site
    c = signed_in(app, google)
    clock[0] += SESSION_IDLE_SECONDS - 60
    assert c.get("/api/people").status_code == 200  # used just in time: the week starts again
    clock[0] += SESSION_IDLE_SECONDS + 1
    assert c.get("/api/people").status_code == 401
    c = signed_in(app, google)
    assert c.post("/api/signout", json={}).status_code == 200
    assert c.get("/api/people").status_code == 401


def test_signing_in_again_replaces_the_old_session(site):
    app, google, clock = site
    c = signed_in(app, google)
    old = c.cookies.get("__Host-link")
    sign_in(c, google)
    assert c.cookies.get("__Host-link") != old
    other = browser(app)
    other.cookies.set("__Host-link", old)
    assert other.get("/api/people").status_code == 401


# ---- Google sign-ins for calendar and email --------------------------------------------------------------------

def test_calendar_sign_ins_are_encrypted_and_bound_to_their_owner(site):
    app, google, clock = site
    c = signed_in(app, google)
    [folder] = folders(app)
    account_id = folder.name
    store = EncryptedFileSecrets(folder / "signins.enc", app.state.pool.signin_key, account_id)
    store.set(connectors.TOKEN_ACCOUNT, "REFRESH-TOKEN-CANARY")
    raw = (folder / "signins.enc").read_bytes()
    assert b"REFRESH-TOKEN-CANARY" not in raw and stat.S_IMODE((folder / "signins.enc").stat().st_mode) == 0o600
    assert store.get(connectors.TOKEN_ACCOUNT) == "REFRESH-TOKEN-CANARY"
    from cryptography.fernet import Fernet
    assert EncryptedFileSecrets(folder / "signins.enc", Fernet.generate_key(), account_id).get(connectors.TOKEN_ACCOUNT) is None
    assert EncryptedFileSecrets(folder / "signins.enc", app.state.pool.signin_key, "f" * 32).get(connectors.TOKEN_ACCOUNT) is None
    assert "REFRESH-TOKEN-CANARY" not in c.get("/api/export").text


def test_connecting_a_calendar_returns_to_this_sites_address(site):
    app, google, clock = site
    c = signed_in(app, google)
    url = c.post("/api/connectors/calendar/start", json={}).json()["url"]
    query = parse_qs(urlsplit(url).query)
    assert query["redirect_uri"] == [PUBLIC + "/connect/google/callback"]
    assert not query["state"][0].startswith("signin.")
    r = c.get(f"/connect/google/callback?state={query['state'][0]}&error=access_denied")
    assert r.status_code == 200 and "didn't connect your calendar" in r.text  # handled by Maya's own copy
    assert browser(app).get(f"/connect/google/callback?state={query['state'][0]}&code=x").status_code == 401


# ---- deletion is real -----------------------------------------------------------------------------------------

def test_delete_everything_cancels_google_removes_the_folder_and_the_account(site):
    app, google, clock = site
    c = signed_in(app, google)
    c.post("/api/people", json={"name": "Alice"})
    [folder] = folders(app)
    EncryptedFileSecrets(folder / "signins.enc", app.state.pool.signin_key, folder.name).set(connectors.TOKEN_ACCOUNT, "REFRESH-1")
    assert c.post("/api/wipe", json={"confirm": "nope"}).status_code == 422 and folder.exists()
    r = c.post("/api/wipe", json={"confirm": "DELETE EVERYTHING"})
    assert r.status_code == 200 and r.json()["account_deleted"] is True
    assert "REFRESH-1" in google.revoked                     # Google was asked to cancel the calendar sign-in
    assert not folder.exists() and app.state.accounts.count() == 0
    assert c.get("/api/people").status_code == 401           # signed out
    c2 = signed_in(app, google)                              # signing in again starts from nothing
    assert c2.get("/api/people").json() == []


def test_accounts_unused_for_thirty_days_are_deleted_and_others_stay(site):
    app, google, clock = site
    signed_in(app, google, MAYA)
    clock[0] += INACTIVE_SECONDS - 86400
    signed_in(app, google, SAM)
    clock[0] += 2 * 86400  # Maya: 31 days unused. Sam: 2 days.
    assert app.state.purge_inactive() == 1
    assert app.state.accounts.count() == 1 and len(folders(app)) == 1


# ---- settings ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("change,words", [
    ({"public_url": "http://link.example.com"}, "https://"), ({"public_url": "https://link.example.com/app"}, "just the site"),
    ({"secret_key": "short"}, "at least 32"), ({"invites": frozenset()}, "nobody could sign in"),
    ({"google_client_secret": ""}, "client ID and secret"), ({"ai_mode": "live"}, "sample AI"),
])
def test_unsafe_settings_refuse_to_start(tmp_path, change, words):
    with pytest.raises(ValueError, match=words):
        config(tmp_path, **change)


def test_settings_come_from_the_environment_and_a_web_client_file(tmp_path):
    client = tmp_path / "web.json"
    client.write_text(json.dumps({"web": {"client_id": CLIENT_ID, "client_secret": "s3"}}))
    cfg = WebConfig.from_env({"LINK_PUBLIC_URL": "https://link.example.com/", "LINK_DATA_ROOT": str(tmp_path / "d"),
                              "LINK_SECRET_KEY": "x" * 40, "COMPANION_GOOGLE_CLIENT_FILE": str(client),
                              "LINK_INVITES": " Maya@Example.com, sam@example.com\nana@example.com "})
    assert cfg.public_url == "https://link.example.com" and cfg.google_client_secret == "s3"
    assert cfg.invites == frozenset({"maya@example.com", "sam@example.com", "ana@example.com"})
    desktop = tmp_path / "desktop.json"
    desktop.write_text(json.dumps({"installed": {"client_id": "x", "client_secret": "y"}}))
    with pytest.raises(ValueError, match="Web application"):
        WebConfig.from_env({"COMPANION_GOOGLE_CLIENT_FILE": str(desktop)})


def test_the_time_zone_sent_at_sign_in_is_kept_and_a_bad_one_is_ignored(site):
    app, google, clock = site
    sign_in(browser(app), google, MAYA, tz="America/Los_Angeles")
    sign_in(browser(app), google, SAM, tz="Not/AZone")
    zones = sorted(r[0] for r in app.state.accounts.conn.execute("SELECT timezone FROM accounts"))
    assert zones == ["America/Los_Angeles", "America/New_York"]


def test_local_testing_on_localhost_uses_a_plain_cookie_without_secure(tmp_path):
    clock = [T0]
    google = FakeGoogle(clock)
    app = create_web_app(config(tmp_path, public_url="http://localhost:8765"), transport=httpx.MockTransport(google.handler),
                         clock=lambda: clock[0])
    c = TestClient(app, base_url="http://localhost:8765", headers={"origin": "http://localhost:8765"})
    cookie = sign_in(c, google).headers["set-cookie"]
    assert cookie.startswith("link_session=") and "Secure" not in cookie
    assert "strict-transport-security" not in c.get("/").headers


def test_the_web_command_refuses_unsafe_settings_and_binds_safely(monkeypatch, capsys, tmp_path):
    from companion.cli import main, web_bind
    for key in ("LINK_PUBLIC_URL", "LINK_SECRET_KEY", "LINK_INVITES", "PORT", "LINK_BIND", "COMPANION_GOOGLE_CLIENT_FILE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LINK_PUBLIC_URL", "https://link.example.com")
    assert main(["web"]) == 2 and "Can't start" in capsys.readouterr().out
    assert web_bind(config(tmp_path, public_url="http://localhost:8765")) == ("127.0.0.1", 8765)
    monkeypatch.setenv("PORT", "8080")
    assert web_bind(config(tmp_path)) == ("0.0.0.0", 8080)
