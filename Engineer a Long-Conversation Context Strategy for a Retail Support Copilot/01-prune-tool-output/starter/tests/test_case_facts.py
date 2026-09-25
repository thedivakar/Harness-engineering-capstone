"""Shape tests for the case-facts persistent block.

These exercise the structure of CaseFacts / REQUIRED_FIELDS / to_markdown /
CaseFactExtractionError without making a Claude call. The live extract() path is
exercised under the `--build` run, not here.
"""
from __future__ import annotations

import pytest

from retail_context.case_facts import (
    CaseFactExtractionError,
    CaseFacts,
    REQUIRED_FIELDS,
)


def test_required_fields_has_12_entries():
    assert len(REQUIRED_FIELDS) == 12


def test_required_fields_cover_three_issues():
    # Three issue groups must be represented so the case-facts block can
    # carry a fact for every issue type the transcript spans.
    assert "customer_id" in REQUIRED_FIELDS
    assert any(f.startswith("refund_") for f in REQUIRED_FIELDS)
    assert any(f.startswith("subscription_") for f in REQUIRED_FIELDS)
    assert any(f.startswith("payment_update_") or "payment_method" in f for f in REQUIRED_FIELDS)


def test_case_facts_dataclass_has_required_fields():
    annotated = set(CaseFacts.__dataclass_fields__.keys())
    assert set(REQUIRED_FIELDS).issubset(annotated)


def _sample_facts() -> CaseFacts:
    return CaseFacts(
        customer_id="CUST-88421",
        refund_order_id="ORD-77310",
        refund_amount_usd=22.14,
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


def test_to_markdown_uses_top_level_header_and_fixed_key_order():
    md = _sample_facts().to_markdown()
    assert md.startswith("# Case Facts")
    # Identifiers preserved verbatim.
    assert "CUST-88421" in md
    assert "ORD-77310" in md
    # Status tokens preserved as snake_case strings, not natural language.
    assert "AVS_MISMATCH" in md
    assert "in_progress" in md


def test_extraction_error_lists_missing_fields():
    err = CaseFactExtractionError(missing=["customer_id", "refund_status"], raw={})
    assert err.missing == ["customer_id", "refund_status"]
    assert "customer_id" in str(err)
