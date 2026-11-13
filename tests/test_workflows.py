"""End-to-end behaviour through the HTTP API, with the mock AI. Synthetic data only."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from companion.ai import MockAI
from companion.app import create_app
from companion.budget import Usage
from companion.security import COOKIE_NAME, CSRF_HEADER
from tests.conftest import BASE


def signed_in(app):
    sid, csrf = app.state.security.new_session_for_tests()
    c = TestClient(app, base_url=BASE, headers={CSRF_HEADER: csrf, "origin": BASE})
    c.cookies.set(COOKIE_NAME, sid)
    return c


def make_action(client, **kw):
    return client.post("/api/actions", json={"title": "Synthetic follow-up", "kind": "follow_up", **kw}).json()


def evidence(client, **kw):
    body = {"title": "Synthetic project", "claim": "Built a report with 3 charts.", "permitted_uses": ["outreach"],
            "metrics": [{"value": "3", "unit": "charts"}], **kw}
    return client.post("/api/evidence", json=body)


# ---- onboarding and preferences -------------------------------------------------------

def test_short_onboarding_stores_answers_without_ai(settings):
    settings.ai_mode = "off"
    client = signed_in(create_app(settings))
    state = client.get("/api/bootstrap").json()["onboarding"]
    assert state["step"] == 0 and state["total"] == 2 and not state["done"]
    for answer in ("Meet peers", "Be direct and concise"):
        state = client.post("/api/onboarding/answer", json={"text": answer}).json()
    assert state["done"]
    kinds = [m["kind"] for m in client.get("/api/memory").json()]
    assert sorted(kinds) == ["goal", "preference"]


def test_preferences_can_be_corrected_in_conversation_and_edited_directly(client):
    r = client.post("/api/chat", json={"message": "From now on I prefer mornings"}).json()
    created = client.post(f"/api/proposals/{r['proposals'][0]['id']}/accept", json={}).json()["created"]
    assert created["kind"] == "preference"
    edited = client.put(f"/api/memory/{created['id']}", json={"kind": "preference", "text": "Evenings, actually"}).json()
    assert edited["text"] == "Evenings, actually"
    assert client.delete(f"/api/memory/{created['id']}").json()["deleted"]
    assert client.get("/api/memory").json() == []


# ---- completion states ----------------------------------------------------------------

def test_copying_or_saving_a_draft_never_marks_it_sent(client):
    ev = evidence(client).json()
    action = make_action(client)
    draft = client.post("/api/drafts/generate", json={"action_id": action["id"], "purpose": "outreach",
                                                      "evidence_ids": [ev["id"]]}).json()["draft"]
    state = lambda: [a for a in client.get("/api/actions").json() if a["id"] == action["id"]][0]["state"]
    assert state() == "drafted"                      # autosave may do this much
    assert client.post(f"/api/drafts/{draft['id']}/copied", json={}).status_code == 200
    client.post("/api/drafts/save", json={"draft_id": draft["id"], "purpose": "outreach", "body": "edited"})
    assert state() == "drafted"                      # copy and edit change nothing
    client.post(f"/api/actions/{action['id']}/state", json={"state": "reviewed"})
    assert state() == "reviewed"
    done = client.post(f"/api/actions/{action['id']}/state", json={"state": "done"}).json()
    assert done["state"] == "done" and done["completed_at"]
    assert client.post(f"/api/actions/{action['id']}/state", json={"state": "reviewed"}).json()["completed_at"] is None


def test_invalid_state_jump_is_refused(client):
    action = make_action(client)
    client.post(f"/api/actions/{action['id']}/state", json={"state": "dropped"})
    assert client.post(f"/api/actions/{action['id']}/state", json={"state": "done"}).status_code == 422


def test_draft_report_separates_supported_claims_from_gaps(client):
    ev = evidence(client).json()
    d = client.post("/api/drafts/generate", json={"purpose": "outreach", "evidence_ids": [ev["id"]]}).json()["draft"]
    assert d["claims"][0]["evidence_id"] == ev["id"]
    assert d["report"]["overall"] == "review"        # evidence is an unverified user claim
    empty = client.post("/api/drafts/generate", json={"purpose": "outreach", "evidence_ids": []}).json()["draft"]
    assert empty["claims"] == [] and empty["gaps"]


def test_manual_edit_is_rechecked(client):
    ev = evidence(client).json()
    d = client.post("/api/drafts/generate", json={"purpose": "outreach", "evidence_ids": [ev["id"]]}).json()["draft"]
    saved = client.post("/api/drafts/save", json={"draft_id": d["id"], "purpose": "outreach",
                                                  "body": d["body"] + " It reached 900 users."}).json()
    assert "untracked_number" in [i["code"] for i in saved["report"]["body_issues"]]


def test_verified_evidence_requires_a_source(client):
    assert evidence(client, status="user_verified_with_artifact").status_code == 422
    assert evidence(client, status="user_verified_with_artifact", source_ref="repo link").status_code == 200


# ---- today view: one recommendation, alternatives, resume note ------------------------

def test_today_opens_on_one_recommendation_with_alternatives(client):
    soon = (date.today() + timedelta(days=1)).isoformat()
    make_action(client, title="Idea A")
    promised = make_action(client, title="Promised follow-up", commitment=True, deadline=soon, effort_min=10)
    make_action(client, title="Idea B")
    make_action(client, title="Idea C")
    view = client.get("/api/today?minutes=15").json()
    assert view["recommended"]["action"]["id"] == promised["id"]
    assert len(view["alternatives"]) == 2
    assert "Promised follow-up" in view["greeting"] and view["recommended"]["reasons"]


def test_resume_note_survives_and_is_shown(client):
    a = make_action(client, commitment=True)
    client.post(f"/api/actions/{a['id']}/note", json={"where_left_off": "Wrote two lines, need the closing ask."})
    view = client.get("/api/today").json()
    assert "need the closing ask" in view["greeting"]
    assert view["recommended"]["action"]["where_left_off"].startswith("Wrote two lines")


def test_empty_today_does_not_invent_work(client):
    view = client.get("/api/today").json()
    assert view["recommended"] is None and "No need to invent work" in view["greeting"]


# ---- reminders, outcomes, ideas -------------------------------------------------------

def test_reminder_surfaces_when_due_and_can_be_snoozed_or_done(client):
    today = client.get("/api/today").json()["today"]   # the app's own date, in its configured time zone
    r = client.post("/api/reminders", json={"text": "Check in", "due_on": today}).json()
    later = client.post("/api/reminders", json={"text": "Later", "due_on": "2099-01-01"}).json()
    due = [x["id"] for x in client.get("/api/today").json()["reminders"]]
    assert r["id"] in due and later["id"] not in due
    client.post(f"/api/reminders/{r['id']}/snooze", json={"days": 3})
    assert client.get("/api/today").json()["reminders"] == []
    client.post(f"/api/reminders/{later['id']}/done", json={})
    assert [x["id"] for x in client.get("/api/reminders").json()] == [r["id"]]


def test_quick_outcome_recording_and_undo(client):
    item = client.post("/api/items", json={"kind": "relationship", "title": "Synthetic Person"}).json()
    o = client.post("/api/outcomes", json={"item_id": item["id"], "type": "reply"}).json()
    assert o["occurred_on"] and o["type"] == "reply"
    assert client.get("/api/items").json()[0]["outcomes"][0]["id"] == o["id"]
    client.delete(f"/api/outcomes/{o['id']}")
    assert client.get("/api/items").json()[0]["outcomes"] == []
    assert client.post("/api/outcomes", json={"item_id": item["id"], "type": "hired!!"}).status_code == 422


def test_idea_is_not_an_obligation_until_promoted(client):
    idea = client.post("/api/ideas", json={"text": "Learn about dbt"}).json()
    assert client.get("/api/actions").json() == []
    assert client.get("/api/today").json()["recommended"] is None
    assert client.get("/api/today").json()["parked_ideas"] == 1
    client.post(f"/api/ideas/{idea['id']}/promote", json={})
    assert client.get("/api/actions").json()[0]["title"] == "Learn about dbt"


# ---- availability without AI ----------------------------------------------------------

def test_everything_manual_works_with_ai_off(settings):
    settings.ai_mode = "off"
    client = signed_in(create_app(settings))
    assert client.get("/api/bootstrap").json()["ai"]["available"] is False
    ev = evidence(client).json()
    action = make_action(client)
    chat = client.post("/api/chat", json={"message": "hello"}).json()
    assert chat["reply"] is None and chat["unavailable"]
    assert client.post("/api/drafts/generate", json={"purpose": "outreach", "evidence_ids": [ev["id"]]}).status_code == 503
    saved = client.post("/api/drafts/save", json={"action_id": action["id"], "purpose": "outreach",
                                                  "body": "Written by hand."})
    assert saved.status_code == 200 and saved.json()["source"] == "user"
    assert client.get("/api/today").json()["recommended"]["action"]["state"] == "drafted"
    assert client.get("/api/export").status_code == 200


def test_exhausted_budget_blocks_ai_but_not_saved_work(settings):
    settings.hard_stop_usd = 0.01
    mock = MockAI(model="claude-sonnet-5-5", usage=Usage(input_tokens=2000, output_tokens=500))
    client = signed_in(create_app(settings, ai_client=mock))
    ev = evidence(client).json()
    r = client.post("/api/drafts/generate", json={"purpose": "outreach", "evidence_ids": [ev["id"]]})
    assert r.status_code == 503 and r.json()["kind"] == "budget"
    assert mock.requests == []
    assert client.get("/api/evidence").json()[0]["id"] == ev["id"]
    assert client.post("/api/drafts/save", json={"purpose": "outreach", "body": "by hand"}).status_code == 200


def test_model_failure_keeps_the_users_message_and_work(settings):
    mock = MockAI(model="claude-sonnet-5-5", script=[RuntimeError("down")])
    client = signed_in(create_app(settings, ai_client=mock))
    r = client.post("/api/chat", json={"message": "are you there?"}).json()
    assert r["reply"] is None and "saved" in r["unavailable"]
    assert client.get("/api/budget").json()["status"]["unknown_calls"] == 1


# ---- persistence, export, deletion, sample data ---------------------------------------

def test_data_and_session_progress_survive_restart(settings):
    first = signed_in(create_app(settings))
    a = make_action(first, commitment=True)
    first.post("/api/session/start", json={"minutes": 30, "action_id": a["id"]})
    first.post(f"/api/actions/{a['id']}/note", json={"where_left_off": "Halfway through."})
    first.post("/api/drafts/save", json={"action_id": a["id"], "purpose": "follow_up", "body": "Draft text"})
    first.app.state.db.close()

    second = signed_in(create_app(settings))
    view = second.get("/api/today").json()
    assert view["recommended"]["action"]["id"] == a["id"]
    assert "You were on this last time." in view["recommended"]["reasons"]
    assert second.get(f"/api/drafts?action_id={a['id']}").json()[0]["body"] == "Draft text"


def test_export_contains_everything_and_wipe_removes_it(client, settings):
    evidence(client)
    client.post("/api/memory", json={"kind": "goal", "text": "EXPORT-ME"})
    export = client.get("/api/export")
    assert "attachment" in export.headers["content-disposition"] and "EXPORT-ME" in export.text
    assert client.post("/api/wipe", json={"confirm": "yes"}).status_code == 422
    assert client.post("/api/wipe", json={"confirm": "DELETE EVERYTHING"}).status_code == 200
    assert client.get("/api/memory").json() == [] and client.get("/api/evidence").json() == []
    assert b"EXPORT-ME" not in settings.db_path.read_bytes()


def test_wipe_does_not_reset_the_spending_cap(settings):
    mock = MockAI(model="claude-sonnet-5-5", usage=Usage(input_tokens=2000, output_tokens=500))
    client = signed_in(create_app(settings, ai_client=mock))
    client.post("/api/chat", json={"message": "hello"})
    before = client.get("/api/budget").json()["status"]["committed_usd"]
    assert before > 0
    client.post("/api/wipe", json={"confirm": "DELETE EVERYTHING"})
    assert client.get("/api/budget").json()["status"]["committed_usd"] == before


def test_sample_data_is_labelled_and_removable(client):
    client.post("/api/sample/load", json={})
    client.post("/api/sample/load", json={})  # idempotent
    titles = [e["title"] for e in client.get("/api/evidence").json()] + \
             [a["title"] for a in client.get("/api/actions").json()] + \
             [i["title"] for i in client.get("/api/items").json()]
    assert len(titles) == 6 and all(t.startswith("[SAMPLE]") for t in titles)
    assert client.get("/api/bootstrap").json()["has_sample"]
    client.post("/api/sample/remove", json={})
    assert client.get("/api/evidence").json() == [] and client.get("/api/actions").json() == []
    assert not client.get("/api/bootstrap").json()["has_sample"]


def test_old_transcripts_are_purged_on_start(settings):
    app = create_app(settings)
    db = app.state.db
    db.run("INSERT INTO sessions(id,started_at) VALUES(1,'2020-01-01T00:00:00+00:00')")
    db.run("INSERT INTO messages(session_id,role,content,created_at) VALUES(1,'user','old','2020-01-01T00:00:00+00:00')")
    db.run("INSERT INTO messages(session_id,role,content,created_at) VALUES(1,'user','new',datetime('now'))")
    db.close()
    assert [m["content"] for m in create_app(settings).state.db.q("SELECT content FROM messages")] == ["new"]


def test_database_file_is_private_to_the_user(client, settings):
    assert oct(settings.db_path.stat().st_mode)[-3:] == "600"


def test_session_timer_info_and_end(client):
    a = make_action(client, commitment=True)
    assert client.get("/api/today").json()["session"] is None
    client.post("/api/chat", json={"message": "hello"})          # a chat alone starts no timer
    assert client.get("/api/today").json()["session"] is None
    client.post("/api/session/start", json={"minutes": 30, "action_id": a["id"]})
    session = client.get("/api/today").json()["session"]
    assert session["minutes"] == 30 and session["focus_action_id"] == a["id"] and session["started_at"]
    client.post("/api/session/end", json={})
    assert client.get("/api/today").json()["session"] is None


def test_onboarding_questions_are_short_with_a_hint(client):
    state = client.get("/api/bootstrap").json()["onboarding"]
    assert len(state["question"]) < 70 and state["hint"]


# ---- starter file -----------------------------------------------------------------------

STARTER = {
    "career_companion_starter": 1,
    "memory": [{"kind": "goal", "text": "Synthetic goal from a file"},
               {"kind": "voice_note", "text": "Plain and direct.", "audience": "recruiter"}],
    "evidence": [{"title": "Synthetic imported project", "claim": "Analysed 9 files.", "permitted_uses": ["profile"],
                  "metrics": [{"value": "9", "unit": "files", "label": "inputs"}],
                  "status": "user_verified_with_artifact", "source_ref": "claims to be verified"}],
    "items": [{"kind": "opportunity", "title": "Synthetic role", "org": "Example Org"}],
    "actions": [{"title": "Synthetic first to-do", "kind": "profile_edit", "item_title": "Synthetic role"}],
}


def test_starter_file_adds_everything_in_one_step(client):
    r = client.post("/api/starter/import", json=STARTER)
    assert r.status_code == 200
    assert r.json()["added"] == {"memory": 2, "evidence": 1, "items": 1, "actions": 1}
    assert client.get("/api/today").json()["recommended"]["action"]["title"] == "Synthetic first to-do"
    assert client.get("/api/today").json()["recommended"]["item"]["title"] == "Synthetic role"


def test_starter_file_cannot_mark_evidence_verified(client):
    client.post("/api/starter/import", json=STARTER)
    ev = client.get("/api/evidence").json()[0]
    assert ev["status"] == "unverified_user_claim" and ev["provenance"] == "imported_file"
    assert {m["provenance"] for m in client.get("/api/memory").json()} == {"imported_file"}


def test_starter_file_is_safe_to_import_twice(client):
    client.post("/api/starter/import", json=STARTER)
    again = client.post("/api/starter/import", json=STARTER).json()
    assert again["added"] == {"memory": 0, "evidence": 0, "items": 0, "actions": 0} and again["skipped"] == 5
    assert len(client.get("/api/evidence").json()) == 1


def test_starter_file_is_validated(client):
    assert client.post("/api/starter/import", json={**STARTER, "career_companion_starter": 2}).status_code == 422
    assert client.post("/api/starter/import", json={**STARTER, "ledger": [{"cost_usd": -99}]}).status_code == 422
    bad = {**STARTER, "memory": [{"kind": "goal", "text": "x", "provenance": "user_typed"}]}
    assert client.post("/api/starter/import", json=bad).status_code == 422
    assert client.get("/api/memory").json() == []


def test_imported_private_memory_still_stays_out_of_drafting(client, mock_ai):
    client.post("/api/starter/import", json={**STARTER, "memory": [{"kind": "constraint", "text": "CANARY-IMPORTED-PRIVATE"}]})
    ev = client.get("/api/evidence").json()[0]
    client.post("/api/drafts/generate", json={"purpose": "profile", "evidence_ids": [ev["id"]]})
    draft_request = [r for r in mock_ai.requests if r.call_type == "draft"][-1]
    assert "CANARY-IMPORTED-PRIVATE" not in draft_request.system + draft_request.user
    assert "Analysed 9 files." in draft_request.user


# ---- setup progress ---------------------------------------------------------------------

def setup(client):
    return client.get("/api/bootstrap").json()["setup"]


def done_ids(client):
    return [s["id"] for s in setup(client)["steps"] if s["done"]]


def test_setup_starts_at_zero_with_five_steps(client):
    s = setup(client)
    assert (s["percent"], s["done"], s["total"], s["complete"]) == (0, 0, 5, False)
    assert [st["id"] for st in s["steps"]] == ["goal", "project", "verified", "profile", "person"]
    assert all(st["title"] and st["unlocks"] for st in s["steps"])


def test_setup_ignores_sample_data(client):
    client.post("/api/sample/load", json={})
    assert client.get("/api/evidence").json() and client.get("/api/items").json()
    assert setup(client)["percent"] == 0


def test_each_setup_step_flips_on_its_own(client):
    client.post("/api/items", json={"kind": "relationship", "title": "Synthetic Person"})
    assert done_ids(client) == ["person"]
    client.post("/api/imports", json={"kind": "resume", "label": "x", "content": "not profile text"})
    assert done_ids(client) == ["person"]                      # only profile text counts for that step
    client.post("/api/imports", json={"kind": "profile_text", "label": "x", "content": "About me"})
    assert done_ids(client) == ["profile", "person"]
    client.post("/api/memory", json={"kind": "preference", "text": "not a goal"})
    assert "goal" not in done_ids(client)
    client.post("/api/memory", json={"kind": "goal", "text": "Synthetic goal"})
    ev = evidence(client).json()
    assert done_ids(client) == ["goal", "project", "profile", "person"] and setup(client)["percent"] == 80
    body = {"title": ev["title"], "claim": ev["claim"], "permitted_uses": ["outreach"],
            "status": "user_verified_with_artifact", "source_ref": "synthetic link"}
    client.put(f"/api/evidence/{ev['id']}", json=body)
    s = setup(client)
    assert (s["percent"], s["done"], s["complete"]) == (100, 5, True)


def test_setup_drops_when_something_is_deleted(client):
    ev = evidence(client).json()
    assert setup(client)["percent"] == 20
    client.delete(f"/api/evidence/{ev['id']}")
    assert setup(client)["percent"] == 0


def test_starter_file_counts_toward_setup_but_never_as_verified(client):
    client.post("/api/starter/import", json=STARTER)
    assert done_ids(client) == ["goal", "project", "person"]   # imported evidence is never pre-verified


# ---- less typing: postings on roles, résumé to evidence, one-click confirmation ---------

RESUME = """Synthetic Person

