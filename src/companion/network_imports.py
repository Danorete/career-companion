"""User-selected networking snapshots. Parsing never browses, calls AI, or commits records."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from urllib.parse import urlsplit, urlunsplit

from . import people, store
from .db import now

MAX_ROWS = 1000


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _csv(text: str, required: set[str]) -> list[dict]:
    lines = text.lstrip('\ufeff').splitlines(keepends=True)
    header = None
    for i, line in enumerate(lines[:30]):
        try:
            fields = {x.strip().casefold() for x in next(csv.reader([line]))}
        except (csv.Error, StopIteration):
            continue
        if required <= fields:
            header = i
            break
    if header is None:
        raise store.RuleError('Expected the original English LinkedIn CSV headers. Choose Connections.csv or messages.csv, not a ZIP archive.')
    try:
        reader = csv.DictReader(io.StringIO(''.join(lines[header:])), strict=True)
        rows = []
        for row in reader:
            if len(rows) >= MAX_ROWS:
                raise store.RuleError('Choose a file with at most 1,000 rows. Split larger exports into smaller CSV files, keeping the header.')
            if None in row or any(v is None for v in row.values()):
                raise store.RuleError('A CSV row has missing or extra columns. Use an unedited LinkedIn export.')
            normalized = {k.strip().casefold(): v.strip() for k, v in row.items()}
            if any(len(v) > 12000 for v in normalized.values()):
                raise store.RuleError('An individual CSV field is too long (maximum 12,000 characters).')
            if any(normalized.values()):
                rows.append(normalized)
        return rows
    except csv.Error as exc:
        raise store.RuleError('The CSV could not be read. Check quoted fields and export it again.') from exc


def profile_url(raw: str) -> str:
    if not raw:
        return ''
    if len(raw) > 1000:
        raise store.RuleError('A profile URL is too long.')
    parts = urlsplit(raw)
    if parts.scheme not in ('http', 'https') or parts.hostname not in ('linkedin.com', 'www.linkedin.com') or parts.username or parts.password or parts.port:
        raise store.RuleError('Profile links must be linkedin.com/in/ links. Links are saved only, never fetched.')
    if not parts.path.startswith('/in/') or not parts.path[4:].strip('/'):
        raise store.RuleError('A profile link is not a LinkedIn /in/ profile URL.')
    return urlunsplit(('https', 'www.linkedin.com', parts.path.rstrip('/'), '', ''))


def _seen(db, kind: str, token: str):
    return db.one('SELECT value FROM kv WHERE key=?', (f'network_import:{kind}:{token}',))


def _remember(db, kind: str, token: str, value: dict):
    db.run('INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
           (f'network_import:{kind}:{token}', json.dumps(value)))


def connections_preview(db, text: str) -> dict:
    rows = _csv(text, {'first name', 'last name', 'company', 'position', 'connected on'})
    existing = people.list_people(db)
    parsed = []
    for i, row in enumerate(rows):
        name = ' '.join(x for x in (row['first name'], row['last name']) if x)
        if not name or len(name) > 200 or len(row['company']) > 200 or len(row['position']) > 200 or len(row['connected on']) > 80:
            raise store.RuleError(f'Connection row {i+1} has a missing name or an oversized field.')
        try:
            url = profile_url(row.get('url', ''))
        except (ValueError, store.RuleError):
            raise store.RuleError(f'Connection row {i+1} has an invalid profile link.')
        item = {'row': i, 'name': name, 'org': row['company'], 'position': row['position'],
                'connected_on': row['connected on'], 'profile_link': url}
        token = fingerprint({k: v for k, v in item.items() if k != 'row'})
        matches = [dict(id=p['id'], name=p['name'], org=p['org'], reason='Same profile link' if url and p['profile_link'] and profile_url_safe(p['profile_link']) == url else 'Similar name; identity needs your review')
                   for p in existing if (url and profile_url_safe(p['profile_link']) == url) or p['name'].casefold() == name.casefold()]
        parsed.append({**item, 'token': token, 'matches': matches, 'already_imported': bool(_seen(db, 'connection', token))})
    return {'rows': parsed, 'count': len(parsed), 'notice': 'Snapshot only. Email addresses are discarded. A connection date is not a conversation date or a measure of closeness.'}


def profile_url_safe(raw: str) -> str:
    try:
        return profile_url(raw)
    except (ValueError, store.RuleError):
        return ''


def confirm_connections(db, text: str, decisions: list[dict]) -> dict:
    preview = connections_preview(db, text)['rows']
    indexed = {r['row']: r for r in preview}
    if len({d['row'] for d in decisions}) != len(decisions):
        raise store.RuleError('Review each connection row only once.')
    result = {'added': 0, 'updated': 0, 'skipped': 0, 'person_ids': []}
    with db.tx():
        for decision in decisions:
            row = indexed.get(decision['row'])
            if not row:
                raise store.RuleError('A selected row is not present in this file.')
            if decision['choice'] == 'skip' or _seen(db, 'connection', row['token']):
                result['skipped'] += 1
                continue
            if decision['choice'] == 'fill_missing':
                if not decision.get('target_id'):
                    raise store.RuleError('Choose an existing person to update.')
                person = people.person_detail(db, decision['target_id'])
                fields = {k: person[k] for k in ('name', 'org', 'profile_link', 'context', 'notes', 'category')}
                fields['org'] = fields['org'] or row['org']
                fields['profile_link'] = fields['profile_link'] or row['profile_link']
                saved = people.save_person(db, person['id'], fields)
                result['updated'] += 1
            else:
                saved = people.save_person(db, None, {'name': row['name'], 'org': row['org'], 'profile_link': row['profile_link'], 'context': '', 'notes': '', 'category': ''})
                result['added'] += 1
            # Source metadata is kept separately; never pretend a connection request was a conversation.
            meta = {'source': 'LinkedIn connection export', 'position': row['position'], 'connected_on': row['connected_on'], 'imported_at': now(), 'snapshot': True}
            db.run('INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                   (f'network_source:{saved["id"]}', json.dumps(meta)))
            _remember(db, 'connection', row['token'], {'person_id': saved['id']})
            result['person_ids'].append(saved['id'])
    db.log('connections_imported', f"added={result['added']} updated={result['updated']} skipped={result['skipped']}")
    return result


def person_source(db, person_id: int) -> dict:
    people.get_person(db, person_id)
    row = db.one('SELECT value FROM kv WHERE key=?', (f'network_source:{person_id}',))
    return json.loads(row['value']) if row else {}


def messages_preview(text: str, kind: str) -> dict:
    if kind == 'text':
        if not text.strip():
            raise store.RuleError('Paste or choose one conversation first.')
        if len(text) > 12000:
            raise store.RuleError('Choose a conversation excerpt of at most 12,000 characters.')
        return {'rows': [{'row': 0, 'sender': 'Conversation excerpt', 'recipients': '', 'date': '', 'content': text}]}
    rows = _csv(text, {'from', 'to', 'date', 'content'})
    return {'rows': [{'row': i, 'sender': r['from'][:200], 'recipients': r['to'][:500], 'date': r['date'][:100], 'content': r['content']} for i, r in enumerate(rows)]}


def confirm_messages(db, text: str, kind: str, selected: list[int], person_id: int | None, note: str, retain: bool, today) -> dict:
    rows = messages_preview(text, kind)['rows']
    ids = set(selected)
    if not ids or len(ids) != len(selected) or not ids <= {r['row'] for r in rows}:
        raise store.RuleError('Choose valid messages to include, without duplicate selections.')
    if not note.strip():
        raise store.RuleError('Write a short recap, keeping uncertain details uncertain.')
    chosen = [r for r in rows if r['row'] in ids]
    exchange = '\n\n'.join(f"{r['date']} {r['sender']} → {r['recipients']}\n{r['content']}".strip() for r in chosen)
    if len(exchange) > 12000:
        raise store.RuleError('Select fewer messages (maximum 12,000 characters in one excerpt).')
    if person_id is not None:
        people.get_person(db, person_id)
    token = fingerprint({'person_id': person_id, 'exchange': exchange})
    with db.tx():
        old = _seen(db, 'messages', token)
        if old:
            return {'already_imported': True, **json.loads(old['value'])}
        entry = people.create_log(db, note=note, item_id=person_id, when={'kind': 'unknown'}, exchange=exchange, keep_exchange=retain, today=today)
        _remember(db, 'messages', token, {'log_id': entry['id']})
    return {'already_imported': False, 'log_id': entry['id']}


def _unescape(value: str) -> str:
    return re.sub(r'\\([nN,;\\])', lambda m: '\n' if m[1].lower() == 'n' else m[1], value)


def calendar_preview(text: str) -> dict:
    """Selected ICS snapshots, no URL fetches, attendee ingestion, alarms, or recurrence expansion."""
    if 'BEGIN:VCALENDAR' not in text:
        raise store.RuleError('Choose an .ics calendar export, not a subscription link.')
    unfolded = re.sub(r'\r?\n[ \t]', '', text)
    events = []; event = None; nested = 0
    for line in unfolded.splitlines():
        line = line.strip()
        if line == 'BEGIN:VEVENT':
            event = {}; nested = 0
        elif line == 'END:VEVENT' and event is not None:
            if len(events) >= 100:
                raise store.RuleError('Choose an export with at most 100 events.')
            events.append({'row': len(events), 'title': event.get('SUMMARY', 'Untitled event')[:300],
                           'when': event.get('DTSTART', 'Time not supplied')[:120], 'timezone': event.get('timezone', ''),
                           'location': event.get('LOCATION', '')[:300], 'description': event.get('DESCRIPTION', '')[:1500],
                           'recurring': 'RRULE' in event, 'status': event.get('STATUS', '')})
            event = None
        elif event is not None:
            if line.startswith('BEGIN:'):
                nested += 1
            elif line.startswith('END:'):
                nested = max(0, nested-1)
            elif not nested and ':' in line:
                key, value = line.split(':', 1); name = key.split(';')[0]
                if name in {'SUMMARY', 'DTSTART', 'LOCATION', 'DESCRIPTION', 'RRULE', 'STATUS'}:
                    event[name] = _unescape(value)
                    if name == 'DTSTART':
                        zone = re.search(r'(?:^|;)TZID=([^;]+)', key)
                        event['timezone'] = zone[1] if zone else ('UTC' if value.endswith('Z') else 'As recorded in export; timezone not supplied')
    if event is not None:
        raise store.RuleError('The calendar export contains an incomplete event.')
    return {'events': events, 'notice': 'Snapshot only. Recurring events are not expanded; canceled events stay labeled. Invitations do not establish attendance. No events, attendees, or conversations have been saved.'}


def forget_import_reference(db, *, person_id: int | None = None, log_id: int | None = None) -> None:
    if person_id is not None:
        db.run('DELETE FROM kv WHERE key=?', (f'network_source:{person_id}',))
    for row in db.q("SELECT key,value FROM kv WHERE key LIKE 'network_import:%'"):
        value = json.loads(row['value'])
        if (person_id is not None and value.get('person_id') == person_id) or (log_id is not None and value.get('log_id') == log_id):
            db.run('DELETE FROM kv WHERE key=?', (row['key'],))
