# Claude AI Engineer — Harness Engineering

Source-of-truth repository for the exercises in the **Claude AI Engineer: Harness Engineering** course (`cd15315`). The course teaches the engineering around a Claude agent — the loop that drives it, the state and context strategies that keep it tractable over long runs, the orchestration that coordinates multiple invocations, and the Claude Code configuration a team works inside.

Each top-level folder is a self-contained course/project with a sequence of hands-on, test-driven exercises. Most exercises ship a `starter/` you fill in and a `solution/` reference, with the acceptance criteria pinned down by a pytest suite (or, for the Claude Code project, a validator).

## Projects

### [Build a Claims Intake Agent with a stop_reason-Driven Loop](Build%20a%20Claims%20Intake%20Agent%20with%20a%20stop_reason-Driven%20Loop/)

Build the agentic loop at the heart of a harness — the `while` loop the model controls, dispatching on `stop_reason` to continue on `tool_use`, return on `end_turn`, and raise on anything unexpected. The loop you write here is the artifact every later project extends.

- `exercises/01-loop/` — Build the `stop_reason`-driven agentic loop.
- `exercises/02-tools-and-audit/` — Tool execution and a per-turn audit trace.
- `exercises/03-dynamic-decomposition/` — Dynamic task decomposition on top of the loop.

### [Engineer a Long-Conversation Context Strategy for a Retail Support Copilot](Engineer%20a%20Long-Conversation%20Context%20Strategy%20for%20a%20Retail%20Support%20Copilot/)

Keep a copilot coherent over long conversations without blowing the context window: prune verbose tool output deterministically, maintain a durable case-facts block, compress under a token budget, and assemble the final prompt.

- `01-prune-tool-output/` — Trim a 57-field tool response to the fields the decision needs (no LLM call).
- `02-case-facts-block/` — Maintain a persistent case-facts block.
- `03-compress-with-budget/` — Compress conversation history under a token budget.
- `04-assemble-and-locate/` — Assemble the working prompt and locate context.

### [Build a Multi-Shift Quality Monitoring System with Claude Orchestration](Build%20a%20Multi-Shift%20Quality%20Monitoring%20System%20with%20Claude%20Orchestration/)

Engineer a Layer 3 orchestration system that runs once per 8-hour shift: tiered state to keep each session tiny, an invocation pipeline, crash recovery, and forked scratchpads.

- `01-tiered-state/` — Hot/warm/cold storage tiers (Pydantic + SQLite).
- `02-invocation-pipeline/` — The per-shift invocation pipeline.
- `03-crash-recovery/` — Resume cleanly after a crash.
- `04-fork-scratchpad/` — Fork sub-agent scratchpads.

### [Configure Claude Code for a Multi-Surface Monorepo Team](Configure%20Claude%20Code%20for%20a%20Multi-Surface%20Monorepo%20Team/)

Configure Claude Code for a team working in a multi-surface monorepo: modular `CLAUDE.md` and path-scoped rules, a project-scoped review command, a forked deploy-check skill, and a plan-mode/explore decision doc.

- `01-compose-modular-claude-code-configuration/` — Modular `CLAUDE.md` `@`-imports and path-scoped `.claude/rules/*.md`.
- `02-author-project-scoped-review-command/` — A project-scoped `/review` command.
- `03-author-forked-deploy-check-skill/` — A forked `deploy-check` skill.
- `04-plan-mode-and-explore-decision-doc/` — Plan mode vs. Explore decision doc.

## Folder layout

Every exercise pairs starter code with a solution and its own instructions. The exact nesting varies slightly by project:

```bash
<project>/
├── <NN-exercise-name>/        # numbered exercise step
│   ├── README.md              # exercise instructions, requirements, verify command
│   ├── starter/               # scaffold with TODO blocks to fill in
│   └── solution/              # reference implementation
```

Project-specific notes:

- **Claims Intake** nests its steps under an `exercises/` folder, and the per-exercise `README.md` lives alongside `starter/` and `solution/`.
- **Multi-Shift** keeps the instructions inside each `starter/README.md` and `solution/README.md` rather than at the exercise root.
- **Long-Conversation Context** and **Monorepo Team** put a `README.md` at the exercise root plus one inside `starter/` and `solution/`.

## Running an exercise

Each exercise's `README.md` is authoritative, but the Python projects follow the same steps — create a virtual environment, install in editable mode with dev extras, then run the scoped verify command:

```bash
cd "<project>/<exercise>/starter"
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q   # or the scoped verify command named in the exercise README
```

Expect the starter suite to fail until the `TODO` blocks are resolved; the exercise is complete when the verify command passes cleanly.

**Run the scoped verify command, not a bare `pytest`.** The Claims Intake, Long-Conversation Context, and Monorepo Team projects are *cumulative* — each exercise ships the full project test suite, so tests for later, not-yet-built steps are present from exercise 1. A bare `pytest` (even in a correct intermediate `solution/`) will show those later tests as expected reds. Each exercise README names the exact subset that should pass at that step; only the final exercise of a project goes fully green on a bare `pytest`. (The Multi-Shift project is the exception — each stage is self-contained and passes on its own.)

## License

See [LICENSE.md](LICENSE.md). Educational content © Udacity, Inc., licensed CC BY-NC-ND 4.0 except where noted.
