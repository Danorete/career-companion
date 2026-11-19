# Plain-language backlog (from the D53 audit, 2026-11-19)

An independent copy review found user-visible text that exposes internals (mock or live AI mode, budgets, record context,
provenance, developer labels). The redesign (D53) fixed the items on #connect, the companion and the top of Today. These
58 are left for a later pass. Line numbers were taken before D53 and may have moved; search for the quoted text.

Rules: **HIDE** in the user version; **SHOW ONLY WHEN** the stated condition holds; **REWRITE** in plain words.
The developer version (`pick(dev, user)` first argument) keeps its wording.

## Hide in the user version (18)

- `src/companion/ai.py:184 (rendered at connection-workflows.js:114)` — “[MOCK] This demonstrates how Link helps you choose a starting point.”  
  Duplicates the disclosure and shows a raw tag. Strip '[MOCK]' tags in the user version.
- `src/companion/coaching.py:126 (rendered by connection-workflows.js:117)` — “What remains uncertain · Keep these as questions -> 'This is a general guide, not an interpretation of your information.'”  
  Third copy of the provenance note. For live plans, rename the disclosure 'Things to find out' with no hint.
- `src/companion/static/app.js:1056` — “Your recorded history; dates can stay approximate.”  
  Record jargon that adds no action. The heading alone is enough.
- `src/companion/static/app.js:1137` — “Saving stays local and works without AI. Organizing with Link sends the selected log to your configured provider in live mode.”  
  Developer jargon ('configured provider', 'live mode'). The what-is-sent disclosure already lives in Settings > About the AI (app.js:1582).
- `src/companion/static/app.js:1537-1538, 1547` — “To get reminders while Link is closed, run this once in Terminal: companion nudge --install / If you delete everything, also run “compani…”  
  CLI instructions in the student version. Replace them with a button or the installer. Keep 'It says how many, never who.' (1532), which is privacy.
- `src/companion/static/app.js:1564-1566` — “Starting and stopping Link / To open Link with one click on a Mac, run this once in Terminal… companion launcher --install”  
  Developer setup. Keep only the 'Quit Link' button.
- `src/companion/static/app.js:1576-1577` — “Keep the setup card in the sidebar”  
  Stale control: updateSetupCard (app.js:386) always empties the sidebar card.
- `src/companion/static/app.js:1634-1637` — “Load labelled sample data / Import a starter file · add your projects, goals and to-dos in one step / A starter file is a .json file prep…”  
  Developer seeding tools. Keep 'Remove sample data' only when S.hasSample.
- `src/companion/static/app.js:1649-1650` — “Activity log · events and costs only, never your text (+ raw rows such as 'ai_call  type=chat model=… cost_usd=…')”  
  Exposes cost/ledger internals and event codes.
- `src/companion/static/app.js:1651-1662` — “Live AI readiness / Configured mode: <mode>. Prices: current|need verification. / No successful live connection test recorded. / Run live…”  
  Budget, ledger, provider and configuration jargon. Dev only.
- `src/companion/static/app.js:1719-1721` — “Link / <section> breadcrumb, 'Search ⌘K', 'Local workspace'”  
  Keep it hidden. 'Local workspace' is also false on the web build (data on Link’s server).
- `src/companion/static/app.js:334` — “Everything you add stays on this computer. / Kept on Link’s server during this test. Delete everything removes it.”  
  Privacy note in navigation. It already appears in Settings > Your data (app.js:1632).
- `src/companion/static/app.js:393-395 (rendered by setupPanel at 1575)` — “Optional: turn on live AI / Not counted above. Unlocks real conversation and AI drafting. Mock mode is a complete setup. / How”  
  Mock/live AI-mode jargon.
- `src/companion/static/app.js:423, src/companion/static/index.html:26` — “Ready”  
  An idle system state with no meaning for the student. User version: show no status at idle. Show 'Thinking…' only while S.busy>0 (app.js:425) and 'Waiting for your OK' only when proposals are pending (app.js:426).
