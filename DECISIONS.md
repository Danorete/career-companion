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
- **Finding it (added after the first real try).** The connection card sits in the calendar tab of Add contacts, which was labelled "Your next meeting" and was easy to miss. In the user version that tab is now "Your calendar" (eyebrow "Connect"), Today shows "Connect your calendar" until a calendar is connected, and the card shows "Loading…" or a plain error instead of staying blank. The developer version keeps the original tab wording (D42).
- **Meet Link button.** The tour launcher was a small pill 12px from the bottom edge, partly under the Link chat bubble. It is now a larger button with a play icon above the bubble, beside the chat panel when it is open, and clear of the welcome screen.

## D44 — Post-event check-in (2026-11-17)
Status: built and tested with frozen time. Not yet tried against a real meeting. Step 4 of D39's plan.

- **Who is asked about.** Only people you kept from a calendar suggestion (D43). A suggestion you never kept is never asked about.
- **When.** One hour after the event ends. A question unanswered for seven days is dropped quietly. Nothing reminds you about it, and nothing in this step runs in the background: the check happens when Today loads.
- **The question.** Today shows one meeting at a time: "How did it go with Maya?" with Great, Fine and Skip. A count says how many more are waiting.
- **What an answer saves.**
  - Great or Fine saves a short note dated to the meeting: the event title, "Went well." or "Went fine.", and any line you added. Answering is how you tell Link the meeting happened, so this is the only path where an invitation turns into a conversation.
  - Skip saves nothing. There is no separate "it didn't happen"; Skip covers it.
  - The note is built only from the event title, your answer and what you typed. No AI is involved and nothing is inferred.
- **Promises.** An optional box ("Did you promise something?") saves the promise in the note and sets it as the person's next step, with a reminder three days later. If the person already has a next step, it is never replaced; the promise stays in the note and the page says so.
- **Records.** The note is an ordinary log (source `calendar_checkin`) and appears in the person's timeline. Removing calendar data later keeps the notes you saved. Schema version 7 adds `checkin_state`, `checkin_at` and `interaction_id` to `encounter_candidates`; version 6 databases gain them without touching rows.
- **Why one tap.** The survey and the builder both found typing a note after every meeting is the bottleneck. This turns it into a tap, with typing optional.
- **Not built.** Dictation, outside-the-app nudges (step 5), a "how did it go?" prompt for meetings you didn't keep, and learning from answers.

## D45 — A calmer first screen: Today, People, Add, Menu (2026-11-17)
Status: built for the user version only. The developer version keeps the full bar and every shortcut (D42).

Why: a first-time user met about 25 things on Today (eight places in the top bar, three ways to add a note, three ways to add people, two floating helpers, and sections for features they had not used yet). The features were right; the visibility was not.

- **Top bar.** Today and People, then **Add** (Add a note, Add contacts, Connect your calendar) and **Menu** (About me, Jobs I'm looking at, What I've done, My messages, Things I pasted, Settings, Take the tour, and a short note about the AI and where data stays). Native `<details>` menus, closed by a click elsewhere, a choice or Escape. Hidden below 1000px, where the mobile tab bar already carries navigation.
- **No spending pill.** The AI note moved into the Menu.
- **Toolbar hidden.** The breadcrumb, a second "Add a note" and the Search button are gone in the user version. The ⌘K search still works from the keyboard.
- **First screen with nobody in Link.** One card, "Start with one person", with the three real steps in order: connect your calendar, keep one person, say how a meeting went. Only the current step shows detail and a button. If calendar sign-in is not available, step 1 becomes "Add someone you know". Quiet links below: add someone by hand, "I don't know anyone yet", take a one-minute tour.
- **Today once there are people.** Header, one setup line only when it matters (people waiting, or a calendar still to connect), the check-in if one is due, then the main next step. Everything else (focus session, conversation to revisit, your people, other to-dos, ideas) sits behind **More for today**, closed.
- **Meet Link.** The floating button is gone in the user version, because it stacked with the Link bubble. It lives in the first-screen card and the Menu. The tour's "Add a note" step now points at the Add button. This reverses the position given to the button earlier the same day, which fixed a real overlap but kept two floaters.
- **Not changed.** Every page, the API, the data and the developer version. People, Add contacts and the rest look as before.
- **Still to do.** The mobile tab bar still lists four sections plus More. A test with three people who have never seen Link, asking "what would you do first?" and timing the first kept person, is the real measure of this change.

