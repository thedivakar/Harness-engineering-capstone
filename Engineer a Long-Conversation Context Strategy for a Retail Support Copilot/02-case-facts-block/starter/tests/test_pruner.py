"""Tool-output pruner."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from retail_context.pruner import KEPT_FIELDS, PrunerMissingFieldError, prune_lookup_order
from retail_context.tokens import count

FIXTURE = Path(__file__).resolve().parent.parent / "data" / "lookup_order_response.json"


@pytest.fixture(scope="module")
def raw():
    return json.loads(FIXTURE.read_text())


def test_lookup_order_fixture_has_at_least_40_fields(raw):
    assert len(raw) >= 40


def test_pruner_keeps_exactly_the_contracted_set(raw):
    pruned = prune_lookup_order(raw)
    assert tuple(pruned.keys()) == KEPT_FIELDS
    assert set(pruned.keys()) == {
        "order_id",
        "order_date",
        "order_total_usd",
        "fulfillment_status",
        "return_eligible_until",
    }


def test_pruned_output_under_200_tokens(raw):
    pruned = prune_lookup_order(raw)
    serialized = json.dumps(pruned)
    assert count(serialized) <= 200


def test_pruner_raises_on_missing_required_field(raw):
    broken = {k: v for k, v in raw.items() if k != "return_eligible_until"}
    with pytest.raises(PrunerMissingFieldError):
        prune_lookup_order(broken)
