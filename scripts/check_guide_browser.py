"""The step-by-step guide for adding a person (decision D52), in a real browser.

Walks the whole guide as a first-time user, then the short path, editing from the review, a failed save, a slow save,
starting from someone found in the calendar, and a phone-sized screen. Fails on any script error. Synthetic data,
sample AI, temporary folders only.
"""
import asyncio
import sys
import tempfile
import threading
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import uvicorn
from playwright.sync_api import expect, sync_playwright
from companion import encounters
from companion.ai import MockAI
from companion.app import create_app
from companion.config import Settings
from companion.connectors import SampleCalendar
from companion.services import local_today

SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None
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
        page.wait_for_timeout(700)
        page.screenshot(path=str(SHOTS / f'guide_{name}.png'))


def chip(page, label):
    return page.locator('.guide-panel').get_by_role('button', name=label, exact=True)


def primary(page):
    return page.locator('.guide-panel .guide-continue, .guide-panel .guide-save').first


def question(page, text):
    page.locator('.guide-panel h2', has_text=text).wait_for()


def first_run(port):
    """A brand-new user: the welcome screen offers the guide; the whole flow; editing; the result in the database."""
    with tempfile.TemporaryDirectory(prefix='link-guide-') as folder:
        settings = Settings(data_dir=Path(folder), port=port, ai_mode='mock')
        app = create_app(settings, MockAI())
        db = app.state.db
        slow_save = {'on': False}

        @app.middleware('http')
        async def slow(request, call_next):  # the server takes its time, so the browser stays free to watch
            if slow_save['on'] and request.url.path == '/api/guide/connection':
                await asyncio.sleep(1.2)
            return await call_next(request)

        server, thread = serve(app, port)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width': 1280, 'height': 900}, device_scale_factor=2 if SHOTS else 1)
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')

                # Ways to begin (D51), now on How Link works (D55): "I met or noticed someone recently" leads to the guide,
                # and Skip goes into the app.
                page.get_by_role('heading', name='Welcome to Link.').wait_for()
                assert page.get_by_role('button', name='Skip to the app').count() >= 1
                shot(page, '0_welcome')
                page.locator('[data-tour="where-met"]').get_by_role('button', name='Add a person', exact=True).click()

                # 1. Who. Continue waits for a name; the preview answers as you type.
                question(page, 'Who did you meet?')
                assert page.locator('.guide-title .eyebrow').text_content() == 'Your first person'
                assert 'about a minute' in page.locator('.guide-step-label').inner_text()
                assert page.evaluate('document.activeElement.tagName') == 'H2', 'focus moves to the question'
                expect(primary(page)).to_be_disabled()
                page.get_by_label('Their name').fill('Priya Raman')
                expect(page.locator('.guide-avatar')).to_have_text('PR')
                expect(page.locator('.guide-preview-name')).to_have_text('Priya Raman')
                page.get_by_label('Where they work or study (optional)').fill('Deloitte')
                shot(page, '1_who')
                page.get_by_label('Where they work or study (optional)').press('Enter')

                # 2. How you met. Optional: the button says Skip until something is chosen.
                question(page, 'How do you know Priya?')
                assert page.locator('.guide-progress').get_attribute('aria-valuenow') == '1'
                expect(primary(page)).to_have_text('Skip this')
                chip(page, 'At a career fair').click()
                chip(page, 'Today').click()
                expect(chip(page, 'At a career fair')).to_have_attribute('aria-pressed', 'true')
                expect(primary(page)).to_have_text('Continue')
                expect(page.locator('.guide-fact', has_text='How you met')).to_contain_text('Met at a career fair, today')
                shot(page, '2_met')
                primary(page).click()

                # 3. What you remember, with a sentence starter.
                question(page, 'What do you remember about Priya?')
                chip(page, 'We talked about…').click()
                page.get_by_label('What you remember').press_sequentially('analytics internships')
                expect(page.locator('.guide-fact', has_text='What you remember')).to_contain_text('We talked about analytics internships')
                primary(page).click()

                # 4. Next step and reminder.
                question(page, 'next step with Priya')
                expect(primary(page)).to_have_text('No next step yet')
                expect(page.get_by_role('group', name='Reminder')).to_be_hidden()
                chip(page, 'Send a thank-you note').click()
                expect(chip(page, 'In 3 days')).to_have_attribute('aria-pressed', 'true')
                chip(page, 'Next week').click()
                shot(page, '3_next')
                primary(page).click()

                # Review, edit, come back: answers are kept.
                question(page, 'Look right?')
                review = page.locator('.guide-review').inner_text()
                for words in ('Priya Raman · Deloitte', 'Met at a career fair, today', 'analytics internships', 'Send a thank-you note · reminder next week'):
                    assert words in review, (words, review)
                page.locator('.guide-review-row', has_text='How you met').get_by_role('button', name='Edit').click()
                question(page, 'How do you know Priya?')
                expect(chip(page, 'At a career fair')).to_have_attribute('aria-pressed', 'true')
                for _ in range(3):
                    primary(page).click()
                    page.wait_for_timeout(450)
                question(page, 'Look right?')
                shot(page, '4_review')

                # Save: everything lands together, and the screen says what was saved.
                primary(page).click()
                page.get_by_role('heading', name='Priya Raman is in Link.').wait_for()
                saved = page.locator('.guide-saved').inner_text()
                assert 'Saved Priya Raman · Deloitte' in saved and 'Noted what you remember, dated today' in saved and 'Send a thank-you note' in saved, saved
                assert 'first connection' in page.locator('.guide-done').inner_text()
                expect(page.locator('.guide-preview-status')).to_have_text('Saved')
                assert page.locator('.guide-preview .eyebrow').text_content() == 'What Link saved'
                expect(page.locator('.guide-head-actions')).to_be_hidden()
                shot(page, '5_done')
                [person] = db.q("SELECT id, title, org, shareable_context FROM items WHERE kind='relationship'")
                assert (person['title'], person['org'], person['shareable_context']) == ('Priya Raman', 'Deloitte', 'Met at a career fair')
                [log] = db.q('SELECT note, occurred_on FROM interactions WHERE item_id=?', (person['id'],))
                assert log['note'] == 'We talked about analytics internships' and log['occurred_on'] == local_today(settings).isoformat()
                [reminder] = db.q('SELECT due_on FROM reminders')
                assert reminder['due_on'] == (local_today(settings) + timedelta(days=7)).isoformat()

                # Another person: a fresh start, no longer "first".
                page.get_by_role('button', name='Add another person').click()
                question(page, 'Who did you meet?')
                assert page.locator('.guide-title .eyebrow').text_content() == 'Add a person'
                assert page.locator('.guide-preview .eyebrow').text_content() == 'What Link will save'
                expect(page.locator('.guide-head-actions')).to_be_visible()
                assert page.get_by_label('Their name').input_value() == ''
                page.get_by_label('Their name').fill('priya raman')
                expect(page.locator('.guide-already')).to_contain_text('You already have Priya Raman in Link.')

                # The short path: a name, three skips, save.
                page.get_by_label('Their name').fill('Sam')
                page.get_by_label('Their name').press('Enter')
                for label in ('Skip this', 'Skip this', 'No next step yet'):
                    expect(primary(page)).to_have_text(label)
                    primary(page).click()
                    page.wait_for_timeout(450)
                question(page, 'Look right?')
                assert page.locator('.guide-review').inner_text().count('Skipped') == 3

                # A failed save keeps every answer and says so.
                page.route('**/api/guide/connection', lambda route: route.fulfill(status=500, content_type='application/json', body='{"error":"Something went wrong."}'))
                primary(page).click()
                expect(page.locator('.guide-error')).to_contain_text('Your answers are still here.')
                expect(primary(page)).to_be_enabled()
                expect(page.locator('.guide-preview-status')).to_have_text('Not saved yet')
                page.unroute('**/api/guide/connection')

                # A slow save shows a spinner, but only once the wait is noticeable.
                slow_save['on'] = True
                primary(page).click()
                page.wait_for_timeout(150)
                assert 'is-slow' not in (primary(page).get_attribute('class') or ''), 'no spinner for a quick wait'
                expect(primary(page)).to_have_text('Saving…')
                expect(page.locator('.guide-preview-status')).to_have_text('Saving…')
                page.wait_for_timeout(500)
                assert page.locator('.guide-save.is-slow .guide-spinner').is_visible(), 'a spinner once the wait is noticeable'
                page.get_by_role('heading', name='Sam is in Link.').wait_for()
                assert page.locator('.guide-saved li').count() == 1
                slow_save['on'] = False

                # The guide is in the Add menu for every later person.
                page.get_by_role('button', name='Back to Today').click()
                page.locator('#add-menu > summary').click()
                page.get_by_role('link', name='Add a person').click()
                question(page, 'Who did you meet?')
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)


