"""People found in a connected calendar (decision D39).

Capture by default, confirm by exception: events become candidates, and only a click makes a person.
An invitation is not a conversation, so keeping a candidate saves a person and nothing else.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone

from . import people, store
from .db import Database, now

SOURCE = "google_calendar"
PAST_DAYS, FUTURE_DAYS = 21, 14
MAX_SMALL_MEETING = 6
MAX_IGNORED = 500
CHECKIN_DELAY = timedelta(hours=1)    # asked about an hour after the event ends
CHECKIN_EXPIRES = timedelta(days=7)   # then quietly dropped; no reminders about reminders
PROMISE_REMINDER_DAYS = 3
ANSWERS = ("great", "fine", "skip")
CONNECTOR_KEY = "connector:google_calendar"
IGNORE_KEY = "calendar_ignore"

KEYWORDS = ("coffee", "networking", "career fair", "informational", "info session", "mentor", "meetup", "meet up",
            "intro call", "introduction", "interview", "recruiter", "alumni", "chat with")
# Addresses that are not people: notification senders, group calendars, rooms.
NOT_A_PERSON = re.compile(r"(^|[._-])(no-?reply|donotreply|notifications?|calendar|invites?|bot)([._-]|@)|"
                          r"@(group|resource)\.calendar\.google\.com$", re.I)


def guess_name(address: str) -> str:
    parts = [p for p in re.split(r"[._\-+]+", address.split("@")[0]) if p and not p.isdigit()]
    return " ".join(p.capitalize() for p in parts)[:80] or address


def _keyword(title: str) -> str | None:
    lowered = title.lower()
    return next((k for k in KEYWORDS if k in lowered), None)


def detect(event: dict, ignored: set[str]) -> list[dict]:
    """Candidates for one event: one per attendee who might be a person to remember. Empty when the event is noise."""
    if event["status"] == "cancelled" or event["all_day"] or not event["start"]:
        return []
    mine = next((a for a in event["attendees"] if a["self"]), None)
    if mine and mine["response"] == "declined":
        return []
    others = [a for a in event["attendees"]
              if not a["self"] and not a["resource"] and a["email"] and not NOT_A_PERSON.search(a["email"])]
    if not others:
        return []
    keyword = _keyword(event["title"])
    if (event["recurring"] or len(others) > MAX_SMALL_MEETING) and not keyword:
        return []  # classes, standing meetings and large groups
    reason = (f"The title mentions “{keyword}”." if keyword
              else f"A meeting with {len(others)} other {'person' if len(others) == 1 else 'people'}.")
    return [{"address": a["email"][:254], "name": (a["name"] or guess_name(a["email"]))[:120], "name_guessed": 0 if a["name"] else 1,
             "title": event["title"][:300], "starts_at": event["start"], "ends_at": event["end"], "reason": reason}
            for a in others if a["email"] not in ignored]


def _ignored(db: Database) -> set[str]:
    row = db.one("SELECT value FROM kv WHERE key=?", (IGNORE_KEY,))
    return set(json.loads(row["value"])) if row else set()


def status(db: Database) -> dict | None:
    row = db.one("SELECT value FROM kv WHERE key=?", (CONNECTOR_KEY,))
    return json.loads(row["value"]) if row else None


def _save_status(db: Database, value: dict) -> None:
    db.run("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (CONNECTOR_KEY, json.dumps(value)))


def mark_connected(db: Database, *, demo: bool = False) -> dict:
    value = {"connected_at": now(), "last_sync": None, "demo": demo}
    _save_status(db, value)
    db.log("calendar_connected", "demo" if demo else "google")
    return value


def sync(db: Database, provider, today: datetime | None = None) -> dict:
    """Read events once and record new candidates. Runs only when the user asks; there is no background sync yet."""
    current = today or datetime.now(timezone.utc)
    events = provider.events(current - timedelta(days=PAST_DAYS), current + timedelta(days=FUTURE_DAYS))
    ignored = _ignored(db)
    added = skipped = 0
    with db.tx():
        for event in events:
            for c in detect(event, ignored):
                known = db.one("SELECT 1 FROM encounter_candidates WHERE source=? AND event_id=? AND address=?",
                               (SOURCE, event["id"], c["address"]))
                if known:
                    skipped += 1
                    continue
                db.run("INSERT INTO encounter_candidates(source,event_id,address,name,name_guessed,title,starts_at,ends_at,reason,created_at)"
                       " VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (SOURCE, event["id"], c["address"], c["name"], c["name_guessed"], c["title"], c["starts_at"], c["ends_at"], c["reason"], now()))
                added += 1
    state = status(db) or mark_connected(db, demo=getattr(provider, "demo", False))
    state["last_sync"] = now()
    _save_status(db, state)
    db.log("calendar_synced", f"events={len(events)} found={added}")
    return {"events_read": len(events), "found": added, "already_known": skipped}


def _addresses(db: Database, item_id: int) -> list[str]:
    row = db.one("SELECT value FROM kv WHERE key=?", (f"person_address:{item_id}",))
    return json.loads(row["value"]) if row else []


def _remember_address(db: Database, item_id: int, address: str) -> None:
    known = _addresses(db, item_id)
    if address not in known:
        db.run("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
               (f"person_address:{item_id}", json.dumps(known + [address])))


def matches(db: Database, name: str, address: str) -> list[dict]:
    """Existing people this could be. A suggestion, not proof."""
    found: dict[int, str] = {}
    for row in db.q("SELECT key,value FROM kv WHERE key LIKE 'person_address:%'"):
        if address in json.loads(row["value"]):
            found[int(row["key"].split(":")[1])] = "Same email address"
    for row in db.q("SELECT id,title FROM items WHERE kind='relationship' AND lower(title)=lower(?)", (name,)):
        found.setdefault(row["id"], "Same name")
    out = []
    for item_id, why in found.items():
        item = store.get(db, "items", item_id)
        if item:
            out.append({"id": item_id, "name": item["title"], "why": why})
    return out


def pending(db: Database) -> list[dict]:
    rows = db.q("SELECT * FROM encounter_candidates WHERE state='pending' ORDER BY starts_at DESC, id")
    return [{**r, "name_guessed": bool(r["name_guessed"]), "matches": matches(db, r["name"], r["address"])} for r in rows]


def _candidate(db: Database, candidate_id: int) -> dict:
    row = db.one("SELECT * FROM encounter_candidates WHERE id=?", (candidate_id,))
    if not row:
        raise store.RuleError("That suggestion isn't there any more.")
    if row["state"] != "pending":
        raise store.RuleError("You've already decided on this one.")
    return row


def keep(db: Database, candidate_id: int, name: str | None = None, person_id: int | None = None) -> dict:
    """Save the person (or link an existing one). Saves no conversation, since an invitation isn't one."""
    c = _candidate(db, candidate_id)
    with db.tx():
        if person_id is not None:
            people.get_person(db, person_id)  # raises when it doesn't exist
            saved = people.person_detail(db, person_id)
        else:
            chosen = (name if name is not None else c["name"]).strip()
            if not chosen:
                raise store.RuleError("Give this person a name first.")
            saved = people.save_person(db, None, {"name": chosen[:120], "org": "", "profile_link": "", "context": "", "notes": "", "category": ""})
        _remember_address(db, saved["id"], c["address"])
        db.run("UPDATE encounter_candidates SET state='kept', item_id=?, decided_at=? WHERE id=?", (saved["id"], now(), candidate_id))
    db.log("encounter_kept", f"candidate={candidate_id} person={saved['id']}")
    return saved


