# Link

Link helps students and recent graduates find a starting point, prepare for professional
conversations, and continue relationships thoughtfully. The app and companion are both **Link**.

The Python package, `companion` command, and existing data folder retain their names so upgrades
keep your information in place. This is a local desktop-browser workflow. The **Connection Studio** desktop design is implemented; mobile capture is deferred.

Start with Link's guided onboarding even if you have no contacts or résumé. It proposes a plan;
you review what becomes a person, log, task, or preference. Existing career tools are still available.
Link never browses or operates LinkedIn and never sends messages for you.

Version one, single user. Decisions are in `DECISIONS.md`; build status is in `PROGRESS.md`.

## Setup on macOS

Requires Python 3.11 or newer. Don't use the system `/usr/bin/python3`; install one with Homebrew
(`brew install python@3.12`), `uv`, or `pyenv`.

```
git clone https://github.com/Danorete/career-companion.git
cd career-companion
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q      # run the current test suite
.venv/bin/companion run
```

`companion run` prints a link and opens it in your browser. The link works once; restart the app for a new
one. The app starts in **mock AI** mode: replies are canned, labelled as mock, and nothing leaves your Mac.
Use `.venv/bin/companion run --demo` to explore guided onboarding and fictional people in an isolated temporary database. Demo always uses mock AI, even if live mode is configured.

Your data lives in `~/Library/Application Support/CareerCompanion/`, outside this repository.

| Setting | Environment variable | Default |
|---|---|---|
| AI mode | `COMPANION_AI_MODE` (`mock`, `live`, `off`) | `mock` |
| Port | `COMPANION_PORT` | `8765` |
| Data folder | `COMPANION_DATA_DIR` | see above |
| Time zone for the daily cap | `COMPANION_TIMEZONE` | `America/New_York` |

## Loading your information in one step

You don't have to type everything in. A starter file is a `.json` file holding evidence, About me entries,
people and roles, and to-dos.

1. On an empty Today page choose "Import a starter file" (or open Settings & data, then "Import a starter file").
2. Choose the file. The app shows everything it contains.
3. Click "Add these N things".

Evidence from a file always arrives as "your claim, not yet verified", whatever the file says. Every imported
entry is marked as imported and can be edited or deleted. Importing the same file twice adds nothing twice.
Keep your own starter file out of this repository: it is personal data. `tests/test_workflows.py` shows the
format (`STARTER`).

## Turning on live AI

Live mode has never made a real API call. Its request format is tested against a stand-in server only. Do
this the first time:

1. In the provider Console, create a workspace for this app and set a spend limit of $20 on it. This is the
   backstop behind the app's own $16 stop.
2. `.venv/bin/companion status`. If prices show as stale (older than 45 days), re-check the official pricing
   page and update `PRICES` and `PRICES_VERIFIED_ON` in `src/companion/budget.py`.
3. `.venv/bin/companion set-key` and paste the key at the hidden prompt. It goes to the macOS Keychain.
4. `COMPANION_AI_MODE=live .venv/bin/companion run`
5. Send one chat message, then compare the Budget tab with the Console. If the first call errors, the app
   stays usable and the call is counted at its maximum cost; run in mock mode until it's fixed.

In live mode, chat sends your private planning context and recent conversation to the provider. Drafting and
job comparison send only the evidence you tick, your voice notes, and what you type in the form.

## What it does

First run is Link's guided onboarding: **Find a starting point**, **Approach someone**, or **Make sense
of an encounter**. You can also skip straight to importing your connections. The workspace appears
afterwards.

Navigation is a rail on the left: four numbered rooms (**01 Today**, **02 People**, **03 Quick log**,
**04 Import**), then **Career tools**, then **About me**, **Pasted material** and **Settings & data**. Each area is described in more detail in the
later sections of this file.

- **Today**: your recommended next action and where you left off, with compact shortcuts to log a
  conversation, prepare for one, or import connections. "Work on this" opens the task without starting a
  timer; focus sessions are optional. With no contacts yet, Today offers a guided start instead.
