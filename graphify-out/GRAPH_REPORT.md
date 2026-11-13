# Graph Report - career-companion  (2026-11-13)

## Corpus Check
- 68 files · ~75,907 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 898 nodes · 2637 edges · 44 communities (34 shown, 10 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eb4629de`
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
- test_network_imports.py
- Link
- test_ai_gateway.py
- test_people.py
- Career Companion: decision record
- link-guide.js
- graphify reference: extra exports and benchmark
- Connection Studio design pass
- graphify reference: query, path, explain
- Link — handoff
- graphify reference: commit hook and native CLAUDE.md integration
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
8. `h()` - 53 edges
9. `Security` - 52 edges
10. `In` - 47 edges

## Surprising Connections (you probably didn't know these)
- `mock_ai()` --calls--> `MockAI`  [INFERRED]
  tests/conftest.py → src/companion/ai.py
- `test_egress_allows_the_provider_api()` --calls--> `AllowlistTransport`  [INFERRED]
  tests/test_ai_gateway.py → src/companion/ai.py
- `app()` --calls--> `create_app()`  [INFERRED]
  tests/conftest.py → src/companion/app.py
- `test_crash_leftover_reservation_becomes_unknown()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_reconcile_sets_total_to_console_figure()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py

## Import Cycles
- None detected.

## Communities (44 total, 10 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.21
Nodes (14): generate(), Connection coaching: useful before contacts, explicit commitments, private/publi, test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people() (+6 more)

### Community 1 - "store.py"
Cohesion: 0.11
Nodes (27): secrets, _deny(), make_guard(), Request, Response, Protection for the local HTTP endpoints (decision D2).  Threats covered: a web p, check_evidence(), _decode() (+19 more)

### Community 3 - "app.js"
Cohesion: 0.10
Nodes (95): act(), actionForm(), api(), applyMotion(), applyTheme(), closeMore(), compareTable(), composeStudio() (+87 more)

### Community 5 - "test_security.py"
Cohesion: 0.06
Nodes (14): fastapi_testclient, anon(), app(), client(), db(), mock_ai(), Shared fixtures. All data here is synthetic; nothing describes a real person., A browser with no session. (+6 more)

### Community 6 - "Database"
Cohesion: 0.08
Nodes (101): BaseTransport, fastapi_responses, fastapi_staticfiles, logging, Protocol, pydantic, AIClient, AIRequest (+93 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (32): FastAPI, create_app(), done_ids(), evidence(), make_action(), End-to-end behaviour through the HTTP API, with the mock AI. Synthetic data only, setup(), signed_in() (+24 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.14
Nodes (34): dataclasses, datetime, Option, date, rank(), Deterministic recommendation (decision D10). The model never ranks.  Order of co, Return at most `limit` options, best first., _score() (+26 more)

### Community 9 - "cli.py"
Cohesion: 0.11
Nodes (19): getpass, Namespace, prices_are_fresh(), date, Align the ledger with the figure the user reads from the provider's Console., _delete_key(), main(), Command line entry point: `companion run`, `companion set-key`, `companion delet (+11 more)

### Community 10 - "network_imports.py"
Cohesion: 0.10
Nodes (35): json, re, calendar_preview(), confirm_connections(), confirm_messages(), connections_preview(), _csv(), fingerprint() (+27 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.10
Nodes (19): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Done (+11 more)

### Community 20 - "coaching.py"
Cohesion: 0.09
Nodes (33): confirm(), ConfirmInput, ConnectionPlan, _decode(), follow_up_candidates(), generate(), get_plan(), Input (+25 more)

### Community 21 - "people.py"
Cohesion: 0.08
Nodes (48): argparse, contextlib, os, pathlib, Desktop design acceptance: contextual panes, keyboard navigation, themes, and da, Desktop-only guided journey smoke test. Requires Playwright and local Chromium., Desktop design acceptance: contextual panes, keyboard navigation, themes, and da, Desktop design acceptance: contextual panes, keyboard navigation, themes, and da (+40 more)

### Community 22 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 23 - "services.py"
Cohesion: 0.06
Nodes (57): now(), active_session(), add_evidence_bulk(), attach_posting(), chat_turn(), confirm_all_evidence(), decide_proposal(), end_session() (+49 more)

### Community 25 - "test_network_imports.py"
Cohesion: 0.08
Nodes (40): math, pytest, cost_usd(), estimate_tokens(), _rates(), Spend control (decision D7).  Every AI call reserves its worst-case cost before, Deliberately high estimate (about 2.5 characters per token) so reservations over, Upper bound: all input billed as a cache write (the dearest input rate), full ou (+32 more)

### Community 26 - "Link"
Cohesion: 0.10
Nodes (19): Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Field notebook design (2026-11-13), Guided desktop connection building, Interface reference, Known limitations (+11 more)

### Community 27 - "test_ai_gateway.py"
Cohesion: 0.20
Nodes (21): httpx2, build_client(), DraftOut, Return (client, reason). The client is None when AI is off or the live gate fail, fake_api(), gateway(), priced_mock(), test_activity_log_holds_metadata_only() (+13 more)

### Community 28 - "test_people.py"
Cohesion: 0.20
Nodes (14): log(), person(), Connection workflow regressions; synthetic records only., test_chat_switch_does_not_reuse_other_person_history(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_legacy_item_migration_keeps_records(), test_minimal_person_and_unassigned_capture() (+6 more)

### Community 29 - "Career Companion: decision record"
Cohesion: 0.12
Nodes (15): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+7 more)

### Community 31 - "link-guide.js"
Cohesion: 0.30
Nodes (11): create(), advance(), clear(), draw(), finish(), node(), pause(), position() (+3 more)

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "Connection Studio design pass"
Cohesion: 0.20
Nodes (9): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, Field notebook redesign (2026-11-13), First-click usability correction, Networking sources and imagery, Quality-of-life and motion update (+1 more)

### Community 39 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 40 - "Link — handoff"
Cohesion: 0.33
Nodes (5): Checks and what is still unverified, Link — handoff, Open threads, Run it on your Mac, What the current build contains

### Community 41 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.40
Nodes (4): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration, Source-read freshness

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
- **111 isolated node(s):** `npx`, `career-companion`, `graphify`, `Usage`, `What graphify is for` (+106 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `store.py`, `create_app`, `BudgetBlocked`, `test_security.py`, `test_workflows.py`, `coaching.py`, `people.py`, `services.py`, `test_network_imports.py`, `test_ai_gateway.py`, `test_people.py`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `Budget` connect `Database` to `test_network_imports.py`, `test_ai_gateway.py`, `cli.py`, `test_workflows.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `Settings` connect `Database` to `test_security.py`, `test_workflows.py`, `cli.py`, `people.py`, `services.py`, `test_network_imports.py`, `test_ai_gateway.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `Budget` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Budget` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `Settings` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Settings` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `Gateway` (e.g. with `Budget` and `BudgetBlocked`) actually correct?**
  _`Gateway` has 56 INFERRED edges - model-reasoned connections that need verification._