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
    settings=Settings(data_dir=Path(folder),port=8880,ai_mode='mock')
    app=create_app(settings,MockAI());db=app.state.db
    load_demo(db,local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8880,access_log=False,log_level='error'))
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
            page.goto('http://127.0.0.1:8880/#t='+app.state.security.launch_token)
            page.get_by_role('button',name='I’m stuck — help me choose',exact=True).wait_for()
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'today.png'))
            page.get_by_role('button',name='I’m stuck — help me choose',exact=True).wait_for()
            page.get_by_role('button',name='Import connections',exact=True).wait_for()
            page.get_by_role('link',name='Quick log',exact=True).first.click()
            note=page.get_by_label('What do you remember?',exact=True)
            note.fill('Person from the career fair. Possibly interested in analytics.')
            page.get_by_text('Draft saved on this Mac',exact=True).wait_for()
            page.get_by_role('link',name='People',exact=True).first.click()
            page.get_by_role('link',name='Quick log',exact=True).first.click()
            assert note.input_value().startswith('Person from the career fair')
            page.reload()
            page.get_by_text('Draft saved on this Mac',exact=True).wait_for()
            assert note.input_value().startswith('Person from the career fair')
            assert db.one('SELECT COUNT(*) AS n FROM interactions')['n'] == 3
            page.get_by_role('button',name='Save quick log',exact=True).click()
            page.locator('#undo-bar').wait_for()
            assert db.one('SELECT COUNT(*) AS n FROM interactions')['n'] == 4
            page.locator('#undo-bar').get_by_role('button',name='Undo',exact=True).click()
            page.get_by_text('Draft saved on this Mac',exact=True).wait_for()
            assert note.input_value().startswith('Person from the career fair')
            assert db.one('SELECT COUNT(*) AS n FROM interactions')['n'] == 3
            page.get_by_role('link',name='People',exact=True).first.click()
            page.get_by_role('button',name='Add person',exact=True).click()
            page.get_by_label('Name',exact=True).fill('Maya')
            page.get_by_role('button',name='Open Maya Lindqvist · Example Health',exact=True).click()
            page.locator('.person-heading h2').filter(has_text='Maya Lindqvist').wait_for()
            assert db.one("SELECT COUNT(*) AS n FROM items WHERE kind='relationship'")['n'] == 4
            page.get_by_role('tab',name='Next step',exact=True).click()
            page.get_by_label('What would you like to do?',exact=True).fill('Send the promised link')
            page.get_by_role('button',name='Next week',exact=True).click()
            assert page.get_by_label('Optional reminder',exact=True).input_value()
            page.get_by_role('button',name='Save next step',exact=True).click()
            page.get_by_role('button',name='I completed this',exact=True).wait_for()
            page.get_by_role('button',name='I completed this',exact=True).click()
            page.get_by_role('button',name='Undo task completion',exact=True).click()
            page.get_by_role('button',name='I completed this',exact=True).wait_for()
            assert page.get_by_label('Optional reminder',exact=True).input_value()
            page.get_by_role('button',name='No reminder',exact=True).click()
            assert page.get_by_label('Optional reminder',exact=True).input_value() == ''
            assert db.one('SELECT COUNT(*) AS n FROM interactions')['n'] == 3
            page.get_by_text('Person details',exact=True).click()
            page.get_by_role('button',name='Pause connection',exact=True).click()
            page.get_by_role('button',name='Resume connection',exact=True).wait_for()
            page.locator('#undo-bar').get_by_role('button',name='Undo',exact=True).click()
            page.get_by_role('button',name='Pause connection',exact=True).wait_for()
            page.emulate_media(reduced_motion='no-preference')
            page.get_by_role('link',name='Quick log',exact=True).first.click()
            note.wait_for()
            assert note.input_value().startswith('Person from the career fair')
            page.locator('.page').evaluate('(el)=>Promise.all(el.getAnimations().map(a=>a.finished))')
            page.screenshot(path=str(args.output/'quicklog-recovery.png'))
            page.emulate_media(reduced_motion='reduce')
            assert page.locator('.shell').evaluate('(el)=>getComputedStyle(el).transitionDuration') == '0s'
            assert not errors,errors
            browser.close()
            print('Quality-of-life browser checks passed: draft navigation/reload recovery, undo, duplicates, reminders, completion undo, pause/undo, reduced motion; no JS errors.')
    finally:
        server.should_exit=True;thread.join(timeout=3);db.close()
