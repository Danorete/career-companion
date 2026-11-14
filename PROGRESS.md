# Progress

Read `DECISIONS.md` first. This file says where the build stands so a later session can resume.

This project moved here from a folder in `Danorete/spotify-listening-bi` on 2026-11-10, with its history.

## Current state (2026-11-13)

- The `link-daily-home` build is committed to this repository. Builds between 2026-11-12 and
  2026-11-13 were only delivered as ZIP archives, because pushes from those sessions were refused.
  Notes below that say "no GitHub push performed" or "GitHub writes returned 403" describe those
  sessions; they no longer apply.
- 199 Python tests pass on Linux, Python 3.12. Schema version 5. Mock AI only.
- `claude/connections-redesign` is a separate People/Quick log implementation built in parallel; it is
  not merged. `claude/less-friction` is included in this build.
- `graphify-out/` was rebuilt from code on 2026-11-13.
- Still unverified: a real provider call, billing reconciliation, macOS, Safari, Keychain.
- Entries below are a dated log; their test counts were correct when written.

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


## Connection-first continuation — 2026-11-12 (Codex)

Resumed from the public repository plus the user-pasted, unfinished `people.py`. The interrupted
session's other local files were unavailable. Preserved the newer `claude/less-friction` branch
(postings/extraction) by merging it into `codex/people-quick-log` rather than replacing its work.

Implemented People list/filter/search, minimal add/edit, person detail/timeline, next steps,
Quick log (unassigned/approximate dates), explicit exchange retention, reviewable AI proposals,
context-approved message drafting and manual sent confirmation. Primary navigation is Today,
People, Quick log; career tools are secondary. Two-question general onboarding preserves old memory.
Added isolated temporary `--demo` mode. No new external access or background model calls.

Important corrections to pasted code: no raw-note fallback into drafting; no exchange retention
without opt-in; completing an internal task is not a contact interaction. Selected-person chat
is isolated on context switches; reading recorded relationship material disables memory proposals.

Validation and exact results are recorded in the implementation PR. Mock AI only; no paid calls.
macOS/Keychain/Safari/live-provider verification still needs the owner's machine. `graphify` is
not installed in this environment, so query/update could not run.

When the interrupted Claude Code session resumes, fetch this branch first and compare its local
uncommitted work. Do not overwrite or reset either version. Back up/export the personal database
before upgrading. Remaining product refinement: use real sessions to tune density and copy;
provider summary extraction remains probabilistic and always requires review.

Final continuation checks: **154 tests passed** on Linux/Python 3.12. Headless Chromium exercised
onboarding, minimal person creation, an assigned approximate-date log, editable mock organization,
person timeline, context-approved drafting, search, and a 390px mobile layout with no JS errors.
`node --check` and `git diff --check` passed. Browser smoke script: `scripts/check_people_browser.py`.
GitHub publication failed with HTTP 403 for both connector branch creation and Git push. Deliver
as source archive and patch; no remote branch or PR was created by this continuation.

## Guided desktop continuation — 2026-11-12

Research-led implementation order accepted by the owner: Link-led onboarding, conversation purpose/
preparation, substantive follow-ups, opportunity requests. Mobile capture and visual redesign deferred.

- App and companion named Link; old data/CLI names retained for compatibility.
- Three onboarding paths work before contact entry. Preparation plans are pending until explicit review;
  confirmation is transactional/idempotent and can attach an existing person without duplicate creation.
- Purpose/why/questions, optional clarification, rehearsal with short ephemeral question continuity,
  separate context-approved message drafting, resume/delete plan history.
- Private planning is structurally excluded from outward requests. User-confirmed working preferences
  can guide planning; constraints/private notes/chat cannot. Mock and manual guides are visibly labeled.
- Contextual follow-ups are dismissible and ignore paused people; time alone produces no suggestion.
- Opportunity flow supports perspective, feedback, team/role questions, introductions and referrals.
- Existing career features and endpoint/budget controls retained. Schema v5 adds connection_plans.
- Guided demo no longer skips onboarding. All data remain local; no new external sources/integrations.

Checks and platform limitations are recorded in HANDOFF.md. No real-provider calls. macOS/Safari/
Keychain/live-provider validation remains for the owner's Mac. `graphify` is unavailable here.
GitHub writes previously returned 403; do not assume this source is pushed to the remote.

