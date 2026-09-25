"""One-shot transcript fixture generator.

Produces `data/transcript_48turns.json` — a 48-turn customer/agent conversation
for the retail "Pantry Plus" online grocery store. Three issues:
  - refund     (turns 1-14, resolved)
  - subscription (turns 15-28, resolved)
  - payment_update (turns 29-48, active)

Required case facts must land at specific turns.

Authoring uses Sonnet 4.6 (one-shot; the project itself defaults to Haiku 4.5
for compression). Validated post-hoc against the placement contract.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from retail_context.client import complete

AUTHORING_MODEL = "claude-sonnet-4-6"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "transcript_48turns.json"

REFUND_SPEC = """You are writing a realistic 14-turn customer-support transcript for a fictitious
online grocery retailer called "Pantry Plus".

Setting: a customer is asking about a refund for a damaged order of pantry items.
The conversation alternates strictly: turn 1 customer, turn 2 agent, turn 3 customer,
turn 4 agent, ... turn 13 customer, turn 14 agent. The conversation ends with the agent
confirming the refund has been processed.

Verbosity target: each turn ~500 words. Customers complain, narrate their day, repeat
themselves, attach context. Agents quote policy, recite procedures, reflect back what the
customer said, list options, set expectations. This is intentionally over-talkative —
real support chats are like this. Do not exceed 550 words per turn.

Required placements — these MUST appear in the *exact* turn:
  - Turn 3: the customer states their customer ID as "CUST-88421" (the agent had asked
    for it; the customer reads it off a screen or email). The exact token CUST-88421
    must appear in turn 3's text.
  - Turn 5: the order in question is identified as "ORD-77310". The exact token
    ORD-77310 must appear in turn 5's text.
  - Turn 9: the refund amount is stated as "$48.99" (the customer is asking what the
    refund will be; the agent quotes the line-item subtotal). The exact token $48.99
    must appear in turn 9's text.
  - Turn 14: the agent confirms the refund has been "processed" to the customer's
    original payment method. The word "processed" must appear in turn 14's text.

Other realism: agents use phrases like "I appreciate your patience", "let me pull that
up", "per our return policy section 4.2", and so on. Customers vent, mention other
unrelated frustrations briefly, etc.

Output: return ONLY a JSON array of 14 objects, each with keys "turn" (int 1-14),
"role" ("customer" or "agent"), and "text" (string). No prose, no markdown, no code
fences — just the JSON array."""

SUBSCRIPTION_SPEC = """You are writing the SECOND segment of a longer customer-support transcript for
the fictitious online grocery retailer "Pantry Plus". Turns are numbered 15 through 28
(14 turns). The same customer from turns 1-14 (customer ID CUST-88421) is now raising a
second issue in the same chat: their monthly subscription has been charged twice this
month and they want it cancelled with a prorated refund for the duplicate.

Turn alternation: turn 15 customer, 16 agent, 17 customer, 18 agent, ..., 27 customer,
28 agent. The conversation ends with the agent confirming cancellation with prorated
refund.

Verbosity target: each turn ~700 words. Same talkative tone as the prior segment.

