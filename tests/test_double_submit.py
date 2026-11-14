"""A double-click or a retried request must not save the same thing twice. All data is synthetic."""


def test_saving_the_same_quick_log_twice_keeps_one(client):
    body = {"note": "Met a recruiter at the fair.", "item_id": None, "when": {"kind": "unknown"}, "exchange": "", "keep_exchange": False}
    first = client.post("/api/logs", json=body).json()
    second = client.post("/api/logs", json=body).json()
    assert first["id"] == second["id"]
    assert len([e for e in client.get("/api/logs").json() if e["note"] == body["note"]]) == 1


def test_adding_the_same_person_twice_keeps_one(client):
    first = client.post("/api/people", json={"name": "Sample Person", "org": "Example Org"}).json()
    second = client.post("/api/people", json={"name": "Sample Person", "org": "Example Org"}).json()
    assert first["id"] == second["id"]
    assert len([p for p in client.get("/api/people").json() if p["name"] == "Sample Person"]) == 1


def test_adding_the_same_todo_twice_keeps_one(client):
    body = {"title": "Send the thank-you note", "kind": "follow_up"}
    first = client.post("/api/actions", json=body).json()
    second = client.post("/api/actions", json=body).json()
    assert first["id"] == second["id"]


def test_genuinely_different_saves_are_not_merged(client):
    a = client.post("/api/logs", json={"note": "First memory.", "item_id": None, "when": {"kind": "unknown"}, "exchange": "", "keep_exchange": False}).json()
    b = client.post("/api/logs", json={"note": "Second memory.", "item_id": None, "when": {"kind": "unknown"}, "exchange": "", "keep_exchange": False}).json()
    assert a["id"] != b["id"]
    p1 = client.post("/api/people", json={"name": "Sample Person"}).json()
    p2 = client.post("/api/people", json={"name": "Sample Person", "org": "Other Org"}).json()
    assert p1["id"] != p2["id"]
