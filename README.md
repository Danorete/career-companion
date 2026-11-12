# Link

Your people, connected. A local workspace for making and keeping connections, with a companion beside it.

The Python package, `companion` command, and existing data folder retain their names so upgrades keep your information in place.

You jot down what you remember about someone you met, find it under that person later, and prepare a
thoughtful next step. Nothing needs to be exact: a rough note, an approximate date and an unsure promise are
all kept as what they are. Link never touches LinkedIn, your inbox or your contacts. You send every message
yourself. The earlier job-search tools (roles, evidence, drafts) are still there under **Career tools**.

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
To look around with fictional people instead of your own, run `.venv/bin/companion run --demo`. The demo
keeps its own database file (the data folder name ends in `-demo`), shows a banner on every page, and can
neither open nor import your records.

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

1. Open Settings, then "Privacy & data", then "Import a starter file".
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

First run is two questions from the companion (working name: Tempo): whether you want help meeting people,
keeping in touch, or both, and how you'd like it to work with you. Each has suggested answers, can be
skipped, and can be changed later in Settings.

- **Today**: one recommended action with its reason and a time estimate; anything else is collapsed. Only
  things you committed to, deadlines, importance and reminders you set are ranked. Time since you last spoke
  to someone never creates a task. A new account offers "Log someone you met" and "Add someone you'd like
  to meet".
- **People**: a compact, searchable list. Each row shows the name and organisation, how you know them, the
  last thing you recorded (approximate dates stay approximate) and the next action if there is one. Filters:
  All, Want to meet, Getting acquainted, Stay in touch, Paused. These are labels you choose, not scores, and
  nobody is categorised for you. Adding someone needs only a name. A saved profile link is text: the app
  never opens it.
- **A person**: how you know them, one editable next action with an optional reminder, a timeline, private
  notes, and three actions: Quick log, Prepare a message, Edit details. Each timeline entry says where it
  came from (your recap, a pasted exchange, an action you confirmed), when it happened and when you logged
  it. Every entry can be edited and deleted.
- **Quick log**: one box, "What do you remember?", reachable from the top of every page. Person and date are
  optional; a log with no person waits under Quick log until you assign it, and no person is ever created for
  you. With AI on, "Save and sort with Tempo" proposes an editable summary split into what happened, what
  you're unsure about, possible commitments and ideas for a next step. Nothing from it is kept until you
  approve it, and a possible commitment stays a note until you set it as the next action yourself. A pasted
  exchange is optional, and the form says what will be kept before you save.
- **Tempo, scoped**: while you're on a person, the panel says who the conversation is about. It can read
  what you recorded about that person and nothing about anyone else, and each person's conversation is kept
  apart from the others.
- **Career tools** (lower in the sidebar): Roles with one-click outcomes and undo, Evidence, Drafts, Pasted
  material, and the optional career setup checklist. Records made before this redesign are unchanged; an
  outcome once recorded on a person appears in their timeline under its original label.
- **Settings**: You & preferences (everything Tempo remembers about you, editable and deletable), AI &
  spending, Privacy & data (export, import, delete, activity log).

Keyboard: Tab reaches everything, a "Skip to main content" link comes first, Enter opens a person from the
list, Command or Control K searches people and records, Enter sends a chat message (Shift+Enter for a new
line), Escape closes a dialog. Motion is removed when macOS "Reduce motion" is on.

## Test results

`164 passed` on Linux, Python 3.12, 2026-11-12. Not yet run on macOS. Coverage by acceptance criterion:

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
| A person needs only a name; categories are the user's choice | `test_adding_someone_needs_only_a_name`, `test_a_saved_profile_link_is_text_and_category_is_the_users_choice` |
| A rough log saves without AI and without a person | `test_a_rough_log_saves_without_ai_and_without_a_person` |
| An approximate date is never given a date | `test_an_approximate_date_is_kept_as_words_with_no_invented_date`, `test_resolve_when_never_gives_an_approximate_entry_a_date` |
| An uncertain promise is never a task or reminder | `test_an_uncertain_promise_never_becomes_a_task_or_reminder` |
| An unassigned log joins an existing person, no duplicates | `test_an_unassigned_log_can_be_given_to_an_existing_person` |
| One person's context never reaches another's draft or chat | `test_a_draft_for_one_person_never_contains_another_persons_context`, `test_switching_people_in_chat_does_not_carry_the_previous_persons_context`, `test_drafting_gets_the_users_recap_and_never_private_notes_or_a_pasted_exchange` |
| A pasted exchange is kept only on request and cannot act | `test_a_pasted_exchange_is_kept_only_when_the_user_says_so` |
| Time since last contact creates no obligation | `test_time_since_last_contact_alone_creates_no_obligation` |
| Existing people, roles, notes and outcomes survive the upgrade | `test_existing_people_roles_notes_and_outcomes_survive_the_upgrade` |
| Demo data is fictional and separate | `test_demo_data_is_fictional_labelled_and_lives_in_its_own_database` |
| Starter file: one-step import, never pre-verified, safe to repeat, validated | `test_starter_file_*` (4 tests), `test_imported_private_memory_still_stays_out_of_drafting` |

