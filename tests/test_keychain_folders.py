"""Each data folder keeps its own Google sign-ins (decision D49). A dictionary stands in for the keychain."""

from __future__ import annotations

import httpx

from companion import app as app_module
from companion import connectors
from companion.ai import MockAI
from companion.config import Settings
from companion.keys import FolderSecrets

from .test_calendar_connect import Secrets


def test_two_folders_never_see_or_replace_each_others_sign_in(tmp_path):
    keychain = Secrets()
    mine, tester = FolderSecrets(keychain, tmp_path / "mine"), FolderSecrets(keychain, tmp_path / "tester")
    mine.set(connectors.TOKEN_ACCOUNT, "MINE")
    assert tester.get(connectors.TOKEN_ACCOUNT) is None
    tester.set(connectors.TOKEN_ACCOUNT, "THEIRS")
    assert mine.get(connectors.TOKEN_ACCOUNT) == "MINE" and tester.get(connectors.TOKEN_ACCOUNT) == "THEIRS"
    assert not any("MINE" == v for k, v in keychain.values.items() if k == connectors.TOKEN_ACCOUNT)  # nothing under the bare name


def test_a_tester_disconnecting_cancels_only_their_own_sign_in(tmp_path):
    keychain = Secrets()
    ok = httpx.MockTransport(lambda r: httpx.Response(200))
    mine, tester = FolderSecrets(keychain, tmp_path / "mine"), FolderSecrets(keychain, tmp_path / "tester")
    for store, token in ((mine, "MINE"), (tester, "THEIRS")):
        store.set(connectors.TOKEN_ACCOUNT, token); store.set(connectors.MAIL_TOKEN_ACCOUNT, token + "-MAIL")
    connectors.GoogleCalendar("id", "secret", tester, transport=ok).disconnect()
    connectors.GoogleMail("id", "secret", tester, transport=ok).disconnect()
    assert tester.get(connectors.TOKEN_ACCOUNT) is None and tester.get(connectors.MAIL_TOKEN_ACCOUNT) is None
    assert mine.get(connectors.TOKEN_ACCOUNT) == "MINE" and mine.get(connectors.MAIL_TOKEN_ACCOUNT) == "MINE-MAIL"


def test_your_usual_folder_adopts_an_older_sign_in_and_other_folders_do_not(tmp_path):
    keychain = Secrets()
    keychain.set(connectors.TOKEN_ACCOUNT, "SAVED-BEFORE")
    assert FolderSecrets(keychain, tmp_path / "tester").get(connectors.TOKEN_ACCOUNT) is None
    usual = FolderSecrets(keychain, tmp_path / "usual", adopt_legacy=True)
    assert usual.get(connectors.TOKEN_ACCOUNT) == "SAVED-BEFORE"
    assert keychain.get(connectors.TOKEN_ACCOUNT) is None                      # moved, not copied
    assert FolderSecrets(keychain, tmp_path / "usual").get(connectors.TOKEN_ACCOUNT) == "SAVED-BEFORE"
    assert FolderSecrets(keychain, tmp_path / "tester").get(connectors.TOKEN_ACCOUNT) is None


def test_the_same_folder_written_two_ways_is_the_same_folder(tmp_path):
    keychain = Secrets()
    FolderSecrets(keychain, tmp_path / "a" / ".." / "mine").set("x", "1")
    assert FolderSecrets(keychain, tmp_path / "mine").get("x") == "1"


def test_the_app_gives_each_data_folder_its_own_entries(tmp_path, monkeypatch):
    keychain = Secrets()
    monkeypatch.setattr(app_module, "KeyringSecrets", lambda: keychain)
    first = app_module.create_app(Settings(data_dir=tmp_path / "one", port=8765, ai_mode="mock"), ai_client=MockAI())
    second = app_module.create_app(Settings(data_dir=tmp_path / "two", port=8765, ai_mode="mock"), ai_client=MockAI())
    first.state.secrets.set(connectors.TOKEN_ACCOUNT, "ONE")
    assert second.state.secrets.get(connectors.TOKEN_ACCOUNT) is None
    assert first.state.secrets.adopt_legacy is False  # a temporary folder is never your usual one