- **People**: a directory beside each person's Overview, Conversations and Next step. Explicitly select a
  person to discuss their private planning context with Link. See "Connection-first workflow" below.
- **Quick log**: capture a conversation with an approximate or unknown date, with or without a person.
- **Import**: LinkedIn connections CSV, selected message excerpts and calendar files. See "Networking
  sources and imagery" below.

Career tools keep the earlier workflows:

- **Roles**: status, last recorded interaction, next action, job postings, and one-click outcomes with undo.
- **Evidence**: claims with a status, numbers, approved uses, banned phrases, and a confidential flag.
- **Drafts**: write beside an adjustable evidence inspector, inspect linked claims, preview passage suggestions, compare prior versions and restore them. Every save is checked against current evidence.
- **About me**: everything the companion remembers, editable and deletable.
- **Pasted material** and **Settings & data**: reference text, AI mode, spending, export, delete,
  activity log. AI mode and budget are always visible in the top-right corner.
- **Setup progress**: shows how far setup has got (for example "60%, 3 of 5 steps"). Each step says what
  it unlocks and links to where you do it. Sample data doesn't count, and live AI is optional.
- **The Link panel**: click the Link character to open it. It shows whether Link is ready, thinking,
  waiting for your OK, or off. Drag its edge (or focus the edge and use the arrow keys) to resize.

Keyboard: Tab reaches everything, a "Skip to main content" link comes first, Enter sends a chat message
(Shift+Enter for a new line), Escape closes the companion on a narrow window. Motion is removed when macOS
"Reduce motion" is on.

## Test results

`199 passed` on Linux, Python 3.12, 2026-11-13. Not yet run on macOS. Coverage by acceptance criterion:

| Criterion | Tests |
|---|---|
| Data and session progress survive restarts | `test_data_and_session_progress_survive_restart` |
| Preferences corrected conversationally | `test_preferences_can_be_corrected_in_conversation_and_edited_directly` |
| Drafts separate supported claims from gaps | `test_validate_and_ranking.py`, `test_draft_report_separates_supported_claims_from_gaps` |
| Private context excluded from drafting | canary tests in `test_privacy_and_injection.py` |
| Copying a draft does not mark it sent | `test_copying_or_saving_a_draft_never_marks_it_sent` |
| Pasted content cannot act or alter memory | `test_turn_with_pasted_material_cannot_create_proposals`, `test_tainted_turn_is_withheld_from_later_context`, `test_model_cannot_change_action_state_or_evidence` |
| AI failure or spent budget leaves work accessible | `test_everything_manual_works_with_ai_off`, `test_exhausted_budget_blocks_ai_but_not_saved_work` |
| No activity inside LinkedIn | `test_egress_refuses_everything_but_the_provider_api` |
| $16 stop, unknown usage counted conservatively | `test_budget.py`, `test_failed_call_is_charged_conservatively` |
| Local endpoints protected | `test_security.py` (22 tests) |
| Session timer starts only on a chosen action, and ends | `test_session_timer_info_and_end` |
| Setup progress: starts at 0, ignores samples, each step independent, drops on delete | `test_setup_*` and `test_each_setup_step_flips_on_its_own` (5 tests) |
| Starter file: one-step import, never pre-verified, safe to repeat, validated | `test_starter_file_*` (4 tests), `test_imported_private_memory_still_stays_out_of_drafting` |
| People, Quick log, next steps, person-scoped drafting | `test_people.py` |
| Guided onboarding, preparation, follow-ups and requests | `test_connection_coaching.py` |
| LinkedIn CSV, message and calendar imports | `test_network_imports.py` |
| Private advice is not an evidence audit | `test_conversation_scope.py`, `test_record_context.py` |
| The companion identifies as Link | `test_identity.py` |

Browser checks are in `scripts/check_*_browser.py`; see "Running the browser checks" at the end of this file.

