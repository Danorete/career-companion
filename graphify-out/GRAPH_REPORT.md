# Graph Report - career-companion  (2026-11-11)

## Corpus Check
- 33 files · ~31,675 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 2, .woff2 2, .lock 1)

## Summary
- 590 nodes · 1635 edges · 22 communities (14 shown, 8 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 257 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c43b69db`
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
1. `create_app()` - 79 edges
2. `Database` - 54 edges
3. `db()` - 51 edges
4. `h()` - 33 edges
5. `Budget` - 28 edges
6. `render()` - 26 edges
7. `In` - 24 edges
8. `Settings` - 24 edges
9. `api()` - 23 edges
10. `insert()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Decisions` --references--> `fx()`  [INFERRED]
  DECISIONS.md → src/companion/static/app.js
- `Test results` --references--> `test_preferences_can_be_corrected_in_conversation_and_edited_directly()`  [INFERRED]
  README.md → tests/test_workflows.py
- `Test results` --references--> `test_imported_private_memory_still_stays_out_of_drafting()`  [INFERRED]
  README.md → tests/test_workflows.py
- `Done` --references--> `setup()`  [INFERRED]
  PROGRESS.md → tests/test_workflows.py
- `Verified platform facts (official docs, checked 2026-11-10)` --references--> `Usage`  [INFERRED]
  DECISIONS.md → src/companion/budget.py

## Import Cycles
- None detected.

## Communities (22 total, 8 thin omitted)

### Community 0 - "ai.py"
Cohesion: 0.06
Nodes (36): Career Companion: decision record, Decisions, Implementation plan, Verified platform facts (official docs, checked 2026-11-10), AIClient, AIRequest, AIResult, AIUnavailable (+28 more)

### Community 1 - "Database"
Cohesion: 0.07
Nodes (42): Gateway, action_state(), sample(), session_end(), wipe(), _clip(), compare_context(), draft_context() (+34 more)

### Community 2 - "create_app"
Cohesion: 0.07
Nodes (57): Done, create_app(), action_add(), action_delete(), action_edit(), action_note(), actions_list(), bootstrap() (+49 more)

### Community 3 - "app.js"
Cohesion: 0.14
Nodes (63): act(), actionForm(), api(), disc(), dueText(), endSession(), errorView(), fill() (+55 more)

### Community 4 - "Budget"
Cohesion: 0.10
Nodes (20): Budget, BudgetBlocked, cost_usd(), estimate_tokens(), prices_are_fresh(), _rates(), worst_case_usd(), test_cost_matches_published_prices() (+12 more)

### Community 5 - "test_security.py"
Cohesion: 0.07
Nodes (7): anon(), app(), client(), mock_ai(), test_dns_rebinding_host_header_is_rejected(), test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "app.py"
Cohesion: 0.06
Nodes (27): ActionIn, ChatIn, CompareIn, DraftGenIn, DraftSaveIn, EvidenceIn, ImportIn, In (+19 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (34): Career Companion, Known limitations, Loading your information in one step, Setup on macOS, Test results, Turning on live AI, What it does, done_ids() (+26 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.14
Nodes (28): Option, rank(), _score(), action(), check(), codes(), ev(), ids() (+20 more)

### Community 9 - "Settings"
Cohesion: 0.11
Nodes (14): build_client(), _delete_key(), main(), _run(), _set_key(), _status(), default_data_dir(), Settings (+6 more)

### Community 10 - "test_privacy_and_injection.py"
Cohesion: 0.18
Nodes (18): _decode(), seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped() (+10 more)

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
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 147 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Usage` connect `ai.py` to `Budget`?**
  _High betweenness centrality (0.215) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `create_app()` (e.g. with `.db_path()` and `app()`) actually correct?**
  _`create_app()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ai.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06453028972783142 - nodes in this community are weakly interconnected._
- **Are the 16 inferred relationships involving `Database` (e.g. with `Gateway` and `Budget`) actually correct?**
  _`Database` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Database` be split into smaller, more focused modules?**
  _Cohesion score 0.07433489827856025 - nodes in this community are weakly interconnected._
- **Are the 49 inferred relationships involving `db()` (e.g. with `action_add()` and `action_delete()`) actually correct?**
  _`db()` has 49 INFERRED edges - model-reasoned connections that need verification._