"""People you email (decision D48).

Reads only who wrote to whom and when: names, addresses and dates from the headers of your newest messages. It never
sees a subject or a message body. A person becomes a suggestion only after a real exchange (you wrote and they wrote
back), and only a click saves them. Nothing here runs unless you connect your email and press the check button.
"""

from __future__ import annotations

import json
from datetime import datetime

from . import people, store
from .db import Database, now
from .encounters import NOT_A_PERSON, _addresses, _remember_address

CONNECTOR_KEY = "connector:google_mail"
MAX_RECIPIENTS = 5  # a message to more people than this is a mass message, not a conversation


def status(db: Database) -> dict | None:
    row = db.one("SELECT value FROM kv WHERE key=?", (CONNECTOR_KEY,))
    return json.loads(row["value"]) if row else None


def _save_status(db: Database, value: dict) -> None:
    db.run("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (CONNECTOR_KEY, json.dumps(value)))


def mark_connected(db: Database, *, demo: bool = False) -> dict:
    value = {"connected_at": now(), "last_sync": None, "demo": demo}
    _save_status(db, value)
    db.log("mail_connected", "demo" if demo else "google")
    return value


def aggregate(messages: list[dict], me: str) -> dict[str, dict]:
    """Per address: how many of the newest messages you sent them and they sent you, and the latest one."""
    stats: dict[str, dict] = {}
    for m in messages:
        if m["bulk"]:
            continue
        parties = [p for p in m["parties"] if p["address"] and p["address"] != me and not NOT_A_PERSON.search(p["address"])]
        if m["direction"] == "sent" and len(parties) > MAX_RECIPIENTS:
            continue
        for p in parties:
            s = stats.setdefault(p["address"], {"name": "", "sent": 0, "received": 0, "last_at": "", "last_direction": ""})
            s["sent" if m["direction"] == "sent" else "received"] += 1
            s["name"] = s["name"] or p["name"]
            if m["at"] > s["last_at"]:
                s["last_at"], s["last_direction"] = m["at"], m["direction"]
    return stats


def _linked_addresses(db: Database) -> dict[str, int]:
    out = {}
    for row in db.q("SELECT key FROM kv WHERE key LIKE 'person_address:%'"):
        item_id = int(row["key"].split(":")[1])
        for address in _addresses(db, item_id):
            out[address] = item_id
    return out


def _write_summary(db: Database, item_id: int, row: dict) -> None:
    value = {"last_at": row["last_at"], "last_direction": row["last_direction"], "sent": row["sent"], "received": row["received"]}
    db.run("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (f"person_email:{item_id}", json.dumps(value)))


def sync(db: Database, provider) -> dict:
    """Read the newest messages once. Only two-way contacts, and people you already know, are written down."""
    stats = aggregate(provider.messages(), provider.self_address())
    linked, added = _linked_addresses(db), 0
    with db.tx():
        for address, s in stats.items():
            item_id = linked.get(address)
            if not (item_id or (s["sent"] >= 1 and s["received"] >= 1)):
                continue
            row = db.one("SELECT * FROM email_contacts WHERE address=?", (address,))
            if row is None:
                db.run("INSERT INTO email_contacts(address,name,sent,received,last_at,last_direction,state,item_id,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                       (address, s["name"][:120], s["sent"], s["received"], s["last_at"], s["last_direction"], "kept" if item_id else "pending", item_id, now()))
                added += 0 if item_id else 1
                row = db.one("SELECT * FROM email_contacts WHERE address=?", (address,))
            else:
                newer = s["last_at"] > row["last_at"]
                state, link = row["state"], row["item_id"]
                if item_id and state in ("pending", "later"):
                    state, link = "kept", item_id
                elif state == "later" and row["decided_at"] and s["last_at"] > row["decided_at"]:
                    state = "pending"  # "not now" ends when there is something newer
                db.run("UPDATE email_contacts SET name=?, sent=?, received=?, last_at=?, last_direction=?, state=?, item_id=?, updated_at=? WHERE address=?",
                       (row["name"] or s["name"][:120], s["sent"], s["received"], max(row["last_at"], s["last_at"]),
                        s["last_direction"] if newer else row["last_direction"], state, link, now(), address))
                row = db.one("SELECT * FROM email_contacts WHERE address=?", (address,))
            if row["state"] == "kept" and row["item_id"]:
                _write_summary(db, row["item_id"], row)
    state = status(db) or mark_connected(db, demo=getattr(provider, "demo", False))
    state["last_sync"] = now()
    _save_status(db, state)
    db.log("mail_synced", f"messages_seen={len(stats)} new={added}")
    return {"people_seen": len(stats), "found": added}


def matches(db: Database, name: str) -> list[dict]:
    """Existing people with the same name. A suggestion, not proof."""
    out = []
    for row in db.q("SELECT id,title FROM items WHERE kind='relationship' AND lower(title)=lower(?)", (name,)) if name else []:
        out.append({"id": row["id"], "name": row["title"], "why": "Same name"})
    return out


def pending(db: Database) -> list[dict]:
    rows = db.q("SELECT * FROM email_contacts WHERE state='pending' ORDER BY last_at DESC, id")
    return [{**r, "matches": matches(db, r["name"])} for r in rows]


def _contact(db: Database, contact_id: int) -> dict:
    row = db.one("SELECT * FROM email_contacts WHERE id=?", (contact_id,))
    if not row:
        raise store.RuleError("That suggestion isn't there any more.")
    if row["state"] not in ("pending", "later"):
        raise store.RuleError("You've already decided on this one.")
    return row


def keep(db: Database, contact_id: int, name: str | None = None, person_id: int | None = None) -> dict:
    """Save the person, or link someone you already have. Saves no conversation and no message."""
    c = _contact(db, contact_id)
    with db.tx():
        if person_id is not None:
            people.get_person(db, person_id)
            saved = people.person_detail(db, person_id)
        else:
            chosen = (name if name is not None else (c["name"] or c["address"].split("@")[0])).strip()
            if not chosen:
                raise store.RuleError("Give this person a name first.")
            saved = people.save_person(db, None, {"name": chosen[:120], "org": "", "profile_link": "", "context": "", "notes": "", "category": ""})
        _remember_address(db, saved["id"], c["address"])
        db.run("UPDATE email_contacts SET state='kept', item_id=?, decided_at=?, updated_at=? WHERE id=?", (saved["id"], now(), now(), contact_id))
        _write_summary(db, saved["id"], c)
    db.log("email_contact_kept", f"contact={contact_id} person={saved['id']}")
    return saved


def dismiss(db: Database, contact_id: int, scope: str = "later") -> dict:
    """`later` hides this person until there is a newer message. `never` stops suggesting this address for good."""
    _contact(db, contact_id)
    if scope not in ("later", "never"):
        raise store.RuleError("Choose not now, or never.")
    db.run("UPDATE email_contacts SET state=?, decided_at=?, updated_at=? WHERE id=?", ("later" if scope == "later" else "never", now(), now(), contact_id))
    db.log("email_contact_dismissed", f"contact={contact_id} scope={scope}")
    return {"dismissed": True, "scope": scope}


def person_summary(db: Database, item_id: int) -> dict | None:
    row = db.one("SELECT value FROM kv WHERE key=?", (f"person_email:{item_id}",))
    return json.loads(row["value"]) if row else None


def disconnect(db: Database, provider, remove_data: bool) -> dict:
    """Cancel the sign-in. With `remove_data`, delete what came from email except people you kept."""
    provider.disconnect()
    with db.tx():
        db.run("DELETE FROM kv WHERE key=?", (CONNECTOR_KEY,))
        if remove_data:
            db.run("DELETE FROM email_contacts")
            db.run("DELETE FROM kv WHERE key LIKE 'person_email:%'")
    db.log("mail_disconnected", "removed_data" if remove_data else "kept_data")
    return {"disconnected": True, "removed_data": remove_data}