def dismiss(db: Database, candidate_id: int, scope: str = "event") -> dict:
    """`event` hides this suggestion. `person` also stops suggesting this address from any event."""
    c = _candidate(db, candidate_id)
    if scope not in ("event", "person"):
        raise store.RuleError("Choose whether to hide this event or this person.")
    with db.tx():
        db.run("UPDATE encounter_candidates SET state='dismissed', decided_at=? WHERE id=?", (now(), candidate_id))
        if scope == "person":
            ignored = sorted(_ignored(db) | {c["address"]})[-MAX_IGNORED:]
            db.run("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (IGNORE_KEY, json.dumps(ignored)))
            db.run("UPDATE encounter_candidates SET state='dismissed', decided_at=? WHERE state='pending' AND address=?", (now(), c["address"]))
    db.log("encounter_dismissed", f"candidate={candidate_id} scope={scope}")
    return {"dismissed": True, "scope": scope}


def disconnect(db: Database, provider, remove_data: bool) -> dict:
    """Cancel the sign-in. With `remove_data`, also delete everything that came from the calendar except people the user kept."""
    provider.disconnect()
    with db.tx():
        db.run("DELETE FROM kv WHERE key=?", (CONNECTOR_KEY,))
        if remove_data:
            kept = {r["item_id"] for r in db.q("SELECT item_id FROM encounter_candidates WHERE state='kept' AND item_id IS NOT NULL")}
            db.run("DELETE FROM encounter_candidates WHERE source=?", (SOURCE,))
            db.run("DELETE FROM kv WHERE key=?", (IGNORE_KEY,))
            for item_id in kept:
                db.run("DELETE FROM kv WHERE key=?", (f"person_address:{item_id}",))
    db.log("calendar_disconnected", "removed_data" if remove_data else "kept_data")
    return {"disconnected": True, "removed_data": remove_data}


# ---- post-event check-in (decision D44) -----------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _ended(row: dict) -> datetime:
    return _parse(row["ends_at"] or row["starts_at"])


def due_checkins(db: Database, current: datetime | None = None) -> list[dict]:
    """Meetings with people you kept that ended at least an hour ago and have not been answered. Old ones expire quietly."""
    current = current or _now()
    due = []
    rows = db.q("SELECT * FROM encounter_candidates WHERE state='kept' AND item_id IS NOT NULL AND checkin_state='open' ORDER BY ends_at, starts_at, id")
    for row in rows:
        ended = _ended(row)
        if current > ended + CHECKIN_EXPIRES:
            db.run("UPDATE encounter_candidates SET checkin_state='expired', checkin_at=? WHERE id=?", (now(), row["id"]))
        elif current >= ended + CHECKIN_DELAY:
            person = store.get(db, "items", row["item_id"])
            if person:
                due.append({"id": row["id"], "item_id": row["item_id"], "name": person["title"], "title": row["title"],
                            "starts_at": row["starts_at"], "ends_at": row["ends_at"]})
    return due


def answer_checkin(db: Database, candidate_id: int, answer: str, note: str = "", promise: str = "", current: datetime | None = None) -> dict:
    """Great or Fine saves a short note dated to the meeting, because answering is how you say it happened. Skip saves nothing."""
    if answer not in ANSWERS:
        raise store.RuleError("Choose Great, Fine or Skip.")
    row = db.one("SELECT * FROM encounter_candidates WHERE id=?", (candidate_id,))
    if not row or row["state"] != "kept" or row["item_id"] is None:
        raise store.RuleError("That check-in isn't there any more.")
    if row["checkin_state"] != "open":
        raise store.RuleError("You've already answered this one.")
    note, promise = " ".join(note.split()), " ".join(promise.split())
    result = {"logged": False, "interaction_id": None, "next_step": False, "promise_in_note": False}
    with db.tx():
        if answer == "skip":
            db.run("UPDATE encounter_candidates SET checkin_state='skipped', checkin_at=? WHERE id=?", (now(), candidate_id))
        else:
            current = current or _now()
            parts = [f"{row['title'] or 'Meeting'}. {'Went well.' if answer == 'great' else 'Went fine.'}"]
            if note:
                parts.append(note)
            if promise:
                parts.append(f"I said I would: {promise}")
            when = people.resolve_when({"kind": "date", "date": row["starts_at"][:10]}, current.date())
            log = store.insert(db, "interactions", item_id=row["item_id"], source="calendar_checkin", note=" ".join(parts),
                               commitments=promise, **when)
            result.update(logged=True, interaction_id=log["id"])
            db.run("UPDATE encounter_candidates SET checkin_state='done', checkin_at=?, interaction_id=? WHERE id=?",
                   (now(), log["id"], candidate_id))
    if result["logged"] and promise:  # after the note is saved: setting a next step opens its own transaction
        if people.next_action(db, row["item_id"]):
            result["promise_in_note"] = True  # never replace a step the person already has
        else:
            people.set_next_action(db, row["item_id"], promise, (current.date() + timedelta(days=PROMISE_REMINDER_DAYS)).isoformat())
            result["next_step"] = True
    db.log("checkin_answered", f"candidate={candidate_id} answer={answer} promise={bool(promise)}")
    return result

