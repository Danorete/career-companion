# Graph Report - career-companion  (2026-11-17)

## Corpus Check
- 72 files · ~74,576 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 2, .woff2 2, .css 2)

## Summary
- 1204 nodes · 3091 edges · 66 communities (48 shown, 18 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 385 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `77c7a3cd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Budget
- need
- create_app
- app.js
- network_imports.py
- test_security.py
- Database
- test_workflows.py
- test_validate_and_ranking.py
- config.py
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
- Database
- create
- test_network_imports.py
- Link
- Setting up the Link coach in Gemini
- test_people.py
- cli.py
- test_checkins.py
- link-guide.js
- db.py
- budget.py
- Message patterns
- .from_env
- calendar_provider
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
- conftest.py
- test_ai_gateway.py
- create
- follow_up_candidates
- Secrets
- local_today
- AllowlistTransport
- attach_posting

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 140 edges
2. `Database` - 140 edges
3. `Settings` - 55 edges
4. `h()` - 52 edges
5. `Budget` - 47 edges
6. `In` - 42 edges
7. `render()` - 39 edges
8. `api()` - 36 edges
9. `BudgetBlocked` - 34 edges
10. `act()` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Decisions` --references--> `fx()`  [INFERRED]
  DECISIONS.md → src/companion/static/app.js
- `D43 — Calendar connect, first slice (2026-11-17)` --references--> `KeyringSecrets`  [INFERRED]
  DECISIONS.md → src/companion/keys.py
- `app()` --calls--> `create_app()`  [INFERRED]
  tests/conftest.py → src/companion/app.py
- `test_old_transcripts_are_purged_on_start()` --calls--> `create_app()`  [INFERRED]
  tests/test_workflows.py → src/companion/app.py
- `Done` --references--> `today()`  [INFERRED]
  PROGRESS.md → src/companion/app.py

## Import Cycles
- None detected.

## Communities (66 total, 18 thin omitted)

### Community 0 - "Budget"
Cohesion: 0.10
Nodes (18): Budget, BudgetBlocked, cost_usd(), _rates(), worst_case_usd(), test_cost_matches_published_prices(), test_crash_leftover_reservation_becomes_unknown(), test_day_and_session_caps() (+10 more)

### Community 1 - "need"
Cohesion: 0.10
Nodes (30): action_add(), action_edit(), action_note(), chat(), draft_copied(), draft_generate(), draft_restore(), draft_save() (+22 more)

### Community 2 - "create_app"
Cohesion: 0.06
Nodes (36): Workflow improvements, create_app(), action_delete(), action_state(), actions_list(), bootstrap(), calendar_info(), calendar_status() (+28 more)

### Community 3 - "app.js"
Cohesion: 0.10
Nodes (93): act(), actionForm(), api(), applyMode(), applyTheme(), checkinCard(), closeMore(), compareTable() (+85 more)

### Community 4 - "network_imports.py"
Cohesion: 0.16
Nodes (19): import_connections(), import_messages(), imported_person_source(), preview_calendar(), preview_connections(), preview_messages(), calendar_preview(), confirm_connections() (+11 more)

### Community 6 - "Database"
Cohesion: 0.05
Nodes (51): ActionIn, AssignIn, BulkEntry, ChatIn, CheckinIn, CompareIn, ConfirmAllIn, ConnectionDecision (+43 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (29): done_ids(), evidence(), make_action(), setup(), signed_in(), test_approved_entries_can_be_added_as_confirmed_in_bulk(), test_copying_or_saving_a_draft_never_marks_it_sent(), test_data_and_session_progress_survive_restart() (+21 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.09
Nodes (39): drafts_list(), Option, rank(), _score(), _banned(), _check_number(), _evidence_quantities(), _has_phrase() (+31 more)

### Community 10 - "network_imports.py"
Cohesion: 0.20
Nodes (17): seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped(), test_item_context_is_opt_in() (+9 more)

### Community 11 - "context.py"
Cohesion: 0.16
Nodes (9): _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext, planning_context() (+1 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.10
Nodes (19): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Done (+11 more)

### Community 20 - "coaching.py"
Cohesion: 0.14
Nodes (18): AIUnavailable, Gateway, ai_smoke(), connection_confirm(), connection_plan(), connection_practice(), confirm(), ConfirmInput (+10 more)

### Community 21 - "people.py"
Cohesion: 0.09
Nodes (32): connection_follow_up_dismiss(), log_assign(), log_suggest(), logs_list(), people_list(), person_add(), person_clear(), person_edit() (+24 more)

### Community 22 - "test_connection_coaching.py"
Cohesion: 0.21
Nodes (13): generate(), test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people(), test_plan_persistence_export_delete_and_invalid_input() (+5 more)

### Community 23 - "Database"
Cohesion: 0.08
Nodes (35): evidence_bulk(), evidence_confirm_all(), proposal_decide(), starter_import(), Database, active_session(), add_evidence_bulk(), chat_turn() (+27 more)

### Community 24 - "create"
Cohesion: 0.24
Nodes (8): create(), choose(), history(), messageTools(), practiceTools(), review(), skip(), start()

### Community 25 - "test_network_imports.py"
Cohesion: 0.24
Nodes (18): connections(), messages(), post(), test_bad_connections_rejected_without_records(), test_calendar_preview_has_no_attendance_or_external_effects(), test_connection_commit_is_atomic_and_foreign_origin_blocked(), test_connections_preview_does_not_commit_or_keep_emails(), test_import_metadata_exported_and_wiped() (+10 more)

### Community 26 - "Link"
Cohesion: 0.10
Nodes (19): Connect Google Calendar (optional), Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Guided desktop connection building, Interface reference, Known limitations (+11 more)

### Community 27 - "Setting up the Link coach in Gemini"
Cohesion: 0.17
Nodes (11): Important: build a skill, not a Gem, Links to recheck, Setting up the Link coach in Gemini, Sharing with testers, Steps, Test it before sharing (10 minutes), What this prototype can and can't test, What to measure with testers (+3 more)

### Community 28 - "test_people.py"
Cohesion: 0.17
Nodes (15): test_a_version_six_database_gains_the_check_in_columns_and_keeps_its_rows(), log(), person(), test_chat_switch_does_not_reuse_other_person_history(), test_demo_never_opens_personal_database(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_legacy_item_migration_keeps_records() (+7 more)

### Community 29 - "cli.py"
Cohesion: 0.06
Nodes (34): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+26 more)

### Community 30 - "test_checkins.py"
Cohesion: 0.28
Nodes (12): clock(), due(), kept(), logs(), test_a_promise_becomes_the_next_step_with_a_reminder(), test_a_promise_never_replaces_a_next_step_you_already_have(), test_asked_an_hour_after_the_meeting_and_expired_after_a_week(), test_disconnecting_and_removing_calendar_data_keeps_the_notes_you_saved() (+4 more)

### Community 31 - "link-guide.js"
Cohesion: 0.51
Nodes (9): advance(), clear(), draw(), finish(), node(), pause(), position(), save() (+1 more)

### Community 32 - "db.py"
Cohesion: 0.21
Nodes (5): checkins_due(), due_checkins(), _ended(), _now(), _parse()

### Community 33 - "budget.py"
Cohesion: 0.22
Nodes (3): ai_readiness(), estimate_tokens(), prices_are_fresh()

### Community 34 - "Message patterns"
Cohesion: 0.20
Nodes (9): 1. Follow-up after a conversation (four parts), 2. First message to someone you have not met, 3. Thank-you after help or an introduction, 4. Asking for help (advice, review, or an introduction), 5. Reconnecting after silence, Avoid, Keeping a promise ("I'll send you the article"), Message patterns (+1 more)

### Community 35 - ".from_env"
Cohesion: 0.20
Nodes (9): load_google_client_file(), _client_file(), test_a_wrong_client_file_gives_a_plain_error_without_its_contents(), test_detection_rules(), test_google_client_settings_come_from_the_environment(), test_the_downloaded_desktop_client_file_is_read(), test_the_two_variables_override_the_file(), test_bootstrap_tells_the_page_which_version_to_show() (+1 more)

### Community 36 - "calendar_provider"
Cohesion: 0.38
Nodes (7): calendar_callback(), calendar_disconnect(), calendar_provider(), calendar_start(), redirect_uri(), wipe(), mark_connected()

### Community 37 - "Connection Studio design pass"
Cohesion: 0.22
Nodes (8): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, First-click usability correction, Networking sources and imagery, Quality-of-life and motion update, Today / Import differentiation

### Community 38 - "encounters.py"
Cohesion: 0.12
Nodes (21): calendar_sync(), encounters_pending(), now(), _addresses(), answer_checkin(), _candidate(), detect(), disconnect() (+13 more)

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
Cohesion: 0.13
Nodes (24): AIClient, AIRequest, AIResult, build_client(), Claim, CompareOut, EvidenceCandidate, ExtractOut (+16 more)

### Community 53 - "test_calendar_connect.py"
Cohesion: 0.18
Nodes (18): attendee(), event(), maya(), Provider, signed_in(), test_a_guessed_name_can_be_corrected_and_blank_is_refused(), test_a_known_address_is_offered_as_the_same_person(), test_a_name_is_guessed_from_the_address_and_marked_as_a_guess() (+10 more)

### Community 54 - "conftest.py"
Cohesion: 0.14
Nodes (9): anon(), app(), client(), db(), mock_ai(), settings(), test_only_google_hosts_over_https_can_be_reached(), test_ui_mode_must_be_user_or_dev() (+1 more)

### Community 56 - "test_ai_gateway.py"
Cohesion: 0.32
Nodes (15): CompanionTurn, DraftOut, fake_api(), gateway(), priced_mock(), test_activity_log_holds_metadata_only(), test_budget_block_never_reaches_the_client(), test_failed_call_is_charged_conservatively() (+7 more)

### Community 57 - "create"
Cohesion: 0.25
Nodes (14): create(), afterDisconnect(), calendarConnect(), calendarDraw(), calendarPanel(), calendarRefresh(), connectionPanel(), draw() (+6 more)

### Community 59 - "Secrets"
Cohesion: 0.27
Nodes (8): google(), ok_handler(), Secrets, test_a_refused_refresh_removes_the_saved_sign_in_and_shows_a_safe_message(), test_authorize_url_uses_pkce_state_and_read_only_scope(), test_events_ask_google_only_for_the_fields_link_keeps(), test_full_sign_in_through_the_callback_without_a_session_cookie(), test_the_callback_with_a_wrong_state_connects_nothing()

### Community 60 - "local_today"
Cohesion: 0.20
Nodes (8): log_add(), log_edit(), person_complete(), sample(), local_today(), due_reminders(), load_sample(), remove_sample()

### Community 61 - "AllowlistTransport"
Cohesion: 0.22
Nodes (4): AllowlistTransport, NeverSent, test_egress_allows_the_provider_api(), test_egress_refuses_everything_but_the_provider_api()

### Community 62 - "attach_posting"
Cohesion: 0.50
Nodes (3): item_add(), item_posting(), attach_posting()

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 350 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `Budget`, `need`, `network_imports.py`, `Database`, `test_workflows.py`, `test_validate_and_ranking.py`, `config.py`, `Progress`, `coaching.py`, `people.py`, `Database`, `cli.py`, `db.py`, `budget.py`, `calendar_provider`, `encounters.py`, `connectors.py`, `ai.py`, `test_calendar_connect.py`, `conftest.py`, `follow_up_candidates`, `local_today`, `attach_posting`?**
  _High betweenness centrality (0.245) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `create_app()` (e.g. with `.db_path()` and `app()`) actually correct?**
  _`create_app()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Budget` be split into smaller, more focused modules?**
  _Cohesion score 0.10099573257467995 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `Database` to `Budget`, `need`, `create_app`, `Database`, `test_workflows.py`, `config.py`, `context.py`, `coaching.py`, `people.py`, `test_people.py`, `cli.py`, `db.py`, `budget.py`, `calendar_provider`, `encounters.py`, `ai.py`, `conftest.py`, `test_ai_gateway.py`, `follow_up_candidates`, `local_today`, `AllowlistTransport`, `attach_posting`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 53 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Should `need` be split into smaller, more focused modules?**
  _Cohesion score 0.10227272727272728 - nodes in this community are weakly interconnected._