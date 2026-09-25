"""Tests for the tiered state foundation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from shift_monitor.cold import ColdStore
from shift_monitor.state import HotState
from shift_monitor.warm import WarmStore

# ---------- hot state model ----------


def test_hotstate_roundtrip_and_size_budget() -> None:
    state = HotState(
        recent_defect_hashes=[f"hash_{i:02d}" for i in range(20)],
        current_shift_summary="Shift A 2026-04-30: 2 low defects, 0 critical.",
        active_alerts=["capacitor-bank-C-7 elevated night-shift defect rate"],
        threshold_statuses={"defect_rate_per_shift": "WARN", "critical_count_24h": "OK"},
    )
    payload = state.to_json_bytes()
    assert isinstance(payload, bytes)
    assert len(payload) <= 5_120, f"hot state {len(payload)} bytes exceeds 5120-byte budget"
    restored = HotState.from_json_bytes(payload)
    assert restored == state


def test_hotstate_rejects_more_than_20_hashes() -> None:
    with pytest.raises(ValueError):
        HotState(
            recent_defect_hashes=[f"h_{i}" for i in range(21)],
            current_shift_summary="",
            active_alerts=[],
            threshold_statuses={},
        )


def test_hotstate_atomic_write(tmp_path: Path) -> None:
    state = HotState(
        recent_defect_hashes=["a", "b"],
        current_shift_summary="s",
        active_alerts=[],
        threshold_statuses={},
    )
    target = tmp_path / "hot_state.json"
    state.write_atomic(target)
    assert target.exists()
    restored = HotState.from_path(target)
    assert restored == state


# ---------- warm store schema and inserts ----------


def test_warmstore_creates_table_and_index(tmp_path: Path) -> None:
    db = tmp_path / "warm.sqlite"
    store = WarmStore(db)
    store.initialize()
    # Schema check
    cols = store.column_names("defects")
    assert cols == ["id", "ts", "shift", "component", "severity", "description"]
    # Index check (named idx_defects_shift_ts on (shift, ts))
    assert store.has_index_on("defects", ("shift", "ts"))


def test_warmstore_insert_many_roundtrips(
    tmp_path: Path, defect_rows: list[dict[str, Any]]
) -> None:
    db = tmp_path / "warm.sqlite"
    store = WarmStore(db)
    store.initialize()
    store.insert_many(defect_rows)
    assert store.count() == len(defect_rows)
    assert store.count() >= 30
    fetched = store.fetch_by_id(defect_rows[0]["id"])
    assert fetched is not None
    assert fetched["component"] == defect_rows[0]["component"]


# ---------- cold store monthly summaries ----------


def test_coldstore_writes_monthly_summary(
    tmp_path: Path, defect_rows: list[dict[str, Any]]
) -> None:
    warm_db = tmp_path / "warm.sqlite"
    store = WarmStore(warm_db)
    store.initialize()
    store.insert_many(defect_rows)

    cold_dir = tmp_path / "cold"
    cold = ColdStore(store=store, cold_dir=cold_dir)
    cold.write_monthly_summary(2026, 3)
    march = cold_dir / "2026-03.md"
    assert march.exists()
    text = march.read_text()
    # Heading + total + top-3 component lines
    assert "# 2026-03" in text
    # March has 23 defects in fixture
    assert "Total defects: 23" in text
    # capacitor-bank-C-7 is top component in March
    assert "capacitor-bank-C-7" in text
    # Top-3 section has at least 3 component lines
    component_lines = [
        line for line in text.splitlines() if line.startswith("- ") and "defect" in line
    ]
    assert len(component_lines) >= 3


def test_coldstore_handles_empty_month(tmp_path: Path) -> None:
    warm_db = tmp_path / "warm.sqlite"
    store = WarmStore(warm_db)
    store.initialize()
    cold = ColdStore(store=store, cold_dir=tmp_path / "cold")
    cold.write_monthly_summary(2030, 1)
    target = tmp_path / "cold" / "2030-01.md"
    assert target.exists()
    assert "Total defects: 0" in target.read_text()


# ---------- indexed defects_since query ----------


def test_defects_since_uses_index_and_does_not_load_full_table(
    tmp_path: Path, defect_rows: list[dict[str, Any]]
) -> None:
    db = tmp_path / "warm.sqlite"
    store = WarmStore(db)
    store.initialize()
    store.insert_many(defect_rows)

    # EXPLAIN QUERY PLAN must show the index is used
    plan = store.explain_defects_since("2026-04-01T00:00:00Z", limit=50)
    plan_text = " ".join(row[-1] for row in plan).lower()
    assert "idx_defects_shift_ts" in plan_text or "using index" in plan_text, plan

    rows = store.defects_since("2026-04-01T00:00:00Z", limit=50)
    # All April rows in fixture = 17
    assert len(rows) == 17
    # Newest first
    timestamps = [r["ts"] for r in rows]
    assert timestamps == sorted(timestamps, reverse=True)


def test_defects_since_respects_limit(
    tmp_path: Path, defect_rows: list[dict[str, Any]]
) -> None:
    db = tmp_path / "warm.sqlite"
    store = WarmStore(db)
    store.initialize()
    store.insert_many(defect_rows)
    rows = store.defects_since("2026-01-01T00:00:00Z", limit=5)
    assert len(rows) == 5
