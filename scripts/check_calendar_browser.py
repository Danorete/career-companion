"""Calendar connection in the demo (decision D39): connect the sample calendar, find people, keep, dismiss, disconnect.

Synthetic temporary data and the built-in sample calendar only. No Google account and no network.
Requires Playwright and Linux Chromium.
"""
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import uvicorn
from playwright.sync_api import expect, sync_playwright
from companion.ai import MockAI
from companion.app import create_app
from companion.config import Settings
from companion.people import load_demo
from companion.services import local_today

PORT = 8893


def open_add_contacts(page):
    page.locator('#add-menu > summary').click()
    page.get_by_role('link', name='Add contacts', exact=True).click()


errors = []
with tempfile.TemporaryDirectory(prefix='link-calendar-') as folder:
    settings = Settings(data_dir=Path(folder), port=PORT, ai_mode='mock')
    app = create_app(settings, MockAI())
    db = app.state.db
    load_demo(db, local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=PORT, access_log=False, log_level='error'))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(.1)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{PORT}/#t={app.state.security.launch_token}')
            open_add_contacts(page)
            page.locator('#source-tab-calendar').click()
            page.get_by_role('heading', name='Connect your calendar').wait_for()
            page.get_by_role('button', name='Try with a sample calendar').wait_for()
            for promise in ('event titles', 'never reads', 'never: '):
                assert promise in page.locator('.connect-card').inner_text().lower(), promise
            page.get_by_role('button', name='Try with a sample calendar').click()
            page.get_by_role('button', name='Check my calendar').wait_for()
            assert 'No accounts connected' not in page.locator('#source-connection-state').inner_text()
            assert 'connected' in page.locator('#source-connection-state').inner_text().lower()
            page.get_by_role('button', name='Check my calendar').click()
            page.get_by_text('Found 3 new people').wait_for()
            assert page.locator('.connect-card article').count() == 3
            assert db.q('SELECT COUNT(*) AS n FROM interactions WHERE source != "demo"') is not None
            before = len(db.q("SELECT id FROM items WHERE kind='relationship'"))
            maya = page.locator('.connect-card article', has_text='Maya Lindqvist')
            maya.get_by_role('button', name='Keep', exact=True).click()
            page.get_by_text('Saved Maya Lindqvist.').wait_for()
            assert len(db.q("SELECT id FROM items WHERE kind='relationship'")) == before + 1
            assert page.locator('.connect-card article').count() == 2
            # The meeting with Maya ended days ago, so Today asks how it went (decision D44). Priya's is still ahead.
            page.get_by_role('link', name='Today', exact=True).first.click()
            page.get_by_role('heading', name='How did it go with Maya Lindqvist?').wait_for()
            assert page.locator('.checkin-card h2').count() == 1
            page.get_by_text('Add a line or a promise').click()
            page.get_by_label('Something you promised (optional)').fill('send her the article')
            page.get_by_role('button', name='Great', exact=True).click()
            page.get_by_text('Saved a note and a reminder for Maya Lindqvist.').wait_for()
            expect(page.locator('.checkin-card')).to_have_count(0)
            [log] = db.q("SELECT * FROM interactions WHERE source='calendar_checkin'")
            assert 'Went well.' in log['note'] and 'send her the article' in log['note']
            assert db.one('SELECT COUNT(*) AS n FROM actions WHERE title=?', ('send her the article',))['n'] == 1
            open_add_contacts(page)
            page.locator('#source-tab-calendar').click()
            page.get_by_role('button', name='Check my calendar').wait_for()
            page.locator('.connect-card article', has_text='Priya').get_by_role('button', name='Never suggest this person', exact=True).click()
            expect(page.locator('.connect-card article')).to_have_count(1)
            page.get_by_role('button', name='Disconnect…').click()
            page.get_by_role('button', name='Disconnect and remove what came from my calendar').click()
            page.get_by_text('Disconnected.').wait_for()
            assert page.locator('#source-connection-state').inner_text() == 'No accounts connected'
            assert db.one('SELECT COUNT(*) AS n FROM encounter_candidates')['n'] == 0
            assert len(db.q("SELECT id FROM items WHERE kind='relationship'")) == before + 1  # kept people stay
            browser.close()
    finally:
        server.should_exit = True
        thread.join(10)
assert not errors, errors
print('Calendar connection checks passed: sample sign-in, people found, keep, never-suggest, disconnect; no JS errors.')
