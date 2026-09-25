"""Position-aware assembly."""
from __future__ import annotations

from retail_context.assemble import build
from retail_context.case_facts import CaseFacts
from retail_context.compressor import Compressed, Summary


def _fake_facts() -> CaseFacts:
    return CaseFacts(
        customer_id="CUST-88421",
        refund_order_id="ORD-77310",
        refund_amount_usd=48.99,
        refund_status="processed",
        subscription_id="SUB-22119",
        subscription_plan="Pantry Plus Monthly",
        subscription_cancel_reason="duplicate_charge",
        subscription_status="cancelled_with_prorated_refund",
        active_payment_method_last4="4242",
        new_payment_method_last4="7782",
        payment_update_failure_code="AVS_MISMATCH",
        payment_update_status="in_progress",
    )


def _fake_compressed() -> Compressed:
    return Compressed(
        summaries={
            "refund": Summary(
                issue_id="refund",
                text="**Outcome.** Refund processed.\n\n**Key facts.**\n- ORD-77310\n- $48.99\n\n**Resolution.** Done.",
                input_tokens=1234,
                output_tokens=123,
            ),
            "subscription": Summary(
                issue_id="subscription",
                text="**Outcome.** Subscription cancelled.\n\n**Key facts.**\n- SUB-22119\n- duplicate_charge\n\n**Resolution.** cancelled_with_prorated_refund.",
                input_tokens=1500,
                output_tokens=140,
            ),
        },
        active_text="Turn 29 (customer): I need to update my card.\n\nTurn 30 (agent): Sure.",
        active_issue_id="payment_update",
    )


def test_assemble_section_order_exact():
    """Exact section header sequence."""
    assembled = build(_fake_facts(), _fake_compressed())
    md = assembled.markdown

    case_idx = md.index("# Case Facts")
    refund_idx = md.index("# Resolved: Refund inquiry")
    sub_idx = md.index("# Resolved: Subscription cancellation")
    active_idx = md.index("# Active issue: Payment-method update")

    assert case_idx < refund_idx < sub_idx < active_idx


def test_active_segment_byte_exact():
    """Active section body is byte-exact equal to active_text."""
    compressed = _fake_compressed()
    assembled = build(_fake_facts(), compressed)
    # The active_text must appear verbatim in the markdown.
    assert compressed.active_text in assembled.markdown
    # And specifically inside the active section (after the header).
    active_header_idx = assembled.markdown.index("# Active issue: Payment-method update")
    assert compressed.active_text in assembled.markdown[active_header_idx:]


def test_no_interleaving_of_resolved_and_active():
    """Section boundaries are exclusive."""
    assembled = build(_fake_facts(), _fake_compressed())
    md = assembled.markdown
    active_idx = md.index("# Active issue:")
    # No resolved-section headers may appear AFTER the active header
    assert "# Resolved:" not in md[active_idx:]
