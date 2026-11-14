# Graph Report - career-companion  (2026-11-14)

## Corpus Check
- 68 files · ~76,429 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 901 nodes · 2645 edges · 48 communities (40 shown, 8 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85b7e02c`
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
- `app()` --calls--> `create_app()`  [INFERRED]
  tests/conftest.py → src/companion/app.py
- `test_crash_leftover_reservation_becomes_unknown()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_reconcile_sets_total_to_console_figure()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py
- `test_release_only_frees_never_sent_calls()` --calls--> `Budget`  [INFERRED]
  tests/test_budget.py → src/companion/budget.py

## Import Cycles
- None detected.

## Communities (48 total, 8 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.21
Nodes (14): generate(), Connection coaching: useful before contacts, explicit commitments, private/publi, test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people() (+6 more)

### Community 1 - "store.py"
Cohesion: 0.10
Nodes (25): Align the ledger with the figure the user reads from the provider's Console., now(), Activity log. Callers pass identifiers and counts, never user content., decide_proposal(), export_all(), Only reachable from an authenticated, CSRF-checked user request., check_evidence(), _decode() (+17 more)

### Community 2 - "create_app"
Cohesion: 0.24
Nodes (19): connections(), messages(), post(), No external services: networking imports are reviewed local snapshots, not live, test_bad_connections_rejected_without_records(), test_calendar_preview_has_no_attendance_or_external_effects(), test_connection_commit_is_atomic_and_foreign_origin_blocked(), test_connections_preview_does_not_commit_or_keep_emails() (+11 more)

### Community 3 - "app.js"
Cohesion: 0.10
Nodes (97): act(), actionForm(), api(), applyMotion(), applyTheme(), arrive(), closeMore(), compareTable() (+89 more)

### Community 4 - "BudgetBlocked"
Cohesion: 0.42
Nodes (13): Claim, CompareOut, EvidenceCandidate, ExtractOut, MetricOut, ProposalOut, BaseModel, QuickLogOut (+5 more)

### Community 5 - "test_security.py"
Cohesion: 0.09
Nodes (4): Local endpoint protection (decision D2)., A cross-site HTML form can only send form encodings, never JSON., test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "Database"
Cohesion: 0.10
Nodes (87): fastapi_responses, fastapi_staticfiles, Protocol, pydantic, AIClient, AIUnavailable, CompanionTurn, Gateway (+79 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (32): FastAPI, create_app(), done_ids(), evidence(), make_action(), End-to-end behaviour through the HTTP API, with the mock AI. Synthetic data only, setup(), signed_in() (+24 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.14
Nodes (34): dataclasses, datetime, Option, date, rank(), Deterministic recommendation (decision D10). The model never ranks.  Order of co, Return at most `limit` options, best first., _score() (+26 more)

### Community 9 - "cli.py"
Cohesion: 0.08
Nodes (37): argparse, contextlib, getpass, logging, Namespace, os, pathlib, Desktop design acceptance: contextual panes, keyboard navigation, themes, and da (+29 more)

### Community 10 - "network_imports.py"
Cohesion: 0.20
Nodes (19): Planning/drafting separation (D5) and untrusted material (D3, D4). Synthetic dat, There is no proposal kind, and no code path, from model output to these records., seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary() (+11 more)

### Community 11 - "AllowlistTransport"
Cohesion: 0.18
Nodes (10): BaseTransport, AllowlistTransport, NeverSent, Exception, Request, Response, The request provably did not leave this machine, so nothing can have been billed, Outbound allowlist. Anything but HTTPS to the provider's API host is refused. (+2 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.10
Nodes (19): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Done (+11 more)

### Community 20 - "coaching.py"
Cohesion: 0.14
Nodes (9): AIRequest, AIResult, MockAI, Any, Deterministic stand-in. Every visible reply is labelled as mock output., estimate_tokens(), Deliberately high estimate (about 2.5 characters per token) so reservations over, manual_plan() (+1 more)

### Community 21 - "people.py"
Cohesion: 0.06
Nodes (61): json, re, _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context() (+53 more)

### Community 22 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 23 - "services.py"
Cohesion: 0.07
Nodes (48): active_session(), add_evidence_bulk(), attach_posting(), confirm_all_evidence(), ensure_session(), _evidence_map(), extract_evidence(), generate_draft() (+40 more)

### Community 24 - "conftest.py"
Cohesion: 0.17
Nodes (11): fastapi_testclient, pytest, anon(), app(), client(), db(), mock_ai(), Shared fixtures. All data here is synthetic; nothing describes a real person. (+3 more)

### Community 25 - "test_network_imports.py"
Cohesion: 0.10
Nodes (24): math, BudgetBlocked, cost_usd(), Exception, _rates(), Spend control (decision D7).  Every AI call reserves its worst-case cost before, A new AI call was refused by a spending rule. `reason` is safe to show the user., Upper bound: all input billed as a cache write (the dearest input rate), full ou (+16 more)

### Community 26 - "Link"
Cohesion: 0.10
Nodes (19): Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Field notebook design (2026-11-13), Guided desktop connection building, Interface reference, Known limitations (+11 more)

### Community 27 - "test_ai_gateway.py"
Cohesion: 0.32
Nodes (15): httpx2, DraftOut, fake_api(), gateway(), priced_mock(), test_activity_log_holds_metadata_only(), test_budget_block_never_reaches_the_client(), test_failed_call_is_charged_conservatively() (+7 more)

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

### Community 32 - "build_client"
Cohesion: 0.20
Nodes (7): build_client(), LiveAI, Profile, Return (client, reason). The client is None when AI is off or the live gate fail, test_default_mode_is_mock(), test_live_mode_with_stale_prices_stays_off(), test_live_mode_without_key_stays_off()

### Community 36 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 37 - "Connection Studio design pass"
Cohesion: 0.18
Nodes (10): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, Field notebook redesign (2026-11-13), First-click usability correction, Motion and usability follow-up (2026-11-14), Networking sources and imagery (+2 more)

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
- **112 isolated node(s):** `npx`, `career-companion`, `graphify`, `Usage`, `What graphify is for` (+107 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `build_client`, `store.py`, `BudgetBlocked`, `test_workflows.py`, `cli.py`, `AllowlistTransport`, `coaching.py`, `people.py`, `services.py`, `conftest.py`, `test_network_imports.py`, `test_ai_gateway.py`, `test_people.py`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `Budget` connect `Database` to `build_client`, `store.py`, `BudgetBlocked`, `test_workflows.py`, `AllowlistTransport`, `coaching.py`, `test_network_imports.py`, `test_ai_gateway.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `Settings` connect `Database` to `build_client`, `store.py`, `BudgetBlocked`, `test_security.py`, `test_workflows.py`, `cli.py`, `AllowlistTransport`, `coaching.py`, `services.py`, `conftest.py`, `test_network_imports.py`, `test_ai_gateway.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 81 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 81 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `Budget` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Budget` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 72 inferred relationships involving `Settings` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Settings` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `Gateway` (e.g. with `Budget` and `BudgetBlocked`) actually correct?**
  _`Gateway` has 56 INFERRED edges - model-reasoned connections that need verification._