- `src/companion/static/app.js:994` — “Add contacts / Bring a LinkedIn export; choose what to keep.”  
  An import prompt with 'export' jargon. Per the owner's directive, imports live in Add > Add contacts (app.js:327).
- `src/companion/static/app.js:999` — “Quick form (next to 'Add person')”  
  A second add path named after its mechanism. Keep only 'Add person' (the guide). The quick form can stay dev-only.
- `src/companion/static/connection-workflows.js:244` — “Possible commitment (unconfirmed): <commitments>”  
  An internal label leaks into user-authored text. Prefill only the plain commitment text.
- `src/companion/static/network-sources.js:211` — “User-selected calendar snapshot (invitation, not attendance): … / Event description (reference data): …”  
  Internal prompt labels end up as user data. Pass the event fields separately, or prefill 'Meeting: <title>, <date>'.

## Show only when relevant (1)

- `src/companion/static/app.js:1028` — “LinkedIn snapshot · source details / Role at export: … · Connected on: … / Imported YYYY-MM-DD. This is not a current employment check or…”  
  Provenance jargon. Rewrite as a small chip: 'From your LinkedIn contacts (Nov 2026) ⓘ'.

## Rewrite in plain words (39)

- `src/companion/ai.py:213-218` — “[mock AI] I'd keep going on “…”. Tell me what's blocking you, or open the draft panel and I'll check the claims against your evidence. / …”  
  Strip the '[mock AI]' tags and 'canned preview' from user-version replies. The mock disclosure already lives in Settings > About the AI (app.js:1581). Optionally add one 'Sample replies' info tooltip in the dock header. 'draft panel / claims / evidence' are dev terms.
- `src/companion/services.py:67-68` — “Nothing is waiting on you. Add an opportunity or a follow-up when one comes up, or park an idea. No need to invent work.”  
  'opportunity' is the internal item kind. Use 'You’re all caught up.'
- `src/companion/services.py:74-76 (reasons from ranking.py:42, 54)` — “With 20 minutes, I'd do one thing: <title>. You already committed to this. Fits your 20 minutes (about 10).”  
  Exposes the ranking parameter: minutes defaults to 20 via the focus-session picker the user never touched. Use 'Next up: Send Jordan the article you mentioned.' Reasons stay behind 'Why this one?'.
- `src/companion/static/app.js:1031-1032` — “ONE THING AN EXPORT CAN’T TELL US / Save private context / toast 'Context saved for planning.' / undo 'Relationship context saved.'”  
  Keep the question 'How do you know Priya?'. Use the button 'Save' and the toast 'Saved.'. Drop the eyebrow.
- `src/companion/static/app.js:1047` — “Your story with this person is still taking shape. A quick log can hold the fragments.”  
  'quick log' is the dev label (user: 'Add a note'). Use 'Nothing yet. Add a note after you talk.'
- `src/companion/static/app.js:1048` — “Private planning notes · Only shared with planning when selected”  
  Exposes the planning-pipeline data flow. Use 'Private notes · Only you see these'.
- `src/companion/static/app.js:1061` — “<n> other open steps are saved under More tools.”  
  'More tools' no longer exists in the user nav (it is now Menu). Use 'You have 2 more steps for Priya' with a link.
- `src/companion/static/app.js:1070-1071` — “Only the recipient name, organization, the context below, your instruction, and public voice preferences go to drafting. Private notes an…”  
  Pipeline jargon ('drafting', 'public voice preferences'). Move it to an info tooltip: 'Link only uses this box and their name. Your private notes stay private.' Label: 'What Link may mention'.
- `src/companion/static/app.js:1075-1076` — “Review before sending. Copying does not mark this sent. / toast 'Recorded as your recap.'”  
  'recap' is record jargon. Use toast 'Saved to Priya’s history.' and the hint 'Read it once before you send it.'
- `src/companion/static/app.js:1080-1081 (values from people.py:215, encounters.py:255)` — “chip 'Historical outcome' / chip entry.source.replaceAll('_',' ') -> 'user recap', 'pasted exchange', 'calendar checkin'”  
  Raw source enums. Map them to 'Your note', 'Pasted chat', 'After a meeting', or show no chip.
