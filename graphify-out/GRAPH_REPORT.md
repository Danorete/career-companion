# Graph Report - career-companion  (2026-11-19)

## Corpus Check
- 97 files · ~123,735 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 2, .woff2 2, .css 2)

## Summary
- 1835 nodes · 4864 edges · 100 communities (69 shown, 31 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 633 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c5d3e2fe`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Budget
- test_web.py
- create_app
- app.js
- network_imports.py
- test_security.py
- Database
- test_workflows.py
- test_validate_and_ranking.py
- test_launcher.py
- network_imports.py
- store.py
- CLAUDE.md
- CLAUDE.md
- career-companion
- Web Interface Guidelines
- chrome-devtools
- Progress
- coaching.py
- config.py
- test_connection_coaching.py
- services.py
- create
- test_network_imports.py
- Link
- Setting up the Link coach in Gemini
- test_people.py
- cli.py
- test_checkins.py
- link-guide.js
- test_nudges.py
- create
- Message patterns
- Secrets
- Security
- Connection Studio design pass
- encounters.py
- Coaching playbook
- Link — handoff
- Link Coach
- connectors.py
- Guidance
- Plain language
- test_mail.py
- Examples
- Link Coach: paste-ready Gem
- Settings
- test_calendar_connect.py
- web.py
- create_web_app
- test_ai_gateway.py
- create
- nudges.py
- cli.py
- _nudge
- AllowlistTransport
- security.py
- Database
- config.py
- .q
- Accounts
- test_calendar_connect.py
- create
- test_journey.py
- launcher.py
- ConnectorError
- check_guide_browser.py
- check_walkthrough_browser.py
- GoogleMail
- GoogleLogin
- ConnectorTransport
- check_web_browser.py
- WebConfig
- SampleCalendar
- SampleMail
- check_companion_browser.py
- Pool
- OAuthFlows
- journey
- test_a_refused_all_folders_list_falls_back_to_the_inbox_and_a_403_says_why
- Plain-language backlog (from the D53 audit, 2026-11-19)
- Limiter
- Notifier
- follow_up_candidates

## God Nodes (most connected - your core abstractions)
1. `create_app()` - 182 edges
2. `Database` - 174 edges
3. `Settings` - 77 edges
4. `h()` - 58 edges
5. `In` - 47 edges
6. `Budget` - 47 edges
7. `api()` - 40 edges
8. `MockAI` - 40 edges
9. `render()` - 38 edges
10. `now()` - 34 edges

## Surprising Connections (you probably didn't know these)
- `D43 — Calendar connect, first slice (2026-11-17)` --references--> `KeyringSecrets`  [INFERRED]
  DECISIONS.md → src/companion/keys.py
- `Done` --references--> `setup_progress()`  [INFERRED]
  PROGRESS.md → src/companion/services.py
- `Decisions` --references--> `fx()`  [INFERRED]
  DECISIONS.md → src/companion/static/app.js
- `app()` --calls--> `create_app()`  [INFERRED]
  tests/conftest.py → src/companion/app.py
- `test_old_transcripts_are_purged_on_start()` --calls--> `create_app()`  [INFERRED]
  tests/test_workflows.py → src/companion/app.py

## Import Cycles
- None detected.

## Communities (100 total, 31 thin omitted)

### Community 0 - "Budget"
Cohesion: 0.09
Nodes (18): Budget, BudgetBlocked, cost_usd(), _rates(), worst_case_usd(), test_cost_matches_published_prices(), test_crash_leftover_reservation_becomes_unknown(), test_day_and_session_caps() (+10 more)

### Community 1 - "test_web.py"
Cohesion: 0.08
Nodes (35): EncryptedFileSecrets, b64(), browser(), config(), csrf(), FakeGoogle, folders(), sign_in() (+27 more)

### Community 2 - "create_app"
Cohesion: 0.03
Nodes (78): Workflow improvements, create_app(), action_delete(), action_state(), actions_list(), ai_readiness(), ai_smoke(), bootstrap() (+70 more)

### Community 3 - "app.js"
Cohesion: 0.08
Nodes (112): act(), actionForm(), api(), applyMode(), applyTheme(), checkinCard(), closeMenus(), closeMore() (+104 more)

### Community 4 - "network_imports.py"
Cohesion: 0.17
Nodes (18): import_connections(), imported_person_source(), preview_calendar(), preview_connections(), preview_messages(), calendar_preview(), confirm_connections(), confirm_messages() (+10 more)

### Community 5 - "test_security.py"
Cohesion: 0.09
Nodes (3): test_dns_rebinding_host_header_is_rejected(), test_form_posts_are_rejected(), test_the_database_layer_refuses_unknown_tables_and_odd_column_names()

### Community 6 - "Database"
Cohesion: 0.05
Nodes (55): D43 — Calendar connect, first slice (2026-11-17), ActionIn, AssignIn, BulkEntry, ChatIn, CheckinIn, CompareIn, ConfirmAllIn (+47 more)

### Community 7 - "test_workflows.py"
Cohesion: 0.07
Nodes (29): done_ids(), evidence(), make_action(), setup(), signed_in(), test_approved_entries_can_be_added_as_confirmed_in_bulk(), test_copying_or_saving_a_draft_never_marks_it_sent(), test_data_and_session_progress_survive_restart() (+21 more)

### Community 8 - "test_validate_and_ranking.py"
Cohesion: 0.09
Nodes (38): Option, rank(), _score(), _banned(), _check_number(), _evidence_quantities(), _has_phrase(), _issue() (+30 more)

### Community 9 - "test_launcher.py"
Cohesion: 0.13
Nodes (14): make(), settings_in(), test_a_background_start_prints_no_link_and_closes_the_first_one(), test_a_link_that_is_not_running_is_started_then_opened(), test_a_running_link_is_asked_for_a_fresh_link_and_the_browser_opens_it(), test_a_web_page_cannot_use_the_launcher_even_with_the_key(), test_another_program_on_the_port_is_never_started_over_or_opened(), test_background_start_is_detached_and_writes_to_a_log_not_the_screen() (+6 more)

### Community 10 - "network_imports.py"
Cohesion: 0.20
Nodes (17): seed(), sent(), test_compare_drops_evidence_ids_the_model_invented(), test_compare_request_contains_no_private_canary(), test_draft_citing_withheld_evidence_is_blocked(), test_draft_request_contains_no_private_canary(), test_invalid_and_excess_proposals_are_dropped(), test_item_context_is_opt_in() (+9 more)

### Community 11 - "store.py"
Cohesion: 0.10
Nodes (17): sample(), _clip(), compare_context(), draft_context(), _eligible(), _evidence_block(), extract_context(), OutwardContext (+9 more)

### Community 17 - "Web Interface Guidelines"
Cohesion: 0.40
Nodes (4): Guidelines Source, How It Works, Usage, Web Interface Guidelines

### Community 19 - "Progress"
Cohesion: 0.09
Nodes (19): Avatar + walkthrough, Clear first clicks, Connection-first continuation — 2026-11-12 (Codex), Connection Studio design implementation — 2026-11-12, Conversation scope fix, Current state (2026-11-13), Daily home / Import separation, Done (+11 more)

### Community 20 - "coaching.py"
Cohesion: 0.17
Nodes (15): Gateway, connection_plan(), connection_practice(), confirm(), ConfirmInput, ConnectionPlan, _decode(), generate() (+7 more)

### Community 22 - "test_connection_coaching.py"
Cohesion: 0.21
Nodes (13): generate(), test_confirm_does_not_overwrite_existing_commitment(), test_confirm_is_explicit_and_idempotent(), test_every_opportunity_request_type_uses_pending_plan(), test_existing_person_association_avoids_duplicate(), test_model_cannot_invent_name_or_write_records(), test_new_user_can_get_value_before_adding_people(), test_plan_persistence_export_delete_and_invalid_input() (+5 more)

### Community 23 - "services.py"
Cohesion: 0.06
Nodes (56): action_add(), action_edit(), action_note(), chat(), draft_copied(), draft_generate(), draft_restore(), draft_save() (+48 more)

### Community 24 - "create"
Cohesion: 0.24
Nodes (10): create(), choose(), history(), messageTools(), practiceTools(), review(), simpleSave(), skip() (+2 more)

### Community 25 - "test_network_imports.py"
Cohesion: 0.24
Nodes (18): connections(), messages(), post(), test_bad_connections_rejected_without_records(), test_calendar_preview_has_no_attendance_or_external_effects(), test_connection_commit_is_atomic_and_foreign_origin_blocked(), test_connections_preview_does_not_commit_or_keep_emails(), test_import_metadata_exported_and_wiped() (+10 more)

### Community 26 - "Link"
Cohesion: 0.08
Nodes (25): Adding a person, step by step, Connect Google Calendar (optional), Connection-first workflow (2026-11-12), Connection Studio design, Conversation context, Everyday connection workflow, Guided desktop connection building, How Link works, your progress, and the walkthrough (+17 more)

### Community 27 - "Setting up the Link coach in Gemini"
Cohesion: 0.17
Nodes (11): Important: build a skill, not a Gem, Links to recheck, Setting up the Link coach in Gemini, Sharing with testers, Steps, Test it before sharing (10 minutes), What this prototype can and can't test, What to measure with testers (+3 more)

### Community 28 - "test_people.py"
Cohesion: 0.21
Nodes (12): log(), person(), test_chat_switch_does_not_reuse_other_person_history(), test_demo_never_opens_personal_database(), test_export_and_delete(), test_imported_log_cannot_create_memory(), test_minimal_person_and_unassigned_capture(), test_retention_is_explicit() (+4 more)

### Community 29 - "cli.py"
Cohesion: 0.06
Nodes (31): Career Companion: decision record, D28 — Connection-first workflow (2026-11-12), D29 — Guided desktop connection building (2026-11-12), D30 — Connection Studio desktop design (2026-11-12), D31 — Link avatar and optional interactive guide, D32 — Everyday usability and motion, D33 — Advice is not an evidence audit, D34 — Reviewable networking snapshots (+23 more)

### Community 30 - "test_checkins.py"
Cohesion: 0.34
Nodes (11): due(), kept(), logs(), test_a_promise_becomes_the_next_step_with_a_reminder(), test_a_promise_never_replaces_a_next_step_you_already_have(), test_asked_an_hour_after_the_meeting_and_expired_after_a_week(), test_disconnecting_and_removing_calendar_data_keeps_the_notes_you_saved(), test_each_check_in_is_answered_once_and_bad_input_is_refused() (+3 more)

### Community 31 - "link-guide.js"
Cohesion: 0.38
Nodes (9): advance(), clear(), draw(), finish(), node(), pause(), position(), save() (+1 more)

### Community 32 - "test_nudges.py"
Cohesion: 0.13
Nodes (26): test_detection_rules(), at(), db(), Notifier, reminder_for(), signed_in(), test_a_check_in_that_is_due_counts_as_a_follow_up(), test_a_computer_that_was_asleep_still_sends_later_the_same_day() (+18 more)

### Community 33 - "create"
Cohesion: 0.15
Nodes (24): Cancel, create(), blockPage(), build(), context(), finishTyping(), goTo(), keepUp() (+16 more)

### Community 34 - "Message patterns"
Cohesion: 0.20
Nodes (9): 1. Follow-up after a conversation (four parts), 2. First message to someone you have not met, 3. Thank-you after help or an introduction, 4. Asking for help (advice, review, or an introduction), 5. Reconnecting after silence, Avoid, Keeping a promise ("I'll send you the article"), Message patterns (+1 more)

### Community 35 - "Secrets"
Cohesion: 0.18
Nodes (9): FolderSecrets, Secrets, test_a_refused_refresh_removes_the_saved_sign_in_and_shows_a_safe_message(), test_export_includes_candidates_but_never_a_token(), test_a_tester_disconnecting_cancels_only_their_own_sign_in(), test_the_same_folder_written_two_ways_is_the_same_folder(), test_two_folders_never_see_or_replace_each_others_sign_in(), test_your_usual_folder_adopts_an_older_sign_in_and_other_folders_do_not() (+1 more)

### Community 36 - "Security"
Cohesion: 0.14
Nodes (5): Security, test_a_minted_link_works_once_and_expires(), test_guessing_a_minted_link_counts_toward_the_lockout(), test_reusing_the_first_link_is_still_refused_without_counting_as_a_guess(), test_the_first_link_and_minted_links_are_separate_and_the_first_can_be_closed()

### Community 37 - "Connection Studio design pass"
Cohesion: 0.20
Nodes (9): Avatar and guide update, Connection Studio design pass, Conversation scope update, Desktop workflow validation, First-click usability correction, How Link works, progress tracker and walkthrough (D55, 2026-11-19), Networking sources and imagery, Quality-of-life and motion update (+1 more)

### Community 38 - "encounters.py"
Cohesion: 0.08
Nodes (39): calendar_start(), calendar_sync(), checkin_answer(), checkins_due(), email_sync(), encounter_dismiss(), now(), _addresses() (+31 more)

### Community 39 - "Coaching playbook"
Cohesion: 0.29
Nodes (6): After (the first 48 hours matter), Before a conversation (coffee chat, career fair, meetup), Coaching playbook, During, I don't know where to start (no contacts yet), When students say...

### Community 40 - "Link — handoff"
Cohesion: 0.33
Nodes (5): Checks and what is still unverified, Link — handoff, Open threads, Run it on your Mac, What the current build contains

### Community 41 - "Link Coach"
Cohesion: 0.29
Nodes (6): Drafting messages, How to help, Link Coach, References (read when needed), Rules you never break, Start of every chat

### Community 42 - "connectors.py"
Cohesion: 0.24
Nodes (4): _b64(), GoogleCalendar, normalize_google(), _when()

### Community 43 - "Guidance"
Cohesion: 0.40
Nodes (4): About Streamline, Guidance, Guidance icons / Streamline, Open-source license

### Community 44 - "Plain language"
Cohesion: 0.33
Nodes (5): Honest privacy wording (say this if asked, or at the start if the student seems worried), Plain language, What Link is (use if someone asks), What not to promise, Words to use

### Community 45 - "test_mail.py"
Cohesion: 0.14
Nodes (16): test_starting_from_someone_you_email_keeps_that_suggestion(), Mail, make(), msg(), synced(), test_a_bad_decision_is_refused_and_decisions_are_final(), test_a_version_seven_database_gains_the_email_table(), test_delete_everything_also_cancels_the_email_sign_in() (+8 more)

### Community 47 - "Examples"
Cohesion: 0.40
Nodes (4): Example 1: starting from zero, Example 2: following up and keeping a promise, Example 3: a student who froze, Examples

### Community 48 - "Link Coach: paste-ready Gem"
Cohesion: 0.50
Nodes (3): Instructions (paste everything below this line into the Instructions box), Knowledge files to upload (Gem editor → Knowledge → Add files), Link Coach: paste-ready Gem

### Community 51 - "Settings"
Cohesion: 0.10
Nodes (31): run(), AIClient, AIRequest, AIResult, build_client(), Claim, CompareOut, EvidenceCandidate (+23 more)

### Community 53 - "test_calendar_connect.py"
Cohesion: 0.13
Nodes (25): attendee(), event(), maya(), Provider, signed_in(), test_a_guessed_name_can_be_corrected_and_blank_is_refused(), test_a_known_address_is_offered_as_the_same_person(), test_a_name_is_guessed_from_the_address_and_marked_as_a_guess() (+17 more)

### Community 54 - "web.py"
Cohesion: 0.13
Nodes (5): _b64url(), signin(), _page(), valid_timezone(), WipeIn

### Community 55 - "create_web_app"
Cohesion: 0.16
Nodes (15): create_web_app(), client_key(), delete_account(), email_mac(), finish(), finish_signin(), guard(), lifespan() (+7 more)

### Community 56 - "test_ai_gateway.py"
Cohesion: 0.30
Nodes (16): AIUnavailable, CompanionTurn, DraftOut, fake_api(), gateway(), priced_mock(), test_activity_log_holds_metadata_only(), test_budget_block_never_reaches_the_client() (+8 more)

### Community 57 - "create"
Cohesion: 0.09
Nodes (43): create(), agent(), checkMark(), chips(), done(), flash(), metStep(), nav() (+35 more)

### Community 58 - "nudges.py"
Cohesion: 0.16
Nodes (18): nudges_info(), nudges_pause(), nudges_resume(), nudges_save(), due_keys(), _eligible(), get_settings(), get_state() (+10 more)

### Community 59 - "cli.py"
Cohesion: 0.15
Nodes (17): _delete_key(), _launch(), main(), _quit(), _run(), _set_key(), _tip_if_client_file_is_open(), _web() (+9 more)

### Community 60 - "_nudge"
Cohesion: 0.20
Nodes (9): _nudge(), install(), is_installed(), plist_bytes(), plist_path(), uninstall(), build_notifier(), MacNotifier (+1 more)

### Community 61 - "AllowlistTransport"
Cohesion: 0.18
Nodes (4): AllowlistTransport, NeverSent, test_egress_allows_the_provider_api(), test_egress_refuses_everything_but_the_provider_api()

### Community 62 - "security.py"
Cohesion: 0.28
Nodes (3): _deny(), make_guard(), guard()

### Community 63 - "Database"
Cohesion: 0.10
Nodes (32): person_clear(), person_get(), Database, _check_source(), _clean(), save_connection(), person_summary(), assign_log() (+24 more)

### Community 65 - "config.py"
Cohesion: 0.13
Nodes (11): anon(), app(), client(), db(), mock_ai(), settings(), test_only_google_hosts_over_https_can_be_reached(), test_refuses_to_bind_anything_but_loopback() (+3 more)

### Community 66 - ".q"
Cohesion: 0.14
Nodes (10): email_contacts_pending(), encounters_pending(), evidence_confirm_all(), evidence_extract(), matches(), pending(), matches(), pending() (+2 more)

### Community 68 - "test_calendar_connect.py"
Cohesion: 0.25
Nodes (10): ask_for_link(), _client_file(), google(), ok_handler(), test_authorize_url_uses_pkce_state_and_read_only_scope(), test_events_ask_google_only_for_the_fields_link_keeps(), test_full_sign_in_through_the_callback_without_a_session_cookie(), test_the_callback_with_a_wrong_state_connects_nothing() (+2 more)

### Community 69 - "create"
Cohesion: 0.27
Nodes (14): create(), celebrate(), check(), compact(), ctas(), enter(), nextLink(), render() (+6 more)

### Community 70 - "test_journey.py"
Cohesion: 0.22
Nodes (8): stages(), test_a_drafted_message_counts_as_reaching_out(), test_a_person_or_a_note_finishes_people_and_notes(), test_any_one_piece_of_groundwork_is_enough(), test_evidence_a_saved_job_or_pasted_text_each_count_as_groundwork(), test_reaching_out_needs_a_kept_plan_not_just_a_suggestion(), test_sample_data_never_counts(), test_skip_and_oriented_are_the_same_flag()

### Community 71 - "launcher.py"
Cohesion: 0.17
Nodes (15): _launcher(), app_path(), applescript_source(), _applescript_string(), _base(), ensure_key(), install(), is_installed() (+7 more)

### Community 75 - "check_guide_browser.py"
Cohesion: 0.30
Nodes (7): chip(), first_run(), from_the_calendar(), primary(), question(), serve(), shot()

### Community 76 - "check_walkthrough_browser.py"
Cohesion: 0.41
Nodes (9): counts(), laptop(), next_step(), phone(), ready(), serve(), shot(), step_no() (+1 more)

### Community 77 - "GoogleMail"
Cohesion: 0.20
Nodes (4): GoogleMail, normalize_message(), test_a_sent_message_with_only_a_to_address_keeps_its_recipient(), test_mail_traffic_may_reach_only_google_sign_in_and_gmail()

### Community 78 - "GoogleLogin"
Cohesion: 0.17
Nodes (3): GoogleLogin, LoginError, normalize_email()

### Community 80 - "check_web_browser.py"
Cohesion: 0.22
Nodes (4): google(), no_mac_words(), sign_in(), through_google()

### Community 81 - "WebConfig"
Cohesion: 0.24
Nodes (4): load_google_client_file(), WebConfig, test_a_wrong_client_file_gives_a_plain_error_without_its_contents(), test_settings_come_from_the_environment_and_a_web_client_file()

### Community 84 - "check_companion_browser.py"
Cohesion: 0.47
Nodes (6): first_visit(), no_technical(), phone_and_people(), serve(), shot(), visible_words()

### Community 87 - "journey"
Cohesion: 0.29
Nodes (4): journey(), journey_oriented(), journey(), mark_oriented()

### Community 88 - "test_a_refused_all_folders_list_falls_back_to_the_inbox_and_a_403_says_why"
Cohesion: 0.33
Nodes (3): _google_reason(), test_a_refused_all_folders_list_falls_back_to_the_inbox_and_a_403_says_why(), _get()

### Community 89 - "Plain-language backlog (from the D53 audit, 2026-11-19)"
Cohesion: 0.40
Nodes (4): Hide in the user version (18), Plain-language backlog (from the D53 audit, 2026-11-19), Rewrite in plain words (39), Show only when relevant (1)

## Knowledge Gaps
- **2 isolated node(s):** `career-companion`, `npx`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 526 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `Budget`, `network_imports.py`, `Database`, `test_workflows.py`, `test_validate_and_ranking.py`, `test_launcher.py`, `store.py`, `coaching.py`, `config.py`, `services.py`, `cli.py`, `test_nudges.py`, `Secrets`, `Security`, `encounters.py`, `test_mail.py`, `Settings`, `test_calendar_connect.py`, `web.py`, `test_ai_gateway.py`, `nudges.py`, `cli.py`, `_nudge`, `security.py`, `Database`, `config.py`, `.q`, `launcher.py`, `check_guide_browser.py`, `check_walkthrough_browser.py`, `check_companion_browser.py`, `Pool`, `OAuthFlows`, `journey`, `follow_up_candidates`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `create_app()` (e.g. with `cancel_sign_ins()` and `Settings`) actually correct?**
  _`create_app()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `career-companion`, `npx` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Budget` be split into smaller, more focused modules?**
  _Cohesion score 0.08773784355179703 - nodes in this community are weakly interconnected._
- **Why does `Career Companion: decision record` connect `cli.py` to `Database`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 110 inferred relationships involving `Database` (e.g. with `AIClient` and `AIRequest`) actually correct?**
  _`Database` has 110 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_web.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08176100628930817 - nodes in this community are weakly interconnected._