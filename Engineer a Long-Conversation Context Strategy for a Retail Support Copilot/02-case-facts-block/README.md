# Exercise 2: Extract Case Facts into a Persistent Block

*Extract transactional case facts from a long transcript into a persistent 12-field Markdown block that survives compression, using an LLM call with a strict schema and a no-silent-fill failure mode.*

---

## What you start with

`starter/` is byte-identical to Exercise 1's `solution/` — your pruner is already in place. New for Exercise 2:

- `retail_context/case_facts.py` is now the active file you implement (four TODO blocks).
- `tests/test_case_facts.py` runs against the shape of `REQUIRED_FIELDS`, the `CaseFacts` dataclass, the `to_markdown()` rendering, and the `CaseFactExtractionError` contract — none of these tests make a Claude call.
- `data/transcript_48turns.json` is the same 48-turn fixture the rest of the pipeline will consume.

## What to build

Open `starter/retail_context/case_facts.py` and resolve the four TODO blocks:

1. **`REQUIRED_FIELDS`** — the 12-field tuple, in the same order you will render them in `to_markdown()`. The order is the contract; the prompt and the dataclass both follow it.
2. **`CaseFacts` dataclass + `to_markdown(self)`** — typed fields (str for IDs / status tokens / last4, float for `refund_amount_usd`), and a Markdown rendering that opens with `# Case Facts` and groups the fields by issue (Customer / Refund (resolved) / Subscription (resolved) / Payment update (active)).
3. **`_SYSTEM_PROMPT`** — a strict-schema extraction prompt: every field required, null on missing (do **not** invent), snake_case status tokens preserved verbatim, `refund_amount_usd` numeric, output JSON only.
4. **`extract(transcript, *, model=None, log_path=None)`** — call `complete_with_system`, parse the JSON, write the `case_facts_call.json` audit log if `log_path` is given, validate every required field is present and non-empty (raise `CaseFactExtractionError` listing what's missing), construct and return a `CaseFacts`.

## Verify

Without an API key (shape tests only):

```bash
pytest tests/test_case_facts.py tests/test_pruner.py tests/test_antipatterns.py::test_pruner_has_no_anthropic_import -v
```

All nine tests must pass.

If you want to exercise the live extraction (one Claude call against the 48-turn transcript, ~$0.01 on Haiku 4.5), you can run a one-liner with `ANTHROPIC_API_KEY` set:

```bash
ANTHROPIC_API_KEY=sk-ant-... python3 -c "
from pathlib import Path
from retail_context import case_facts, transcript
t = transcript.load('data/transcript_48turns.json')
facts = case_facts.extract(t, log_path=Path('runs/ex2-smoke/case_facts_call.json'))
print(facts.to_markdown())
"
```

Inspect the rendered Markdown: every required field appears in the fixed order with the right type (string for IDs, number for `refund_amount_usd`, snake_case for status tokens). `case_facts_call.json` contains the audit log.

## Where to look if you get stuck

- **The full system prompt** sits in front of one Claude call. There is no agentic loop here — the model returns one JSON object or you raise. This is structured *output*, not structured conversation.
- **Why a loud failure mode?** Silent null-fill on a missing field would mean the eval (later in the arc) confidently cites a value the model invented. The strict guard is the defense against that class of failure.
- **`_parse_json` is provided** — it handles the case where the model accidentally wraps its output in a `` ``` `` fence despite the prompt. Use it.

## When you're done

Compare to `solution/retail_context/case_facts.py` for the reference. Exercise 3 picks up from your solution to build the token counter and the resolved-segment compressor that runs alongside this block.
