# Career Companion: decision record

Status: accepted 2026-11-10. Personal, single-user, local tool. Version one.

## Verified platform facts (official docs, checked 2026-11-10)

| Fact | Value | Source |
|---|---|---|
| Model IDs | `claude-sonnet-5-5`, `claude-haiku-5-5` (also `claude-opus-5-5`, `claude-fable-5-2`) | platform.claude.com/docs/en/about-claude/models/overview |
| Sonnet 5.5 price per MTok | $2 input, $10 output, $2.50 5-minute cache write, $4 1-hour cache write, $0.10 cache read | .../about-claude/pricing |
| Haiku 5.5 price per MTok | $0.10 input, $0.50 output, $0.125 / $0.20 cache write, $0.01 cache read; 5x higher when the prompt exceeds 100,000 tokens | same |
| Thinking | Billed as output tokens and counted inside `max_tokens`. Sonnet 5.5 rejects `disabled`; `between_tools` turns off up-front thinking at low/medium/high effort. Haiku 5.5 accepts `disabled` at high effort or below | .../build-with-claude/thinking, .../effort |
| Effort | `output_config.effort`; default `high` on Sonnet 5.5, `medium` on Haiku 5.5 | .../build-with-claude/effort |
| Structured output | `client.messages.parse(output_format=PydanticModel)`, generally available; refusals and `max_tokens` stops can break the schema | .../build-with-claude/structured-outputs |
| Prompt caching | Minimum 512 tokens on both models, 5-minute default TTL, usage fields `cache_creation_input_tokens` and `cache_read_input_tokens` | .../build-with-claude/prompt-caching |
| Token counting | `client.messages.count_tokens`, free, an estimate | .../build-with-claude/token-counting |
| Spend limits | Organization and per-workspace limits set in Console (not on the default workspace). At a user-set limit the API returns HTTP 400. Billing month resets 00:00 UTC on the 1st | .../api/rate-limits |
| Data handling | API inputs and outputs deleted within 30 days by default; up to 2 years if flagged for a usage-policy violation. No training on API data under commercial terms | privacy.claude.com article 7996866; code.claude.com/docs/en/data-usage |
| Python SDK | `anthropic` 2.7.0 installed; `messages.parse` accepts `thinking`, `output_config`, `output_format`; `Usage` has the cache fields | installed package, inspected |

Not verified: prepaid credits and auto-reload behaviour, Console usage-page lag, the exact live behaviour of `messages.parse` combined with `thinking` and `effort` (no API key was used; the live client has never made a real call), and every macOS-specific item in the limitations section of the README.

## Decisions

