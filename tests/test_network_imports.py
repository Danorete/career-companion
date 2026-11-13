"""No external services: networking imports are reviewed local snapshots, not live discovery."""
import csv
import io
import json

import pytest
from companion import context, store


def connections(rows=None):
    stream=io.StringIO();stream.write('Notes:\nSome connections do not share email addresses.\n\n')
    writer=csv.writer(stream);writer.writerow(['First Name','Last Name','URL','Email Address','Company','Position','Connected On'])
    writer.writerows(rows or [['Avery','Example','https://www.linkedin.com/in/avery-example/','PRIVATE_EMAIL@example.test','Example Co','Analyst','13 Nov 2026']])
    return stream.getvalue()


def messages(rows=None):
    stream=io.StringIO();writer=csv.writer(stream);writer.writerow(['FROM','TO','DATE','CONTENT'])
    writer.writerows(rows or [['Avery Example','User','2026-11-12 15:30:00 UTC','Maybe I can review the dashboard.'],['Unrelated Person','Other User','2026-11-13','DO_NOT_STORE_THIS']])
    return stream.getvalue()


def post(client,path,body):
    response=client.post('/api/network/'+path,json=body)
    assert response.status_code==200,response.text
    return response.json()


def test_connections_preview_does_not_commit_or_keep_emails(client,app):
    preview=post(client,'connections/preview',{'text':'\ufeff'+connections()})
    row=preview['rows'][0]
    assert row['name']=='Avery Example'
    assert row['profile_link']=='https://www.linkedin.com/in/avery-example'
    assert row['connected_on']=='13 Nov 2026'
    assert 'PRIVATE_EMAIL' not in json.dumps(preview)
    assert client.get('/api/people').json()==[]
    assert client.get('/api/logs').json()==[]
    assert app.state.db.one('SELECT COUNT(*) n FROM ledger')['n']==0
    assert not app.state.db.one("SELECT key FROM kv WHERE key LIKE 'network_%'")


def test_selected_connections_only_and_idempotent(client,app):
    text=connections([['Avery','Example','https://linkedin.com/in/a','private','Co','Analyst','13 Nov 2026'],['Unselected','Person','','private','Co','Manager','12 Nov 2026']])
    body={'text':text,'decisions':[{'row':0,'choice':'add'}]}
    assert post(client,'connections/confirm',body)['added']==1
    assert post(client,'connections/confirm',body)['skipped']==1
    people=client.get('/api/people').json();assert len(people)==1
    assert people[0]['category']=='' and people[0]['entries']==0 and people[0]['next_action'] is None
    source=client.get(f"/api/network/people/{people[0]['id']}/source").json()
    assert source['position']=='Analyst' and source['snapshot']
    assert 'private' not in json.dumps(source)
    assert client.get('/api/actions').json()==[]


def test_matching_requires_choice_and_preserves_existing_context(client):
    p=client.post('/api/people',json={'name':'Avery Example','org':'Current Org','notes':'Private relationship context','context':'Met in class','category':'stay_in_touch'}).json()
    text=connections();preview=post(client,'connections/preview',{'text':text})
    assert preview['rows'][0]['matches'][0]['id']==p['id']
    result=post(client,'connections/confirm',{'text':text,'decisions':[{'row':0,'choice':'fill_missing','target_id':p['id']}]})
    assert result['updated']==1
    p=client.get(f"/api/people/{p['id']}").json()
    assert p['org']=='Current Org' and p['notes']=='Private relationship context'
    assert p['context']=='Met in class' and p['category']=='stay_in_touch'
    assert p['profile_link']=='https://www.linkedin.com/in/avery-example'


def test_imported_snapshot_reaches_private_chat_with_qualifications(client,app):
    result=post(client,'connections/confirm',{'text':connections(),'decisions':[{'row':0,'choice':'add'}]})
    _,prompt,_=context.planning_context(app.state.db,{'id':999},'Help me reconnect.',None,'',result['person_ids'][0])
    assert 'Role at export: Analyst' in prompt
    assert 'not verified current employment or relationship strength' in prompt
    assert '<untrusted_material kind="linkedin_snapshot">' in prompt


def test_connection_commit_is_atomic_and_foreign_origin_blocked(client):
    text=connections()
    response=client.post('/api/network/connections/confirm',json={'text':text,'decisions':[{'row':0,'choice':'add'},{'row':99,'choice':'add'}]})
    assert response.status_code==422
    assert client.get('/api/people').json()==[]
    response=client.post('/api/network/connections/confirm',json={'text':text,'decisions':[{'row':0,'choice':'add'}]},headers={'origin':'https://evil.example'})
    assert response.status_code==403
    assert client.get('/api/people').json()==[]


@pytest.mark.parametrize('text',[
    'wrong,file\nmissing,headers',
    'First Name,Last Name,Company,Position,Connected On\nA,B,Co,Role',
    connections([['A','B','javascript:alert(1)','','Co','Role','today']]),
    connections([['A','B','https://localhost/in/a','','Co','Role','today']]),
    connections([['A','B','https://linkedin.com.evil.test/in/a','','Co','Role','today']]),
    connections([['A','B','https://user:password@linkedin.com/in/a','','Co','Role','today']]),
    connections([['A','B','https://linkedin.com:bad/in/a','','Co','Role','today']]),
])
def test_bad_connections_rejected_without_records(client,text):
    assert client.post('/api/network/connections/preview',json={'text':text}).status_code==422
    assert client.get('/api/people').json()==[]


def test_row_limits_and_duplicate_decisions(client):
    text=connections([['A','B','','','Co','Role','today']]*1001)
    assert client.post('/api/network/connections/preview',json={'text':text}).status_code==422
    assert client.post('/api/network/connections/confirm',json={'text':connections(),'decisions':[{'row':0,'choice':'add'},{'row':0,'choice':'add'}]}).status_code==422


