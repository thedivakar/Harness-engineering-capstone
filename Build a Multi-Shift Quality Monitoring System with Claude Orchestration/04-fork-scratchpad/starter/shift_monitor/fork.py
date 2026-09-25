"""Layer 3 fork: copy hot state into an isolated working directory per hypothesis.

`fork_session` here is the application-side framing: the SDK / CLI primitive lives at
Layer 2; here we reproduce the *semantics* (shared baseline, isolated scratchpads,
no cross-contamination) using state-file copies.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterable
from pathlib import Path

from .scratchpad import Scratchpad


def fork_for_hypothesis(
    base_hot_state_path: Path,
    hypothesis_id: str,
    forks_root: Path,
) -> Path:
    # TODO: Create a per-hypothesis working directory at `forks_root / hypothesis_id`
    # and copy the base hot state into it.
    #
    #   1. Make the directory exist (parents=True, exist_ok=True).
    #   2. Use shutil.copyfile to copy `base_hot_state_path` to
    #      `<fork_dir>/hot_state.json`. The base file's bytes must remain
    #      untouched after this call (this is what "shared baseline" means).
    #   3. Return the fork directory path.
    raise NotImplementedError


def merge_findings(scratchpad_paths: Iterable[Path], main_scratchpad: Path) -> None:
    # TODO: Append every entry from each fork's scratchpad into the main scratchpad.
    #
    # Important: route every appended entry through `Scratchpad(main_scratchpad).append(entry)`.
    # Do not open the main file with raw `open(..., "a")` to "speed it up" — that
    # bypasses the fsync semantics inside Scratchpad.append and silently weakens
    # durability. Use the same append path the rest of the system uses.
    #
    # Skip fork paths that don't exist (a fork may not have produced any findings).
    raise NotImplementedError