def from_the_calendar(port):
    """People found in the calendar are offered on the first question; picking one keeps that suggestion."""
    with tempfile.TemporaryDirectory(prefix='link-guide-cal-') as folder:
        settings = Settings(data_dir=Path(folder), port=port, ai_mode='mock')
        app = create_app(settings, MockAI())
        db = app.state.db
        db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
        db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
        encounters.mark_connected(db, demo=True)
        encounters.sync(db, SampleCalendar())
        server, thread = serve(app, port)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                context = browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce', device_scale_factor=2 if SHOTS else 1)
                page = context.new_page()
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')
                page.locator('#main h1, #main h2').first.wait_for()  # signed in and loaded (phone layout: no Menu button)
                page.goto(f'http://127.0.0.1:{port}/#add')
                question(page, 'Who did you meet?')
                found = page.locator('.guide-found')
                expect(found).to_contain_text('People Link found')
                first = found.locator('.guide-found-chip').first
                name = first.locator('strong').inner_text()
                first.click()
                assert page.get_by_label('Their name').input_value() == name
                expect(first).to_have_attribute('aria-pressed', 'true')
                assert found.locator('.guide-found-chip[aria-pressed="true"]').count() == 1
                expect(page.locator('.guide-source-pill')).to_contain_text('From your calendar')
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'no sideways scroll on a phone'
                shot(page, '6_phone_found')
                page.get_by_label('Their name').press('Enter')
                question(page, 'How do you know')
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                for _ in range(3):
                    primary(page).click()
                question(page, 'Look right?')
                primary(page).click()
                page.get_by_role('heading', name=f'{name} is in Link.').wait_for()
                kept = db.q("SELECT state, item_id FROM encounter_candidates WHERE state='kept'")
                assert len(kept) == 1 and kept[0]['item_id'], kept
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)


first_run(8901)
from_the_calendar(8902)
assert not errors, errors
print('Guide checks passed: welcome choice, all four questions with live preview, edit from review, short path, '
      'failed and slow saves, Add menu, calendar suggestion, phone width; no JS errors.')