- `src/companion/static/app.js:1083-1087` — “Uncertain: … / Possible commitments (not tasks): … / Suggestions: … / Retained original exchange / Logged YYYY-MM-DD”  
  Evidence-status and provenance vocabulary. Show the note and summary. Fold the rest into one 'Details' disclosure with plain labels ('Not sure about', 'Things you might do'). Drop 'Logged …'.
- `src/companion/static/app.js:1089` — “Associated person / Unassigned / toast 'Log association changed.'”  
  Use 'Who was this with?', 'No one yet', toast 'Moved.'
- `src/companion/static/app.js:1090` — “Organize with Link / 'Optional clarification: ' + text / toast(proposal.reason)”  
  Button: 'Tidy this up'. Drop the 'Optional clarification:' prefix. Map reason strings as for app.js:584.
- `src/companion/static/app.js:1097-1101` — “Review facts and preserve uncertainty. Nothing changes until you save. / Original recollection / Reviewed factual summary / Uncertain det…”  
  Use plain labels: 'What happened', 'Short summary', 'Not sure about', 'Things you might do', 'Delete the pasted chat', button 'Save', toast 'Saved.'
- `src/companion/static/app.js:1136` — “Keep the original exchange on this Mac / Unchecked: only your written recap is saved. To retain an exchange without a recap, explicitly c…”  
  Keep the checkbox (retention consent). Replace the paragraph with an info tooltip: 'If unchecked, Link keeps only your note.'
- `src/companion/static/app.js:1139` — “Unassigned · associate when ready”  
  Use 'Not linked to anyone yet'.
- `src/companion/static/app.js:1677-1680` — “This usually means the app stopped running. / Is the terminal window that started the app still open and running? / If you restarted the …”  
  Terminal/dev jargon. Use 'Link isn’t running. Open it from Spotlight, then try again.' Hide 'Details:' in the user version.
- `src/companion/static/app.js:168-169, 174` — “Please check the form: <field> <pydantic msg> / Request failed (<status>)”  
  Developer error text. In the user version, toast 'Something didn’t save. Try again.' and log details to the console.
- `src/companion/static/app.js:171` — “This browser session ended. Stop the app and start it again for a new link.”  
  Recovery is needed, but the wording is technical. Use 'Link restarted. Open Link again from Spotlight.'
- `src/companion/static/app.js:441, 57-58` — ““<text>” as a working preference. / …as a drafting rule. / …as a voice note. / …as a boundary. / …as a constraint.”  
  Shows the internal memory_kind taxonomy. Use 'Remember this? “I prefer mornings”'. Keep 'Nothing is saved until you say so.' (451) for consent, and Save it / No thanks.
- `src/companion/static/app.js:613-615` — “…Paste the job description and I'll line it up against your evidence. / Pick the evidence to lean on, then write it yourself or with me. …”  
  'evidence' is the dev label (the user label is 'What I’ve done', USER_LABELS app.js:37). Use '20 minutes on: <title>. I’ll keep your place.'
- `src/companion/static/app.js:652, 675 (values from store.py:50-54)` — “You left it at: 'Not started.' / 'Draft saved. Not reviewed yet.' / 'Reviewed. Not sent or applied yet: that step is yours, outside this …”  
  Internal state notes written into where_left_off. When the value equals a STATE_NOTE, show an empty input with the placeholder 'Where did you leave it? (optional)', or hide the well until the user has typed something.
- `src/companion/static/app.js:661` — “Drop this? You can bring it back from People & roles.”  
  Stale/dev section name. Use 'Drop this for now? You can bring it back later.'
- `src/companion/static/app.js:761, 763` — “A promise becomes your next step for this person, with a reminder in 3 days. If they already have a next step, it stays and the promise g…”  
  Save-mechanics paragraphs. Fold both into one info tooltip, or show one line: 'Link saves a short note. Skip saves nothing.'
