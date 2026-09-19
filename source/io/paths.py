# ------------------------------------------------------------------
# File:    source/io/paths.py
# Author:  Jonas Scholz
# Purpose: Resolve repo-root / static / output / MULTALL paths for all modules.
# ------------------------------------------------------------------

"""Centralised path resolution for the refactored package.

Replaces the ad-hoc ``Path(__file__).parent.parent`` blocks that were
duplicated in src/GUI.py and src/stage_calculation.py. Behavior is
identical: paths resolve relative to the repository root.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

STATIC_FOLDER = REPO_ROOT / "static"
JSON_FILE = "Populated_data.json"
JSON_PATH = STATIC_FOLDER / JSON_FILE

OUTPUT_FOLDER_DEFAULT = "Run_Multall"


def resolve_absolute(folder: str | os.PathLike) -> str:
    """Return ``folder`` absolute; relative paths are resolved against repo root
    (matches the old ``os.path.join(current_dir, folder)`` behavior)."""
    folder_str = os.fspath(folder)
    if os.path.isabs(folder_str):
        return folder_str
    return os.path.join(str(REPO_ROOT), folder_str)