Final guided workflow checks: 168 automated tests passed on Linux/Python 3.12. Both
`scripts/check_connection_browser.py` and `scripts/check_people_browser.py` passed in Chromium
with no JS errors. Syntax and whitespace checks passed. The guided script additionally verifies
referral ask selection and saved-plan resumption after reload. No live AI calls were made.

### Identity correction

The UI rename alone was insufficient: the general planning prompt did not explicitly name the
assistant. It now identifies the companion as Link and states that obsolete historical names do
not change its current identity. Mock identity questions also return Link. Existing history is
preserved. Live model obedience remains a behavioral check rather than a mathematical guarantee.

## Connection Studio design implementation — 2026-11-12

Built the approved desktop direction: dedicated `static/studio.css`, paper/forest palette with dark
scheme, Georgia/Inter typography, top navigation, split onboarding, split plan review, People directory
and person tabs, quieter Quick log, and expandable Link panel. Existing workflows are retained.
Today work no longer requires a timer; focus sessions remain explicit. Relationship work uses the
relevant guided flow rather than jumping directly to career evidence drafting.

Locally bundled original link mark/vector motif plus 13 attributed Guidance icon symbols from pinned
upstream. No reference-site image/video/font assets copied and no new runtime network access.
The CSS pass introduced no database migration. Existing privacy and budget boundaries remain.

Verification: all 170 Python tests passed on Linux/Python 3.12. Existing People and guided-connection
Chromium scripts passed; new `scripts/check_studio_browser.py` passed keyboard directory/tabs,
next-step completion/undo without false contact, expandable/resizable Link panel, light/dark palette,
desktop overflow, attribution, and opening work without starting a timer. No JS errors. Syntax and
whitespace checks passed. Mock AI only; macOS/Safari/live API still require the owner's environment.
Graphify is unavailable here; its update command could not run. GitHub write access was previously
403, so deliver as source archive rather than claiming a remote PR exists.

## Avatar + walkthrough
Added original Link character, click-to-open panel, optional contextual six-step guide, pause/resume/replay, Settings entry and deterministic UI-only progression. Browser acceptance: `scripts/check_avatar_browser.py`. No schema changes. Deliverable folder: `link-avatar-guide`.


## Quality-of-life + fluid interactions
Added local Quick log recovery, undo for common edits and log save, exact task/reminder restoration, duplicate suggestions, descriptive-name guidance, direct starting prompts, flexible reminder shortcuts, reversible pause, and reduced-motion-aware transitions. New acceptance script: scripts/check_qol_browser.py. Latest source folder: link-polished-workflows. Graphify remains unavailable.

## Conversation scope fix
Removed the blanket evidence-audit instruction from private chat. Selected person context and reviewed summaries now reach planning. Outward claim checks/privacy boundaries remain intact. Latest folder: link-context-advice. Live response quality still needs the user's real conversation test.

## Networking sources + imagery
Added Sources & imports with user-reviewed LinkedIn CSV, selected conversations and local ICS meeting preparation. Added original people/conversation/calendar SVGs, People/Settings entry points, snapshot source labels, and one optional private relationship-context question. No schema migration, OAuth, browser extension, external fetch or automatic engagement. Latest folder: link-network-sources. Acceptance script: scripts/check_network_browser.py. No personal exports were used in development.

## Clear first clicks
Replaced the hard-to-discover entry flow with illustrated Today capabilities and direct one-click imports/logging/calendar/coaching. Import is now primary navigation. First welcome can bypass coaching straight to connection import. New acceptance script: scripts/check_first_clicks_browser.py. Latest folder: link-clear-start.

## Daily home / Import separation
Today now resumes actual work, with compact shortcuts and useful empty states. Import alone owns the illustrated source catalogue and review flows. No backend/schema changes. Latest source folder: link-daily-home. Updated first-click browser checks assert the pages differ while remaining easy to navigate.

## Field notebook redesign — 2026-11-13 (decision D38)
Left wayfinding rail, meta strip and room pager; Today with Recent context; shorter copy across Today, People,
Quick log, Import, onboarding and the Link panel; typed headlines and Link replies with Pause motion and
reduced-motion support; bundled Source Serif 4 and IBM Plex Mono. New stylesheet `static/rail.css`, loaded after
`studio.css`. New browser check `scripts/check_rail_browser.py`; all browser scripts now read `CHROMIUM_PATH`.
199 Python tests and all eight browser checks pass on Linux. Not yet seen on macOS or Safari. The map,
storyboard and annotated-message ideas exist only in Figma.
