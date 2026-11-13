# Desktop workflow validation

Date: 2026-11-12. Platform: Linux, Python 3.12, headless Chromium.

`python -m pytest -q`: **168 passed**.

Coverage added for: value before contact entry; pending proposals with no domain writes;
explicit/idempotent confirmation; association without duplicates; preserving existing commitments;
unknown encounter dates; manual fallback; preventing invented names and planning-generated outward
openings; exclusion of private notes, constraints and chat; approved-context rehearsals; working
preferences used only in planning; dismissible substantive follow-ups; all opportunity request types;
export/deletion; and validation of malformed identifiers and modes.

Two browser scripts passed, using temporary synthetic databases and mock AI:

- `scripts/check_connection_browser.py`: no-contact onboarding, encounter review, person creation,
  preparation, rehearsal, separate message drafting, reload/resume and referral choice.
- `scripts/check_people_browser.py`: the existing People/Quick log, date, review, direct editor,
  search, and layout regression flow.

No JavaScript errors. `node --check` and `git diff --check` passed. Live model behavior,
provider billing, Safari and Keychain were not tested. No paid requests were made.

## Connection Studio design pass

All 170 Python regression tests passed. People and guided desktop browser scripts passed again.
New `scripts/check_studio_browser.py` passed: keyboard directory selection; roving person tabs;
recorded conversations rendering as text; saving/completing/undoing next steps without false contact;
Link panel expansion/resizing; light and dark appearance; desktop overflow check at 1280px;
Guidance attribution; and opening work without starting a timed session. No JavaScript errors.
Screenshots were visually inspected; a DOM-array rendering issue and a dark surface override were
corrected. Syntax and whitespace checks passed. No real-provider calls were made.

### Avatar and guide update
170 Python tests pass. `scripts/check_avatar_browser.py` verifies real click advancement, quick-log typing, pause/resume/replay, note preservation, no automatic interaction saves and no JavaScript errors in Chromium with mock AI. Existing desktop regression script checks remain applicable. macOS/Safari and live API behavior remain unverified.

`graphify update .` could not run because the graphify executable is unavailable in this environment.

### Quality-of-life and motion update
173 Python tests pass, including local-draft retention consent, no automatic timeline/tasks/memory, limits/foreign-Origin protection, and exact task undo preserving other tasks and reminder dates. `check_qol_browser.py` passes draft recovery across navigation/reload, save undo, existing-person suggestions, reminder shortcuts, completion undo, pause/undo and reduced motion. Guide, Studio and guided connection browser suites also passed during this update, using only temporary synthetic data and mock AI. No macOS/Safari/live-provider verification was performed. JavaScript syntax and git whitespace checks pass. Graphify is unavailable, so its update command could not run.

### Conversation scope update
175 Python tests pass. Added checks that selected relationship context and reviewed summaries reach private planning, while private notes and timeline summaries remain excluded from unapproved outward drafting. Prompt checks retain outward claim validation and explicitly scope private advice away from evidence audits. These verify assembly/instructions, not actual live model compliance; a real conversation remains the acceptance test. Graphify could not run (executable unavailable).

### Networking sources and imagery
199 Python tests pass. Coverage includes CSV preambles/BOM, row/field/URL limits, reviewed selection, preservation of existing notes/organizations, no writes or model calls from previews, email exclusion, repeat-import idempotence, transaction rollback, foreign-Origin rejection, selected-message consent, no unselected text persistence, unknown conversation date, source metadata in private fenced planning, delete/export/wipe cleanup, ICS cancellation/recurrence/timezone labels, alarm/attendee exclusion and no attendance inference.

`check_network_browser.py` passes in Chromium with temporary synthetic files and mock AI: original local imagery loading, connection preview and explicit matching, selected recap without retaining originals, ICS-to-preparation without timeline writes, private relationship-context prompt, snapshot labels, keyboard tabs and dark theme. Existing `check_studio_browser.py` also passes. Screenshots visually inspected in light/dark themes. JavaScript syntax checks and git whitespace check pass. No real user exports, live model calls or macOS/Safari tests were used. Graphify update was attempted but its executable is unavailable.

### First-click usability correction
199 Python tests pass. New `check_first_clicks_browser.py` verifies the Home capability map, primary Import navigation, one-click connection/message/calendar controls, logging and no-network coaching alternatives, and fresh-user onboarding import bypass. All five key entry buttons are visible at 1470×956; the three primary task buttons also fit at 1280×800. Screenshots visually inspected. Existing networking, quality-of-life and guided-coaching browser scripts pass with no JavaScript errors, temporary data and mock AI only. JavaScript syntax/whitespace checks pass. No macOS/Safari verification or live calls in this update. Graphify unavailable; update attempted.

### Today / Import differentiation
199 Python tests pass. Updated `check_first_clicks_browser.py` verifies a real recommended action and compact shortcuts on Today at 1470×956 and 1280×800, absence of the import catalogue on Today, all three source tabs on Import, direct import/logging/preparation links, onboarding bypass and a guided no-contacts empty state. Today/Import screenshots visually inspected. Existing quality-of-life and Studio browser scripts pass with temporary synthetic records and mock AI, no JS errors. No macOS/Safari or real-provider calls in this update. Syntax and whitespace checks pass. Graphify update attempted but executable is unavailable.
