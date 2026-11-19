"""The web version in a real browser (decision D50). Google is stood in for: the browser's trip to Google's sign-in
page is intercepted and sent straight back, and the token exchange is answered by a local stand-in.

Checks the sign-in page, a full sign-in, that no "on this Mac" wording is left on the web, Sign out, and that Delete
everything removes the account and returns to the sign-in page. Temporary data and sample AI only.
"""
import base64
import json
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import httpx
import uvicorn
from playwright.sync_api import expect, sync_playwright
from companion.web import WebConfig, create_web_app

PORT = 8896
PUBLIC = f'http://localhost:{PORT}'
CLIENT_ID = 'web-client.apps.example'
MAC_WORDS = ('on this Mac', 'this computer', 'leaves this', 'Terminal', 'Spotlight', 'Quit Link', 'companion launcher')
nonce = {'value': ''}


def google(request: httpx.Request) -> httpx.Response:
    if request.url.path == '/revoke':
        return httpx.Response(200)
    claims = {'iss': 'https://accounts.google.com', 'aud': CLIENT_ID, 'exp': time.time() + 3600, 'nonce': nonce['value'],
              'email': 'maya@example.com', 'email_verified': True}
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b'=').decode()
    return httpx.Response(200, json={'id_token': 'e30.' + payload + '.sig'})


def through_google(route):
    """Link's /signin answers with a trip to Google. Instead of going, come straight back as Google would."""
    answer = route.fetch(max_redirects=0)
    target = answer.headers['location']
    assert target.startswith('https://accounts.google.com/'), target
    query = parse_qs(urlsplit(target).query)
    nonce['value'] = query['nonce'][0]
    assert query['scope'] == ['openid email'], query['scope']
    route.fulfill(status=302, headers={'location': f"{PUBLIC}/connect/google/callback?state={query['state'][0]}&code=c"})


def never_google(route):
    raise AssertionError('the browser tried to reach Google for real: ' + route.request.url)


def sign_in(page):
    page.goto(PUBLIC + '/')
    page.get_by_role('link', name='Sign in with Google').click()
    expect(page.locator('body')).to_have_attribute('data-hosted', '1')  # the app has loaded, as the web version
    explore = page.get_by_role('button', name='Skip to the app')  # How Link works' skip into the app (D55)
    page.wait_for_timeout(500)
    if explore.count():  # a brand-new account starts on How Link works
        no_mac_words(page, 'welcome screen')
        assert 'Everything you add stays in your account' in page.locator('#main').inner_text()
        explore.first.click()
    page.locator('#more-menu > summary').wait_for()


def no_mac_words(page, where):
    text = page.locator('body').inner_text()
    for words in MAC_WORDS:
        assert words not in text, (where, words)


errors = []
with tempfile.TemporaryDirectory(prefix='link-web-') as folder:
    cfg = WebConfig(public_url=PUBLIC, data_root=Path(folder), secret_key='k' * 48, google_client_id=CLIENT_ID,
                    google_client_secret='secret', invites=frozenset({'maya@example.com'}))
    app = create_web_app(cfg, transport=httpx.MockTransport(google))
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
            context = browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce', timezone_id='America/Chicago')
            context.route(f'{PUBLIC}/signin*', through_google)
            context.route('https://accounts.google.com/**', never_google)
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))

            # 1. Signed out: the sign-in page, with the data promise.
            page.goto(PUBLIC + '/')
            page.get_by_role('heading', name='Where your information goes').wait_for()
            text = page.locator('main').inner_text()
            assert 'invite-only' in text and 'Delete everything' in text and '30 days' in text and 'could technically see' in text
            assert 'tz=America%2FChicago' in page.get_by_role('link', name='Sign in with Google').get_attribute('href')
            page.set_viewport_size({'width': 390, 'height': 844})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'sign-in page scrolls sideways on a phone'
            page.set_viewport_size({'width': 1280, 'height': 900})

            # 2. Sign in through the stand-in Google; the app opens and knows it is the web version.
            sign_in(page)
            assert page.evaluate('document.body.dataset.hosted') == '1'
            [account] = list((Path(folder) / 'people').iterdir())
            assert app.state.accounts.count() == 1
            no_mac_words(page, 'first screen')

            # 3. The Menu offers Sign out, not Quit, and says where data is kept.
            page.locator('#more-menu > summary').click()
            menu = page.locator('#more-menu').inner_text()
            assert 'Sign out' in menu and 'Quit Link' not in menu and 'Link’s server' in menu, menu
            page.keyboard.press('Escape')
            for route in ('settings', 'sources', 'today', 'quicklog', 'start'):
                page.goto(f'{PUBLIC}/#{route}')
                page.locator('#main').wait_for()
                page.wait_for_timeout(400)
                no_mac_words(page, route)
            # The walkthrough says where things are kept on the web, in every step (D55).
            page.goto(f'{PUBLIC}/#start')
            page.get_by_role('button', name='Show me how it works').first.click()
            said = []
            for _ in range(60):
                page.locator('.tour-card[data-ready="true"]').wait_for()
                said.append(page.locator('.tour-card').inner_text())
                if page.locator('.tour-finale').is_visible():
                    break
                step = page.locator('.tour-card').get_attribute('data-step')
                page.locator('.tour-next').click()
                page.locator(f'.tour-card:not([data-step="{step}"])').wait_for()
            tour = '\n'.join(said)
            assert 'Everything you add stays in your account' in tour, 'the tour says where things are kept on the web'
            for words in MAC_WORDS:
                assert words not in tour, ('tour', words)
            page.keyboard.press('Escape')
            page.locator('#main h1').first.wait_for()
            page.goto(f'{PUBLIC}/#settings')
            page.get_by_role('heading', name='Signing out').wait_for()
            assert page.get_by_role('heading', name='Starting and stopping Link').count() == 0

            # 4. Sign out returns to the sign-in page; the data stays.
            page.locator('#more-menu > summary').click()
            page.locator('#more-menu').get_by_role('button', name='Sign out').click()
            page.get_by_role('link', name='Sign in with Google').wait_for()
            assert account.exists()

            # 5. Delete everything removes the account and the folder, and signs out.
            sign_in(page)
            page.goto(f'{PUBLIC}/#settings')
            page.locator('summary', has_text='Delete everything').click()  # it sits in a closed section
            help_text = page.locator('details.help', has_text='Delete everything').inner_text()
            assert 'deletes your account' in help_text and 'Time Machine' not in help_text, help_text
            page.get_by_label('Type DELETE EVERYTHING to confirm').fill('DELETE EVERYTHING')
            page.get_by_role('button', name='Delete everything').click()
            page.get_by_role('link', name='Sign in with Google').wait_for()
            assert not account.exists() and app.state.accounts.count() == 0
            browser.close()
    finally:
        server.should_exit = True
        thread.join(10)
assert not errors, errors
print('Web version checks passed: sign-in page, Google sign-in, no Mac-only wording, Sign out, Delete everything; no JS errors.')
