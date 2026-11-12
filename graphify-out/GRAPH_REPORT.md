# Graph Report - career-companion  (2026-11-12)

## Corpus Check
- 39 files · ~52,075 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 2, .woff2 2, .lock 1)

## Summary
- 783 nodes · 2322 edges · 38 communities (24 shown, 14 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 390 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `116614d8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- people.py
- context.py
- create_app
- app.js
- Budget
- test_security.py
- app.py
- test_workflows.py
- test_validate_and_ranking.py
- Settings
- ai.py
- insert
- CLAUDE.md
- .claude/CLAUDE.md
- career-companion
- Web Interface Guidelines
- chrome-devtools
- Progress
- save_draft
- services.py
- need
- store.py
- local_today
- conftest.py
- .one
- Link
- delete
- check_evidence

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 111 edges
2. `Database` - 88 edges
3. `db()` - 74 edges
4. `h()` - 56 edges
5. `In` - 37 edges
6. `api()` - 36 edges
7. `render()` - 36 edges
8. `insert()` - 33 edges
9. `act()` - 30 edges
10. `Test results` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Workflow improvements` --references--> `draft_versions()`  [INFERRED]
  README.md → src/companion/app.py
- `Done` --references--> `today()`  [INFERRED]
  PROGRESS.md → src/companion/app.py
- `Decisions` --references--> `fx()`  [INFERRED]
  DECISIONS.md → src/companion/static/app.js
- `Test results` --references--> `test_resolve_when_never_gives_an_approximate_entry_a_date()`  [INFERRED]
  README.md → tests/test_people.py
- `Verified platform facts (official docs, checked 2026-11-10)` --references--> `Usage`  [INFERRED]
  DECISIONS.md → src/companion/budget.py

## Import Cycles
- None detected.

## Communities (38 total, 14 thin omitted)

### Community 0 - "people.py"
Cohesion: 0.18
Nodes (22): Database, assign_log(), clear_next_action(), complete_next_action(), create_log(), delete_person(), _entry(), get_log() (+14 more)

### Community 1 - "context.py"
Cohesion: 0.22
Nodes (9): _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext, planning_context() (+1 more)

### Community 2 - "create_app"
Cohesion: 0.08
Nodes (35): create_app(), actions_list(), bootstrap(), compare(), drafts_list(), evidence_bulk(), evidence_confirm_all(), evidence_extract() (+27 more)

### Community 3 - "app.js"
Cohesion: 0.10
Nodes (96): act(), actionForm(), api(), applyRoute(), applyTheme(), closeMore(), compareTable(), composeStudio() (+88 more)

### Community 4 - "Budget"
Cohesion: 0.10
Nodes (24): Career Companion: decision record, Decisions, Implementation plan, Verified platform facts (official docs, checked 2026-11-10), Budget, BudgetBlocked, cost_usd(), estimate_tokens() (+16 more)

### Community 5 - "test_security.py"
Cohesion: 0.09
Nodes (3): test_dns_rebinding_host_header_is_rejected(), test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "app.py"
Cohesion: 0.06
Nodes (42): ActionIn, BulkEntry, ChatIn, CompareIn, ConfirmAllIn, DraftClaimIn, DraftGenIn, DraftSaveIn (+34 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.05
Nodes (58): Checks (2026-11-12), Test results, MockAI, log(), person(), signed_in(), test_a_draft_for_one_person_never_contains_another_persons_context(), test_a_pasted_exchange_is_kept_only_when_the_user_says_so() (+50 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.09
Nodes (38): Option, rank(), _score(), _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue() (+30 more)

### Community 9 - "Settings"
Cohesion: 0.10
Nodes (16): build_client(), ai_readiness(), prices_are_fresh(), _delete_key(), main(), _run(), _set_key(), _status() (+8 more)

### Community 10 - "ai.py"
Cohesion: 0.05
Nodes (53): AIClient, AIRequest, AIResult, AIUnavailable, AllowlistTransport, Claim, CompanionTurn, CompareOut (+45 more)

### Community 11 - "insert"
Cohesion: 0.12
Nodes (18): now(), load_demo(), log(), person(), set_next_action(), add_evidence_bulk(), attach_posting(), confirm_all_evidence() (+10 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.12
Nodes (14): Connections redesign — started 2026-11-12 (decision D28), Design, Done, How to resume, Increments, Less typing — 2026-11-12 (decision D27), Limitations and what is left, Link workflow upgrade — 2026-11-11 (+6 more)

### Community 20 - "save_draft"
Cohesion: 0.32
Nodes (6): _evidence_map(), restore_draft(), save_draft(), snapshot_draft(), test_restore_revalidates_against_current_evidence_and_rejects_other_draft(), test_schema_one_draft_survives_upgrade_and_first_edit()

### Community 21 - "services.py"
Cohesion: 0.17
Nodes (17): Gateway, notes_for_draft(), suggest_log(), active_session(), chat_turn(), _draft_scope(), ensure_session(), extract_evidence() (+9 more)

### Community 23 - "need"
Cohesion: 0.12
Nodes (17): action_add(), action_edit(), action_note(), draft_copied(), draft_generate(), draft_restore(), draft_save(), draft_suggest() (+9 more)

### Community 25 - "store.py"
Cohesion: 0.21
Nodes (5): _decode(), due_reminders(), load_sample(), purge_old_messages(), rows()

### Community 26 - "local_today"
Cohesion: 0.19
Nodes (12): action_state(), chat(), log_add(), log_edit(), outcome_add(), person_next_action_done(), reminder_snooze(), sample() (+4 more)

### Community 27 - "conftest.py"
Cohesion: 0.27
Nodes (4): anon(), app(), client(), mock_ai()

### Community 31 - ".one"
Cohesion: 0.33
Nodes (3): onboarding_state(), posting_for(), test_versions_survive_reopen_restore_and_deduplicate()

### Community 32 - "Link"
Cohesion: 0.22
Nodes (8): Interface reference, Known limitations, Link, Loading your information in one step, Setup on macOS, Turning on live AI, What it does, Workflow improvements

### Community 33 - "delete"
Cohesion: 0.22
Nodes (9): action_delete(), draft_delete(), evidence_delete(), import_delete(), item_delete(), log_delete(), memory_delete(), outcome_delete() (+1 more)

### Community 35 - "check_evidence"
Cohesion: 0.50
Nodes (4): evidence_add(), evidence_edit(), starter_import(), check_evidence()

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 184 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Usage` connect `Budget` to `ai.py`?**
  _High betweenness centrality (0.232) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `create_app()` (e.g. with `.db_path()` and `app()`) actually correct?**
  _`create_app()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `create_app` be split into smaller, more focused modules?**
  _Cohesion score 0.08362369337979095 - nodes in this community are weakly interconnected._
- **Are the 48 inferred relationships involving `Database` (e.g. with `Gateway` and `Budget`) actually correct?**
  _`Database` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09595959595959595 - nodes in this community are weakly interconnected._
- **Are the 72 inferred relationships involving `db()` (e.g. with `action_add()` and `action_delete()`) actually correct?**
  _`db()` has 72 INFERRED edges - model-reasoned connections that need verification._