| # | Decision | Choice |
|---|---|---|
| D1 | Stack | Python 3.11+, FastAPI, SQLite (stdlib `sqlite3`), vanilla JS front end served from the same process. No Streamlit, no CDN, no build step. |
| D2 | Local endpoint protection | Bind `127.0.0.1` only (startup refuses anything else), port 8765. Every request: `Host` allowlist. Every state-changing request: matching `Origin`, JSON content type, session cookie (`HttpOnly`, `SameSite=Strict`), and a per-session CSRF header. No CORS, `OPTIONS` refused. Single-use launch token delivered in the URL fragment. Strict CSP; all model and imported text rendered with `textContent`. |
| D3 | Model capability boundary | The model has no tools. It returns schema-validated JSON. It can only produce *proposals* (memory, reminder, idea), which become pending rows that only a click commits. It has no way to change an action's state, evidence, or settings. |
| D4 | Untrusted material | Pasted job descriptions and conversation text go through Import and are wrapped as untrusted in prompts. A chat turn with imported material attached cannot create any proposal (they are dropped in code), and that turn is replaced by a placeholder in later conversation history. |
| D5 | Planning versus drafting | Two separate code paths. Drafting input is built from an allowlist: voice items for the audience, eligible evidence, and text typed into the draft form. It never receives goals, constraints, boundaries, private notes, or chat history. Canary tests enforce this. |
| D6 | Evidence and claim checks | Evidence has a status (`unverified_user_claim`, `user_verified_with_artifact`, `do_not_claim`), permitted uses, structured metrics (value, unit, label), banned phrases, and a confidential flag. Code checks every draft: evidence ID exists and is permitted, numbers match a metric's value and unit, banned phrases are absent, numbers in the body are traceable. Strong wording not found in the evidence is flagged for human review. Semantic overclaims are not machine-verified. |
| D7 | Budget | $20 monthly budget, hard stop at $16 of committed spend for every new AI call. Each call reserves worst-case cost (conservative input estimate plus full `max_tokens`) before dispatch and settles to actual usage. A call whose outcome is unknown stays charged at its reservation. Caps: $1 per session, $2 per day. Month boundary is UTC, matching the provider. Unknown models are refused. No SDK retries. |
| D8 | Models | Conversation, drafting, comparison: `claude-sonnet-5-5`, effort `medium`, thinking `between_tools`. All configurable; Opus and Fable are priced in the table but never selected by default. |
| D9 | Live-call gate | Default mode is `mock`. Live mode needs `COMPANION_AI_MODE=live`, a key in Keychain, and a price table verified within the last 45 days; otherwise the app stays usable with AI off. |
| D10 | Recommendation | Code ranks actions (deadline, importance, existing commitment, in progress, fits the time available). The app opens on one recommended action with up to two alternatives collapsed. Exploratory actions never outrank an open commitment. The model does not rank. |
| D11 | Proactive colleague | The docked companion greets with a code-generated briefing (zero cost), runs the short onboarding as a scripted conversation, and converses through the model when AI is available. No background model calls. |
| D12 | Confirmation rule | Model-proposed memory changes and reminders need a click. Marking an action done needs a click. Autosaving drafts, session progress, and the resume note does not. Copying a draft never changes state. |
| D13 | Storage | `~/Library/Application Support/CareerCompanion/` on macOS, outside the repo, files mode 600. Chat transcripts kept 30 days. `secure_delete` on; "delete everything" removes the database files. Backups, exports, and the provider's 30-day retention are outside the app's control. No forensic-erasure promise. |
| D14 | Credentials | macOS Keychain through `keyring`, set with a hidden prompt. No environment-variable or file fallback. The key never reaches the browser or logs. |
| D15 | Egress and logs | The live client uses an HTTP transport that only allows `https://api.anthropic.com`. Logs and the activity table hold metadata only (event, IDs, token counts, cost). |
| D16 | Without AI | Every workspace feature (evidence, opportunities, actions, drafts, outcomes, reminders, memory, export) works with AI off, over budget, or failing. |
| D17 | Resume card, reminder, outcomes | Interpreted as: a card showing where you left off on the recommended action; date-based reminders that surface when the app is open (no notifications); one-click outcome buttons (reply, interview, no response, rejection, offer). |
| D19 | Visual direction | "Daylight" layout (light, typographic, open sheet) with the session ring from the "Console" direction, chosen by the user from two mockups on 2026-11-10. Three surfaces: ground (chrome), sheet (work), tint (companion). Space Grotesk for headings, Inter for text, one indigo accent, amber for "waiting for your OK". Light theme only for now. |
| D20 | Fonts and CSP | Both fonts are bundled as files under `static/fonts/` (SIL Open Font License). The policy gained `font-src 'self'` and nothing else; no inline styles, no outside requests. |
| D21 | Companion identity | Working name "Tempo". An orb mark with four states: ready, thinking, waiting for your OK, AI off. The panel resizes (drag or arrow keys) and collapses to a corner pill; both are remembered in the browser as layout preferences only. |
| D22 | First run | Onboarding is a dedicated screen with the companion centred: one question at a time, a progress bar, skip on every question. The workspace appears only afterwards. |
| D23 | Session timer | Starting a session records its start time and length; the ring counts down from that, so it survives a reload. A chat on its own starts no timer. The app never alarms; the companion says once when time is up. |
| D24 | Starter file | Bulk import of the user's own information from a `.json` file they choose and preview. Imported evidence is always stored as an unverified claim; entries carry the provenance `imported_file`; duplicates are skipped; unknown fields are rejected. The user's file is personal data and stays out of the repository. |
| D25 | Setup progress | Five milestones, not a field count: a goal, a project, one verified claim, pasted profile text, one person or role. Shown as a percentage together with "N of 5 steps". Sample rows never count. Live AI is listed as optional and is not part of the percentage, so mock mode is a complete setup. Computed on the server and sent with the bootstrap data; the interface refreshes it on every page render. The sidebar card hides at 100% and can be pinned back from Settings (a browser layout preference). |
| D18 | Out of scope for version one | LinkedIn integration or automation, URL fetching, background AI calls, people discovery, accounts, billing, hosting, desktop packaging, streaming responses. |
| D26 | Motion libraries | Amends D1. Anime.js 4.5.0 (page reveal) and Motion 14.12.0, mini build (toast, chat bubbles) are vendored under `static/vendor/`, MIT licensed, served from this app only: still no CDN, no build step at run time, and the Content-Security-Policy is unchanged. They load on demand and the app works the same without them. Motion always plays, and the app does not read the device's `prefers-reduced-motion` setting. That is acceptable for a single-user app and must be revisited before any public version (D18): add the check back in `fx()` and in `style.css`. How they were built is in `static/vendor/README.md`. **Superseded in part by D32:** `fx()` now skips animation under `prefers-reduced-motion`. |
| D27 | Less typing | Three changes after the first real use showed setup was too much work. (1) A role and its job posting are added in one form; the posting is stored as pasted, untrusted material linked to the role, and the comparison runs from the role. (2) A résumé pasted on the Evidence page is turned into entries by one AI call that receives only that text; code strips or flags any number the résumé does not contain; nothing is saved until the user reviews the list and adds it. (3) The user can mark entries as confirmed in bulk, at import or with one click for everything unverified. "Confirmed" records that the user stands behind the entry and names their source, for example the master résumé. Starter files still cannot mark themselves verified (D24); only an action on screen can. |

