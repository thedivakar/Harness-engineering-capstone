"""Tests for the push-work-down invocation pipeline."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from shift_monitor import pipeline
from shift_monitor.client import RecordedClaudeClient
from shift_monitor.invocation import (
    Invocation,
    resumed,
    rich,
    thin,
)
from shift_monitor.scratchpad import Scratchpad, ScratchpadEntry
from shift_monitor.state import HotState
from shift_monitor.warm import WarmStore


@pytest.fixture
def seeded_warm(tmp_path: Path, defect_rows: list[dict[str, Any]]) -> WarmStore:
    store = WarmStore(tmp_path / "warm.sqlite")
    store.initialize()
    store.insert_many(defect_rows)
    return store


@pytest.fixture
def hot_state() -> HotState:
    return HotState(
        recent_defect_hashes=[f"h{i:02d}" for i in range(5)],
        current_shift_summary="Shift B 2026-04-29: 1 medium coolant-loop leak.",
        active_alerts=["capacitor-bank-C-7 elevated night-shift defect rate"],
        threshold_statuses={"defect_rate_per_shift": "WARN"},
    )


# ---------- SQL-side gather (no Python filtering) ----------


def test_gather_new_defects_is_pure_passthrough_to_sql(seeded_warm: WarmStore) -> None:
    since = "2026-04-01T00:00:00Z"
    expected = seeded_warm.defects_since(since, limit=50)
    actual = pipeline.gather_new_defects(seeded_warm, since, limit=50)
    assert actual == expected


def test_gather_new_defects_has_no_python_side_filtering() -> None:
    """AST inspection: no comprehensions, filters, ifs over rows."""
    source = inspect.getsource(pipeline.gather_new_defects)
    forbidden = ["if ", "for ", "filter(", "[r for", "[d for"]
    body = source.split("def gather_new_defects")[1]
    for token in forbidden:
        assert token not in body, (
            f"gather_new_defects must delegate to SQL, found '{token}' in body"
        )


# ---------- distinct invocation shapes ----------


def test_invocation_shapes_are_distinct(
    hot_state: HotState, defect_rows: list[dict[str, Any]]
) -> None:
    t = thin("What changed since 04:00?")
    r = rich(role="quality engineer", hot_state=hot_state, new_defects=defect_rows[:3])
    re = resumed(
        session_id="sess-2026-04-30-C",
        summary="Prior step found 3 defects on lot 2026-0430-B.",
        latest_message="Continue analysis.",
        prior_steps=[{"name": "gather", "payload": {"count": 3}}],
        new_defects=[],
    )
    assert isinstance(t, Invocation) and t.shape == "thin"
    assert isinstance(r, Invocation) and r.shape == "rich"
    assert isinstance(re, Invocation) and re.shape == "resumed"
    # Distinct prompts
    assert len({t.prompt, r.prompt, re.prompt}) == 3
    # Thin is shortest, rich and resumed both substantially longer
    assert len(t.prompt) < len(r.prompt)
    assert len(t.prompt) < len(re.prompt)
    # Rich contains the hot state summary; thin does not
    assert hot_state.current_shift_summary in r.prompt
    assert hot_state.current_shift_summary not in t.prompt
    # Resumed contains the partial-findings header
    assert "Prior partial findings" in re.prompt


# ---------- rich prompt size budget ----------


def test_build_rich_prompt_stays_under_4000_chars(
    hot_state: HotState, defect_rows: list[dict[str, Any]]
) -> None:
    prompt = pipeline.build_rich_prompt(
        role="quality engineer",
        hot_state=hot_state,
        new_defects=defect_rows[:8],
    )
    assert len(prompt) < 4_000, f"prompt is {len(prompt)} chars (limit 4000)"
    # Verify it actually contains the items it should
    assert hot_state.current_shift_summary in prompt
    for d in defect_rows[:8]:
        assert d["id"] in prompt


# ---------- run-shift orchestration and CLI ----------


def test_run_shift_invokes_client_exactly_once_and_writes_state(
    tmp_path: Path,
    seeded_warm: WarmStore,
    hot_state: HotState,
    recorded_shift_c_response: dict[str, Any],
) -> None:
    hot_path = tmp_path / "hot_state.json"
    hot_state.write_atomic(hot_path)
    scratchpad_path = tmp_path / "shift_scratchpad.jsonl"
    client = RecordedClaudeClient(responses=[recorded_shift_c_response["content"]])

    result = pipeline.run_shift(
        shift_id="C",
        client=client,
        warm=seeded_warm,
        hot_state_path=hot_path,
        scratchpad_path=scratchpad_path,
        since_ts="2026-04-29T22:00:00Z",
    )

    assert client.call_count == 1
    assert result.shift_id == "C"
    assert hot_path.exists()
    updated = HotState.from_path(hot_path)
    # Hot state summary must have been updated by the run
    assert updated.current_shift_summary != hot_state.current_shift_summary
    # Scratchpad must have at least one entry from this run
    sp = Scratchpad(scratchpad_path)
    entries = sp.read()
    assert any(isinstance(e, ScratchpadEntry) and e.hypothesis_id == "shift-C" for e in entries)


def test_run_shift_cli_entry_point_works(
    tmp_path: Path,
    seeded_warm: WarmStore,
    hot_state: HotState,
    recorded_shift_c_response: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`python -m shift_monitor run-shift --shift <ID>` is invokable."""
    hot_path = tmp_path / "hot_state.json"
    hot_state.write_atomic(hot_path)
    scratchpad_path = tmp_path / "shift_scratchpad.jsonl"
    recorded_path = tmp_path / "recorded.json"
    recorded_path.write_text(json.dumps({"content": recorded_shift_c_response["content"]}))

    from shift_monitor import __main__ as cli

    rc = cli.main(
        [
            "run-shift",
            "--shift",
            "C",
            "--warm-db",
            str(seeded_warm.db_path),
            "--hot-state",
            str(hot_path),
            "--scratchpad",
            str(scratchpad_path),
            "--since",
            "2026-04-29T22:00:00Z",
            "--recorded-response",
            str(recorded_path),
        ]
    )
    assert rc == 0
    assert scratchpad_path.exists()
