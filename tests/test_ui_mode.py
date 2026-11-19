"""Two versions of one app: the user version (default) and the developer version."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from companion.ai import MockAI
from companion.app import create_app
from companion.config import Settings
from companion.security import COOKIE_NAME, CSRF_HEADER

from .conftest import BASE, PORT


def _signed_in(tmp_path, mode):
    app = create_app(Settings(data_dir=tmp_path / mode, port=PORT, ai_mode="mock", ui_mode=mode), ai_client=MockAI())
    sid, csrf = app.state.security.new_session_for_tests()
    client = TestClient(app, base_url=BASE, headers={CSRF_HEADER: csrf, "origin": BASE})
    client.cookies.set(COOKIE_NAME, sid)
    return client


def test_user_version_is_the_default(tmp_path):
    assert Settings(data_dir=tmp_path).ui_mode == "user"


def test_ui_mode_must_be_user_or_dev(tmp_path):
    with pytest.raises(ValueError):
        Settings(data_dir=tmp_path, ui_mode="admin")


def test_ui_mode_can_be_set_from_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPANION_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("COMPANION_UI_MODE", "dev")
    assert Settings.from_env().ui_mode == "dev"
    monkeypatch.delenv("COMPANION_UI_MODE")
    assert Settings.from_env().ui_mode == "user"


@pytest.mark.parametrize("mode", ["user", "dev"])
def test_bootstrap_tells_the_page_which_version_to_show(tmp_path, mode):
    assert _signed_in(tmp_path, mode).get("/api/bootstrap").json()["ui_mode"] == mode


def test_the_cli_rejects_an_unknown_mode():
    from companion.cli import main

    with pytest.raises(SystemExit):
        main(["run", "--mode", "admin"])
