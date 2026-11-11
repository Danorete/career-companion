# Graph Report - career-companion  (2026-11-11)

## Corpus Check
- 33 files · ~30,554 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 2, .woff2 2, .lock 1)

## Summary
- 573 nodes · 1593 edges · 20 communities (14 shown, 6 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 288 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f6c4729e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ai.py
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

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 80 edges
2. `Database` - 53 edges
3. `db()` - 51 edges
4. `h()` - 29 edges
5. `Budget` - 28 edges
6. `render()` - 25 edges
7. `In` - 24 edges
8. `Settings` - 24 edges
9. `api()` - 23 edges
10. `insert()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Verified platform facts (official docs, checked 2026-11-10)` --references--> `Usage`  [INFERRED]
  DECISIONS.md → src/companion/budget.py
- `Test results` --references--> `test_egress_refuses_everything_but_the_provider_api()`  [INFERRED]
  README.md → tests/test_ai_gateway.py
- `Test results` --references--> `test_failed_call_is_charged_conservatively()`  [INFERRED]
  README.md → tests/test_ai_gateway.py
- `Test results` --references--> `test_model_cannot_change_action_state_or_evidence()`  [INFERRED]
  README.md → tests/test_privacy_and_injection.py
- `Test results` --references--> `test_tainted_turn_is_withheld_from_later_context()`  [INFERRED]
  README.md → tests/test_privacy_and_injection.py

## Import Cycles
- None detected.

## Communities (20 total, 6 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.07
Nodes (31): AIClient, AIRequest, AIResult, AIUnavailable, AllowlistTransport, Claim, CompanionTurn, CompareOut (+23 more)

### Community 1 - "Database"
Cohesion: 0.07
Nodes (43): Gateway, idea_decide(), sample(), _clip(), compare_context(), draft_context(), _eligible(), _evidence_block() (+35 more)

### Community 2 - "create_app"
Cohesion: 0.07
Nodes (55): Done, create_app(), action_add(), action_delete(), action_edit(), action_note(), action_state(), actions_list() (+47 more)

### Community 3 - "app.js"
Cohesion: 0.15
Nodes (58): act(), actionForm(), api(), disc(), dueText(), endSession(), errorView(), fill() (+50 more)

### Community 4 - "Budget"
Cohesion: 0.10
Nodes (24): Career Companion: decision record, Decisions, Implementation plan, Verified platform facts (official docs, checked 2026-11-10), Budget, BudgetBlocked, cost_usd(), estimate_tokens() (+16 more)

### Community 5 - "test_security.py"
Cohesion: 0.07
Nodes (7): anon(), app(), client(), mock_ai(), test_dns_rebinding_host_header_is_rejected(), test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "app.py"
Cohesion: 0.07
Nodes (27): ActionIn, ChatIn, CompareIn, DraftGenIn, DraftSaveIn, EvidenceIn, ImportIn, In (+19 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.08
Nodes (28): Career Companion, Known limitations, Loading your information in one step, Setup on macOS, Test results, Turning on live AI, What it does, evidence() (+20 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.14
Nodes (28): Option, rank(), _score(), action(), check(), codes(), ev(), ids() (+20 more)

### Community 9 - "Settings"
Cohesion: 0.09
Nodes (15): build_client(), prices_are_fresh(), _delete_key(), main(), _run(), _set_key(), _status(), default_data_dir() (+7 more)

### Community 10 - "test_privacy_and_injection.py"
Cohesion: 0.20
Nodes (17): seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped(), test_item_context_is_opt_in() (+9 more)

### Community 11 - "validate.py"
Cohesion: 0.22
Nodes (10): _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue(), quantities(), _strong_words(), _unit() (+2 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.40
Nodes (4): How to resume, Next, in order, Not started, deliberately, Progress

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 144 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `ai.py`, `Database`, `Budget`, `test_security.py`, `app.py`, `test_workflows.py`, `Settings`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `create_app()` (e.g. with `AIClient` and `AIUnavailable`) actually correct?**
  _`create_app()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ai.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0679563492063492 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `Database` to `ai.py`, `create_app`, `Budget`, `app.py`, `Settings`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Database` (e.g. with `Gateway` and `Budget`) actually correct?**
  _`Database` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Should `Database` be split into smaller, more focused modules?**
  _Cohesion score 0.07382091592617908 - nodes in this community are weakly interconnected._