The interface was also driven in headless Chromium at 1470 x 860 (13-inch MacBook Air), 1710 x 1010 and
390 x 844: onboarding, the empty account, sample data, a confirmed suggestion, a full session, a draft and
an edit, outcome recording, every section, a slowed-down load, a forced error and recovery, panel resize by
keyboard, collapse and reopen. No script errors; no control under 44 px; text contrast 5.4:1 or better on the
pairs measured; no sideways scrolling at any size.

## Known limitations

**Not verified**
- No real API call has been made. How `messages.parse` behaves live with `thinking` and `effort` together,
  and real token counts and costs, are unconfirmed.
- Nothing has been run on macOS: Keychain prompts (they may repeat if the Python binary changes), Safari
  (clipboard, cookies on `127.0.0.1`), and whether port 8765 is free are untested.
- Whether failed API requests are billed. The app assumes they might be and counts them at maximum.
- Console usage-page lag, and prepaid-credit behaviour.

**By design**
- Claim checks cover references, permissions, numbers (value and unit), and banned phrases. Strong wording is
  flagged by a word list. A paraphrase that overstates can pass every check. You are the reviewer.
- "Pasted content cannot act" rests on structure: the model has no tools, and a turn with pasted material
  cannot create suggestions. A model can still be influenced in what it *says* in that turn, so read replies
  about pasted material critically.
- The budget uses the app's own price table and a deliberately high token estimate. It is a control, not an
  invoice. The provider's workspace limit is the real backstop.
- Deleting removes the database files. It does not reach Time Machine or other backups, exported files, or
  the provider's copies (deleted within 30 days by default; longer if flagged for a policy violation). It is
  not forensic erasure.
- The database is not encrypted by the app. It relies on FileVault and file permissions. Malware running as
  your macOS user could read it.
- Reminders appear only when the app is open. There are no notifications and no background work.
- Replies are not streamed, so a live reply appears all at once after a pause.
- Pasting a résumé does not create evidence entries by itself. A starter file does that in bulk; someone still has to write the file.
- Appearance supports light, dark, and system mode. Preferences are stored in this browser.
- The session ring is a timer, not an alarm: nothing sounds, and it only updates while the app is open.
- Panel width and collapsed state are stored in the browser (layout only, no personal data).
- The ranking weights are a first guess. Change them in `src/companion/ranking.py` after real sessions.
- One browser session per launch; no multi-tab coordination beyond the shared cookie.
- Dependencies are version-ranged in `pyproject.toml`; `requirements.lock` records the tested versions
  without hashes.

**Out of scope for version one**: LinkedIn integration or automation, URL fetching, background AI calls,
people discovery, accounts, billing, hosting, desktop packaging.

## Interface reference

Link's web controls adapt the [iOS 27 Builder community kit](https://www.figma.com/design/AukfOZC1FQTHjg1plgzdEz/?node-id=6171-452): capsule search fields, prominent capsule buttons, and a floating mobile tab bar. The implementation uses the existing HTML/CSS/JavaScript stack; it does not embed Figma renders or require SwiftUI. Glass surfaces have opaque fallbacks, and motion follows the system reduced-motion preference. On mobile, Today, People, Evidence and Drafts are direct tabs; About me, Pasted material and Settings remain available under More.

## Workflow improvements

- Click a tagged claim to select its passage, then expand its evidence, source and verification status. Claims without links remain explicitly unverified by this interface.
- Version history compares old and current text. Restore rechecks the old wording against the current evidence library and keeps the overwritten text in history. History starts when a draft is first saved or edited after this upgrade. Deleting a draft also deletes its versions.
- Select draft text to shorten, clarify, or check it. Suggestions use the outward-drafting allowlist, require an explicit accept, and do not replace text if you have edited it since requesting the suggestion. Mock suggestions are labelled.
- Failed saves keep edits in memory for retry, including when navigating between sections. A browser-close warning appears for unsaved work. This is not crash recovery: unsaved text can be lost if the browser or process is terminated. Saved drafts and history live in the local database.
- Import plain text or Markdown from a résumé or README, review extracted passages, and approve entries as unverified evidence. PDF text must be copied/pasted; no remote extraction or model call runs during import.
- Command/Control+K searches local people, evidence, drafts and commands. Appearance settings offer light/dark/system. The writing inspector supports drag, arrow keys, Home and End; its width is remembered.
- Settings includes provider readiness and a user-triggered live connection test. The test sends a fixed diagnostic prompt without user records through the normal budget gate. It uses API budget. No real-provider call was made while developing this upgrade; compare the app ledger with the provider Console before relying on billing accuracy.

