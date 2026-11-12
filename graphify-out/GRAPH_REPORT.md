# Graph Report - career-companion  (2026-11-12)

## Corpus Check
- 39 files · ~44,333 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 2, .woff2 2, .lock 1)

## Summary
- 752 nodes · 2169 edges · 30 communities (18 shown, 12 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 393 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6c6cba77`
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
- store.py
- services.py
- test_people.py
- Database

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 112 edges
2. `Database` - 87 edges
3. `db()` - 74 edges
4. `h()` - 40 edges
5. `In` - 37 edges
6. `insert()` - 33 edges
7. `render()` - 29 edges
8. `rows()` - 27 edges
9. `Budget` - 27 edges
10. `Settings` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Done` --references--> `today()`  [INFERRED]
  PROGRESS.md → src/companion/app.py
- `Workflow improvements` --references--> `draft_versions()`  [INFERRED]
  README.md → src/companion/app.py
- `Test results` --references--> `test_preferences_can_be_corrected_in_conversation_and_edited_directly()`  [INFERRED]
  README.md → tests/test_workflows.py
- `Test results` --references--> `test_imported_private_memory_still_stays_out_of_drafting()`  [INFERRED]
  README.md → tests/test_workflows.py
- `Done` --references--> `setup()`  [INFERRED]
  PROGRESS.md → tests/test_workflows.py

## Import Cycles
- None detected.

## Communities (30 total, 12 thin omitted)

### Community 0 - "people.py"
Cohesion: 0.13
Nodes (23): person_next_action_clear(), person_next_action_done(), assign_log(), clear_next_action(), complete_next_action(), create_log(), _entry(), get_log() (+15 more)

### Community 1 - "context.py"
Cohesion: 0.13
Nodes (15): Gateway, _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext (+7 more)

### Community 2 - "create_app"
Cohesion: 0.05
Nodes (74): Workflow improvements, create_app(), action_add(), action_delete(), action_edit(), action_note(), action_state(), actions_list() (+66 more)

### Community 3 - "app.js"
Cohesion: 0.13
Nodes (72): act(), actionForm(), api(), applyTheme(), closeMore(), compareTable(), composeStudio(), disc() (+64 more)

### Community 4 - "Budget"
Cohesion: 0.10
Nodes (24): Career Companion: decision record, Decisions, Implementation plan, Verified platform facts (official docs, checked 2026-11-10), Budget, BudgetBlocked, cost_usd(), estimate_tokens() (+16 more)

### Community 5 - "test_security.py"
Cohesion: 0.07
Nodes (7): anon(), app(), client(), mock_ai(), test_dns_rebinding_host_header_is_rejected(), test_form_posts_are_rejected(), test_refuses_to_bind_anything_but_loopback()

### Community 6 - "app.py"
Cohesion: 0.06
Nodes (42): ActionIn, BulkEntry, ChatIn, CompareIn, ConfirmAllIn, DraftClaimIn, DraftGenIn, DraftSaveIn (+34 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.06
Nodes (40): Interface reference, Known limitations, Link, Loading your information in one step, Setup on macOS, Test results, Turning on live AI, What it does (+32 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.09
Nodes (38): Option, rank(), _score(), _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue() (+30 more)

### Community 9 - "Settings"
Cohesion: 0.10
Nodes (16): build_client(), ai_readiness(), prices_are_fresh(), _delete_key(), main(), _run(), _set_key(), _status() (+8 more)

### Community 10 - "ai.py"
Cohesion: 0.05
Nodes (52): AIClient, AIRequest, AIResult, AIUnavailable, AllowlistTransport, Claim, CompanionTurn, CompareOut (+44 more)

### Community 11 - "insert"
Cohesion: 0.12
Nodes (16): evidence_add(), person_delete(), sample(), starter_import(), delete_person(), load_demo(), log(), person() (+8 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.12
Nodes (14): Connections redesign — started 2026-11-12 (decision D28), Design, Done, How to resume, Increments, Less typing — 2026-11-12 (decision D27), Link workflow upgrade — 2026-11-11, Migration (additive only; no row is rewritten or reinterpreted) (+6 more)

### Community 20 - "store.py"
Cohesion: 0.16
Nodes (13): _evidence_map(), generate_draft(), _note_draft_saved(), restore_draft(), save_draft(), snapshot_draft(), _decode(), due_reminders() (+5 more)

### Community 21 - "services.py"
Cohesion: 0.17
Nodes (13): today(), now(), chat_turn(), end_session(), ensure_session(), export_all(), onboarding_answer(), onboarding_state() (+5 more)

### Community 24 - "test_people.py"
Cohesion: 0.11
Nodes (22): log(), person(), signed_in(), test_a_draft_for_one_person_never_contains_another_persons_context(), test_a_pasted_exchange_is_kept_only_when_the_user_says_so(), test_a_person_can_be_found_and_resumed_after_a_gap(), test_a_rough_log_saves_without_ai_and_without_a_person(), test_a_saved_profile_link_is_text_and_category_is_the_users_choice() (+14 more)

### Community 31 - "Database"
Cohesion: 0.27
Nodes (3): Database, posting_for(), test_versions_survive_reopen_restore_and_deduplicate()

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 181 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Usage` connect `Budget` to `ai.py`, `test_workflows.py`?**
  _High betweenness centrality (0.191) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `create_app()` (e.g. with `AIClient` and `CompanionTurn`) actually correct?**
  _`create_app()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `people.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13446969696969696 - nodes in this community are weakly interconnected._
- **Are the 67 inferred relationships involving `Database` (e.g. with `Gateway` and `Budget`) actually correct?**
  _`Database` has 67 INFERRED edges - model-reasoned connections that need verification._
- **Should `context.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1339031339031339 - nodes in this community are weakly interconnected._
- **Are the 72 inferred relationships involving `db()` (e.g. with `action_add()` and `action_delete()`) actually correct?**
  _`db()` has 72 INFERRED edges - model-reasoned connections that need verification._