## D46 — Reminders outside the app: desktop channel only (2026-11-17)
Status: built and tested with a stand-in notifier. The builder confirmed the test reminder appeared on a real Mac. The login agent has not been installed on a real Mac yet. Step 5 of D39's plan.

- **Channel.** A macOS notification from a small local helper. No server, no hosted service, no AI.
- **What is due.** A person you kept whose meeting is waiting for "How did it go?" (D44), or a pending reminder on an open next step (D17). Several things for one person count once.
- **The words.** "1 follow-up due today. Open Link." or "N follow-ups due today. Open Link." Fixed words and a number, never a name, a title or a note. The macOS command is run without a shell, and a check refuses any quote or backslash in the text.
- **Rules.**
  - Off until you turn it on.
  - At most one reminder a day, at a time you choose, and never inside quiet hours (default 9 pm to 8 am). A reminder time inside quiet hours is refused.
  - If the computer was asleep at the chosen time, the reminder comes later the same day, still outside quiet hours.
  - Pause for 1 to 14 days from Settings.
  - After two reminders in a row for the same person that led nowhere (the person was still due at the next reminder), that person is left out of reminders. They still appear in Link. Acting on it, or choosing "Bring those people back", starts the count again.
  - If macOS can't show the notification, nothing is recorded, so the next pass tries again.
- **The helper.** `companion nudge` does one pass. `companion nudge --install` writes a login agent (`com.career-companion.nudge`) that runs it every 15 minutes, passing along `COMPANION_DATA_DIR` and `COMPANION_TIMEZONE` if set. Installing and removing it is a deliberate Terminal command. The web page can show whether it is installed but cannot install it. The helper's log holds counts only.
- **State.** Settings and bookkeeping are stored as identifiers and counts in the existing key-value table (no schema change). They hold no names.
- **Delete everything** removes the settings but not the login agent, which then finds nothing to do. The page says to run `companion nudge --uninstall`.
- **Deliberately not built: the calendar-event channel from D39.** An event on your own calendar would need Link to write to your calendar. That means a wider Google permission, a new consent screen, and breaking the promise on the connect screen that Link "never adds, changes or deletes an event". It would also put a generic title on Google's servers. It stays out until you decide to trade that promise for it.
- **Limits.**
  - Mac only for now. On other computers the page says so and the test reminder explains why.
  - A reminder cannot open Link, because Link is started from Terminal and its sign-in link works once. You still start Link yourself. A launcher would fix that and is not built.
  - Reminders fire only while the computer is awake and logged in.
  - macOS may need Notifications allowed for Script Editor, which is what `osascript` shows as.

## D47 — One-click start and quit (2026-11-17)
Status: built. `Link.app` was installed and opened Link on the builder's Mac once (2026-11-17). The launcher ran end to end against a real background server on Linux.

Why: a reminder (D46) cannot open Link, and Link started only from Terminal with a link that works once. The reminder said "Open Link" but opening it took a command.