## Implementation plan

1. Foundation: config, database, schema, progress file.
2. Local endpoint security and its tests.
3. Budget ledger and its tests.
4. AI layer: schemas, mock client, gated live client, egress allowlist, gateway.
5. Domain: memory, evidence, items, actions, outcomes, reminders, ideas, proposals, ranking, resume note.
6. Context assembly, claim validation, drafting and comparison pipelines; canary and injection tests.
7. HTTP API and browser interface; end-to-end tests; browser check.
8. Export, delete, sample data, setup instructions, limitations.

## D28 — Connection-first workflow (2026-11-12)

- Primary navigation is Today, People, Quick log. Roles and evidence remain available as optional Career tools; no existing records are deleted or reclassified.
- Schema v4 adds `items.category`, `items.profile_link`, and `interactions`. It also preserves the v3 role-posting import migration from `claude/less-friction`.
- A person can be created with a name alone. Categories are user-selected; existing people remain uncategorized.
- Quick logs accept unassigned people and approximate/unknown dates. Occurrence and logging dates are separate. Possible commitments never create tasks automatically.
- AI organization returns an unsaved proposal. The user reviews/edits before saving. In mock mode no real interpretation is claimed. Raw exchange retention is explicit opt-in.
- Outward messages use a separate drafting request with user-approved context. No raw-note fallback. Switching selected people starts a separate backend planning session. Turns reading relationship context cannot create memory proposals.
- Completing an internal next action does not imply contact or create an interaction. Historical outcome labels are preserved.
- General onboarding asks two optional questions. Existing personal memory is preserved. Career setup remains in Settings.
- `companion run --demo` uses temporary fictional data and forces mock AI, without opening the personal database. The database is removed on normal shutdown; abrupt termination may leave the temporary directory behind.
- Local, single-user scope and existing budget/security controls remain. No LinkedIn automation, fetching, or background AI calls were added. This is not a hosted multi-user release.

## D29 — Guided desktop connection building (2026-11-12)

