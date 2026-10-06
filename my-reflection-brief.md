Reflection Brief — Harness Engineering Capstone
Name: Divakar  
Date: 2026-10-06
Every answer below cites a concrete artifact from this submission. The cited paths are relative to the capstone root.
Environment
Models: System 1 and System 2 artifacts use `claude-haiku-4-5-20251001`; System 4 uses the recorded `claude-sonnet-4-6` response; System 3 is validated locally.
OS / Python: Linux environment, Python 3.13.0 is recorded in `evidence/system2_context_strategy/pytest_S2.log`.
Approx. API spend: System 1 recorded $0.1238 for its run in `evidence/system1_agentic_loop/summary.md`; the submitted artifacts do not record one combined spend total for all systems.
---
Part 1 — Per-system
System 1 — Agentic loop
Loop control.  
The trace `evidence/system1_agentic_loop/claim_01_kitchen_fire.jsonl` records `stop_reason: "tool_use"` on turn 1 followed by `stop_reason: "end_turn"` on turn 2. The continue/stop decision is implemented in `Build a Claims Intake Agent with a stop_reason-Driven Loop/exercises/03-dynamic-decomposition/solution/claims_intake/loop.py`: `tool_use` executes tool results and continues, `end_turn` returns the final state, and any other value raises `UnexpectedStopReason`. This is also directly covered by `tests/test_loop.py::test_loop_terminates_on_end_turn` and `::test_loop_continues_on_tool_use`, with the anti-pattern audit in `tests/test_antipatterns.py`.
Anti-pattern.  
`tests/test_antipatterns.py::test_no_string_membership_against_text_in_loop` checks that the loop does not use string-membership tests against model text to drive control flow. If this anti-pattern were introduced, a phrase in the assistant's natural-language output could accidentally become a control signal and terminate or redirect the loop even though the API's `stop_reason` had not requested that behavior. The same test file also checks that the loop does not use an integer-literal iteration cap as its primary stopping mechanism.
Tool design.  
`classify_claim` and `route_to_adjuster` both deal with the claim-type vocabulary, but their descriptions clearly separate classification from terminal routing: `classify_claim` records a type/confidence/rationale, while `route_to_adjuster` is a terminal tool called only after classification and severity. The schemas also use enums, required fields, and explicit sequencing guidance in `claims_intake/tools.py`. A structured tool error such as `{"is_error":true,"error_category":"permanent","is_retryable":false,"message":"classify_claim must be called before routing"}` tells the agent exactly what failed and whether retrying is appropriate, which a generic error string would not guarantee.
Your numbers.  
In `evidence/system1_agentic_loop/summary.md`, `claim_03_water_damage` completed in 7 turns at an estimated $0.0307, including one clarification. The README for the final dynamic-decomposition exercise gives an approximate $0.05 total for the full run rather than a per-claim price, so the claim-level figure is not directly comparable to that total. The actual eight-claim run recorded $0.1238 total, reflecting the real token usage of the captured run.
System 2 — Context strategy
The reduction.  
`evidence/system2_context_strategy/budget.json` records 38,708 baseline tokens, 16,797 assembled tokens, and 56.61% reduction. The active section is 15,789 tokens, about 94% of the assembled context, so it dominates because the current payment-method issue is still being worked and must retain turn-by-turn fidelity. The active segment is therefore kept byte-exact while the resolved issues are compressed.
Summarize vs preserve.  
The rule in `retail_context/compressor.py` is status-based: only segments whose status is `resolved` are summarized, while the active segment is preserved byte-exact. `budget.json` records the resulting section sizes as case facts 204, resolved refund 373, resolved subscription 449, and active 15,789 tokens; the compression calls show refund 12,334 → 360 tokens and subscription 11,475 → 436 tokens. This preserves the current working conversation while reducing older resolved narrative to compact summaries.
Facts block.  
In `evidence/system2_context_strategy/eval.jsonl`, all 6/6 questions pass, including Q6 whose expected structured status is `in_progress`. In the case-facts-stripped `eval_control.jsonl`, Q6's model answer says the structured token is not present, so it is a real regression caused by removing the persistent Case Facts block. The original captured artifact had a substring-scoring false positive because the answer mentioned `in_progress` as an example while denying that it was present; the evaluator has been corrected so that this negative/example mention is scored as FAIL, documented in `control_scoring_note.md`.
System 3 — Claude Code config
Path-scoped rules.  
`evidence/system3_claude_config/evidence_rule_rule_react.md` has frontmatter `paths: ["src/components/**/*", "src/pages/**/*"]`. This is better than putting React guidance in a directory-level `CLAUDE.md` because the rule activates only for matching paths while remaining cross-cutting across the monorepo. The same path-scoping approach is used for API and test rules in the submitted `.claude` structure.
Forked skill.  
`evidence/system3_claude_config/evidence_rule_skill.md` contains `context: fork` and an `allowed-tools` list limited to read-oriented commands such as `Read`, `Grep`, `Glob`, and read-only Git/GitHub checks. Forking keeps verbose deployment-check discovery out of the main session, while the read-only allowlist prevents the skill from modifying, pushing, or deploying the repository. Without those constraints, a diagnostic check could pollute the main context or accidentally gain mutation/deployment authority.
Scope.  
`evidence/system3_claude_config/evidence_rule_claude.md` defines project-level configuration as `./CLAUDE.md`, `.claude/standards/`, and `.claude/rules/`, while user-level configuration is under `~/.claude/`. A concrete project-level example in this submission is `.claude/rules/react.md`; the documented user-level example is `~/.claude/CLAUDE.md`, which is intentionally not shared through version control. The validator result in `evidence/system3_claude_config/validator_output.txt` is `OK`.
System 4 — Orchestration
Push work down.  
The warm fixture contains 40 defect rows, while the captured shift run returned 0 new defects because its `since` timestamp was `2026-09-25T02:10:04Z` and the newest fixture defect is from April 29. `WarmStore.defects_since()` uses the indexed SQL query `SELECT * FROM defects WHERE ts > ? ORDER BY ts DESC LIMIT ?`, with timestamp indexes defined in `warm.py`; the supporting evidence is `evidence/system4_orchestration/sql_filter_evidence.md`. Because the timestamp predicate and limit execute in SQLite before `gather_new_defects()` returns, the model receives only the filtered result rather than the full 40-row history.
Crash recovery.  
`shift_monitor/recovery.py` defines a 30-minute stale-resume threshold: incomplete state at 1, 29, or 30 minutes resumes, while 31 or 60 minutes starts fresh; these cases are all visible in `pytest_S4.log`. A fresh start is safer once partial state is stale because the old working set is no longer trusted as the current shift state, so the architecture can restart from the known findings/summary rather than replay stale partial progress. This behavior is summarized in `evidence/system4_orchestration/recovery_evidence.md`.
Small state.  
`evidence/system4_orchestration/hot_state_size.txt` records `hot_state.json` at 643 bytes, well below the approximately 5 KB budget enforced by the tiered-state tests. The budget matters even for a once-per-shift system because the hot state persists across indefinitely many shifts, so an unbounded state file would eventually increase every future read/write and model prompt. A fixed small state keeps the per-shift working set predictable while warm/cold storage retains longer history.
---
Part 2 — Synthesis
Three layers.  
Model: `claims_intake/client.py` and `claims_intake/system_prompt.py` define the model-facing interaction and domain guidance. Harness: `claims_intake/loop.py` is the deterministic control layer that interprets `stop_reason`, executes tools, tracks tokens, and enforces the budget. Orchestration: `shift_monitor/pipeline.py`, `warm.py`, and `recovery.py` coordinate state retrieval, invocation, recovery, and persistence across shifts.
Deterministic vs prompt.  
A deterministic behavior is the orchestration atomic/state enforcement and the agentic-loop `stop_reason` handling, both backed by tests such as `test_run_shift_invokes_client_exactly_once_and_writes_state` and `test_loop_terminates_on_end_turn`. Prompt-based guidance appears in the insurance system prompt and the rich shift prompt, where the model is told what report structure and domain behavior to produce. Deterministic enforcement is appropriate for safety-critical boundaries and invariants; prompts are appropriate when the model must reason about facts and choose among domain actions.
Context, two faces.  
System 2 manages context within one long conversation, reducing 38,708 → 16,797 tokens (56.61%) while preserving the active issue verbatim. System 4 manages context across shifts, keeping `hot_state.json` at 643 bytes and querying only new defects from warm storage. Both apply the same principle—keep the working context small and high-signal—but System 2 uses summarization/compression while System 4 uses tiered state plus SQL filtering.
Reliability you can't see in one run.  
`pytest_S4.log::test_fork_for_hypothesis_copies_state_without_mutating_base` guarantees that a hypothesis branch cannot mutate the base state, something a single successful shift run would not demonstrate. The same suite tests independent scratchpads for two forks. This matters before shipping because a single run can look correct while hidden state contamination could corrupt later shifts or sibling investigations.
Blast radius.  
System 4 has a bounded blast radius because the model sees the SQL-filtered new-defect slice plus a small hot state, rather than the entire warm database. Its state writes are atomic and its test suite verifies the 5 KB hot-state budget, while `run_shift` makes one client call per shift. The operational kill switch is to stop/disable the shift invocation before calling `run_shift`; the architecture does not require the model to have direct database-write or deployment authority.
---
Part 3 — Honest assessment
What broke.  
The submitted artifacts do not contain a reliable first-try environment failure, so I cannot truthfully invent one. What I can verify is that the final checks passed with 29 System 1 tests, 30 System 2 tests, 35 System 3 tests, and 33 System 4 tests, and the System 3 validator returned `OK`. Those artifacts are the evidence I used to confirm the final environment was working.
What you'd change.  
I would change the control-evaluation scorer so it distinguishes an expected token being asserted from the model merely mentioning that token inside a negative statement. The submitted Q6 control answer says the `in_progress` token is not present, but the original substring scorer marked it `passed: true` because the token appeared in an example phrase. The corrected evaluator and `control_scoring_note.md` make that regression explicit, which would make the evidence pipeline more reliable before the next submission.