- **`companion launch`.** If Link is running, it asks for a fresh one-time sign-in link and opens it. If not, it starts Link quietly in the background, waits up to 15 seconds, then opens it. If something else is on the port, it says so and starts nothing.
- **How it asks.** A random key is created in the data folder on first start (`launcher.key`, readable by your user only, like the database). `GET /launcher/token` with that key in a header returns a new single-use link that expires after five minutes. Web pages cannot use it: a cross-site request is refused before the route runs, a custom header would need a preflight (refused), and they don't have the key. The page-facing guard (D2) is otherwise unchanged. The first printed link and these minted links are separate, each works once, and wrong guesses count toward the same lockout.
- **Background start.** `companion run --background` prints no link, so no sign-in link ever lands in a log, and it closes the first link. Its output goes to `link.log`, which holds warnings and nothing personal.
- **Quit.** **Quit Link** in the Menu and Settings (`POST /api/quit`, needs a signed-in page) and `companion quit` (`POST /launcher/quit`, needs the key and Link's own origin). Both stop Link the same way as Ctrl+C. The page then says "Link has stopped."
- **`Link.app`.** `companion launcher --install` compiles a small AppleScript app with `osacompile` into `~/Applications/Link.app`. It runs `companion launch` with the same data folder, client-file path, timezone, AI mode, version and port as when it was installed, and shows a dialog pointing to `link.log` if Link can't start. It never copies a Google client ID or secret into the app. Paths with quotes are escaped so they cannot end the script early.
- **Cost of this convenience.** Link keeps running in the background until you quit it, listening only on 127.0.0.1. Anything that can run as your user can read the key file, as it can already read the database (D2).
- **Not done.** A reminder still cannot open Link by itself: clicking a notification shown through `osascript` opens Script Editor, not Link. A possible later experiment is posting the reminder from `Link.app` itself, which is untested. There is no custom icon. On Windows the launcher, the reminders helper and the signal-based quit would each need their own version.


## D48 — Email connection, headers only (2026-11-17)
Status: built and tested on the sample mailbox and in the browser. Not tried with a real Google account.

Why: people you already email are the easiest ones to forget to add. Reading who wrote to whom, and when, removes typing without reading anything private.

- **What it reads.** Sender and recipient names and addresses, plus dates and a few list headers, from your newest 150 sent messages and newest 150 messages you did not send, in any folder (archived replies included). Never a subject, body or attachment. Scope: `gmail.metadata`, which cannot read bodies.
- **Who becomes a suggestion.** Only someone you wrote to who wrote back. One-way mail, newsletters, no-reply addresses and mass messages (more than 5 recipients) never do. A click on **Keep** saves a person and nothing else.
- **Not now** hides someone until newer mail arrives. **Never** stops suggesting that address.
- **Kept people** show "You last wrote them on Nov 12" from dates only. Stored as counts and dates in `email_contacts` (schema 8) plus one key-value row per person.
- **Disconnect** can also remove what came from email; people you kept stay.
- **Launch blocker.** `gmail.metadata` is a restricted Google scope. It works for test users now, but a public release needs Google's security assessment.
- **Deferred.** Detecting promises or parsing LinkedIn notification emails needs subjects or bodies. That would break the headers-only promise, so it is not built.

## D49 — Each data folder keeps its own Google sign-ins (2026-11-17)
Status: built and tested with a stand-in keychain. On the builder's Mac (2026-11-17), the existing sign-in moved over by itself and calendar and email stayed connected. A second folder on a real Mac has not been tried yet.

Why: first-time-user tests happen on the builder's Mac, each tester in a fresh data folder. The keychain is shared by everything running as one Mac user, and sign-ins were saved under fixed names. A tester connecting Google would have replaced the builder's sign-in, and the tester's own sign-in would have stayed on the builder's Mac.

- **Names.** Google sign-ins are saved as `<account>:<folder id>`, where the id is the first 16 hex characters of a SHA-256 of the data folder's full path. A different folder cannot read, replace or delete another folder's entries.
- **No reconnecting.** The usual data folder (the default location) adopts a sign-in saved before this change the first time it reads it, and the old entry is removed. Other folders never adopt it.
- **Ending a test.** Delete everything in the tester's folder cancels that folder's Google sign-ins only.
- **Not covered.** The AI provider key is still one per Mac user. With live AI on, a tester's folder would spend on the owner's key, and each folder has its own monthly cap. Run tests with mock AI.

## D50 — Web version for remote testers, and what it must have before anyone signs in (2026-11-18)
Status: front door built and tested (items 1 to 7, 8 except a live-AI cap, 10). Not yet: email reminders, the sample-data demo for strangers, the feedback button, usage counts, pinned dependencies and the deploy to Railway (9, 11). The Mac app stays as it is.

How it is built: `web.py` is a front door in front of the existing app. It signs people in, checks every request, and hands each request to that person's own copy of the app, which opens only their own database file. The app itself runs unchanged in a `hosted` mode with no launcher, no Quit and no one-time links, and with wording that never says "on this Mac".

Why: most testers are not near the builder, and a web link works on any device. This reverses the local-first rule (D41) for the test run only. The plan for later versions is still to keep people's information on their own device.

What testers are told: during the test, Link keeps their information on Link's server so follow-ups work between visits. It is deleted when they click Delete everything, or automatically after 30 days without signing in. The person running the server could technically see it. A future version will keep everything on their own device.

Must be true before any tester signs in, each with a test:
1. **Only invited people get in.** Sign in with Google (`openid`, email only). An account is created only for an address on the invite list, which matches the Google test users. A stranger with the link gets nothing but the sample-data demo.
2. **Each person's data is separate by construction.** One database file per account. A request can only open the signed-in person's file. Tests try every route as person A against person B's records.
3. **Sessions.** HTTPS only with HSTS. Cookie is `__Host-`, Secure, HttpOnly, SameSite. Server-side session that expires after 7 days idle, a new session on every sign-in, sign-out ends it. CSRF token and origin check on every change, as now. Host allowlist set to the app's own address.
4. **Google sign-ins encrypted at rest.** Calendar and email refresh tokens are encrypted with a key that exists only in the hosting provider's secret settings. Never in the database in plain text, an export, a log or the page.
5. **Secrets live only in the host's secret settings.** Web client secret, encryption key, session key. Never in the repository, which is public.
6. **Logs hold no personal data.** No request bodies, tokens, email addresses or query strings.
7. **Deletion is real.** Delete everything removes the person's database file and cancels their Google sign-ins. A daily job deletes accounts after 30 days without a sign-in. No backups during the test, so deleted means deleted.
8. **Limits.** Sign-in and request rate limits per person and per address, the existing request size limits, sample AI by default with a spending cap if live AI is ever turned on.
9. **Pinned dependencies** with a vulnerability audit before every deploy.
10. **No admin page** for browsing anyone's data.
11. **Re-check before sharing.** The full check from 2026-11-18 is run again against the deployed site, plus a header and TLS scan of the live address, before the LinkedIn post goes out.

Not possible to promise: perfect security. These are layered defenses, each tested, reviewed by the same tool that wrote them. An independent review has not been done.

## D51 — Idea: two ways to start, with an optional guided start that doubles as research (2026-11-19)
Status: idea from the builder, noted only. Not decided, not built.

The idea: a new person picks how to begin.
- **Start from zero.** The app as it is now.
- **Walk me through it.** A guide helps them log their first connection, step by step. Along the way it asks a few
  questions like the ones in the Google feedback form. One flow does two jobs: setting up their first connection, and
  showing the builder who is using Link and how, so updates follow real use.

Promised with it: this is declared up front, and only data that belongs to the study is used.

Points to settle when it is designed (not decisions yet):
- Agreeing to answer study questions is a separate, optional choice from using Link. Saying no still gives the full
  guided start, just without the questions.
- Study answers are kept apart from the person's contacts and notes, never include a contact's details, and say in
  the disclosure what is collected, why, for how long, and that Delete everything removes them.
- Only what the study needs: their answers and simple counts (for example, finished the first connection: yes/no).
- If the findings are used for a class, a paper or anything published, check first whether the school's research
  ethics board (IRB) needs to review it. Product feedback alone usually doesn't.
- The web version runs with sample AI for now, so the guide would follow a fixed script rather than live AI, unless
  live AI is turned on with a spending cap.
- It builds on what exists: the welcome screen ("What do you need help with?"), the guided walkthrough, and the
  planned feedback button and usage counts (D50).

## D52 — A step-by-step guide for adding a person, first and every time after (2026-11-19)
Status: built and tested (17 tests, a browser check). The study questions from D51 are not part of it.

Why: adding someone was a blank form, and typing everything at once is the bottleneck the survey found. A guide that
asks one short question at a time, and shows Link responding to each answer, makes the first person easy and every
later one quick.

What it is:
- **Two ways to begin (D51).** The welcome screen offers "Walk me through it" (recommended) or "Start on my own".
  The guide is also on the start card, the empty Today screen, the Add menu ("Add a person") and the People page
  (Add person; Quick form keeps the old form).
- **Four questions, then a review.** Who (a name is enough; where they work is optional), how you met and when
  (tap a choice or write your own), what you remember (sentence starters), one small next step with a reminder.
  Every question but the name can be skipped. The review has an Edit link for each answer.
- **People Link already found** in the calendar or email are offered on the first question. Picking one keeps that
  suggestion, as pressing Keep would, and the guide adds the rest.
- **One save.** `POST /api/guide/connection` checks every answer before writing anything, then saves the person, a
  dated note (what you remember, or how you met when that is all there is) and the next step with its reminder.

Feedback and motion, from research:
- Nielsen Norman Group's response-time limits: under 0.1 s needs no indicator; a spinner that flashes for less than
  a second makes people anxious. So the save button says "Saving…" at once, and its spinner appears only after 0.4 s.
  Moving progress makes people willing to wait about three times longer, so progress fills as you go.
- Visibility of system status: a live preview card fills in as you type, and the line that just changed glows briefly.
  The preview's status reads "Not saved yet", "Saving…", then "Saved".
- From onboarding teardowns (Flow, Evernote, ROBIN, Inbound via CXL): say how long it takes ("about a minute"), show
  "Step 2 of 4", make the first real success the goal, and let unsure steps be skipped. Optional steps say "Skip this"
  until answered, then "Continue".
- Success is confirmed item by item: a drawn check mark, then each saved thing appears in turn.
- Motion is short (150 to 450 ms) and stops entirely when the system asks for reduced motion. Focus moves to each new
  question and a screen reader hears the step. A chosen chip's tick is drawn with CSS borders, not a character,
  because generated text would become part of the button's spoken name.

Found and fixed while building it: the page label crashed on any page not in the navigation list; the error screen
and the expired-session message said "terminal window" on the web version; the duplicate-name hint missed people
added earlier in the same visit.

## D53 — A calm, one-column start and a floating companion (2026-11-19)
Status: built and tested (a new browser check, older checks updated, an adversarial review). People keeps its two-panel
layout for now.

Adversarial review (2026-11-19): 36 reviewers in four lenses (accessibility, behavior, visual, trust) found 32 issues;
skeptics confirmed 31 (about 20 distinct) and all are fixed, with regression checks for the serious ones. The modal
chat now also blocks nodes added while it is open, leaves the toast and native dialogs alone, and closes before the
search palette opens. Tips step aside as soon as typing starts or they would cover the focused control (only real
controls count: the page itself takes focus after every navigation), Escape on a tip keeps focus at the sprite, and a
hide timer can no longer swallow the next tip. The one-tap Save names the person it saves to, quotes the exact note it
would keep, words the box by who the note goes with, and leaves a note Link wrote itself unticked. Restored on the page:
the referral limit ("Link can’t tell you whether someone will say yes") and the event-availability limit. Live AI plans
are labelled; with live AI the chat chip says "Using your notes on Priya". The tour advances when the person closes the
chat instead of closing it on a timer. Also fixed: a literal "null" on the review page, leftover side-column rules that
reflowed pages, the welcome margin from 601 to 680px, the developer tour button on the phone tab bar, and the off state
of the tips switch (now over 5:1).

Why: a coworker who saw the demo found it too much for a first-time user. Measured before the change at 1280 to 1440
wide: #connect showed 193 words in three competing columns (a marketing panel, the question, and the companion panel);
at 1024 the marketing panel clipped its own headline ("Rememb…", "awkwar…"); Today printed a stray "null".

What changed:
- **#connect is one question and three cards** in a centered 640px column: "What do you need help with?", then "I don’t
  know where to start" (No contacts needed), "Reach out to someone" (We’ll help you find the words), "I just met
  someone" (Write down what you remember; opens the step-by-step guide, D52, in the user version). A first visit adds a
  quiet "Skip for now" (the second way to begin, D51). Visible words on first paint: 193 to 60 in the app (69% fewer),
  166 to 59 on the first-visit welcome (64% fewer). Imports live in Add; the privacy note and the CC BY icon credit
  live in Settings.
- **One question at a time after a card.** One box, one button that waits for words, and the promise "Nobody gets
  contacted. You decide what to keep." stays on the page (not only in a tip, since tips can be turned off). Extra
  fields sit under "Add more detail".
- **Save in one tap.** The review shows the suggested step and name prefilled and "Keep my note with them" ticked, all
  visible and editable before Save; everything else is under "More options". Sample (mock) answers say so in plain
  words. The developer version keeps the original form, labels and the AI encounter flow for "Make sense of an
  encounter".
- **The companion is a floating sprite.** A 64px button bottom-right (56px on phones, above the tab bar) that breathes
  very slightly when idle. The chat opens as a drawer over the page at every width (a bottom sheet on phones): a
  dialog that takes focus, makes everything outside it unreachable, closes on Escape or an outside click, and returns
  focus to where it came from. Nothing about the page's layout changes when it opens. The old column, resize handle
  and stored panel width are gone.
- **Tips.** One or two sentences beside the sprite after something happens. Confirmations ("Saved. Your next step is
  waiting on Today.") replace that save's toast and fall back to the toast when they can't show, so each save is
  confirmed once. Suggestions ("Want help writing to Priya?") show at most once each, 3 per visit and 30 s apart. No tip
  appears while typing or while the chat is open; each hides after 5.5 s, pauses on hover or focus, has "Turn off tips"
  and a close button, and is spoken by one polite live region without moving focus. A switch (role=switch, fixed
  label) in the chat header and in Settings turns tips on and off; the choice is remembered in this browser.
- **Technical states hidden in the user version.** No "Ready · mock replies" (the chat says "Sample replies" only while
  answers are samples), no "A little clarity" panel, no "Clear record context" (a chip "About Priya ×" instead), no
  "Your saved preparation" list (one "Pick up where you left off →" line). The sample banner says "These are practice
  people".
- **Fixed along the way:** the stray "null" on Today; the sprite's face disappearing in dark mode (its colors now come
  from the theme); class-name collisions between the tour and the guide; chat replies scrolling the whole page; the
  tour getting stuck behind the modal drawer (it now closes the drawer through `window.LinkCompanion`); iPhone zoom on
  13px inputs (16px on touch screens); missing safe-area insets (`viewport-fit=cover`).

Research and review:
- The ui-ux-pro-max design-system search (variance 2, motion 2, density 2) pointed to minimal, spacious, subtle motion;
  its palette and web fonts were not adopted (the forest-green theme stays, and the security policy allows only local
  fonts). Its UX guidance set the details: visible 2px focus, focus never hidden under floating UI (WCAG 2.4.11),
  transient messages of a few seconds, at most one or two animated elements per view, reduced motion honored,
  balanced headline wrapping with a bounded measure.
- A four-lens audit (copy, layout, companion behavior, technical labels) ran before building; its copy, companion and
  layout findings are applied above. Its 58 remaining plain-language fixes outside these screens are listed in
  `docs/plain-language-backlog.md`.

Not done here: People as a single column (it still uses a directory and a workspace with an inner scroller); server-side
text such as "[MOCK]" tags in sample answers and the ranking wording in Today's greeting ("With 20 minutes, I'd do one
thing…"); the backlog file above.

## D54 — The first screen says what Link is and where each choice leads (2026-11-19)
Status: built and tested (the companion browser check covers it).

Why: after D53 the first screen was calm but assumed context. A brand-new user could not tell what Link is for, what
each card would do, or where "Skip for now" goes.

- **One line under the question** (first visit only): "Link remembers who you met, what you talked about, and what
  to say next." It fits on one line from tablet width up; on phones it wraps to two.
- **Card lines say the outcome**, each true to the screen it opens:
  - I don’t know where to start: "No contacts needed. Explore ideas and find one small first step."
  - Reach out to someone: "Get help writing a first message. Start with just a name; nothing is sent." (It starts
    from what you type, not from saved notes; the message help is on its review screen.)
  - I just met someone: "Save a few quick details now, so you remember them later." (the step-by-step guide)
- **Skip says where it goes**: a quiet underlined "Skip for now" with "Goes straight to Today, your home screen." as its
  description (aria-describedby), so its name stays short.
- **The browser tab** reads "Link · Remember the people you meet" instead of the internal name "Connection Studio".
- Phones get a 16px side margin on the welcome screen, which it lacked.
- Measured visible words (same method as D53): the first-visit screen rises from 59 to 89, which is 46% fewer than
  before D53 (166) and below D53's 60% target, a trade made on purpose for clarity. The in-app #connect shares the new
  card lines and rises from 60 to 69, still 64% fewer than before (193). The developer version keeps its original
  card wording.

## D55 — How Link works, a progress tracker, and a walkthrough on practice data (2026-11-19)
Status: built and tested (`tests/test_journey.py`, `scripts/check_walkthrough_browser.py`; the older browser checks
were updated for the new first screen).

Why: a tester who used Link with no guidance asked for a starting page and a step-by-step tutorial, a more specific
"I don't know where to start", and plain explanations of how everything works, what it is for, and why Link asks for
each thing. People who arrive confused need the reason, not only the question.

- **How Link works (`#start`) is the first screen** in the user version; the developer version keeps the D53/D54
  welcome. It says what Link is; where things are kept (`here()` wording: "this computer" on the Mac, "your account"
  on the web); that Link never contacts anyone; and how sample answers work when Link's AI is not on (expected, not an
  error, and not advice written for you). It gives three concrete starting points:
  - "I met or noticed someone recently…" leads to Add a person or Add a note.
  - "I don't have a specific person in mind yet" leads to About me, What I've done or Jobs I'm looking at, or to
    Explore ideas with Link. It also points to People and Today.
  - "I want to see the whole thing first" starts the walkthrough.

  The page then explains why Link asks each question, including the four optional boxes under Add more detail. Every
  way in from a first visit finishes the first stage: `POST /api/journey/oriented` sets the same flag as Skip. Later,
  the page is in Menu, More (phones), Settings, search, and the tracker on Today.