The database adds a `draft_versions` table on startup without relocating existing records. The `companion` command and data directory stay the same.

## Connection-first workflow (2026-11-12)

The main workspace now focuses on **Today**, **People**, and **Quick log**. Career tools remain
available in the sidebar; existing roles, evidence, drafts, and outcome labels are retained.

Add a person with just a name. Open them for context, a timeline, and an optional next step.
Quick log captures fragments with an approximate or unknown date and can stay unassigned until
later. Save locally without AI. “Organize with Link” sends that selected log to your provider
in live mode and returns an editable proposal; it does not commit facts or create tasks.
Original exchanges are retained only when explicitly selected. Private planning notes and chat
are excluded from message drafting. Review the exact approved context before generating a message.
Copying does not mark it sent. Completing a research task does not count as contacting someone.

To explore **fictional people in an isolated temporary database**, stop the regular app and run:

```bash
.venv/bin/companion run --demo
```

Demo mode always uses mock AI, even if your environment is configured for live mode. It never
opens your regular database. Normal shutdown removes the temporary demo directory; a crash or
forced kill may leave that directory in the system temporary folder. Personal data should not
be entered into demo mode. To return to your records, stop the demo and run the normal command.

Back up/export your data before upgrading. The schema upgrade is additive; it does not delete
existing records. This remains a local single-user app, not a public hosted service.

Optional browser smoke check (requires Playwright and Chromium installed separately):
`python scripts/check_people_browser.py --output /tmp/link-browser-check`.
It runs synthetic records in a temporary database with mock AI and writes screenshots only.
The Python regression suite does not require Playwright. See "Running the browser checks" below.

## Guided desktop connection building

Start with **Find a starting point**, **Approach someone**, or **Make sense of an encounter**.
Link helps clarify a purpose and proposes a plan before requesting structured records. Save the
plan alone, or explicitly add a person, original recollection, chosen next action, or preference.
A recollection's date remains unknown until you choose one in Quick log. Existing users can start
from **I'm stuck — help me choose** on Today. Demo mode now includes onboarding.

From a person, use **Help me prepare**, **Find a reason to follow up**, or **Ask for help or an
opportunity**. Preparation is resumable. Optional practice is clearly fictional, not a simulation
of that specific person's actual thoughts. Message drafting uses only the context you approve
in its editor and public voice preferences; no private plan, relationship notes or chat is attached.
Generated text and factual claims still require human review. Nothing is sent automatically.

Planning may use your saved working preferences, but not private constraints or relationship notes.
The selected workflow fields go to the AI provider in live mode. Pending plans also store your inputs
locally; they can be deleted from the preparation history and are included in export/full deletion.
Mock output demonstrates the workflow without interpreting your information. With AI off or budget
reached, you receive an explicitly general manual guide and can still save your next step.

Desktop browser smoke test: `python scripts/check_connection_browser.py --output /tmp/link-guided-check`
(requires separately installed Playwright and Linux Chromium). Mobile capture is not implemented.

## Connection Studio design

The app now uses a desktop-first editorial workspace: warm reading surfaces, serif headings,
locally bundled Inter, and light/dark appearance. Primary navigation is at the top. People keeps
a compact directory beside a person's Overview, Conversations and Next step sections. Arrow keys
navigate directory buttons and tabs; text fields retain normal editing behavior.

Link remains available as a floating control and expands into a resizable companion panel. Guided
onboarding and plan review use a two-part composition; Quick log remains a simple capture surface.
Today’s **Work on this** opens the task without starting a timer. Optional focus sessions remain.

