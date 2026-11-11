# Graph Report - career-companion  (2026-11-11)

## Corpus Check
- 31 files · ~30,036 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .woff2 2, .graphify-bak 1, (none) 1)

## Summary
- 564 nodes · 1583 edges · 17 communities (12 shown, 5 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 288 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1aef8376`
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
- validate.py
- Progress
- CLAUDE.md
- .claude/CLAUDE.md
- career-companion

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
- `Done` --references--> `today()`  [INFERRED]
  PROGRESS.md → src/companion/app.py
- `Verified platform facts (official docs, checked 2026-11-10)` --references--> `Usage`  [INFERRED]
  DECISIONS.md → src/companion/budget.py
- `Test results` --references--> `test_failed_call_is_charged_conservatively()`  [INFERRED]
  README.md → tests/test_ai_gateway.py
- `Test results` --references--> `test_egress_refuses_everything_but_the_provider_api()`  [INFERRED]
  README.md → tests/test_ai_gateway.py
- `Test results` --references--> `test_turn_with_pasted_material_cannot_create_proposals()`  [INFERRED]
  README.md → tests/test_privacy_and_injection.py

## Import Cycles
- None detected.

## Communities (17 total, 5 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.05
Nodes (47): AIClient, AIRequest, AIResult, AIUnavailable, AllowlistTransport, Claim, CompanionTurn, CompareOut (+39 more)

### Community 1 - "Database"
Cohesion: 0.08
Nodes (41): Gateway, _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), OutwardContext, planning_context() (+33 more)

### Community 2 - "create_app"
Cohesion: 0.07
Nodes (56): create_app(), action_add(), action_delete(), action_edit(), action_note(), action_state(), actions_list(), bootstrap() (+48 more)

### Community 3 - "app.js"
Cohesion: 0.15
Nodes (57): act(), actionForm(), api(), disc(), dueText(), endSession(), errorView(), fill() (+49 more)

### Community 4 - "Budget"
Cohesion: 0.09
Nodes (24): Career Companion: decision record, Decisions, Implementation plan, Verified platform facts (official docs, checked 2026-11-10), Budget, BudgetBlocked, cost_usd(), estimate_tokens() (+16 more)

### Community 5 - "test_security.py"
Cohesion: 0.05
Nodes (8): default_data_dir(), anon(), app(), client(), mock_ai(), test_dns_rebinding_host_header_is_rejected(), test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "app.py"
Cohesion: 0.07
Nodes (27): ActionIn, ChatIn, CompareIn, DraftGenIn, DraftSaveIn, EvidenceIn, ImportIn, In (+19 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (29): Career Companion, Known limitations, Loading your information in one step, Setup on macOS, Test results, Turning on live AI, What it does, MockAI (+21 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.14
Nodes (28): Option, rank(), _score(), action(), check(), codes(), ev(), ids() (+20 more)

### Community 9 - "Settings"
Cohesion: 0.15
Nodes (14): build_client(), prices_are_fresh(), _delete_key(), main(), _run(), _set_key(), _status(), Settings (+6 more)

### Community 10 - "validate.py"
Cohesion: 0.22
Nodes (10): _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue(), quantities(), _strong_words(), _unit() (+2 more)

### Community 11 - "Progress"
Cohesion: 0.33
Nodes (5): Done, How to resume, Next, in order, Not started, deliberately, Progress

## Knowledge Gaps
- **1 isolated node(s):** `career-companion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 138 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `ai.py`, `Database`, `Budget`, `test_security.py`, `app.py`, `test_workflows.py`, `Settings`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `create_app()` (e.g. with `AIClient` and `AIUnavailable`) actually correct?**
  _`create_app()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ai.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05462962962962963 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `Database` to `ai.py`, `create_app`, `Budget`, `test_security.py`, `app.py`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Database` (e.g. with `Gateway` and `Budget`) actually correct?**
  _`Database` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Should `Database` be split into smaller, more focused modules?**
  _Cohesion score 0.07952815829528158 - nodes in this community are weakly interconnected._