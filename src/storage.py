"""JSON file management for snapshots and rollback logs."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import (
    SNAPSHOTS_DIR,
    ROLLBACKS_DIR,
    LATEST_DIR,
    ROLLBACK_LOG_FILE,
    LATEST_COMPARISON_FILE,
    THAMES_LATEST_FILE,
    NSOH_LATEST_FILE,
)
from .models import Snapshot, ComparisonResult


def ensure_directories():
    """Create data directories if they don't exist."""
    for dir_path in [SNAPSHOTS_DIR, ROLLBACKS_DIR, LATEST_DIR]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def get_snapshot_path(timestamp: str, source: str) -> str:
    """Get the file path for a snapshot.

    Args:
        timestamp: ISO timestamp.
        source: "thames" or "nsoh".

    Returns:
        File path for the snapshot.
    """
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    date_folder = dt.strftime("%Y-%m-%d")
    time_str = dt.strftime("%H-%M-%S")

    folder_path = Path(SNAPSHOTS_DIR) / date_folder
    folder_path.mkdir(parents=True, exist_ok=True)

    return str(folder_path / f"{source}_{time_str}.json")


def save_snapshot(snapshot: Snapshot) -> str:
    """Save a snapshot to the snapshots directory.

    Args:
        snapshot: The snapshot to save.

    Returns:
        Path where the snapshot was saved.
    """
    ensure_directories()
    path = get_snapshot_path(snapshot.timestamp, snapshot.source)

    with open(path, "w") as f:
        json.dump(snapshot.to_dict(), f, indent=2)

    return path


def save_latest(snapshot: Snapshot):
    """Save a snapshot as the latest for its source.

    Args:
        snapshot: The snapshot to save.
    """
    ensure_directories()

    filename = THAMES_LATEST_FILE if snapshot.source == "thames" else NSOH_LATEST_FILE
    path = Path(LATEST_DIR) / filename

    with open(path, "w") as f:
        json.dump(snapshot.to_dict(), f, indent=2)


def load_latest(source: str) -> Optional[Snapshot]:
    """Load the latest snapshot for a source.

    Args:
        source: "thames" or "nsoh".

    Returns:
        Snapshot if found, None otherwise.
    """
    filename = THAMES_LATEST_FILE if source == "thames" else NSOH_LATEST_FILE
    path = Path(LATEST_DIR) / filename

    if not path.exists():
        return None

    with open(path, "r") as f:
        data = json.load(f)
        return Snapshot.from_dict(data)


def append_rollback_log(result: ComparisonResult):
    """Append a comparison result to the rollback log.

    Only appends if rollbacks were detected.

    Args:
        result: The comparison result.
    """
    if result.rollbacks_detected == 0:
        return

    ensure_directories()
    log_path = Path(ROLLBACKS_DIR) / ROLLBACK_LOG_FILE

    # Load existing log or create new
    log_entries = []
    if log_path.exists():
        with open(log_path, "r") as f:
            log_entries = json.load(f)

    # Append new entry
    log_entries.append(result.to_dict())

    # Save updated log
    with open(log_path, "w") as f:
        json.dump(log_entries, f, indent=2)


def save_latest_comparison(result: ComparisonResult):
    """Save the latest comparison result.

    Args:
        result: The comparison result.
    """
    ensure_directories()
    path = Path(ROLLBACKS_DIR) / LATEST_COMPARISON_FILE

    with open(path, "w") as f:
        json.dump(result.to_dict(), f, indent=2)


def load_rollback_log() -> list[ComparisonResult]:
    """Load all rollback events from the log.

    Returns:
        List of ComparisonResults.
    """
    log_path = Path(ROLLBACKS_DIR) / ROLLBACK_LOG_FILE

    if not log_path.exists():
        return []

    with open(log_path, "r") as f:
        data = json.load(f)
        return [ComparisonResult.from_dict(entry) for entry in data]
