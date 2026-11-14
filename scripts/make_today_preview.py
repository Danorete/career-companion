"""Regenerate static/today-preview.webp, the Today screenshot shown on first run.

Uses the fictional demo data in a temporary database with mock AI, so no personal data can end up in the image.
Needs Playwright, a Chromium build (set CHROMIUM_PATH if it is not at /usr/bin/chromium) and ImageMagick's
`convert`. Run it after changing Today's design.
"""
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import uvicorn
from playwright.sync_api import sync_playwright
from companion.app import create_app
from companion.config import Settings
from companion.ai import MockAI
from companion.people import load_demo
from companion.services import local_today

OUT = ROOT / 'src' / 'companion' / 'static' / 'today-preview.webp'

with tempfile.TemporaryDirectory(prefix='link-preview-') as folder:
    settings = Settings(data_dir=Path(folder), port=8896, ai_mode='mock')
    app = create_app(settings, MockAI())
    db = app.state.db
    load_demo(db, local_today(settings))
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('onboarding_step','2')")
    db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8896, log_level='error'))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(.1)
    png = Path(folder) / 'today.png'
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
        page.add_init_script("localStorage.setItem('cc.dockOpen','false')")
        page.goto('http://127.0.0.1:8896/#t=' + app.state.security.launch_token)
        page.locator('.today-grid .hero h2').wait_for()
        page.wait_for_timeout(800)
        page.evaluate("document.querySelectorAll('.guide-launcher,.dock-pill,#toast,.demo-label').forEach(e => e.style.visibility = 'hidden')")
        page.screenshot(path=str(png))
        browser.close()
    server.should_exit = True
    subprocess.run(['convert', str(png), '-resize', '1120x700', '-quality', '82', str(OUT)], check=True)
print('Wrote', OUT)