- `src/companion/static/app.js:791 (790 strips it only in the hint)` — “[SAMPLE] <action title>”  
  The raw title prefix leaks. Apply the same clean() the hero uses (app.js:655) everywhere titles render, including the greeting and the chat context title.
- `src/companion/static/app.js:798` — “Park an idea · it waits here and never becomes a to-do on its own”  
  Explains a system guarantee. Use the hint 'for later'.
- `src/companion/static/app.js:826` — “Type options: 'follow up', 'job compare', 'profile edit', 'interview prep' (S.enums.action_kinds with k.replace('_',' '))”  
  Raw enum values, with only the first underscore replaced. Map them to plain labels or drop the field in the user version; 'Importance' and 'Minutes needed' can default.
- `src/companion/static/app.js:941 (used at 813, 1009, 1054)` — “No interaction recorded / <when_text> · approximate / Date unknown”  
  Record jargon. Use 'Not in touch yet' and 'around <when_text>'. Omit 'Date unknown'.
- `src/companion/static/app.js:964-965` — “Profile link (saved only; not fetched) / Context approved for messages / Private planning notes”  
  Data-classification and fetching jargon. Use 'Profile link', 'Okay to mention in messages', 'Private notes (only you)'.
- `src/companion/static/connection-guide.js:257` — “<n> / 2000 · kept in this draft”  
  Shows a character limit and in-memory 'draft' state. Show the counter only above ~1800 characters, and drop '· kept in this draft'.
- `src/companion/static/connection-guide.js:319 (messages from app.js:168-169, 174)` — “<err.message> Your answers are still here. e.g. 'Please check the form: name String should have at most 120 characters' / 'Request failed…”  
  Raw validation and HTTP text. Use 'Couldn’t save just now. Your answers are still here.' plus Try again.
- `src/companion/static/connection-workflows.js:127-128` — “One optional question · You can save without answering / Update the proposal”  
  'proposal' is mechanics. Use the button 'Update my next step' and drop the hint.
- `src/companion/static/connection-workflows.js:241-243 (reason from coaching.py:224)` — “A possible conversation to revisit / 'Your note contains a possible commitment. Confirm what happened before deciding.' / 'Your recorded …”  
  Evidence-status vocabulary ('Unconfirmed', 'recorded conversation'). Use 'You mentioned you might send Priya the article. Still want to?' with buttons 'Yes, help me' / 'Not now'.
- `src/companion/static/index.html:7, app.js:1803` — “Link — Connection Studio”  
  Internal studio codename. Use 'Link'.
- `src/companion/static/network-sources.js:17-18` — “Choose a file smaller than 290 KB. Split larger exports, retaining their CSV header. / Choose a UTF-8 text export, not a ZIP or PDF.”  
  Use 'That file is too big. Try the Connections file from LinkedIn.' / 'Choose the .csv file, not the .zip.'
- `src/companion/static/network-sources.js:204, 206, 210 (notice network_imports.py:214)` — “This is a local snapshot, not a connected account or live calendar sync. / Attendee lists, alarms and subscription links are not imported…”  
  Parser internals. Use 'Pick an event to get ready for.' and the eyebrow 'Repeats' / '<date>'.
- `src/companion/static/network-sources.js:221, 92` — “Your files and an optional read-only calendar · You choose what stays · No LinkedIn automation / Clear imported previews / 'No accounts c…”  
  Mechanism disclaimers and a state indicator. Keep one line, 'You choose who to keep.'. Hide 'Clear imported previews' until a preview exists.
- `src/companion/static/network-sources.js:51, 30 (notice from network_imports.py:92)` — “Filling blanks preserves existing names, organizations, notes and context. Exported role and connection date stay labeled as a snapshot; …”  
  Snapshot and 'closeness score' internals. Keep one privacy line, 'Email addresses are ignored.', and put the rest in an info tooltip.
- `src/companion/static/network-sources.js:86, 212` — “Recap saved. Review it in Quick log or the person’s Conversations tab. / Afterward, use Quick log to record whether you actually met and …”  
  'Quick log' is the dev label (user: 'Add a note'). Use 'Saved to <name>’s history.'
