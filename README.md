# Link

Link helps students and recent graduates find a starting point, prepare for professional
conversations, and continue relationships thoughtfully. The app and companion are both **Link**.

The Python package, `companion` command, and existing data folder retain their names so upgrades
keep your information in place. This is a local desktop-browser workflow. The **Connection Studio** desktop design is implemented; mobile capture is deferred.

Start with Link's guided onboarding even if you have no contacts or résumé. It proposes a plan;
you review what becomes a person, log, task, or preference. Existing career tools are still available.
Link never signs in to LinkedIn, browses it or operates it, and never sends messages for you. LinkedIn data
comes only from files you export yourself. Calendar and email connections, and nudges outside the app, are
decided but not built yet (D39 to D41 in `DECISIONS.md`).

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
| Version | `COMPANION_UI_MODE` or `companion run --mode` (`user`, `dev`) | `user` |
| Google Calendar sign-in | `COMPANION_GOOGLE_CLIENT_FILE`, or `COMPANION_GOOGLE_CLIENT_ID` and `COMPANION_GOOGLE_CLIENT_SECRET` | unset (calendar connection off) |
| Port | `COMPANION_PORT` | `8765` |
| Data folder | `COMPANION_DATA_DIR` | see above |
| Time zone for the daily cap | `COMPANION_TIMEZONE` | `America/New_York` |

## Two versions

`companion run` opens the **user version**: everyday words ("Add a note", "Add contacts"), no spending meter or AI
settings, and one plain line when the AI is off or showing sample answers. `companion run --mode dev` opens the
**developer version**: the original wording, the AI budget, the mock/live switch and spending details. The browser
checks in `scripts/` run the developer version, except `check_user_mode_browser.py`, which checks both. See D42.

## Connect Google Calendar (optional)

Link can read your Google Calendar to find people you have met or are about to meet. It is read-only: it never adds,
changes or deletes an event, and it never reads event descriptions, places or notes. Nothing is saved as a person
until you click Keep, and an invitation is never treated as a conversation. Decision D43 has the details.

After a meeting with someone you kept, Today asks "How did it go with ...?" about an hour after it ends. Great or
Fine saves a short note dated to the meeting, an optional line adds to it, and an optional promise becomes your
next step with a reminder in three days. Skip saves nothing, and an unanswered question quietly goes away after a
week (decision D44).

In `--demo` mode this works with a fictional sample calendar and needs no Google account.

To connect your own calendar you need your own Google sign-in settings. This is the part to do once:

1. In the Google Cloud Console, create a project and turn on the **Google Calendar API**. For email, also turn on the **Gmail API**.
2. Under the OAuth consent screen, choose **External**, keep it in **Testing**, add your own Google address as a test
   user, and add the read-only calendar scope (`.../auth/calendar.readonly`). For email, also add `.../auth/gmail.metadata`
   (names, addresses and dates only; Link never reads a subject or body).
3. Create an **OAuth client ID** of type **Desktop app**. Copy the client ID and secret.
4. Download the client's JSON file, move it somewhere outside this repository, and make it private:

```
mkdir -p ~/.config/link && mv ~/Downloads/client_secret_*.json ~/.config/link/google-client.json && chmod 600 ~/.config/link/google-client.json
```

   Then start Link with `COMPANION_GOOGLE_CLIENT_FILE` pointing at it:

```
COMPANION_GOOGLE_CLIENT_FILE=~/.config/link/google-client.json .venv/bin/companion run
```

   `COMPANION_GOOGLE_CLIENT_ID` and `COMPANION_GOOGLE_CLIENT_SECRET` also work and override the file. Git ignores
   `client_secret*.json`, but keep the file out of the repository anyway. The file must be a **Desktop app** client.
   `companion status` shows whether Link found sign-in settings, without printing them.

5. Open **Add contacts**, then the calendar tab, then **Connect Google Calendar**. Your browser opens Google; after you
   approve, it returns to Link on `http://127.0.0.1:<port>`. The sign-in is stored in your system keychain, never in the
   database, an export or a log. **Disconnect** removes it, and Delete everything removes it too.

