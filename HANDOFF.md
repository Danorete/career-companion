# Link — Connection Studio

This is the complete working app with the approved desktop design, guided connection workflows,
and the earlier People/Quick log redesign. It is not a standalone mockup.

## Preview on your Mac

1. Stop the previous app with Ctrl+C.
2. Extract the ZIP into a NEW folder. It is named `link-connection-studio`.
3. Run the following. The `&&` guards stop subsequent commands if the folder or setup fails,
   so an older app cannot accidentally be launched from the previous working directory.

```bash
cd ~/Downloads/link-connection-studio &&
python3 -m venv .venv &&
.venv/bin/pip install -e ".[dev]" &&
.venv/bin/companion run --demo
```

Python 3.11+ is supported. On this user's Mac, Python 3.13 is already available. Open the freshly
printed browser link. The terminal/browser title says **Link — Connection Studio**.

Demo uses fictional people in a separate temporary database and always forces mock AI. No personal
database or credentials are included or opened. Stop with Ctrl+C. Normal shutdown removes demo data;
a forced kill can leave the isolated temporary folder behind.

To use an EMPTY, persistent preview without opening your original records:

```bash
COMPANION_DATA_DIR="$HOME/Library/Application Support/LinkStudioPreview" COMPANION_AI_MODE=mock .venv/bin/companion run
```

Before ordinary use with your original records, back up/export your database. This design pass adds
no migration beyond the prior schema v5. Do not overwrite your original source folder or the paused
Claude Code working tree; compare and integrate after preserving both versions.

## What changed

- Framed warm-paper layout, editorial serif headings, forest accents and a matching dark theme.
- Top navigation; compact People directory with Overview/Conversations/Next step tabs.
- Two-part onboarding and plan review; quieter Quick log; expandable/resizable Link panel.
- Work without a compulsory timer; focus sessions remain optional.
- Locally bundled Guidance icons (CC BY 4.0), attribution in the interface and source license file.

## Checks and limits

170 automated Python tests passed on Linux/Python 3.12. People, guided workflow, and new studio
browser checks passed in Chromium. No JS errors; syntax and whitespace checks passed. No paid API
calls. Live model behavior, Safari, Keychain and macOS installation still need local verification.
Motion honors reduced-motion preferences. Mobile capture and a hosted multi-user version are deferred.

GitHub write access previously returned 403. This archive contains the local implementation; no
remote PR publication is implied. `PROGRESS.md`, decisions D28-D30 and `VALIDATION.md` document
resume points. Graphify was not installed, so its graph update could not run.

## Latest delivery: link-avatar-guide
Latest source adds the Link character and optional interactive desktop walkthrough. Unzip into its own folder; stop the old server before launching. Existing personal application data remains outside this source folder. `companion run --demo` uses isolated sample data and mock AI. No database migration is needed. No GitHub push was performed.


## Latest delivery: link-polished-workflows
Contains avatar/guide and quality-of-life update. Stop the old server and launch this extracted folder. Normal launch uses existing app data; --demo remains isolated mock mode. No schema migration. Draft protection covers the main Quick log recap; other forms retain their existing behavior. Undo history is session-local, one latest common edit, with explicit permanent-delete exceptions. No GitHub push performed. macOS/Safari/live AI verification remains pending.

## Latest delivery: link-context-advice
Includes all earlier UI/workflow improvements plus the private-chat scope fix. Use the same Keychain key and data directory; no migration or re-import required. Stop the old server, install from this folder and launch with COMPANION_AI_MODE=live (without --demo). Local files and GitHub content are not automatically accessible to chat.

## Latest delivery: link-network-sources
Includes all earlier changes plus Sources & imports, three original local illustrations and an optional relationship-context prompt. Existing DB/Keychain location is unchanged; no migration or resume re-import is required. Stop the old process and launch from this extracted folder using COMPANION_AI_MODE=live (omit --demo). All source parsing is local and model-free; preparation/chat uses the normal provider gate. No live LinkedIn/Google account connection is present. Limits, data handling and deferred OAuth are in README. No GitHub push performed; Mac/Safari testing remains pending.

## Latest delivery: link-clear-start
Usability correction after the user could not find Sources & imports. The default Today screen now shows Bring your connections, Capture a conversation and Prepare for a meeting; Import appears in primary navigation. Each CTA opens its actual task. Welcome offers direct import without coaching questions. All data locations and Keychain setup remain unchanged; no migration or re-import. Stop the older process before starting this folder. Source import rules and deferred live account sync remain as before. No GitHub push performed.

## Latest delivery: link-daily-home
Fixes Today/Import duplication. Today: next action, resume point, quick log/preparation and people. Import: source choices and review tools. Main Import navigation and the welcome import bypass remain. Data, key and app launch settings are unchanged; no migration or re-import. No GitHub push performed. Mac/Safari verification remains pending.
