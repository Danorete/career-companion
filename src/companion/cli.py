"""Command line entry point: `companion run`, `companion set-key`, `companion delete-key`, `companion status`."""

from __future__ import annotations

import argparse
import getpass
import logging
import sys
import webbrowser

from .config import Settings


def _tip_if_client_file_is_open() -> None:
    import os
    import stat

    path = os.environ.get("COMPANION_GOOGLE_CLIENT_FILE")
    try:
        if path and os.stat(os.path.expanduser(path)).st_mode & (stat.S_IRWXG | stat.S_IRWXO):
            print(f"  Tip: other users on this computer can read {path}. Run: chmod 600 {path}")
    except OSError:
        pass


def _run(args: argparse.Namespace) -> int:
    import uvicorn

    from .app import create_app

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    try:
        settings = Settings.from_env()
    except ValueError as exc:
        print(f"Can't start: {exc}")
        return 2
    _tip_if_client_file_is_open()
    if args.mode:
        from dataclasses import replace as _replace
        settings = _replace(settings, ui_mode=args.mode)
    demo_dir = None
    if args.demo:
        import tempfile
        from dataclasses import replace
        from pathlib import Path
        demo_dir = tempfile.TemporaryDirectory(prefix="link-demo-")
        settings = replace(settings, data_dir=Path(demo_dir.name), ai_mode="mock")
    app = create_app(settings)
    if args.demo:
        from .people import load_demo
        from .services import local_today
        load_demo(app.state.db, local_today(settings))
        app.state.db.run("INSERT OR REPLACE INTO kv(key,value) VALUES('demo_mode','1')")
    ai = app.state.gateway.availability()
    if args.background:
        # Started by `companion launch`: no printed link (so none lands in a log) and the first link is closed.
        app.state.security.revoke_initial_token()
        print(f"Link is running in the background on port {settings.port}. Data folder: {settings.data_dir}", flush=True)
    else:
        url = f"http://{settings.host}:{settings.port}/#t={app.state.security.launch_token}"
        print("Link — Connection Studio" + (" [FICTIONAL DEMO]" if args.demo else ""))
        print(f"  Data folder : {settings.data_dir}")
        print(f"  AI          : {ai['mode']} ({ai['reason']})")
        print(f"  Version     : {'developer' if settings.ui_mode == 'dev' else 'user'} ({settings.ui_mode})")
        print(f"  Open        : {url}")
        print("  The link works once. Restart the app to get a new one. Press Ctrl+C to stop, or use Quit Link in the Menu.")
        if not args.no_browser:
            webbrowser.open(url)
    # Access logging is off: request lines are not needed and logs stay free of personal data.
    import os
    import signal

    app.state.request_shutdown = lambda: os.kill(os.getpid(), signal.SIGINT)  # the same clean stop as pressing Ctrl+C
    try:
        uvicorn.run(app, host=settings.host, port=settings.port, access_log=False, log_level="warning")
    finally:
        app.state.db.close()
        if demo_dir is not None:
            demo_dir.cleanup()
    return 0


def _launch(_: argparse.Namespace) -> int:
    from . import launcher

    try:
        settings = Settings.from_env()
    except ValueError as exc:
        print(f"Can't start: {exc}")
        return 2
    code, message = launcher.launch(settings)
    print(message)
    return code


def _quit(_: argparse.Namespace) -> int:
    from . import launcher

    try:
        settings = Settings.from_env()
    except ValueError as exc:
        print(f"Settings problem: {exc}")
        return 2
    code, message = launcher.quit_running(settings)
    print(message)
    return code


def _launcher(args: argparse.Namespace) -> int:
    """Install or remove the one-click Mac app."""
    from pathlib import Path

    from . import launcher

    try:
        settings = Settings.from_env()
    except ValueError as exc:
        print(f"Can't start: {exc}")
        return 2
    home = Path.home()
    if args.uninstall:
        print(launcher.uninstall(home))
    elif args.status:
        print(f"Link.app installed: {'yes' if launcher.is_installed(home) else 'no'}")
    else:
        print(launcher.install(home, settings.data_dir))
    return 0