Not yet verified: this has been tested against stand-ins only. No real Google sign-in has been tried. As far as I know,
an app in Testing mode is limited to listed test users and Google may expire its sign-in after about a week; school
Google accounts may need an administrator's approval. Check Google's current rules before you rely on it.

## Open Link with one click (Mac)

Run this once in Terminal, from the same settings you normally start Link with (the same `COMPANION_DATA_DIR`, and
a `COMPANION_GOOGLE_CLIENT_FILE` if you use one):

```
.venv/bin/companion launcher --install
```

It builds `~/Applications/Link.app`. Open it from Spotlight (Cmd+Space, then "Link") or drag it to your Dock. If Link is
already running, it opens a fresh one-time sign-in link in your browser. If not, it starts Link quietly in the background
first. **Quit Link** in the Menu (or `companion quit`) stops it. `companion launch` does the same thing from Terminal,
and `companion launcher --uninstall` removes the app. Link stays running in the background until you quit it, listening only
on this computer. Its log is `link.log` in your data folder. Decision D47 has the details.

**After an update** (decision D56): `git pull` downloads new code, and opening Link then starts the new code. If an older
copy is still running, opening Link stops it and starts the new one ("Restarted Link with the update"). The same install
command also adds a git hook in this folder, so `git pull` opens Link by itself whenever it brings changes. Run
`companion launcher --status` to check it, and `companion launcher --uninstall` to remove it with the app. If your git
uses a shared hooks folder (`core.hooksPath`), the hook is skipped, and you open Link after pulling.

The builder installed and opened `Link.app` on a real Mac (see PROGRESS, 2026-11-17). The launcher itself, including the
restart after an update, was run end to end against a real background server on Linux.

## Reminders outside Link (optional, Mac)

Link can show one desktop reminder a day when a follow-up is due: a meeting you kept that needs a "How did it go?",
or a reminder that has come due. It says how many and never who, because a notification appears on a lock screen
and is stored by the operating system. Quiet hours (9 pm to 8 am by default) are always respected, and after two
reminders in a row that lead nowhere for the same person, Link stops reminding you about them (decision D46).

1. Open **Menu**, then **Settings**, then **Reminders outside Link**. Choose **Once a day** and a time.
2. Click **Send a test reminder** to check that macOS shows it. If it doesn't, open System Settings, then Notifications,
   and allow notifications for Script Editor.
3. To get reminders while Link is closed, run this once in Terminal. It installs a small login agent that checks every
   15 minutes and reads only Link's own data:

```
.venv/bin/companion nudge --install
```

   Remove it with `companion nudge --uninstall`. Delete everything does not remove it. `companion nudge --dry-run`
   shows what it would do, and `companion nudge --status` says whether it is installed. Its log, in your data folder,
   holds counts only.

Verified once: the builder's test reminder appeared on a real Mac. Not yet verified: the login agent (`--install`) has only
been tested with stand-ins, and no real reminder for a due follow-up has been shown. A reminder cannot open Link by itself,
so you still start Link yourself.

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

Primary navigation is at the top: **Today**, **People**, **Quick log** and **Import**, with **Career
tools**, **About me** and **Settings & data** beside them. Each area is described in more detail in the
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

`403 passed` on Linux, Python 3.13, 2026-11-19. Not yet run on macOS. Coverage by acceptance criterion:

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
| Progress tracker counts real records only, in any order | `test_journey.py` (11 tests) |

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
| `check_calendar_browser.py` | Sample calendar: connect, find people, keep, never suggest, disconnect; the page's connection label stays true |
| `check_launcher_end_to_end.py` | Not a browser check: starts a real background Link, signs in with a minted link, checks no link reaches the log, and quits it |
| `check_nudges_browser.py` | Settings: turn reminders on, quiet hours, test reminder, pause and resume, and the message on a computer that cannot show one |
| `check_user_mode_browser.py` | User version uses plain words and hides spending and AI-mode controls; developer version keeps them |
| `check_qol_browser.py` | Quick log recovery, undo, duplicate-name suggestions, reminders, reduced motion |
| `check_avatar_browser.py` | Link character and the Meet Link walkthrough (developer version) |
| `check_walkthrough_browser.py` | How Link works as the first screen, the progress tracker, every walkthrough step on practice data with nothing written, leaving, real progress, why-we-ask lines, phone (D55) |

