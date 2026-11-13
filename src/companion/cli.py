"""Command line entry point: `companion run`, `companion set-key`, `companion delete-key`, `companion status`."""

from __future__ import annotations

import argparse
import getpass
import logging
import sys
import webbrowser

from .config import Settings


def _run(args: argparse.Namespace) -> int:
    import uvicorn

    from .app import create_app

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    settings = Settings.from_env()
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
    url = f"http://{settings.host}:{settings.port}/#t={app.state.security.launch_token}"
    ai = app.state.gateway.availability()
    print("Link — Connection Studio" + (" [FICTIONAL DEMO]" if args.demo else ""))
    print(f"  Data folder : {settings.data_dir}")
    print(f"  AI          : {ai['mode']} ({ai['reason']})")
    print(f"  Open        : {url}")
    print("  The link works once. Restart the app to get a new one. Press Ctrl+C to stop.")
    if not args.no_browser:
        webbrowser.open(url)
    # Access logging is off: request lines are not needed and logs stay free of personal data.
    try:
        uvicorn.run(app, host=settings.host, port=settings.port, access_log=False, log_level="warning")
    finally:
        app.state.db.close()
        if demo_dir is not None:
            demo_dir.cleanup()
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

    settings = Settings.from_env()
    print(f"Data folder      : {settings.data_dir}")
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
    run.add_argument("--demo", action="store_true", help="use temporary fictional data and mock AI; never opens your personal database")
    run.set_defaults(func=_run)
    sub.add_parser("set-key", help="store the API key in the system keychain").set_defaults(func=_set_key)
    sub.add_parser("delete-key", help="remove the API key").set_defaults(func=_delete_key)
    sub.add_parser("status", help="show configuration without starting").set_defaults(func=_status)
    args = parser.parse_args(argv)
    if not args.command:
        args = parser.parse_args(["run"])
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
