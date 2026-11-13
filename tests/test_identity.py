"""Current companion identity must be explicit even with legacy context."""
from companion import store
from companion.context import PLANNING_SYSTEM


def test_current_name_is_explicit_in_system_prompt():
    assert 'Your name is Link' in PLANNING_SYSTEM
    assert 'obsolete companion name' in PLANNING_SYSTEM


def test_mock_identity_and_old_history_do_not_change_current_name(client,app,mock_ai):
    client.post('/api/chat',json={'message':'The companion used to be named Tempo.'})
    response=client.post('/api/chat',json={'message':"What's your name?"})
    assert response.status_code == 200
    assert 'I’m Link' in response.json()['reply']
    assert 'Your name is Link' in mock_ai.requests[-1].system
    assert 'obsolete companion name' in mock_ai.requests[-1].system
    # Keep historical user content intact, rather than rewriting or deleting it.
    assert any('Tempo' in row['content'] for row in store.rows(app.state.db,'messages'))
