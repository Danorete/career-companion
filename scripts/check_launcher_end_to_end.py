"""The launcher against a real background server (decision D47). No browser: the "browser" is a list.

Starts Link for real on a spare port with a temporary data folder and mock AI, signs in with the link the launcher
mints, and stops it again. Touches no personal data.
"""
import os
import stat
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import httpx
from companion import launcher
from companion.config import Settings

PORT = 8899
with tempfile.TemporaryDirectory(prefix='link-launch-') as folder:
    os.environ.update(COMPANION_DATA_DIR=folder, COMPANION_PORT=str(PORT), COMPANION_AI_MODE='mock')
    # The server we start must import this copy of the code.
    os.environ['PYTHONPATH'] = str(Path(__file__).resolve().parents[1] / 'src') + os.pathsep + os.environ.get('PYTHONPATH', '')
    settings = Settings.from_env()
    base = f'http://127.0.0.1:{PORT}'
    opened = []
    try:
        assert launcher.ask_for_link(base, None) is None, 'the port should start free'
        code, message = launcher.launch(settings, opener=opened.append)
        assert code == 0 and len(opened) == 1, (code, message)
        first = opened[0].split('#t=')[1]
        assert stat.S_IMODE(launcher.key_path(Path(folder)).stat().st_mode) == 0o600

        with httpx.Client(base_url=base, trust_env=False) as client:
            assert client.post('/auth/exchange', json={'token': first}, headers={'origin': base}).status_code == 200
            assert client.get('/api/bootstrap').status_code == 200            # signed in with the minted link
            assert client.post('/auth/exchange', json={'token': first}, headers={'origin': base}).status_code == 403  # works once
        code, _ = launcher.launch(settings, opener=opened.append)              # already running: a second fresh link, no second server
        assert code == 0 and opened[1] != opened[0]
        log = (Path(folder) / 'link.log').read_text(errors='replace')
        assert '#t=' not in log and first not in log, 'a sign-in link must never be written to the log'

        code, message = launcher.quit_running(settings)
        assert (code, message) == (0, 'Link has stopped.'), (code, message)
        for _ in range(50):
            if launcher.ask_for_link(base, None) is None:
                break
            time.sleep(.1)
        else:
            raise AssertionError('Link was still answering after Quit')
        assert launcher.quit_running(settings) == (0, "Link wasn't running.")
    finally:
        launcher.quit_running(settings)  # never leave a server behind
print('Launcher checks passed: started in the background, signed in once with a minted link, no link in the log, and stopped on Quit.')
