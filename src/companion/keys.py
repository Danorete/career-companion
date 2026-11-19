"""API key storage in the macOS Keychain (decision D14). No file or environment fallback."""

from __future__ import annotations

SERVICE = "career-companion"
ACCOUNT = "anthropic-api-key"


def get_api_key() -> str | None:
    try:
        import keyring

        return keyring.get_password(SERVICE, ACCOUNT) or None
    except Exception:
        return None


def set_api_key(value: str) -> None:
    import keyring

    keyring.set_password(SERVICE, ACCOUNT, value)


def delete_api_key() -> None:
    import keyring

    try:
        keyring.delete_password(SERVICE, ACCOUNT)
    except Exception:
        pass


class KeyringSecrets:
    """Connector sign-ins (refresh tokens) live in the system keychain only, never in the database,
    an export or a log (decisions D14, D39). Tests inject a dictionary-backed stand-in with the same methods."""

    def get(self, account: str) -> str | None:
        try:
            import keyring

            return keyring.get_password(SERVICE, account) or None
        except Exception:
            return None

    def set(self, account: str, value: str) -> None:
        import keyring

        keyring.set_password(SERVICE, account, value)

    def delete(self, account: str) -> None:
        try:
            import keyring

            keyring.delete_password(SERVICE, account)
        except Exception:
            pass



def _folder_id(data_dir) -> str:
    from pathlib import Path
    import hashlib

    return hashlib.sha256(str(Path(data_dir).expanduser().resolve()).encode("utf-8")).hexdigest()[:16]


class FolderSecrets:
    """Gives each data folder its own keychain entries (decision D49).

    The keychain is shared by everything running as your user, so without this, a tester signing in to Google from a
    fresh data folder on your Mac would replace your sign-in, and theirs would stay behind. Entries are named
    `<account>:<folder id>`, where the id is a hash of the folder's full path. Your usual data folder adopts a sign-in
    saved before this change (under the bare name) the first time it is read, so nobody has to reconnect.
    """

    def __init__(self, inner, data_dir, adopt_legacy: bool = False):
        self.inner, self.folder, self.adopt_legacy = inner, _folder_id(data_dir), adopt_legacy

    def _name(self, account: str) -> str:
        return f"{account}:{self.folder}"

    def get(self, account: str) -> str | None:
        value = self.inner.get(self._name(account))
        if value is None and self.adopt_legacy:
            legacy = self.inner.get(account)
            if legacy:
                try:
                    self.inner.set(self._name(account), legacy)
                    self.inner.delete(account)
                except Exception:
                    pass  # still usable this time; the move is tried again next read
                return legacy
        return value

    def set(self, account: str, value: str) -> None:
        self.inner.set(self._name(account), value)

    def delete(self, account: str) -> None:
        self.inner.delete(self._name(account))
        if self.adopt_legacy:
            self.inner.delete(account)  # a sign-in from before D49 must not survive a disconnect


class EncryptedFileSecrets:
    """Google sign-ins for one person in the web version (decision D50). A server has no keychain, so each person's
    sign-ins sit in one file in their own folder, encrypted with a key that exists only in the host's secret settings.

    Each value is sealed together with the person's account id and the entry's name, so a file copied into another
    person's folder, or an entry moved under another name, does not open. The file is readable by the server user only.
    """

    def __init__(self, path, key: bytes, owner: str):
        from pathlib import Path

        from cryptography.fernet import Fernet

        self.path, self.owner, self._fernet = Path(path), owner, Fernet(key)

    def _load(self) -> dict:
        import json

        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return {}

    def _save(self, items: dict) -> None:
        import json
        import os

        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(items, out)
        os.replace(tmp, self.path)

    def get(self, account: str) -> str | None:
        import json

        from cryptography.fernet import InvalidToken

        sealed = self._load().get(account)
        if not sealed:
            return None
        try:
            inside = json.loads(self._fernet.decrypt(sealed.encode("ascii")))
        except (InvalidToken, ValueError):
            return None
        if inside.get("owner") != self.owner or inside.get("account") != account:
            return None
        return inside.get("value") or None

    def set(self, account: str, value: str) -> None:
        import json

        items = self._load()
        items[account] = self._fernet.encrypt(json.dumps({"owner": self.owner, "account": account, "value": value}).encode()).decode("ascii")
        self._save(items)

    def delete(self, account: str) -> None:
        items = self._load()
        if items.pop(account, None) is not None:
            self._save(items)