They need the Python `playwright` package (`.venv/bin/pip install playwright`), which is not part of
`.[dev]`. Every script launches Chromium from `/usr/bin/chromium`, which suits the Linux machines they
were written on. On a Mac, change `executable_path` in the script to your browser, for example
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, or remove it and run
`.venv/bin/playwright install chromium` once. Run a script from the repository root:

```bash
.venv/bin/python scripts/check_first_clicks_browser.py --output /tmp/link-check
```

The first four in the table were re-run on Linux on 2026-11-13 and passed with no JavaScript errors.
The other three last passed in the sessions recorded in `VALIDATION.md`.

## Link, the floating companion

Decision D53. Link is the round button in the bottom-right corner. Click it to chat; the chat opens over the page and
closes with Escape or a click outside it. After you do something, Link may show a one- or two-sentence tip beside the
button. Turn tips off with **Turn off tips** on any tip, or with the **Tips** switch in the chat or in Settings.

## Adding a person, step by step

Decision D52. Choose **Add a person** on How Link works or in the Add menu, or **Add person** on the People page. Link asks four short questions (who, how you met, what you remember, one next step), shows what it
will save as you answer, and saves everything at once. Only the name is required. **Quick form** on the People page
keeps the one-screen form.

## How Link works, your progress, and the walkthrough

Decision D55. A first visit opens **How Link works**: what Link is for, where your information is kept, why answers are
samples in this version, three ways to begin when you don't know where to start, and why Link asks each question. The
bar at the top, **How far you've come**, has four stages (Start here, Groundwork, People & notes, Reaching out) and fills
in only from what you add yourself. It also sits at the top of Today until every stage is done.

**Show me how it works** starts a walkthrough of about three minutes: Link moves through the real app with a practice
person, typing and clicking for you and saying why each question is there. Nothing is saved and nobody is contacted.
Pause, Back, Next, Replay step and Skip to the app work at any time; Esc leaves. Find the page again in Menu (More on a
phone) or Settings, and replay the walkthrough from Menu with **Take the tour**.

## The web version (for remote testers)

Decision D50. The same app, behind a front door that signs people in with Google. Only addresses on an invite list get
in, and each person's data is in its own database file. The Mac app above is unchanged.

To try it on your own Mac before it goes online (quit the Mac app first; both use port 8765):

1. In Google Cloud, create an OAuth client of type **Web application** with the redirect URI
   `http://localhost:8765/connect/google/callback`, and add the scopes `openid` and `.../auth/userinfo.email`.
   Save its JSON file as `~/link-private/google-web-client.json` (`chmod 600`).
2. Install the extra piece the web version needs, and make a secret key once. Keep the key: a new key means everyone's
   account and saved Google connections stop working.

```
.venv/bin/pip install -e '.[web]'
python3 -c "import secrets; print(secrets.token_urlsafe(48))" > ~/link-private/web-secret-key && chmod 600 ~/link-private/web-secret-key
```

3. Start it, with your own address on the invite list (separate several with commas):

```
LINK_PUBLIC_URL=http://localhost:8765 LINK_DATA_ROOT=~/link-web-test LINK_SECRET_KEY="$(cat ~/link-private/web-secret-key)" COMPANION_GOOGLE_CLIENT_FILE=~/link-private/google-web-client.json LINK_INVITES=you@gmail.com .venv/bin/companion web
```

Settings, all read from environment variables: `LINK_PUBLIC_URL` (the site's address; https except on localhost),
`LINK_DATA_ROOT` (where accounts live), `LINK_SECRET_KEY` (at least 32 characters; encrypts saved Google sign-ins and
scrambles email addresses), `LINK_INVITES`, the Google Web client (`COMPANION_GOOGLE_CLIENT_FILE`, or
`COMPANION_GOOGLE_CLIENT_ID` and `COMPANION_GOOGLE_CLIENT_SECRET`), `PORT`, and `LINK_TRUST_PROXY=1` behind a host's proxy.
