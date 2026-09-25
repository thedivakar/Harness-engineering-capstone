"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture(scope="session")
def defect_rows() -> list[dict[str, Any]]:
    with (FIXTURES_DIR / "defects.json").open() as f:
        rows: list[dict[str, Any]] = json.load(f)
    return rows


@pytest.fixture(scope="session")
def recorded_shift_c_response() -> dict[str, Any]:
    with (FIXTURES_DIR / "recorded_responses" / "shift_C_2026-04-30.json").open() as f:
        payload: dict[str, Any] = json.load(f)
    return payload
