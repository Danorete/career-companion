from companion import store
from companion.db import Database


def test_versions_survive_reopen_restore_and_deduplicate(client, app):
    payload = dict(purpose='outreach', audience='', body='Original')
    draft = client.post('/api/drafts/save', json=payload).json()
    payload['draft_id'] = draft['id']
    client.post('/api/drafts/save', json=payload)
    payload['body'] = 'Edited'
    client.post('/api/drafts/save', json=payload)
    versions = client.get(f"/api/drafts/{draft['id']}/versions").json()
    assert len(versions) == 2
    copy = Database(app.state.settings.db_path)
    assert copy.one('SELECT COUNT(*) AS n FROM draft_versions')['n'] == 2
    copy.close()
    result = client.post(f"/api/drafts/{draft['id']}/versions/{versions[-1]['id']}/restore", json={}).json()
    assert result['body'] == 'Original'
    assert len(client.get(f"/api/drafts/{draft['id']}/versions").json()) == 3
    client.delete(f"/api/drafts/{draft['id']}")
    assert app.state.db.one('SELECT COUNT(*) AS n FROM draft_versions')['n'] == 0


def test_restore_revalidates_against_current_evidence_and_rejects_other_draft(client, app):
    from companion.services import snapshot_draft
    ev = store.insert(app.state.db, 'evidence', title='Example', claim='Built a project.', status='user_verified_with_artifact', source_ref='artifact', permitted_uses=['outreach'], provenance='user')
    draft = store.insert(app.state.db, 'drafts', purpose='outreach', audience='', body='Built a project.', claims=[{'text':'Built a project.', 'evidence_id':ev['id']}], gaps=[], report={}, source='user')
    snapshot_draft(app.state.db, draft)
    version = client.get(f"/api/drafts/{draft['id']}/versions").json()[0]
    store.delete(app.state.db, 'evidence', ev['id'])
    restored = client.post(f"/api/drafts/{draft['id']}/versions/{version['id']}/restore", json={}).json()
    assert restored['report']['overall'] == 'blocked'
    other = client.post('/api/drafts/save', json={'purpose':'outreach','body':'Other'}).json()
    assert client.post(f"/api/drafts/{other['id']}/versions/{version['id']}/restore", json={}).status_code == 422


def test_schema_one_draft_survives_upgrade_and_first_edit(tmp_path):
    import sqlite3
    from companion.services import save_draft
    path = tmp_path / 'legacy.sqlite3'
    conn = sqlite3.connect(path)
    conn.executescript('''
        PRAGMA user_version=1;
        CREATE TABLE drafts (
          id INTEGER PRIMARY KEY, action_id INTEGER, purpose TEXT NOT NULL,
          audience TEXT NOT NULL DEFAULT '', body TEXT NOT NULL,
          claims TEXT NOT NULL DEFAULT '[]', gaps TEXT NOT NULL DEFAULT '[]',
          report TEXT NOT NULL DEFAULT '{}', source TEXT NOT NULL,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        INSERT INTO drafts(id,purpose,body,source,created_at,updated_at)
          VALUES(42,'outreach','Legacy writing to preserve','user','2026-11-10','2026-11-10');
    ''')
    conn.close()
    db = Database(path)
    assert store.get(db, 'drafts', 42)['body'] == 'Legacy writing to preserve'
    save_draft(db, 42, action_id=None, purpose='outreach', audience='', body='Edited after upgrade')
    versions = store.rows(db, 'draft_versions', 'draft_id=?', (42,), 'id ASC')
    assert [v['body'] for v in versions] == ['Legacy writing to preserve', 'Edited after upgrade']
    from companion.db import SCHEMA_VERSION
    assert db.one('PRAGMA user_version')['user_version'] == SCHEMA_VERSION
    db.close()
