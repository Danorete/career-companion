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
| D15 | Egress and logs | The live client uses an HTTP transport that only allows `https://api.anthropic.com`. Logs and the activity table hold metadata only (event, IDs, token counts, cost). **Amended by D39:** connector hosts are added one provider at a time, each listed in D39. |
| D16 | Without AI | Every workspace feature (evidence, opportunities, actions, drafts, outcomes, reminders, memory, export) works with AI off, over budget, or failing. |
| D17 | Resume card, reminder, outcomes | Interpreted as: a card showing where you left off on the recommended action; date-based reminders that surface when the app is open (no notifications); one-click outcome buttons (reply, interview, no response, rejection, offer). **Amended by D39:** nudges can now reach the user outside the open app. |
| D19 | Visual direction | "Daylight" layout (light, typographic, open sheet) with the session ring from the "Console" direction, chosen by the user from two mockups on 2026-11-10. Three surfaces: ground (chrome), sheet (work), tint (companion). Space Grotesk for headings, Inter for text, one indigo accent, amber for "waiting for your OK". Light theme only for now. |
| D20 | Fonts and CSP | Both fonts are bundled as files under `static/fonts/` (SIL Open Font License). The policy gained `font-src 'self'` and nothing else; no inline styles, no outside requests. |
| D21 | Companion identity | Working name "Tempo". An orb mark with four states: ready, thinking, waiting for your OK, AI off. The panel resizes (drag or arrow keys) and collapses to a corner pill; both are remembered in the browser as layout preferences only. |
| D22 | First run | Onboarding is a dedicated screen with the companion centred: one question at a time, a progress bar, skip on every question. The workspace appears only afterwards. |
| D23 | Session timer | Starting a session records its start time and length; the ring counts down from that, so it survives a reload. A chat on its own starts no timer. The app never alarms; the companion says once when time is up. |
| D24 | Starter file | Bulk import of the user's own information from a `.json` file they choose and preview. Imported evidence is always stored as an unverified claim; entries carry the provenance `imported_file`; duplicates are skipped; unknown fields are rejected. The user's file is personal data and stays out of the repository. |
| D25 | Setup progress | Five milestones, not a field count: a goal, a project, one verified claim, pasted profile text, one person or role. Shown as a percentage together with "N of 5 steps". Sample rows never count. Live AI is listed as optional and is not part of the percentage, so mock mode is a complete setup. Computed on the server and sent with the bootstrap data; the interface refreshes it on every page render. The sidebar card hides at 100% and can be pinned back from Settings (a browser layout preference). |
| D18 | Out of scope for version one | LinkedIn integration or automation, URL fetching, background AI calls, people discovery, accounts, billing, hosting, desktop packaging, streaming responses. **Amended by D39, D40:** calendar and email sync (not AI) and the official LinkedIn export are in scope; LinkedIn sign-in, scraping, extensions and automation, background AI calls, hosting and accounts stay out. |
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


## D39 — Connectors and nudges, local-first (2026-11-17)
Status: decided, not built. Amends D15, D17 and D18.

Why: the 12-response survey found the stall points were time, energy and forgetting, not fear of networking. Typing every memory by hand is a bottleneck even for the builder. Reminders that only appear when the app is open depend on the same discipline that is failing.

**Principle: capture by default, confirm by exception.** Nothing becomes a person, a promise or a task without a one-tap confirmation (extends D12). Nothing in this decision ends manual input completely. It aims at near-zero typing.

**Sources, in order of build.**
1. Calendar, read-only. Events with at least one outside attendee, or words like "coffee chat" or "career fair", become encounter candidates. Fields kept: title, start and end, attendee names and addresses.
2. Email headers. Fields kept: sender and recipient names and addresses, date, thread id. Subject lines and bodies are not kept by default. Skip no-reply and bulk senders. Create a person only after a two-way exchange.
3. Email bodies, opt-in only, and only user-sent messages in threads with people already in Link, to propose promises ("I'll send you the article"). Rule-based matching runs first. Any text sent to the AI is limited to what D5 allows, and no AI call runs in the background (D18).

