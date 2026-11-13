"""Workflows: the session briefing, onboarding, chat turns, proposals, drafting, comparison."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import context, store
from .ai import AIUnavailable, CompanionTurn, CompareOut, DraftOut, ExtractOut, Gateway
from .config import Settings
from .db import Database, now
from .ranking import Option, rank
from .validate import quantities, validate_draft

MAX_PROPOSALS_PER_TURN = 3

ONBOARDING = [
    ("goal", "Would you like help meeting people, keeping in touch, or both?", "Start wherever you are. No existing network required."),
    ("preference", "How would you like your companion to work with you?", "For example: a proactive colleague with clear recommendations, a quiet assistant, or someone to explore ideas with."),
]


def local_today(settings: Settings) -> date:
    return datetime.now(timezone.utc).astimezone(ZoneInfo(settings.timezone)).date()


# ---- sessions -------------------------------------------------------------------------

def active_session(db: Database) -> dict | None:
    return db.one("SELECT * FROM sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1")


def start_session(db: Database, minutes: int, action_id: int | None) -> dict:
    db.run("UPDATE sessions SET ended_at=? WHERE ended_at IS NULL", (now(),))
    sid = db.run("INSERT INTO sessions(started_at,minutes,focus_action_id) VALUES(?,?,?)", (now(), minutes, action_id))
    return db.one("SELECT * FROM sessions WHERE id=?", (sid,))  # type: ignore[return-value]


def end_session(db: Database) -> None:
    db.run("UPDATE sessions SET ended_at=? WHERE ended_at IS NULL", (now(),))


def ensure_session(db: Database) -> dict:
    return active_session(db) or start_session(db, 20, None)


# ---- briefing: code-generated, costs nothing ------------------------------------------

def _option(o: Option, db: Database) -> dict:
    item = store.get(db, "items", o.action["item_id"]) if o.action["item_id"] else None
    return {"action": o.action, "reasons": o.reasons,
            "item": {"id": item["id"], "title": item["title"], "org": item["org"]} if item else None}


def today_view(db: Database, settings: Settings, minutes: int) -> dict:
    today = local_today(settings)
    reminders = store.due_reminders(db, today)
    last = db.one("SELECT * FROM sessions ORDER BY id DESC LIMIT 1")
    options = rank(store.rows(db, "actions"), minutes, today,
                   last_focus_id=last["focus_action_id"] if last else None,
                   reminder_action_ids={r["action_id"] for r in reminders if r["action_id"]})
    days_away = None
    if last:
        days_away = (datetime.now(timezone.utc) - datetime.fromisoformat(last["started_at"])).days

    if not options:
        greeting = ("Nothing is waiting on you. Add an opportunity or a follow-up when one comes up, "
                    "or park an idea. No need to invent work.")
    else:
        top = options[0]
        opener = "" if not days_away else (
            f"Welcome back. It's been {days_away} day{'s' if days_away != 1 else ''}, and nothing needs catching up. ")
        left = top.action["where_left_off"]
        greeting = (f"{opener}With {minutes} minutes, I'd do one thing: {top.action['title']}. "
                    + " ".join(top.reasons[:2])
                    + (f" You left it at: {left}" if left and left != store.STATE_NOTES["suggested"] else ""))
    active = active_session(db)
    return {
        "minutes": minutes, "greeting": greeting, "days_away": days_away,
        # Only a session the user started on a specific action has a timer.
        "session": active if active and active["focus_action_id"] else None,
        "today": today.isoformat(),
        "recommended": _option(options[0], db) if options else None,
        "alternatives": [_option(o, db) for o in options[1:]],
        "reminders": reminders,
        "parked_ideas": db.one("SELECT COUNT(*) AS n FROM ideas WHERE state='parked'")["n"],
    }


def options_text(db: Database, settings: Settings, minutes: int) -> str:
    view = today_view(db, settings, minutes)
    opts = ([view["recommended"]] if view["recommended"] else []) + view["alternatives"]
    return "\n".join(f"- {o['action']['title']} ({o['action']['state']}): {' '.join(o['reasons'])}" for o in opts)


# ---- onboarding: scripted, works without AI -------------------------------------------

def onboarding_state(db: Database) -> dict:
    row = db.one("SELECT value FROM kv WHERE key='onboarding_step'")
    step = int(row["value"]) if row else 0
    done = step >= len(ONBOARDING)
    return {"done": done, "step": step, "total": len(ONBOARDING),
            "question": None if done else ONBOARDING[step][1],
            "hint": None if done else ONBOARDING[step][2]}


def onboarding_answer(db: Database, text: str) -> dict:
    state = onboarding_state(db)
    if state["done"]:
        return state
    kind = ONBOARDING[state["step"]][0]
    if text.strip():
        store.insert(db, "memory", kind=kind, text=text.strip(), provenance="user_typed")
    db.run("INSERT INTO kv(key,value) VALUES('onboarding_step',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
           (str(state["step"] + 1),))
    return onboarding_state(db)


# ---- chat -----------------------------------------------------------------------------

def _valid_proposal(p) -> dict | None:
    text = p.text.strip()[:500]
    if not text:
        return None
    if p.kind == "memory":
        if p.memory_kind not in store.MEMORY_KINDS:
            return None
        return {"memory_kind": p.memory_kind, "text": text}
    if p.kind == "reminder":
        try:
            due = date.fromisoformat(p.due_on)
        except ValueError:
            due = date.today() + timedelta(days=3)
        return {"text": text, "due_on": due.isoformat()}
    if p.kind == "idea":
        return {"text": text}
    return None


def chat_turn(db: Database, gateway: Gateway, settings: Settings, message: str, import_id: int | None, context_item_id: int | None = None) -> dict:
    session = ensure_session(db)
    import_row = store.get(db, "imports", import_id) if import_id else None
    previous = db.one("SELECT value FROM kv WHERE key='chat_context_item'")
    scope = str(context_item_id or "")
    if previous and previous["value"] != scope:
        end_session(db)
        session = ensure_session(db)
    db.run("INSERT INTO kv(key,value) VALUES('chat_context_item',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (scope,))
    tainted = int(bool(import_row or context_item_id))
    system, user, meta = context.planning_context(
        db, session, message, import_row, options_text(db, settings, session["minutes"]), context_item_id)
    store.insert(db, "messages", session_id=session["id"], role="user", content=message, has_import=tainted)
    try:
        turn = gateway.call("companion_turn", system, user, CompanionTurn, session_id=session["id"], meta=meta)
    except AIUnavailable as e:
        return {"reply": None, "unavailable": e.reason, "proposals": [], "dropped_proposals": 0}
    assert isinstance(turn, CompanionTurn)
    store.insert(db, "messages", session_id=session["id"], role="assistant", content=turn.reply, has_import=tainted)

    created, dropped = [], 0
    if tainted:
        # Structural rule (D4): a turn that read pasted material cannot propose anything.
        dropped = len(turn.proposals)
        if dropped:
            db.log("proposals_dropped_import_turn", f"count={dropped}")
    else:
        for p in turn.proposals[:MAX_PROPOSALS_PER_TURN]:
            payload = _valid_proposal(p)
            if payload is None:
                dropped += 1
                continue
            created.append(store.insert(db, "proposals", kind=p.kind, payload=payload,
                                        rationale=p.rationale[:300], session_id=session["id"]))
        dropped += max(0, len(turn.proposals) - MAX_PROPOSALS_PER_TURN)
    return {"reply": turn.reply, "unavailable": None, "proposals": created, "dropped_proposals": dropped}


def decide_proposal(db: Database, proposal_id: int, accept: bool) -> dict:
    """Only reachable from an authenticated, CSRF-checked user request."""
    with db.tx():
        p = store.get(db, "proposals", proposal_id)
        if not p or p["state"] != "pending":
            raise store.RuleError("That suggestion was already handled.")
        result = None
        if accept:
            payload = p["payload"]
            if p["kind"] == "memory":
                result = store.insert(db, "memory", kind=payload["memory_kind"], text=payload["text"],
                                      provenance="user_confirmed")
            elif p["kind"] == "reminder":
                result = store.insert(db, "reminders", text=payload["text"], due_on=payload["due_on"])
            elif p["kind"] == "idea":
                result = store.insert(db, "ideas", text=payload["text"])
        store.update(db, "proposals", proposal_id, state="accepted" if accept else "rejected", decided_at=now())
    db.log("proposal_decided", f"id={proposal_id} kind={p['kind']} accepted={accept}")
    return {"proposal": store.get(db, "proposals", proposal_id), "created": result}


# ---- drafting -------------------------------------------------------------------------

def _evidence_map(db: Database) -> dict[int, dict]:
    return {e["id"]: e for e in store.rows(db, "evidence")}


def _note_draft_saved(db: Database, action_id: int | None) -> None:
    """Autosave is allowed to move suggested -> drafted. It never goes further."""
    if not action_id:
        return
    action = store.get(db, "actions", action_id)
    if action and action["state"] == "suggested":
        store.set_action_state(db, action_id, "drafted")


def generate_draft(db: Database, gateway: Gateway, *, action_id: int | None, purpose: str, audience: str,
                   evidence_ids: list[int], instruction: str, shareable_note: str,
                   include_item_context: bool) -> dict:
    action = store.get(db, "actions", action_id) if action_id else None
    ctx = context.draft_context(db, purpose, audience, evidence_ids, instruction, shareable_note,
                                action["item_id"] if action else None, include_item_context)
    session = active_session(db)
    out = gateway.call("draft", ctx.system, ctx.user, DraftOut, session_id=session["id"] if session else None,
                       meta=ctx.meta)
    assert isinstance(out, DraftOut)
    claims = [c.model_dump() for c in out.claims]
    # Validate against the whole library, so a reference to an entry that was held back is caught as such.
    report = validate_draft(out.body, claims, _evidence_map(db), purpose)
    draft = store.insert(db, "drafts", action_id=action_id, purpose=purpose, audience=audience, body=out.body,
                         claims=claims, gaps=[g[:300] for g in out.gaps[:10]], report=report, source="ai")
    snapshot_draft(db, draft)
    _note_draft_saved(db, action_id)
    return {"draft": draft, "excluded_evidence": ctx.excluded}


def suggest_passage(db: Database, gateway: Gateway, *, selection: str, operation: str, **fields) -> dict:
    action = store.get(db, "actions", fields.get("action_id")) if fields.get("action_id") else None
    ctx = context.draft_context(db, fields["purpose"], fields["audience"], fields["evidence_ids"],
                                fields["instruction"], fields["shareable_note"],
                                action["item_id"] if action else None, fields["include_item_context"])
    instruction = {"shorten": "Shorten the passage without changing its meaning.",
                   "clarify": "Clarify the passage while preserving the user's voice and factual meaning.",
                   "check": "Keep the passage unchanged and tag its claims for evidence checking."}[operation]
    user = ctx.user + "\n## Passage task\n" + instruction + "\n" + context.wrap_untrusted("selected_passage", selection)
    meta = {**ctx.meta, "selection": selection, "operation": operation}
    session = active_session(db)
    out = gateway.call("draft", ctx.system, user, DraftOut, session_id=session["id"] if session else None, meta=meta)
    claims = [c.model_dump() for c in out.claims]
    return {"body": out.body, "claims": claims, "gaps": out.gaps,
            "report": validate_draft(out.body, claims, {e["id"]: e for e in ctx.evidence}, fields["purpose"]),
            "excluded_evidence": ctx.excluded}


def snapshot_draft(db: Database, draft: dict) -> None:
    fields = {k: draft[k] for k in ("body", "purpose", "audience", "claims", "gaps", "source")}
    latest = store.rows(db, "draft_versions", "draft_id=?", (draft["id"],), "id DESC LIMIT 1")
    if not latest or any(latest[0][k] != value for k, value in fields.items()):
        store.insert(db, "draft_versions", draft_id=draft["id"], **fields)


def save_draft(db: Database, draft_id: int | None, *, action_id: int | None, purpose: str, audience: str,
               body: str, claims: list[dict] | None = None) -> dict:
    """Atomically retain the old and new text; unchanged autosaves do not create versions."""
    with db.tx():
        existing = store.get(db, "drafts", draft_id) if draft_id else None
        if existing:
            snapshot_draft(db, existing)
        claims = claims if claims is not None else (existing["claims"] if existing else [])
        report = validate_draft(body, claims, _evidence_map(db), purpose)
        if existing:
            draft = store.update(db, "drafts", existing["id"], body=body, report=report, audience=audience, purpose=purpose, claims=claims)
        else:
            draft = store.insert(db, "drafts", action_id=action_id, purpose=purpose, audience=audience, body=body,
                                 claims=claims, gaps=[], report=report, source="user")
        snapshot_draft(db, draft)
        _note_draft_saved(db, (existing or {}).get("action_id") or action_id)
    return draft


def restore_draft(db: Database, draft_id: int, version_id: int) -> dict:
    with db.tx():
        current = store.get(db, "drafts", draft_id)
        version = store.get(db, "draft_versions", version_id)
        if not current or not version or version["draft_id"] != draft_id:
            raise store.RuleError("That version does not belong to this draft.")
        snapshot_draft(db, current)
        fields = {k: version[k] for k in ("body", "purpose", "audience", "claims", "gaps", "source")}
        fields["report"] = validate_draft(version["body"], version["claims"], _evidence_map(db), version["purpose"])
        restored = store.update(db, "drafts", draft_id, **fields)
        snapshot_draft(db, restored)
        db.log("draft_restored", f"id={draft_id} version={version_id}")
    return restored


def run_compare(db: Database, gateway: Gateway, import_id: int) -> dict:
    import_row = store.get(db, "imports", import_id)
    if not import_row:
        raise store.RuleError("No such pasted material.")
    ctx = context.compare_context(db, import_row)
    session = active_session(db)
    out = gateway.call("compare", ctx.system, ctx.user, CompareOut,
                       session_id=session["id"] if session else None, meta=ctx.meta)
    assert isinstance(out, CompareOut)
    known = {e["id"]: e for e in ctx.evidence}
    rows = []
    for r in out.requirements[:8]:
        valid = [i for i in r.evidence_ids if i in known]  # drop ids the model made up
        rows.append({
            "requirement": r.requirement[:300],
            "evidence": [{"id": i, "title": known[i]["title"], "status": known[i]["status"]} for i in valid],
            "invented_ids": [i for i in r.evidence_ids if i not in known],
            "gap": r.gap[:300] if r.gap else ("" if valid else "No supporting evidence."),
        })
    return {"summary": out.summary[:600], "requirements": rows}


# ---- less typing: postings attached to roles, résumé to evidence, one-click confirmation ----

def attach_posting(db: Database, item: dict, content: str) -> dict:
    """Store a job posting as pasted (untrusted) material linked to its role. One posting per role."""
    db.run("DELETE FROM imports WHERE item_id=? AND kind='job_description'", (item["id"],))
    label = (item["title"] + (" · " + item["org"] if item["org"] else "") + " posting")[:200]
    row = store.insert(db, "imports", kind="job_description", label=label, content=content, item_id=item["id"])
    db.log("posting_attached", f"item_id={item['id']} chars={len(content)}")
    return {"id": row["id"], "length": len(content)}


def posting_for(db: Database, item_id: int) -> dict | None:
    row = db.one("SELECT id, LENGTH(content) AS length FROM imports WHERE item_id=? AND kind='job_description' "
                 "ORDER BY id DESC LIMIT 1", (item_id,))
    return row


def extract_evidence(db: Database, gateway: Gateway, text: str) -> dict:
    """Ask the model to turn a résumé into evidence candidates. Nothing is saved here: the caller shows the
    candidates and the user approves them. Numbers the résumé does not contain are removed or flagged in code."""
    system, user, meta = context.extract_context(text)
    session = active_session(db)
    out = gateway.call("extract", system, user, ExtractOut, session_id=session["id"] if session else None, meta=meta)
    assert isinstance(out, ExtractOut)
    source_values = {q["value"] for q in quantities(text)}
    existing = {r["title"].strip().lower() for r in db.q("SELECT title FROM evidence")}
    candidates = []
    for entry in out.entries[:20]:
        title, claim = entry.title.strip()[:200], entry.claim.strip()[:2000]
        if not title or not claim:
            continue
        metrics = [{"value": m.value.strip()[:40], "unit": m.unit.strip()[:40], "label": m.label.strip()[:200]}
                   for m in entry.metrics[:20]
                   if m.value.strip() and all(q["value"] in source_values for q in quantities(m.value))]
        invented = sorted({q["text"] for q in quantities(claim) if q["value"] not in source_values})
        candidates.append({"title": title, "claim": claim, "metrics": metrics,
                           "number_warnings": invented, "already_have": title.lower() in existing})
    db.log("evidence_extracted", f"candidates={len(candidates)} chars={len(text)}")
    return {"candidates": candidates, "truncated": len(text) > context.MAX_RESUME_CHARS}


def add_evidence_bulk(db: Database, entries: list[dict], source_ref: str, confirmed: bool,
                      permitted_uses: list[str]) -> dict:
    """Save entries the user approved on screen. `confirmed` records that the user stands behind them,
    with the résumé (or whatever they named) as the source."""
    status = "user_verified_with_artifact" if confirmed else "unverified_user_claim"
    store.check_evidence({"status": status, "source_ref": source_ref})
    added = skipped = 0
    with db.tx():
        for e in entries:
            if db.one("SELECT 1 FROM evidence WHERE LOWER(title)=LOWER(?)", (e["title"],)):
                skipped += 1
                continue
            store.insert(db, "evidence", title=e["title"], claim=e["claim"], metrics=e.get("metrics", []),
                         source_ref=source_ref, status=status, permitted_uses=permitted_uses, do_not_claim="",
                         confidential=bool(e.get("confidential")), provenance="resume_import")
            added += 1
    db.log("evidence_bulk_added", f"added={added} skipped={skipped} confirmed={confirmed}")
    return {"added": added, "skipped": skipped}


def confirm_all_evidence(db: Database, source_ref: str) -> dict:
    """One click for "I stand behind all of these". Entries that already name a source keep it."""
    rows = db.q("SELECT id, source_ref FROM evidence WHERE status='unverified_user_claim' AND is_sample=0")
    with db.tx():
        for r in rows:
            store.update(db, "evidence", r["id"], status="user_verified_with_artifact",
                         source_ref=r["source_ref"].strip() or source_ref)
    db.log("evidence_confirmed_all", f"count={len(rows)}")
    return {"confirmed": len(rows)}


# ---- setup progress: milestones, not field counts ------------------------------------

SETUP_STEPS = [
    ("goal", "Say what you're working toward", "Better picks for the next thing to do"),
    ("project", "Add a project", "Drafts have something to cite"),
    ("verified", "Verify a claim", "Drafts can state it as fact"),
    ("profile", "Paste your profile text", "Link sees where you're starting"),
    ("person", "Add a person or role", "Follow-ups and ranking"),
]


def setup_progress(db: Database) -> dict:
    """Five milestones in the order that reaches a useful draft fastest. Sample rows never count,
    so loading the samples cannot make an empty account look finished."""
    def has(sql: str) -> bool:
        return db.one(sql) is not None

    done = {
        "goal": has("SELECT 1 FROM memory WHERE kind='goal' AND is_sample=0"),
        "project": has("SELECT 1 FROM evidence WHERE is_sample=0"),
        "verified": has("SELECT 1 FROM evidence WHERE is_sample=0 AND status='user_verified_with_artifact'"),
        "profile": has("SELECT 1 FROM imports WHERE kind='profile_text'"),
        "person": has("SELECT 1 FROM items WHERE is_sample=0"),
    }
    steps = [{"id": sid, "title": title, "unlocks": unlocks, "done": done[sid]} for sid, title, unlocks in SETUP_STEPS]
    count = sum(1 for st in steps if st["done"])
    return {"steps": steps, "done": count, "total": len(steps),
            "percent": round(100 * count / len(steps)), "complete": count == len(steps)}


# ---- starter file: bulk-add the user's own information ---------------------------------

def import_starter(db: Database, data: dict) -> dict:
    """Add entries from a file the user chose and previewed. Nothing here is trusted as verified:
    evidence always arrives as an unverified claim, and every entry is marked as imported so it
    can be reviewed, edited, or deleted. Re-importing the same file adds nothing twice."""
    added = {"memory": 0, "evidence": 0, "items": 0, "actions": 0}
    skipped = 0
    with db.tx():
        for m in data.get("memory", []):
            if db.one("SELECT 1 FROM memory WHERE kind=? AND text=?", (m["kind"], m["text"])):
                skipped += 1
                continue
            store.insert(db, "memory", provenance="imported_file", **m)
            added["memory"] += 1
        for e in data.get("evidence", []):
            if db.one("SELECT 1 FROM evidence WHERE title=?", (e["title"],)):
                skipped += 1
                continue
            store.insert(db, "evidence", provenance="imported_file", **{**e, "status": "unverified_user_claim"})
            added["evidence"] += 1
        for it in data.get("items", []):
            if db.one("SELECT 1 FROM items WHERE kind=? AND title=?", (it["kind"], it["title"])):
                skipped += 1
                continue
            store.insert(db, "items", **it)
            added["items"] += 1
        for a in data.get("actions", []):
            fields = dict(a)
            item_title = fields.pop("item_title", "")
            if db.one("SELECT 1 FROM actions WHERE title=?", (fields["title"],)):
                skipped += 1
                continue
            item = db.one("SELECT id FROM items WHERE title=?", (item_title,)) if item_title else None
            store.insert(db, "actions", item_id=item["id"] if item else None, where_left_off="Not started.", **fields)
            added["actions"] += 1
    db.log("starter_imported", " ".join(f"{k}={v}" for k, v in added.items()) + f" skipped={skipped}")
    return {"added": added, "skipped": skipped}


# ---- export ---------------------------------------------------------------------------

def export_all(db: Database) -> dict:
    from .db import USER_TABLES

    return {"exported_at": now(), "note": "Everything Career Companion stores, including private notes.",
            "tables": {t: store.rows(db, t, order="rowid ASC") for t in USER_TABLES}}