- Audience: undergraduates/recent graduates who need help starting and continuing professional relationships. A pre-existing contact list, résumé, or complete profile is not required.
- Link is both app and companion name. Desktop workflow first; mobile capture and visual redesign are explicitly deferred.
- Guided onboarding branches into finding a starting point, approaching someone, or making sense of a recent encounter. The same flow is reachable from Today. Existing onboarding answers/memory are preserved.
- `coaching.py` returns pending schema-validated connection plans. They are persisted for resumption but create no person, memory, log, or commitment until review. Confirm is transactional and idempotent; adding a step never overwrites an existing commitment. Users can associate an existing person instead of creating another.
- Schema v5 adds `connection_plans` and includes it in export/deletion. The v4 schema migration remains additive.
- Planning uses only workflow fields, selected recipient name/organization, and user-confirmed working preferences. It excludes private relationship notes, constraints, chat, and the evidence library. Outward drafting is a separate call using the two context fields shown in its editor plus public voice information. Planning-generated opening/closing fields are discarded, preventing private planning from becoming an outward draft through that path.
- Preparation offers purpose, questions, considerations, an optional clarification, and a next step. Rehearsal is explicitly fictional; only approved professional context, the user's answer, and the last simulated question are sent. No personality grades, predictions of a real person's feelings, or job guarantees.
- Follow-ups require recorded substance (possible commitments or next-step notes), not elapsed time. They remain suggestions, respect paused people, and can be dismissed without changing a relationship or creating a task.
- Opportunity guidance distinguishes perspective, feedback, team/role questions, introductions, and referrals. It requires review and keeps an easy decline; no readiness score or implied agreement.
- AI unavailable/budget exhausted: inputs remain saved in a general manual plan. Mock responses are labeled examples, not personalized interpretation. Demo now exposes guided onboarding rather than skipping it.
- No new integrations, network hosts, automatic sending, or background calls. Existing budget gateway and endpoint guard apply to every new route.

## D30 — Connection Studio desktop design (2026-11-12)

- Approved direction combines editorial type, a tactile reading surface, clear wayfinding, and spatial selection. References: GoShuin, Forge, AUGE, Arc, ZRK and Streamline Guidance. No reference-site artwork, footage or proprietary typefaces is copied.
- `studio.css` is a dedicated final design layer. Locally available Georgia serif headings pair with bundled Inter. Paper/forest light colors and a matching dark scheme replace the previous blue/glass styling. Stored theme choices are respected; new users start light. Reduced-motion and high-contrast preferences are supported.
- Desktop top navigation replaces the large permanent sidebar. Optional Career tools remain in a disclosure. Existing Link panel can expand, collapse and resize next to the workspace. Backend routes, consent boundaries and stored data are unchanged.
- People is a directory beside a selected-person workspace. Overview, Conversations and Next step use keyboard-operable tabs. Up/down/Home/End navigate directory buttons without intercepting text editing; Enter selects. The compact overview shows recent moments without flattening DOM arrays to strings.
- Onboarding is a framed two-part cover/choice composition. Preparation is a two-part spread: reasoning on one side, review and working tools on the other. Quick log is a quiet writing surface with optional prompts.
- Today opens work without requiring a timer. A focus session remains an explicit optional choice. Relationship outreach/follow-up work opens its contextual guided workflow; other career workflows remain intact.
- 13 Guidance icon symbols are bundled from Streamline's pinned source commit 52d750c9ce051e51cb181b7a78932120c48541d0, CC BY 4.0. Public attribution appears in the interface and `static/GUIDANCE-LICENSE.md`. Changes are documented. Assets are served locally under the existing CSP; no CDN or new runtime network host.
- No schema change, external integrations, automatic sending, paid calls, mobile capture or public hosting was added by the design pass.

## D31 — Link avatar and optional interactive guide
Use one original interlocking-loop character for the app mark, companion header and clickable launcher. The companion remains collapsed by default; actual AI availability/thinking state drives its presentation. No microphone or speech permissions.

An optional six-step walkthrough responds to actual panel opening, navigation and typing. It highlights existing controls without blocking the workspace. Pause/Escape and skip are always available; replay lives in Settings & data and Meet Link. Only tour position is stored in browser preferences; no automatic content saves, memory writes or model calls. Reload pauses the guide. Reduced motion is respected. This is deterministic UI guidance, not autonomous AI navigation.


