"""Desktop-only guided journey smoke test. Requires Playwright and local Chromium.

Synthetic records, temporary database, mock AI. No real API calls.
"""
import argparse
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

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=Path('/tmp/link-guided-check'))
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='link-guided-') as folder:
    app=create_app(Settings(data_dir=Path(folder),port=8877,ai_mode='mock'),MockAI())
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8877,access_log=False,log_level='error'))
    thread=threading.Thread(target=server.run,daemon=True)
    thread.start()
    for _ in range(50):
        if server.started: break
        time.sleep(.1)
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1470,'height':956},reduced_motion='reduce')
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8877/#t='+app.state.security.launch_token)
            page.get_by_role('heading',name='Good people. Real possibilities.',exact=True).wait_for()
            page.screenshot(path=str(args.output/'onboarding.png'))
            page.get_by_role('button',name='Find a starting point',exact=True).click()
            page.get_by_label('Tell Link',exact=True).fill("I'm a recent graduate working full time. No campus access, and I'm curious about analytics.")
            page.get_by_role('button',name='Think it through with Link',exact=True).click()
            page.get_by_role('heading',name='Here’s a possible next step.',exact=True).wait_for()
            assert app.state.db.one('SELECT COUNT(*) AS n FROM items')['n'] == 0
            assert app.state.db.one('SELECT COUNT(*) AS n FROM actions')['n'] == 0
            page.get_by_role('button',name='Use the suggested step',exact=True).click()
            page.get_by_role('button',name='Save my plan',exact=True).click()
            page.get_by_text('Saved. No one has been contacted.',exact=True).wait_for()
            assert app.state.db.one('SELECT COUNT(*) AS n FROM actions')['n'] == 1
            page.get_by_role('button',name='Back to Today',exact=True).click()
            page.get_by_role('button',name='I’m stuck — help me choose',exact=True).click()
            page.get_by_role('button',name='Make sense of an encounter',exact=True).click()
            page.get_by_label('Tell Link',exact=True).fill('Met Maya at an event last week. Think I offered to send a project.')
            page.get_by_role('button',name='Think it through with Link',exact=True).click()
            page.get_by_role('heading',name='Here’s a possible next step.',exact=True).wait_for()
            page.get_by_text('Add the person',exact=True).click()
            page.get_by_label('Person name to save',exact=True).fill('Maya Example')
            page.get_by_role('checkbox',name='Save my original recollection',exact=False).check()
            page.get_by_role('button',name='Save my plan',exact=True).click()
            page.get_by_text('Saved. No one has been contacted.',exact=True).wait_for()
            page.get_by_role('button',name='Open person',exact=True).click()
            page.locator('.person-heading h2').filter(has_text='Maya Example').wait_for()
            page.get_by_role('button',name='Help me prepare',exact=True).click()
            page.get_by_label('Tell Link',exact=True).fill('How do analytics teams decide which projects to prioritize?')
            page.get_by_role('button',name='Think it through with Link',exact=True).click()
            page.get_by_role('heading',name='Here’s a possible next step.',exact=True).wait_for()
            page.get_by_text('Practice a short conversation',exact=True).click()
            page.get_by_label('Your practice answer',exact=True).fill("I'm interested in understanding how you choose useful projects.")
            page.get_by_role('button',name='Practice with Link',exact=True).click()
            page.get_by_text('Fictional rehearsal',exact=True).wait_for()
            page.screenshot(path=str(args.output/'preparation.png'))
            page.get_by_text('Prepare a message',exact=True).click()
            page.get_by_label('Context I approve for this message',exact=True).fill('We met at an event and discussed analytics.')
            page.get_by_role('button',name='Generate a message',exact=True).click()
            page.get_by_label('Connection message draft',exact=True).wait_for()
            page.get_by_role('button',name='Save my plan',exact=True).click()
            page.get_by_text('Saved. No one has been contacted.',exact=True).wait_for()
            page.reload()
            page.get_by_role('button',name='Resume plan',exact=True).first.wait_for()
            page.get_by_role('link',name='People',exact=True).first.click()
            page.locator('.person-row').filter(has_text='Maya Example').click()
            page.locator('.person-heading h2').filter(has_text='Maya Example').wait_for()
            page.get_by_role('button',name='Ask for help or an opportunity',exact=True).click()
            page.get_by_label('Tell Link',exact=True).fill('Would you be comfortable discussing a referral, or should I prepare more context first?')
            page.get_by_role('combobox').select_option('referral')
            page.get_by_role('button',name='Think it through with Link',exact=True).click()
            page.get_by_role('heading',name='Here’s a possible next step.',exact=True).wait_for()
            assert app.state.gateway.client.requests[-1].meta['ask_type'] == 'referral'
            page.get_by_text('Prepare a message',exact=True).click()
            assert page.get_by_label('What I want to ask or say',exact=True).input_value().startswith('Discuss a referral:')
            page.locator('#main').evaluate('(el) => el.scrollTop=0')
            page.screenshot(path=str(args.output/'opportunity-plan.png'))
            assert not errors, errors
            assert 'Tempo' not in page.locator('body').inner_text()
            browser.close()
            print('Guided desktop journey passed; no JS errors. No live AI calls.')
    finally:
        server.should_exit=True
        thread.join(timeout=3)
        app.state.db.close()
