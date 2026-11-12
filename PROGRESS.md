# Progress

Read `DECISIONS.md` first. This file says where the build stands so a later session can resume.

This project moved here from a folder in `Danorete/spotify-listening-bi` on 2026-11-10, with its history.

## How to resume

```
git clone https://github.com/Danorete/career-companion.git
cd career-companion
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q        # must be green before changing anything
COMPANION_DATA_DIR=/tmp/cc-dev .venv/bin/companion run --no-browser
```

## Done

- [x] 1. Foundation: `config.py`, `db.py` (schema v1)
- [x] 2. Local endpoint security: `security.py`, `tests/test_security.py`
- [x] 3. Budget ledger: `budget.py`, `tests/test_budget.py`
- [x] 4. AI layer: `ai.py` (mock client, gated live client, egress allowlist, gateway), `keys.py`, `tests/test_ai_gateway.py`
- [x] 5. Domain: `store.py`, `ranking.py`, `tests/test_validate_and_ranking.py`
- [x] 6. Context assembly and claim checks: `context.py`, `validate.py`, `services.py`, `tests/test_privacy_and_injection.py`
- [x] 7a. HTTP API: `app.py`, `cli.py`, `tests/test_workflows.py`

- [x] 7b. Browser interface: `src/companion/static/` (checked in headless Chromium, no console errors)
- [x] 8. `README.md` (setup, live-AI steps, test results, limitations), `requirements.lock`

- [x] 9. Design pass (decisions D19 to D23): dedicated onboarding, focused Today with session ring, companion
  identity and states, resizable and collapsible panel, sidebar navigation, bundled fonts, loading and error
  states, keyboard and reduced-motion support. Interface files: `static/index.html`, `static/style.css`,
  `static/app.js`. Backend additions: `POST /api/session/end`, `session` and `today` in `/api/today`,
  onboarding hints, `font-src 'self'` in the CSP.

- [x] 10. Starter-file import (decision D24): `POST /api/starter/import`, preview and confirm in Settings & data,
  third first-step on the empty Today page.

- [x] 11. Setup progress (decision D25): `setup_progress` in `services.py`, `setup` in `/api/bootstrap`, sidebar
  card, checklist on Today and in Settings. Also: the companion panel now closes when the window narrows.

State at last update (2026-11-11): 127 tests pass on Linux, Python 3.13. Mock AI only. The interface was
checked in headless Chromium at 1470 x 860, 1710 x 1010 and 390 x 844.

Design reference (two directions, private to the owner): https://claude.ai/artifact/BNv3bCGtPEPwBRF5jZtMUG

## Next, in order

1. Run the test suite and the app on the Mac. Note anything macOS-specific in README limitations.
2. Enter real evidence, voice samples, and to-dos. Use it in mock mode for a few sessions.
3. First live call, following "Turning on live AI" in the README.
4. Design follow-ups, if wanted: a dark theme, a different companion name, streaming replies.
5. After about two weeks of real sessions, review: ranking weights, the strong-word list in
   `validate.py`, and whether the onboarding questions were the right four.

## Not started, deliberately

- First live API call. The live client's request shape is tested against a fake transport only.
  Before enabling: re-check prices if `PRICES_VERIFIED_ON` in `budget.py` is over 45 days old, set a
  workspace spend limit in the provider Console, run `companion set-key`, start with
  `COMPANION_AI_MODE=live`, send one chat message, and compare the Budget tab with the Console.
- Everything listed as out of scope in decision D18.

## Link workflow upgrade — 2026-11-11

Implemented sequentially, from workflow value to polish:

1. Claim-to-evidence inspector with editor passage selection.
2. Persistent draft history, comparison and evidence-revalidated restoration.
3. Preview/accept selected-passage actions (shorten, clarify, check).
4. Serialized autosave, in-memory recovery, explicit retry and unload warning.
5. Relationship status/last interaction/next action and explicit record-scoped planning.
6. Local text/Markdown evidence import with editable preview and approval.
7. Live readiness and explicit budget-gated connection test (real provider verification remains pending).
8. Command/Control+K local record search.
9. Actual task first on Today.
10. Persistent light/dark/system appearance.
11. Accessible, remembered evidence-inspector width.
12. Fluid companion expansion that preserves the editor and scroll position.

Backend: 135 tests pass on Linux. Browser workflow checks include version restore, suggestion acceptance, a simulated save outage and retry, import, command search and readiness. The new database table is additive. Unsaved text recovery is in-memory, not protection against browser crashes.

Still requires the owner's environment: a real live-provider call and billing reconciliation; macOS/Safari verification. `graphify` is unavailable here, so its query/update commands could not run.

## Less typing — 2026-11-12 (decision D27)

Prompted by the first real session, where adding one role took two screens and silently cut the posting off.

1. People & roles: the add form takes the job posting too. Each role shows its posting, "Compare with my
   evidence" and the result in place. An existing role can have a posting added or replaced.
2. Evidence: "Import from your résumé" now has "Extract with Tempo" (one AI call, résumé text only) with a
   single review list, and "Add as confirmed evidence" for the whole list. The no-AI split is still there.
3. Evidence: "Confirm all N" marks every unverified entry as verified in one click.

Backend: `imports.item_id` (additive, migrated in place; schema version 3), `POST /api/items` accepts
`posting`, `POST /api/items/{id}/posting`, `POST /api/evidence/extract`, `/bulk`, `/confirm-all`, and an
`extract` AI call profile. 143 tests pass. Checked in headless Chromium in mock mode.

