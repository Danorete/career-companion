"""The four-stage journey on the starting page (decision D55). Real records only; synthetic data throughout."""

from __future__ import annotations


def stages(client) -> dict:
    return {st["id"]: st["done"] for st in client.get("/api/journey").json()["stages"]}


def test_a_new_account_starts_at_the_first_stage(client):
    j = client.get("/api/journey").json()
    assert [st["id"] for st in j["stages"]] == ["start", "groundwork", "people", "outreach"]
    assert (j["done"], j["total"], j["percent"], j["current"], j["complete"]) == (0, 4, 0, "start", False)
    assert all(st["title"] and st["detail"] for st in j["stages"])


def test_bootstrap_carries_the_journey(client):
    assert client.get("/api/bootstrap").json()["journey"] == client.get("/api/journey").json()


def test_getting_oriented_finishes_the_first_stage_and_the_welcome(client):
    j = client.post("/api/journey/oriented", json={}).json()
    assert (j["done"], j["percent"], j["current"]) == (1, 25, "groundwork")
    assert client.get("/api/bootstrap").json()["onboarding"]["done"] is True


def test_skip_and_oriented_are_the_same_flag(client):
    client.post("/api/onboarding/skip", json={})
    assert stages(client)["start"] is True


def test_sample_data_never_counts(app, client):
    assert client.post("/api/sample/load", json={}).status_code == 200
    assert app.state.db.one("SELECT COUNT(*) AS n FROM items WHERE is_sample=1")["n"] == 2  # the samples really are there
    assert stages(client) == {"start": False, "groundwork": False, "people": False, "outreach": False}


def test_any_one_piece_of_groundwork_is_enough(client):
    client.post("/api/memory", json={"kind": "goal", "text": "Find a summer data internship"})
    assert stages(client)["groundwork"] is True


def test_evidence_a_saved_job_or_pasted_text_each_count_as_groundwork(app, client):
    for body in ({"title": "Club dashboard", "claim": "Built a dashboard for the data club."},):
        assert client.post("/api/evidence", json=body).status_code == 200
    assert stages(client)["groundwork"] is True
    app.state.db.run("DELETE FROM evidence")
    client.post("/api/items", json={"kind": "opportunity", "title": "Data Analyst Intern", "org": "Example Co"})
    assert stages(client)["groundwork"] is True
    app.state.db.run("DELETE FROM items")
    assert stages(client)["groundwork"] is False
    client.post("/api/imports", json={"kind": "job_description", "label": "Posting", "content": "Python and SQL."})
    assert stages(client)["groundwork"] is True


def test_a_person_or_a_note_finishes_people_and_notes(app, client):
    out = client.post("/api/guide/connection", json={"name": "Priya Raman"}).json()
    assert stages(client)["people"] is True
    client.delete(f"/api/items/{out['person']['id']}")
    assert stages(client)["people"] is False  # the bar reflects what is there now
    client.post("/api/logs", json={"note": "Met someone from the analytics team at the fair."})
    assert stages(client)["people"] is True


def test_reaching_out_needs_a_kept_plan_not_just_a_suggestion(client):
    plan = client.post("/api/connections/plans", json={"mode": "reconnect", "recollection": "Priya, she runs the data club"}).json()
    assert stages(client)["outreach"] is False  # a suggestion alone is not progress
    client.post(f"/api/connections/plans/{plan['id']}/confirm", json={"name": "Priya", "next_action": "Ask about the club"})
    j = client.get("/api/journey").json()
    assert {st["id"]: st["done"] for st in j["stages"]}["outreach"] is True


def test_a_drafted_message_counts_as_reaching_out(client):
    client.post("/api/drafts/generate", json={"purpose": "outreach", "audience": "peer", "evidence_ids": [],
                                             "instruction": "Ask about the data club", "shareable_note": "", "include_item_context": False})
    assert stages(client)["outreach"] is True


def test_stages_can_finish_out_of_order(client):
    client.post("/api/guide/connection", json={"name": "Sam"})
    j = client.get("/api/journey").json()
    assert {st["id"]: st["done"] for st in j["stages"]} == {"start": False, "groundwork": False, "people": True, "outreach": False}
    assert (j["done"], j["percent"], j["current"]) == (1, 25, "start")  # the current stage is the first one still open