- **How far you've come.** Four stages: Start here, Groundwork, People & notes, Reaching out. The server computes them
  from real records only (`GET /api/journey`, also in bootstrap). Samples never count and the tour never writes.
  - Groundwork: any memory, evidence, saved job or pasted text.
  - People & notes: a person or a note.
  - Reaching out: a kept plan, a drafted message, an outcome, or a finished outreach or follow-up step. A suggestion on
    its own is not progress.

  Stages can finish in any order; the current one is the first not done. The tracker shows on How Link works and, in a
  compact form, at the top of Today until every stage is done (once more to mark the finish). When a stage finishes,
  the bar grows from where this viewer last saw it, the dot draws its check, and Link says "Stage done: …" as a tip, or
  through the live region when tips are off.
- **The walkthrough** (`link-walkthrough.js`): 33 steps in the same four parts, over the real app, with a practice
  person (Maya Chen). It follows embedded-uiux-walkthrough: real components, demo-only data, a no-write sandbox, a
  pointer that moves and clicks, a spotlight, typed narration, and `data-tour` hooks. While it runs:
  - every request goes through a sandbox. Lists answer with the practice person only, saves are answered in memory, and
    nothing but a read reaches the server;
  - the page is inert: clicks, typing, search (Cmd/Ctrl+K) and screen readers stay in the card;
  - leaving reloads the page, so nothing from the tour lingers in memory. The tour won't start over a message with
    unsaved changes.

  Controls: Back, Pause/Play (moving on by itself, with a thin timer line), Replay step, Next, Skip to the app, Esc.
  The last step offers Add my first person, Back to How Link works, Replay the tour, and Back. The tour's own tracker is
  dashed and striped, says "Part n of 4" and "Practice only", and sits in a card marked "Practice tour · nothing is
  saved", so it can't pass for real progress. With reduced motion the text appears at once and nothing moves on by
  itself.
