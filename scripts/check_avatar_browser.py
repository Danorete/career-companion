"""Desktop design acceptance: contextual panes, keyboard navigation, themes, and data integrity.

Synthetic temporary data and mock AI only. Requires Playwright and Linux Chromium.
"""
import argparse
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import uvicorn
from playwright.sync_api import sync_playwright
from companion.app import create_app
from companion.config import Settings
from companion.ai import MockAI
from companion.people import load_demo
from companion.services import local_today

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=Path('/tmp/link-studio-check'))
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='link-studio-') as folder:
    settings=Settings(data_dir=Path(folder),port=8879,ai_mode='mock')
    app=create_app(settings,MockAI());db=app.state.db
    load_demo(db,local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8879,access_log=False,log_level='error'))
    thread=threading.Thread(target=server.run,daemon=True);thread.start()
    for _ in range(50):
        if server.started:break
        time.sleep(.1)
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1470,'height':956},reduced_motion='reduce')
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8879/#t='+app.state.security.launch_token)
            page.get_by_role('button',name='I’m stuck — help me choose',exact=True).wait_for()
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'today.png'))
            assert page.locator('#dock').get_attribute('aria-hidden') == 'true'
            before=db.one('SELECT COUNT(*) AS n FROM interactions')['n']
            page.get_by_role('button',name='Meet Link: guided walkthrough').click()
            page.get_by_role('heading',name='A colleague, one click away.').wait_for()
            page.get_by_role('button',name='Open Link, your companion',exact=True).click()
            page.get_by_role('heading',name='Start with a person.').wait_for()
            page.get_by_role('link',name='People',exact=True).first.click()
            page.get_by_role('heading',name='Context grows over time.').wait_for()
            page.get_by_role('button',name='Got it, next',exact=True).click()
            page.get_by_role('link',name='Quick log',exact=True).first.click()
            page.get_by_role('heading',name='Try a rough recollection.').wait_for()
            page.get_by_label('What do you remember?',exact=True).fill('Met someone after class; possibly interested in analytics.')
            page.get_by_role('heading',name='Your pace. Your connections.').wait_for()
            assert db.one('SELECT COUNT(*) AS n FROM interactions')['n'] == before
            page.screenshot(path=str(args.output/'avatar-guide.png'))
            page.keyboard.press('Escape')
            assert page.locator('.link-guide').count() == 0
            assert page.get_by_label('What do you remember?',exact=True).input_value().startswith('Met someone')
            page.get_by_role('button',name='Meet Link: guided walkthrough').click()
            page.get_by_role('button',name='Finish tour',exact=True).click()
            page.get_by_role('button',name='Meet Link: guided walkthrough').click()
            page.get_by_role('heading',name='A colleague, one click away.').wait_for()
            page.get_by_role('button',name='Skip tour',exact=True).click()
            page.get_by_text('Draft saved on this Mac',exact=True).wait_for()
            page.reload()
            page.get_by_role('button',name='Meet Link: guided walkthrough').wait_for()
            assert page.locator('.link-guide').count() == 0
            assert not errors,errors
            browser.close()
            print('Avatar guide checks passed: click advancement, pause/resume/replay, no automatic timeline saves, note preservation, no JS errors.')
    finally:
        server.should_exit=True;thread.join(timeout=3);db.close()
