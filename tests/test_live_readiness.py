from companion import store


def test_readiness_does_not_call_provider_and_mock_cannot_smoke(client, app):
    assert client.get('/api/ai/readiness').status_code == 200
    assert app.state.gateway.client.requests == []
    assert client.post('/api/ai/smoke', json={}).status_code == 503
    assert app.state.gateway.client.requests == []


def test_smoke_only_sends_fixed_test_prompt(client, app):
    store.insert(app.state.db, 'memory', kind='goal', text='PRIVATE_TEST_CANARY', provenance='user')
    app.state.gateway.client.name = 'live'
    result = client.post('/api/ai/smoke', json={})
    assert result.status_code == 200
    req = app.state.gateway.client.requests[-1]
    assert 'PRIVATE_TEST_CANARY' not in req.user
    assert store.rows(app.state.db, 'proposals') == []
    assert client.get('/api/ai/readiness').json()['last_test']
