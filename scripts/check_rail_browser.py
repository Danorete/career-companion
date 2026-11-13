"""Field-notebook redesign acceptance: wayfinding rail, typed headlines, Pause motion, pager, Link panel.

Synthetic temporary data and mock AI only. Requires Playwright and a Chromium build
(set CHROMIUM_PATH if it is not at /usr/bin/chromium).
"""
import argparse
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import uvicorn
from playwright.sync_api import sync_playwright
from companion.app import create_app
from companion.config import Settings
from companion.ai import MockAI
from companion.people import load_demo
from companion.services import local_today

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=Path('/tmp/link-rail-check'))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory(prefix='link-rail-') as folder:
    settings = Settings(data_dir=Path(folder), port=8885, ai_mode='mock')
    app = create_app(settings, MockAI())
    db = app.state.db
    load_demo(db, local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8885, access_log=False, log_level='error'))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(.1)
    errors = []
    url = 'http://127.0.0.1:8885/#t=' + app.state.security.launch_token
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), headless=True, args=['--no-sandbox'])

            # Motion allowed: the headline types, but its accessible name is complete from the start.
            page = browser.new_page(viewport={'width': 1440, 'height': 900})
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(url)
            heading = page.get_by_role('heading', name='One thing today.', exact=True)
            heading.wait_for()
            assert page.locator('#main .typed-visual').count() == 1, 'headline should be typing on first visit'
            page.wait_for_function("() => !document.querySelector('#main .typed-visual')", timeout=4000)
            assert heading.inner_text() == 'One thing today.'

            # Rail: four numbered rooms, career tools, status, Pause motion.
            rail = page.locator('#side')
            for name in ('Today', 'People', 'Quick log', 'Import'):
                assert rail.get_by_role('link', name=name, exact=True).is_visible(), name
            assert rail.get_by_role('link', name='Today', exact=True).get_attribute('aria-current') == 'page'
            for name in ('Roles', 'Evidence', 'Drafts', 'About me', 'Settings & data'):
                assert rail.get_by_role('link', name=name, exact=True).is_visible(), name
            assert 'this mac only' in rail.inner_text().lower()
            box = rail.bounding_box()
            assert box['x'] == 0 and box['width'] <= 260, box

            # Today: meta strip, recent context with honest dates, pager to People.
            assert page.locator('.meta-strip .room-index').inner_text().upper().startswith('01 / 04')
            page.get_by_role('heading', name='Recent context', exact=True).wait_for()
            assert page.locator('.today-recent .when-chip').count() >= 1
            pager = page.get_by_role('navigation', name='Rooms')
            assert pager.get_by_role('link', name='People →').count() == 1
            page.screenshot(path=str(args.output / 'today.png'))

            # A heading types only on the first visit of a session.
            pager.get_by_role('link', name='People →').click()
            page.get_by_role('heading', name='Your people.', exact=True).wait_for()
            assert rail.get_by_role('link', name='People', exact=True).get_attribute('aria-current') == 'page'
            rail.get_by_role('link', name='Today', exact=True).click()
            page.get_by_role('heading', name='One thing today.', exact=True).wait_for()
            assert page.locator('#main .typed-visual').count() == 0

            # Pause motion: pressed state, document flag, survives reload, and headlines appear at once.
            pause = rail.get_by_role('button', name='Pause motion')
            pause.click()
            assert rail.get_by_role('button', name='Pause motion').get_attribute('aria-pressed') == 'true'
            assert page.evaluate("document.documentElement.dataset.motion") == 'paused'
            assert page.evaluate("document.activeElement.classList.contains('pause-motion')")
            page.reload()
            page.get_by_role('heading', name='One thing today.', exact=True).wait_for()
            assert page.locator('#main .typed-visual').count() == 0
            rail.get_by_role('link', name='Quick log', exact=True).click()
            page.get_by_role('heading', name='What do you remember?', exact=True).wait_for()
            assert page.locator('#main .typed-visual').count() == 0
            rail.get_by_role('button', name='Pause motion').click()
            assert page.evaluate("document.documentElement.dataset.motion") == 'auto'

            # The Link avatar opens the companion panel on demand.
            page.get_by_role('button', name='Open Link, your companion').click()
            page.locator('#dock').wait_for(state='visible')
            assert not page.evaluate("document.body.classList.contains('dock-closed')")
            page.wait_for_timeout(600)
            assert page.locator('#dock').bounding_box()['width'] >= 300
            page.screenshot(path=str(args.output / 'quicklog-with-link.png'))

            # Laptop width: no sideways scrolling.
            page.set_viewport_size({'width': 1280, 'height': 800})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')

            # System reduced-motion preference: a room not visited yet still appears at once.
            # (The launch link works once, so this reuses the same signed-in page.)
            page.set_viewport_size({'width': 1440, 'height': 900})
            page.emulate_media(reduced_motion='reduce')
            rail.get_by_role('link', name='Import', exact=True).click()
            page.get_by_role('heading', name='You choose what stays.', exact=True).wait_for()
            assert page.locator('#main .typed-visual').count() == 0
            page.evaluate("localStorage.setItem('cc.theme', JSON.stringify('dark'))")
            page.reload()
            page.get_by_role('heading', name='You choose what stays.', exact=True).wait_for()
            page.screenshot(path=str(args.output / 'import-dark.png'))
            browser.close()
    finally:
        server.should_exit = True
    assert not errors, errors
    print('Rail checks passed: numbered rooms, career tools, local status, typed headline with full accessible name, '
          'first-visit-only typing, Pause motion (persists, keeps focus), reduced motion, pager, recent context, '
          'Link panel on demand, no overflow at 1280; no JS errors.')
