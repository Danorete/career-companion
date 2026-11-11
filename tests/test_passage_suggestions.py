from companion import store


def test_suggestion_never_overwrites_or_uses_private_context(client, app):
    private = 'PRIVATE_CANARY_DO_NOT_SEND'
    store.insert(app.state.db, 'memory', kind='goal', text=private, provenance='user')
    store.insert(app.state.db, 'evidence', title='Secret', claim=private, confidential=True, provenance='user', permitted_uses=['outreach'])
    result = client.post('/api/drafts/suggest', json={'purpose':'outreach','selection':'A sentence. Another sentence.','operation':'shorten'}).json()
    assert result['body'] == 'A sentence.'
    assert store.rows(app.state.db, 'drafts') == []
    request = app.state.gateway.client.requests[-1]
    assert private not in request.user and private not in request.system


def test_manual_claim_linking_is_validated(client, app):
    result = client.post('/api/drafts/save', json={'purpose':'outreach','body':'A claim.', 'claims':[{'text':'A claim.','evidence_id':99999}]}).json()
    assert result['report']['overall'] == 'blocked'
