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

