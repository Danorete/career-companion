# Graph Report - career-companion  (2026-11-14)

## Corpus Check
- 71 files · ~79,635 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 916 nodes · 2669 edges · 55 communities (41 shown, 14 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dd15a333`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ai.py
- store.py
- create_app
- app.js
- BudgetBlocked
- test_security.py
- Database
- test_workflows.py
- test_validate_and_ranking.py
- cli.py
- network_imports.py
- AllowlistTransport
- CLAUDE.md
- CLAUDE.md
- career-companion
- Web Interface Guidelines
- chrome-devtools
- Progress
- coaching.py
- people.py
- What You Must Do When Invoked
- services.py
- conftest.py
- test_network_imports.py
- Link
- test_ai_gateway.py
- test_people.py
- Career Companion: decision record
- security.py
- link-guide.js
- build_client
- cli.py
- validate_draft
- generate_draft
- graphify reference: extra exports and benchmark
- Connection Studio design pass
- test_double_submit.py
- graphify reference: query, path, explain
- Link — handoff
- graphify reference: commit hook and native CLAUDE.md integration
- db.py
- Guidance
- graphify reference: add a URL and watch a folder
- graphify reference: incremental update and cluster-only
- test_conversation_scope.py
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- extraction-spec.md
- attach_posting
- setup_progress

## God Nodes (most connected - your core abstractions)
1. `Database` - 168 edges
2. `Budget` - 91 edges
3. `Settings` - 88 edges
4. `Gateway` - 73 edges
5. `AIUnavailable` - 72 edges
6. `CompanionTurn` - 66 edges
7. `AIClient` - 58 edges
8. `h()` - 53 edges
9. `Security` - 52 edges
10. `In` - 47 edges

## Surprising Connections (you probably didn't know these)
- `mock_ai()` --calls--> `MockAI`  [INFERRED]
  tests/conftest.py → src/companion/ai.py
- `test_crash_leftover_reservation_becomes_unknown()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_reconcile_sets_total_to_console_figure()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_release_only_frees_never_sent_calls()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `settings()` --calls--> `Settings`  [INFERRED]
  tests/conftest.py → src/companion/config.py

## Import Cycles
- None detected.

## Communities (55 total, 14 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.21
Nodes (14): generate(), Connection coaching: useful before contacts, explicit commitments, private/publi, test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people() (+6 more)

### Community 1 - "store.py"
Cohesion: 0.18
Nodes (20): check_evidence(), _decode(), delete(), due_reminders(), _encode(), get(), insert(), load_sample() (+12 more)

### Community 2 - "create_app"
Cohesion: 0.24
Nodes (19): connections(), messages(), post(), No external services: networking imports are reviewed local snapshots, not live, test_bad_connections_rejected_without_records(), test_calendar_preview_has_no_attendance_or_external_effects(), test_connection_commit_is_atomic_and_foreign_origin_blocked(), test_connections_preview_does_not_commit_or_keep_emails() (+11 more)

### Community 3 - "app.js"
Cohesion: 0.10
Nodes (97): act(), actionForm(), api(), applyMotion(), applyTheme(), arrive(), closeMore(), compareTable() (+89 more)

### Community 4 - "BudgetBlocked"
Cohesion: 0.29
Nodes (10): FastAPI, create_app(), app(), signed_in(), test_everything_manual_works_with_ai_off(), test_exhausted_budget_blocks_ai_but_not_saved_work(), test_model_failure_keeps_the_users_message_and_work(), test_old_transcripts_are_purged_on_start() (+2 more)

### Community 5 - "test_security.py"
Cohesion: 0.09
Nodes (4): Local endpoint protection (decision D2)., A cross-site HTML form can only send form encodings, never JSON., test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "Database"
Cohesion: 0.08
Nodes (102): fastapi_responses, fastapi_staticfiles, Protocol, pydantic, AIClient, AIRequest, AIResult, AIUnavailable (+94 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.09
Nodes (16): done_ids(), evidence(), End-to-end behaviour through the HTTP API, with the mock AI. Synthetic data only, setup(), test_approved_entries_can_be_added_as_confirmed_in_bulk(), test_draft_report_separates_supported_claims_from_gaps(), test_each_setup_step_flips_on_its_own(), test_export_contains_everything_and_wipe_removes_it() (+8 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.15
Nodes (33): datetime, Option, date, rank(), Deterministic recommendation (decision D10). The model never ranks.  Order of co, Return at most `limit` options, best first., _score(), action() (+25 more)

### Community 9 - "cli.py"
Cohesion: 0.10
Nodes (36): argparse, dataclasses, getpass, logging, Namespace, os, pathlib, re (+28 more)

### Community 10 - "network_imports.py"
Cohesion: 0.10
Nodes (34): json, calendar_preview(), confirm_connections(), confirm_messages(), connections_preview(), _csv(), fingerprint(), messages_preview() (+26 more)

### Community 11 - "AllowlistTransport"
Cohesion: 0.29
Nodes (7): make_action(), test_copying_or_saving_a_draft_never_marks_it_sent(), test_data_and_session_progress_survive_restart(), test_invalid_state_jump_is_refused(), test_resume_note_survives_and_is_shown(), test_session_timer_info_and_end(), test_today_opens_on_one_recommendation_with_alternatives()

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.10
Nodes (19): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Done (+11 more)

### Community 21 - "people.py"
Cohesion: 0.07
Nodes (46): _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext, planning_context() (+38 more)

### Community 22 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 23 - "services.py"
Cohesion: 0.12
Nodes (26): now(), active_session(), add_evidence_bulk(), chat_turn(), confirm_all_evidence(), decide_proposal(), end_session(), ensure_session() (+18 more)

### Community 24 - "conftest.py"
Cohesion: 0.18
Nodes (10): fastapi_testclient, pytest, anon(), client(), db(), mock_ai(), Shared fixtures. All data here is synthetic; nothing describes a real person., A browser with no session. (+2 more)

### Community 25 - "test_network_imports.py"
Cohesion: 0.08
Nodes (28): math, BudgetBlocked, cost_usd(), estimate_tokens(), Exception, _rates(), Spend control (decision D7).  Every AI call reserves its worst-case cost before, Align the ledger with the figure the user reads from the provider's Console. (+20 more)

### Community 26 - "Link"
Cohesion: 0.10
Nodes (19): Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Field notebook design (2026-11-13), Guided desktop connection building, Interface reference, Known limitations (+11 more)

### Community 27 - "test_ai_gateway.py"
Cohesion: 0.11
Nodes (31): BaseTransport, httpx2, AllowlistTransport, build_client(), DraftOut, LiveAI, NeverSent, Exception (+23 more)

### Community 28 - "test_people.py"
Cohesion: 0.20
Nodes (14): log(), person(), Connection workflow regressions; synthetic records only., test_chat_switch_does_not_reuse_other_person_history(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_legacy_item_migration_keeps_records(), test_minimal_person_and_unassigned_capture() (+6 more)

### Community 29 - "Career Companion: decision record"
Cohesion: 0.12
Nodes (15): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+7 more)

### Community 30 - "security.py"
Cohesion: 0.22
Nodes (9): secrets, _deny(), make_guard(), Request, Response, Protection for the local HTTP endpoints (decision D2).  Threats covered: a web p, starlette_requests, starlette_responses (+1 more)

### Community 31 - "link-guide.js"
Cohesion: 0.30
Nodes (11): create(), advance(), clear(), draw(), finish(), node(), pause(), position() (+3 more)

### Community 34 - "validate_draft"
Cohesion: 0.22
Nodes (15): _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue(), Any, quantities(), Claim checks for drafts (decision D6).  Machine-checked: evidence IDs exist and (+7 more)

### Community 35 - "generate_draft"
Cohesion: 0.23
Nodes (11): _evidence_map(), generate_draft(), _note_draft_saved(), Autosave is allowed to move suggested -> drafted. It never goes further., Atomically retain the old and new text; unchanged autosaves do not create versio, restore_draft(), save_draft(), snapshot_draft() (+3 more)

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "Connection Studio design pass"
Cohesion: 0.15
Nodes (12): Accent and first-run preview (2026-11-14), Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, Field notebook redesign (2026-11-13), First-click usability correction, Motion and usability follow-up (2026-11-14) (+4 more)

### Community 39 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 40 - "Link — handoff"
Cohesion: 0.33
Nodes (5): Checks and what is still unverified, Link — handoff, Open threads, Run it on your Mac, What the current build contains

### Community 41 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.40
Nodes (4): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration, Source-read freshness

### Community 42 - "db.py"
Cohesion: 0.50
Nodes (3): contextlib, sqlite3, SQLite storage. One connection, one lock, explicit transactions.

### Community 43 - "Guidance"
Cohesion: 0.40
Nodes (4): About Streamline, Guidance, Guidance icons / Streamline, Open-source license

### Community 44 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 45 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **115 isolated node(s):** `npx`, `career-companion`, `graphify`, `Usage`, `What graphify is for` (+110 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `cli.py`, `store.py`, `generate_draft`, `BudgetBlocked`, `test_workflows.py`, `cli.py`, `db.py`, `coaching.py`, `people.py`, `attach_posting`, `services.py`, `setup_progress`, `test_network_imports.py`, `test_ai_gateway.py`, `test_people.py`, `conftest.py`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `Budget` connect `Database` to `cli.py`, `test_ai_gateway.py`, `BudgetBlocked`, `test_network_imports.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `Settings` connect `Database` to `BudgetBlocked`, `test_security.py`, `cli.py`, `services.py`, `conftest.py`, `test_network_imports.py`, `test_ai_gateway.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `Budget` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Budget` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `Settings` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Settings` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `Gateway` (e.g. with `Budget` and `BudgetBlocked`) actually correct?**
  _`Gateway` has 56 INFERRED edges - model-reasoned connections that need verification._