<!-- TODO (Exercise 3): Replace this file with the compression prompt.

This file is the system message for the per-resolved-segment Claude call in
`compressor.summarize_segment`. It is committed as a *template* so the
intent is auditable: a reviewer reads this file to decide whether following it
would reliably produce the required structure.

Required structure of the model's output:

  1. ONE sentence naming what was resolved (past-tense outcome).
  2. 3-6 bullet facts: amounts, IDs, statuses, dates — preserved verbatim.
  3. ONE sentence naming the resolution (the segment's terminal state).

Rules to bake into the prompt:

  - Total output ≤ 500 tokens. Tight is better than verbose.
  - Preserve identifiers and amounts byte-exact (e.g., ORD-77310, $22.14 —
    no "around $20", no "approximately").
  - Preserve snake_case status tokens verbatim from the transcript.
  - No prose around the structure — no preambles, no closing remarks, no
    code fences in the output.

The prompt is yours to write. The above is the contract the reviewer (and
the eval pipeline) will check against. -->
