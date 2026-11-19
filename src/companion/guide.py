"""The step-by-step guide for adding a person (decision D52).

The guide asks a few short questions: who, how you met, what you remember, and what to do next. It saves the answers
in one go. Everything is checked before anything is written, so a mistake in a later answer can't leave half a person
behind. A person found in the calendar or email can be the starting point; then that suggestion is kept, exactly as
pressing Keep would, and the guide adds the rest.
"""

from __future__ import annotations

from datetime import date, timedelta

from . import encounters, mailbook, people, store
from .db import Database


def _clean(text: str) -> str:
    return " ".join((text or "").split())


def _check_source(db: Database, source: dict | None) -> None:
    if not source:
        return
    table = "encounter_candidates" if source["kind"] == "calendar" else "email_contacts"
    row = db.one(f"SELECT state FROM {table} WHERE id=?", (source["id"],))
    if row is None:
        raise store.RuleError("That suggestion isn't there any more. Type the name instead.")
    if row["state"] not in ("pending", "later"):
        raise store.RuleError("You've already decided on that suggestion. Type the name instead.")


def save_connection(db: Database, data: dict, today: date) -> dict:
    """Save a person from the guide's answers. Returns the person and a plain summary of what was saved."""
    name = _clean(data["name"])
    if not name:
        raise store.RuleError("Give this person a name first.")
    org, context = _clean(data.get("org", "")), _clean(data.get("context", ""))
    memory = (data.get("memory") or "").strip()
    next_step = _clean(data.get("next_step", ""))
    when = data.get("when") or {"kind": "unknown"}
    people.resolve_when(when, today)  # raises before anything is written
    _check_source(db, data.get("source"))
    days = data.get("remind_in_days")
    remind_on = (today + timedelta(days=days)).isoformat() if (next_step and days is not None) else None

    source = data.get("source")
    if source and source["kind"] == "calendar":
        person = encounters.keep(db, source["id"], name=name)
    elif source and source["kind"] == "email":
        person = mailbook.keep(db, source["id"], name=name)
    else:
        person = people.save_person(db, None, {"name": name, "org": org, "profile_link": "", "context": context,
                                               "notes": "", "category": "getting_acquainted"})
    pid = person["id"]
    if source and (org or context):
        current = people.get_person(db, pid)
        people.save_person(db, pid, {"name": name, "org": org or current.get("org", ""), "profile_link": current.get("profile_link", ""),
                                     "context": context or current.get("shareable_context", ""),
                                     "notes": current.get("private_notes", ""), "category": current.get("category") or "getting_acquainted"})

    note = memory or context  # "Met at a career fair" is worth a dated line on its own
    if note:
        people.create_log(db, note=note, item_id=pid, when=when, exchange="", keep_exchange=False, today=today)
    if next_step:
        people.set_next_action(db, pid, next_step, remind_on)
    db.log("guide_saved", f"person={pid} source={source['kind'] if source else 'typed'} note={bool(note)} next={bool(next_step)}")
    return {"person": people.person_detail(db, pid), "logged": bool(note), "next_step": next_step or None, "remind_on": remind_on}
