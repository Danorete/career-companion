# Graph Report - career-companion  (2026-11-12)

## Corpus Check
- 37 files · ~38,954 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 2, .woff2 2, .lock 1)

## Summary
- 663 nodes · 1856 edges · 32 communities (18 shown, 14 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 325 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f260cea9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_ai_gateway.py
- Database
- create_app
- app.js
- Budget
- test_security.py
- app.py
- test_workflows.py
- test_validate_and_ranking.py
- Settings
- test_privacy_and_injection.py
- validate.py
- CLAUDE.md
- .claude/CLAUDE.md
- career-companion
- Web Interface Guidelines
- chrome-devtools
- Progress
- ai.py
- budget.py
- Settings
- AllowlistTransport
- Link

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 92 edges
2. `Database` - 65 edges
3. `db()` - 58 edges
4. `h()` - 40 edges
5. `In` - 30 edges
6. `render()` - 29 edges
7. `Budget` - 27 edges
8. `api()` - 26 edges
9. `insert()` - 26 edges
10. `need()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Workflow improvements` --references--> `draft_versions()`  [INFERRED]
  README.md → src/companion/app.py
- `Done` --references--> `setup_progress()`  [INFERRED]
  PROGRESS.md → src/companion/services.py
- `Decisions` --references--> `fx()`  [INFERRED]
  DECISIONS.md → src/companion/static/app.js
- `Test results` --references--> `test_preferences_can_be_corrected_in_conversation_and_edited_directly()`  [INFERRED]
  README.md → tests/test_workflows.py
- `Test results` --references--> `test_imported_private_memory_still_stays_out_of_drafting()`  [INFERRED]
  README.md → tests/test_workflows.py

## Import Cycles
- None detected.

## Communities (32 total, 14 thin omitted)

### Community 0 - "test_ai_gateway.py"
Cohesion: 0.26
Nodes (16): AIUnavailable, DraftOut, fake_api(), handler(), gateway(), priced_mock(), test_activity_log_holds_metadata_only(), test_budget_block_never_reaches_the_client() (+8 more)

### Community 1 - "Database"
Cohesion: 0.07
Nodes (43): Gateway, bootstrap(), evidence_confirm_all(), _clip(), compare_context(), draft_context(), _eligible(), _evidence_block() (+35 more)

### Community 2 - "create_app"
Cohesion: 0.06
Nodes (72): Done, create_app(), action_add(), action_delete(), action_edit(), action_note(), action_state(), actions_list() (+64 more)

### Community 3 - "app.js"
Cohesion: 0.13
Nodes (72): act(), actionForm(), api(), applyTheme(), closeMore(), compareTable(), composeStudio(), disc() (+64 more)

### Community 4 - "Budget"
Cohesion: 0.09
Nodes (27): Career Companion: decision record, Decisions, Implementation plan, Verified platform facts (official docs, checked 2026-11-10), Budget, BudgetBlocked, cost_usd(), _rates() (+19 more)

### Community 5 - "test_security.py"
Cohesion: 0.07
Nodes (7): anon(), app(), client(), mock_ai(), test_dns_rebinding_host_header_is_rejected(), test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "app.py"
Cohesion: 0.06
Nodes (35): ActionIn, BulkEntry, ChatIn, CompareIn, ConfirmAllIn, DraftClaimIn, DraftGenIn, DraftSaveIn (+27 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (33): Test results, MockAI, done_ids(), evidence(), make_action(), setup(), signed_in(), test_approved_entries_can_be_added_as_confirmed_in_bulk() (+25 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.14
Nodes (28): Option, rank(), _score(), action(), check(), codes(), ev(), ids() (+20 more)

### Community 9 - "Settings"
Cohesion: 0.17
Nodes (10): ai_readiness(), prices_are_fresh(), _delete_key(), main(), _run(), _set_key(), _status(), delete_api_key() (+2 more)

### Community 10 - "test_privacy_and_injection.py"
Cohesion: 0.19
Nodes (18): CompanionTurn, ProposalOut, seed(), sent(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped() (+10 more)

### Community 11 - "validate.py"
Cohesion: 0.22
Nodes (10): _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue(), quantities(), _strong_words(), _unit() (+2 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.29
Nodes (6): How to resume, Less typing — 2026-11-12 (decision D27), Link workflow upgrade — 2026-11-11, Next, in order, Not started, deliberately, Progress

### Community 20 - "ai.py"
Cohesion: 0.17
Nodes (10): AIRequest, AIResult, Claim, CompareOut, EvidenceCandidate, ExtractOut, MetricOut, Requirement (+2 more)

### Community 22 - "Settings"
Cohesion: 0.15
Nodes (9): AIClient, build_client(), LiveAI, Profile, default_data_dir(), Settings, test_default_mode_is_mock(), test_live_mode_with_stale_prices_stays_off() (+1 more)

### Community 23 - "AllowlistTransport"
Cohesion: 0.16
Nodes (4): AllowlistTransport, NeverSent, test_egress_allows_the_provider_api(), test_egress_refuses_everything_but_the_provider_api()

### Community 25 - "Link"
Cohesion: 0.22
Nodes (8): Interface reference, Known limitations, Link, Loading your information in one step, Setup on macOS, Turning on live AI, What it does, Workflow improvements

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 168 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Usage` connect `Budget` to `test_ai_gateway.py`, `ai.py`, `budget.py`, `test_workflows.py`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `create_app()` (e.g. with `AIClient` and `CompanionTurn`) actually correct?**
  _`create_app()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database` be split into smaller, more focused modules?**
  _Cohesion score 0.06963470319634703 - nodes in this community are weakly interconnected._
- **Are the 46 inferred relationships involving `Database` (e.g. with `Gateway` and `Budget`) actually correct?**
  _`Database` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Should `create_app` be split into smaller, more focused modules?**
  _Cohesion score 0.05515832482124617 - nodes in this community are weakly interconnected._
- **Are the 56 inferred relationships involving `db()` (e.g. with `action_add()` and `action_delete()`) actually correct?**
  _`db()` has 56 INFERRED edges - model-reasoned connections that need verification._