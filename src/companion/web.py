"""Link on the web (decision D50): the front door in front of one private copy of Link per person.

What this file adds on top of the app everyone already uses:

- **Invite-only sign-in with Google.** Only `openid email` is asked for. An account exists only for an address on the
  invite list, and only after Google confirms the address. The address itself is never stored: accounts are found by
  a keyed hash of it.
- **Separate data by construction.** Each account has its own folder, its own database file and its own copy of the
  app. A request is handed to the signed-in person's copy and nothing else, so one person's request has no way to
  name another person's records.
- **Sessions made for the open internet.** HTTPS only, HSTS, a `__Host-` cookie that scripts cannot read, sessions
  stored on the server as hashes, a CSRF token on every change, idle and absolute expiry, and rate limits.
- **Real deletion.** Delete everything cancels the person's Google sign-ins, removes their folder and account, and
  signs them out. Accounts unused for 30 days are deleted the same way.

The launcher and Quit do not exist here, because one person must never be able to stop the server for everyone.
Logs hold counts and reasons only: never an email address, a token, a name or anything anyone typed.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import html
import json
import logging
import os
import re
import secrets
import shutil
import sqlite3
import threading
import time
from collections import OrderedDict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal
from urllib.parse import urlencode, urlsplit
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from starlette.routing import Mount

from . import connectors
from .app import STATIC, create_app
from .config import Settings, load_google_client_file
from .keys import EncryptedFileSecrets
from .security import CSRF_HEADER, MAX_BODY_BYTES, OAUTH_CALLBACK_PATH, SAFE_METHODS, SECURITY_HEADERS

log = logging.getLogger("companion.web")

LOGIN_SCOPE = "openid email"
LOGIN_HOSTS = frozenset({"oauth2.googleapis.com"})  # the only host the front door itself ever contacts
LOGIN_STATE_PREFIX = "signin."                     # connector states never contain a dot, so the two never collide
GOOGLE_ISSUERS = {"https://accounts.google.com", "accounts.google.com"}
FLOW_SECONDS = 600
SESSION_IDLE_SECONDS = 7 * 86400
SESSION_MAX_SECONDS = 30 * 86400
INACTIVE_SECONDS = 30 * 86400
TOUCH_EVERY_SECONDS = 300
PURGE_EVERY_SECONDS = 6 * 3600
API_PER_MINUTE = 240
SIGNIN_PER_TEN_MINUTES = 20
POOL_SIZE = 64
HSTS = "max-age=31536000; includeSubDomains"
# Parts of the Mac app that must not exist on a shared server.
BLOCKED_PREFIXES = ("/auth/", "/launcher/")
BLOCKED_PATHS = frozenset({"/api/quit"})
DEFAULT_TIMEZONE = "America/New_York"


class LoginError(Exception):
    """The message is safe to show the person signing in."""


# ---- settings -----------------------------------------------------------------------------------------------------

def normalize_email(address: str) -> str:
    return address.strip().lower()


@dataclass
class WebConfig:
    public_url: str
    data_root: Path
    secret_key: str
    google_client_id: str
    google_client_secret: str
    invites: frozenset
    ai_mode: str = "mock"
    ui_mode: str = "user"
    trust_proxy: bool = False

    def __post_init__(self) -> None:
        parts = urlsplit(self.public_url.strip())
        local = parts.hostname in ("localhost", "127.0.0.1")
        if parts.scheme != "https" and not (parts.scheme == "http" and local):
            raise ValueError("LINK_PUBLIC_URL must start with https:// (http:// is allowed only for localhost).")
        if parts.path not in ("", "/") or parts.query or parts.fragment or parts.username or parts.password:
            raise ValueError("LINK_PUBLIC_URL is just the site's address, like https://link.example.com.")
        self.public_url = f"{parts.scheme}://{parts.netloc}"
        if len(self.secret_key) < 32:
            raise ValueError("LINK_SECRET_KEY must be at least 32 characters. Make one with: "
                             "python3 -c \"import secrets; print(secrets.token_urlsafe(48))\"")
        if not self.google_client_id or not self.google_client_secret:
            raise ValueError("The web version needs a Google Web application client ID and secret.")
        self.invites = frozenset(normalize_email(a) for a in self.invites if a.strip())
        if not self.invites:
            raise ValueError("LINK_INVITES is empty, so nobody could sign in.")
        if self.ai_mode not in ("mock", "off"):
            raise ValueError("The web version runs with sample AI (mock) or no AI (off) for now.")
        self.data_root = Path(self.data_root).expanduser()

    @property
    def secure(self) -> bool:
        return self.public_url.startswith("https://")

    @property
    def host(self) -> str:
        return urlsplit(self.public_url).netloc

    @property
    def cookie_name(self) -> str:
        # `__Host-` makes the browser refuse the cookie unless it is Secure, host-only and for the whole site.
        return "__Host-link" if self.secure else "link_session"

    @property
    def redirect_uri(self) -> str:
        return self.public_url + OAUTH_CALLBACK_PATH

    @classmethod
    def from_env(cls, env: dict | None = None) -> "WebConfig":
        env = dict(os.environ if env is None else env)
        client: dict[str, str] = {}
        if env.get("COMPANION_GOOGLE_CLIENT_FILE"):
            client = load_google_client_file(env["COMPANION_GOOGLE_CLIENT_FILE"], kind="web")
        return cls(
            public_url=env.get("LINK_PUBLIC_URL", ""),
            data_root=Path(env.get("LINK_DATA_ROOT", "/data")),
            secret_key=env.get("LINK_SECRET_KEY", ""),
            google_client_id=env.get("COMPANION_GOOGLE_CLIENT_ID", client.get("google_client_id", "")).strip(),
            google_client_secret=env.get("COMPANION_GOOGLE_CLIENT_SECRET", client.get("google_client_secret", "")).strip(),
            invites=frozenset(a for a in re.split(r"[\s,;]+", env.get("LINK_INVITES", "")) if a),
            ai_mode=env.get("COMPANION_AI_MODE", "mock"),
            trust_proxy=env.get("LINK_TRUST_PROXY", "") == "1",
        )


def _derive(secret: str, label: str) -> bytes:
    """Separate keys for separate jobs, all from the one secret in the host's settings."""
    return hmac.new(secret.encode("utf-8"), label.encode("utf-8"), hashlib.sha256).digest()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def valid_timezone(name: str) -> str:
    try:
        ZoneInfo(name)
    except Exception:
        return DEFAULT_TIMEZONE
    return name if 0 < len(name) <= 64 else DEFAULT_TIMEZONE


