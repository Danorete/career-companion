from companion import store


def test_selected_record_is_explicit_and_planning_only(client, app):
    item = store.insert(app.state.db, 'items', kind='relationship', title='Person', private_notes='SELECTED_PRIVATE_CANARY')
    client.post('/api/chat', json={'message':'Help me prepare.'})
    assert 'SELECTED_PRIVATE_CANARY' not in app.state.gateway.client.requests[-1].user
    client.post('/api/chat', json={'message':'Help me prepare.', 'context_item_id':item['id']})
    assert 'SELECTED_PRIVATE_CANARY' in app.state.gateway.client.requests[-1].user
    client.post('/api/drafts/suggest', json={'purpose':'outreach','selection':'Hi there.','operation':'clarify'})
    assert 'SELECTED_PRIVATE_CANARY' not in app.state.gateway.client.requests[-1].user
