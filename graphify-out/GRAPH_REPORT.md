# Graph Report - career-companion  (2026-11-17)

## Corpus Check
- 76 files · ~80,504 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 2, .woff2 2, .css 2)

## Summary
- 1308 nodes · 3421 edges · 78 communities (53 shown, 25 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 400 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e101dfbf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Budget
- store.py
- create_app
- app.js
- network_imports.py
- test_security.py
- Database
- test_workflows.py
- test_validate_and_ranking.py
- Settings
- network_imports.py
- context.py
- CLAUDE.md
- CLAUDE.md
- career-companion
- Web Interface Guidelines
- chrome-devtools
- Progress
- coaching.py
- people.py
- test_connection_coaching.py
- services.py
- create
- test_network_imports.py
- Link
- Setting up the Link coach in Gemini
- test_people.py
- cli.py
- validate_draft
- link-guide.js
- test_nudges.py
- prices_are_fresh
- Message patterns
- add_evidence_bulk
- Database
- Connection Studio design pass
- encounters.py
- Coaching playbook
- Link — handoff
- Link Coach
- connectors.py
- Guidance
- Plain language
- Examples
- Link Coach: paste-ready Gem
- ai.py
- test_calendar_connect.py
- generate_draft
- test_ai_gateway.py
- create
- nudges.py
- decide_proposal
- local_today
- AllowlistTransport
- check_user_mode_browser.py
- config.py
- rank
- MockAI
- rows
- insert
- nudge_agent.py
- delete
- check_nudges_browser.py
- LiveAI
- confirm_all_evidence
- import_starter

## God Nodes (most connected - your core abstractions)
1. `Database` - 154 edges
2. `create_app()` - 149 edges
3. `Settings` - 58 edges
4. `h()` - 57 edges
5. `Budget` - 47 edges
6. `In` - 44 edges
7. `render()` - 39 edges
8. `api()` - 37 edges
9. `BudgetBlocked` - 34 edges
10. `act()` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Decisions` --references--> `fx()`  [INFERRED]
  DECISIONS.md → src/companion/static/app.js
- `D43 — Calendar connect, first slice (2026-11-17)` --references--> `KeyringSecrets`  [INFERRED]
  DECISIONS.md → src/companion/keys.py
- `test_old_transcripts_are_purged_on_start()` --calls--> `create_app()`  [INFERRED]
  tests/test_workflows.py → src/companion/app.py
- `Done` --references--> `today()`  [INFERRED]
  PROGRESS.md → src/companion/app.py
- `D29 — Guided desktop connection building (2026-11-12)` --references--> `connection_plans()`  [INFERRED]
  DECISIONS.md → src/companion/app.py

## Import Cycles
- None detected.

## Communities (78 total, 25 thin omitted)

### Community 0 - "Budget"
Cohesion: 0.11
Nodes (17): Budget, cost_usd(), _rates(), worst_case_usd(), test_cost_matches_published_prices(), test_crash_leftover_reservation_becomes_unknown(), test_day_and_session_caps(), test_haiku_long_prompt_is_five_times_dearer() (+9 more)

### Community 1 - "store.py"
Cohesion: 0.13
Nodes (23): action_edit(), action_note(), action_state(), chat(), draft_copied(), draft_generate(), draft_restore(), draft_save() (+15 more)

### Community 2 - "create_app"
Cohesion: 0.07
Nodes (27): create_app(), bootstrap(), calendar_callback(), calendar_disconnect(), calendar_info(), calendar_provider(), calendar_start(), calendar_status() (+19 more)

### Community 3 - "app.js"
Cohesion: 0.09
Nodes (99): act(), actionForm(), api(), applyMode(), applyTheme(), checkinCard(), closeMenus(), closeMore() (+91 more)

### Community 4 - "network_imports.py"
Cohesion: 0.17
Nodes (18): import_connections(), imported_person_source(), preview_calendar(), preview_connections(), preview_messages(), calendar_preview(), confirm_connections(), confirm_messages() (+10 more)

### Community 6 - "Database"
Cohesion: 0.05
Nodes (53): ActionIn, AssignIn, BulkEntry, ChatIn, CheckinIn, CompareIn, ConfirmAllIn, ConnectionDecision (+45 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (29): done_ids(), evidence(), make_action(), setup(), signed_in(), test_approved_entries_can_be_added_as_confirmed_in_bulk(), test_copying_or_saving_a_draft_never_marks_it_sent(), test_data_and_session_progress_survive_restart() (+21 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.29
Nodes (16): check(), codes(), ev(), test_banned_phrase_blocks_in_claim_and_in_body(), test_banned_phrase_matches_whole_words_only(), test_do_not_claim_confidential_and_wrong_use_block(), test_edited_out_claim_is_reported(), test_number_absent_from_evidence_blocks() (+8 more)

### Community 9 - "Settings"
Cohesion: 0.27
Nodes (6): run(), build_client(), Settings, test_default_mode_is_mock(), test_live_mode_with_stale_prices_stays_off(), test_live_mode_without_key_stays_off()

### Community 10 - "network_imports.py"
Cohesion: 0.20
Nodes (17): seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped(), test_item_context_is_opt_in() (+9 more)

### Community 11 - "context.py"
Cohesion: 0.17
Nodes (11): log_suggest(), _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext (+3 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.10
Nodes (19): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Done (+11 more)

### Community 20 - "coaching.py"
Cohesion: 0.15
Nodes (17): Gateway, connection_follow_ups(), connection_plan(), connection_practice(), confirm(), ConfirmInput, ConnectionPlan, _decode() (+9 more)

### Community 21 - "people.py"
Cohesion: 0.12
Nodes (27): log_assign(), logs_list(), people_list(), person_add(), person_clear(), person_edit(), keep(), assign_log() (+19 more)

### Community 22 - "test_connection_coaching.py"
Cohesion: 0.21
Nodes (13): generate(), test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people(), test_plan_persistence_export_delete_and_invalid_input() (+5 more)

### Community 23 - "services.py"
Cohesion: 0.16
Nodes (16): compare(), evidence_extract(), session_end(), active_session(), chat_turn(), end_session(), ensure_session(), extract_evidence() (+8 more)

### Community 24 - "create"
Cohesion: 0.24
Nodes (8): create(), choose(), history(), messageTools(), practiceTools(), review(), skip(), start()

### Community 25 - "test_network_imports.py"
Cohesion: 0.24
Nodes (18): connections(), messages(), post(), test_bad_connections_rejected_without_records(), test_calendar_preview_has_no_attendance_or_external_effects(), test_connection_commit_is_atomic_and_foreign_origin_blocked(), test_connections_preview_does_not_commit_or_keep_emails(), test_import_metadata_exported_and_wiped() (+10 more)

### Community 26 - "Link"
Cohesion: 0.10
Nodes (20): Connect Google Calendar (optional), Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Guided desktop connection building, Interface reference, Known limitations (+12 more)

### Community 27 - "Setting up the Link coach in Gemini"
Cohesion: 0.17
Nodes (11): Important: build a skill, not a Gem, Links to recheck, Setting up the Link coach in Gemini, Sharing with testers, Steps, Test it before sharing (10 minutes), What this prototype can and can't test, What to measure with testers (+3 more)

### Community 28 - "test_people.py"
Cohesion: 0.21
Nodes (12): log(), person(), test_chat_switch_does_not_reuse_other_person_history(), test_demo_never_opens_personal_database(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_minimal_person_and_unassigned_capture(), test_retention_is_explicit() (+4 more)

### Community 29 - "cli.py"
Cohesion: 0.07
Nodes (24): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+16 more)

### Community 30 - "validate_draft"
Cohesion: 0.22
Nodes (10): _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue(), quantities(), _strong_words(), _unit() (+2 more)

### Community 31 - "link-guide.js"
Cohesion: 0.38
Nodes (9): advance(), clear(), draw(), finish(), node(), pause(), position(), save() (+1 more)

### Community 32 - "test_nudges.py"
Cohesion: 0.08
Nodes (39): _delete_key(), main(), _run(), _set_key(), _status(), _tip_if_client_file_is_open(), delete_api_key(), get_api_key() (+31 more)

### Community 34 - "Message patterns"
Cohesion: 0.20
Nodes (9): 1. Follow-up after a conversation (four parts), 2. First message to someone you have not met, 3. Thank-you after help or an introduction, 4. Asking for help (advice, review, or an introduction), 5. Reconnecting after silence, Avoid, Keeping a promise ("I'll send you the article"), Message patterns (+1 more)

### Community 36 - "Database"
Cohesion: 0.13
Nodes (15): calendar_sync(), Database, _addresses(), _candidate(), matches(), pending(), _remember_address(), status() (+7 more)

### Community 37 - "Connection Studio design pass"
Cohesion: 0.22
Nodes (8): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, First-click usability correction, Networking sources and imagery, Quality-of-life and motion update, Today / Import differentiation

### Community 38 - "encounters.py"
Cohesion: 0.13
Nodes (15): now(), answer_checkin(), detect(), disconnect(), dismiss(), due_checkins(), _ended(), guess_name() (+7 more)

### Community 39 - "Coaching playbook"
Cohesion: 0.29
Nodes (6): After (the first 48 hours matter), Before a conversation (coffee chat, career fair, meetup), Coaching playbook, During, I don't know where to start (no contacts yet), When students say...

### Community 40 - "Link — handoff"
Cohesion: 0.33
Nodes (5): Checks and what is still unverified, Link — handoff, Open threads, Run it on your Mac, What the current build contains

### Community 41 - "Link Coach"
Cohesion: 0.29
Nodes (6): Drafting messages, How to help, Link Coach, References (read when needed), Rules you never break, Start of every chat

### Community 42 - "connectors.py"
Cohesion: 0.06
Nodes (9): _b64(), ConnectorError, ConnectorTransport, GoogleCalendar, NeverSent, normalize_google(), OAuthFlows, SampleCalendar (+1 more)

### Community 43 - "Guidance"
Cohesion: 0.40
Nodes (4): About Streamline, Guidance, Guidance icons / Streamline, Open-source license

### Community 44 - "Plain language"
Cohesion: 0.33
Nodes (5): Honest privacy wording (say this if asked, or at the start if the student seems worried), Plain language, What Link is (use if someone asks), What not to promise, Words to use

### Community 47 - "Examples"
Cohesion: 0.40
Nodes (4): Example 1: starting from zero, Example 2: following up and keeping a promise, Example 3: a student who froze, Examples

### Community 48 - "Link Coach: paste-ready Gem"
Cohesion: 0.50
Nodes (3): Instructions (paste everything below this line into the Instructions box), Knowledge files to upload (Gem editor → Knowledge → Add files), Link Coach: paste-ready Gem

### Community 51 - "ai.py"
Cohesion: 0.24
Nodes (15): AIClient, AIResult, Claim, CompareOut, EvidenceCandidate, ExtractOut, MetricOut, Profile (+7 more)

### Community 53 - "test_calendar_connect.py"
Cohesion: 0.08
Nodes (47): load_google_client_file(), attendee(), _client_file(), event(), google(), maya(), ok_handler(), Provider (+39 more)

### Community 54 - "generate_draft"
Cohesion: 0.23
Nodes (9): _evidence_map(), generate_draft(), _note_draft_saved(), restore_draft(), save_draft(), snapshot_draft(), test_restore_revalidates_against_current_evidence_and_rejects_other_draft(), test_schema_one_draft_survives_upgrade_and_first_edit() (+1 more)

### Community 56 - "test_ai_gateway.py"
Cohesion: 0.23
Nodes (17): AIUnavailable, CompanionTurn, DraftOut, ai_smoke(), fake_api(), gateway(), priced_mock(), test_activity_log_holds_metadata_only() (+9 more)

### Community 57 - "create"
Cohesion: 0.25
Nodes (14): create(), afterDisconnect(), calendarConnect(), calendarDraw(), calendarPanel(), calendarRefresh(), connectionPanel(), draw() (+6 more)

### Community 58 - "nudges.py"
Cohesion: 0.12
Nodes (20): nudges_info(), nudges_pause(), _nudge(), build_notifier(), due_keys(), _eligible(), get_settings(), get_state() (+12 more)

### Community 60 - "local_today"
Cohesion: 0.17
Nodes (10): connection_confirm(), import_messages(), log_add(), log_edit(), outcome_add(), person_complete(), sample(), local_today() (+2 more)

### Community 61 - "AllowlistTransport"
Cohesion: 0.20
Nodes (4): AllowlistTransport, NeverSent, test_egress_allows_the_provider_api(), test_egress_refuses_everything_but_the_provider_api()

### Community 65 - "config.py"
Cohesion: 0.14
Nodes (7): default_data_dir(), anon(), client(), db(), mock_ai(), settings(), test_user_version_is_the_default()

### Community 67 - "rank"
Cohesion: 0.26
Nodes (12): Option, rank(), _score(), action(), ids(), test_at_most_three_options_and_closed_actions_excluded(), test_existing_commitment_beats_a_more_important_new_idea(), test_fit_to_available_time_and_reasons() (+4 more)

### Community 68 - "MockAI"
Cohesion: 0.22
Nodes (3): AIRequest, MockAI, _signed_in()

### Community 69 - "rows"
Cohesion: 0.15
Nodes (13): Workflow improvements, actions_list(), draft_versions(), drafts_list(), evidence_list(), ideas_list(), imports_list(), items_list() (+5 more)

### Community 70 - "insert"
Cohesion: 0.17
Nodes (11): action_add(), evidence_add(), idea_add(), import_add(), item_add(), item_posting(), memory_add(), reminder_add() (+3 more)

### Community 71 - "nudge_agent.py"
Cohesion: 0.33
Nodes (5): install(), is_installed(), plist_bytes(), plist_path(), uninstall()

### Community 72 - "delete"
Cohesion: 0.20
Nodes (11): action_delete(), connection_plan_delete(), draft_delete(), evidence_delete(), import_delete(), item_delete(), log_delete(), memory_delete() (+3 more)

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 381 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `Budget`, `store.py`, `network_imports.py`, `Database`, `test_workflows.py`, `Settings`, `context.py`, `Progress`, `coaching.py`, `people.py`, `services.py`, `cli.py`, `validate_draft`, `test_nudges.py`, `prices_are_fresh`, `add_evidence_bulk`, `Database`, `encounters.py`, `connectors.py`, `ai.py`, `test_calendar_connect.py`, `test_ai_gateway.py`, `nudges.py`, `decide_proposal`, `local_today`, `check_user_mode_browser.py`, `MockAI`, `rows`, `insert`, `nudge_agent.py`, `delete`, `confirm_all_evidence`, `import_starter`?**
  _High betweenness centrality (0.255) - this node is a cross-community bridge._
- **Are the 55 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 55 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Budget` be split into smaller, more focused modules?**
  _Cohesion score 0.10752688172043011 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `Database` to `Budget`, `store.py`, `create_app`, `Database`, `test_workflows.py`, `Settings`, `context.py`, `coaching.py`, `people.py`, `services.py`, `test_nudges.py`, `add_evidence_bulk`, `encounters.py`, `ai.py`, `generate_draft`, `test_ai_gateway.py`, `nudges.py`, `decide_proposal`, `local_today`, `AllowlistTransport`, `config.py`, `MockAI`, `rows`, `insert`, `delete`, `LiveAI`, `confirm_all_evidence`, `import_starter`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `create_app()` (e.g. with `first_time_screen()` and `.db_path()`) actually correct?**
  _`create_app()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `store.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12666666666666668 - nodes in this community are weakly interconnected._