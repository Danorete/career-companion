# Graph Report - career-companion  (2026-11-13)

## Corpus Check
- 67 files · ~72,664 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 886 nodes · 2594 edges · 53 communities (45 shown, 8 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b2e28967`
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
- validate_draft
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
- config.py
- test_network_imports.py
- Link
- test_ai_gateway.py
- test_people.py
- Career Companion: decision record
- AllowlistTransport
- link-guide.js
- Usage
- generate_draft
- conftest.py
- security.py
- graphify reference: extra exports and benchmark
- Connection Studio design pass
- make_action
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

## God Nodes (most connected - your core abstractions)
1. `Database` - 167 edges
2. `Budget` - 91 edges
3. `Settings` - 88 edges
4. `Gateway` - 73 edges
5. `AIUnavailable` - 72 edges
6. `CompanionTurn` - 66 edges
7. `AIClient` - 58 edges
8. `Security` - 52 edges
9. `h()` - 50 edges
10. `In` - 47 edges

## Surprising Connections (you probably didn't know these)
- `mock_ai()` --calls--> `MockAI`  [INFERRED]
  tests/conftest.py → src/companion/ai.py
- `test_cost_matches_published_prices()` --calls--> `cost_usd()`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_haiku_long_prompt_is_five_times_dearer()` --calls--> `cost_usd()`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_crash_leftover_reservation_becomes_unknown()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_reconcile_sets_total_to_console_figure()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py

## Import Cycles
- None detected.

## Communities (53 total, 8 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.14
Nodes (19): httpx2, AIRequest, AIResult, Claim, CompareOut, EvidenceCandidate, ExtractOut, MetricOut (+11 more)

### Community 1 - "store.py"
Cohesion: 0.11
Nodes (24): Align the ledger with the figure the user reads from the provider's Console., now(), Activity log. Callers pass identifiers and counts, never user content., decide_proposal(), Only reachable from an authenticated, CSRF-checked user request., check_evidence(), _decode(), delete() (+16 more)

### Community 2 - "create_app"
Cohesion: 0.29
Nodes (10): FastAPI, create_app(), app(), signed_in(), test_everything_manual_works_with_ai_off(), test_exhausted_budget_blocks_ai_but_not_saved_work(), test_model_failure_keeps_the_users_message_and_work(), test_old_transcripts_are_purged_on_start() (+2 more)

### Community 3 - "app.js"
Cohesion: 0.10
Nodes (90): act(), actionForm(), api(), applyTheme(), closeMore(), compareTable(), composeStudio(), connectionMotif() (+82 more)

### Community 4 - "BudgetBlocked"
Cohesion: 0.12
Nodes (19): BudgetBlocked, Exception, A new AI call was refused by a spending rule. `reason` is safe to show the user., Upper bound: all input billed as a cache write (the dearest input rate), full ou, worst_case_usd(), Open reservations are committed spend, so parallel calls cannot overshoot the st, test_cost_matches_published_prices(), test_crash_leftover_reservation_becomes_unknown() (+11 more)

### Community 5 - "test_security.py"
Cohesion: 0.09
Nodes (4): Local endpoint protection (decision D2)., A cross-site HTML form can only send form encodings, never JSON., test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "Database"
Cohesion: 0.13
Nodes (74): fastapi_responses, fastapi_staticfiles, Protocol, AIClient, AIUnavailable, CompanionTurn, Gateway, AI could not be used. `reason` is safe to show. Saved work is unaffected. (+66 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.09
Nodes (16): done_ids(), evidence(), End-to-end behaviour through the HTTP API, with the mock AI. Synthetic data only, setup(), test_approved_entries_can_be_added_as_confirmed_in_bulk(), test_draft_report_separates_supported_claims_from_gaps(), test_each_setup_step_flips_on_its_own(), test_export_contains_everything_and_wipe_removes_it() (+8 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.15
Nodes (33): datetime, Option, date, rank(), Deterministic recommendation (decision D10). The model never ranks.  Order of co, Return at most `limit` options, best first., _score(), action() (+25 more)

### Community 9 - "cli.py"
Cohesion: 0.14
Nodes (20): getpass, logging, Namespace, prices_are_fresh(), date, _delete_key(), main(), Command line entry point: `companion run`, `companion set-key`, `companion delet (+12 more)

### Community 10 - "network_imports.py"
Cohesion: 0.10
Nodes (35): json, re, calendar_preview(), confirm_connections(), confirm_messages(), connections_preview(), _csv(), fingerprint() (+27 more)

### Community 11 - "validate_draft"
Cohesion: 0.22
Nodes (15): _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue(), Any, quantities(), Claim checks for drafts (decision D6).  Machine-checked: evidence IDs exist and (+7 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.11
Nodes (17): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Daily home / Import separation, Done, Guided desktop continuation — 2026-11-12 (+9 more)

### Community 20 - "coaching.py"
Cohesion: 0.06
Nodes (44): pydantic, confirm(), ConnectionPlan, _decode(), follow_up_candidates(), generate(), get_plan(), list_plans() (+36 more)

### Community 21 - "people.py"
Cohesion: 0.14
Nodes (30): assign_log(), clear_next_action(), complete_next_action(), create_log(), _entry(), get_log(), get_person(), _legacy() (+22 more)

### Community 22 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 23 - "services.py"
Cohesion: 0.11
Nodes (23): active_session(), add_evidence_bulk(), attach_posting(), confirm_all_evidence(), ensure_session(), export_all(), extract_evidence(), import_starter() (+15 more)

### Community 24 - "config.py"
Cohesion: 0.24
Nodes (12): argparse, pathlib, Desktop design acceptance: contextual panes, keyboard navigation, themes, and da, Desktop-only guided journey smoke test. Requires Playwright and local Chromium., Desktop design acceptance: contextual panes, keyboard navigation, themes, and da, Desktop design acceptance: contextual panes, keyboard navigation, themes, and da, Temporary browser verification with synthetic, isolated data. No live API calls., Desktop design acceptance: contextual panes, keyboard navigation, themes, and da (+4 more)

### Community 25 - "test_network_imports.py"
Cohesion: 0.24
Nodes (19): connections(), messages(), post(), No external services: networking imports are reviewed local snapshots, not live, test_bad_connections_rejected_without_records(), test_calendar_preview_has_no_attendance_or_external_effects(), test_connection_commit_is_atomic_and_foreign_origin_blocked(), test_connections_preview_does_not_commit_or_keep_emails() (+11 more)

### Community 26 - "Link"
Cohesion: 0.11
Nodes (18): Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Guided desktop connection building, Interface reference, Known limitations, Link (+10 more)

### Community 27 - "test_ai_gateway.py"
Cohesion: 0.23
Nodes (18): build_client(), DraftOut, LiveAI, Return (client, reason). The client is None when AI is off or the live gate fail, fake_api(), gateway(), priced_mock(), test_activity_log_holds_metadata_only() (+10 more)

### Community 28 - "test_people.py"
Cohesion: 0.20
Nodes (14): log(), person(), Connection workflow regressions; synthetic records only., test_chat_switch_does_not_reuse_other_person_history(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_legacy_item_migration_keeps_records(), test_minimal_person_and_unassigned_capture() (+6 more)

### Community 29 - "Career Companion: decision record"
Cohesion: 0.13
Nodes (14): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+6 more)

### Community 30 - "AllowlistTransport"
Cohesion: 0.16
Nodes (11): BaseTransport, AllowlistTransport, NeverSent, Exception, Request, Response, The request provably did not leave this machine, so nothing can have been billed, Outbound allowlist. Anything but HTTPS to the provider's API host is refused. (+3 more)

### Community 31 - "link-guide.js"
Cohesion: 0.30
Nodes (11): create(), advance(), clear(), draw(), finish(), node(), pause(), position() (+3 more)

### Community 32 - "Usage"
Cohesion: 0.19
Nodes (10): dataclasses, math, Any, cost_usd(), estimate_tokens(), _rates(), Spend control (decision D7).  Every AI call reserves its worst-case cost before, Deliberately high estimate (about 2.5 characters per token) so reservations over (+2 more)

### Community 33 - "generate_draft"
Cohesion: 0.23
Nodes (11): _evidence_map(), generate_draft(), _note_draft_saved(), Autosave is allowed to move suggested -> drafted. It never goes further., Atomically retain the old and new text; unchanged autosaves do not create versio, restore_draft(), save_draft(), snapshot_draft() (+3 more)

### Community 34 - "conftest.py"
Cohesion: 0.18
Nodes (10): fastapi_testclient, pytest, anon(), client(), db(), mock_ai(), Shared fixtures. All data here is synthetic; nothing describes a real person., A browser with no session. (+2 more)

### Community 35 - "security.py"
Cohesion: 0.22
Nodes (9): secrets, _deny(), make_guard(), Request, Response, Protection for the local HTTP endpoints (decision D2).  Threats covered: a web p, starlette_requests, starlette_responses (+1 more)

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "Connection Studio design pass"
Cohesion: 0.22
Nodes (8): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, First-click usability correction, Networking sources and imagery, Quality-of-life and motion update, Today / Import differentiation

### Community 38 - "make_action"
Cohesion: 0.29
Nodes (7): make_action(), test_copying_or_saving_a_draft_never_marks_it_sent(), test_data_and_session_progress_survive_restart(), test_invalid_state_jump_is_refused(), test_resume_note_survives_and_is_shown(), test_session_timer_info_and_end(), test_today_opens_on_one_recommendation_with_alternatives()

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
Cohesion: 0.40
Nodes (4): contextlib, os, sqlite3, SQLite storage. One connection, one lock, explicit transactions.

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
- **106 isolated node(s):** `npx`, `career-companion`, `graphify`, `Usage`, `What graphify is for` (+101 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `ai.py`, `Usage`, `create_app`, `store.py`, `BudgetBlocked`, `generate_draft`, `conftest.py`, `test_workflows.py`, `db.py`, `coaching.py`, `people.py`, `services.py`, `test_ai_gateway.py`, `test_people.py`, `AllowlistTransport`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `Budget` connect `Database` to `ai.py`, `Usage`, `create_app`, `store.py`, `BudgetBlocked`, `test_ai_gateway.py`, `AllowlistTransport`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Settings` connect `Database` to `ai.py`, `Usage`, `create_app`, `store.py`, `BudgetBlocked`, `conftest.py`, `test_security.py`, `cli.py`, `services.py`, `config.py`, `test_ai_gateway.py`, `AllowlistTransport`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `Budget` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Budget` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `Settings` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Settings` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `Gateway` (e.g. with `Budget` and `BudgetBlocked`) actually correct?**
  _`Gateway` has 56 INFERRED edges - model-reasoned connections that need verification._