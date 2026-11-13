"""Connection coaching: useful before contacts, explicit commitments, private/public isolation."""
from companion import store
from companion.ai import AIUnavailable
from companion.coaching import ConnectionPlan, manual_plan


def generate(client, **extra):
    response=client.post('/api/connections/plans',json={'mode':'starting','recollection':'Not sure where to begin',**extra})
    assert response.status_code == 200, response.text
    return response.json()


def test_new_user_can_get_value_before_adding_people(client):
    plan=generate(client)
    assert plan['payload']['next_step']
    assert plan['status'] == 'pending'
    assert client.get('/api/people').json() == []
    assert client.get('/api/actions').json() == []
    assert client.get('/api/memory').json() == []


def test_confirm_is_explicit_and_idempotent(client):
    plan=generate(client,mode='met',recollection='Met an analyst, perhaps healthcare; think I offered a link.')
    fields={'name':'Example Name','save_recollection':True,'next_action':'Review whether to send my link','preference':'Direct suggestions'}
    one=client.post(f"/api/connections/plans/{plan['id']}/confirm",json=fields)
    two=client.post(f"/api/connections/plans/{plan['id']}/confirm",json=fields)
    assert one.status_code == 200, one.text
    assert one.json() == two.json()
    assert len(client.get('/api/people').json()) == 1
    assert len(client.get('/api/actions').json()) == 1
    assert len(client.get('/api/logs').json()) == 1
    entry=client.get('/api/logs').json()[0]
    assert entry['when_kind'] == 'unknown'
    assert entry['occurred_on'] is None
    assert client.get('/api/bootstrap').json()['onboarding']['done']


def test_save_plan_does_not_require_person_task_or_memory(client):
    plan=generate(client)
    result=client.post(f"/api/connections/plans/{plan['id']}/confirm",json={})
    assert result.status_code == 200
    assert result.json() == {'item_id':None,'log_id':None,'action_id':None}
    assert client.get('/api/people').json() == []
    assert client.get('/api/actions').json() == []


def test_unavailable_ai_has_manual_fallback_and_keeps_input(client,mock_ai):
    mock_ai.script.append(TimeoutError('provider unavailable'))
    plan=generate(client,recollection='No campus access; working full time.')
    assert plan['source'] == 'manual'
    assert plan['inputs']['recollection'] == 'No campus access; working full time.'
    assert plan['payload']['next_step']
    assert client.post(f"/api/connections/plans/{plan['id']}/confirm",json={}).status_code == 200


def test_model_cannot_invent_name_or_write_records(client,mock_ai):
    proposal=manual_plan('met')
    proposal.suggested_name='Invented Person'
    proposal.opening='A private detail escaped'
    proposal.closing='More private text'
    mock_ai.script.append(proposal)
    plan=generate(client,mode='met',recollection='Met someone but forgot their name.')
    assert plan['payload']['suggested_name'] == ''
    assert plan['payload']['opening'] == ''
    assert plan['payload']['closing'] == ''
    assert client.get('/api/people').json() == []
    assert client.get('/api/actions').json() == []
    assert client.get('/api/memory').json() == []


def test_private_record_and_chat_not_in_coaching_or_practice(client,app,mock_ai):
    p=client.post('/api/people',json={'name':'Maya','notes':'PRIVATE_PERSON_CANARY'}).json()
    store.insert(app.state.db,'memory',kind='constraint',text='PRIVATE_MEMORY_CANARY',provenance='user_typed')
    client.post('/api/chat',json={'message':'PRIVATE_CHAT_CANARY'})
    plan=generate(client,mode='prepare',item_id=p['id'],approved_context='Met at an event',recollection='PRIVATE_RECOLLECTION_CANARY')
    request=mock_ai.requests[-1]
    assert 'PRIVATE_PERSON_CANARY' not in request.user
    assert 'PRIVATE_MEMORY_CANARY' not in request.user
    assert 'PRIVATE_CHAT_CANARY' not in request.user
    response=client.post(f"/api/connections/plans/{plan['id']}/practice",json={'answer':'I would like to learn about your work'})
    assert response.status_code == 200, response.text
    assert 'PRIVATE_RECOLLECTION_CANARY' not in mock_ai.requests[-1].user
    assert 'PRIVATE_PERSON_CANARY' not in mock_ai.requests[-1].user
    client.post('/api/drafts/generate',json={'purpose':'outreach','audience':'peer','evidence_ids':[], 'instruction':'Ask a question','shareable_note':'Met at an event','include_item_context':False})
    assert all(text not in mock_ai.requests[-1].user for text in ['PRIVATE_RECOLLECTION_CANARY','PRIVATE_PERSON_CANARY','PRIVATE_MEMORY_CANARY','PRIVATE_CHAT_CANARY'])