**Access.** OAuth with a loopback redirect. Tokens live in Keychain (D14). Each connector adds only its own provider hosts to the egress allowlist (amends D15 and D20), confirmed when it is built: Google APIs for Google accounts, Microsoft Graph for Microsoft accounts. No other outside host. Sync runs on the user's computer, with rate limits, and is not AI.

**Consent.** Each connector shows its fields before it connects: what it reads, what it keeps and what it never reads. Promise: "Reads only what you connect, only these fields, disconnect any time." Disconnect removes the tokens and offers to remove data that came from that source. Delete everything (D13) removes all of it.

**Post-event check-in replaces the manual log.** About an hour after an event ends, Link asks "How did it go with Maya?" with one tap (Great, Fine, Skip) and an optional typed or dictated note. An unanswered check-in expires quietly.

**Nudges outside the app (amends D17).** Channels, in order: a desktop notification from a small local helper, and an event on the user's own calendar. No hosted service in version one.
- At most one nudge a day, at a time the user sets, with quiet hours.
- One action per nudge, plus snooze. Stop after two ignored nudges for the same person.
- Text outside Link is generic, for example "1 follow-up due today. Open Link". Calendar events use a generic title such as "Link: follow-up due". Names appear only inside Link, because a notification or a calendar entry is stored or shown outside the app.
- Limit: local nudges only fire while the computer is on. Phone push needs a hosted relay, which stays out of scope (D18) until it is decided separately. If it is ever built, the relay holds only schedule times and a device token, never contacts.

**Measure.** Typed notes per user per week. If capture works, it falls toward zero.

**Trust copy.** Use these statements, and keep each one true:
- "Reads only what you connect, only these fields, disconnect any time."
- "Never sends a message for you."
- "Never signs in to LinkedIn or browses it for you."
- "Never shares your data with anyone else."
Do not use the old line "Never AI" for Import. AI is optional and clearly labelled, and mock output is shown as mock.

## D40 — LinkedIn data sources (2026-11-17)
Status: decided. Amends D18.

LinkedIn's Help Center says it does not permit third-party software, including browser plug-ins and extensions, that scrape or modify its site (page "Prohibited software and extensions", read as a search excerpt on 2026-11-17; the full page would not load, so read it again before relying on exact wording). Tools that read LinkedIn in the background survive on selective enforcement, and the risk to a restricted account falls on the user.

Allowed:
- The user's own official data export (Settings and privacy, Data privacy, Get a copy of your data), guided in the app with a link to LinkedIn's own instructions, and a monthly "refresh your export" prompt.
- Once email is connected, notification emails LinkedIn sends the user ("accepted your invitation", "new message"), reading names and event type only.
- A profile link the user types or pastes. It is stored as text and never fetched (D18, URL fetching).

Not allowed in the product: LinkedIn sign-in or cookies, scraping, background reading, automated actions, and a browser extension or clipper. A clipper may exist only behind the developer-mode flag, only after the owner has read LinkedIn's current terms, and with a plain warning at install. Do not design anything around avoiding LinkedIn's detection.

## D41 — Each student's data stays theirs (2026-11-17)
Status: decided.

- No pooling. Data from a user's export, calendar or email is never combined across users, shared, resold or used for analytics about other users.
- No reuse. Data from a source is used only for that user.
- Minimal. Keep only the fields D39 lists, because connections' names and addresses are other people's data.
- Deletion works. Disconnect removes a source's tokens and, on request, its data. Delete everything removes all.
- Any future hosted part (for example phone push) holds schedule times and a device token only, and never contacts or message text.
- The Gemini coaching prototype in `gemini-skill/` is a separate test, not part of the product. Text typed into it goes to Google, so it never carries the "stays on your computer" promise.

## D42 — Two versions: user and developer (2026-11-17)
Status: built.

