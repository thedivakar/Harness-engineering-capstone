You are condensing a resolved customer-support conversation segment into a tight factual summary that will be placed in the *middle* of a longer context window (the compressible zone). The compressed form must preserve every fact a downstream agent might need to reason about, while shedding narrative bulk.

# Required structure

Produce a Markdown block with exactly this shape:

```
**Outcome.** <one sentence stating what was resolved, in past tense>

**Key facts.**
- <bullet 1 — a specific, decision-relevant fact>
- <bullet 2>
- <bullet 3>
- <bullet 4 (optional)>
- <bullet 5 (optional)>
- <bullet 6 (optional)>

**Resolution.** <one sentence stating the final state at segment close>
```

Rules:

- The "Outcome" sentence is past tense and concrete (e.g., "The customer's damaged-order refund was processed for $48.99 to their original payment method").
- The "Key facts" list must be **3–6 bullets**. Each bullet is a specific fact a future agent might need: amounts, IDs, statuses, dates, reasons. No filler ("customer was upset"), no procedural narration ("agent looked up the policy").
- The "Resolution" sentence states the segment's terminal state and matches whatever status field is recorded in the underlying CRM.
- Preserve every numeric value, ID, and status code verbatim from the source — do not round, paraphrase, or generalize ("about $50" is forbidden when the source says "$48.99").
- Total length: ≤ 500 tokens. Aim for ~300 tokens — tight is better than verbose.
- Output ONLY the Markdown block above. No preamble, no postscript, no code fences.