Data Intern, Example Org
- Built 3 dashboards used by 12 analysts.

Capstone project
- Cleaned 40,000 rows of survey data in Python.
"""


def test_role_and_posting_are_added_in_one_step(client):
    item = client.post("/api/items", json={"kind": "opportunity", "title": "Analyst", "org": "Example Org",
                                           "posting": "Requirements: SQL, Tableau, " + "x" * 5000}).json()
    assert item["posting"]["length"] > 5000                      # nothing is cut off at 2,000 characters
    listed = client.get("/api/items").json()[0]
    assert listed["posting"]["id"] == item["posting"]["id"]
    stored = client.get("/api/imports").json()[0]
    assert stored["kind"] == "job_description" and stored["item_id"] == item["id"]
    assert client.post("/api/compare", json={"import_id": item["posting"]["id"]}).status_code == 200


def test_posting_can_be_added_or_replaced_on_an_existing_role(client):
    item = client.post("/api/items", json={"kind": "opportunity", "title": "Analyst"}).json()
    assert item["posting"] is None
    first = client.post(f"/api/items/{item['id']}/posting", json={"content": "First version"}).json()
    second = client.post(f"/api/items/{item['id']}/posting", json={"content": "Second version, longer"}).json()
    stored = client.get("/api/imports").json()
    assert len(stored) == 1 and stored[0]["content"] == "Second version, longer"   # replaced, not duplicated
    assert first["length"] == len("First version") and second["length"] == len("Second version, longer")
    client.delete(f"/api/items/{item['id']}")
    assert client.get("/api/imports").json()[0]["item_id"] is None   # the text is kept, just unlinked


def test_resume_extraction_saves_nothing_until_approved(client):
    r = client.post("/api/evidence/extract", json={"text": RESUME})
    assert r.status_code == 200 and len(r.json()["candidates"]) >= 2
    assert client.get("/api/evidence").json() == []


def test_extraction_flags_and_strips_numbers_the_resume_does_not_contain(client, mock_ai):
    from companion.ai import EvidenceCandidate, ExtractOut, MetricOut
    mock_ai.script.append(ExtractOut(entries=[
        EvidenceCandidate(title="Data Intern", claim="Built 3 dashboards used by 500 analysts.",
                          metrics=[MetricOut(value="3", unit="dashboards", label="built"),
                                   MetricOut(value="500", unit="analysts", label="users")])]))
    c = client.post("/api/evidence/extract", json={"text": RESUME}).json()["candidates"][0]
    assert [m["value"] for m in c["metrics"]] == ["3"]             # the invented metric is dropped
    assert c["number_warnings"] == ["500"]                         # and the claim is flagged


def test_approved_entries_can_be_added_as_confirmed_in_bulk(client):
    entries = [{"title": "Data Intern", "claim": "Built 3 dashboards.", "metrics": [{"value": "3", "unit": "dashboards"}]},
               {"title": "Capstone", "claim": "Cleaned 40,000 rows."}]
    body = {"entries": entries, "source_ref": "Master résumé, Nov 2026", "confirmed": True,
            "permitted_uses": ["profile", "resume", "outreach"]}
    assert client.post("/api/evidence/bulk", json=body).json() == {"added": 2, "skipped": 0}
    ev = client.get("/api/evidence").json()
    assert {e["status"] for e in ev} == {"user_verified_with_artifact"}
    assert {e["source_ref"] for e in ev} == {"Master résumé, Nov 2026"} and ev[0]["provenance"] == "resume_import"
    assert client.post("/api/evidence/bulk", json=body).json() == {"added": 0, "skipped": 2}
    assert "verified" in done_ids(client)                          # the setup step is satisfied
    assert client.post("/api/evidence/bulk", json={**body, "source_ref": ""}).status_code == 422


def test_one_click_confirms_only_the_users_unverified_entries(client):
    evidence(client)                                               # unverified, no source
    evidence(client, title="Has a source", source_ref="repo link")
    evidence(client, title="Never", status="do_not_claim")
    client.post("/api/sample/load", json={})
    assert client.post("/api/evidence/confirm-all", json={"source_ref": "Confirmed by me"}).json() == {"confirmed": 2}
    by_title = {e["title"]: e for e in client.get("/api/evidence").json()}
    assert by_title["Synthetic project"]["status"] == "user_verified_with_artifact"
    assert by_title["Synthetic project"]["source_ref"] == "Confirmed by me"
    assert by_title["Has a source"]["source_ref"] == "repo link"   # an existing source is kept
    assert by_title["Never"]["status"] == "do_not_claim"
    assert by_title["[SAMPLE] Example dashboard project"]["status"] == "unverified_user_claim"


def test_extraction_request_carries_only_the_resume(client, mock_ai):
    client.post("/api/memory", json={"kind": "goal", "text": "CANARY-GOAL-PRIVATE"})
    client.post("/api/items", json={"kind": "relationship", "title": "P", "private_notes": "CANARY-NOTE-PRIVATE"})
    client.post("/api/evidence/extract", json={"text": RESUME})
    req = [r for r in mock_ai.requests if r.call_type == "extract"][-1]
    assert "CANARY" not in req.system + req.user and "40,000 rows" in req.user
    assert req.user.count("</untrusted_material>") == 1


def test_older_database_gains_the_posting_link_without_losing_rows(tmp_path):
    import sqlite3
    from companion.db import Database
    path = tmp_path / "old.sqlite3"
    conn = sqlite3.connect(path)
    conn.executescript("""CREATE TABLE imports (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL,
        content TEXT NOT NULL, created_at TEXT NOT NULL);
        INSERT INTO imports(kind,label,content,created_at) VALUES('other','kept','old text','2026-11-10');""")
    conn.close()
    db = Database(path)
    row = db.one("SELECT * FROM imports")
    assert row["label"] == "kept" and row["item_id"] is None
    db.close()
