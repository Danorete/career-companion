"""The beginner layout and the floating companion (decision D53), in a real browser.

Checks the one-column Connect screen, the sprite, tips (show, close, auto-hide, turn off and back on), the chat drawer
(opens over the page, focus, the page behind is unreachable, Escape and outside click close it, focus returns), the
one-tap save, and that no technical labels show in the user version. Synthetic data and sample AI only.
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

SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None
TECHNICAL = ('mock replies', 'Clear record context', 'Your saved preparation', 'A LITTLE CLARITY', 'null', 'mock AI')
errors = []


def serve(app, port):
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port, access_log=False, log_level='error'))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(.1)
    return server, thread


def shot(page, name):
    if SHOTS:
        page.wait_for_timeout(500)
        page.screenshot(path=str(SHOTS / f'companion_{name}.png'))


def visible_words(page):
    return page.evaluate("""() => document.body.innerText""")


def no_technical(page, where):
    text = visible_words(page)
    for words in TECHNICAL:
        assert words not in text.split('\n') and (words == 'null' or words not in text), (where, words)


def first_visit(port):
    with tempfile.TemporaryDirectory(prefix='link-companion-') as folder:
        settings = Settings(data_dir=Path(folder), port=port, ai_mode='mock')
        app = create_app(settings, MockAI())
        db = app.state.db
        server, thread = serve(app, port)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width': 1280, 'height': 800}, device_scale_factor=2 if SHOTS else 1)
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')

                # One question, three cards, a quiet skip. Nothing else competes.
                page.get_by_role('heading', name='What do you need help with?').wait_for()
                cards = page.locator('.connect-card')
                expect(cards).to_have_count(3)
                assert [c.locator('strong').inner_text() for c in cards.all()] == ['I don’t know where to start', 'Reach out to someone', 'I just met someone']
                assert page.get_by_role('button', name='Skip for now', exact=True).count() == 1
                # A brand-new user learns what Link is for, what each card leads to, and where Skip goes (D54).
                expect(page.locator('.connect-lede')).to_have_text('Link remembers who you met, what you talked about, and what to say next.')
                lede = page.locator('.connect-lede').bounding_box()
                assert lede['height'] < 30, 'the value line fits on one line on a laptop'
                helpers = [c.locator('small').inner_text() for c in cards.all()]
                assert helpers[0].startswith('No contacts needed.') and 'first message' in helpers[1] and 'nothing is sent' in helpers[1] and 'remember them later' in helpers[2], helpers
                skip_btn = page.get_by_role('button', name='Skip for now', exact=True)
                assert skip_btn.get_attribute('aria-describedby') == 'connect-skip-note'
                expect(page.locator('#connect-skip-note')).to_have_text('Goes straight to Today, your home screen.')
                assert page.title() == 'Link · Remember the people you meet'
                for gone in ('Already have a network?', 'Your context stays in your control', 'Remember the people you meet'):
                    assert gone not in visible_words(page), gone

                # The welcome tip: shown once, spoken politely, closable.
                bubble = page.locator('#sprite-bubble')
                expect(bubble).to_be_visible()
                expect(page.locator('#sprite-text')).to_contain_text('Hi, I’m Link')
                expect(page.locator('#sprite-live')).to_contain_text('Hi, I’m Link')
                assert page.evaluate('document.activeElement.id') != 'sprite-close', 'a tip never takes focus'
                shot(page, '1_welcome_tip')
                page.locator('#sprite-close').click()
                expect(bubble).to_be_hidden()

                # The sprite opens the chat as a drawer over the page; the page behind waits.
                sprite = page.locator('#dock-pill')
                expect(sprite).to_have_attribute('aria-expanded', 'false')
                box_before = page.locator('#main').bounding_box()
                sprite.click()
                expect(page.locator('#dock')).to_be_visible()
                expect(sprite).to_have_attribute('aria-expanded', 'true')
                assert page.evaluate('document.activeElement.id') == 'chat-input', 'focus goes to the message box'
                assert page.evaluate("document.getElementById('main').inert"), 'the page behind cannot be reached'
                assert page.locator('#main').bounding_box() == box_before, 'opening the chat never squeezes the page'
                assert page.locator('#dock').get_attribute('role') == 'dialog'
                no_technical(page, 'drawer')
                shot(page, '2_drawer')
                page.keyboard.press('Escape')
                expect(page.locator('#dock')).to_be_hidden()
                assert page.evaluate('document.activeElement.id') == 'dock-pill', 'focus returns to the sprite'
                assert not page.evaluate("document.getElementById('main').inert")
                sprite.click()
                expect(page.locator('#dock')).to_be_visible()
                page.mouse.click(200, 400)  # outside the drawer, on the dimmed page
                expect(page.locator('#dock')).to_be_hidden()

                # Review fixes: the toast is still spoken, later nodes are blocked, and search closes the chat first.
                sprite.click()
                expect(page.locator('#dock')).to_be_visible()
                assert not page.evaluate("document.getElementById('toast').inert"), 'save messages are still spoken'
                assert page.evaluate("(() => { const b = document.createElement('button'); b.id = 'late'; document.body.append(b); return new Promise(r => setTimeout(() => r(b.inert), 50)); })()"), 'a node added while the chat is open is blocked'
                page.keyboard.press('Control+k')
                expect(page.locator('#dock')).to_be_hidden()
                assert page.evaluate("document.activeElement.closest('dialog.command-palette') !== null"), 'search takes focus'
                page.keyboard.type('peo')
                assert page.locator('dialog.command-palette input').input_value() == 'peo'
                page.keyboard.press('Escape')  # a search field's first Escape clears its text (browser behavior)…
                page.keyboard.press('Escape')  # …the second closes the search
                assert not page.evaluate('!!document.querySelector("dialog.command-palette[open]")'), 'search closed'
                assert not page.evaluate("document.getElementById('late').inert"), 'it is released when the chat closes'

                # A starter card: one question, one box, one button that waits for words.
                page.get_by_role('button', name='Reach out to someone').click()
                page.get_by_role('heading', name='Who do you want to reach out to?').wait_for()
                heading, hint = page.locator('#connect-question').bounding_box(), page.locator('.connect-hint').bounding_box()
                assert heading['y'] + heading['height'] <= hint['y'] + 1, 'the first-visit question uses the one-column layout'
                go = page.get_by_role('button', name='Show me a next step')
                expect(go).to_be_disabled()
                expect(page.locator('.connect-promise')).to_have_text('Nobody gets contacted. You decide what to keep.')  # on the page, not only in a tip
                page.get_by_label('Who do you want to reach out to?').fill('Maya, a data analyst I met at the career fair. I want to ask how she got into analytics.')
                shot(page, '3_question')
                go.click()
                page.get_by_role('heading', name='Here’s a possible next step.').wait_for()
                expect(page.locator('.connect-hint', has_text='sample answer')).to_be_visible()  # honest about sample AI
                no_technical(page, 'review')  # includes no stray "null"
                next_step = page.get_by_label('Your next step')
                assert next_step.input_value().strip(), 'the suggested step comes prefilled'
                # The exact note that would be kept is on screen, and the box says who it goes with.
                expect(page.locator('.connect-note-preview')).to_have_text('Maya, a data analyst I met at the career fair. I want to ask how she got into analytics.')
                keep = page.get_by_label('Keep this note (only you see it)')
                assert keep.is_checked()
                page.get_by_label('Their name (optional)').fill('Maya Chen')
                assert page.get_by_label('Keep this note with Maya Chen').is_checked()
                page.get_by_label('Their name (optional)').fill('')
                shot(page, '4_review')
                page.get_by_role('button', name='Save', exact=True).click()
                page.get_by_text('Saved. No one has been contacted.').wait_for()
                # A save is confirmed once, by a tip (confirmations are never rationed)…
                expect(page.locator('#sprite-text')).to_have_text('Saved. Your next step is waiting on Today.')
                shot(page, '4b_saved_tip')
                # Escape on a tip's button hides it and keeps focus on the page, at the sprite.
                page.wait_for_timeout(600)  # let the page finish rendering (it moves focus to the new page when done)
                page.locator('#sprite-mute').focus()
                page.keyboard.press('Escape')
                expect(bubble).to_be_hidden()
                assert page.evaluate('document.activeElement.id') == 'dock-pill'
                # A tip never sits over the field you're typing in: it steps aside as soon as typing starts.
                page.goto(page.url.split('#')[0] + '#quicklog')
                note = page.get_by_label('What do you remember?')
                note.wait_for()
                page.evaluate("document.getElementById('sprite-bubble').hidden = false")  # a tip is up
                note.click()
                expect(bubble).to_be_hidden()
                page.evaluate("document.getElementById('sprite-bubble').hidden = false")
                note.type('Met Priya')
                expect(bubble).to_be_hidden()
                note.fill('')
                # …and tips can be turned off right on a tip; it is remembered.
                page.locator('#side').get_by_role('link', name='Today').click()
                page.locator('#main h1').first.wait_for()
                page.wait_for_timeout(600)
                page.evaluate("document.getElementById('sprite-bubble').hidden = false")
                page.get_by_role('button', name='Turn off tips').click()
                expect(bubble).to_be_hidden()
                assert page.evaluate("localStorage.getItem('cc.tipsOn')") == 'false'
                expect(page.locator('#sprite-live')).to_contain_text('Tips are off')
                assert db.one("SELECT COUNT(*) AS n FROM interactions")['n'] == 1, 'the note was kept'
                assert db.one("SELECT COUNT(*) AS n FROM actions WHERE commitment=1")['n'] == 1, 'the next step was saved'

                # Tips back on from the drawer's toggle.
                sprite.click()
                toggle = page.locator('#dock [data-tips-toggle]')
                assert toggle.get_attribute('role') == 'switch' and toggle.inner_text() == 'Tips'  # a fixed label
                expect(toggle).to_have_attribute('aria-checked', 'false')
                toggle.click()
                expect(toggle).to_have_attribute('aria-checked', 'true')
                page.keyboard.press('Escape')

                # Today: no stray "null", no technical labels, sprite present, no third column.
                page.locator('#side').get_by_role('link', name='Today').click()
                page.locator('#main h1').first.wait_for()  # Today's first-person screen or its daily view
                no_technical(page, 'today')
                expect(page.locator('#dock')).to_be_hidden()  # closed, after its short slide
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)


def phone_and_people(port):
    with tempfile.TemporaryDirectory(prefix='link-companion-phone-') as folder:
        settings = Settings(data_dir=Path(folder), port=port, ai_mode='mock')
        app = create_app(settings, MockAI())
        db = app.state.db
        load_demo(db, local_today(settings))
        db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
        server, thread = serve(app, port)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                context = browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce', device_scale_factor=2 if SHOTS else 1)
                page = context.new_page()
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')
                page.locator('#main h1, #main h2').first.wait_for()
                page.goto(f'http://127.0.0.1:{port}/#connect')
                page.get_by_role('heading', name='What do you need help with?').wait_for()
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'no sideways scroll'
                sprite, tabs = page.locator('#dock-pill').bounding_box(), page.locator('#mobile-tabs').bounding_box()
                assert sprite['y'] + sprite['height'] <= tabs['y'], 'the sprite sits above the tab bar'
                assert page.evaluate("getComputedStyle(document.querySelector('#dock-pill .orb')).animationName") == 'none', 'no motion when reduced'
                shot(page, '5_phone_connect')
                page.locator('#dock-pill').click()
                drawer = page.locator('#dock').bounding_box()
                assert drawer['width'] >= 389 and drawer['y'] > 0, 'a bottom sheet on a phone'
                page.keyboard.press('Escape')

                # People: opening someone offers help once, and the chat knows who you mean. A fresh visit with no
                # reminders due and the hello already seen, so no other suggestion has used this visit's spacing.
                db.run('DELETE FROM reminders')
                page.evaluate("localStorage.setItem('cc.tipsEver', JSON.stringify(['hello', 'welcome']))")
                page.goto(f'http://127.0.0.1:{port}/#people')
                page.reload()
                page.locator('.person-row').first.click()
                page.locator('.person-heading h2').wait_for()
                name = page.locator('.person-heading h2').inner_text()
                expect(page.locator('#sprite-text')).to_contain_text('Want help writing to ' + name.split()[0])
                page.locator('#dock-pill').click()
                expect(page.locator('.context-now')).to_contain_text('About ' + name.replace('[SAMPLE] ', ''))
                page.get_by_role('button', name='Stop talking about ' + name.replace('[SAMPLE] ', '')).click()
                expect(page.locator('#studio-context')).to_be_hidden()
                no_technical(page, 'people drawer')
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)


first_visit(8921)
phone_and_people(8922)
assert not errors, errors
print('Companion checks passed: one-column Connect, tips (show, close, off, on), drawer over the page with focus and '
      'outside-click close, one-tap save, no technical labels, phone layout; no JS errors.')
