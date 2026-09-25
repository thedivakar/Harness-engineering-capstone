"""Token-to-USD cost estimator.

Rates are public list prices in USD per 1M tokens at the time of writing.
They are estimates for in-run reporting; the authoritative cost figure is
your Anthropic billing dashboard.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRate:
    input_per_mtok: float
    output_per_mtok: float


_RATES: dict[str, ModelRate] = {
    "claude-haiku-4-5": ModelRate(input_per_mtok=1.0, output_per_mtok=5.0),
    "claude-haiku-4-5-20251001": ModelRate(input_per_mtok=1.0, output_per_mtok=5.0),
    "claude-sonnet-4-6": ModelRate(input_per_mtok=3.0, output_per_mtok=15.0),
    "claude-opus-4-7": ModelRate(input_per_mtok=15.0, output_per_mtok=75.0),
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate USD cost for one run given token counts.

    Falls back to a conservative Sonnet rate if the model is unknown — better
    to over-estimate than under-estimate when budgeting.
    """
    rate = _RATES.get(model) or _RATES["claude-sonnet-4-6"]
    return (
        (input_tokens / 1_000_000.0) * rate.input_per_mtok
        + (output_tokens / 1_000_000.0) * rate.output_per_mtok
    )