## D32 — Everyday usability and motion
Keep one unfinished Quick log in a protected local DB workspace, not browser storage or model memory. Debounce and serialize saves, show real save/failure state, and warn before leaving while unsaved work remains. Never retain pasted exchange text without opt-in. Wipe/export include the workspace. No schema migration is needed (existing kv storage).

Suggest matching names; let users open the existing person or explicitly confirm a separate one. Unknown names may be descriptions. Do not infer identity or merge records automatically. Add direct starting prompts and optional reminder shortcuts; event dates remain user chosen. Undo uses explicit user requests, targets the original task ID and preserves other open tasks. Persistent history deletion remains explicit and permanent.

Use a shared 220ms page entrance plus short panel, control and disclosure transitions. No exit animation delays navigation. Respect prefers-reduced-motion. CSS disclosure interpolation progressively enhances browsers that support it; others open normally.

## D33 — Advice is not an evidence audit
The general chat previously challenged every unsupported claim, even during relationship advice and app feedback. Scope validation to outward factual claims, explicit verification requests and material contradictions. User-reported context is a working account, not independently verified fact. Do not gate coaching on a resume or artifacts. Include the selected record's saved context and reviewed conversation summaries in private planning; outward builders remain unchanged. Explicitly explain that local files, GitHub URLs and resumes are not automatically readable.

## D34 — Reviewable networking snapshots
Implement LinkedIn connection CSV, selected messages/text and selected ICS meeting preparation using local parsing only. Preview never commits, sends to a model or fetches external URLs. Explicit per-row decisions create contacts or fill blank fields; name/profile matches are suggestions and never silently merge people. Preserve existing relationship notes and groups. Email addresses are discarded. Keep role/connection date as separate source metadata, not timeline events. Fenced snapshot context may assist private planning without becoming current verified facts.

Selected conversation import requires a user recap and explicit opt-in to retain the selected original text. Unselected messages and raw files are never persisted. Hash receipts prevent repeated imports; export/wipe include source metadata, and permanent deletion removes relevant receipts. No batch Undo is promised. Model suggestions and pasted instructions cannot authorize writes.

Calendar assistance uses a selected local ICS snapshot, with no OAuth or live sync. Keep recorded timezone labels, canceled status and recurrence warning. Never equate invitation with attendance; no recurrence expansion, attendee import, alarm handling, subscription fetching or attachment fetching. Pass one user-selected event to existing preparation only after a click. Keep Gmail/Google/Outlook OAuth and GitHub enrichment as later work.

## D35 — Imagery that supports connection workflows
Three original local SVG scenes represent people, conversations and meetings, in the existing forest/cream/ochre palette. Use illustrations on accessible keyboard-operated source tabs; keep data review controls close to the initial viewport. Art is decorative, has empty alt text, and makes no external requests. Preserve reduced-motion behavior and both themes.

## D36 — Features must be discoverable from the front door
User feedback showed the Sources overview was too hidden behind People/Settings and optional Career tools. Promote Import to primary navigation, and make Today explain the product through three illustrated, actionable paths. Each import CTA must open the requested task with its controls in view, not require finding another tab. Include explicit no-contacts/no-calendar alternatives. Keep optional onboarding import access on the first welcome screen, without forcing questionnaire completion. Preserve daily actions and continuity below the feature map; remove duplicate introductory prompt rows.

Add a browser acceptance check for visible capability buttons at a 1470×956 desktop viewport, direct task routing, main Import navigation, logging/coaching alternatives and fresh-user onboarding bypass. No API or schema changes are needed.

## D37 — Distinct daily workspace and import hub
The feature map on Today repeated Import's three illustrated categories, making the two pages feel identical. Remove the duplicated catalogue from Today. Restore the next action and resume point as its main content, with compact log/preparation/import shortcuts and context-sensitive empty states. Keep Import in primary navigation and retain all reviewed source workflows there. Remove the repeated lower workspace summary links and unused evidence/draft fetches from Today. Keep the first welcome import bypass. First-click acceptance now checks meaningful page differentiation, visible recommended action/shortcuts at laptop sizes, and a substantive empty-state path.