The connections redesign was driven in headless Chromium at 1470 x 860 in four runs (74 checks, all passing):
a new user with AI off using the keyboard; a database created before the redesign, with mock AI; the demo;
and deep links, undo and a 390 x 844 phone width. No script errors, no control under 44 px, no request left
the machine.

Before the redesign the interface was also driven at 1470 x 860 (13-inch MacBook Air), 1710 x 1010 and
390 x 844: onboarding, the empty account, sample data, a confirmed suggestion, a full session, a draft and
an edit, outcome recording, every section, a slowed-down load, a forced error and recovery, panel resize by
keyboard, collapse and reopen. No script errors; no control under 44 px; text contrast 5.4:1 or better on the
pairs measured; no sideways scrolling at any size.

## Known limitations

**Not verified**
- One live call has succeeded: the connection test, on the owner's Mac on 2026-11-11. The quick-log sorting
  prompt and the résumé extraction prompt have only run against the mock and a stand-in provider, so how well
  the live model separates certain from uncertain details is unconfirmed. Real costs have not been reconciled
  with the provider Console.
- The automated tests and browser runs are on Linux. On macOS only startup, Keychain and the connection test
  have been exercised by hand; Safari (clipboard, cookies on `127.0.0.1`) is untested.
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
- People: the four category names are fixed; which category someone is in is yours to set, change or clear.
  There is one next action per person; older open to-dos for them are listed underneath it.
- Quick log: a log with no person is matched by hand; the app does not guess who it is about. In mock mode
  the "sort" is a rough sentence split, labelled as mock. If you answer Tempo's one clarifying question, the
  answer is added to your note. A summary you approve is treated as your own words afterwards, including one
  that drew on a pasted exchange, so read it before ticking it for a draft.
- Approximate dates are ordered in the timeline by a rough guess that is never shown; the order can be off.
- Deleting a person deletes their timeline and next action. Messages drafted for them are kept, unlinked.
- A draft can take at most 10 ticked notes.
- The demo is seeded once into its own database. Changes you make there stay there.
- Replies are not streamed, so a live reply appears all at once after a pause.
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

Link's web controls adapt the [iOS 27 Builder community kit](https://www.figma.com/design/AukfOZC1FQTHjg1plgzdEz/?node-id=6171-452): capsule search fields, prominent capsule buttons, and a floating mobile tab bar. The implementation uses the existing HTML/CSS/JavaScript stack; it does not embed Figma renders or require SwiftUI. Glass surfaces have opaque fallbacks, and motion follows the system reduced-motion preference. On mobile, Today, People and Quick log are direct tabs; Career tools and Settings are under More.

## Workflow improvements

- Click a tagged claim to select its passage, then expand its evidence, source and verification status. Claims without links remain explicitly unverified by this interface.
- Version history compares old and current text. Restore rechecks the old wording against the current evidence library and keeps the overwritten text in history. History starts when a draft is first saved or edited after this upgrade. Deleting a draft also deletes its versions.
- Select draft text to shorten, clarify, or check it. Suggestions use the outward-drafting allowlist, require an explicit accept, and do not replace text if you have edited it since requesting the suggestion. Mock suggestions are labelled.
- Failed saves keep edits in memory for retry, including when navigating between sections. A browser-close warning appears for unsaved work. This is not crash recovery: unsaved text can be lost if the browser or process is terminated. Saved drafts and history live in the local database.
- Import plain text or Markdown from a résumé or README, review extracted passages, and approve entries as unverified evidence. PDF text must be copied/pasted; no remote extraction or model call runs during import.
- Command/Control+K searches local people, evidence, drafts and commands. Appearance settings offer light/dark/system. The writing inspector supports drag, arrow keys, Home and End; its width is remembered.
- Settings includes provider readiness and a user-triggered live connection test. The test sends a fixed diagnostic prompt without user records through the normal budget gate. It uses API budget. No real-provider call was made while developing this upgrade; compare the app ledger with the provider Console before relying on billing accuracy.

The database adds a `draft_versions` table on startup without relocating existing records. The `companion` command and data directory stay the same.
