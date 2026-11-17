# Graph Report - career-companion  (2026-11-17)

## Corpus Check
- 67 files · ~66,077 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 2, .woff2 2, .css 2)

## Summary
- 1012 nodes · 2561 edges · 57 communities (39 shown, 18 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 311 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c8d47f49`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ai.py
- store.py
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
- Career Companion: decision record
- rows
- link-guide.js
- delete
- db.py
- Message patterns
- RuleError
- local_today
- Connection Studio design pass
- add_evidence_bulk
- Coaching playbook
- Link — handoff
- Link Coach
- Guidance
- Plain language
- Examples
- Link Coach: paste-ready Gem
- confirm_all_evidence
- suggest_log
- decide_proposal

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 123 edges
2. `Database` - 123 edges
3. `h()` - 51 edges
4. `Settings` - 50 edges
5. `Budget` - 47 edges
6. `In` - 39 edges
7. `render()` - 38 edges
8. `api()` - 35 edges
9. `BudgetBlocked` - 34 edges
10. `act()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `Decisions` --references--> `fx()`  [INFERRED]
  DECISIONS.md → src/companion/static/app.js
- `app()` --calls--> `create_app()`  [INFERRED]
  tests/conftest.py → src/companion/app.py
- `test_old_transcripts_are_purged_on_start()` --calls--> `create_app()`  [INFERRED]
  tests/test_workflows.py → src/companion/app.py
- `Done` --references--> `today()`  [INFERRED]
  PROGRESS.md → src/companion/app.py
- `D29 — Guided desktop connection building (2026-11-12)` --references--> `connection_plans()`  [INFERRED]
  DECISIONS.md → src/companion/app.py

## Import Cycles
- None detected.

## Communities (57 total, 18 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.05
Nodes (62): AIClient, AIRequest, AIResult, AIUnavailable, AllowlistTransport, build_client(), Claim, CompanionTurn (+54 more)

### Community 1 - "store.py"
Cohesion: 0.16
Nodes (18): action_add(), action_state(), idea_add(), idea_decide(), import_add(), memory_add(), reminder_add(), wipe() (+10 more)

### Community 2 - "create_app"
Cohesion: 0.08
Nodes (24): create_app(), action_edit(), action_note(), ai_smoke(), chat(), compare(), draft_copied(), draft_generate() (+16 more)

### Community 3 - "app.js"
Cohesion: 0.10
Nodes (92): act(), actionForm(), api(), applyMode(), applyTheme(), closeMore(), compareTable(), composeStudio() (+84 more)

### Community 4 - "network_imports.py"
Cohesion: 0.16
Nodes (19): import_connections(), import_messages(), imported_person_source(), preview_calendar(), preview_connections(), preview_messages(), calendar_preview(), confirm_connections() (+11 more)

### Community 5 - "test_security.py"
Cohesion: 0.05
Nodes (13): anon(), app(), client(), db(), mock_ai(), settings(), test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback() (+5 more)

### Community 6 - "Database"
Cohesion: 0.05
Nodes (47): ActionIn, AssignIn, BulkEntry, ChatIn, CompareIn, ConfirmAllIn, ConnectionDecision, ConnectionsConfirmIn (+39 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (29): done_ids(), evidence(), make_action(), setup(), signed_in(), test_approved_entries_can_be_added_as_confirmed_in_bulk(), test_copying_or_saving_a_draft_never_marks_it_sent(), test_data_and_session_progress_survive_restart() (+21 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.09
Nodes (38): Option, rank(), _score(), _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue() (+30 more)

### Community 9 - "config.py"
Cohesion: 0.10
Nodes (11): ai_readiness(), prices_are_fresh(), _delete_key(), main(), _run(), _set_key(), _status(), default_data_dir() (+3 more)

### Community 10 - "network_imports.py"
Cohesion: 0.20
Nodes (17): seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped(), test_item_context_is_opt_in() (+9 more)

### Community 11 - "context.py"
Cohesion: 0.15
Nodes (8): _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext, planning_context()

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.10
Nodes (19): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Done (+11 more)

### Community 20 - "coaching.py"
Cohesion: 0.13
Nodes (17): connection_follow_ups(), connection_plan(), connection_practice(), confirm(), ConfirmInput, ConnectionPlan, _decode(), follow_up_candidates() (+9 more)

### Community 21 - "people.py"
Cohesion: 0.10
Nodes (30): connection_follow_up_dismiss(), log_add(), log_assign(), logs_list(), people_list(), person_add(), person_clear(), person_edit() (+22 more)

### Community 22 - "test_connection_coaching.py"
Cohesion: 0.21
Nodes (13): generate(), test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people(), test_plan_persistence_export_delete_and_invalid_input() (+5 more)

### Community 23 - "Database"
Cohesion: 0.13
Nodes (27): Gateway, bootstrap(), Database, load_demo(), active_session(), chat_turn(), end_session(), ensure_session() (+19 more)

### Community 24 - "create"
Cohesion: 0.24
Nodes (8): create(), choose(), history(), messageTools(), practiceTools(), review(), skip(), start()

### Community 25 - "test_network_imports.py"
Cohesion: 0.24
Nodes (18): connections(), messages(), post(), test_bad_connections_rejected_without_records(), test_calendar_preview_has_no_attendance_or_external_effects(), test_connection_commit_is_atomic_and_foreign_origin_blocked(), test_connections_preview_does_not_commit_or_keep_emails(), test_import_metadata_exported_and_wiped() (+10 more)

### Community 26 - "Link"
Cohesion: 0.11
Nodes (18): Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Guided desktop connection building, Interface reference, Known limitations, Link (+10 more)

### Community 27 - "Setting up the Link coach in Gemini"
Cohesion: 0.17
Nodes (11): Important: build a skill, not a Gem, Links to recheck, Setting up the Link coach in Gemini, Sharing with testers, Steps, Test it before sharing (10 minutes), What this prototype can and can't test, What to measure with testers (+3 more)

### Community 28 - "test_people.py"
Cohesion: 0.20
Nodes (13): log(), person(), test_chat_switch_does_not_reuse_other_person_history(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_legacy_item_migration_keeps_records(), test_minimal_person_and_unassigned_capture(), test_retention_is_explicit() (+5 more)

### Community 29 - "Career Companion: decision record"
Cohesion: 0.10
Nodes (19): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+11 more)

### Community 30 - "rows"
Cohesion: 0.17
Nodes (12): Workflow improvements, actions_list(), draft_versions(), drafts_list(), evidence_list(), ideas_list(), imports_list(), items_list() (+4 more)

### Community 31 - "link-guide.js"
Cohesion: 0.38
Nodes (10): advance(), clear(), draw(), finish(), node(), pause(), position(), save() (+2 more)

### Community 32 - "delete"
Cohesion: 0.20
Nodes (11): action_delete(), connection_plan_delete(), draft_delete(), evidence_delete(), import_delete(), item_delete(), log_delete(), memory_delete() (+3 more)

### Community 33 - "db.py"
Cohesion: 0.25
Nodes (3): test_restore_revalidates_against_current_evidence_and_rejects_other_draft(), test_schema_one_draft_survives_upgrade_and_first_edit(), test_versions_survive_reopen_restore_and_deduplicate()

### Community 34 - "Message patterns"
Cohesion: 0.20
Nodes (9): 1. Follow-up after a conversation (four parts), 2. First message to someone you have not met, 3. Thank-you after help or an introduction, 4. Asking for help (advice, review, or an introduction), 5. Reconnecting after silence, Avoid, Keeping a promise ("I'll send you the article"), Message patterns (+1 more)

### Community 35 - "RuleError"
Cohesion: 0.20
Nodes (7): evidence_add(), evidence_edit(), person_next(), starter_import(), import_starter(), check_evidence(), RuleError

### Community 36 - "local_today"
Cohesion: 0.22
Nodes (8): connection_confirm(), log_edit(), outcome_add(), person_complete(), reminder_snooze(), sample(), local_today(), remove_sample()

### Community 37 - "Connection Studio design pass"
Cohesion: 0.22
Nodes (8): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, First-click usability correction, Networking sources and imagery, Quality-of-life and motion update, Today / Import differentiation

### Community 39 - "Coaching playbook"
Cohesion: 0.29
Nodes (6): After (the first 48 hours matter), Before a conversation (coffee chat, career fair, meetup), Coaching playbook, During, I don't know where to start (no contacts yet), When students say...

### Community 40 - "Link — handoff"
Cohesion: 0.33
Nodes (5): Checks and what is still unverified, Link — handoff, Open threads, Run it on your Mac, What the current build contains

### Community 41 - "Link Coach"
Cohesion: 0.29
Nodes (6): Drafting messages, How to help, Link Coach, References (read when needed), Rules you never break, Start of every chat

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

## Knowledge Gaps
- **2 isolated node(s):** `npx`, `career-companion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 301 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `ai.py`, `store.py`, `network_imports.py`, `test_security.py`, `Database`, `test_workflows.py`, `test_validate_and_ranking.py`, `config.py`, `Progress`, `coaching.py`, `people.py`, `Database`, `Career Companion: decision record`, `rows`, `delete`, `RuleError`, `local_today`, `add_evidence_bulk`, `confirm_all_evidence`, `suggest_log`, `decide_proposal`?**
  _High betweenness centrality (0.340) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `create_app()` (e.g. with `Settings` and `.db_path()`) actually correct?**
  _`create_app()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `npx`, `career-companion` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ai.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05215123859191656 - nodes in this community are weakly interconnected._
- **Why does `connection_plans()` connect `Career Companion: decision record` to `create_app`, `coaching.py`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `create_app` be split into smaller, more focused modules?**
  _Cohesion score 0.07777777777777778 - nodes in this community are weakly interconnected._