One codebase, one switch. `Settings.ui_mode` is `user` (the default) or `dev`, set by `COMPANION_UI_MODE` or `companion run --mode`. The server reports it in `/api/bootstrap`, and the page applies it once at start.

- **User version:** plain words, no spending meter, no AI-mode or budget controls. One line says when the AI is off, paused for the month, or showing sample answers, so mock output is never presented as real advice.
- **Developer version:** the original wording, the AI budget and the mock/live switch.
- **Words changed in the user version:** Quick log is "Add a note", Import is "Add contacts", Evidence is "What I've done", Roles is "Jobs I'm looking at", Drafts is "My messages", Pasted material is "Things I pasted", Career tools is "More tools". The three first-run choices read "I don't know where to start", "Reach out to someone" and "I just met someone".
- **Not changed:** the API, the schema, the server-side onboarding questions and what the AI is allowed to see. Only labels and which controls show.
- **Why not two copies of the app:** parallel copies already diverged once (`connections-redesign`).
- **Still to do:** most longer sentences inside the workflows are unchanged, the demo banner still says "mock AI", and the Setup list in Settings still says "Unlocks". These belong to a second plain-language pass after testers read it.

## D43 — Calendar connect, first slice (2026-11-17)
Status: built and tested against stand-ins. No real Google sign-in has been tried. Implements the first source of D39.

- **Provider.** Google Calendar, read-only (`calendar.readonly`), primary calendar only. A fictional sample calendar stands in for the demo, so the whole flow can be tried without an account.
- **Sign-in.** OAuth for a Desktop app with PKCE, returning to `http://127.0.0.1:<port>/connect/google/callback`. The refresh token lives in the system keychain through `KeyringSecrets` (D14). The short-lived access token stays in memory. No token is in the database, an export, a log or the page.
- **Request guard (amends D2, one path only).** Google sends the browser back to the callback, which is a cross-site navigation by design. The guard lets exactly `GET /connect/google/callback` through its cross-site check. Every other route still refuses cross-site requests, and the Host check still applies. The callback trusts only a `state` value that is random, works once, expires after 10 minutes, and is held in memory (at most 5 pending). It answers with a small page rather than a redirect, because the browser withholds the session cookie from a redirect chain that began on another site.
- **Outbound traffic (amends D15).** A separate transport lets calendar code reach only `oauth2.googleapis.com` and `www.googleapis.com` over HTTPS. The AI transport is unchanged and still allows only the AI provider. The browser, not Link, opens `accounts.google.com`.
- **Fields.** Link asks Google for event title, start, end, status, recurrence, and attendee name, address and response. It does not ask for descriptions, places or notes. Addresses are kept, as D39 says.
- **What becomes a suggestion.** An event with at least one other human invited, not cancelled, not all-day, not declined by you. Recurring events and groups of more than six need a networking word in the title (coffee, networking, career fair, informational, mentor, meetup, interview, recruiter, alumni and similar). No-reply senders, group calendars and rooms are ignored.
- **Confirm by exception.** Nothing is a person until Keep. Keep saves a person and no conversation, because an invitation does not establish that anyone met. The person is offered as "same as" an existing one when the address or exact name matches. "Not now" hides one event. "Never suggest this person" also stops that address from any later event.
- **No background work.** Checking the calendar is a button. There is no scheduled sync and no AI involved.
- **Disconnect.** Keeps what was found, or removes everything that came from the calendar. People you kept stay in either case. Delete everything also cancels the sign-in, because the keychain is outside the database files.
- **Trust copy.** The page says what Link reads, never reads and never does, and its "No accounts connected" label follows the real state.
- **Schema.** Version 6 adds `encounter_candidates`, included in export and delete.
- **Limits.** 250 events per check, no paging, 21 days back and 14 days ahead. One calendar. No Microsoft sign-in yet.
- **Next.** The post-event check-in, which asks how a meeting went with a tap, is step 4 of the plan.