def _nudge(args: argparse.Namespace) -> int:
    """One pass of the reminder helper, or install and remove it. Output is counts only, never names."""
    from datetime import datetime
    from pathlib import Path

    from . import nudge_agent, nudges
    from .db import Database

    try:
        settings = Settings.from_env()
    except ValueError as exc:
        print(f"Can't start: {exc}")
        return 2
    home = Path.home()
    if args.install:
        print(nudge_agent.install(home, settings.data_dir / "nudge.log"))
        return 0
    if args.uninstall:
        print(nudge_agent.uninstall(home))
        return 0
    if args.status:
        print(f"Helper installed: {'yes' if nudge_agent.is_installed(home) else 'no'}")
        return 0
    db = Database(settings.db_path)
    try:
        result = nudges.run_once(db, nudges.build_notifier(), nudges.local_now(settings), dry_run=args.dry_run)
    finally:
        db.close()
    print(f"{datetime.now().isoformat(timespec='minutes')} sent={result['sent']} count={result['count']} reason={result['reason']}")
    return 0


def _set_key(_: argparse.Namespace) -> int:
    from .keys import set_api_key

    value = getpass.getpass("Paste your API key (input is hidden): ").strip()
    if not value:
        print("Nothing entered. No change.")
        return 1
    set_api_key(value)
    print("Saved to the system keychain. It is never written to a file or shown in the browser.")
    return 0


def _delete_key(_: argparse.Namespace) -> int:
    from .keys import delete_api_key

    delete_api_key()
    print("API key removed from the keychain.")
    return 0


def _status(_: argparse.Namespace) -> int:
    from .budget import PRICES_VERIFIED_ON, prices_are_fresh
    from .keys import get_api_key

    try:
        settings = Settings.from_env()
    except ValueError as exc:
        print(f"Settings problem : {exc}")
        return 2
    print(f"Data folder      : {settings.data_dir}")
    print(f"Google Calendar  : {'sign-in settings found' if settings.google_client_id else 'not set up'}")
    print(f"AI mode          : {settings.ai_mode}")
    print(f"API key stored   : {'yes' if get_api_key() else 'no'}")
    print(f"Prices verified  : {PRICES_VERIFIED_ON} ({'current' if prices_are_fresh() else 'STALE: re-verify'})")
    print(f"Budget           : ${settings.hard_stop_usd:.0f} stop within ${settings.monthly_budget_usd:.0f} a month")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="companion", description="Link (local connection companion, single user)")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run", help="start the app and open the browser")
    run.add_argument("--no-browser", action="store_true")
    run.add_argument("--background", action="store_true", help="used by the launcher: no browser, no printed link")
    run.add_argument("--mode", choices=("user", "dev"), help="user: plain wording for testers (default). dev: developer controls and original wording")
    run.add_argument("--demo", action="store_true", help="use temporary fictional data and mock AI; never opens your personal database")
    run.set_defaults(func=_run)
    sub.add_parser("launch", help="open Link in your browser, starting it quietly first if it isn't running").set_defaults(func=_launch)
    sub.add_parser("quit", help="stop a running Link").set_defaults(func=_quit)
    one_click = sub.add_parser("launcher", help="install or remove Link.app, a one-click way to open Link (Mac)")
    one_click_group = one_click.add_mutually_exclusive_group()
    one_click_group.add_argument("--uninstall", action="store_true", help="remove Link.app")
    one_click_group.add_argument("--status", action="store_true", help="say whether Link.app is installed")
    one_click.set_defaults(func=_launcher)
    nudge = sub.add_parser("nudge", help="show today's reminder if one is due, or install or remove the helper that does it")
    nudge.add_argument("--dry-run", action="store_true", help="say what would happen without showing anything")
    group = nudge.add_mutually_exclusive_group()
    group.add_argument("--install", action="store_true", help="install the helper (a Mac login agent that checks every 15 minutes)")
    group.add_argument("--uninstall", action="store_true", help="remove the helper")
    group.add_argument("--status", action="store_true", help="say whether the helper is installed")
    nudge.set_defaults(func=_nudge)
    sub.add_parser("set-key", help="store the API key in the system keychain").set_defaults(func=_set_key)
    sub.add_parser("delete-key", help="remove the API key").set_defaults(func=_delete_key)
    sub.add_parser("status", help="show configuration without starting").set_defaults(func=_status)
    args = parser.parse_args(argv)
    if not args.command:
        args = parser.parse_args(["run"])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
