"""Reminders outside Link (decision D46): the Settings section, with a stand-in notifier.

No real notification is shown and nothing leaves the computer. Requires Playwright and Linux Chromium.
"""
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import uvicorn
from playwright.sync_api import expect, sync_playwright
from companion import nudges
from companion.ai import MockAI
from companion.app import create_app
from companion.config import Settings


class Notifier:
    supported, reason = True, ''

    def __init__(self):
        self.sent = []

    def send(self, title, body):
        self.sent.append((title, body))
        return True


def run(port, notifier, check):
    with tempfile.TemporaryDirectory(prefix='link-nudges-') as folder:
        app = create_app(Settings(data_dir=Path(folder), port=port, ai_mode='mock'), MockAI(), notifier=notifier)
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
                page = browser.new_page(viewport={'width': 1440, 'height': 1100}, reduced_motion='reduce')
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{port}/#t={app.state.security.launch_token}')
                page.locator('#more-menu > summary').click()
                page.get_by_role('link', name='Settings', exact=True).click()
                page.get_by_role('heading', name='Reminders outside Link').wait_for()
                check(page, app)
                browser.close()
        finally:
            server.should_exit = True
            thread.join(10)
        assert not errors, errors


def on_a_mac(page, app):
    box = page.locator('#nudges')
    assert 'never who' in box.inner_text()
    page.get_by_label('Remind me').select_option('on')
    expect(page.get_by_text('companion nudge --install')).to_be_visible()  # tells you how to make it work with Link closed
    assert nudges.get_settings(app.state.db)['enabled'] is True
    page.get_by_label('Time of day').fill('08:30')
    expect(page.get_by_label('Time of day')).to_have_value('08:30')
    assert '9:00 PM to 8:00 AM' in page.locator('#nudges summary').inner_text()
    page.get_by_label('Time of day').fill('23:00')  # inside quiet hours: refused, and the saved time stays
    expect(page.get_by_text('Pick a reminder time outside your quiet hours.')).to_be_visible()
    assert nudges.get_settings(app.state.db)['time'] == '08:30'
    page.get_by_role('button', name='Send a test reminder').click()
    expect(page.get_by_text('Sent. Look for it on your screen.')).to_be_visible()
    assert app.state.sent == [('Link', 'This is a test reminder. Nothing is due.')]
    page.get_by_role('button', name='Pause for 3 days').click()
    expect(page.locator('#nudges .notice[role=status]')).to_contain_text('Paused until')
    page.get_by_role('button', name='Resume reminders', exact=False).click()
    expect(page.get_by_text('Reminders are back on.')).to_be_visible()


def on_another_computer(page, app):
    expect(page.get_by_text('Desktop reminders need a Mac for now.')).to_be_visible()
    page.get_by_role('button', name='Send a test reminder').click()
    expect(page.locator('#nudges .notice[role=status]')).to_contain_text('Mac')


mac = Notifier()
run(8895, mac, lambda page, app: (setattr(app.state, 'sent', mac.sent), on_a_mac(page, app)))
run(8896, nudges.UnsupportedNotifier(), on_another_computer)
print('Reminder settings checks passed: turn on, quiet hours, test reminder, pause and resume, and the message on a computer that cannot show one; no JS errors.')