- **Why we ask.** Reach out shows a "Why we ask:" line under each question and a reason under each optional box, linked
  with `aria-describedby`. Each says what the answer is for, so it stays true whether the answer comes from Link's AI, a
  sample or the general guide. Checked against `coaching.py`: the goal never reaches a drafted message, and "Anything
  you're happy to mention" is the only background a drafted message may use.
- **Sample answers.** The user version's review says "Sample answer: Link’s AI isn’t switched on in this version, so
  this shows what a next step looks like. It wasn’t written from your answer." It no longer shows the "[MOCK]" tag; the
  developer version keeps it.
- **"I don't know where to start"** on Connect now leads to the three starting points. Its helper line: "See three
  common ways to begin, and pick the one that sounds like you."
- **Also:**
  - Page titles match the menu in the user version: What I've done, Jobs I'm looking at, Things I pasted, My messages.
  - Fixed: opening Add a person again from a menu after a save tried to draw a sixth question, and the page failed to
    load.
- **Motion.** transitions.dev tokens: 150, 250, 400 and 500 ms; ease-out for things entering, ease-in-out for things
  moving. web-animation-design rules: transform and opacity only, interface changes under 300 ms, and a reduced-motion
  rule for every animation. The pointer's glide and the typing are demonstrations, so they run longer.

