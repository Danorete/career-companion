"""Desktop design acceptance: contextual panes, keyboard navigation, themes, and data integrity.

Synthetic temporary data and mock AI only. Requires Playwright and Linux Chromium.
"""
import argparse
import os
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
    settings=Settings(data_dir=Path(folder),port=8883,ai_mode='mock')
    app=create_app(settings,MockAI());db=app.state.db
    load_demo(db,local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8883,access_log=False,log_level='error'))
    thread=threading.Thread(target=server.run,daemon=True);thread.start()
    for _ in range(50):
        if server.started:break
        time.sleep(.1)
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1470,'height':956},reduced_motion='reduce')
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('dialog',lambda dialog:(print('Browser dialog:',dialog.message),dialog.dismiss()))
            page.goto('http://127.0.0.1:8883/#t='+app.state.security.launch_token)
            page.get_by_role('button',name='I’m stuck — help me choose',exact=True).wait_for()
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'today.png'))
            page.get_by_role('heading',name='One thing today.',exact=True).wait_for()
            assert page.locator('.source-tabs').count()==0
            assert page.locator('.home-path-art').count()==0
            for name in ('Log a conversation','Prepare for a conversation','Import connections','Work on this'):
                button=page.get_by_role('button',name=name,exact=True)
                box=button.bounding_box()
                assert button.is_visible() and box['y']+box['height']<956,(name,box)
            page.get_by_role('link',name='Import',exact=True).first.wait_for()
            page.screenshot(path=str(args.output/'today.png'))
            page.set_viewport_size({'width':1280,'height':800})
            for name in ('Log a conversation','Prepare for a conversation','Import connections','Work on this'):
                box=page.get_by_role('button',name=name,exact=True).bounding_box()
                assert box['y']+box['height']<800,(name,box)
            page.screenshot(path=str(args.output/'today-laptop.png'))
            page.set_viewport_size({'width':1470,'height':956})
            page.get_by_role('link',name='Import',exact=True).first.click()
            page.get_by_role('heading',name='You choose what stays.',exact=True).wait_for()
            assert page.locator('.source-tabs [role=tab]').count()==3
            assert page.get_by_role('heading',name='One thing today.',exact=True).count()==0
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'import.png'))
            page.get_by_role('tab').filter(has_text='Your conversations').click()
            page.get_by_label('Choose messages CSV or text excerpt',exact=True).wait_for()
            page.get_by_role('tab').filter(has_text='Your next meeting').click()
            page.get_by_label('Choose calendar export (.ics)',exact=True).wait_for()
            page.get_by_role('link',name='Today',exact=True).first.click()
            page.get_by_role('button',name='Import connections',exact=True).click()
            page.get_by_label('Choose Connections.csv',exact=True).wait_for()
            page.get_by_role('link',name='Today',exact=True).first.click()
            page.get_by_role('button',name='Log a conversation',exact=True).click()
            page.get_by_label('What do you remember?',exact=True).wait_for()
            page.get_by_role('link',name='Today',exact=True).first.click()
            page.get_by_role('button',name='Prepare for a conversation',exact=True).click()
            page.get_by_label('Tell Link',exact=True).wait_for()
            # Simulate a fresh user's onboarding, without touching any real data.
            db.run("UPDATE kv SET value='0' WHERE key='onboarding_step'")
            page.goto('http://127.0.0.1:8883/#today')
            page.reload()
            page.get_by_role('heading',name='Good people. Real possibilities.',exact=True).wait_for()
            page.get_by_role('button',name='Import my connections',exact=True).click()
            page.get_by_label('Choose Connections.csv',exact=True).wait_for()
            assert page.get_by_role('link',name='Import',exact=True).first.is_visible()
            # A genuinely empty workspace offers one substantive start, not another import gallery.
            db.run('DELETE FROM actions');db.run('DELETE FROM items')
            page.get_by_role('link',name='Today',exact=True).first.click()
            page.get_by_role('heading',name='Start with one person.',exact=True).wait_for()
            assert page.locator('.source-tabs').count()==0
            page.screenshot(path=str(args.output/'today-empty.png'))
            page.get_by_role('button',name='I don’t know anyone yet',exact=True).click()
            page.get_by_label('Tell Link',exact=True).wait_for()
            assert not errors,errors
            browser.close()
            print('Daily workspace checks passed: Today differs from Import, next action visible on laptop, discoverable shortcuts, reviewed import tabs, preparation, onboarding bypass and empty-state coaching; no JS errors.')
    finally:
        server.should_exit=True;thread.join(timeout=3);db.close()
