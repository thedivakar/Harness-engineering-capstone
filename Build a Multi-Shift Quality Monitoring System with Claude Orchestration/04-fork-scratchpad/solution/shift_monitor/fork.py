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
    fork_dir = forks_root / hypothesis_id
    fork_dir.mkdir(parents=True, exist_ok=True)
    target = fork_dir / "hot_state.json"
    shutil.copyfile(base_hot_state_path, target)
    return fork_dir


def merge_findings(scratchpad_paths: Iterable[Path], main_scratchpad: Path) -> None:
    main = Scratchpad(main_scratchpad)
    for path in scratchpad_paths:
        if not path.exists():
            continue
        for entry in Scratchpad(path).read():
            main.append(entry)