Required placements — exact-turn:
  - Turn 16: the agent confirms the subscription ID as "SUB-22119". Exact token
    SUB-22119 must appear in turn 16.
  - Turn 17: the customer confirms the plan name as "Pantry Plus Monthly". Exact phrase
    "Pantry Plus Monthly" must appear in turn 17.
  - Turn 23: the cancellation reason "duplicate_charge" surfaces — the agent records it
    as the structured cancel reason in their CRM, and includes the literal string
    duplicate_charge in their message (e.g., "I'll mark this in our system as
    duplicate_charge"). Exact token duplicate_charge must appear in turn 23.
  - Turn 28: the agent confirms the subscription is now in status
    "cancelled_with_prorated_refund". Exact token cancelled_with_prorated_refund
    must appear in turn 28.

The customer may briefly reference the earlier refund inquiry being resolved already
("now that the damaged-order refund is sorted, I also wanted to ask about...").

Output: return ONLY a JSON array of 14 objects with keys "turn" (int 15-28), "role",
"text". No prose, no markdown, no code fences."""

PAYMENT_UPDATE_SPEC = """You are writing the THIRD segment of a longer customer-support transcript for
"Pantry Plus". Turns numbered 29 through 48 (20 turns). The same customer (CUST-88421)
is now raising a third issue: they need to update the credit card on file because the
old one is expiring. The new card they want to add has been failing with an AVS error
that neither the customer nor the agent can immediately resolve. **This issue is not
resolved at the end of the segment** — it's still active and pending further work.

Turn alternation: turn 29 customer, 30 agent, ..., 47 customer, 48 customer (so the
final turn is the customer, mid-issue). The very last turn (48) is the customer still
asking for help with the unresolved AVS issue — the conversation ends mid-stream.

Verbosity target: each turn ~550 words. Same talkative tone. Do not exceed 600 words per turn.

Required placements — exact-turn:
  - Turn 31: the customer's currently-on-file card is identified by its last 4 digits
    "4242". The exact token 4242 must appear in turn 31.
  - Turn 39: the new card the customer is trying to add has last 4 digits "7782".
    The exact token 7782 must appear in turn 39.
  - Turn 44: the payment gateway returns the failure code "AVS_MISMATCH". The exact
    token AVS_MISMATCH must appear in turn 44 (the agent reads it from the gateway
    response and quotes it back).

The segment ends with the issue unresolved — last turn shows the customer asking what
to try next. Do NOT have the agent successfully add the card. The issue's narrative
status by turn 48 is "in_progress".

Turn 48 is the customer (not the agent), and represents a partial / unresolved state.

Output: return ONLY a JSON array of 20 objects with keys "turn" (int 29-48), "role",
"text". No prose, no markdown, no code fences."""


def author_segment(spec: str, expected_turns: list[int]) -> list[dict]:
    raw = complete(spec, model=AUTHORING_MODEL, max_tokens=16000).strip()

    # Strip optional ``` fences if the model used them
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.rstrip().endswith("```"):
            raw = raw.rsplit("```", 1)[0]

    turns = json.loads(raw)
    actual_turns = [t["turn"] for t in turns]
    if actual_turns != expected_turns:
        raise ValueError(
            f"Turn numbers mismatch.\n  expected: {expected_turns}\n  got:      {actual_turns}"
        )
    return turns


def validate_placements(turns: list[dict], placements: dict[int, list[str]]) -> None:
    by_turn = {t["turn"]: t["text"] for t in turns}
    errors: list[str] = []
    for turn, required_tokens in placements.items():
        text = by_turn.get(turn, "")
        for tok in required_tokens:
            if tok not in text:
                errors.append(f"  Turn {turn}: missing required token {tok!r}")
    if errors:
        raise ValueError("Placement validation failed:\n" + "\n".join(errors))


def main() -> int:
    print("Authoring refund segment (turns 1-14)...")
    refund = author_segment(REFUND_SPEC, list(range(1, 15)))
    validate_placements(
        refund,
        {3: ["CUST-88421"], 5: ["ORD-77310"], 9: ["$48.99"], 14: ["processed"]},
    )
    for t in refund:
        t["issue_id"] = "refund"

    print("Authoring subscription segment (turns 15-28)...")
    subscription = author_segment(SUBSCRIPTION_SPEC, list(range(15, 29)))
    validate_placements(
        subscription,
        {
            16: ["SUB-22119"],
            17: ["Pantry Plus Monthly"],
            23: ["duplicate_charge"],
            28: ["cancelled_with_prorated_refund"],
        },
    )
    for t in subscription:
        t["issue_id"] = "subscription"

    print("Authoring payment_update segment (turns 29-48)...")
    payment = author_segment(PAYMENT_UPDATE_SPEC, list(range(29, 49)))
    validate_placements(
        payment,
        {31: ["4242"], 39: ["7782"], 44: ["AVS_MISMATCH"]},
    )
    for t in payment:
        t["issue_id"] = "payment_update"

    fixture = {
        "customer_id": "CUST-88421",
        "active_issue_id": "payment_update",
        "issue_boundaries": {
            "refund": [1, 14],
            "subscription": [15, 28],
            "payment_update": [29, 48],
        },
        "turns": refund + subscription + payment,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(fixture, indent=2))
    print(f"Wrote {len(fixture['turns'])} turns to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
