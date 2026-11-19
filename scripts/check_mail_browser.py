"""Email connection in the demo (decision D48): connect the sample mailbox, keep, never-suggest, disconnect.

Synthetic temporary data and the built-in sample mailbox only. No Google account and no network.
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

PORT = 8894
errors = []
with tempfile.TemporaryDirectory(prefix='link-mail-') as folder:
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
            page.locator('#add-menu > summary').click()
            page.get_by_role('link', name='Add contacts', exact=True).click()
            page.locator('#source-tab-calendar').click()
            page.get_by_role('heading', name='Connect your email').wait_for()
            page.get_by_role('button', name='Try with a sample mailbox').wait_for()
            text = page.locator('.connect-card[aria-label="Email connection"]').inner_text()
            assert 'never reads' in text.lower() and 'what a message says' in text.lower(), text
            page.get_by_role('button', name='Try with a sample mailbox').click()
            page.get_by_role('button', name='Check my email').click()
            card = page.locator('.connect-card[aria-label="Email connection"] article')
            expect(card).to_have_count(2)
            assert 'sam.ortega' not in page.locator('#main').inner_text() and 'digest@' not in page.locator('#main').inner_text()
            before = len(db.q("SELECT id FROM items WHERE kind='relationship'"))
            card.filter(has_text='maya.lindqvist').get_by_role('button', name='Keep', exact=True).click()
            expect(card).to_have_count(1)
            assert len(db.q("SELECT id FROM items WHERE kind='relationship'")) in (before, before + 1)
            card.first.get_by_role('button', name='Never suggest this person', exact=True).click()
            expect(card).to_have_count(0)
            page.get_by_role('button', name='Disconnect…').last.click()
            page.get_by_role('button', name='Disconnect and remove what came from my email').click()
            page.get_by_text('Disconnected.').last.wait_for()
            assert db.one('SELECT COUNT(*) AS n FROM email_contacts')['n'] == 0
            browser.close()
    finally:
        server.should_exit = True
        thread.join(10)
assert not errors, errors
print('Email connection checks passed: sample mailbox, people found, keep, never-suggest, disconnect; no JS errors.')
