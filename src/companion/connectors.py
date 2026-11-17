"""Calendar connectors (decision D39). Read-only.

Nothing here runs unless the user connects a calendar. No code path creates, edits, accepts or deletes a
calendar event, sends a message, or reads anything outside the fields asked for below. Outbound traffic goes
through a transport that refuses every host except Google's sign-in and calendar API hosts.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"  # opened by the browser, never fetched by Link
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE = "https://oauth2.googleapis.com/revoke"
GOOGLE_EVENTS = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
GOOGLE_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"
# Only the fields D39 lists: title, times, status, attendee names and addresses. No description, location or notes.
GOOGLE_FIELDS = ("items(id,summary,status,start,end,recurringEventId,"
                 "attendees(email,displayName,self,responseStatus,resource),organizer(self)),nextPageToken")
CALENDAR_HOSTS = frozenset({"oauth2.googleapis.com", "www.googleapis.com"})
TOKEN_ACCOUNT = "google-calendar-refresh-token"
FLOW_SECONDS = 600
MAX_PENDING_FLOWS = 5
MAX_EVENTS = 250


class ConnectorError(Exception):
    """The message is safe to show the user. It never contains a token or a raw response."""


class NeverSent(Exception):
    """A request was refused before leaving this computer."""


class ConnectorTransport(httpx.BaseTransport):
    """Outbound allowlist for calendar traffic. HTTPS to the listed hosts only."""

    def __init__(self, inner: httpx.BaseTransport | None = None, hosts: frozenset[str] = CALENDAR_HOSTS):
        self.inner = inner or httpx.HTTPTransport()
        self.hosts = hosts

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if request.url.scheme != "https" or request.url.host not in self.hosts:
            raise NeverSent(f"blocked outbound request to {request.url.host}")
        return self.inner.handle_request(request)


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


class OAuthFlows:
    """Sign-ins in progress. Each `state` is random, works once, and expires. Held in memory only."""

    def __init__(self, clock=time.time):
        self._clock = clock
        self._pending: dict[str, tuple[str, float]] = {}

    def begin(self) -> tuple[str, str]:
        """Returns (state, code_challenge). The PKCE verifier stays here."""
        now = self._clock()
        self._pending = {s: v for s, v in self._pending.items() if v[1] > now}
        while len(self._pending) >= MAX_PENDING_FLOWS:
            self._pending.pop(next(iter(self._pending)))
        state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
        self._pending[state] = (verifier, now + FLOW_SECONDS)
        return state, _b64(hashlib.sha256(verifier.encode()).digest())

    def take(self, state: str) -> str | None:
        """Returns the verifier once for a live state, otherwise None. A second use fails."""
        found = None
        for known in list(self._pending):
            if secrets.compare_digest(known.encode(), (state or "").encode()):
                found = known
        if found is None:
            return None
        verifier, expires = self._pending.pop(found)
        return verifier if expires > self._clock() else None


class GoogleCalendar:
    name = "google_calendar"
    demo = False

    def __init__(self, client_id: str, client_secret: str, store, transport: httpx.BaseTransport | None = None, clock=time.time):
        self.client_id, self.client_secret, self.store, self._clock = client_id, client_secret, store, clock
        self._http = httpx.Client(transport=ConnectorTransport(transport), timeout=20.0, trust_env=False)
        self._access: tuple[str, float] | None = None

    @property
    def configured(self) -> bool:
        return bool(self.client_id)

    def has_token(self) -> bool:
        return self.store.get(TOKEN_ACCOUNT) is not None

    def authorize_url(self, redirect_uri: str, state: str, challenge: str) -> str:
        if not self.configured:
            raise ConnectorError("Calendar sign-in isn't set up in this copy of Link yet.")
        return GOOGLE_AUTH + "?" + urlencode({
            "client_id": self.client_id, "redirect_uri": redirect_uri, "response_type": "code", "scope": GOOGLE_SCOPE,
            "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
            "access_type": "offline", "prompt": "consent"})

    def _token_request(self, data: dict) -> dict:
        body = {"client_id": self.client_id, **data}
        if self.client_secret:
            body["client_secret"] = self.client_secret
        try:
            resp = self._http.post(GOOGLE_TOKEN, data=body)
        except (httpx.HTTPError, NeverSent):
            raise ConnectorError("Couldn't reach Google. Check your connection and try again.") from None
        if resp.status_code != 200:
            if data.get("grant_type") == "refresh_token":
                self.store.delete(TOKEN_ACCOUNT)
                self._access = None
                raise ConnectorError("Google no longer accepts the saved sign-in. Connect your calendar again.")
            raise ConnectorError("Google didn't accept the sign-in. Try connecting again.")
        return resp.json()

    def complete(self, code: str, verifier: str, redirect_uri: str) -> None:
        tokens = self._token_request({"code": code, "code_verifier": verifier, "redirect_uri": redirect_uri,
                                      "grant_type": "authorization_code"})
        refresh = tokens.get("refresh_token")
        if not refresh:
            raise ConnectorError("Google didn't return a long-lasting sign-in. Remove Link's access in your Google "
                                 "account, then connect again.")
        self.store.set(TOKEN_ACCOUNT, refresh)
        self._access = (tokens["access_token"], self._clock() + int(tokens.get("expires_in", 3600)) - 60)

    def _access_token(self) -> str:
        if self._access and self._access[1] > self._clock():
            return self._access[0]
        refresh = self.store.get(TOKEN_ACCOUNT)
        if not refresh:
            raise ConnectorError("Your calendar isn't connected.")
        tokens = self._token_request({"refresh_token": refresh, "grant_type": "refresh_token"})
        self._access = (tokens["access_token"], self._clock() + int(tokens.get("expires_in", 3600)) - 60)
        return self._access[0]

    def events(self, time_min: datetime, time_max: datetime) -> list[dict]:
        params = {"timeMin": time_min.astimezone(timezone.utc).isoformat(), "timeMax": time_max.astimezone(timezone.utc).isoformat(),
                  "singleEvents": "true", "orderBy": "startTime", "maxResults": str(MAX_EVENTS), "fields": GOOGLE_FIELDS}
        try:
            resp = self._http.get(GOOGLE_EVENTS, params=params, headers={"Authorization": "Bearer " + self._access_token()})
        except (httpx.HTTPError, NeverSent):
            raise ConnectorError("Couldn't reach Google Calendar. Try again in a moment.") from None
        if resp.status_code == 401:
            self._access = None
            raise ConnectorError("Google asked Link to sign in again. Try checking your calendar once more.")
        if resp.status_code != 200:
            raise ConnectorError("Google Calendar didn't share your events (status " + str(resp.status_code) + ").")
        return [normalize_google(item) for item in resp.json().get("items", [])]

    def disconnect(self) -> None:
        refresh = self.store.get(TOKEN_ACCOUNT)
        self.store.delete(TOKEN_ACCOUNT)
        self._access = None
        if refresh:  # Best effort: ask Google to cancel the grant. The local sign-in is already gone either way.
            try:
                self._http.post(GOOGLE_REVOKE, data={"token": refresh})
            except (httpx.HTTPError, NeverSent):
                pass


def _when(value: dict) -> tuple[str, bool]:
    if value.get("dateTime"):
        return value["dateTime"], False
    return value.get("date", ""), True


def normalize_google(item: dict) -> dict:
    start, all_day = _when(item.get("start", {}))
    end, _ = _when(item.get("end", {}))
    attendees = [{"email": (a.get("email") or "").strip().lower(), "name": (a.get("displayName") or "").strip(),
                  "self": bool(a.get("self")), "response": a.get("responseStatus", ""), "resource": bool(a.get("resource"))}
                 for a in item.get("attendees", [])]
    return {"id": str(item.get("id", ""))[:200], "title": (item.get("summary") or "")[:300], "start": start, "end": end,
            "all_day": all_day, "status": item.get("status", ""), "recurring": bool(item.get("recurringEventId")),
            "attendees": attendees}


class SampleCalendar:
    """Fictional events for the demo, so the flow can be tried without a Google account or network."""

    name = "google_calendar"
    demo = True
    configured = True

    def __init__(self, clock=lambda: datetime.now(timezone.utc)):
        self._clock = clock

    def has_token(self) -> bool:
        return True

    def authorize_url(self, redirect_uri: str, state: str, challenge: str) -> str:
        raise ConnectorError("The sample calendar needs no sign-in.")

    def complete(self, code: str, verifier: str, redirect_uri: str) -> None:
        raise ConnectorError("The sample calendar needs no sign-in.")

    def disconnect(self) -> None:
        return None

    def events(self, time_min: datetime, time_max: datetime) -> list[dict]:
        base = self._clock().replace(hour=10, minute=0, second=0, microsecond=0)
        me = {"email": "you@example.com", "name": "You", "self": True, "response": "accepted", "resource": False}

        def person(name, address, response="accepted"):
            return {"email": address, "name": name, "self": False, "response": response, "resource": False}

        def event(key, title, days, attendees, **extra):
            start = base + timedelta(days=days)
            return {"id": "sample-" + key, "title": title, "start": start.isoformat(), "end": (start + timedelta(hours=1)).isoformat(),
                    "all_day": False, "status": "confirmed", "recurring": False, "attendees": attendees, **extra}

        return [
            event("coffee", "Coffee chat with Maya", -3, [me, person("Maya Lindqvist", "maya.lindqvist@example.com")]),
            event("informational", "Informational interview: data careers", 2, [me, person("Priya Venkataraman", "priya.v@example.com")]),
            event("mentor", "Mentor catch-up", 5, [me, person("", "sam.ortega@example.com")]),
            event("meetup", "Data Club weekly", 1, [me] + [person("Member %d" % i, "member%d@example.com" % i) for i in range(9)]),
            event("lecture", "Statistics lecture", -1, [me, person("Prof. Okafor", "okafor@example.com")], recurring=True),
            event("solo", "Study block", 0, [me]),
            event("declined", "Call with a recruiter", 3, [{**me, "response": "declined"}, person("Recruiter", "recruiter@example.com")]),
            {**event("allday", "Career week", 4, [me, person("Ada Mensah", "ada.mensah@example.com")]), "all_day": True},
        ]