def test_confirm_does_not_overwrite_existing_commitment(client):
    p=client.post('/api/people',json={'name':'Example'}).json()
    client.post(f"/api/people/{p['id']}/next",json={'title':'Original promise'})
    plan=generate(client,mode='follow_up',item_id=p['id'])
    client.post(f"/api/connections/plans/{plan['id']}/confirm",json={'next_action':'New chosen step'})
    assert {a['title'] for a in client.get('/api/actions').json()} == {'Original promise','New chosen step'}


def test_followup_suggestions_need_substance_and_respect_pause(client):
    p=client.post('/api/people',json={'name':'Example'}).json()
    entry=client.post('/api/logs',json={'item_id':p['id'],'note':'Had a conversation','when':{'kind':'date','date':'2020-01-01'}}).json()
    assert client.get('/api/connections/follow-ups').json() == []
    client.put(f"/api/logs/{entry['id']}",json={'commitments':'May have offered a resource'})
    suggestions=client.get('/api/connections/follow-ups').json()
    assert suggestions[0]['possible_commitments'].startswith('May have')
    assert client.get('/api/actions').json() == []
    client.put(f"/api/people/{p['id']}",json={'name':'Example','category':'paused'})
    assert client.get('/api/connections/follow-ups').json() == []


def test_plan_persistence_export_delete_and_invalid_input(client):
    plan=generate(client)
    assert client.get('/api/connections/plans').json()[0]['id'] == plan['id']
    assert client.post('/api/connections/plans',json={'mode':'scrape'}).status_code == 422
    assert client.post('/api/connections/plans',json={'mode':'met','item_id':999999}).status_code == 422
    assert 'connection_plans' in client.get('/api/export').json()['tables']
    assert client.delete(f"/api/connections/plans/{plan['id']}").json()['deleted']
    assert client.post(f"/api/connections/plans/{plan['id']}/confirm",json={}).status_code == 422


def test_existing_person_association_avoids_duplicate(client):
    p=client.post('/api/people',json={'name':'Existing Person'}).json()
    plan=generate(client,mode='reconnect')
    response=client.post(f"/api/connections/plans/{plan['id']}/confirm",json={'existing_person_id':p['id'],'name':'Do not create me'})
    assert response.json()['item_id'] == p['id']
    assert len(client.get('/api/people').json()) == 1


def test_selected_person_cannot_be_replaced_at_confirmation(client):
    a=client.post('/api/people',json={'name':'First'}).json()
    b=client.post('/api/people',json={'name':'Second'}).json()
    plan=generate(client,mode='prepare',item_id=a['id'])
    response=client.post(f"/api/connections/plans/{plan['id']}/confirm",json={'existing_person_id':b['id']})
    assert response.status_code == 422
    assert client.get('/api/connections/plans').json()[0]['status'] == 'pending'


def test_dismiss_followup_does_not_change_relationship_or_create_task(client):
    p=client.post('/api/people',json={'name':'Example'}).json()
    entry=client.post('/api/logs',json={'item_id':p['id'],'note':'Conversation'}).json()
    client.put(f"/api/logs/{entry['id']}",json={'next_steps':'Could share an update'})
    assert client.get('/api/connections/follow-ups').json()
    assert client.post(f"/api/connections/follow-ups/{entry['id']}/dismiss",json={}).status_code == 200
    assert client.get('/api/connections/follow-ups').json() == []
    assert client.get('/api/people').json()[0]['category'] == ''
    assert client.get('/api/actions').json() == []


def test_every_opportunity_request_type_uses_pending_plan(client):
    for ask in ['perspective','feedback','team','introduction','referral']:
        plan=generate(client,mode='opportunity',ask_type=ask)
        assert plan['inputs']['ask_type'] == ask
        assert plan['status'] == 'pending'
    assert client.get('/api/actions').json() == []


def test_preferences_inform_planning_but_never_practice(client,app,mock_ai):
    store.insert(app.state.db,'memory',kind='preference',text='WORK_STYLE_CANARY: be brief',provenance='user_confirmed')
    store.insert(app.state.db,'memory',kind='constraint',text='PRIVATE_FINANCE_CANARY',provenance='user_typed')
    plan=generate(client)
    assert 'WORK_STYLE_CANARY' in mock_ai.requests[-1].user
    assert 'PRIVATE_FINANCE_CANARY' not in mock_ai.requests[-1].user
    response=client.post(f"/api/connections/plans/{plan['id']}/practice",json={'answer':'Hello','previous_question':'What would you like to learn?'})
    assert response.status_code == 200
    assert 'WORK_STYLE_CANARY' not in mock_ai.requests[-1].user
    assert 'PRIVATE_FINANCE_CANARY' not in mock_ai.requests[-1].user
    assert 'What would you like to learn?' in mock_ai.requests[-1].user