## D56 — Opening Link after an update shows the update, and git pull can open it (2026-11-19)
Status: built and tested (`tests/test_launcher.py`, `scripts/check_launcher_end_to_end.py`).

Why: three times the builder ran `git pull` and expected the new Link, but `git pull` only downloads code, and opening
Link handed back the copy already running, which still runs the code it started with.

- **Each running copy says which code it runs.** The launcher's key-protected `/launcher/token` now returns a fingerprint
  of Link's own files (paths, sizes and modification times of its .py, .js, .css, .html and .svg files). A pull rewrites
  the files it changes, so the fingerprint moves. A false alarm only costs a restart.
- **Opening Link restarts an older copy.** `companion launch` (and so `Link.app`) compares the running copy's
  fingerprint with the code on disk. When they differ, it stops the old copy, starts the new code, and says "Restarted
  Link with the update". A copy started before this change gives no fingerprint, so it counts as older. If the old
  copy won't stop, it says to use Menu > Quit Link and nothing else happens.
- **git pull can open Link.** `companion launcher --install` also writes a git `post-merge` hook in this checkout, so a
  pull that brings changes opens Link: `Link.app` on a Mac when installed, otherwise `companion launch` with the
  settings carried from the install. It never carries a secret.
  - The hook is marked as Link's. A hook that someone else wrote is never replaced or removed.
  - A shared hooks folder (`core.hooksPath`) is skipped, because a hook there would open Link after a pull in every
    repository.
  - `--status` reports the hook; `--uninstall` removes it with the app.
- Not part of this: pulling updates automatically. Link never runs git by itself; the person decides when to update.
