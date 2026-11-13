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
    settings=Settings(data_dir=Path(folder),port=8878,ai_mode='mock')
    app=create_app(settings,MockAI());db=app.state.db
    load_demo(db,local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8878,access_log=False,log_level='error'))
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
            page.goto('http://127.0.0.1:8878/#t='+app.state.security.launch_token)
            page.get_by_role('button',name='I’m stuck — help me choose',exact=True).wait_for()
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'today.png'))
            sessions_before=db.one('SELECT COUNT(*) AS n FROM sessions')['n']
            page.get_by_role('button',name='Work on this',exact=True).click()
            page.get_by_label('Tell Link',exact=True).wait_for()
            assert db.one('SELECT COUNT(*) AS n FROM sessions')['n'] == sessions_before
            page.get_by_role('link',name='Today',exact=True).first.click()
            page.get_by_role('button',name='Work on this',exact=True).wait_for()
            page.get_by_role('link',name='People',exact=True).first.click()
            page.locator('.person-row').filter(has_text='Jordan Abara').click()
            page.locator('.person-heading h2').filter(has_text='Jordan Abara').wait_for()
            assert page.locator('.person-row').count() == 4
            jordan=page.locator('.person-row').filter(has_text='Jordan Abara')
            jordan.focus();jordan.press('ArrowDown');page.keyboard.press('Enter')
            page.locator('.person-heading h2').filter(has_text='Maya Lindqvist').wait_for()
            assert '[object HTMLElement]' not in page.locator('body').inner_text()
            page.get_by_role('tab',name='Overview',exact=True).focus()
            page.keyboard.press('ArrowRight')
            page.get_by_role('tab',name='Conversations',exact=True).wait_for()
            page.get_by_text('Possibly works in healthcare.',exact=False).wait_for()
            page.get_by_role('tab',name='Conversations',exact=True).focus();page.keyboard.press('ArrowRight')
            page.get_by_label('What would you like to do?',exact=True).fill('Review whether I offered a project link')
            before=db.one('SELECT COUNT(*) AS n FROM interactions')['n']
            page.get_by_role('button',name='Save next step',exact=True).click()
            page.get_by_role('button',name='I completed this',exact=True).click()
            page.get_by_role('button',name='Undo task completion',exact=True).wait_for()
            assert db.one('SELECT COUNT(*) AS n FROM interactions')['n'] == before
            page.get_by_role('button',name='Undo task completion',exact=True).click()
            page.get_by_role('button',name='I completed this',exact=True).wait_for()
            page.get_by_role('tab',name='Overview',exact=True).click()
            page.get_by_role('button',name='Think with Link',exact=True).click()
            page.get_by_label('Message Link',exact=True).wait_for()
            assert page.locator('#dock').get_attribute('aria-hidden') == 'false'
            old=page.locator('#dock').bounding_box()['width']
            page.get_by_role('separator',name='Resize companion panel',exact=True).focus()
            page.keyboard.press('ArrowLeft')
            assert page.locator('#dock').bounding_box()['width'] > old
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'people-with-link.png'))
            page.get_by_role('button',name='Collapse companion panel',exact=True).click()
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'people.png'))
            assert page.locator('a[href="https://www.streamlinehq.com/icons/guidance"]').count() > 0
            page.evaluate("localStorage.setItem('cc.theme',JSON.stringify('dark'))")
            page.reload()
            page.locator('.person-row').filter(has_text='Maya Lindqvist').click()
            page.locator('.person-heading h2').filter(has_text='Maya Lindqvist').wait_for()
            assert page.locator('html').get_attribute('data-theme') == 'dark'
            assert page.locator('#main').evaluate('(el)=>getComputedStyle(el).backgroundColor') == 'rgb(25, 38, 31)'
            page.screenshot(path=str(args.output/'people-dark.png'))
            page.set_viewport_size({'width':1280,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert page.locator('#main').evaluate('(el)=>el.scrollWidth <= el.clientWidth + 1')
            page.get_by_role('link',name='Quick log',exact=True).first.click()
            page.get_by_label('What do you remember?',exact=True).fill('A synthetic design check. No real personal data.')
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'quick-log-dark.png'))
            assert not errors,errors
            browser.close()
            print('Studio desktop checks passed: tabs, keyboard directory, next-step undo, no false contact, dock resizing, both themes, attribution, and layout. No JS errors.')
    finally:
        server.should_exit=True;thread.join(timeout=3);db.close()
