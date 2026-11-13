"""Temporary browser verification with synthetic, isolated data. No live API calls."""
import sys, threading, tempfile
from pathlib import Path
import uvicorn
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from companion.app import create_app
from companion.config import Settings
from companion.ai import MockAI
from companion import store
from playwright.sync_api import sync_playwright

import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=Path('/tmp/link-browser-check'))
args=parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
folder=tempfile.TemporaryDirectory(prefix='link-browser-')
settings=Settings(data_dir=Path(folder.name),port=8876,ai_mode='mock')
app=create_app(settings,MockAI())
server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8876,log_level='error',access_log=False))
thread=threading.Thread(target=server.run,daemon=True);thread.start()
import time
for _ in range(50):
    if server.started:break
    time.sleep(.1)
base='http://127.0.0.1:8876'
errors=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1470,'height':956},reduced_motion='reduce')
  page.on('pageerror',lambda err:errors.append(str(err)))
  page.goto(base)
  page.evaluate('''async token => {await fetch('/auth/exchange',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});}''', app.state.security.launch_token)
  page.reload()
  page.wait_for_timeout(800)
  assert not errors, errors
  page.get_by_role('button',name='Explore the workspace first',exact=True).click()
  page.get_by_role('link',name='People',exact=True).first.click()
  page.get_by_role('button',name='Add person',exact=True).first.click()
  page.get_by_label('Name',exact=True).fill('Maya Example')
  page.get_by_role('button',name='Add person',exact=True).last.click()
  page.locator('.person-heading h2').filter(has_text='Maya Example').wait_for()
  page.get_by_role('button',name='Log interaction',exact=True).click()
  page.get_by_label('What do you remember?',exact=True).fill('Met Maya at an event last week. Possibly healthcare. Think I offered to send a project.')
  page.get_by_role('combobox').nth(1).select_option('approx')
  page.get_by_label('Roughly when, in your own words',exact=True).fill('last week')
  page.get_by_role('button',name='Save quick log',exact=True).click()
  page.get_by_text('last week · approximate',exact=True).wait_for()
  page.get_by_role('button',name='Organize with Link',exact=True).click()
  page.get_by_role('button',name='Save reviewed entry',exact=True).wait_for()
  page.get_by_label('Reviewed factual summary',exact=True).fill('Met Maya at an event. Discussed a project.')
  page.get_by_role('button',name='Save reviewed entry',exact=True).click()
  page.get_by_role('link',name='People',exact=True).first.click()
  page.locator('.person-heading h2').filter(has_text='Maya Example').wait_for()
  page.locator('#main').evaluate('(el) => el.scrollTop=0')
  page.screenshot(path=str(args.output/'people-detail.png'),full_page=True)
  page.get_by_text('Quick message editor',exact=True).click()
  page.get_by_label('Context you approve for this message',exact=True).fill('We met at an event and discussed my project.')
  page.get_by_role('button',name='Prepare draft',exact=True).click()
  page.get_by_label('Message draft',exact=True).wait_for()
  page.get_by_role('button',name='← All people',exact=True).click()
  page.get_by_label('Search people',exact=True).fill('Maya')
  page.locator('#main').evaluate('(el) => el.scrollTop=0')
  page.screenshot(path=str(args.output/'people-list.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  page.screenshot(path=str(args.output/'people-mobile.png'),full_page=True)
  print('Browser workflow passed. JS errors:',errors)
  assert not errors
  browser.close()
finally:
 server.should_exit=True
 thread.join(timeout=3)
 app.state.db.close()
 folder.cleanup()
