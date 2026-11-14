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
    settings=Settings(data_dir=Path(folder),port=8882,ai_mode='mock')
    app=create_app(settings,MockAI());db=app.state.db
    load_demo(db,local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8882,access_log=False,log_level='error'))
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
            page.goto('http://127.0.0.1:8882/#t='+app.state.security.launch_token)
            page.get_by_role('button',name='I’m stuck — help me choose',exact=True).wait_for()
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'today.png'))
            page.get_by_role('link',name='People',exact=True).first.click()
            page.get_by_role('button',name='Import connections',exact=True).click()
            page.get_by_role('heading',name='You choose what stays.',exact=True).wait_for()
            assert page.get_by_role('tab').count()==3
            assert page.locator('.network-art').count()==3
            for img in page.locator('.network-art').all():
                assert img.evaluate('(el)=>el.complete && el.naturalWidth>0')
            ledger_before=db.one('SELECT COUNT(*) n FROM ledger')['n']
            csv_text='First Name,Last Name,URL,Email Address,Company,Position,Connected On\nAvery,Example,https://www.linkedin.com/in/avery-example,PRIVATE_EMAIL@example.test,Example Co,Analyst,13 Nov 2026\nMaya,Lindqvist,https://www.linkedin.com/in/maya-example,,Different Export Org,Analyst,12 Nov 2026\n'
            page.get_by_label('Choose Connections.csv',exact=True).set_input_files({'name':'Connections.csv','mimeType':'text/csv','buffer':csv_text.encode()})
            try:
                page.locator('.network-review').wait_for(timeout=10000)
            except Exception:
                print('JS errors:',errors)
                print('Workspace:',page.locator('#main').inner_text())
                print('Toast:',page.locator('#toast').inner_text())
                raise
            page.get_by_label('Import choice for Avery Example',exact=True).wait_for(timeout=3000)
            assert db.one("SELECT COUNT(*) n FROM items WHERE kind='relationship'")['n']==4
            assert 'PRIVATE_EMAIL@example.test' not in page.locator('#main').inner_text()
            page.get_by_label('Import choice for Avery Example',exact=True).select_option('add')
            maya_id=db.one("SELECT id FROM items WHERE title='Maya Lindqvist'")['id']
            page.get_by_label('Import choice for Maya Lindqvist',exact=True).select_option('match:'+str(maya_id))
            page.get_by_role('button',name='Confirm selected connections',exact=True).click()
            page.get_by_text('1 person added · 1 reviewed update',exact=False).wait_for()
            assert db.one("SELECT COUNT(*) n FROM items WHERE kind='relationship'")['n']==5
            assert db.one("SELECT org FROM items WHERE id=?",(maya_id,))['org']=='Example Health'
            assert db.one('SELECT COUNT(*) n FROM interactions')['n']==3
            page.get_by_role('tab').filter(has_text='Your conversations').click()
            msg='FROM,TO,DATE,CONTENT\nAvery Example,User,2026-11-12,Maybe I can review your project.\nUnrelated Person,Other User,2026-11-13,DO_NOT_RETAIN\n'
            page.get_by_label('Choose messages CSV or text excerpt',exact=True).set_input_files({'name':'messages.csv','mimeType':'text/csv','buffer':msg.encode()})
            page.get_by_label('Include message 1',exact=True).check()
            page.get_by_label('Your conversation recap',exact=True).fill('Avery may have offered a review. I should check what we agreed.')
            page.get_by_label('Person (optional)',exact=True).select_option(str(maya_id))
            page.get_by_role('button',name='Save selected conversation',exact=True).click()
            page.get_by_text('Recap saved.',exact=False).wait_for()
            saved=db.one("SELECT * FROM interactions ORDER BY id DESC LIMIT 1")
            assert saved['item_id']==maya_id and saved['exchange']=='' and saved['when_kind']=='unknown'
            page.get_by_role('tab').filter(has_text='Your next meeting').click()
            ics='BEGIN:VCALENDAR\nBEGIN:VEVENT\nSUMMARY:Coffee with Avery\nDTSTART;TZID=America/New_York:20261116T100000\nDESCRIPTION:Discuss dashboards\nLOCATION:Campus lounge\nEND:VEVENT\nEND:VCALENDAR'
            page.get_by_label('Choose calendar export (.ics)',exact=True).set_input_files({'name':'meeting.ics','mimeType':'text/calendar','buffer':ics.encode()})
            page.get_by_role('button',name='Prepare for this conversation',exact=True).wait_for()
            assert db.one('SELECT COUNT(*) n FROM interactions')['n']==4
            assert db.one('SELECT COUNT(*) n FROM ledger')['n']==ledger_before
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'sources-calendar.png'))
            page.get_by_role('button',name='Prepare for this conversation',exact=True).click()
            page.get_by_label('Tell Link',exact=True).wait_for()
            assert db.one('SELECT COUNT(*) n FROM interactions')['n']==4
            page.get_by_role('link',name='People',exact=True).first.click()
            page.locator('.person-row').filter(has_text='Avery Example').click()
            page.get_by_text('LinkedIn snapshot · source details',exact=True).click()
            page.get_by_text('Role at export: Analyst',exact=False).wait_for()
            page.get_by_label('How do you know this person?',exact=True).fill('We met at a campus event; I am unsure whether I offered a project link.')
            page.get_by_role('button',name='Save private context',exact=True).click()
            page.get_by_label('How do you know this person?',exact=True).wait_for(state='detached')
            assert 'campus event' in db.one("SELECT private_notes FROM items WHERE title='Avery Example'")['private_notes']
            assert db.one('SELECT COUNT(*) n FROM interactions')['n']==4
            page.get_by_role('button',name='Import connections',exact=True).click()
            page.get_by_role('tab').filter(has_text='Your people').click()
            page.locator('#main').evaluate('(el)=>el.scrollTop=0')
            page.screenshot(path=str(args.output/'sources-overview.png'))
            page.get_by_role('tab').filter(has_text='Your people').focus();page.keyboard.press('ArrowRight')
            assert page.get_by_role('tab').filter(has_text='Your conversations').get_attribute('aria-selected')=='true'
            page.evaluate("localStorage.setItem('cc.theme',JSON.stringify('dark'))")
            page.reload()
            page.get_by_role('heading',name='You choose what stays.',exact=True).wait_for()
            page.screenshot(path=str(args.output/'sources-dark.png'))
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not errors,errors
            browser.close()
            print('Networking sources browser checks passed: imagery, CSV preview/confirmation, explicit matching, selected recap, calendar preparation without attendance, source labels, keyboard tabs, dark theme; no JS errors.')
    finally:
        server.should_exit=True;thread.join(timeout=3);db.close()
