# Link — handoff

The source of truth is this repository, `Danorete/career-companion`. Earlier builds were passed
around as ZIP archives (`link-connection-studio`, `link-avatar-guide`, `link-polished-workflows`,
`link-context-advice`, `link-network-sources`, `link-clear-start`, `link-daily-home`) because pushes
from those sessions were refused. The last of them, `link-daily-home`, is now committed here and
contains everything in the earlier ones. Work from a clone, not from an extracted ZIP.

## Run it on your Mac

Stop any older copy first with Ctrl+C, so an old build isn't still serving the port.

```bash
git clone https://github.com/Danorete/career-companion.git
```

```bash
cd career-companion && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
```

Try it with fictional people and mock AI, in a temporary database that never touches your records:

```bash
.venv/bin/companion run --demo
```

Use your own records (the data folder and Keychain key are unchanged from earlier builds):

```bash
.venv/bin/companion run
```

Add `COMPANION_AI_MODE=live` in front of that command for live AI; see "Turning on live AI" in the
README first. Python 3.11 or newer is required.

To try an empty, persistent workspace without opening your real records:

```bash
COMPANION_DATA_DIR="$HOME/Library/Application Support/LinkStudioPreview" COMPANION_AI_MODE=mock .venv/bin/companion run
```

Back up or export your data before upgrading. The database is at schema version 5; upgrades are
additive and don't delete records. Demo mode removes its temporary folder on a normal shutdown; a
forced kill can leave it behind in the system temporary folder.

## What the current build contains

In the order it was built (details in `PROGRESS.md`, reasons in `DECISIONS.md` D28–D37):

- People, Quick log with approximate dates, next steps, and person-scoped message drafting.
- Guided onboarding and connection workflows: prepare, follow up, ask for help or an opportunity.
- The Connection Studio design: top navigation, People directory with tabs, light and dark themes.
- The Link character, the optional Meet Link walkthrough, and the resizable Link panel.
- Quick log recovery, Undo for common edits, duplicate-name suggestions, reminder shortcuts.
- Private advice no longer turns into an evidence audit.
- Import: LinkedIn connections CSV, selected message excerpts and `.ics` calendar files, all parsed
  locally and reviewed before anything is saved.
- Today and Import are separate: Today resumes your work, Import holds the source catalogue.
- From `claude/less-friction`: job postings on roles, résumé-to-evidence extraction, "Confirm all".

## Checks and what is still unverified

199 Python tests pass on Linux, Python 3.12 (2026-11-13). The browser checks in `scripts/` are
described at the end of `README.md`; history of each run is in `VALIDATION.md`.

Never tested: a real call to the AI provider, provider billing against the app's own ledger, macOS,
Safari and the Keychain. Phone-width layout is deferred. Mock AI only so far.

## Open threads

- `claude/connections-redesign` is a separate, unmerged People and Quick log implementation, built in
  parallel with this one. This build doesn't include it. Compare the two before deleting either branch.
- `graphify-out/` was rebuilt on 2026-11-13 from code only. Docs and images aren't in it yet; run
  `/graphify --update` in an assistant session to add them.
