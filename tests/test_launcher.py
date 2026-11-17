"""One-click start (decision D47). Nothing starts a real server, opens a browser, or builds a real app."""

from __future__ import annotations

import os
import stat
import threading
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from companion import launcher
from companion.ai import MockAI
from companion.app import create_app
from companion.cli import main
from companion.config import Settings
from companion.security import COOKIE_NAME, CSRF_HEADER, MINTED_TOKEN_SECONDS, Security

from .conftest import BASE, PORT

KEY_HEADER = "x-launcher-key"


def make(tmp_path):
    app = create_app(Settings(data_dir=tmp_path / "d", port=PORT, ai_mode="mock"), ai_client=MockAI())
    return app, TestClient(app, base_url=BASE)


# ---- one-time links for the launcher ---------------------------------------------------------

def test_a_minted_link_works_once_and_expires(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr("companion.security.time.monotonic", lambda: clock[0])
    sec = Security(PORT)
    first, second = sec.mint_launch_token(), sec.mint_launch_token()
    assert sec.exchange(first) is not None and sec.exchange(first) is None
    clock[0] += MINTED_TOKEN_SECONDS + 1
    assert sec.exchange(second) is None


def test_the_first_link_and_minted_links_are_separate_and_the_first_can_be_closed(monkeypatch):
    sec = Security(PORT)
    minted = sec.mint_launch_token()
    sec.revoke_initial_token()
    assert sec.exchange(sec.launch_token) is None   # nobody was shown this one
    assert sec.exchange(minted) is not None


def test_guessing_a_minted_link_counts_toward_the_lockout():
    sec = Security(PORT)
    minted = sec.mint_launch_token()
    for _ in range(5):
        assert sec.exchange("guess") is None
    assert sec.exchange(minted) is None  # locked out, as for the first link


def test_reusing_the_first_link_is_still_refused_without_counting_as_a_guess():
    sec = Security(PORT)
    assert sec.exchange(sec.launch_token) is not None
    for _ in range(10):
        assert sec.exchange(sec.launch_token) is None
    assert sec.exchange(sec.mint_launch_token()) is not None


# ---- the key and the routes --------------------------------------------------------------------

def test_the_key_file_is_private_and_stays_the_same_between_starts(tmp_path):
    app, _ = make(tmp_path)
    path = launcher.key_path(tmp_path / "d")
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    key = path.read_text().strip()
    again = create_app(Settings(data_dir=tmp_path / "d", port=PORT, ai_mode="mock"), ai_client=MockAI())
    assert launcher.read_key(tmp_path / "d") == key and again is not app


def test_only_the_key_gets_a_link_and_the_link_signs_you_in_once(tmp_path):
    app, c = make(tmp_path)
    key = launcher.read_key(tmp_path / "d")
    assert c.get("/launcher/token").status_code == 401
    assert c.get("/launcher/token", headers={KEY_HEADER: "wrong"}).status_code == 401
    token = c.get("/launcher/token", headers={KEY_HEADER: key}).json()["token"]
    assert c.post("/auth/exchange", json={"token": token}, headers={"origin": BASE}).status_code == 200
    assert TestClient(app, base_url=BASE).post("/auth/exchange", json={"token": token}, headers={"origin": BASE}).status_code == 403


def test_a_web_page_cannot_use_the_launcher_even_with_the_key(tmp_path):
    app, c = make(tmp_path)
    key = launcher.read_key(tmp_path / "d")
    assert c.get("/launcher/token", headers={KEY_HEADER: key, "sec-fetch-site": "cross-site"}).status_code == 403
    assert c.get("/launcher/token", headers={KEY_HEADER: key, "host": "evil.example"}).status_code == 400
    assert c.post("/launcher/quit", headers={KEY_HEADER: key, "origin": "https://evil.example", "content-type": "application/json"}, content=b"{}").status_code == 403


def test_quit_needs_the_key_and_an_own_origin_and_then_stops_link(tmp_path):
    app, c = make(tmp_path)
    key, stopped = launcher.read_key(tmp_path / "d"), threading.Event()
    app.state.request_shutdown = stopped.set
    json_headers = {"origin": BASE, "content-type": "application/json"}
    assert c.post("/launcher/quit", headers=json_headers, content=b"{}").status_code == 401
    assert c.post("/launcher/quit", headers={KEY_HEADER: key, "content-type": "application/json"}, content=b"{}").status_code == 403  # no origin
    assert not stopped.wait(0.6)
    assert c.post("/launcher/quit", headers={KEY_HEADER: key, **json_headers}, content=b"{}").json() == {"stopping": True}
    assert stopped.wait(3)


def test_the_menu_item_quits_only_when_signed_in(tmp_path):
    app, anon = make(tmp_path)
    stopped = threading.Event(); app.state.request_shutdown = stopped.set
    assert anon.post("/api/quit", json={}, headers={"origin": BASE}).status_code == 401
    sid, csrf = app.state.security.new_session_for_tests()
    c = TestClient(app, base_url=BASE, headers={CSRF_HEADER: csrf, "origin": BASE}); c.cookies.set(COOKIE_NAME, sid)
    assert c.post("/api/quit", json={}).json() == {"stopping": True} and stopped.wait(3)


# ---- companion launch ---------------------------------------------------------------------------

def settings_in(tmp_path):
    return SimpleNamespace(host="127.0.0.1", port=PORT, data_dir=tmp_path)


def test_a_running_link_is_asked_for_a_fresh_link_and_the_browser_opens_it(tmp_path):
    (tmp_path / "launcher.key").write_text("KEY")
    asked, opened = [], []
    code, message = launcher.launch(settings_in(tmp_path), ask=lambda base, key: asked.append((base, key)) or (200, "TOKEN"),
                                    spawn=lambda s: pytest.fail("already running"), opener=opened.append)
    assert (code, asked, opened) == (0, [(f"http://127.0.0.1:{PORT}", "KEY")], [f"http://127.0.0.1:{PORT}/#t=TOKEN"]) and "Opened" in message


def test_a_link_that_is_not_running_is_started_then_opened(tmp_path):
    answers = iter([None, None, (200, "T2")]); spawned, opened = [], []
    code, _ = launcher.launch(settings_in(tmp_path), ask=lambda *a: next(answers), spawn=spawned.append, opener=opened.append, sleep=lambda s: None)
    assert code == 0 and len(spawned) == 1 and opened == [f"http://127.0.0.1:{PORT}/#t=T2"]


def test_it_gives_up_with_a_pointer_to_the_log_when_link_never_starts(tmp_path):
    ticks = iter(range(0, 1000, 5))
    code, message = launcher.launch(settings_in(tmp_path), ask=lambda *a: None, spawn=lambda s: None, opener=lambda u: pytest.fail("no browser"),
                                    sleep=lambda s: None, clock=lambda: next(ticks))
    assert code == 1 and "link.log" in message


def test_another_program_on_the_port_is_never_started_over_or_opened(tmp_path):
    code, message = launcher.launch(settings_in(tmp_path), ask=lambda *a: (401, None), spawn=lambda s: pytest.fail("no start"),
                                    opener=lambda u: pytest.fail("no browser"))
    assert code == 1 and str(PORT) in message


def test_background_start_is_detached_and_writes_to_a_log_not_the_screen(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda args, **kw: seen.update(args=args, kw=kw))
    launcher.spawn_background(settings_in(tmp_path / "data"), python="/venv/bin/python")
    assert seen["args"] == ["/venv/bin/python", "-m", "companion.cli", "run", "--background"]
    assert seen["kw"]["start_new_session"] is True and seen["kw"]["stdin"] == launcher.subprocess.DEVNULL
    assert (tmp_path / "data" / "link.log").exists()


def test_quit_reports_each_case_plainly(tmp_path):
    (tmp_path / "launcher.key").write_text("KEY")
    sent = {}
    ok = lambda url, **kw: sent.update(url=url, **kw) or SimpleNamespace(status_code=200)
    assert launcher.quit_running(settings_in(tmp_path), post=ok) == (0, "Link has stopped.")
    assert sent["headers"]["X-Launcher-Key"] == "KEY" and sent["headers"]["Origin"] == f"http://127.0.0.1:{PORT}"
    def down(*a, **k):
        raise httpx.ConnectError("refused")
    assert launcher.quit_running(settings_in(tmp_path), post=down) == (0, "Link wasn't running.")
    assert launcher.quit_running(settings_in(tmp_path), post=lambda *a, **k: SimpleNamespace(status_code=401))[0] == 1


# ---- the background run mode and the commands ------------------------------------------------------

def test_a_background_start_prints_no_link_and_closes_the_first_one(tmp_path, monkeypatch, capsys):
    import uvicorn

    monkeypatch.setenv("COMPANION_DATA_DIR", str(tmp_path))
    seen = {}
    def fake_run(app, **kw):
        seen["app"] = app
        assert app.state.security.exchange(app.state.security.launch_token) is None
        assert callable(app.state.request_shutdown)
    monkeypatch.setattr(uvicorn, "run", fake_run)
    assert main(["run", "--background"]) == 0
    out = capsys.readouterr().out
    assert "#t=" not in out and "background" in out and "app" in seen


def test_the_launch_quit_and_launcher_commands(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("COMPANION_DATA_DIR", str(tmp_path)); monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(launcher, "launch", lambda settings: (0, "Opened Link in your browser."))
    monkeypatch.setattr(launcher, "quit_running", lambda settings: (0, "Link has stopped."))
    assert main(["launch"]) == 0 and main(["quit"]) == 0
    assert main(["launcher", "--status"]) == 0
    out = capsys.readouterr().out
    assert "Opened Link" in out and "Link has stopped." in out and "Link.app installed: no" in out


def test_launcher_accepts_install_like_the_nudge_command(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("COMPANION_DATA_DIR", str(tmp_path)); monkeypatch.setenv("HOME", str(tmp_path))
    calls = []
    monkeypatch.setattr(launcher, "install", lambda home, data_dir: calls.append(home) or "Installed Link.app.")
    assert main(["launcher", "--install"]) == 0 and main(["launcher"]) == 0
    assert len(calls) == 2 and capsys.readouterr().out.count("Installed Link.app.") == 2
    with pytest.raises(SystemExit):
        main(["launcher", "--install", "--uninstall"])


# ---- the Mac app ----------------------------------------------------------------------------------------

def test_the_app_script_runs_launch_with_the_same_settings_and_never_copies_a_secret(tmp_path):
    env = {"COMPANION_DATA_DIR": "/Users/me/Library/Application Support/My \"Link\"", "COMPANION_GOOGLE_CLIENT_FILE": "/Users/me/link-private/g.json",
           "COMPANION_GOOGLE_CLIENT_SECRET": "TOP-SECRET", "COMPANION_GOOGLE_CLIENT_ID": "id", "UNRELATED": "no"}
    text = launcher.applescript_source("/venv/bin/python", Path("/data/link.log"), env)
    assert "do shell script" in text and "companion.cli launch" in text and "/venv/bin/python" in text
    assert "g.json" in text and "TOP-SECRET" not in text and "COMPANION_GOOGLE_CLIENT_ID" not in text and "UNRELATED" not in text
    assert '\\"Link\\"' in text            # a quote in a path cannot end the AppleScript string early
    assert "display dialog" in text and "/data/link.log" in text


def test_installing_builds_the_app_with_osacompile(tmp_path):
    seen = {}
    def runner(cmd, **kw):
        seen["cmd"] = cmd; seen["script"] = Path(cmd[-1]).read_text()
        Path(cmd[cmd.index("-o") + 1]).mkdir(parents=True)  # what osacompile would make
        return SimpleNamespace(returncode=0)
    msg = launcher.install(tmp_path, tmp_path / "data", runner=runner, platform="darwin", python="/p", env={})
    assert seen["cmd"][:2] == ["osacompile", "-o"] and seen["cmd"][2].endswith("Applications/Link.app") and "launch" in seen["script"]
    assert "Installed" in msg and "Spotlight" in msg and launcher.is_installed(tmp_path)
    assert launcher.uninstall(tmp_path) == "Removed Link.app." and launcher.uninstall(tmp_path) == "Link.app wasn't installed."


def test_installing_elsewhere_or_when_macos_refuses_is_explained(tmp_path):
    assert "Mac" in launcher.install(tmp_path, tmp_path, runner=lambda *a, **k: pytest.fail("no command"), platform="linux")
    assert "could not build" in launcher.install(tmp_path, tmp_path, runner=lambda *a, **k: SimpleNamespace(returncode=1), platform="darwin")
    assert not launcher.is_installed(tmp_path)