def test_selected_messages_recap_only_by_default(client,app):
    text=messages();preview=post(client,'messages/preview',{'text':text,'kind':'csv'})
    assert len(preview['rows'])==2
    assert client.get('/api/logs').json()==[]
    body={'text':text,'kind':'csv','selected':[0],'note':'Avery may have offered a review.','retain':False}
    result=post(client,'messages/confirm',body)
    entry=client.get('/api/logs').json()[0]
    assert entry['exchange']=='' and entry['when_kind']=='unknown' and entry['item_id'] is None
    assert entry['note']==body['note']
    assert post(client,'messages/confirm',body)['already_imported']
    assert len(client.get('/api/logs').json())==1
    # Raw selected/unselected messages never persist in KV receipts or logs.
    assert 'DO_NOT_STORE_THIS' not in json.dumps(app.state.db.q('SELECT * FROM kv'))
    assert 'Maybe I can review' not in json.dumps(app.state.db.q('SELECT * FROM kv'))
    assert client.get('/api/actions').json()==[]
    assert result['log_id']==entry['id']


def test_message_retention_is_selected_and_explicit(client):
    out=post(client,'messages/confirm',{'text':messages(),'kind':'csv','selected':[0],'note':'A possible offer.','retain':True})
    entry=client.get('/api/logs').json()[0]
    assert 'Maybe I can review' in entry['exchange'] and 'DO_NOT_STORE_THIS' not in entry['exchange']
    assert out['log_id']==entry['id']


@pytest.mark.parametrize('selected,note',[([], 'recap'),([999],'recap'),([0,0],'recap'),([0],'')])
def test_message_selection_and_recap_required(client,selected,note):
    assert client.post('/api/network/messages/confirm',json={'text':messages(),'kind':'csv','selected':selected,'note':note}).status_code==422
    assert client.get('/api/logs').json()==[]


def test_text_conversation_and_nonexistent_person(client):
    text='Avery: Perhaps next week?\nMe: I will check.'
    out=post(client,'messages/preview',{'text':text,'kind':'text'})
    assert out['rows'][0]['content']==text
    assert client.post('/api/network/messages/confirm',json={'text':text,'kind':'text','selected':[0],'person_id':999,'note':'Recap'}).status_code==422
    assert client.post('/api/network/messages/preview',json={'text':'x'*12001,'kind':'text'}).status_code==422


def test_import_receipts_deleted_with_records_and_reimport_possible(client,app):
    text=connections();result=post(client,'connections/confirm',{'text':text,'decisions':[{'row':0,'choice':'add'}]})
    pid=result['person_ids'][0]
    assert client.delete(f'/api/items/{pid}').status_code==200
    assert not app.state.db.one("SELECT key FROM kv WHERE key LIKE 'network_source:%' OR key LIKE 'network_import:connection:%'")
    assert post(client,'connections/confirm',{'text':text,'decisions':[{'row':0,'choice':'add'}]})['added']==1
    body={'text':messages(),'kind':'csv','selected':[0],'note':'Recap'}
    log=post(client,'messages/confirm',body)
    assert client.delete(f"/api/logs/{log['log_id']}").status_code==200
    assert not post(client,'messages/confirm',body)['already_imported']


ICS='''BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Coffee with Avery
DTSTART;TZID=America/New_York:20261116T100000
DESCRIPTION:Discuss dashboards\\nNo attendance implied.
LOCATION:Campus lounge
ATTENDEE:mailto:DO_NOT_IMPORT@example.test
RRULE:FREQ=WEEKLY
BEGIN:VALARM
DESCRIPTION:DO_NOT_USE_ALARM_DESCRIPTION
ATTACH:https://localhost/private
END:VALARM
END:VEVENT
BEGIN:VEVENT
SUMMARY:Canceled event
DTSTART;VALUE=DATE:20261117
STATUS:CANCELLED
END:VEVENT
END:VCALENDAR'''


def test_calendar_preview_has_no_attendance_or_external_effects(client,app):
    result=post(client,'calendar/preview',{'text':ICS})
    event=result['events'][0]
    assert event['timezone']=='America/New_York' and event['recurring']
    assert event['description']=='Discuss dashboards\nNo attendance implied.'
    assert 'DO_NOT_IMPORT' not in json.dumps(result) and 'DO_NOT_USE_ALARM' not in json.dumps(result)
    assert result['events'][1]['status']=='CANCELLED'
    assert client.get('/api/logs').json()==[] and client.get('/api/actions').json()==[]
    assert app.state.db.one('SELECT COUNT(*) n FROM ledger')['n']==0


def test_invalid_calendar_and_event_limit(client):
    assert client.post('/api/network/calendar/preview',json={'text':'https://calendar.example/calendar.ics'}).status_code==422
    assert client.post('/api/network/calendar/preview',json={'text':'BEGIN:VCALENDAR\nBEGIN:VEVENT\nSUMMARY:Incomplete'}).status_code==422
    assert client.post('/api/network/calendar/preview',json={'text':'BEGIN:VCALENDAR\n'+('BEGIN:VEVENT\nSUMMARY:Event\nEND:VEVENT\n'*101)+'END:VCALENDAR'}).status_code==422


def test_import_metadata_exported_and_wiped(client,app):
    post(client,'connections/confirm',{'text':connections(),'decisions':[{'row':0,'choice':'add'}]})
    exported=client.get('/api/export').json()
    assert any(row['key'].startswith('network_source:') for row in exported['tables']['kv'])
    response=client.post('/api/wipe',json={'confirm':'DELETE EVERYTHING'})
    assert response.status_code==200,response.text
    assert not app.state.db.one("SELECT key FROM kv WHERE key LIKE 'network_%'")
