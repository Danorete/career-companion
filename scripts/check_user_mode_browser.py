"""User version versus developer version (decision D42).

Checks that the user version uses plain words and hides spending and AI-mode controls, and that the
developer version keeps them. Synthetic temporary data and mock AI only. Requires Playwright and Linux Chromium.
"""
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import uvicorn
from playwright.sync_api import sync_playwright
from companion.ai import MockAI
from companion.app import create_app
from companion.config import Settings
from companion.people import load_demo
from companion.services import local_today

PORTS = {'user': 8891, 'dev': 8892}


def check(mode, page, app, port, finished):
    page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')
    if not finished:
        page.get_by_role('button', name=('I just met someone' if mode == 'user' else 'Make sense of an encounter'), exact=True).wait_for()
        heading = 'Remember the people you meet. Follow up without the awkwardness.' if mode == 'user' else 'Good people. Real possibilities.'
        page.get_by_role('heading', name=heading, exact=True).wait_for()
        return
    page.locator('#side').wait_for()
    side = page.locator('#side').inner_text()
    if mode == 'user':
        for word in ('Add a note', 'Add contacts', 'More tools', 'About the AI'):
            assert word in side, (word, side)
        for word in ('Quick log', 'Career tools', 'AI budget', 'Mock AI', '$'):
            assert word not in side, (word, side)
    else:
        for word in ('Quick log', 'Import', 'Career tools', 'Mock AI', 'AI budget'):
            assert word in side, (word, side)
    page.goto(f'http://127.0.0.1:{port}/#settings')
    page.get_by_text('Appearance').first.wait_for()
    text = page.locator('#main').inner_text().lower()
    assert ('about the ai' in text) == (mode == 'user'), mode
    assert ('spending this month' in text) == (mode == 'dev'), mode


for mode, port in PORTS.items():
    for finished in (False, True):
        with tempfile.TemporaryDirectory(prefix='link-mode-') as folder:
            settings = Settings(data_dir=Path(folder), port=port, ai_mode='mock', ui_mode=mode)
            app = create_app(settings, MockAI())
            db = app.state.db
            load_demo(db, local_today(settings))
            db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
            if finished:
                db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
            server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port, access_log=False, log_level='error'))
            thread = threading.Thread(target=server.run, daemon=True)
            thread.start()
            for _ in range(50):
                if server.started:
                    break
                time.sleep(.1)
            errors = []
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                    page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    check(mode, page, app, port, finished)
                    browser.close()
            finally:
                server.should_exit = True
                thread.join(10)
            assert not errors, errors
print('User and developer versions behave as designed; no JS errors. No live AI calls.')