Guidance icons by [Streamline](https://www.streamlinehq.com/icons/guidance) are bundled under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); attribution and modifications are recorded
in `src/companion/static/GUIDANCE-LICENSE.md`. No fonts or icons load from a CDN.

Desktop design smoke check: `python scripts/check_studio_browser.py --output /tmp/link-studio-check`
(requires separately installed Playwright and Linux Chromium). Safari/macOS-specific behavior still
requires local testing. Mobile capture and public hosting remain out of scope.

### Meet Link
Click the Link character to open the companion. **Meet Link** starts an optional interactive walkthrough: open the companion, find People, and try Quick log. The walkthrough makes no model calls and never adds history or tasks by itself. User-typed Quick log notes autosave as unfinished local drafts. Escape pauses it; **Settings & data → Take the guided walkthrough** replays it. Tour position is a browser preference and is paused on reload.


### Everyday connection workflow
Quick log automatically keeps one unfinished recap in the local database (never browser storage), including approximate timing and the selected person. It survives page changes and reloads; **Discard unfinished note** removes it. A pasted exchange is retained only when **Keep the original exchange on this Mac** is checked. Drafts are private workspace data, not AI memory or timeline entries; they are included in data export and removed by Delete everything.

Use descriptive names when you don’t know someone’s name yet. Add person suggests existing matches before creating a separate record. Today offers three direct starting prompts. Next step includes **No reminder**, **Next week**, and **After an event** (you choose the date). Paused connections retain their history and are excluded from suggested follow-ups.

An Undo bar reverses the latest supported change during the current session: saving a quick log (restores the draft), editing person details, changing a log’s person, reviewing a log, saving or clearing a next step, and pausing/resuming a connection. Task completion has its own Undo button, including reminder restoration. Explicit permanent deletion and removal of a retained exchange are not undoable; there is no automatic merging. Short transitions honor reduced-motion preferences.

### Conversation context
Link can advise on a relationship or the app using what you tell it and the selected person's saved context and reviewed summaries. Ordinary coaching does not require evidence verification or a resume. An imported resume helps with professional claims; it does not unlock general conversation. Local files and saved GitHub links are not automatically read. Public drafting still uses the separate evidence and privacy controls.

## Networking sources and imagery
Open **People → Import connections** or **Settings & data → Open Sources & imports**. Three original, bundled SVG illustrations introduce the local workflows; no remote image requests are made.

- **Your people:** choose the English `Connections.csv` from LinkedIn’s official export. Preview is read-only. Select new people or explicitly choose a suggested match. Filling blanks preserves existing names, organizations, relationship notes, context and groups. Role at export and connection date are labeled snapshot metadata, not evidence of current employment, closeness or a conversation. Email addresses are discarded. Repeating the same import skips previously confirmed rows. An imported person with no relationship context gets one optional private question: “How do you know this person?”
- **Your conversations:** choose LinkedIn `messages.csv`, a `.txt` excerpt, or paste one excerpt. Search participants/text, select individual messages, choose the person yourself, and write a recap. Original text is saved only when you opt in; otherwise only the recap is stored. Unselected messages and the original file are never stored. Message timestamps are source data; the log date remains unknown until edited. No commitments become tasks automatically. Repeating the same selected messages for the same person does not add a second log.
- **Your next meeting:** choose an `.ics` calendar snapshot, review one event and click **Prepare for this conversation**. No event or attendance record is saved by preview. Canceled events remain labeled; recurring series are not expanded. Attendees, alarms, attachments and subscription links are not imported or followed. Afterward, Quick log lets you record what actually happened. Google/Outlook account sync and Gmail access remain deferred; there is no OAuth connection in this version.

Files must be UTF-8 text under 290 KB in the UI. Server validation allows at most 1,000 CSV rows, 100 calendar events, and 12,000 characters in one selected conversation excerpt. Non-English CSV headers and ZIP archives are not supported. Split larger exports and keep the header. Imported previews remain only in browser memory and are cleared on reload or by **Clear imported previews**. Imported records and source metadata are included in export/wipe; deleting a person or log removes the associated import receipt. Bulk import has no batch Undo: review selections before confirming. Existing per-person edit/undo and permanent-delete controls remain available.

All parsing is local and makes no model calls. Choosing AI preparation, chat or Organize with Link afterward uses the normal live-mode context and budget rules. Imported metadata is fenced as untrusted snapshot data in planning, and never grants the model write access. No LinkedIn browsing, scraping, graph search, messaging, live sync or automatic outreach is added.

Official references checked November 13, 2026: [LinkedIn access](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access), [data export](https://www.linkedin.com/help/linkedin/answer/a1339364), [User Agreement](https://www.linkedin.com/legal/user-agreement), [Gmail scope restrictions](https://developers.google.com/workspace/gmail/api/auth/scopes).

## Today and Import have different jobs
**Today** is the daily workspace: one recommended next action, a resume point, quick logging/preparation, saved plans and your people. With no contacts, it offers a small guided start or a way to add someone you know. It does not repeat the illustrated import catalogue. The compact **Import connections** shortcut remains visible, and **Import** stays in primary navigation.

**Import** owns the source overview: connection CSV, selected message excerpts and calendar files, followed by their explicit review controls. It remains one click away. The initial welcome screen still allows importing without completing coaching questions. Existing saved data, Keychain configuration and import safeguards are unchanged.

## Running the browser checks

Each script in `scripts/` starts the app on synthetic data in a temporary database with mock AI, drives
it in headless Chromium, and writes screenshots to the `--output` folder:

| Script | What it checks |
|---|---|
| `check_first_clicks_browser.py` | Today and Import are different pages; shortcuts, onboarding bypass, empty states |
| `check_network_browser.py` | LinkedIn CSV preview and matching, selected conversations, calendar preparation |
| `check_studio_browser.py` | People directory and tabs by keyboard, next-step undo, Link panel, both themes |
| `check_people_browser.py` | People, Quick log, approximate dates, review, search, narrow layout |
| `check_connection_browser.py` | Guided onboarding, preparation, rehearsal, drafting, resume after reload |
| `check_qol_browser.py` | Quick log recovery, undo, duplicate-name suggestions, reminders, reduced motion |
| `check_avatar_browser.py` | Link character and the Meet Link walkthrough |
| `check_rail_browser.py` | Left rail, typed headlines, Pause motion, reduced motion, page links, Link panel |

They need the Python `playwright` package (`.venv/bin/pip install playwright`), which is not part of
`.[dev]`. Each script launches the browser named by `CHROMIUM_PATH`, or `/usr/bin/chromium` if it is not
set. On a Mac, point it at Chrome. Run a script from the repository root:

```bash
CHROMIUM_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" .venv/bin/python scripts/check_rail_browser.py --output /tmp/link-check
```

All eight passed on Linux on 2026-11-13 with no JavaScript errors.

## Field notebook design (2026-11-13)

The layout follows the proposal in Figma (decision D38):

- **Left rail.** Four numbered rooms with a one-line hint each, Career tools below a rule, then About me,
  Pasted material and Settings. The foot of the rail shows AI mode, budget and "This Mac only", and a
  **Pause motion** button.
- **Meta strip and page links.** Each page starts with its number ("02 / 04 · People"), the date and Search
  (⌘K), and ends with links to the previous and next room.
- **Today** puts the next action beside **Recent context**: your last three quick logs with honest dates
  (exact, "~ last week", or "Date unknown").
- **Fewer words.** Headlines, labels and the Link panel's notes are shorter. Where a visible label was
  shortened, its accessible name keeps the full wording (for example "Log" is announced as "Log a
  conversation").
- **Typed headlines.** A page's headline, and Link's short replies, type themselves out on the first visit in
  a session. The full text is in the page from the start for screen readers. With macOS "Reduce motion" on,
  or Pause motion pressed, text appears at once and animations stop.
- **Type.** Source Serif 4 for headings and IBM Plex Mono for labels, both bundled locally under the SIL
  Open Font License (`static/fonts/LICENSE-*.txt`). Inter stays for body text.

No database or API changes. Phone layout is unchanged and still deferred.