Not done: `graphify update .` (graphify is not installed in the cloud session, so `graphify-out/` is stale
for these changes). The extraction prompt has not been run against the live model.

## Connections redesign — started 2026-11-12 (decision D28)

Goal: a new user can capture an imperfect recollection, find it under the right person later, and prepare a
thoughtful next step, without keeping a CRM. Built on top of the "less typing" branch (pull request #3).

### What exists today (inspected)

- `items` holds people (`kind='relationship'`) and roles (`kind='opportunity'`) in one table, shown as one
  mixed list of large cards. `outcomes` (reply, interview, rejection, offer...) attach to either.
- `actions` and `reminders` drive Today's ranking. Ranking does not use time since last contact.
- Chat can be scoped to one record (`context_item_id`), but conversation history is not scoped.
- Drafting takes shareable context from the action's record only. It has no notion of a person's timeline.
- Onboarding is four career questions. Sample data lives in the same tables as real data, flagged `is_sample`.

### Migration (additive only; no row is rewritten or reinterpreted)

| Change | Why |
|---|---|
| `items.category` (default empty), `items.profile_link` | People filters; a saved link is text and is never fetched |
| New table `interactions` | Timeline entries and quick logs, with source, interaction date vs logged date, and date precision |
| `messages.context_item_id` | Keeps one person's conversation out of another's |
| `drafts.item_id` | A message prepared for a person stays attached to that person |

Existing people stay uncategorized. Existing outcomes on people stay where they are and appear in the
person's timeline under their original label. Roles, evidence, drafts, pasted material and memory are untouched.

### Design

- Primary navigation: Today, People, Quick log. Settings holds context, preferences, privacy, AI usage and
  data. Roles, Evidence, Drafts and Pasted material move to a secondary "Career tools" group.
- People: compact searchable list with category filters; a person needs only a name.
- Person view: shared context, one next action with optional reminder, timeline, notes, and Tempo scoped to
  that person.
- Quick log: one text box, optional person, optional date (today, yesterday, approximate, unknown). Saves
  without AI. With AI, a proposed summary separates recorded context, uncertain details, possible
  commitments and suggested next steps; nothing is committed without a click, and a possible commitment is
  text until the user makes it the next action.
- Today: one recommended action; new users are offered "Log someone you met" or "Add someone you'd like to meet".
- Onboarding: two general questions. Fictional demo data lives in a separate database (`companion run --demo`).

### Increments

- [x] 1. Schema, people, logs, next action, scoped chat and drafting, onboarding, demo mode (backend + tests)
- [x] 2. Navigation, People, person view, Quick log, Today, Settings, onboarding (interface)
- [x] 3. Browser verification of the nine scenarios, guideline review, docs

### Checks (2026-11-12)

`164 passed` (`.venv/bin/python -m pytest -q`). 21 of them are new, in `tests/test_people.py`.

Headless Chromium at 1470 x 860, four runs, 74 checks, all passing:

| Scenario asked for | Where it is checked |
|---|---|
| Adding someone with only a name | Run A by keyboard; `test_adding_someone_needs_only_a_name` |
| Saving a rough log without AI | Run A (AI off, no person chosen); `test_a_rough_log_saves_without_ai_and_without_a_person` |
| An approximate date without invented precision | Runs A and B ("Roughly: last week", no date stored); two tests |
| An uncertain commitment stays out of confirmed tasks | Run B (no action, no reminder, Today unchanged); `test_an_uncertain_promise_never_becomes_a_task_or_reminder` |
| Associating an unassigned log with an existing person | Run A; `test_an_unassigned_log_can_be_given_to_an_existing_person` |
| Switching people without drafting-context leakage | Run B (request bodies, cleared form, scope banner); three canary tests |
| Finding a person and resuming after a gap | Run B (Command K, history and next action shown); `test_a_person_can_be_found_and_resumed_after_a_gap` |
| Existing people, roles, notes and outcomes preserved | Run B on a schema-3 database; `test_existing_people_roles_notes_and_outcomes_survive_the_upgrade` |
| Keyboard at a MacBook-sized viewport | Runs A and D: skip link first, sidebar, Add person, Quick log dialog, a person row opened with Enter, undo |

Also checked: the demo (banner, four fictional people, no starter import), a bookmarked category filter,
undo after clearing a next action, an unfinished log surviving navigation, dark theme, and 390 x 844 with no
sideways scrolling.

Design review: the Web Interface Guidelines (fetched 2026-11-12) were applied to the new screens. Fixed as a
result: confirmation or undo on every destructive action, deep links for the people filter and settings
sections, section headings, placeholders, scroll containment in the dialog, long-list rendering, and keeping
an unfinished log when moving around. Deliberately not followed: Title Case for buttons (the app uses
sentence case throughout) and "avoid first person" (Tempo speaks as a colleague by design). The Figma tools
were not available in this session (not signed in), so no Figma file was produced or consulted.

One bug found on the way and fixed: the first Tab press on a fresh page went to the Tempo button instead of
the skip link, because the closed panel scrolled its chat log.

### Limitations and what is left

- The quick-log sorting prompt has not run against the live model. Try it on two or three real notes and
  check that hedged details land under "Not sure about" before relying on it.
- Category names are fixed; only the assignment is editable.
- Unassigned logs are matched to people by hand.
- Draft, role and evidence screens under Career tools keep their earlier wording and layout.
- This branch is stacked on `claude/less-friction` (pull request #3), so it includes that change.
- Verification scripts are not in the repository; they were run from a scratch folder.

