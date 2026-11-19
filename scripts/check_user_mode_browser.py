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
        if mode == 'user':  # How Link works is the first screen (D55)
            page.get_by_role('heading', name='Welcome to Link.', exact=True).wait_for()
            page.get_by_role('button', name='Show me how it works').first.wait_for()
        else:  # the developer version keeps the original welcome: one column, one question (D53)
            page.get_by_role('button', name='Make sense of an encounter', exact=True).wait_for()
            page.get_by_role('heading', name='Where shall we begin?', exact=True).wait_for()
        return
    page.locator('#side').wait_for()
    side = page.locator('#side').inner_text()
    if mode == 'user':
        # Two places to look, then two menus. Nothing about spending or the AI provider is on the bar itself.
        assert [w for w in side.split() if w] == ['Link', 'Today', 'People', 'Add', 'Menu'], side
        assert page.locator('.workspace-toolbar').is_hidden() and page.locator('.guide-launcher').is_hidden()
        page.locator('#add-menu > summary').click()
        add = page.locator('#add-menu').inner_text()
        for word in ('Add a note', 'Add contacts', 'Connect your calendar'):
            assert word in add, (word, add)
        page.keyboard.press('Escape')
        assert page.locator('.menu[open]').count() == 0
        page.locator('#more-menu > summary').click()
        menu = page.locator('#more-menu').inner_text()
        for word in ('About me', 'Jobs I’m looking at', 'Settings', 'How Link works', 'Take the tour', 'Quit Link', 'answers are samples', 'stays on this computer'):
            assert word in menu, (word, menu)
        for word in ('Quick log', 'Career tools', 'AI budget', 'Mock AI', '$'):
            assert word not in menu + side, (word, menu)
        page.locator('h1').first.click()  # a click elsewhere closes it
        assert page.locator('.menu[open]').count() == 0
    else:
        for word in ('Quick log', 'Import', 'Career tools', 'Mock AI', 'AI budget'):
            assert word in side, (word, side)
    page.goto(f'http://127.0.0.1:{port}/#settings')
    page.get_by_text('Appearance').first.wait_for()
    text = page.locator('#main').inner_text().lower()
    assert ('about the ai' in text) == (mode == 'user'), mode
    assert ('spending this month' in text) == (mode == 'dev'), mode


def first_time_screen():
    from companion.connectors import SampleCalendar
    port = 8893
    with tempfile.TemporaryDirectory(prefix='link-first-') as folder:
        settings = Settings(data_dir=Path(folder), port=port, ai_mode='mock', ui_mode='user')
        app = create_app(settings, MockAI(), calendar=SampleCalendar())
        app.state.db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
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
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')
                page.get_by_role('heading', name='Start with one person.').wait_for()
                steps = page.locator('.start-steps li')
                assert steps.count() == 3 and page.locator('.start-steps li[aria-current="step"]').count() == 1
                assert 'Connect your calendar' in steps.nth(0).inner_text()
                assert page.get_by_role('button', name='Connect your calendar').count() == 1  # one primary action
                assert page.locator('.guide-launcher').is_hidden() and page.locator('.workspace-toolbar').is_hidden()
                page.get_by_role('button', name='Connect your calendar').click()
                page.get_by_role('heading', name='Connect your calendar').wait_for()
                page.locator('#more-menu > summary').click()
                page.get_by_role('button', name='Quit Link').click()
                page.get_by_role('heading', name='Link has stopped.').wait_for()
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)
        assert not errors, errors


first_time_screen()
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