# ---- accounts and sessions ----------------------------------------------------------------------------------------

class Accounts:
    """Who has an account, and which sessions are signed in. No email address, no name, no session id in clear."""

    def __init__(self, path: Path, clock: Callable[[], float]):
        self.clock, self.lock = clock, threading.RLock()
        path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(path.parent, 0o700)
        self.conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
            PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA secure_delete=ON;
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY, email_mac TEXT NOT NULL UNIQUE, timezone TEXT NOT NULL,
                created_at REAL NOT NULL, last_seen REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions (
                sid_hash TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                csrf TEXT NOT NULL, created_at REAL NOT NULL, last_seen REAL NOT NULL);
        """)
        os.chmod(path, 0o600)

    @staticmethod
    def _hash(sid: str) -> str:
        return hashlib.sha256(sid.encode("utf-8")).hexdigest()

    def _one(self, sql: str, params: tuple = ()) -> dict | None:
        with self.lock:
            row = self.conn.execute(sql, params).fetchone()
        return dict(row) if row else None

    def _run(self, sql: str, params: tuple = ()) -> None:
        with self.lock:
            self.conn.execute(sql, params)

    def find_or_create(self, email_mac: str, timezone: str) -> dict:
        now = self.clock()
        with self.lock:
            row = self._one("SELECT * FROM accounts WHERE email_mac=?", (email_mac,))
            if row is None:
                account_id = secrets.token_hex(16)
                self._run("INSERT INTO accounts(id,email_mac,timezone,created_at,last_seen) VALUES(?,?,?,?,?)",
                          (account_id, email_mac, timezone, now, now))
                return {"id": account_id, "timezone": timezone, "new": True}
            self._run("UPDATE accounts SET last_seen=? WHERE id=?", (now, row["id"]))
            return {"id": row["id"], "timezone": row["timezone"], "new": False}

    def get(self, account_id: str) -> dict | None:
        return self._one("SELECT id, timezone, last_seen FROM accounts WHERE id=?", (account_id,))

    def new_session(self, account_id: str) -> tuple[str, str]:
        sid, csrf, now = secrets.token_urlsafe(32), secrets.token_urlsafe(32), self.clock()
        self._run("INSERT INTO sessions(sid_hash,account_id,csrf,created_at,last_seen) VALUES(?,?,?,?,?)",
                  (self._hash(sid), account_id, csrf, now, now))
        return sid, csrf

    def session(self, sid: str | None) -> dict | None:
        """The signed-in account for this cookie, or None. Expired sessions are removed on sight."""
        if not sid or len(sid) > 128:
            return None
        sid_hash, now = self._hash(sid), self.clock()
        row = self._one("SELECT s.*, a.timezone FROM sessions s JOIN accounts a ON a.id = s.account_id WHERE s.sid_hash=?",
                        (sid_hash,))
        if row is None:
            return None
        if now - row["last_seen"] > SESSION_IDLE_SECONDS or now - row["created_at"] > SESSION_MAX_SECONDS:
            self._run("DELETE FROM sessions WHERE sid_hash=?", (sid_hash,))
            return None
        if now - row["last_seen"] > TOUCH_EVERY_SECONDS:
            self._run("UPDATE sessions SET last_seen=? WHERE sid_hash=?", (now, sid_hash))
            self._run("UPDATE accounts SET last_seen=? WHERE id=?", (now, row["account_id"]))
        return {"account": {"id": row["account_id"], "timezone": row["timezone"]}, "csrf": row["csrf"]}

    def end_session(self, sid: str | None) -> None:
        if sid:
            self._run("DELETE FROM sessions WHERE sid_hash=?", (self._hash(sid),))

    def delete(self, account_id: str) -> None:
        self._run("DELETE FROM accounts WHERE id=?", (account_id,))  # its sessions go with it

    def inactive(self, before: float) -> list[dict]:
        with self.lock:
            return [dict(r) for r in self.conn.execute("SELECT id, timezone FROM accounts WHERE last_seen < ?", (before,))]

    def purge_sessions(self) -> None:
        now = self.clock()
        self._run("DELETE FROM sessions WHERE last_seen < ? OR created_at < ?", (now - SESSION_IDLE_SECONDS, now - SESSION_MAX_SECONDS))

    def count(self) -> int:
        return (self._one("SELECT COUNT(*) AS n FROM accounts") or {"n": 0})["n"]


class Limiter:
    """At most `limit` events per `window` seconds for each key."""

    def __init__(self, limit: int, window: float, clock: Callable[[], float]):
        self.limit, self.window, self.clock = limit, window, clock
        self.hits: dict[str, deque] = {}
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = self.clock()
        with self.lock:
            if len(self.hits) > 10_000:  # keep memory bounded
                self.hits = {k: q for k, q in self.hits.items() if q and q[-1] > now - self.window}
            q = self.hits.setdefault(key, deque())
            while q and q[0] <= now - self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True


# ---- one private copy of Link per person -------------------------------------------------------------------------

class Pool:
    def __init__(self, cfg: WebConfig, clock: Callable[[], float], app_kwargs: dict | None = None):
        self.cfg, self.clock, self.app_kwargs = cfg, clock, dict(app_kwargs or {})
        self.signin_key = base64.urlsafe_b64encode(_derive(cfg.secret_key, "link-signins-v1"))
        self.apps: OrderedDict[str, FastAPI] = OrderedDict()
        self.lock = threading.RLock()

    def folder(self, account_id: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{32}", account_id):
            raise ValueError("bad account id")
        return self.cfg.data_root / "people" / account_id

    def get(self, account: dict) -> FastAPI:
        with self.lock:
            app = self.apps.get(account["id"])
            if app is not None:
                self.apps.move_to_end(account["id"])
                return app
            folder = self.folder(account["id"])
            settings = Settings(data_dir=folder, hosted=True, public_url=self.cfg.public_url, ai_mode=self.cfg.ai_mode,
                                ui_mode=self.cfg.ui_mode, timezone=account.get("timezone") or DEFAULT_TIMEZONE,
                                google_client_id=self.cfg.google_client_id, google_client_secret=self.cfg.google_client_secret)
            store = EncryptedFileSecrets(folder / "signins.enc", self.signin_key, account["id"])
            app = create_app(settings, secret_store=store, **self.app_kwargs)
            self.apps[account["id"]] = app
            while len(self.apps) > POOL_SIZE:
                _, old = self.apps.popitem(last=False)
                old.state.db.close()
            return app

    def close(self, account_id: str) -> None:
        with self.lock:
            app = self.apps.pop(account_id, None)
            if app is not None:
                app.state.db.close()


# ---- Google sign-in for the account itself ------------------------------------------------------------------------

class GoogleLogin:
    """Signs a person in to Link with Google. Asks only for `openid email`; reads nothing else from their account."""

    def __init__(self, cfg: WebConfig, transport: httpx.BaseTransport | None, clock: Callable[[], float]):
        self.cfg, self.clock = cfg, clock
        self._http = httpx.Client(transport=connectors.ConnectorTransport(transport, LOGIN_HOSTS), timeout=20.0, trust_env=False)

    def authorize_url(self, state: str, challenge: str, nonce: str) -> str:
        return connectors.GOOGLE_AUTH + "?" + urlencode({
            "client_id": self.cfg.google_client_id, "redirect_uri": self.cfg.redirect_uri, "response_type": "code",
            "scope": LOGIN_SCOPE, "state": state, "nonce": nonce, "code_challenge": challenge,
            "code_challenge_method": "S256", "prompt": "select_account", "access_type": "online"})

    def email(self, code: str, verifier: str, nonce: str) -> str:
        """Trade the code for Google's signed statement of who this is, check it, and return the confirmed address.

        The statement comes straight from Google's token endpoint over HTTPS, in exchange for Link's client secret,
        so it cannot have been altered in between. Every claim is still checked before it is believed."""
        try:
            resp = self._http.post(connectors.GOOGLE_TOKEN, data={
                "code": code, "client_id": self.cfg.google_client_id, "client_secret": self.cfg.google_client_secret,
                "redirect_uri": self.cfg.redirect_uri, "grant_type": "authorization_code", "code_verifier": verifier})
        except (httpx.HTTPError, connectors.NeverSent):
            raise LoginError("Couldn't reach Google. Try again in a moment.") from None
        if resp.status_code != 200:
            raise LoginError("Google didn't confirm the sign-in. Go back and try again.")
        try:
            token = str(resp.json().get("id_token", ""))
            payload = token.split(".")[1]
            claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        except (ValueError, IndexError, AttributeError):
            raise LoginError("Google's answer wasn't readable. Try again.") from None
        now = self.clock()
        audience = claims.get("aud")
        audiences = audience if isinstance(audience, list) else [audience]
        if claims.get("iss") not in GOOGLE_ISSUERS or self.cfg.google_client_id not in audiences:
            raise LoginError("That sign-in wasn't meant for Link.")
        if not isinstance(claims.get("exp"), (int, float)) or claims["exp"] < now:
            raise LoginError("That sign-in expired. Try again.")
        if not hmac.compare_digest(str(claims.get("nonce", "")), nonce):
            raise LoginError("That sign-in didn't match this browser. Try again.")
        if claims.get("email_verified") is not True or not claims.get("email"):
            raise LoginError("Google hasn't confirmed that email address yet.")
        return normalize_email(str(claims["email"]))


# ---- the front door -----------------------------------------------------------------------------------------------

class WipeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirm: Literal["DELETE EVERYTHING"]


def _page(message: str, status: int = 200, refresh: str | None = None) -> HTMLResponse:
    """A small page for sign-in results. No script, so the strict content policy holds."""
    meta = f'<meta http-equiv="refresh" content="1;url={html.escape(refresh)}">' if refresh else ""
    body = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, '
            f'initial-scale=1"><title>Link</title>{meta}<link rel="stylesheet" href="/static/style.css"></head>'
            f'<body class="login"><main class="login-box"><h1>Link</h1><p>{html.escape(message)}</p>'
            f'<p><a href="/">Back to Link</a></p></main></body></html>')
    return HTMLResponse(body, status_code=status)


def _deny(status: int, reason: str) -> JSONResponse:
    return JSONResponse({"error": reason}, status_code=status)


def create_web_app(cfg: WebConfig, *, transport: httpx.BaseTransport | None = None, clock: Callable[[], float] = time.time,
                   app_kwargs: dict | None = None) -> FastAPI:
    cfg.data_root.mkdir(parents=True, exist_ok=True)
    os.chmod(cfg.data_root, 0o700)
    accounts = Accounts(cfg.data_root / "accounts.sqlite3", clock)
    pool = Pool(cfg, clock, {"google_transport": transport, **(app_kwargs or {})})
    login = GoogleLogin(cfg, transport, clock)
    email_key = _derive(cfg.secret_key, "link-email-v1")
    flows: dict[str, tuple[str, str, str, float]] = {}  # state -> (verifier, nonce, timezone, expiry)
    flows_lock = threading.Lock()
    api_limit = Limiter(API_PER_MINUTE, 60, clock)
    signin_limit = Limiter(SIGNIN_PER_TEN_MINUTES, 600, clock)

    def email_mac(address: str) -> str:
        return hmac.new(email_key, normalize_email(address).encode("utf-8"), hashlib.sha256).hexdigest()

    def client_key(request: Request) -> str:
        if cfg.trust_proxy:  # the host's proxy appends the real address last; earlier entries can be forged
            forwarded = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
            if forwarded:
                return forwarded[-1]
        return request.client.host if request.client else "unknown"

    def delete_account(account: dict) -> None:
        """Cancel the person's Google sign-ins, then remove their folder and their account. Nothing is kept."""
        try:
            pool.get(account).state.cancel_sign_ins()
        except Exception:  # deletion goes ahead even if Google can't be reached; the encrypted file goes with the folder
            log.warning("could not reach Google while deleting an account; its saved sign-ins are deleted anyway")
        pool.close(account["id"])
        shutil.rmtree(pool.folder(account["id"]), ignore_errors=True)
        accounts.delete(account["id"])

    def purge_inactive() -> int:
        gone = accounts.inactive(clock() - INACTIVE_SECONDS)
        for account in gone:
            delete_account(account)
        accounts.purge_sessions()
        if gone:
            log.info("deleted %d accounts unused for 30 days", len(gone))
        return len(gone)

    async def purge_loop() -> None:
        while True:
            try:
                await asyncio.to_thread(purge_inactive)
            except Exception:
                log.exception("the 30-day clean-up failed; it runs again later")
            await asyncio.sleep(PURGE_EVERY_SECONDS)

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        task = asyncio.create_task(purge_loop())
        try:
            yield
        finally:
            task.cancel()

    app = FastAPI(title="Link", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.accounts, app.state.pool, app.state.cfg = accounts, pool, cfg
    app.state.purge_inactive, app.state.email_mac = purge_inactive, email_mac

    def finish(response: Response) -> Response:
        response.headers.update(SECURITY_HEADERS)
        if cfg.secure:
            response.headers["Strict-Transport-Security"] = HSTS
        return response

    def set_session_cookie(response: Response, sid: str) -> None:
        response.set_cookie(cfg.cookie_name, sid, max_age=SESSION_MAX_SECONDS, path="/", secure=cfg.secure,
                            httponly=True, samesite="lax")

    def finish_signin(request: Request) -> Response:
        state = request.query_params.get("state", "")
        with flows_lock:
            now = clock()
            for key in [k for k, v in flows.items() if v[3] < now]:
                del flows[key]
            flow = flows.pop(state, None)
        if flow is None:
            return _page("That sign-in link was already used or has expired. Go back and sign in again.", 400)
        verifier, nonce, timezone, _ = flow
        code = request.query_params.get("code", "")
        if request.query_params.get("error") or not code:
            return _page("Google didn't sign you in. Go back and try again.", 400)
        try:
            address = login.email(code, verifier, nonce)
        except LoginError as exc:
            log.info("sign-in refused: %s", exc)
            return _page(str(exc), 400)
        if address not in cfg.invites:
            log.info("sign-in refused: address not on the invite list")
            return _page("That Google account isn't on the invite list for this test. Ask the person who invited you "
                         "to add the exact address you signed in with.", 403)
        account = accounts.find_or_create(email_mac(address), timezone)
        accounts.end_session(request.cookies.get(cfg.cookie_name))  # a fresh session on every sign-in
        sid, _ = accounts.new_session(account["id"])
        log.info("signed in (%s account)", "new" if account["new"] else "existing")
        response = _page("You're signed in. Taking you to Link.", refresh="/")
        set_session_cookie(response, sid)
        return response

    @app.middleware("http")
    async def guard(request: Request, call_next):
        path, method = request.url.path, request.method.upper()
        # 1. Only this site's own address: defeats DNS rebinding and stray hostnames.
        if request.headers.get("host", "") != cfg.host:
            return finish(_deny(400, "host not allowed"))
        if method not in SAFE_METHODS and method not in {"POST", "PUT", "DELETE"}:
            return finish(_deny(405, "method not allowed"))
        if path.startswith(BLOCKED_PREFIXES) or path in BLOCKED_PATHS:
            return finish(_deny(404, "not found"))
        # 2. Requests from other sites. Following a link here (a page navigation) is fine; anything else is refused.
        origin = request.headers.get("origin")
        if origin is not None and origin != cfg.public_url:
            return finish(_deny(403, "origin not allowed"))
        fetch_site = request.headers.get("sec-fetch-site")
        navigation = method == "GET" and request.headers.get("sec-fetch-mode") == "navigate" and not path.startswith("/api/")
        if fetch_site not in (None, "same-origin", "none") and not navigation:
            return finish(_deny(403, "cross-site request"))
        mutating = method not in SAFE_METHODS
        if mutating:
            if origin is None:
                return finish(_deny(403, "origin required"))
            if method != "DELETE" and not request.headers.get("content-type", "").startswith("application/json"):
                return finish(_deny(415, "json required"))
            try:
                length = int(request.headers.get("content-length", "0"))
            except ValueError:
                return finish(_deny(400, "bad content-length"))
            if length > MAX_BODY_BYTES:
                return finish(_deny(413, "body too large"))
        # 3. Coming back from Google after signing in to Link itself.
        if path == OAUTH_CALLBACK_PATH and request.query_params.get("state", "").startswith(LOGIN_STATE_PREFIX):
            if not signin_limit.allow(client_key(request)):
                return finish(_page("Too many sign-in attempts. Wait a few minutes and try again.", 429))
            return finish(await asyncio.to_thread(finish_signin, request))
        # 4. Who is signed in. Everything personal needs a session, and every change needs the CSRF token too.
        session = await asyncio.to_thread(accounts.session, request.cookies.get(cfg.cookie_name))
        if session is not None:
            request.scope["link.account"], request.scope["link.csrf"] = session["account"], session["csrf"]
        personal = path.startswith("/api/") or path == OAUTH_CALLBACK_PATH
        if personal:
            if session is None:
                if path == OAUTH_CALLBACK_PATH:
                    return finish(_page("Sign in to Link first, then connect again.", 401))
                return finish(_deny(401, "not signed in"))
            if not api_limit.allow(session["account"]["id"]):
                return finish(_deny(429, "too many requests; wait a minute"))
            if mutating and not hmac.compare_digest(request.headers.get(CSRF_HEADER, "").encode(), session["csrf"].encode()):
                return finish(_deny(403, "bad csrf token"))
        return finish(await call_next(request))

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True}

    @app.get("/")
    def index(request: Request) -> Response:
        signed_in = "link.account" in request.scope
        return FileResponse(STATIC / ("index.html" if signed_in else "signin.html"))

    @app.get("/signin")
    def signin(request: Request, tz: str = "") -> Response:
        if not signin_limit.allow(client_key(request)):
            return _page("Too many sign-in attempts. Wait a few minutes and try again.", 429)
        state = LOGIN_STATE_PREFIX + secrets.token_urlsafe(32)
        verifier, nonce = secrets.token_urlsafe(64), secrets.token_urlsafe(24)
        with flows_lock:
            if len(flows) > 5_000:
                flows.clear()  # a flood of abandoned sign-ins; real people just start again
            flows[state] = (verifier, nonce, valid_timezone(tz), clock() + FLOW_SECONDS)
        challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
        return RedirectResponse(login.authorize_url(state, challenge, nonce), status_code=303)

    @app.post("/api/signout")
    def signout(request: Request) -> Response:
        accounts.end_session(request.cookies.get(cfg.cookie_name))
        response = JSONResponse({"signed_out": True})
        response.delete_cookie(cfg.cookie_name, path="/", secure=cfg.secure, httponly=True, samesite="lax")
        return response

    @app.post("/api/wipe")
    def wipe(request: Request, body: WipeIn) -> Response:
        delete_account(request.scope["link.account"])
        log.info("an account deleted itself")
        response = JSONResponse({"ok": True, "account_deleted": True})
        response.delete_cookie(cfg.cookie_name, path="/", secure=cfg.secure, httponly=True, samesite="lax")
        return response

    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    async def personal_copy(scope: dict, receive: Any, send: Any) -> None:
        """Hand the request to the signed-in person's own copy of Link. Nobody else's copy is reachable from here."""
        account = scope.get("link.account")
        if scope["type"] != "http" or account is None:
            response = _deny(404, "not found")
            await response(scope, receive, send)
            return
        inner = await asyncio.to_thread(pool.get, account)
        await inner(scope, receive, send)

    app.router.routes.append(Mount("", app=personal_copy))
    return app
