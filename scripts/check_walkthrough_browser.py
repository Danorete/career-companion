"""How Link works, its progress tracker and the agent-guided walkthrough (decision D55), in a real browser.

1. A brand-new user lands on How Link works: what Link is, where things are kept, sample answers, three ways to begin,
   why each question is asked, and the tracker at stage 1.
2. The walkthrough, start to finish, on a laptop with reduced motion: every step, the agent's typing and clicks, the
   practice person in People and Today, the Reach out flow with its reasons, Back, Replay, and the controls. The page
   behind is inert, nothing but reads reach the server, and the database is unchanged.
3. Leaving: Back to How Link works writes nothing; Escape finishes the first stage (one request) and lands on Today.
4. Real progress: adding a person moves the tracker on Today and on How Link works; the stage is announced.
5. "I don't know where to start" leads to the three starting points; Reach out explains each question; a real sample
   answer says why it is a sample and shows no "[MOCK]" tag; Menu and Settings offer the page and the tour.
6. A phone with motion: the page and tour fit the screen, the text types, Pause shows it all and stops the tour moving
   on, Play resumes, and Skip to the app leaves without writing anything.
Fails on any script error. Synthetic data, sample AI, temporary folders only.
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
from companion.db import USER_TABLES

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
        page.wait_for_timeout(400)
        page.screenshot(path=str(SHOTS / f'walkthrough_{name}.png'))


def counts(db):
    return {t: db.one(f'SELECT COUNT(*) AS n FROM {t}')['n'] for t in USER_TABLES}


def until(page, expression, timeout=20000):
    """Poll an expression from Python. The page's Content-Security-Policy forbids string evaluation inside the page, which
    wait_for_function needs once a page has reloaded; page.evaluate goes through the debugger and is allowed."""
    end = time.time() + timeout / 1000
    while time.time() < end:
        try:
            if page.evaluate(expression):
                return
        except Exception:  # the page is navigating
            pass
        page.wait_for_timeout(100)
    raise AssertionError('timed out waiting for ' + expression)


def ready(page, timeout=20000):
    page.locator('.tour-card[data-ready="true"]').wait_for(timeout=timeout)
    return page.locator('.tour-title').inner_text()


def step_no(page):
    return int(page.locator('.tour-card').get_attribute('data-step'))


def next_step(page):
    before = step_no(page)
    page.locator('.tour-next').click()
    until(page, f'document.querySelector(".tour-card").dataset.step !== "{before}"')
    return ready(page)


def laptop(port):
    with tempfile.TemporaryDirectory(prefix='link-walkthrough-') as folder:
        app = create_app(Settings(data_dir=Path(folder), port=port, ai_mode='mock'), MockAI())
        db = app.state.db
        server, thread = serve(app, port)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                context = browser.new_context(viewport={'width': 1280, 'height': 860}, reduced_motion='reduce', device_scale_factor=2 if SHOTS else 1)
                page = context.new_page()
                page.on('pageerror', lambda e: errors.append(str(e)))
                writes = []
                page.on('request', lambda r: writes.append(r.method + ' ' + r.url.split(str(port))[-1]) if r.method != 'GET' else None)
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')

                # 1. How Link works is the first screen.
                page.get_by_role('heading', name='Welcome to Link.').wait_for()
                main = page.locator('#main')
                text = main.inner_text()
                for words in ('remember the people you meet', 'Everything you add stays on this computer.', 'Link never contacts anyone.',
                              'How far you’ve come', 'Not sure where to start?', 'I met or noticed someone recently', 'I don’t have a specific person in mind yet',
                              'I want to see the whole thing first.', 'About sample answers', 'isn’t switched on in this version', 'not an error', 'Why Link asks what it asks'):
                    assert words in text, words
                bar = page.locator('.journey [role=progressbar]')
                assert bar.get_attribute('aria-valuenow') == '0' and 'Stage 1 of 4' in bar.get_attribute('aria-valuetext')
                expect(page.locator('.journey [aria-current=step]')).to_contain_text('Start here')
                where = page.locator('[data-tour="start-where"]')
                for label in ('Add a person', 'Add a note', 'About me', 'What I’ve done', 'Jobs I’m looking at', 'Explore ideas with Link', 'Start the walkthrough'):
                    assert where.get_by_role('button', name=label, exact=True).count() == 1, label
                why = page.locator('[data-tour="start-why"]').text_content()  # inside closed groups: present, not yet shown
                for words in ('Why them, or why there?', 'never goes into a message', 'only background Link may put in a message',
                              'You don’t need a polished portfolio', 'A first name is enough'):
                    assert words in why, words
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                shot(page, '1_start')
                before = counts(db)
                writes.clear()  # signing in posted once; from here on, nothing may

                # 2. The walkthrough: a modal card, the page inert, practice data only.
                page.get_by_role('button', name='Show me how it works').first.click()
                card = page.locator('.tour-card')
                card.wait_for()
                assert card.get_attribute('role') == 'dialog' and card.get_attribute('aria-modal') == 'true'
                assert page.evaluate('document.querySelector(".tour-card").contains(document.activeElement)'), 'focus starts in the card'
                assert ready(page) == 'Hi, I’m Link.'
                expect(page.locator('.tour-chip')).to_have_text('Practice tour · nothing is saved')
                tour_bar = page.locator('.tour-card .journey.is-tour')
                expect(tour_bar).to_contain_text('Tour progress')
                expect(tour_bar).to_contain_text('Part 1 of 4: Start here')
                expect(tour_bar).to_contain_text('Practice only')
                expect(page.locator('.tour-play')).to_have_text('Play')  # reduced motion: nothing moves on by itself
                assert page.locator('.tour-text-live').inner_text() == page.locator('#tour-desc').inner_text(), 'reduced motion: the text appears at once'
                assert page.evaluate('document.querySelector(".shell").inert'), 'the page behind is inert'
                page.mouse.click(240, 38)  # where the Today link sits: the shield takes it
                page.wait_for_timeout(300)
                assert page.evaluate('location.hash') == '#start', 'a click on the page does nothing during the tour'
                for _ in range(6):
                    page.keyboard.press('Tab')
                    assert page.evaluate('document.querySelector(".tour-card").contains(document.activeElement)'), 'Tab stays in the card'
                page.wait_for_timeout(1500)
                assert step_no(page) == 0, 'paused: no step moves on by itself'
                shot(page, '2_tour_start')

                seen = {}
                total = int(page.locator('.tour-step').inner_text().split(' of ')[1].split(' ')[0])
                while True:
                    title = page.locator('.tour-title').inner_text()
                    seen[title] = step_no(page)
                    if title == 'Add a person.':
                        assert page.locator('#main input[aria-label="Their name"]').input_value() == 'Maya Chen', 'the agent typed the name'
                        expect(page.locator('.guide-preview-name')).to_have_text('Maya Chen')
                        shot(page, '3_add_person')
                    if title == 'How you met.':  # Back returns, Next comes back to the same place
                        page.locator('.tour-back').click()
                        assert ready(page) == 'Watch the preview.'
                        assert next_step(page) == 'How you met.'
                        expect(page.locator('#main .guide-chip', has_text='At a club or event')).to_have_attribute('aria-pressed', 'true')
                    if title == 'What you remember.':  # Replay this step runs it again
                        page.locator('.tour-replay').click()
                        assert ready(page) == 'What you remember.'
                        assert 'SQL workshops' in page.locator('#main .guide-stage textarea').input_value()
                    if title == 'Check it, then save.':
                        expect(page.locator('#main .guide-done h2')).to_have_text('Maya Chen is in Link.')
                        shot(page, '4_saved_practice')
                    if title == 'Add a note.':
                        assert 'Coffee chat with Maya' in page.locator('#main .quicklog-page textarea').first.input_value()
                        expect(page.locator('#quick-draft-status')).to_have_text('Tour: nothing you type here is saved.')
                    if title == 'People.':
                        expect(page.locator('#main .person-row')).to_contain_text('Maya Chen')
                    if title == 'Today is home.':
                        expect(page.locator('#hero-title')).to_have_text('Send Maya a thank-you note')
                        shot(page, '5_today_practice')
                    if title == 'Who, and why them?':
                        assert page.locator('#main .connect-form > textarea').input_value().startswith('Maya Chen. She leads the data club')
                        expect(page.locator('#connect-why')).to_contain_text('Why we ask:')
                    if title == 'Why them, or why there?':
                        expect(page.locator('#why-why_person')).to_be_visible()
                        assert page.locator('#main [data-tour="field-why_person"] textarea').get_attribute('aria-describedby') == 'why-why_person'
                        box = page.locator('#main [data-tour="field-why_person"]').bounding_box()
                        assert 0 <= box['y'] < 860 * 0.7, 'the field was brought into view'
                        shot(page, '6_why_them')
                    if title == 'Here’s a possible next step.':
                        expect(page.locator('#main .plan-story')).to_contain_text('Practice answer for the walkthrough. Nothing here is saved.')
                        shot(page, '7_plan')
                    if title == 'That’s the whole loop.':
                        expect(page.locator('.tour-finale')).to_be_visible()
                        expect(tour_bar).to_contain_text('Tour complete')
                        shot(page, '8_finale')
                        break
                    assert step_no(page) < total - 1
                    next_step(page)
                assert len(seen) == total, (len(seen), total)
                assert writes == [], writes
                assert counts(db) == before, 'the tour changed nothing in the database'

                # 3. Leaving. Back to How Link works writes nothing; the welcome is still there.
                page.get_by_role('button', name='Back to How Link works').click()
                page.get_by_role('heading', name='Welcome to Link.').wait_for()
                assert writes == [] and counts(db) == before
                assert page.locator('.tour-card').count() == 0
                # Escape mid-tour finishes the first stage, with one request, and lands on Today.
                page.get_by_role('button', name='Show me how it works').first.click()
                ready(page)
                next_step(page)
                page.keyboard.press('Escape')
                until(page, 'location.hash === "#today"')
                page.locator('.journey.is-compact').wait_for()
                assert writes == ['POST /api/journey/oriented'], writes
                after = counts(db)
                assert {t: n for t, n in after.items() if n != before[t]} == {'kv': after['kv']}, 'only the stage flag changed'
                assert page.evaluate("fetch('/api/people').then(r => r.json())") == [], 'the practice person is gone'

                # 4. Real progress: Today's tracker, then a real person moves it on.
                compact = page.locator('.journey.is-compact')
                expect(compact).to_contain_text('25%')
                expect(compact.locator('[aria-current=step]')).to_contain_text('Groundwork')
                page.goto(page.url.split('#')[0] + '#add')
                page.get_by_label('Their name').fill('Priya Raman')
                page.locator('.guide-continue').click()
                for _ in range(3):
                    page.locator('.guide-panel .guide-continue').click()
                    page.wait_for_timeout(150)
                page.locator('.guide-save').click()
                page.get_by_role('heading', name='Priya Raman is in Link.').wait_for()
                page.locator('#side').get_by_role('link', name='Today').click()
                compact = page.locator('.journey.is-compact')
                compact.wait_for()
                expect(compact).to_contain_text('50%')
                stage = compact.locator('[data-stage="people"]')
                assert 'is-done' in stage.get_attribute('class') and 'just-done' not in stage.get_attribute('class'), 'reduced motion: no pop'
                expect(page.locator('#sprite-live')).to_contain_text('Stage done: People & notes')
                shot(page, '9_today_progress')
                page.goto(page.url.split('#')[0] + '#start')
                page.get_by_role('heading', name='How Link works.').wait_for()
                expect(page.locator('.journey-next')).to_contain_text('Up next: Add one thing about you')
                expect(page.locator('.journey-go')).to_have_text('Open About me →')

                # 5. "I don't know where to start" leads to the three starting points.
                page.goto(page.url.split('#')[0] + '#connect')
                page.get_by_role('button', name='I don’t know where to start').click()
                until(page, 'document.activeElement && document.activeElement.id === "start-where-title"')
                assert page.evaluate('location.hash') == '#start'
                # Reach out explains each question, and a real sample answer says why it is a sample.
                page.goto(page.url.split('#')[0] + '#connect')
                page.get_by_role('button', name='Reach out to someone').click()
                page.get_by_role('heading', name='Who do you want to reach out to?').wait_for()
                expect(page.locator('#connect-why')).to_have_text('Why we ask: A specific person and a real reason make the first message much easier to write.')
                assert page.get_by_label('Who do you want to reach out to?').get_attribute('aria-describedby') == 'connect-why'
                page.locator('[data-tour="more-detail"] > summary').click()
                for key in ('why_person', 'goal', 'approved_context', 'example'):
                    expect(page.locator('#why-' + key)).to_be_visible()
                page.get_by_label('Who do you want to reach out to?').fill('Priya, she runs the analytics club.')
                page.get_by_role('button', name='Show me a next step').click()
                page.get_by_role('heading', name='Here’s a possible next step.').wait_for()
                story = page.locator('.plan-story').inner_text()
                assert 'Sample answer: Link’s AI isn’t switched on in this version' in story and '[MOCK' not in story, story
                # Menu and Settings offer the page and the tour.
                page.locator('#more-menu > summary').click()
                menu = page.locator('#more-menu')
                assert menu.get_by_role('link', name='How Link works').count() == 1 and menu.get_by_role('button', name='Take the tour').count() == 1
                page.keyboard.press('Escape')
                page.goto(page.url.split('#')[0] + '#settings')
                page.get_by_role('heading', name='Meet Link').wait_for()
                section = page.get_by_role('heading', name='Meet Link').locator('..')
                assert section.get_by_role('button', name='How Link works').count() == 1 and section.get_by_role('button', name='Take the tour').count() == 1
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)


def phone(port):
    with tempfile.TemporaryDirectory(prefix='link-walkthrough-phone-') as folder:
        app = create_app(Settings(data_dir=Path(folder), port=port, ai_mode='mock'), MockAI())
        db = app.state.db
        db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")  # past the welcome already
        server, thread = serve(app, port)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
                context = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2 if SHOTS else 1)
                page = context.new_page()
                page.on('pageerror', lambda e: errors.append(str(e)))
                writes = []
                page.on('request', lambda r: writes.append(r.method + ' ' + r.url) if r.method != 'GET' else None)
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')
                page.locator('#mobile-more-button').click()  # How Link works is in More on a phone
                page.locator('#mobile-more').get_by_role('link', name='How Link works').click()
                page.get_by_role('heading', name='How Link works.').wait_for()
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'no sideways scroll'
                before = counts(db)
                writes.clear()  # signing in posted once; from here on, nothing may
                page.get_by_role('button', name='Show me how it works').first.click()
                page.locator('.tour-card').wait_for()
                expect(page.locator('.tour-card')).to_have_class('tour-card is-typing')  # the text types itself
                expect(page.locator('.tour-play')).to_have_text('Pause')
                box = page.locator('.tour-card').bounding_box()
                assert box['x'] >= 0 and box['x'] + box['width'] <= 390 and box['y'] + box['height'] <= 844, box
                # Pause: the text shows in full at once and nothing moves on.
                page.locator('.tour-play').click()
                expect(page.locator('.tour-play')).to_have_text('Play')
                assert page.locator('.tour-text-live').inner_text() == page.locator('#tour-desc').inner_text()
                ready(page)
                page.wait_for_timeout(9000)
                assert step_no(page) == 0, 'paused tours wait'
                # Play: it moves on by itself.
                page.locator('.tour-play').click()
                until(page, 'document.querySelector(".tour-card").dataset.step === "1"', 20000)
                shot(page, '10_phone_tour')
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'no sideways scroll in the tour'
                page.get_by_role('button', name='Skip to the app').click()
                until(page, 'location.hash === "#today"')
                page.locator('#main h1').first.wait_for()
                assert writes == [], writes  # already past the welcome, so leaving writes nothing at all
                assert counts(db) == before
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)


laptop(8941)
phone(8942)
assert not errors, errors
print('Walkthrough checks passed: How Link works as the first screen, tracker, every tour step with practice data, inert page, '
      'Back, Replay, Pause and Play, no writes during the tour, leaving, real progress, why-we-ask lines, sample wording, phone; no JS errors.')
