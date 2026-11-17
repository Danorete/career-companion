# Graph Report - career-companion  (2026-11-17)

## Corpus Check
- 72 files · ~76,020 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 2, .woff2 2, .css 2)

## Summary
- 1213 nodes · 3117 edges · 65 communities (46 shown, 19 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 389 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `24022045`
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
- Database
- create
- test_network_imports.py
- Link
- Setting up the Link coach in Gemini
- test_people.py
- cli.py
- validate_draft
- link-guide.js
- onboarding_state
- prices_are_fresh
- Message patterns
- add_evidence_bulk
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
- test_draft_history.py
- test_ai_gateway.py
- create
- follow_up_candidates
- decide_proposal
- store.py
- AllowlistTransport

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 141 edges
2. `Database` - 140 edges
3. `Settings` - 56 edges
4. `h()` - 55 edges
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
- `D29 — Guided desktop connection building (2026-11-12)` --references--> `connection_plans()`  [INFERRED]
  DECISIONS.md → src/companion/app.py
- `Done` --references--> `today()`  [INFERRED]
  PROGRESS.md → src/companion/app.py
- `db()` --calls--> `Database`  [INFERRED]
  tests/conftest.py → src/companion/db.py

## Import Cycles
- None detected.

## Communities (65 total, 19 thin omitted)

### Community 0 - "Budget"
Cohesion: 0.10
Nodes (18): Budget, BudgetBlocked, cost_usd(), _rates(), worst_case_usd(), test_cost_matches_published_prices(), test_crash_leftover_reservation_becomes_unknown(), test_day_and_session_caps() (+10 more)

### Community 1 - "need"
Cohesion: 0.08
Nodes (31): action_add(), action_edit(), action_note(), connection_confirm(), draft_copied(), draft_generate(), draft_restore(), draft_save() (+23 more)

### Community 2 - "create_app"
Cohesion: 0.06
Nodes (34): Workflow improvements, create_app(), action_delete(), actions_list(), ai_readiness(), checkin_answer(), compare(), connection_plan() (+26 more)

### Community 3 - "app.js"
Cohesion: 0.09
Nodes (97): act(), actionForm(), api(), applyMode(), applyTheme(), checkinCard(), closeMenus(), closeMore() (+89 more)

### Community 4 - "network_imports.py"
Cohesion: 0.17
Nodes (18): import_connections(), imported_person_source(), preview_calendar(), preview_connections(), preview_messages(), calendar_preview(), confirm_connections(), confirm_messages() (+10 more)

### Community 6 - "Database"
Cohesion: 0.05
Nodes (51): ActionIn, AssignIn, BulkEntry, ChatIn, CheckinIn, CompareIn, ConfirmAllIn, ConnectionDecision (+43 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (29): done_ids(), evidence(), make_action(), setup(), signed_in(), test_approved_entries_can_be_added_as_confirmed_in_bulk(), test_copying_or_saving_a_draft_never_marks_it_sent(), test_data_and_session_progress_survive_restart() (+21 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.14
Nodes (29): Option, rank(), _score(), action(), check(), codes(), ev(), ids() (+21 more)

### Community 9 - "Settings"
Cohesion: 0.20
Nodes (8): AIClient, build_client(), LiveAI, Profile, Settings, test_default_mode_is_mock(), test_live_mode_with_stale_prices_stays_off(), test_live_mode_without_key_stays_off()

### Community 10 - "network_imports.py"
Cohesion: 0.20
Nodes (17): seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped(), test_item_context_is_opt_in() (+9 more)

### Community 11 - "context.py"
Cohesion: 0.13
Nodes (11): log_suggest(), _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext (+3 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.11
Nodes (17): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Guided desktop continuation — 2026-11-12 (+9 more)

### Community 20 - "coaching.py"
Cohesion: 0.22
Nodes (12): confirm(), ConfirmInput, ConnectionPlan, _decode(), generate(), get_plan(), Input, list_plans() (+4 more)

### Community 21 - "people.py"
Cohesion: 0.07
Nodes (32): first_time_screen(), connection_follow_up_dismiss(), log_assign(), logs_list(), people_list(), person_add(), person_clear(), person_complete() (+24 more)

### Community 22 - "test_connection_coaching.py"
Cohesion: 0.21
Nodes (13): generate(), test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people(), test_plan_persistence_export_delete_and_invalid_input() (+5 more)

### Community 23 - "Database"
Cohesion: 0.13
Nodes (24): Done, Gateway, chat(), session_end(), today(), Database, active_session(), chat_turn() (+16 more)

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
Cohesion: 0.16
Nodes (15): test_a_version_six_database_gains_the_check_in_columns_and_keeps_its_rows(), log(), person(), test_chat_switch_does_not_reuse_other_person_history(), test_demo_never_opens_personal_database(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_legacy_item_migration_keeps_records() (+7 more)

### Community 29 - "cli.py"
Cohesion: 0.06
Nodes (33): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+25 more)

### Community 30 - "validate_draft"
Cohesion: 0.24
Nodes (9): _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue(), quantities(), _strong_words(), _unit() (+1 more)

### Community 31 - "link-guide.js"
Cohesion: 0.38
Nodes (9): advance(), clear(), draw(), finish(), node(), pause(), position(), save() (+1 more)

### Community 32 - "onboarding_state"
Cohesion: 0.29
Nodes (6): bootstrap(), onboarding_answer(), onboarding_skip(), onboarding_answer(), onboarding_state(), setup_progress()

### Community 34 - "Message patterns"
Cohesion: 0.20
Nodes (9): 1. Follow-up after a conversation (four parts), 2. First message to someone you have not met, 3. Thank-you after help or an introduction, 4. Asking for help (advice, review, or an introduction), 5. Reconnecting after silence, Avoid, Keeping a promise ("I'll send you the article"), Message patterns (+1 more)

### Community 35 - "add_evidence_bulk"
Cohesion: 0.27
Nodes (4): evidence_bulk(), evidence_confirm_all(), add_evidence_bulk(), confirm_all_evidence()

### Community 36 - "calendar_provider"
Cohesion: 0.24
Nodes (10): calendar_callback(), calendar_disconnect(), calendar_info(), calendar_provider(), calendar_start(), calendar_status(), calendar_sync(), redirect_uri() (+2 more)

### Community 37 - "Connection Studio design pass"
Cohesion: 0.22
Nodes (8): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, First-click usability correction, Networking sources and imagery, Quality-of-life and motion update, Today / Import differentiation

### Community 38 - "encounters.py"
Cohesion: 0.10
Nodes (26): checkins_due(), encounter_dismiss(), encounters_pending(), now(), _addresses(), answer_checkin(), _candidate(), detect() (+18 more)

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
Cohesion: 0.16
Nodes (16): AIRequest, AIResult, Claim, CompareOut, EvidenceCandidate, ExtractOut, MetricOut, MockAI (+8 more)

### Community 53 - "test_calendar_connect.py"
Cohesion: 0.05
Nodes (59): default_data_dir(), load_google_client_file(), anon(), app(), client(), db(), mock_ai(), settings() (+51 more)

### Community 54 - "test_draft_history.py"
Cohesion: 0.50
Nodes (3): test_restore_revalidates_against_current_evidence_and_rejects_other_draft(), test_schema_one_draft_survives_upgrade_and_first_edit(), test_versions_survive_reopen_restore_and_deduplicate()

### Community 56 - "test_ai_gateway.py"
Cohesion: 0.25
Nodes (17): AIUnavailable, CompanionTurn, DraftOut, ai_smoke(), fake_api(), gateway(), priced_mock(), test_activity_log_holds_metadata_only() (+9 more)

### Community 57 - "create"
Cohesion: 0.25
Nodes (14): create(), afterDisconnect(), calendarConnect(), calendarDraw(), calendarPanel(), calendarRefresh(), connectionPanel(), draw() (+6 more)

### Community 60 - "store.py"
Cohesion: 0.14
Nodes (14): action_state(), evidence_add(), evidence_edit(), sample(), starter_import(), import_starter(), check_evidence(), _decode() (+6 more)

### Community 61 - "AllowlistTransport"
Cohesion: 0.20
Nodes (4): AllowlistTransport, NeverSent, test_egress_allows_the_provider_api(), test_egress_refuses_everything_but_the_provider_api()

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 354 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `Budget`, `need`, `network_imports.py`, `Database`, `test_workflows.py`, `Settings`, `context.py`, `people.py`, `Database`, `cli.py`, `validate_draft`, `onboarding_state`, `prices_are_fresh`, `add_evidence_bulk`, `calendar_provider`, `encounters.py`, `connectors.py`, `ai.py`, `test_calendar_connect.py`, `test_ai_gateway.py`, `follow_up_candidates`, `decide_proposal`, `store.py`?**
  _High betweenness centrality (0.243) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `create_app()` (e.g. with `first_time_screen()` and `.db_path()`) actually correct?**
  _`create_app()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Budget` be split into smaller, more focused modules?**
  _Cohesion score 0.09841269841269841 - nodes in this community are weakly interconnected._
- **Why does `Decisions` connect `cli.py` to `app.js`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Are the 53 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Should `need` be split into smaller, more focused modules?**
  _Cohesion score 0.08377896613190731 - nodes in this community are weakly interconnected._