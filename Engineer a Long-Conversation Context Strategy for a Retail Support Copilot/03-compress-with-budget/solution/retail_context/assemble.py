"""Position-aware context assembly.

Layout (top → bottom):
  # Case Facts                       — top boundary, structured (≤ 600 tokens)
  # Resolved: Refund inquiry         — middle, compressible zone (≤ 500 tokens)
  # Resolved: Subscription cancellation — middle, compressible zone (≤ 500 tokens)
  # Active issue: Payment-method update — bottom boundary, byte-exact verbatim

This places key findings at both context boundaries (Case Facts at top, the
active turn-by-turn at bottom against the new user turn) and lets the resolved
narrative occupy the lower-attention middle. Sections are exclusive — no
interleaving.
"""
from __future__ import annotations

from dataclasses import dataclass

from retail_context.case_facts import CaseFacts
from retail_context.compressor import Compressed
from retail_context.tokens import count

# TODO: Define the exact-text header contract.
# RESOLVED_TITLES maps `issue_id` ("refund", "subscription") to the literal
# Markdown header string that must appear above that section in the assembled
# context. ACTIVE_TITLES does the same for the active segment.
# The AST audit (test_antipatterns.py) regex-matches against these exact strings,
# so they are part of the contract — change them and the
# audit fails. Use level-1 headings (# ...), not ##.
RESOLVED_TITLES: dict[str, str] = {}
ACTIVE_TITLES: dict[str, str] = {}


@dataclass
class AssembledContext:
    markdown: str
    case_facts_block: str
    resolved_blocks: dict[str, str]
    active_block: str
    active_raw_text: str  # byte-exact verbatim source for the active segment

    def section_tokens(self) -> dict[str, int]:
        sections = {"case_facts": count(self.case_facts_block)}
        for issue_id, block in self.resolved_blocks.items():
            sections[f"resolved_{issue_id}"] = count(block)
        sections["active"] = count(self.active_block)
        return sections

    def total_tokens(self) -> int:
        return count(self.markdown)


def build(case_facts: CaseFacts, compressed: Compressed) -> AssembledContext:
    # TODO: Implement the top → middle → bottom assembly.
    #
    # 1. Top boundary — the case-facts block.
    #    Render `case_facts.to_markdown()` and ensure it ends with exactly one
    #    trailing newline.
    #
    # 2. Middle — the resolved-section blocks, in declaration order.
    #    For each issue_id in ("refund", "subscription"):
    #      - confirm `compressed.summaries` contains that issue_id; if not,
    #        raise KeyError naming the missing issue.
    #      - render the block as f"{RESOLVED_TITLES[issue_id]}\n\n{summary_text}\n"
    #        where summary_text is the stripped `.text` of the Summary.
    #    Order matters — refund before subscription — because the regex
    #    audits the exact section sequence.
    #
    # 3. Bottom boundary — the active block (byte-exact).
    #    Look up the active title in ACTIVE_TITLES by compressed.active_issue_id;
    #    if missing, fall back to f"# Active issue: {compressed.active_issue_id}".
    #    The body is `compressed.active_text` unchanged (this is the byte-exact
    #    contract — do not strip, re-render, or normalize).
    #
    # 4. Concatenate top + blank line + refund block + blank line + subscription
    #    block + blank line + active block into the final `markdown` string.
    #
    # 5. Return an AssembledContext with all five fields populated. The
    #    `active_raw_text` field is `compressed.active_text` — the AST audit uses
    #    it to verify the assembled `active_block` body equals the raw turns.
    raise NotImplementedError("Exercise 4: implement position-aware assembly")
